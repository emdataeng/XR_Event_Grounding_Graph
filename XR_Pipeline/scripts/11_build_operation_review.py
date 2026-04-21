#!/usr/bin/env python3
"""11_build_operation_review.py — Build a human-readable review package for operation events.

Consumes:
  object_tracks.csv          — 06_link_object_tracks.py
  event_windows.csv          — 07_build_event_windows.py
  objects/operation_events.csv — 10b_build_operation_events.py
  graphs/scene_state_package.json — 09b_build_scene_state_package.py (optional)

Produces under data/processed/<session>/reviews/operations/:
  session_review.json        — machine-readable session-level summary
  session_review.md          — human-readable session summary
  op_<id>_<type>.json        — per-operation evidence bundle (machine)
  op_<id>_<type>.md          — per-operation evidence summary (human)
  op_<id>_<type>_f<frame>.png — representative overlay frame (if debug_boxes/ exist)

Usage:
  python scripts/11_build_operation_review.py --session session_003
  python scripts/11_build_operation_review.py --session session_003 --max-frames 5
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.scene_state_package import load_scene_state_package
from src.domain_config import load_domain_config
from src.run_metadata import (
    build_run_metadata, save_run_metadata,
    check_staleness, emit_staleness_warnings,
)

app = typer.Typer()
console = Console()


@app.command()
def main(
    session:    str  = typer.Option("session_001", help="Session identifier"),
    config:     str  = typer.Option(None,          help="Path to pipeline.yaml override"),
    force:      bool = typer.Option(False, "--force",
                                    help="Continue even if upstream output is stale."),
    max_frames: int  = typer.Option(3,
                                    help="Max overlay frames to copy per operation (0 = skip)."),
):
    """Build per-operation evidence bundles and a session-level review package."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # D2: load domain config for review labeling
    domain = load_domain_config(cfg=cfg)
    domain_name = domain.domain_name if domain else None

    # ── Staleness guard ───────────────────────────────────────────────────────
    warnings = check_staleness(paths.processed_root, "10b_build_operation_events", cfg, thr)
    if not emit_staleness_warnings(warnings, console=console, force=force):
        raise typer.Exit(1)

    # ── Check prerequisites ───────────────────────────────────────────────────
    ops_path = paths.objects_dir / "operation_events.csv"
    if not ops_path.exists():
        console.print("[red]operation_events.csv not found. Run 10b first.[/red]")
        raise typer.Exit(1)

    for name, p in [("object_tracks.csv", paths.object_tracks),
                    ("event_windows.csv", paths.event_windows)]:
        if not p.exists():
            console.print(f"[red]{name} not found.[/red]")
            raise typer.Exit(1)

    # ── Load inputs ───────────────────────────────────────────────────────────
    ops_df    = pd.read_csv(ops_path)
    tracks_df = pd.read_csv(paths.object_tracks)
    events_df = pd.read_csv(paths.event_windows)

    ssp: dict | None = None
    if paths.scene_state_package.exists():
        ssp = load_scene_state_package(paths.scene_state_package)

    # Optional: motion diagnostics (from stage 07)
    motion_debug_df: "pd.DataFrame | None" = None
    if paths.track_motion_debug.exists():
        motion_debug_df = pd.read_csv(paths.track_motion_debug)

    # Optional: workflow timeline (from stage 10c)
    timeline: "dict | None" = None
    if paths.workflow_timeline.exists():
        with open(paths.workflow_timeline) as _f:
            timeline = json.load(_f)

    console.print(
        f"[bold]Building operation review[/bold] | "
        f"{len(ops_df)} operations, "
        f"{tracks_df['track_id'].nunique()} tracks, "
        f"{len(events_df)} primitive events"
    )

    out_dir = paths.reviews_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Per-operation evidence bundles ────────────────────────────────────────
    n_written = 0
    for _, op in ops_df.iterrows():
        bundle = _build_operation_bundle(op, tracks_df, events_df)
        slug   = f"op_{op['operation_id']}_{op['operation_type']}"

        (out_dir / f"{slug}.json").write_text(
            json.dumps(bundle, indent=2, default=str)
        )
        (out_dir / f"{slug}.md").write_text(
            _render_operation_md(bundle)
        )

        if max_frames > 0:
            _copy_overlay_frames(op, paths, out_dir, slug, max_frames)

        n_written += 1

    console.print(f"[green]✓ {n_written} per-operation bundles → {out_dir}[/green]")

    # ── Session-level review ─────────────────────────────────────────────────
    session_review = _build_session_review(
        session_id=session,
        ops_df=ops_df,
        tracks_df=tracks_df,
        events_df=events_df,
        ssp=ssp,
        motion_debug_df=motion_debug_df,
        timeline=timeline,
        thr=thr,
        domain_name=domain_name,
    )

    (out_dir / "session_review.json").write_text(
        json.dumps(session_review, indent=2, default=str)
    )
    (out_dir / "session_review.md").write_text(
        _render_session_md(session_review)
    )
    console.print(f"[green]✓ session_review.{{json,md}} → {out_dir}[/green]")

    # ── Console summary table ─────────────────────────────────────────────────
    if not ops_df.empty:
        table = Table(title="Operation Review Summary")
        table.add_column("ID"); table.add_column("Type"); table.add_column("Agent")
        table.add_column("Object"); table.add_column("Frames"); table.add_column("Conf")
        for _, op in ops_df.sort_values("confidence", ascending=False).iterrows():
            table.add_row(
                str(op["operation_id"]),
                str(op["operation_type"]),
                str(op["agent_track_id"] or "–"),
                str(op["object_track_id"] or "–"),
                f"{op['start_frame_idx']}→{op['end_frame_idx']}",
                f"{op['confidence']:.2f}",
            )
        console.print(table)

    # Print session-level workflow summary
    wf = session_review.get("workflow_phase")
    if wf:
        console.print(
            f"\nWorkflow phase: [bold]{wf['label']}[/bold] "
            f"(conf={wf['confidence']:.2f}, {wf['evidence']})"
        )

    unresolved = session_review.get("unresolved_candidates", [])
    if unresolved:
        console.print(f"[yellow]Unresolved candidates: {len(unresolved)}[/yellow]")

    # ── Run metadata ──────────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="11_build_operation_review",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "n_operations": len(ops_df),
            "n_bundles":    n_written,
            "review_dir":   str(out_dir),
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


# ── Per-operation bundle ──────────────────────────────────────────────────────

def _build_operation_bundle(
    op: "pd.Series",
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
) -> dict:
    """Build a self-contained evidence bundle dict for a single operation."""
    op_type    = str(op["operation_type"])
    agent_tid  = str(op["agent_track_id"]) if _notnull(op["agent_track_id"]) else None
    object_tid = str(op["object_track_id"]) if _notnull(op["object_track_id"]) else None

    # Involved classes and roles
    involved: list[dict] = []
    for tid in filter(None, [agent_tid, object_tid]):
        t_rows = tracks_df[tracks_df["track_id"] == tid]
        if not t_rows.empty:
            first = t_rows.sort_values("timestamp_ns").iloc[0]
            involved.append({
                "track_id":       tid,
                "semantic_class": str(first.get("semantic_class", "unknown")),
                "object_role":    str(first.get("object_role", "workpiece")),
            })

    # Primitive evidence events
    ev_raw   = op.get("evidence_event_ids", "[]")
    ev_ids   = json.loads(ev_raw) if isinstance(ev_raw, str) else []
    ev_rows  = events_df[events_df["event_id"].isin(ev_ids)]
    evidence = []
    for _, ev in ev_rows.iterrows():
        evidence.append({
            "event_id":      str(ev["event_id"]),
            "event_type":    str(ev["event_type"]),
            "frame_range":   [int(ev["start_frame_idx"]), int(ev["end_frame_idx"])],
            "trigger_reason": str(ev.get("trigger_reason", "")),
            "confidence":    float(ev.get("confidence", 0.5)),
        })

    # Natural-language explanation
    explanation = _explain_operation(op_type, involved, evidence)

    return {
        "operation_id":   str(op["operation_id"]),
        "operation_type": op_type,
        "frame_range":    [int(op["start_frame_idx"]), int(op["end_frame_idx"])],
        "confidence":     round(float(op["confidence"]), 3),
        "involved_tracks": involved,
        "evidence_events": evidence,
        "notes":           str(op.get("notes", "")),
        "explanation":     explanation,
        "generated_at":    datetime.now(timezone.utc).isoformat(),
    }


def _explain_operation(
    op_type: str,
    involved: list,
    evidence: list,
) -> str:
    """Generate a one-sentence natural-language explanation."""
    agents   = [t for t in involved if t["object_role"] == "hand"]
    objects  = [t for t in involved if t["object_role"] != "hand"]
    ev_types = sorted({e["event_type"] for e in evidence})

    agent_str  = agents[0]["track_id"]  if agents  else "an unknown agent"
    object_str = objects[0]["semantic_class"] if objects else "an unknown object"
    ev_str     = ", ".join(ev_types) if ev_types else "no primitive events"

    _EXPLANATIONS = {
        "HOLD":              f"{agent_str} was continuously near {object_str} without moving it (evidence: {ev_str}).",
        "PICK_UP":           f"{agent_str} picked up {object_str} — interaction onset coincided with workpiece movement (evidence: {ev_str}).",
        "PUT_DOWN":          f"{agent_str} placed {object_str} down — workpiece movement ended near interaction offset (evidence: {ev_str}).",
        "CONTACT":           f"{object_str} came into close contact with another object (evidence: {ev_str}).",
        "TRANSFER":          f"{object_str} moved without a detected agent — cause inferred as transfer (evidence: {ev_str}).",
        "USE_TOOL":          f"{agent_str} used a tool near {object_str} (evidence: {ev_str}).",
        "PICK_UP_CANDIDATE": f"{object_str} moved from rest but no hand was detected — pick-up inferred at lower confidence (evidence: {ev_str}).",
        "PUT_DOWN_CANDIDATE": f"{object_str} came to rest after moving but no hand was detected — put-down inferred at lower confidence (evidence: {ev_str}).",
    }
    return _EXPLANATIONS.get(op_type, f"{op_type} involving {object_str} (evidence: {ev_str}).")


# ── Session-level review ──────────────────────────────────────────────────────

def _build_session_review(
    session_id: str,
    ops_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    ssp: "dict | None",
    motion_debug_df: "pd.DataFrame | None" = None,
    timeline: "dict | None" = None,
    thr: "dict | None" = None,
    domain_name: "str | None" = None,
) -> dict:
    """Build a session-level summary dict."""
    if ops_df.empty:
        return {
            "session_id":          session_id,
            "domain_name":         domain_name,
            "n_operations":        0,
            "n_primitive_events":  len(events_df),
            "n_tracks":            int(tracks_df["track_id"].nunique()) if not tracks_df.empty else 0,
            "operation_counts":    {},
            "primitive_event_counts": {},
            "manipulated_objects": [],
            "workflow_phase":      None,
            "unresolved_candidates": [],
            "phase_explanation":   "No operations detected.",
            "state_changes":       _build_state_changes(motion_debug_df, events_df),
            "workflow_timeline":   _build_timeline_summary(timeline),
            "detection_gaps":      _build_detection_gaps(
                events_df, ops_df, tracks_df, motion_debug_df, thr
            ),
        }

    op_counts = ops_df["operation_type"].value_counts().to_dict()

    # Manipulated objects (appeared as object_track_id in any op)
    manip_tids = ops_df["object_track_id"].dropna().unique().tolist()
    manip_objects = []
    for tid in manip_tids:
        t_rows = tracks_df[tracks_df["track_id"] == str(tid)]
        if not t_rows.empty:
            sem = str(t_rows["semantic_class"].iloc[0])
            role = str(t_rows.get("object_role", pd.Series(["workpiece"])).iloc[0]) if "object_role" in t_rows.columns else "workpiece"
            manip_objects.append({"track_id": tid, "semantic_class": sem, "object_role": role})

    # Workflow phase (prefer SSP, fall back to ops_df)
    wf_phase: "dict | None" = None
    if ssp:
        wf_phase = ssp.get("state_summary", {}).get("workflow_phase")
    if wf_phase is None and not ops_df.empty:
        op_weights = (
            ops_df.groupby("operation_type")["confidence"]
            .agg(["count", "mean"])
        )
        op_weights["score"] = op_weights["count"] * op_weights["mean"]
        best_type  = op_weights["score"].idxmax()
        best_score = float(op_weights.loc[best_type, "score"])
        total      = float(op_weights["score"].sum())
        wf_phase = {
            "label":      str(best_type).lower(),
            "confidence": round(best_score / total if total > 0 else 0.0, 3),
            "evidence":   f"{int(op_weights.loc[best_type, 'count'])} {best_type} events",
        }

    # Unresolved candidates
    candidates = ops_df[
        ops_df["operation_type"].str.endswith("_CANDIDATE", na=False)
    ]
    unresolved = [
        {
            "operation_id":   str(r["operation_id"]),
            "operation_type": str(r["operation_type"]),
            "object":         str(r["object_track_id"]) if _notnull(r["object_track_id"]) else None,
            "confidence":     round(float(r["confidence"]), 3),
            "notes":          str(r["notes"]),
        }
        for _, r in candidates.iterrows()
    ]

    # Phase explanation
    phase_explanation = _explain_phase(wf_phase, ops_df) if wf_phase else "No phase determined."

    # Primitive vs operation timeline summary
    prim_type_counts = events_df["event_type"].value_counts().to_dict() if not events_df.empty else {}

    # E1: State-change summary from motion debug
    state_changes = _build_state_changes(motion_debug_df, events_df)

    # E2: Workflow timeline summary
    timeline_summary = _build_timeline_summary(timeline)

    # E3: Detection gap analysis — explain why PICK_UP / MOVE didn't fire
    detection_gaps = _build_detection_gaps(events_df, ops_df, tracks_df, motion_debug_df, thr)

    return {
        "session_id":          session_id,
        "domain_name":         domain_name,
        "n_operations":        len(ops_df),
        "n_primitive_events":  len(events_df),
        "n_tracks":            int(tracks_df["track_id"].nunique()),
        "operation_counts":    {str(k): int(v) for k, v in op_counts.items()},
        "primitive_event_counts": {str(k): int(v) for k, v in prim_type_counts.items()},
        "manipulated_objects": manip_objects,
        "workflow_phase":      wf_phase,
        "unresolved_candidates": unresolved,
        "phase_explanation":   phase_explanation,
        "state_changes":       state_changes,
        "workflow_timeline":   timeline_summary,
        "detection_gaps":      detection_gaps,
    }


def _explain_phase(wf_phase: dict, ops_df: pd.DataFrame) -> str:
    label  = wf_phase.get("label", "unknown")
    conf   = wf_phase.get("confidence", 0.0)
    evid   = wf_phase.get("evidence", "")
    # Find the best supporting operation
    phase_ops = ops_df[
        ops_df["operation_type"].str.lower() == label
    ].sort_values("confidence", ascending=False)
    if phase_ops.empty:
        return (
            f"The dominant workflow phase is '{label}' (conf={conf:.2f}, {evid}). "
            "No individual supporting operation found."
        )
    best = phase_ops.iloc[0]
    return (
        f"The dominant workflow phase is '{label}' (conf={conf:.2f}, {evid}). "
        f"Best supporting operation: {best['operation_id']} "
        f"(frames {best['start_frame_idx']}–{best['end_frame_idx']}, "
        f"conf={best['confidence']:.2f}). "
        f"Notes: {best['notes']}"
    )


# ── E1: State-change summary ──────────────────────────────────────────────────

def _build_state_changes(
    motion_debug_df: "pd.DataFrame | None",
    events_df: pd.DataFrame,
) -> dict:
    """Summarise motion per track from track_motion_debug.csv (E1)."""
    move_events = events_df[events_df["event_type"] == "MOVE"] if not events_df.empty else pd.DataFrame()

    per_track: list = []
    if motion_debug_df is not None and not motion_debug_df.empty:
        for tid, grp in motion_debug_df.groupby("track_id"):
            disps = grp["displacement_m"].dropna()
            max_disp = float(disps.max()) if len(disps) else 0.0
            thr_val  = float(grp["move_threshold_m"].iloc[0]) if "move_threshold_m" in grp.columns else None
            n_fired  = int(grp["would_fire_move"].sum()) if "would_fire_move" in grp.columns else 0
            per_track.append({
                "track_id":           str(tid),
                "semantic_class":     str(grp["semantic_class"].iloc[0]) if "semantic_class" in grp.columns else "unknown",
                "object_role":        str(grp["object_role"].iloc[0]) if "object_role" in grp.columns else "unknown",
                "max_displacement_m": round(max_disp, 4),
                "move_threshold_m":   round(thr_val, 4) if thr_val is not None else None,
                "steps_above_threshold": n_fired,
                "below_threshold_by_m": round(thr_val - max_disp, 4) if thr_val and max_disp < thr_val else None,
            })

    # Tracks that actually produced MOVE primitive events
    move_tids: list = []
    for _, me in move_events.iterrows():
        try:
            import json as _json
            tids_in = [str(t) for t in _json.loads(me["primary_track_ids"])]
            move_tids.extend(tids_in)
        except Exception:
            pass

    return {
        "per_track_motion":       per_track,
        "tracks_with_move_events": list(set(move_tids)),
        "n_move_primitive_events": len(move_events),
    }


# ── E2: Workflow timeline summary ─────────────────────────────────────────────

def _build_timeline_summary(timeline: "dict | None") -> dict:
    """Build a compact workflow timeline summary for the session_review (E2)."""
    if not timeline:
        return {"available": False}

    summary = timeline.get("summary", {})
    phases  = timeline.get("phases", [])
    trans   = timeline.get("phase_transitions", [])

    phase_summaries = [
        {
            "phase_id":   p["phase_id"],
            "label":      p["label"],
            "frames":     [p["start_frame_idx"], p["end_frame_idx"]],
            "confidence": p["confidence"],
            "n_ops":      len(p.get("supporting_operations", [])),
            "objects":    p.get("object_tracks", []),
        }
        for p in phases
    ]

    transition_summaries = [
        {
            "from": t["from_label"],
            "to":   t["to_label"],
            "gap_s": round(t["gap_ns"] / 1e9, 2),
            "is_new_activity": t["is_new_activity"],
        }
        for t in trans
    ]

    return {
        "available":           True,
        "total_phases":        summary.get("total_phases", 0),
        "dominant_phase":      summary.get("dominant_phase", "idle"),
        "phase_sequence":      summary.get("phase_sequence", []),
        "has_manipulation":    summary.get("has_manipulation", False),
        "has_placement":       summary.get("has_placement", False),
        "phases":              phase_summaries,
        "transitions":         transition_summaries,
    }


# ── E3: Detection gap analysis ────────────────────────────────────────────────

def _build_detection_gaps(
    events_df: pd.DataFrame,
    ops_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    motion_debug_df: "pd.DataFrame | None",
    thr: "dict | None",
) -> dict:
    """Explain why expected operations (PICK_UP, MOVE) may be missing (E3)."""
    thr = thr or {}
    e_cfg  = thr.get("events", {})
    op_cfg = thr.get("operation_events", {})
    pickup_gap = int(op_cfg.get("pickup_link_frame_gap", 10))

    gaps: list[str] = []

    # Did any MOVE primitive events fire?
    move_events = events_df[events_df["event_type"] == "MOVE"] if not events_df.empty else pd.DataFrame()
    interact_events = events_df[events_df["event_type"] == "INTERACTION"] if not events_df.empty else pd.DataFrame()
    n_moves = len(move_events)
    n_interactions = len(interact_events)

    move_missing = n_moves == 0
    if move_missing:
        gaps.append("No MOVE primitive events detected.")

    # Per-track near-threshold evidence from motion debug
    near_threshold_tracks: list = []
    if motion_debug_df is not None and not motion_debug_df.empty:
        for tid, grp in motion_debug_df.groupby("track_id"):
            disps = grp["displacement_m"].dropna()
            if disps.empty:
                continue
            max_disp  = float(disps.max())
            thr_val   = float(grp["move_threshold_m"].iloc[0]) if "move_threshold_m" in grp.columns else None
            sem_class = str(grp["semantic_class"].iloc[0]) if "semantic_class" in grp.columns else "unknown"
            role      = str(grp["object_role"].iloc[0])     if "object_role"    in grp.columns else "unknown"

            if thr_val is not None and max_disp < thr_val:
                near_threshold_tracks.append({
                    "track_id":           str(tid),
                    "semantic_class":     sem_class,
                    "object_role":        role,
                    "max_displacement_m": round(max_disp, 4),
                    "threshold_m":        round(thr_val, 4),
                    "below_by_m":         round(thr_val - max_disp, 4),
                })
                gaps.append(
                    f"Track {tid} ({sem_class}/{role}): max displacement "
                    f"{max_disp:.3f}m < threshold {thr_val:.3f}m "
                    f"(below by {thr_val - max_disp:.3f}m). "
                    "Consider lowering threshold or check depth quality."
                )

    # Were there INTERACTION events? If so, did any get linked to MOVE events?
    if n_interactions == 0 and not tracks_df.empty:
        has_hand = (
            "object_role" in tracks_df.columns and
            (tracks_df["object_role"] == "hand").any()
        )
        if has_hand:
            gaps.append(
                "No INTERACTION events despite hand tracks being present. "
                "Hand may not have come within near_threshold_m of any workpiece."
            )
        else:
            gaps.append("No hand-role tracks detected — PICK_UP/HOLD require hand tracks.")

    elif n_interactions > 0 and move_missing:
        gaps.append(
            f"{n_interactions} INTERACTION event(s) found but no MOVE events — "
            "all will produce HOLD (not PICK_UP). "
            f"PICK_UP requires a MOVE within {pickup_gap} frames of interaction onset."
        )

    # Did we get PICK_UP operations?
    n_pickup = int((ops_df["operation_type"] == "PICK_UP").sum()) if not ops_df.empty else 0
    n_hold   = int((ops_df["operation_type"] == "HOLD").sum())    if not ops_df.empty else 0
    n_total  = len(ops_df)

    if n_total == 0:
        gaps.append("No operations detected at all.")
    elif n_hold > 0 and n_pickup == 0:
        gaps.append(
            f"Only HOLD detected ({n_hold} event(s)). "
            "This typically means the hand was near the workpiece "
            "but no movement was detected within the PICK_UP linking window."
        )

    return {
        "n_move_primitive_events":         n_moves,
        "n_interaction_primitive_events":  n_interactions,
        "n_pickup_operations":             n_pickup,
        "n_hold_operations":               n_hold,
        "move_events_missing":             move_missing,
        "near_threshold_tracks":           near_threshold_tracks,
        "summary":                         gaps,
    }


# ── Markdown renderers ────────────────────────────────────────────────────────

def _render_operation_md(bundle: dict) -> str:
    lines = [
        f"# Operation {bundle['operation_id']}: {bundle['operation_type']}",
        "",
        f"**Confidence:** {bundle['confidence']:.2f}  ",
        f"**Frames:** {bundle['frame_range'][0]}–{bundle['frame_range'][1]}  ",
        "",
        "## Explanation",
        "",
        bundle["explanation"],
        "",
        "## Involved Tracks",
        "",
    ]
    for t in bundle["involved_tracks"]:
        lines.append(
            f"- `{t['track_id']}` — class: **{t['semantic_class']}**, role: {t['object_role']}"
        )
    lines += [
        "",
        "## Primitive Evidence",
        "",
    ]
    if bundle["evidence_events"]:
        for ev in bundle["evidence_events"]:
            lines.append(
                f"- `{ev['event_id']}` ({ev['event_type']}) "
                f"frames {ev['frame_range'][0]}–{ev['frame_range'][1]} — "
                f"{ev['trigger_reason']} (conf={ev['confidence']:.2f})"
            )
    else:
        lines.append("_No linked primitive events._")
    lines += [
        "",
        "## Raw Notes",
        "",
        bundle.get("notes", ""),
        "",
        f"_Generated: {bundle['generated_at']}_",
    ]
    return "\n".join(lines)


def _render_session_md(review: dict) -> str:
    sid = review["session_id"]
    domain_name = review.get("domain_name")
    domain_line = f"**Domain:** {domain_name}  " if domain_name else "**Domain:** generic (no domain config)  "
    lines = [
        f"# Session Review — {sid}",
        "",
        domain_line,
        f"**Tracks:** {review['n_tracks']}  ",
        f"**Primitive events:** {review['n_primitive_events']}  ",
        f"**Operation events:** {review['n_operations']}  ",
        "",
        "## Workflow Phase",
        "",
    ]
    wf = review.get("workflow_phase")
    if wf:
        lines += [
            f"**Phase:** {wf['label']}  ",
            f"**Confidence:** {wf['confidence']:.2f}  ",
            f"**Evidence:** {wf['evidence']}  ",
            "",
            review.get("phase_explanation", ""),
        ]
    else:
        lines.append("_No workflow phase determined._")

    lines += [
        "",
        "## Operation Counts",
        "",
    ]
    for op_type, cnt in review.get("operation_counts", {}).items():
        lines.append(f"- **{op_type}:** {cnt}")

    lines += [
        "",
        "## Primitive Event Counts",
        "",
    ]
    for ev_type, cnt in review.get("primitive_event_counts", {}).items():
        lines.append(f"- **{ev_type}:** {cnt}")

    lines += [
        "",
        "## Manipulated Objects",
        "",
    ]
    manip = review.get("manipulated_objects", [])
    if manip:
        for m in manip:
            lines.append(f"- `{m['track_id']}` — {m['semantic_class']} ({m['object_role']})")
    else:
        lines.append("_No manipulated objects detected._")

    unresolved = review.get("unresolved_candidates", [])
    lines += [
        "",
        f"## Unresolved Candidates ({len(unresolved)})",
        "",
    ]
    if unresolved:
        for c in unresolved:
            lines.append(
                f"- `{c['operation_id']}` ({c['operation_type']}) "
                f"obj={c['object'] or '?'} conf={c['confidence']:.2f}: {c['notes']}"
            )
    else:
        lines.append("_No unresolved candidates._")

    # E3: Detection gap analysis
    gaps_info = review.get("detection_gaps", {})
    gap_msgs  = gaps_info.get("summary", [])
    lines += [
        "",
        "## Detection Gap Analysis",
        "",
        f"**MOVE events:** {gaps_info.get('n_move_primitive_events', '?')}  ",
        f"**INTERACTION events:** {gaps_info.get('n_interaction_primitive_events', '?')}  ",
        f"**PICK_UP detected:** {gaps_info.get('n_pickup_operations', '?')}  ",
        f"**HOLD detected:** {gaps_info.get('n_hold_operations', '?')}  ",
        "",
    ]
    if gap_msgs:
        for msg in gap_msgs:
            lines.append(f"- {msg}")
    else:
        lines.append("_No detection gaps identified._")

    near_thr = gaps_info.get("near_threshold_tracks", [])
    if near_thr:
        lines += ["", "### Tracks near MOVE threshold", ""]
        for t in near_thr:
            lines.append(
                f"- `{t['track_id']}` ({t['semantic_class']}/{t['object_role']}): "
                f"max {t['max_displacement_m']:.3f}m vs threshold {t['threshold_m']:.3f}m "
                f"(below by {t['below_by_m']:.3f}m)"
            )

    # E1: State changes
    sc = review.get("state_changes", {})
    per_track = sc.get("per_track_motion", [])
    lines += [
        "",
        "## Motion / State Changes",
        "",
        f"**Tracks with MOVE events:** {len(sc.get('tracks_with_move_events', []))}  ",
        f"**Total MOVE primitive events:** {sc.get('n_move_primitive_events', 0)}  ",
        "",
    ]
    if per_track:
        lines.append("| Track | Class | Role | MaxDisp(m) | Threshold(m) | FireCount |")
        lines.append("|-------|-------|------|------------|--------------|-----------|")
        for t in per_track:
            thr_str   = f"{t['move_threshold_m']:.3f}" if t["move_threshold_m"] is not None else "—"
            lines.append(
                f"| `{t['track_id']}` | {t['semantic_class']} | {t['object_role']} "
                f"| {t['max_displacement_m']:.3f} | {thr_str} | {t['steps_above_threshold']} |"
            )

    # E2: Workflow timeline
    wt = review.get("workflow_timeline", {})
    if wt.get("available"):
        lines += [
            "",
            "## Workflow Timeline",
            "",
            f"**Phases:** {wt['total_phases']}  ",
            f"**Dominant:** {wt['dominant_phase']}  ",
            f"**Sequence:** {' → '.join(wt.get('phase_sequence', []))}  ",
            f"**Has manipulation:** {wt['has_manipulation']}  ",
            f"**Has placement:** {wt['has_placement']}  ",
        ]
        transitions = wt.get("transitions", [])
        if transitions:
            lines += ["", "### Phase Transitions", ""]
            for tr in transitions:
                new_act = " *(new activity)*" if tr["is_new_activity"] else ""
                lines.append(f"- **{tr['from']}** → **{tr['to']}** (gap {tr['gap_s']}s){new_act}")

    return "\n".join(lines)


# ── Overlay frame copy ────────────────────────────────────────────────────────

def _copy_overlay_frames(
    op: "pd.Series",
    paths: "PipelinePaths",
    out_dir: Path,
    slug: str,
    max_frames: int,
) -> None:
    """Copy representative debug_box frames into the review directory."""
    try:
        import shutil
        start = int(op["start_frame_idx"])
        end   = int(op["end_frame_idx"])
        mid   = (start + end) // 2

        # Sample up to max_frames evenly across the window
        n = min(max_frames, end - start + 1)
        if n <= 1:
            candidates = [mid]
        else:
            step = max(1, (end - start) // (n - 1))
            candidates = list(range(start, end + 1, step))[:n]

        for f in candidates:
            src = paths.debug_box_dir / f"frame_{f:06d}_detections.png"
            if not src.exists():
                # Find nearest available
                available = sorted(paths.debug_box_dir.glob("frame_*_detections.png"))
                if not available:
                    return
                src = min(available, key=lambda p: abs(int(p.stem.split("_")[1]) - f))

            dst = out_dir / f"{slug}_f{f:06d}.png"
            shutil.copy2(src, dst)
    except Exception:
        pass   # Overlay frames are best-effort; don't fail the review build


# ── Helpers ───────────────────────────────────────────────────────────────────

def _notnull(val) -> bool:
    """Return True if val is not None/NaN/empty-string."""
    if val is None:
        return False
    try:
        import math
        if math.isnan(float(val)):
            return False
    except (TypeError, ValueError):
        pass
    return str(val) not in ("", "nan", "None")


if __name__ == "__main__":
    app()
