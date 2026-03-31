"""Scene State Package builder — normalised reasoning-layer input contract.

Produces a Scene State Package (SSP) from pipeline DataFrames, conforming to
the reasoning layer input contract schema v1.0.

The package is:
  - entity-centric       (one entry per persistent tracked object)
  - relation-centric     (explicit typed predicates with confidence + status)
  - temporally aware     (valid_time on every relation, time_window on header)
  - uncertainty-aware    (existence_confidence, pose_sigma, class_entropy)
  - provenance-preserving (provenance_refs trace every belief to its source)
  - representation-agnostic (reasoner never sees raw masks or detector output)

Contract compliance: Level 2 — Traceable (includes observations, hypotheses,
provenance, and constraints on top of the mandatory Level 1 fields).

The reasoning layer should treat the SSP as follows:
  - entities  : candidate world objects
  - relations : candidate facts, NOT guaranteed truth
  - confidence: relative strength, not strict probability unless declared
  - status    : controls trust level (observed / derived_upstream /
                hypothesized / rejected)
  - observations : explanatory support for traceability, not logic atoms
  - hypotheses   : promoted to relations when promotion_rule is satisfied
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.geometry import spatial_relation

# ── Contract constants ────────────────────────────────────────────────────────

SCHEMA_VERSION = "1.0"

# Relations with confidence below this threshold AND _CANDIDATE status are
# kept as hypotheses rather than promoted to accepted relations.
HYPOTHESIS_CONFIDENCE_THRESHOLD = 0.80

# A track whose most-recent frame is within this many frames of the session's
# last frame is considered currently "visible".
ACTIVE_FRAME_WINDOW = 5

# ── Controlled predicate vocabulary ──────────────────────────────────────────
# Maps pipeline event types to the contract's stable relation predicate set.
# Keeping this map here makes the reasoner independent of pipeline event names.

_EVENT_TO_PREDICATE: Dict[str, str] = {
    # Entity existence / visibility
    "APPEAR":                    "present",
    "DISAPPEAR":                 "occluded",
    "INSPECT":                   "visible",
    # Geometric / spatial (derived from trajectory)
    "MOVE":                      "moving",
    "PLACE":                     "contact_candidate",
    "CO_LOCATE":                 "near",
    "SEPARATE":                  "moving_away",
    # Action / interaction
    "INTERACTION":               "touching_candidate",
    # Procedural state candidates
    "ALIGN_CANDIDATE":           "aligned_candidate",
    "ATTACH_CANDIDATE":          "attached_candidate",
    "STATE_CHANGE_CANDIDATE":    "step_ready_candidate",
    "ASSEMBLY_CHANGE_CANDIDATE": "step_completed_candidate",
    "USE_TOOL_CANDIDATE":        "touching_candidate",
}

# Status reflects how the belief was established.
_EVENT_TO_STATUS: Dict[str, str] = {
    "APPEAR":                    "observed",
    "DISAPPEAR":                 "observed",
    "MOVE":                      "observed",
    "CO_LOCATE":                 "observed",
    "SEPARATE":                  "observed",
    "PLACE":                     "derived_upstream",
    "INTERACTION":               "derived_upstream",
    "INSPECT":                   "derived_upstream",
    "ALIGN_CANDIDATE":           "hypothesized",
    "ATTACH_CANDIDATE":          "hypothesized",
    "STATE_CHANGE_CANDIDATE":    "hypothesized",
    "ASSEMBLY_CHANGE_CANDIDATE": "hypothesized",
    "USE_TOOL_CANDIDATE":        "hypothesized",
}

# Human-readable source names for the provenance block.
_SOURCE_DISPLAY: Dict[str, str] = {
    "grounding_dino": "GroundingDINO",
    "yolo":           "YOLO",
    "depth_blobs":    "DepthBlobs",
}

# Spatial relation labels from geometry.spatial_relation() → contract predicate.
_GEOMETRY_TO_PREDICATE: Dict[str, Optional[str]] = {
    "NEAR":     "near",
    "ABOVE":    "above",
    "BELOW":    "below",
    "LEFT_OF":  "left_of",
    "RIGHT_OF": "right_of",
    "FAR":      None,   # FAR pairs are omitted — not salient
}


# ── Public API ────────────────────────────────────────────────────────────────

def build_scene_state_package(
    session_id: str,
    tracks_df: pd.DataFrame,
    obs_df: pd.DataFrame,
    events_df: pd.DataFrame,
    roles_df: pd.DataFrame,
    cfg: Dict[str, Any],
    thr: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble a Scene State Package from pipeline DataFrames.

    Parameters
    ----------
    session_id : str
        Session identifier (becomes scene_id in the package header).
    tracks_df : pd.DataFrame
        object_tracks.csv — one row per (track × frame) observation link.
    obs_df : pd.DataFrame
        object_observations.csv — one row per raw detector hit.
    events_df : pd.DataFrame
        events.csv — one row per detected event window.
    roles_df : pd.DataFrame
        event_object_roles.csv — track roles within each event.
    cfg : dict
        pipeline.yaml config dict.
    thr : dict
        thresholds.yaml config dict.

    Returns
    -------
    dict
        Full Level-2 Scene State Package ready for JSON serialisation.
    """
    now_utc = datetime.now(timezone.utc)

    # Anchor session timestamps to wall clock.
    # The package timestamp == now.  The session epoch is derived so that
    # the session's max relative timestamp maps to now.
    if not tracks_df.empty:
        min_ts_ns = int(tracks_df["timestamp_ns"].min())
        max_ts_ns = int(tracks_df["timestamp_ns"].max())
    else:
        min_ts_ns = max_ts_ns = 0

    session_epoch = now_utc - timedelta(seconds=max_ts_ns / 1e9)
    near_threshold_m = float(thr.get("events", {}).get("near_threshold_m", 0.3))

    # ── Build each contract section ───────────────────────────────────────────
    entities = _build_entities(
        tracks_df, obs_df, events_df, session_epoch, near_threshold_m
    )

    event_relations, hypotheses = _build_relations_from_events(
        events_df, tracks_df, session_epoch
    )

    live_relations = _build_live_spatial_relations(
        tracks_df, near_threshold_m, session_epoch,
        existing_count=len(event_relations),
    )

    all_relations = event_relations + live_relations

    observations = _build_observations(obs_df, tracks_df, session_epoch)

    state_summary = _build_state_summary(tracks_df, all_relations, events_df)
    provenance    = _build_provenance(obs_df, tracks_df, cfg)
    constraints   = _build_constraints(cfg, thr)

    # ── Assemble header ───────────────────────────────────────────────────────
    unique_frames = int(tracks_df["frame_idx"].nunique()) if not tracks_df.empty else 0

    return {
        "schema_version": SCHEMA_VERSION,
        "scene_id":        session_id,
        "timestamp":       _fmt_iso(now_utc),
        "time_window": {
            "start":             _ns_to_iso(min_ts_ns, session_epoch),
            "end":               _ns_to_iso(max_ts_ns, session_epoch),
            "frames_aggregated": unique_frames,
        },
        "entities":      entities,
        "relations":     all_relations,
        "hypotheses":    hypotheses,
        "observations":  observations,
        "state_summary": state_summary,
        "provenance":    provenance,
        "constraints":   constraints,
    }


def save_scene_state_package(pkg: Dict[str, Any], path: Path) -> None:
    """Serialise the package to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(pkg, f, indent=2)


def load_scene_state_package(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


# ── Section builders ──────────────────────────────────────────────────────────

def _build_entities(
    tracks_df: pd.DataFrame,
    obs_df: pd.DataFrame,
    events_df: pd.DataFrame,
    session_epoch: datetime,
    near_threshold_m: float,
) -> List[Dict]:
    """One entity per persistent track.

    Required contract fields:  entity_id, entity_type, existence_confidence
    Recommended fields:        class_label, geometry, identity_track,
                               state_tags, uncertainty, provenance_refs
    """
    if tracks_df.empty:
        return []

    global_max_frame = int(tracks_df["frame_idx"].max())

    # Confidence lookup: observation_id -> detection confidence
    conf_lookup: Dict[str, float] = {}
    if not obs_df.empty:
        for _, orow in obs_df.iterrows():
            oid = str(orow["observation_id"])
            raw = orow.get("confidence")
            conf_lookup[oid] = float(raw) if not _is_nan(raw) else 0.5

    # Tracks currently involved in an INTERACTION (= "held" state tag)
    held_tids: set = set()
    if not events_df.empty and "event_type" in events_df.columns:
        recent_interact = events_df[
            (events_df["event_type"] == "INTERACTION") &
            (events_df["end_frame_idx"] >= global_max_frame - ACTIVE_FRAME_WINDOW)
        ]
        for _, ev in recent_interact.iterrows():
            for tid in json.loads(ev["primary_track_ids"]):
                held_tids.add(tid)

    entities = []
    for tid, grp in tracks_df.groupby("track_id"):
        grp_s = grp.sort_values("timestamp_ns").reset_index(drop=True)
        sem_class = str(grp_s["semantic_class"].iloc[0])
        last_row  = grp_s.iloc[-1]

        # existence_confidence — mean detection score across all linked observations
        linked_oids = [str(v) for v in grp_s["observation_id"].dropna().tolist()]
        confs = [conf_lookup[o] for o in linked_oids if o in conf_lookup]
        existence_conf = round(float(np.mean(confs)), 3) if confs else 0.75

        # Geometry — last known pose + bounding-box dimensions
        position = [_f(last_row["x"]), _f(last_row["y"]), _f(last_row["z"])]
        dimensions = [
            _f(last_row.get("w")), _f(last_row.get("h")), _f(last_row.get("d"))
        ]

        # Uncertainty — positional spread across the track's lifetime
        xs = grp_s["x"].dropna().values.astype(float)
        ys = grp_s["y"].dropna().values.astype(float)
        zs = grp_s["z"].dropna().values.astype(float)
        pose_sigma = [
            round(float(np.std(xs)), 3) if len(xs) > 1 else 0.05,
            round(float(np.std(ys)), 3) if len(ys) > 1 else 0.05,
            round(float(np.std(zs)), 3) if len(zs) > 1 else 0.05,
        ]

        # State tags
        state_tags: List[str] = []
        if int(grp_s["frame_idx"].max()) >= global_max_frame - ACTIVE_FRAME_WINDOW:
            state_tags.append("visible")
        else:
            state_tags.append("absent")

        # Stationary: max step displacement in the last 5 positions
        positions = np.column_stack([xs, ys, zs]) if len(xs) > 1 else None
        if positions is not None and len(positions) >= 2:
            steps = np.linalg.norm(np.diff(positions[-5:], axis=0), axis=1)
            if steps.max() < 0.05:
                state_tags.append("stationary")

        if tid in held_tids:
            state_tags.append("held")

        # Provenance refs — observation_ids already carry their own prefix
        prov_refs = linked_oids[:10]

        entities.append({
            "entity_id":             tid,
            "entity_type":           "hand" if sem_class == "hands" else "object",
            "class_label":           sem_class,
            "existence_confidence":  existence_conf,
            "geometry": {
                "representation_type": "bounding_box_3d",
                "pose": {
                    "position": position,
                },
                "dimensions": dimensions,
            },
            "identity_track": {
                "track_id":          tid,
                "persistence_frames": int(grp_s["frame_idx"].nunique()),
            },
            "state_tags":    state_tags,
            "uncertainty": {
                "pose_sigma":    pose_sigma,
                # class_entropy is 0: class_must_match=True enforces a single
                # semantic class per track throughout its lifetime.
                "class_entropy": 0.0,
            },
            "provenance_refs": prov_refs,
        })

    return entities


def _build_relations_from_events(
    events_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    session_epoch: datetime,
) -> Tuple[List[Dict], List[Dict]]:
    """Map pipeline events to contract relations and hypotheses.

    The status field is critical: it tells the reasoner whether a relation is
    hard truth (observed), computed geometry (derived_upstream), or a candidate
    that needs further evidence (hypothesized).

    Returns
    -------
    (relations, hypotheses)
    """
    if events_df.empty:
        return [], []

    # Map track_id -> observation_ids for provenance propagation
    # observation_ids already carry their own prefix (e.g. "obs_e6c5bf83")
    track_obs_refs: Dict[str, List[str]] = {}
    if not tracks_df.empty:
        for tid, grp in tracks_df.groupby("track_id"):
            refs = [str(v) for v in grp["observation_id"].dropna().tolist()[:5]]
            track_obs_refs[tid] = refs

    relations: List[Dict] = []
    hypotheses: List[Dict] = []
    rel_idx = 0
    hyp_idx = 0

    for _, ev in events_df.iterrows():
        etype      = str(ev["event_type"])
        predicate  = _EVENT_TO_PREDICATE.get(etype, etype.lower())
        status     = _EVENT_TO_STATUS.get(etype, "derived_upstream")
        confidence = float(ev.get("confidence", 0.7))
        args       = json.loads(ev["primary_track_ids"])

        # Aggregate provenance refs from all involved tracks (deduped, capped)
        prov_refs: List[str] = []
        for tid in args:
            prov_refs.extend(track_obs_refs.get(tid, []))
        prov_refs = list(dict.fromkeys(prov_refs))[:6]

        valid_time = {
            "start": _ns_to_iso(int(ev["start_ts_ns"]), session_epoch),
            "end":   _ns_to_iso(int(ev["end_ts_ns"]),   session_epoch),
        }

        # Decide: accepted relation or hypothesis.
        # _CANDIDATE events and any low-confidence pairwise event go to hypotheses.
        goes_to_hypothesis = (
            status == "hypothesized"
            or (confidence < HYPOTHESIS_CONFIDENCE_THRESHOLD and status != "observed")
        )

        if goes_to_hypothesis:
            hyp_idx += 1
            hyp: Dict[str, Any] = {
                "hypothesis_id":   f"hyp_{hyp_idx:04d}",
                "predicate":       predicate,
                "arguments":       args,
                "confidence":      round(confidence, 3),
                "support_evidence": prov_refs,
                "valid_time":      valid_time,
                "source_event_id": ev["event_id"],
            }
            if confidence < HYPOTHESIS_CONFIDENCE_THRESHOLD:
                hyp["promotion_rule"] = (
                    f"promote_if_confidence_above_{HYPOTHESIS_CONFIDENCE_THRESHOLD}"
                    "_sustained_for_10_frames"
                )
            hypotheses.append(hyp)

        else:
            rel_idx += 1

            # Extract numeric distance from trigger_reason if present
            qualifiers: Dict[str, Any] = {}
            trigger = str(ev.get("trigger_reason", ""))
            m = re.search(r"([\d.]+)\s*m", trigger)
            if m:
                qualifiers["distance_m"] = float(m.group(1))

            rel: Dict[str, Any] = {
                "relation_id": f"rel_{rel_idx:04d}",
                "predicate":   predicate,
                "arguments":   args,
                "confidence":  round(confidence, 3),
                "status":      status,
                "valid_time":  valid_time,
                "provenance_refs": prov_refs,
            }
            if qualifiers:
                rel["qualifiers"] = qualifiers
            relations.append(rel)

    return relations, hypotheses


def _build_live_spatial_relations(
    tracks_df: pd.DataFrame,
    near_threshold_m: float,
    session_epoch: datetime,
    existing_count: int,
) -> List[Dict]:
    """Compute a current-frame spatial snapshot between all visible entity pairs.

    These relations carry status='derived_upstream' because they are computed
    from last-known positions, not directly observed by a detector.
    """
    if tracks_df.empty:
        return []

    # Latest known position per track
    latest: Dict[str, Dict] = {}
    for tid, grp in tracks_df.groupby("track_id"):
        last = grp.sort_values("timestamp_ns").iloc[-1]
        pos = [float(last["x"]), float(last["y"]), float(last["z"])]
        if any(np.isnan(p) for p in pos):
            continue
        latest[tid] = {"pos": pos, "ts_ns": int(last["timestamp_ns"])}

    relations: List[Dict] = []
    tids = list(latest.keys())
    idx = existing_count

    for i, tid_a in enumerate(tids):
        for tid_b in tids[i + 1:]:
            idx += 1
            pos_a = np.array(latest[tid_a]["pos"])
            pos_b = np.array(latest[tid_b]["pos"])
            dist  = float(np.linalg.norm(pos_b - pos_a))

            raw_rel  = spatial_relation(pos_a, pos_b, threshold_m=near_threshold_m)
            predicate = _GEOMETRY_TO_PREDICATE.get(raw_rel)
            if predicate is None:
                continue  # FAR pairs are not salient — skip

            # Confidence decays linearly with distance (floor 0.30)
            confidence = round(max(0.30, 1.0 - dist / 3.0), 3)

            ts_ns = max(latest[tid_a]["ts_ns"], latest[tid_b]["ts_ns"])
            ts_iso = _ns_to_iso(ts_ns, session_epoch)

            relations.append({
                "relation_id": f"rel_{idx:04d}",
                "predicate":   predicate,
                "arguments":   [tid_a, tid_b],
                "confidence":  confidence,
                "status":      "derived_upstream",
                "qualifiers": {
                    "distance_m":     round(dist, 3),
                    "tolerance_used": near_threshold_m,
                },
                "valid_time": {
                    "start": ts_iso,
                    "end":   ts_iso,
                },
                "uncertainty": {
                    "kind": "geometric_threshold",
                },
                "provenance_refs": [],
            })

    return relations


def _build_observations(
    obs_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    session_epoch: datetime,
) -> List[Dict]:
    """Wrap raw detector hits as contract Observation records.

    These are optional for the reasoner during inference but are essential for
    explainability: every relation and entity can be traced back to them.
    """
    if obs_df.empty:
        return []

    # Reverse map: observation_id -> list of track_ids that consumed it
    obs_to_tracks: Dict[str, List[str]] = {}
    if not tracks_df.empty and "observation_id" in tracks_df.columns:
        for _, trow in tracks_df.iterrows():
            oid = str(trow["observation_id"])
            tid = str(trow["track_id"])
            obs_to_tracks.setdefault(oid, []).append(tid)

    observations: List[Dict] = []
    for _, row in obs_df.iterrows():
        oid        = str(row["observation_id"])
        source_raw = str(row.get("source", "unknown"))
        ts_ns      = int(row["timestamp_ns"]) if not _is_nan(row.get("timestamp_ns")) else 0
        conf       = row.get("confidence")

        observations.append({
            "observation_id": oid,   # already prefixed e.g. "obs_e6c5bf83"
            "source_type":    source_raw,
            "source_name":    _SOURCE_DISPLAY.get(source_raw, source_raw),
            "timestamp":      _ns_to_iso(ts_ns, session_epoch),
            "about_entities": obs_to_tracks.get(oid, []),
            "payload": {
                "frame_idx":       int(row["frame_idx"]) if not _is_nan(row.get("frame_idx")) else 0,
                "semantic_class":  str(row["semantic_class"]),
                "confidence":      round(float(conf), 3) if not _is_nan(conf) else 0.5,
                "position_world":  [_f(row["x"]), _f(row["y"]), _f(row["z"])],
            },
        })

    return observations


def _build_state_summary(
    tracks_df: pd.DataFrame,
    relations: List[Dict],
    events_df: pd.DataFrame,
) -> Dict:
    """Compact scene snapshot — aids debugging and fast reasoning bootstrapping."""
    if tracks_df.empty:
        return {}

    global_max_frame = int(tracks_df["frame_idx"].max())

    # Active entities: tracks visible in the last ACTIVE_FRAME_WINDOW frames
    active_tids: List[str] = [
        tid for tid, grp in tracks_df.groupby("track_id")
        if int(grp["frame_idx"].max()) >= global_max_frame - ACTIVE_FRAME_WINDOW
    ]

    # Phase candidates: dominant event types in the last 20 % of the session
    phase_candidates: List[Dict] = []
    if not events_df.empty:
        max_ts  = int(events_df["end_ts_ns"].max())
        cutoff  = int(max_ts * 0.80)
        recent  = events_df[events_df["end_ts_ns"] >= cutoff]
        if not recent.empty:
            for etype, count in recent["event_type"].value_counts().head(3).items():
                phase_candidates.append({
                    "label":      etype.lower(),
                    "confidence": round(count / len(recent), 2),
                })

    # Salient relations: top 5 distinct predicate+args by confidence
    sorted_rels = sorted(relations, key=lambda r: r.get("confidence", 0), reverse=True)
    seen: set = set()
    salient: List[str] = []
    for r in sorted_rels:
        key = "{pred}({args})".format(
            pred=r["predicate"],
            args=",".join(str(a) for a in r.get("arguments", [])),
        )
        if key not in seen:
            seen.add(key)
            salient.append(key)
        if len(salient) == 5:
            break

    return {
        "current_phase_candidates": phase_candidates,
        "active_entities":          active_tids,
        "salient_relations":        salient,
    }


def _build_provenance(
    obs_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    cfg: Dict,
) -> Dict:
    """Global provenance: how the package was constructed."""
    sources: List[str] = []
    if not obs_df.empty and "source" in obs_df.columns:
        for src in obs_df["source"].dropna().unique():
            display = _SOURCE_DISPLAY.get(str(src), str(src))
            if display not in sources:
                sources.append(display)

    pipeline_steps = sources + ["SpatialTracker", "SceneStatePackageBuilder"]

    frame_ids: List[int] = (
        sorted(int(v) for v in tracks_df["frame_idx"].unique().tolist())
        if not tracks_df.empty else []
    )

    return {
        "pipeline":          pipeline_steps,
        "source_modalities": ["rgb", "depth"],
        "frame_ids":         frame_ids,
    }


def _build_constraints(cfg: Dict, thr: Dict) -> Dict:
    """Pass upstream assumptions and hard context to the reasoning layer."""
    detection_prompt = cfg.get("detection_prompt", "")
    expected_types = [
        t.strip().rstrip(".").strip()
        for t in detection_prompt.split(".")
        if t.strip()
    ]

    return {
        "reference_frame":       "world_frame",
        "task_context":          cfg.get("session_id", "unknown_session"),
        "expected_entity_types": expected_types,
        "tolerance_profile":     "coarse_rgbd",
        "near_threshold_m":      float(thr.get("events", {}).get("near_threshold_m", 0.3)),
    }


# ── Utilities ─────────────────────────────────────────────────────────────────

def _ns_to_iso(ts_ns: int, session_epoch: datetime) -> str:
    """Convert a relative-nanosecond timestamp to ISO 8601 wall-clock string."""
    dt = session_epoch + timedelta(seconds=ts_ns / 1e9)
    return _fmt_iso(dt)


def _fmt_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _f(val: Any) -> float:
    """Safe float conversion; returns 0.0 for None / NaN."""
    if val is None:
        return 0.0
    try:
        v = float(val)
        return 0.0 if v != v else v   # NaN check
    except (TypeError, ValueError):
        return 0.0


def _is_nan(val: Any) -> bool:
    if val is None:
        return True
    try:
        return float(val) != float(val)
    except (TypeError, ValueError):
        return True
