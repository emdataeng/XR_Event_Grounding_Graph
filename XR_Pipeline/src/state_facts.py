"""state_facts.py — Formal state-facts layer (Phase 1).

Converts pipeline outputs (tracks, events, operation events, support-state transitions)
into explicit, time-scoped, queryable facts for the assembly reasoning layer.

Fact predicate vocabulary
--------------------------
Presence / lifecycle
    present(object)                 — object tracked in scene
    appeared(object)                — object newly entered the scene
    disappeared(object)             — object left the scene

Motion
    started_moving(object)          — object began a MOVE event
    stopped_moving(object)          — MOVE event ended

Proximity / spatial
    near(a, b)                      — objects within near_threshold (CO_LOCATE)
    touching_candidate(a, b)        — potential physical contact (INTERACTION)

Support state (from support_state_transitions.csv)
    resting(object)                 — no operation, object at rest
    carried(object)                 — object being held/moved by hand
    surface_contact(object)         — object touching another surface

Operation-derived relations
    holding(agent, object)          — HOLD or PICK_UP operation active
    released(object)                — PUT_DOWN or PUT_DOWN_CANDIDATE completed
    in_contact(a, b)                — CONTACT operation
    inserted_into_candidate(a, b)   — INSERT_CANDIDATE operation
    placed_on_candidate(a, b)       — PLACE_ONTO_CANDIDATE operation
    aligned_with_candidate(a, b)    — ALIGN_CANDIDATE operation
    attached_to_candidate(a, b)     — ATTACH_CANDIDATE operation
    used_tool_on(tool, object)      — USE_TOOL operation

Inter-object relation facts (Section 5)
    co_held(a, b)           — two non-hand objects held by same agent simultaneously
    co_held_started(a, b)   — point fact: co_held relation begins at this frame
    co_held_ended(a, b)     — point fact: co_held relation ends at this frame

Fact status lifecycle
---------------------
  candidate   — weak evidence, below confidence threshold or single-source
  active      — currently holding, well-evidenced
  achieved    — relation held and is now completed / stable
  invalidated — was active but a subsequent event contradicts it
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

import pandas as pd

# ── Predicate mappings ────────────────────────────────────────────────────────

_EVENT_TO_PREDICATE: Dict[str, str] = {
    "APPEAR":     "appeared",
    "DISAPPEAR":  "disappeared",
    "MOVE":       "started_moving",
    "CO_LOCATE":  "near",
    "INTERACTION": "touching_candidate",
    "PLACE":      "touching_candidate",
    "SEPARATE":   "near",          # de-facto separating; near but direction reversed
}

_OP_TO_PREDICATE: Dict[str, str] = {
    "HOLD":                  "holding",
    "PICK_UP":               "holding",
    "PUT_DOWN":              "released",
    "PUT_DOWN_CANDIDATE":    "released",
    "CONTACT":               "in_contact",
    "INSERT_CANDIDATE":      "inserted_into_candidate",
    "PLACE_ONTO_CANDIDATE":  "placed_on_candidate",
    "ALIGN_CANDIDATE":       "aligned_with_candidate",
    "ATTACH_CANDIDATE":      "attached_to_candidate",
    "USE_TOOL":              "used_tool_on",
}

_SUPPORT_TO_PREDICATE: Dict[str, str] = {
    "RESTING":    "resting",
    "CARRIED":    "carried",
    "IN_CONTACT": "surface_contact",
    "ACTIVE":     "resting",    # fallback — "active but unclassified" ~ resting
}

# Operations that establish a binary relation (agent → object)
_BINARY_OPS = frozenset({
    "HOLD", "PICK_UP", "CONTACT", "INSERT_CANDIDATE",
    "PLACE_ONTO_CANDIDATE", "ALIGN_CANDIDATE", "ATTACH_CANDIDATE", "USE_TOOL",
})

# High-confidence threshold: facts above this are 'active', below are 'candidate'
_ACTIVE_CONFIDENCE = 0.55

# Predicates that are semantically uncertain by definition (regardless of confidence)
_CANDIDATE_PREDICATES = frozenset({"touching_candidate", "near"})

# ── Column schema ─────────────────────────────────────────────────────────────

_FACT_COLS = [
    "fact_id", "predicate", "subject_id", "object_id",
    "status", "confidence", "start_frame_idx", "end_frame_idx",
    "evidence_refs", "source_stage", "domain_relevance",
]
FACT_COLS = _FACT_COLS  # public alias for tests / downstream code


# ── Public API ────────────────────────────────────────────────────────────────

def compute_state_facts(
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    ops_df: pd.DataFrame,
    support_df: Optional[pd.DataFrame] = None,
    domain_config=None,  # Optional[DomainConfig]
    track_classes: Optional[Dict[str, str]] = None,  # pre-built track→class lookup
) -> pd.DataFrame:
    """Compute explicit state facts from pipeline outputs.

    Parameters
    ----------
    tracks_df     : object_tracks.csv
    events_df     : events.csv  (event_windows or merged)
    ops_df        : operation_events.csv
    support_df    : support_state_transitions.csv  (optional)
    domain_config : DomainConfig  (optional — used to mark domain_relevance)
    track_classes : pre-built track_id→semantic_class dict (optional — derived from
                    tracks_df when not supplied)

    Returns
    -------
    DataFrame with columns: fact_id, predicate, subject_id, object_id,
    status, confidence, start_frame_idx, end_frame_idx, evidence_refs,
    source_stage, domain_relevance
    """
    domain_predicates: set = set()
    if domain_config is not None and hasattr(domain_config, "assembly_predicates"):
        domain_predicates = {p.name for p in domain_config.assembly_predicates}

    rows: List[Dict[str, Any]] = []
    counter = [0]

    def _next_id() -> str:
        counter[0] += 1
        return f"fact_{counter[0]:04d}"

    def _status(conf: float, predicate: str = "") -> str:
        if predicate in _CANDIDATE_PREDICATES:
            return "candidate"
        return "active" if conf >= _ACTIVE_CONFIDENCE else "candidate"

    def _relevant(pred: str) -> bool:
        return bool(not domain_predicates or pred in domain_predicates)

    def _row(
        predicate: str,
        subject_id: str,
        object_id: Optional[str],
        confidence: float,
        start_frame: int,
        end_frame: int,
        evidence_refs: List[str],
        source_stage: str,
        status_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "fact_id":          _next_id(),
            "predicate":        predicate,
            "subject_id":       subject_id,
            "object_id":        object_id,
            "status":           status_override or _status(confidence, predicate),
            "confidence":       round(confidence, 3),
            "start_frame_idx":  int(start_frame),
            "end_frame_idx":    int(end_frame),
            "evidence_refs":    json.dumps(evidence_refs),
            "source_stage":     source_stage,
            "domain_relevance": _relevant(predicate),
        }

    # ── 1. Presence facts from tracks ─────────────────────────────────────────
    if tracks_df is not None and not tracks_df.empty:
        for tid, grp in tracks_df.groupby("track_id"):
            grp_s = grp.sort_values("frame_idx")
            start_f = int(grp_s["frame_idx"].min())
            end_f   = int(grp_s["frame_idx"].max())
            conf    = float(grp_s.get("linkage_score", pd.Series([0.75])).mean()) if "linkage_score" in grp_s.columns else 0.75
            rows.append(_row("present", str(tid), None, conf, start_f, end_f, [], "tracks"))

    # ── 2. Event facts ────────────────────────────────────────────────────────
    if events_df is not None and not events_df.empty:
        for _, ev in events_df.iterrows():
            etype = str(ev.get("event_type", ""))
            predicate = _EVENT_TO_PREDICATE.get(etype)
            if predicate is None:
                continue

            conf       = float(ev.get("confidence", 0.6))
            start_f    = int(ev.get("start_frame_idx", 0))
            end_f      = int(ev.get("end_frame_idx", start_f))
            eid        = str(ev.get("event_id", ""))
            try:
                track_ids = json.loads(ev.get("primary_track_ids", "[]"))
            except (json.JSONDecodeError, TypeError):
                track_ids = []

            if not track_ids:
                continue

            subject = str(track_ids[0])
            obj     = str(track_ids[1]) if len(track_ids) > 1 else None

            rows.append(_row(predicate, subject, obj, conf, start_f, end_f, [eid], "events"))

            # MOVE also generates a stopped_moving fact at end_frame
            if etype == "MOVE":
                rows.append(_row(
                    "stopped_moving", subject, None, conf,
                    end_f, end_f, [eid], "events",
                ))

    # ── 3. Operation facts ────────────────────────────────────────────────────
    if ops_df is not None and not ops_df.empty:
        for _, op in ops_df.iterrows():
            otype = str(op.get("operation_type", ""))
            predicate = _OP_TO_PREDICATE.get(otype)
            if predicate is None:
                continue

            conf    = float(op.get("confidence", 0.65))
            start_f = int(op.get("start_frame_idx", 0))
            end_f   = int(op.get("end_frame_idx", start_f))
            op_id   = str(op.get("operation_id", ""))

            agent_raw  = op.get("agent_track_id")
            object_raw = op.get("object_track_id")
            agent_str  = str(agent_raw) if _valid_id(agent_raw) else None
            object_str = str(object_raw) if _valid_id(object_raw) else None

            if otype in _BINARY_OPS:
                # Binary: subject=agent, object=patient
                subj = agent_str or object_str
                obj  = object_str if agent_str else None
            else:
                # Unary (PUT_DOWN/PUT_DOWN_CANDIDATE): subject=object being released
                subj = object_str
                obj  = None

            if subj is None:
                continue

            # Completed operations → achieved; candidates → candidate
            if "_CANDIDATE" in otype:
                status = "candidate"
            else:
                status = "achieved" if conf >= _ACTIVE_CONFIDENCE else "candidate"

            rows.append(_row(predicate, subj, obj, conf, start_f, end_f, [op_id], "operations", status))

    # ── 4. Support-state facts ────────────────────────────────────────────────
    if support_df is not None and not support_df.empty:
        for _, row in support_df.iterrows():
            state = str(row.get("state", ""))
            predicate = _SUPPORT_TO_PREDICATE.get(state)
            if predicate is None:
                continue

            tid     = str(row.get("track_id", ""))
            start_f = int(row.get("start_frame_idx", 0))
            end_f   = int(row.get("end_frame_idx", start_f))
            op_id   = row.get("trigger_operation_id")
            refs    = [str(op_id)] if _valid_id(op_id) else []

            if not tid:
                continue

            conf = 0.80 if state == "CARRIED" else 0.70
            rows.append(_row(predicate, tid, None, conf, start_f, end_f, refs, "support_state"))

        # ── 4b. Support-state transition facts ───────────────────────────────
        # Detect consecutive state changes for each track and emit transition facts.
        for tid, grp in support_df.groupby("track_id"):
            grp_s = grp.sort_values("start_frame_idx").reset_index(drop=True)
            for i in range(len(grp_s) - 1):
                prev_row = grp_s.iloc[i]
                next_row = grp_s.iloc[i + 1]
                prev_state = str(prev_row.get("state", ""))
                next_state  = str(next_row.get("state", ""))
                t_frame = int(next_row.get("start_frame_idx", 0))

                op_ref = next_row.get("trigger_operation_id") or prev_row.get("trigger_operation_id")
                refs   = [str(op_ref)] if _valid_id(op_ref) else []

                # CARRIED → RESTING or IN_CONTACT: object was released / set down
                if prev_state == "CARRIED" and next_state in ("RESTING", "IN_CONTACT"):
                    rows.append(_row(
                        "released", str(tid), None, 0.80,
                        t_frame, t_frame, refs, "support_state",
                        status_override="achieved",
                    ))

                # Generic state transition marker
                rows.append(_row(
                    "support_changed", str(tid), None, 0.75,
                    t_frame, t_frame, refs, "support_state",
                ))

    # ── 5. Inter-object relation facts ───────────────────────────────────────────
    # Build a track→class lookup (used to skip hand tracks from co_held pairs)
    _tc: Dict[str, str] = {}
    if track_classes:
        _tc = {str(k): str(v) for k, v in track_classes.items()}
    elif tracks_df is not None and not tracks_df.empty and "semantic_class" in tracks_df.columns:
        for _tid, _grp in tracks_df.groupby("track_id"):
            _tc[str(_tid)] = str(_grp["semantic_class"].iloc[0])

    _hand_role_keywords = {"hand"}

    def _is_hand_track(tid: str) -> bool:
        cls = _tc.get(str(tid), "")
        return cls.lower() in _hand_role_keywords or "hand" in cls.lower()

    # 5a — co_held(a, b): two non-hand objects held by same agent simultaneously
    if ops_df is not None and not ops_df.empty:
        hold_types = {"HOLD", "PICK_UP"}
        hold_ops = ops_df[ops_df["operation_type"].isin(hold_types)].copy()

        for agent_raw, agent_grp in hold_ops.groupby("agent_track_id"):
            if not _valid_id(agent_raw):
                continue
            recs = agent_grp[
                ["object_track_id", "start_frame_idx", "end_frame_idx", "confidence", "operation_id"]
            ].to_dict("records")

            for i in range(len(recs)):
                for j in range(i + 1, len(recs)):
                    a, b = recs[i], recs[j]
                    a_obj = str(a["object_track_id"]) if _valid_id(a["object_track_id"]) else None
                    b_obj = str(b["object_track_id"]) if _valid_id(b["object_track_id"]) else None
                    if not a_obj or not b_obj:
                        continue
                    # Skip hand-to-hand pairs
                    if _is_hand_track(a_obj) or _is_hand_track(b_obj):
                        continue

                    a_s, a_e = int(a["start_frame_idx"]), int(a["end_frame_idx"])
                    b_s, b_e = int(b["start_frame_idx"]), int(b["end_frame_idx"])

                    # Compute temporal overlap
                    ov_start = max(a_s, b_s)
                    ov_end   = min(a_e, b_e)
                    if ov_start > ov_end:
                        continue  # no overlap

                    conf = round(min(float(a["confidence"]), float(b["confidence"])) * 0.9, 3)
                    refs = [
                        str(r) for r in [a.get("operation_id"), b.get("operation_id")]
                        if _valid_id(r)
                    ]

                    # Sustained co_held fact
                    rows.append(_row(
                        "co_held", a_obj, b_obj, conf,
                        ov_start, ov_end, refs, "operations",
                        status_override="active",
                    ))
                    # Transition: co_held begins
                    rows.append(_row(
                        "co_held_started", a_obj, b_obj, conf,
                        ov_start, ov_start, refs, "operations",
                        status_override="active",
                    ))
                    # Transition: co_held ends
                    rows.append(_row(
                        "co_held_ended", a_obj, b_obj, conf,
                        ov_end, ov_end, refs, "operations",
                        status_override="active",
                    ))

    if not rows:
        return pd.DataFrame(columns=_FACT_COLS)

    return pd.DataFrame(rows)[_FACT_COLS]


def facts_to_json(facts_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Serialize facts DataFrame to a JSON-compatible list of dicts."""
    out = []
    for _, row in facts_df.iterrows():
        d = row.to_dict()
        # Decode evidence_refs JSON string back to list
        try:
            d["evidence_refs"] = json.loads(d["evidence_refs"])
        except (json.JSONDecodeError, TypeError):
            d["evidence_refs"] = []
        out.append(d)
    return out


def active_facts(facts_df: pd.DataFrame, frame_idx: Optional[int] = None) -> pd.DataFrame:
    """Return facts that are active (and optionally alive at frame_idx)."""
    mask = facts_df["status"].isin({"active", "achieved"})
    if frame_idx is not None:
        mask = mask & (facts_df["start_frame_idx"] <= frame_idx) & (facts_df["end_frame_idx"] >= frame_idx)
    return facts_df[mask]


def facts_for_predicate(facts_df: pd.DataFrame, predicate: str) -> pd.DataFrame:
    """Return all facts matching a given predicate."""
    return facts_df[facts_df["predicate"] == predicate]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _valid_id(val: Any) -> bool:
    """Return True if val is a non-null, non-nan track/operation ID string."""
    if val is None:
        return False
    try:
        s = str(val)
        return s.lower() not in {"nan", "none", "", "null"}
    except Exception:
        return False
