"""workflow_queries.py — Workflow-layer query answering.

Routes natural-language questions to the appropriate data sources (operation
events CSV, scene state package, EGG graph, workflow timeline) and returns a
human-readable string answer.

This module is used by scripts/12_demo_queries.py and is importable for tests.

Supported query topics
----------------------
"What step is happening now?"           — active operations from SSP / ops_df
"What object is being manipulated?"     — highest-confidence op with workpiece
"What changed in the scene?"            — MOVE events + change-type ops
"Which operation has the strongest evidence?" — by confidence score
"What is the current workflow phase?"   — workflow_phase from SSP / timeline
"Why do you think this step is happening?"   — evidence chain for active phase
"Show the evidence for the current workflow phase" — evidence event list
"Which tracks contributed to this operation?"  — agent/object track IDs
"What candidate operations were considered but not promoted?" — CANDIDATE ops
"What phase transition just happened?"  — last transition from timeline
"What happened before this phase?"      — previous phase from timeline
"How many phases were there?"           — phase count from timeline
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import pandas as pd


# ── Public API ────────────────────────────────────────────────────────────────

def answer_workflow_query(
    query: str,
    ops_df: "Optional[pd.DataFrame]",
    ssp: "Optional[Dict[str, Any]]",
    graph: "Optional[Dict[str, Any]]" = None,
    timeline: "Optional[Dict[str, Any]]" = None,
) -> str:
    """Route a natural-language query and return a string answer.

    Parameters
    ----------
    query    : natural language question
    ops_df   : operation_events.csv as a DataFrame, or None
    ssp      : scene_state_package dict, or None
    graph    : EGG graph dict (for MOVE-event context), or None
    timeline : workflow_timeline.json dict (Phase 3), or None

    Returns
    -------
    A plain-text answer string.
    """
    graph    = graph or {}
    timeline = timeline or {}
    q = query.lower().strip()

    # ── "Why do you think this step is happening?" — must precede "step" check
    if "why" in q:
        return _why_this_step(ops_df, ssp)

    # ── "What step is happening now?" ────────────────────────────────────────
    if "step" in q or "happening now" in q:
        return _active_operations(ops_df, ssp)

    # ── "What object is being manipulated?" ──────────────────────────────────
    if "manipulat" in q or "object is being" in q:
        return _manipulated_object(ops_df)

    # ── "What changed in the scene?" ─────────────────────────────────────────
    if "changed" in q:
        return _scene_changes(ops_df, graph)

    # ── "Which operation has the strongest evidence?" / "best" ───────────────
    if ("strongest" in q or "best" in q) and ("evidence" in q or "operation" in q):
        return _strongest_evidence(ops_df)

    # ── "Show the evidence for …" or "evidence for the current workflow phase"
    if "evidence" in q:
        return _evidence_for_phase(ops_df, ssp)

    # ── Timeline-aware queries ────────────────────────────────────────────────
    if "transition" in q:
        return _last_phase_transition(timeline)

    if "before" in q and "phase" in q:
        return _previous_phase(timeline)

    if ("how many" in q or "count" in q) and "phase" in q:
        return _phase_count(timeline, ops_df)

    # ── "What is the current workflow phase?" ────────────────────────────────
    if "workflow" in q or "phase" in q:
        return _workflow_phase(ops_df, ssp, timeline)

    # ── "Which tracks contributed to this operation?" ────────────────────────
    if "track" in q and ("contribut" in q or "operation" in q):
        return _contributing_tracks(ops_df)

    # ── "What candidate operations were considered but not promoted?" ─────────
    if "candidate" in q or ("not promoted" in q):
        return _candidate_operations(ops_df)

    return "Query not specifically matched."


# ── Query handlers ────────────────────────────────────────────────────────────

def _active_operations(
    ops_df: Optional[pd.DataFrame],
    ssp: Optional[Dict],
) -> str:
    if ssp:
        active_ops = ssp.get("state_summary", {}).get("active_operations", [])
        if active_ops:
            items = [
                f"{op['operation_type']} (agent={op['agent'] or '?'}, "
                f"obj={op['object'] or '?'}, conf={op['confidence']:.2f})"
                for op in active_ops
            ]
            return "Active: " + "; ".join(items)
        wf = ssp.get("state_summary", {}).get("workflow_phase")
        if wf:
            return (
                f"No operations active in the final frames, but the "
                f"dominant phase was '{wf['label']}' (conf={wf['confidence']:.2f})."
            )
    if ops_df is not None and not ops_df.empty:
        last_op = ops_df.sort_values("end_frame_idx", ascending=False).iloc[0]
        return (
            f"Most recent operation: {last_op['operation_type']} "
            f"(frame {last_op['end_frame_idx']}, conf={last_op['confidence']:.2f})."
        )
    return "No operation events available. Run 10b first."


def _manipulated_object(ops_df: Optional[pd.DataFrame]) -> str:
    if ops_df is not None and not ops_df.empty:
        best = ops_df.dropna(subset=["object_track_id"]).sort_values(
            "confidence", ascending=False
        ).head(1)
        if not best.empty:
            r = best.iloc[0]
            return (
                f"Track '{r['object_track_id']}' — involved in "
                f"{r['operation_type']} "
                f"(frames {r['start_frame_idx']}–{r['end_frame_idx']}, "
                f"conf={r['confidence']:.2f})."
            )
    return "No manipulation events detected."


def _scene_changes(
    ops_df: Optional[pd.DataFrame],
    graph: Dict,
) -> str:
    changes: List[str] = []
    # From graph: MOVE events
    move_objs = [
        o["semantic_class"]
        for e in graph.get("events", []) if e["event_type"] == "MOVE"
        for edge in graph.get("event_edges", []) if edge["event_id"] == e["event_id"]
        for o in graph.get("objects", []) if o["track_id"] == edge["track_id"]
    ]
    if move_objs:
        changes.append(f"Moved: {', '.join(sorted(set(move_objs)))}")
    # From ops: change-type operations
    if ops_df is not None and not ops_df.empty:
        change_ops = ops_df[
            ops_df["operation_type"].isin(
                ["PICK_UP", "PUT_DOWN", "CONTACT", "TRANSFER",
                 "PICK_UP_CANDIDATE", "PUT_DOWN_CANDIDATE"]
            )
        ]
        if not change_ops.empty:
            op_summary = change_ops["operation_type"].value_counts()
            changes.append(
                "Operations: " + ", ".join(
                    f"{cnt}×{ot}" for ot, cnt in op_summary.items()
                )
            )
    return "; ".join(changes) if changes else "No significant changes detected."


def _strongest_evidence(ops_df: Optional[pd.DataFrame]) -> str:
    if ops_df is not None and not ops_df.empty:
        best = ops_df.sort_values("confidence", ascending=False).iloc[0]
        ev_ids = best.get("evidence_event_ids", "[]")
        n_evidence = len(json.loads(ev_ids) if isinstance(ev_ids, str) else [])
        return (
            f"{best['operation_type']} (id={best['operation_id']}) — "
            f"conf={best['confidence']:.2f}, "
            f"{n_evidence} evidence event(s). "
            f"Notes: {best['notes']}"
        )
    return "No operation events available."


def _workflow_phase(
    ops_df: Optional[pd.DataFrame],
    ssp: Optional[Dict],
    timeline: Optional[Dict] = None,
) -> str:
    # Prefer timeline if available (most complete)
    if timeline and timeline.get("phases"):
        summary = timeline.get("summary", {})
        dominant = summary.get("dominant_phase", "idle")
        sequence = summary.get("phase_sequence", [])
        n_phases  = summary.get("total_phases", 0)
        return (
            f"Timeline: {n_phases} phase(s). "
            f"Dominant: '{dominant}'. "
            f"Sequence: {' → '.join(sequence) if sequence else '(none)'}."
        )
    if ssp:
        wf = ssp.get("state_summary", {}).get("workflow_phase")
        if wf:
            return (
                f"Phase: '{wf['label']}' "
                f"(confidence={wf['confidence']:.2f}, {wf['evidence']})."
            )
    if ops_df is not None and not ops_df.empty:
        dominant = ops_df["operation_type"].value_counts().idxmax()
        return (
            f"Dominant operation type: {dominant} "
            f"({ops_df['operation_type'].value_counts()[dominant]} occurrences). "
            "Run 10c for full workflow timeline analysis."
        )
    return "No operation events, SSP, or timeline available."


def _why_this_step(
    ops_df: Optional[pd.DataFrame],
    ssp: Optional[Dict],
) -> str:
    """Explain the evidence chain behind the current workflow phase."""
    parts: List[str] = []

    if ssp:
        wf = ssp.get("state_summary", {}).get("workflow_phase")
        if wf:
            parts.append(
                f"The dominant phase is '{wf['label']}' because {wf['evidence']} "
                f"(confidence={wf['confidence']:.2f})."
            )
        active = ssp.get("state_summary", {}).get("active_operations", [])
        if active:
            descs = [
                f"{op['operation_type']} of {op['object'] or 'unknown'} "
                f"by {op['agent'] or 'unknown'}"
                for op in active
            ]
            parts.append("Active supporting operations: " + "; ".join(descs) + ".")

    if ops_df is not None and not ops_df.empty:
        # Show the top-2 ops by confidence with their notes
        top = ops_df.sort_values("confidence", ascending=False).head(2)
        evidence_lines = [
            f"  • {r['operation_type']} (conf={r['confidence']:.2f}): {r['notes']}"
            for _, r in top.iterrows()
        ]
        parts.append("Top evidence:\n" + "\n".join(evidence_lines))

    return "\n".join(parts) if parts else "No evidence available."


def _evidence_for_phase(
    ops_df: Optional[pd.DataFrame],
    ssp: Optional[Dict],
) -> str:
    """List the primitive event IDs that support the current workflow phase."""
    if ops_df is None or ops_df.empty:
        return "No operation events available."

    # Find operations that match the dominant phase
    dominant = ops_df["operation_type"].value_counts().idxmax()
    phase_ops = ops_df[ops_df["operation_type"] == dominant]

    all_ev_ids: List[str] = []
    for _, row in phase_ops.iterrows():
        ev_raw = row.get("evidence_event_ids", "[]")
        try:
            all_ev_ids.extend(json.loads(ev_raw) if isinstance(ev_raw, str) else [])
        except Exception:
            pass

    unique_ev = list(dict.fromkeys(all_ev_ids))
    lines = [
        f"Phase '{dominant}' supported by {len(phase_ops)} operation(s), "
        f"{len(unique_ev)} primitive event(s):",
    ]
    for eid in unique_ev[:10]:
        lines.append(f"  • {eid}")
    if len(unique_ev) > 10:
        lines.append(f"  … and {len(unique_ev) - 10} more.")
    return "\n".join(lines)


def _contributing_tracks(ops_df: Optional[pd.DataFrame]) -> str:
    """List all track IDs that appear as agent or object in operations."""
    if ops_df is None or ops_df.empty:
        return "No operation events available."

    agents   = set(ops_df["agent_track_id"].dropna().astype(str).tolist())
    objects  = set(ops_df["object_track_id"].dropna().astype(str).tolist())
    combined = agents | objects

    lines = [f"{len(combined)} track(s) contributed to detected operations:"]
    for tid in sorted(combined):
        roles: List[str] = []
        if tid in agents:
            roles.append("agent")
        if tid in objects:
            roles.append("object")
        op_types = sorted(set(
            ops_df[
                (ops_df["agent_track_id"].astype(str) == tid) |
                (ops_df["object_track_id"].astype(str) == tid)
            ]["operation_type"].tolist()
        ))
        lines.append(
            f"  • {tid} [{', '.join(roles)}] — "
            f"{', '.join(op_types)}"
        )
    return "\n".join(lines)


def _last_phase_transition(timeline: Optional[Dict]) -> str:
    """Return the most recent phase transition from the workflow timeline."""
    if not timeline:
        return "No workflow timeline available. Run 10c first."
    transitions = timeline.get("phase_transitions", [])
    if not transitions:
        return "No phase transitions recorded (only one phase or no operations)."
    last = transitions[-1]
    return (
        f"Last transition: '{last['from_label']}' → '{last['to_label']}' "
        f"(gap {last['gap_ns'] / 1e9:.1f}s). {last['evidence']}"
    )


def _previous_phase(timeline: Optional[Dict]) -> str:
    """Return the phase that occurred before the current (last) phase."""
    if not timeline:
        return "No workflow timeline available. Run 10c first."
    phases = timeline.get("phases", [])
    if not phases:
        return "No phases in timeline."
    if len(phases) < 2:
        return f"Only one phase recorded: '{phases[0]['label']}'. No previous phase."
    current  = phases[-1]
    previous = phases[-2]
    return (
        f"Previous phase: '{previous['label']}' "
        f"(frames {previous['start_frame_idx']}–{previous['end_frame_idx']}, "
        f"conf={previous['confidence']:.2f}). "
        f"Current: '{current['label']}' "
        f"(frames {current['start_frame_idx']}–{current['end_frame_idx']})."
    )


def _phase_count(timeline: Optional[Dict], ops_df: Optional[pd.DataFrame]) -> str:
    """Return how many phases were identified in the session."""
    if timeline and timeline.get("phases") is not None:
        n = len(timeline["phases"])
        seq = timeline.get("summary", {}).get("phase_sequence", [])
        return (
            f"{n} phase(s) detected in this session. "
            f"Sequence: {' → '.join(seq) if seq else '(none)'}."
        )
    if ops_df is not None and not ops_df.empty:
        return (
            "Timeline not built yet (run 10c). "
            f"Found {len(ops_df)} operation events spanning "
            f"frames {int(ops_df['start_frame_idx'].min())}–"
            f"{int(ops_df['end_frame_idx'].max())}."
        )
    return "No timeline or operation events available."


def _candidate_operations(ops_df: Optional[pd.DataFrame]) -> str:
    """List CANDIDATE operations that were not promoted to full operations."""
    if ops_df is None or ops_df.empty:
        return "No operation events available."

    candidates = ops_df[
        ops_df["operation_type"].str.endswith("_CANDIDATE", na=False)
    ]
    if candidates.empty:
        return "No candidate operations recorded (all detections were promoted or no candidates exist)."

    lines = [f"{len(candidates)} candidate operation(s) detected but not promoted:"]
    for _, row in candidates.iterrows():
        lines.append(
            f"  • {row['operation_type']} (id={row['operation_id']}, "
            f"obj={row['object_track_id'] or '?'}, "
            f"conf={row['confidence']:.2f}, "
            f"frames={row['start_frame_idx']}–{row['end_frame_idx']}): "
            f"{row['notes']}"
        )
    return "\n".join(lines)
