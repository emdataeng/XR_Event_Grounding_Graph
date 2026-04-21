"""subtask_events.py — Subtask / step inference layer (Phase 3).

Infers assembly subtask candidates from state facts + operation events +
domain config.  The goal is a step layer between raw operations and high-level
reasoning — e.g. "insert_part" rather than just "INSERT_CANDIDATE".

Design principles
-----------------
- Weak evidence stays as status='candidate', strong as 'in_progress'/'achieved'.
- No hard labels unless evidence is strong.  Better to under-commit.
- Falls back to a generic template set when no domain config is provided.
- Each subtask records which facts and operations support it, so reasoning can
  trace back to raw evidence.

Generic template fallback (used when domain_config is None)
-----------------------------------------------------------
PICK_UP / HOLD                → pick_up_part
PUT_DOWN / PUT_DOWN_CANDIDATE → place_part
CONTACT                       → contact_parts
INSERT_CANDIDATE              → insert_part
PLACE_ONTO_CANDIDATE          → place_part
ALIGN_CANDIDATE               → align_part
ATTACH_CANDIDATE              → attach_part
USE_TOOL                      → use_tool
TRANSFER                      → transfer_part
APPROACH                      → approach_target
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

# ── Generic template fallback ─────────────────────────────────────────────────

_GENERIC_OP_TO_TEMPLATE: Dict[str, str] = {
    "PICK_UP":               "pick_up_part",
    "HOLD":                  "pick_up_part",
    "PUT_DOWN":              "place_part",
    "PUT_DOWN_CANDIDATE":    "place_part",
    "CONTACT":               "contact_parts",
    "INSERT_CANDIDATE":      "insert_part",
    "PLACE_ONTO_CANDIDATE":  "place_part",
    "ALIGN_CANDIDATE":       "align_part",
    "ATTACH_CANDIDATE":      "attach_part",
    "USE_TOOL":              "use_tool",
    "TRANSFER":              "transfer_part",
    "APPROACH":              "approach_target",
}

# Inter-object relation facts → generic template fallback
_RELATION_FACT_TO_TEMPLATE: Dict[str, str] = {
    "co_held":            "co_held_parts",
    "in_contact":         "contact_parts",
    "touching_candidate": "contact_parts",
}

# Support-state transitions that imply a subtask (independent of explicit ops)
_SUPPORT_TRANSITION_TO_TEMPLATE: Dict[Tuple[str, str], str] = {
    ("CARRIED", "RESTING"):     "release_part",
    ("CARRIED", "IN_CONTACT"):  "place_part",
}

# Candidate operation types → weaker status
_CANDIDATE_OPS = frozenset({
    "PICK_UP_CANDIDATE", "PUT_DOWN_CANDIDATE", "INSERT_CANDIDATE",
    "PLACE_ONTO_CANDIDATE", "ALIGN_CANDIDATE", "ATTACH_CANDIDATE",
})

# Output column schema
_SUBTASK_COLS = [
    "subtask_id", "template_name", "instance_label", "status",
    "agent_track_id", "patient_track_id", "target_track_id",
    "required_facts", "supporting_facts", "supporting_operations",
    "confidence", "start_frame_idx", "end_frame_idx", "why_this_subtask",
]
SUBTASK_COLS = _SUBTASK_COLS  # public alias for tests / downstream code


# ── Public API ────────────────────────────────────────────────────────────────

def infer_subtask_events(
    facts_df: pd.DataFrame,
    ops_df: pd.DataFrame,
    domain_config=None,  # Optional[DomainConfig]
    tracks_df: Optional[pd.DataFrame] = None,
    support_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Infer subtask candidates from state facts + operations + domain config.

    Parameters
    ----------
    facts_df      : state_facts.csv DataFrame (from state_facts.compute_state_facts)
    ops_df        : operation_events.csv DataFrame
    domain_config : DomainConfig (optional)

    Returns
    -------
    DataFrame with subtask event rows (columns: subtask_id, template_name, …)
    """
    if (
        (ops_df is None or ops_df.empty)
        and (facts_df is None or facts_df.empty)
        and (support_df is None or support_df.empty)
    ):
        return pd.DataFrame(columns=_SUBTASK_COLS)

    ops_df     = ops_df     if ops_df     is not None else pd.DataFrame()
    facts_df   = facts_df   if facts_df   is not None else pd.DataFrame()

    # Build track class lookup from tracks_df (track_id → semantic_class)
    track_classes: Dict[str, str] = {}
    if tracks_df is not None and not tracks_df.empty and "semantic_class" in tracks_df.columns:
        for tid, grp in tracks_df.groupby("track_id"):
            track_classes[str(tid)] = str(grp["semantic_class"].iloc[0])

    # Build a fact lookup: predicate → list of fact rows
    fact_lookup: Dict[str, List[Dict]] = {}
    if not facts_df.empty:
        for _, fr in facts_df.iterrows():
            pred = str(fr["predicate"])
            fact_lookup.setdefault(pred, []).append(fr.to_dict())

    rows: List[Dict[str, Any]] = []
    counter = [0]

    def _next_id() -> str:
        counter[0] += 1
        return f"sub_{counter[0]:04d}"

    # ── Choose template source ─────────────────────────────────────────────────
    if domain_config is not None and domain_config.subtask_templates:
        templates = {t.name: t for t in domain_config.subtask_templates}
    else:
        templates = None  # use generic fallback

    # ── Dependency checking helper ─────────────────────────────────────────────
    achieved_templates: Set[str] = set()  # populated as we scan

    def _prereqs_met(template_name: str) -> bool:
        if domain_config is None:
            return True
        required = domain_config.required_before(template_name)
        return all(r in achieved_templates for r in required)

    # ── Process each operation ─────────────────────────────────────────────────
    if not ops_df.empty:
        ops_sorted = ops_df.sort_values("start_frame_idx").reset_index(drop=True)

        for _, op in ops_sorted.iterrows():
            otype   = str(op.get("operation_type", ""))
            op_id   = str(op.get("operation_id", ""))
            conf    = float(op.get("confidence", 0.5))
            start_f = int(op.get("start_frame_idx", 0))
            end_f   = int(op.get("end_frame_idx", start_f))

            agent_raw  = op.get("agent_track_id")
            object_raw = op.get("object_track_id")
            agent_str  = _valid_str(agent_raw)
            object_str = _valid_str(object_raw)

            # Determine template name
            if templates is not None:
                tmpl_name = _match_template_for_op(otype, templates)
            else:
                tmpl_name = _GENERIC_OP_TO_TEMPLATE.get(otype)

            if not tmpl_name:
                continue

            # Gather required / supporting facts
            req_facts: List[str] = []
            sup_facts: List[str] = []

            if templates is not None and tmpl_name in templates:
                tmpl = templates[tmpl_name]
                for pred in tmpl.trigger_predicates:
                    matching = _facts_near_window(fact_lookup, pred, start_f, end_f)
                    for f in matching:
                        fid = str(f.get("fact_id", ""))
                        req_facts.append(f"{pred}({f.get('subject_id','')},{f.get('object_id','')})")
                        sup_facts.append(fid)

            # Also collect any active facts that overlap this operation window
            for pred, flist in fact_lookup.items():
                for f in flist:
                    if _overlaps(int(f.get("start_frame_idx", 0)),
                                 int(f.get("end_frame_idx", 0)),
                                 start_f, end_f):
                        fid = str(f.get("fact_id", ""))
                        if fid not in sup_facts:
                            sup_facts.append(fid)

            # Determine status
            if otype in _CANDIDATE_OPS:
                base_status = "candidate"
            elif conf >= 0.65:
                base_status = "achieved"
            elif conf >= 0.45:
                base_status = "in_progress"
            else:
                base_status = "candidate"

            # Downgrade to blocked if prerequisites not met
            if base_status in ("in_progress", "achieved") and not _prereqs_met(tmpl_name):
                base_status = "blocked"

            if base_status == "achieved":
                achieved_templates.add(tmpl_name)

            # Build instance label using object semantic classes
            patient_class = track_classes.get(object_str, "") if object_str else ""
            agent_class   = track_classes.get(agent_str,  "") if agent_str  else ""
            if patient_class and patient_class not in ("hand", ""):
                instance_label = f"{tmpl_name}({patient_class})"
            else:
                instance_label = tmpl_name

            # Build descriptive why string
            duration = end_f - start_f + 1
            patient_desc = f" {patient_class}" if patient_class else ""
            agent_desc   = f" {agent_class}"   if agent_class   else ""
            why = f"{otype} {op_id}:{agent_desc} acted on{patient_desc} ({start_f}→{end_f}, {duration} frames)"
            if req_facts:
                why += f" with {', '.join(req_facts[:2])}"

            rows.append({
                "subtask_id":            _next_id(),
                "template_name":         tmpl_name,
                "instance_label":        instance_label,
                "status":                base_status,
                "agent_track_id":        agent_str,
                "patient_track_id":      object_str,
                "target_track_id":       None,
                "required_facts":        json.dumps(req_facts),
                "supporting_facts":      json.dumps(sup_facts[:10]),
                "supporting_operations": json.dumps([op_id]),
                "confidence":            round(conf, 3),
                "start_frame_idx":       start_f,
                "end_frame_idx":         end_f,
                "why_this_subtask":      why,
            })

    # ── Derive subtasks from support-state transitions ─────────────────────────
    if support_df is not None and not support_df.empty:
        # Frame windows already covered by explicit PUT_DOWN/PUT_DOWN_CANDIDATE ops
        covered_frames: Set[int] = set()
        if not ops_df.empty:
            for _, op in ops_df.iterrows():
                if str(op.get("operation_type", "")) in ("PUT_DOWN", "PUT_DOWN_CANDIDATE"):
                    ef = int(op.get("end_frame_idx", 0))
                    covered_frames.update(range(ef - 3, ef + 4))

        # Build HOLD/PICK_UP lookup: object_track_id → list of ops (for finding agent)
        hold_by_patient: Dict[str, List[Dict]] = {}
        if not ops_df.empty:
            for _, op in ops_df.iterrows():
                if str(op.get("operation_type", "")) in ("HOLD", "PICK_UP"):
                    obj = _valid_str(op.get("object_track_id"))
                    if obj:
                        hold_by_patient.setdefault(obj, []).append(op.to_dict())

        # Known domain template names (for subgoal lookup compatibility)
        domain_tmpl_names: Set[str] = set()
        if domain_config is not None and hasattr(domain_config, "subtask_templates"):
            domain_tmpl_names = {t.name for t in domain_config.subtask_templates}

        for tid, grp in support_df.groupby("track_id"):
            grp_s = grp.sort_values("start_frame_idx").reset_index(drop=True)
            for i in range(len(grp_s) - 1):
                prev_state = str(grp_s.iloc[i].get("state", ""))
                next_state  = str(grp_s.iloc[i + 1].get("state", ""))
                t_frame     = int(grp_s.iloc[i + 1].get("start_frame_idx", 0))

                tmpl_name = _SUPPORT_TRANSITION_TO_TEMPLATE.get((prev_state, next_state))
                if tmpl_name is None or t_frame in covered_frames:
                    continue

                tid_str      = str(tid)
                patient_class = track_classes.get(tid_str, "")

                # Find the most recent preceding HOLD/PICK_UP agent for this object
                agent_str = None
                preceding = [
                    h for h in hold_by_patient.get(tid_str, [])
                    if int(h.get("end_frame_idx", 0)) <= t_frame
                ]
                if preceding:
                    agent_str = _valid_str(preceding[-1].get("agent_track_id"))
                agent_class = track_classes.get(agent_str, "") if agent_str else ""

                # Instance label
                if patient_class and patient_class not in ("hand", ""):
                    inst_label = f"{tmpl_name}({patient_class})"
                else:
                    inst_label = tmpl_name

                # Why string
                agent_desc   = f" {agent_class}"   if agent_class   else ""
                patient_desc = f" {patient_class}" if patient_class else ""
                why = (
                    f"{prev_state}→{next_state} transition at frame {t_frame}:"
                    f"{agent_desc} released{patient_desc}"
                )

                start_f = int(grp_s.iloc[i].get("end_frame_idx", t_frame))

                base_status = "achieved"
                if base_status in ("in_progress", "achieved") and not _prereqs_met(tmpl_name):
                    base_status = "blocked"
                if base_status == "achieved":
                    achieved_templates.add(tmpl_name)

                rows.append({
                    "subtask_id":            _next_id(),
                    "template_name":         tmpl_name,
                    "instance_label":        inst_label,
                    "status":                base_status,
                    "agent_track_id":        agent_str,
                    "patient_track_id":      tid_str,
                    "target_track_id":       None,
                    "required_facts":        json.dumps([]),
                    "supporting_facts":      json.dumps([]),
                    "supporting_operations": json.dumps([]),
                    "confidence":            0.75,
                    "start_frame_idx":       start_f,
                    "end_frame_idx":         t_frame,
                    "why_this_subtask":      why,
                })

    # ── Derive subtasks from inter-object relation facts ───────────────────────
    # Use co_held facts to infer co_held_parts(a, b) as a candidate subtask.
    # This models the observation that two objects held by the same agent are
    # potentially in proximity / weak contact — a candidate assembly event.
    _inter_preds = {"co_held"}
    for pred_name in _inter_preds:
        for f in fact_lookup.get(pred_name, []):
            subj = str(f.get("subject_id", "")) if _valid_str(f.get("subject_id")) else None
            obj  = str(f.get("object_id",  "")) if _valid_str(f.get("object_id"))  else None
            if not subj or not obj:
                continue

            start_f = int(f.get("start_frame_idx", 0))
            end_f   = int(f.get("end_frame_idx", start_f))
            conf    = float(f.get("confidence", 0.5))
            fid     = str(f.get("fact_id", ""))

            # Choose template from domain config if available
            if templates is not None:
                tmpl_name = _match_template_for_pred(pred_name, templates)
            else:
                tmpl_name = _RELATION_FACT_TO_TEMPLATE.get(pred_name)

            if not tmpl_name:
                continue

            subj_class = track_classes.get(subj, "")
            obj_class  = track_classes.get(obj,  "")

            if subj_class and obj_class and subj_class not in ("hand", "") and obj_class not in ("hand", ""):
                instance_label = f"{tmpl_name}({subj_class},{obj_class})"
            elif subj_class and subj_class not in ("hand", ""):
                instance_label = f"{tmpl_name}({subj_class})"
            else:
                instance_label = tmpl_name

            duration = end_f - start_f + 1
            why = (
                f"{pred_name} fact {fid}: {subj_class or subj} and {obj_class or obj} "
                f"co-held ({start_f}→{end_f}, {duration} frames)"
            )

            rows.append({
                "subtask_id":            _next_id(),
                "template_name":         tmpl_name,
                "instance_label":        instance_label,
                "status":                "candidate",  # co_held is weak contact evidence
                "agent_track_id":        subj,
                "patient_track_id":      obj,
                "target_track_id":       None,
                "required_facts":        json.dumps([]),
                "supporting_facts":      json.dumps([fid]),
                "supporting_operations": json.dumps([]),
                "confidence":            round(conf * 0.8, 3),
                "start_frame_idx":       start_f,
                "end_frame_idx":         end_f,
                "why_this_subtask":      why,
            })

    if not rows:
        return pd.DataFrame(columns=_SUBTASK_COLS)

    return pd.DataFrame(rows)[_SUBTASK_COLS]


def subtask_sequence_json(subtasks_df: pd.DataFrame, session_id: str = "unknown") -> Dict[str, Any]:
    """Serialise subtasks to a sequence JSON with status timeline."""
    phases: Dict[str, List[Dict]] = {}
    for _, row in subtasks_df.iterrows():
        tmpl = str(row["template_name"])
        phases.setdefault(tmpl, []).append({
            "subtask_id":    row["subtask_id"],
            "instance_label": row.get("instance_label", tmpl),
            "status":        row["status"],
            "confidence":    row["confidence"],
            "start_frame":   row["start_frame_idx"],
            "end_frame":     row["end_frame_idx"],
            "agent":         row["agent_track_id"],
            "patient":       row["patient_track_id"],
        })

    ordered = subtasks_df.sort_values("start_frame_idx").to_dict(orient="records")
    for rec in ordered:
        try:
            rec["required_facts"]      = json.loads(rec["required_facts"])
            rec["supporting_facts"]    = json.loads(rec["supporting_facts"])
            rec["supporting_operations"] = json.loads(rec["supporting_operations"])
        except (json.JSONDecodeError, TypeError):
            pass

    status_counts = subtasks_df["status"].value_counts().to_dict() if not subtasks_df.empty else {}

    return {
        "schema_version": "1.0",
        "session_id":     session_id,
        "total_subtasks": len(subtasks_df),
        "status_summary": status_counts,
        "subtask_sequence": ordered,
        "by_template":    phases,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _match_template_for_op(otype: str, templates: Dict) -> Optional[str]:
    """Find the first template whose trigger_operations includes otype."""
    for name, tmpl in templates.items():
        if otype in tmpl.trigger_operations:
            return name
    # fallback: generic map
    return _GENERIC_OP_TO_TEMPLATE.get(otype)


def _match_template_for_pred(pred: str, templates: Dict) -> Optional[str]:
    """Find the first template whose trigger_predicates includes pred."""
    for name, tmpl in templates.items():
        if pred in getattr(tmpl, "trigger_predicates", []):
            return name
    # fallback: relation fact map
    return _RELATION_FACT_TO_TEMPLATE.get(pred)


def _facts_near_window(
    fact_lookup: Dict[str, List[Dict]],
    predicate: str,
    start_f: int,
    end_f: int,
    tolerance: int = 5,
) -> List[Dict]:
    """Return facts with the given predicate that overlap the frame window ± tolerance."""
    candidates = fact_lookup.get(predicate, [])
    result = []
    for f in candidates:
        fs = int(f.get("start_frame_idx", 0))
        fe = int(f.get("end_frame_idx", 0))
        if _overlaps(fs, fe, start_f - tolerance, end_f + tolerance):
            result.append(f)
    return result


def _overlaps(s1: int, e1: int, s2: int, e2: int) -> bool:
    return s1 <= e2 and s2 <= e1


def _valid_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val)
    return None if s.lower() in {"nan", "none", "", "null"} else s
