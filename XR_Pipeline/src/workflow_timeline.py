"""workflow_timeline.py — Session-level workflow timeline construction (Phase 3).

Transforms a flat list of operation events into a structured timeline of
workflow phases, enabling the pipeline to answer session-level questions like:
  "What phase happened before this?"
  "What changed between phase 2 and phase 3?"
  "What is the evidence for the current phase?"

Phase segmentation strategy
-----------------------------
1.  Sort operations by start_ts_ns.
2.  Group temporally adjacent operations into clusters (gap-based segmentation).
    A new cluster starts when the gap between consecutive operations exceeds
    phase_gap_ns (default 3 s).
3.  Label each cluster by its dominant operation type using a priority mapping.
4.  Transitions between clusters are recorded with evidence.

Phase labels (priority order, first match wins)
------------------------------------------------
manipulation  — PICK_UP, PUT_DOWN
hold          — HOLD
tool_use      — USE_TOOL
placement     — PLACE_ONTO_CANDIDATE, INSERT_CANDIDATE, ALIGN_CANDIDATE, ATTACH_CANDIDATE
approach      — APPROACH
transfer      — TRANSFER, PICK_UP_CANDIDATE, PUT_DOWN_CANDIDATE
contact       — CONTACT
idle          — (no operations in window)

Output artifacts
----------------
workflow_timeline.json  — full timeline with phases + transitions + summary
workflow_timeline.csv   — one row per phase (for downstream queries)
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# ── Phase label priority ──────────────────────────────────────────────────────

# Map each operation type to a phase label.  Lower number = higher priority.
_OP_TO_PHASE: Dict[str, Tuple[str, int]] = {
    "PICK_UP":              ("manipulation", 0),
    "PUT_DOWN":             ("manipulation", 0),
    "HOLD":                 ("hold",         1),
    "USE_TOOL":             ("tool_use",     2),
    "PLACE_ONTO_CANDIDATE": ("placement",    3),
    "INSERT_CANDIDATE":     ("placement",    3),
    "ALIGN_CANDIDATE":      ("placement",    3),
    "ATTACH_CANDIDATE":     ("placement",    3),
    "APPROACH":             ("approach",     4),
    "TRANSFER":             ("transfer",     5),
    "PICK_UP_CANDIDATE":    ("transfer",     5),
    "PUT_DOWN_CANDIDATE":   ("transfer",     5),
    "CONTACT":              ("contact",      6),
}

_PHASE_GAP_NS_DEFAULT = 3_000_000_000  # 3 seconds


# ── Public API ────────────────────────────────────────────────────────────────

def build_workflow_timeline(
    ops_df: pd.DataFrame,
    thr: Optional[Dict[str, Any]] = None,
    session_id: str = "unknown",
    domain_config=None,  # Optional[DomainConfig] — shapes phase labels and adds domain_name to summary
) -> Dict[str, Any]:
    """Build a structured workflow timeline from operation events.

    Parameters
    ----------
    ops_df :     operation_events.csv as a DataFrame (may be empty).
    thr :        thresholds dict (for phase_gap_ns override).
    session_id : session identifier for provenance.

    Returns
    -------
    dict with keys: schema_version, session_id, phases, phase_transitions, summary.
    """
    thr = thr or {}
    phase_gap_ns = int(
        thr.get("operation_events", {}).get("phase_gap_ns", _PHASE_GAP_NS_DEFAULT)
    )

    # D2: extract domain metadata for labeling and summary
    domain_name: Optional[str] = None
    domain_phase_labels: Optional[set] = None
    if domain_config is not None:
        domain_name = domain_config.domain_name
        _labels = domain_config.phase_labels()
        if _labels:
            domain_phase_labels = set(_labels)

    if ops_df is None or ops_df.empty:
        tl = _empty_timeline(session_id)
        tl["summary"]["domain_name"] = domain_name
        return tl

    ops_sorted = ops_df.sort_values("start_ts_ns").reset_index(drop=True)

    # ── Cluster operations into temporal groups ───────────────────────────────
    clusters: List[List[Dict]] = []
    current_cluster: List[Dict] = []
    prev_end_ns = None

    for _, row in ops_sorted.iterrows():
        row_dict = row.to_dict()
        start_ns = int(row["start_ts_ns"])
        if prev_end_ns is not None and (start_ns - prev_end_ns) > phase_gap_ns:
            clusters.append(current_cluster)
            current_cluster = []
        current_cluster.append(row_dict)
        prev_end_ns = max(prev_end_ns or 0, int(row["end_ts_ns"]))

    if current_cluster:
        clusters.append(current_cluster)

    # ── Build phase list ──────────────────────────────────────────────────────
    phases: List[Dict[str, Any]] = []
    phase_counter = 0

    for cluster in clusters:
        phase_counter += 1
        label, confidence, dominant_op = _label_cluster(cluster, domain_phase_labels=domain_phase_labels)

        start_f = min(op["start_frame_idx"] for op in cluster)
        end_f   = max(op["end_frame_idx"]   for op in cluster)
        start_ns = min(int(op["start_ts_ns"]) for op in cluster)
        end_ns   = max(int(op["end_ts_ns"])   for op in cluster)

        op_ids = [str(op["operation_id"]) for op in cluster]
        op_types = list({op["operation_type"] for op in cluster})

        # Collect manipulated tracks (objects that were acted on)
        object_tracks = list({
            str(op["object_track_id"])
            for op in cluster
            if op.get("object_track_id") and str(op["object_track_id"]) != "nan"
        })

        phases.append({
            "phase_id":             f"phase_{phase_counter:04d}",
            "label":                label,
            "start_frame_idx":      start_f,
            "end_frame_idx":        end_f,
            "start_ts_ns":          start_ns,
            "end_ts_ns":            end_ns,
            "confidence":           round(confidence, 3),
            "dominant_operation":   dominant_op,
            "operation_types":      op_types,
            "supporting_operations": op_ids,
            "object_tracks":        object_tracks,
            "evidence":             _phase_evidence(cluster, label),
            "previous_phase_id":    f"phase_{phase_counter - 1:04d}" if phase_counter > 1 else None,
        })

    # ── Build transitions ─────────────────────────────────────────────────────
    transitions: List[Dict[str, Any]] = []
    for i in range(len(phases) - 1):
        a = phases[i]
        b = phases[i + 1]
        gap_ns = b["start_ts_ns"] - a["end_ts_ns"]
        transitions.append({
            "from_phase_id": a["phase_id"],
            "to_phase_id":   b["phase_id"],
            "from_label":    a["label"],
            "to_label":      b["label"],
            "gap_ns":        gap_ns,
            "is_new_activity": gap_ns > phase_gap_ns,
            "evidence": (
                f"Phase '{a['label']}' ended at frame {a['end_frame_idx']}, "
                f"'{b['label']}' started at frame {b['start_frame_idx']} "
                f"(gap {gap_ns / 1e9:.1f}s)."
            ),
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    all_objects = list({
        t for p in phases for t in p["object_tracks"]
    })
    candidate_count = sum(
        1 for _, row in ops_df.iterrows()
        if "_CANDIDATE" in str(row.get("operation_type", ""))
    )
    # Weight dominant_phase by total operation count per label, not phase count.
    phase_labels = [p["label"] for p in phases]
    op_count_by_label: Dict[str, int] = {}
    for p in phases:
        label = p["label"]
        op_count_by_label[label] = (
            op_count_by_label.get(label, 0) + len(p["supporting_operations"])
        )
    dominant_phase = max(op_count_by_label, key=op_count_by_label.get) if op_count_by_label else "idle"

    summary = {
        "total_phases":          len(phases),
        "dominant_phase":        dominant_phase,
        "phase_sequence":        phase_labels,
        "total_operations":      len(ops_df),
        "manipulated_objects":   all_objects,
        "unresolved_candidates": candidate_count,
        "has_manipulation":      any(p["label"] == "manipulation" for p in phases),
        "has_placement":         any(p["label"] == "placement"    for p in phases),
        "domain_name":           domain_name,
    }

    return {
        "schema_version": "1.0",
        "session_id":     session_id,
        "phases":         phases,
        "phase_transitions": transitions,
        "summary":        summary,
    }


def timeline_to_df(timeline: Dict[str, Any]) -> pd.DataFrame:
    """Convert timeline phases list to a flat CSV-friendly DataFrame."""
    phases = timeline.get("phases", [])
    if not phases:
        return pd.DataFrame(columns=[
            "phase_id", "label", "start_frame_idx", "end_frame_idx",
            "start_ts_ns", "end_ts_ns", "confidence", "dominant_operation",
            "operation_count", "object_tracks",
        ])
    rows = []
    for p in phases:
        rows.append({
            "phase_id":            p["phase_id"],
            "label":               p["label"],
            "start_frame_idx":     p["start_frame_idx"],
            "end_frame_idx":       p["end_frame_idx"],
            "start_ts_ns":         p["start_ts_ns"],
            "end_ts_ns":           p["end_ts_ns"],
            "confidence":          p["confidence"],
            "dominant_operation":  p["dominant_operation"],
            "operation_count":     len(p["supporting_operations"]),
            "object_tracks":       json.dumps(p["object_tracks"]),
        })
    return pd.DataFrame(rows)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _label_cluster(cluster: List[Dict], domain_phase_labels: Optional[set] = None) -> Tuple[str, float, str]:
    """Determine the phase label, confidence, and dominant op for a cluster."""
    if not cluster:
        return "idle", 0.0, ""

    # Count operations by type, weighted by confidence
    type_weights: Dict[str, float] = {}
    for op in cluster:
        otype = str(op.get("operation_type", ""))
        conf  = float(op.get("confidence", 0.5))
        type_weights[otype] = type_weights.get(otype, 0.0) + conf

    # Pick the type with highest priority (lowest priority number) among the top-weighted
    best_label = "contact"
    best_priority = 99
    best_op = ""
    best_weight = 0.0

    for otype, weight in type_weights.items():
        phase_label, priority = _OP_TO_PHASE.get(otype, ("contact", 7))
        if priority < best_priority or (priority == best_priority and weight > best_weight):
            best_label    = phase_label
            best_priority = priority
            best_op       = otype
            best_weight   = weight

    # Confidence = mean confidence of operations in this cluster
    total_conf = sum(float(op.get("confidence", 0.5)) for op in cluster)
    confidence = min(1.0, total_conf / len(cluster))

    # D2: if domain defines phase labels and the computed label isn't in them,
    # keep the generic label (domain may not yet list all phases).
    # The presence of domain_name in summary lets downstream tools know the domain context.
    if domain_phase_labels and best_label not in domain_phase_labels:
        # Fall through with generic label — domain.workflow_phases should be extended
        # to include this label for full alignment.
        pass

    return best_label, confidence, best_op


def _phase_evidence(cluster: List[Dict], label: str) -> str:
    """Build a short human-readable evidence string for a phase."""
    n = len(cluster)
    op_types = list({op["operation_type"] for op in cluster})
    op_summary = ", ".join(op_types)
    agent_tracks = list({
        str(op["agent_track_id"])
        for op in cluster
        if op.get("agent_track_id") and str(op["agent_track_id"]) != "nan"
    })
    obj_tracks = list({
        str(op["object_track_id"])
        for op in cluster
        if op.get("object_track_id") and str(op["object_track_id"]) != "nan"
    })
    parts = [f"{n} operation(s): {op_summary}"]
    if agent_tracks:
        parts.append(f"agent(s): {', '.join(agent_tracks)}")
    if obj_tracks:
        parts.append(f"object(s): {', '.join(obj_tracks)}")
    return "; ".join(parts)


def _empty_timeline(session_id: str) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "session_id":     session_id,
        "phases":         [],
        "phase_transitions": [],
        "summary": {
            "total_phases": 0,
            "dominant_phase": "idle",
            "phase_sequence": [],
            "total_operations": 0,
            "manipulated_objects": [],
            "unresolved_candidates": 0,
            "has_manipulation": False,
            "has_placement": False,
        },
    }
