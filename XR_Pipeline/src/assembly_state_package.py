"""assembly_state_package.py — Assembly State Package builder (Phase 5).

Produces a single consolidated JSON that the reasoning layer reads instead of
scraping multiple files.  The package distils the assembly graph + state facts
+ subtask events into the key reasoning inputs:

  active_facts          — facts currently active (status in active/achieved)
  active_subtasks       — subtasks in_progress or candidate
  achieved_subgoals     — confirmed subgoal names
  blocked_subgoals      — subgoals whose subtask is blocked
  likely_next_subtasks  — pending subtasks whose dependencies are all met
  current_assembly_phase — label of the dominant current phase
  constraint_satisfaction — which dependency rules are satisfied / violated
  unresolved_ambiguities  — candidate facts or subtasks with low confidence
  evidence_summary        — counts of supporting operations / facts per subgoal
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import pandas as pd


# ── Public API ────────────────────────────────────────────────────────────────

def build_assembly_state_package(
    facts_df: pd.DataFrame,
    subtasks_df: pd.DataFrame,
    assembly_graph: Optional[Dict[str, Any]] = None,
    timeline: Optional[Dict[str, Any]] = None,
    domain_config=None,  # Optional[DomainConfig]
    session_id: str = "unknown",
) -> Dict[str, Any]:
    """Build the assembly state package.

    Parameters
    ----------
    facts_df        : state_facts.csv
    subtasks_df     : subtask_events.csv
    assembly_graph  : assembly_graph.json (optional, for subgoal info)
    timeline        : workflow_timeline.json (optional)
    domain_config   : DomainConfig (optional)
    session_id      : session identifier

    Returns
    -------
    Assembly state package dict ready for JSON serialisation.
    """
    facts_df    = facts_df    if (facts_df    is not None and not facts_df.empty)    else pd.DataFrame()
    subtasks_df = subtasks_df if (subtasks_df is not None and not subtasks_df.empty) else pd.DataFrame()

    # ── Active facts ──────────────────────────────────────────────────────────
    active_facts: List[Dict] = []
    if not facts_df.empty:
        for _, fr in facts_df[facts_df["status"].isin({"active", "achieved"})].iterrows():
            active_facts.append({
                "fact_id":    str(fr["fact_id"]),
                "predicate":  str(fr["predicate"]),
                "subject_id": str(fr["subject_id"]),
                "object_id":  _or_none(fr.get("object_id")),
                "confidence": float(fr["confidence"]),
                "frames":     [int(fr["start_frame_idx"]), int(fr["end_frame_idx"])],
                "source":     str(fr.get("source_stage", "")),
            })

    # ── Active subtasks ───────────────────────────────────────────────────────
    active_subtasks: List[Dict] = []
    blocked_subtasks: List[str] = []
    achieved_subtask_templates: set = set()

    if not subtasks_df.empty:
        for _, sub in subtasks_df.iterrows():
            status = str(sub["status"])
            if status in ("in_progress", "candidate"):
                active_subtasks.append({
                    "subtask_id":    str(sub["subtask_id"]),
                    "template_name": str(sub["template_name"]),
                    "status":        status,
                    "confidence":    float(sub["confidence"]),
                    "frames":        [int(sub["start_frame_idx"]), int(sub["end_frame_idx"])],
                    "agent":         _or_none(sub.get("agent_track_id")),
                    "patient":       _or_none(sub.get("patient_track_id")),
                    "why":           str(sub.get("why_this_subtask", "")),
                })
            elif status == "achieved":
                achieved_subtask_templates.add(str(sub["template_name"]))
            elif status == "blocked":
                blocked_subtasks.append(str(sub["subtask_id"]))

    # ── Achieved subgoals ─────────────────────────────────────────────────────
    achieved_subgoals: List[Dict] = []
    blocked_subgoals: List[str] = []

    if assembly_graph is not None:
        for node in assembly_graph.get("nodes", []):
            if node["node_type"] == "subgoal":
                if node["status"] in ("achieved", "achieved_then_released"):
                    achieved_subgoals.append({
                        "name":              node["name"],
                        "instance_name":     node.get("instance_name", node["name"]),
                        "patient_class":     node.get("patient_class", ""),
                        "predicate":         node.get("predicate", ""),
                        "status":            node["status"],
                        "invalidated_at":    node.get("invalidated_at"),
                        "achieved_by_subtask": node.get("achieved_by_subtask"),
                    })
    elif domain_config is not None:
        # Derive from achieved subtask templates when no graph available
        for sg in domain_config.subgoal_templates:
            if sg.achieved_by in achieved_subtask_templates:
                achieved_subgoals.append({
                    "name":          sg.name,
                    "instance_name": sg.name,
                    "patient_class": "",
                    "predicate":     sg.predicate,
                    "achieved_by_subtask": None,
                })

    # Blocked subgoals: subgoal_templates whose achieved_by is blocked
    if domain_config is not None:
        for sg in domain_config.subgoal_templates:
            if (
                sg.achieved_by not in achieved_subtask_templates
                and not subtasks_df.empty
                and any(
                    r["template_name"] == sg.achieved_by and r["status"] == "blocked"
                    for _, r in subtasks_df.iterrows()
                )
            ):
                blocked_subgoals.append(sg.name)

    # ── Likely next subtasks ──────────────────────────────────────────────────
    likely_next: List[Dict] = []
    if domain_config is not None and not subtasks_df.empty:
        for tmpl in domain_config.subtask_templates:
            # Not yet achieved, not currently active
            if tmpl.name in achieved_subtask_templates:
                continue
            if any(
                r["template_name"] == tmpl.name and r["status"] in ("in_progress", "candidate")
                for _, r in subtasks_df.iterrows()
            ):
                continue
            # Check prerequisites
            prereqs = domain_config.required_before(tmpl.name)
            if all(p in achieved_subtask_templates for p in prereqs):
                why_next = f"prerequisites met: {prereqs}" if prereqs else "no prerequisites required"
                likely_next.append({
                    "template_name":     tmpl.name,
                    "description":       tmpl.description,
                    "prerequisites_met": prereqs,
                    "why_likely":        why_next,
                })

    # ── Current assembly phase ────────────────────────────────────────────────
    current_phase = "idle"
    if timeline is not None:
        phases = timeline.get("phases", [])
        if phases:
            current_phase = phases[-1].get("label", "idle")

    if domain_config is not None and active_subtasks:
        # Check phase_hints to refine current phase
        latest_tmpl = active_subtasks[-1]["template_name"] if active_subtasks else None
        if latest_tmpl:
            for phase_label, hint_templates in domain_config.phase_hints.items():
                if latest_tmpl in hint_templates:
                    current_phase = phase_label
                    break

    # ── Constraint satisfaction ───────────────────────────────────────────────
    constraint_sat: Dict[str, Any] = {}
    if domain_config is not None:
        for rule in domain_config.dependency_rules:
            key = f"{rule.subtask}_requires_{rule.requires}"
            constraint_sat[key] = {
                "satisfied":  rule.requires in achieved_subtask_templates,
                "subtask":    rule.subtask,
                "requires":   rule.requires,
                "description": rule.description,
            }

    # ── Unresolved ambiguities ────────────────────────────────────────────────
    ambiguities: List[Dict] = []
    if not facts_df.empty:
        low_conf_facts = facts_df[
            (facts_df["status"] == "candidate") & (facts_df["confidence"] < 0.5)
        ]
        for _, fr in low_conf_facts.head(5).iterrows():
            ambiguities.append({
                "type":      "low_confidence_fact",
                "fact_id":   str(fr["fact_id"]),
                "predicate": str(fr["predicate"]),
                "confidence": float(fr["confidence"]),
            })
    if blocked_subtasks:
        for sid in blocked_subtasks[:5]:
            ambiguities.append({
                "type":       "blocked_subtask",
                "subtask_id": sid,
            })

    # ── State transitions ─────────────────────────────────────────────────────
    state_transitions: List[Dict] = []
    if not facts_df.empty and "predicate" in facts_df.columns:
        trans_preds = {"released", "support_changed"}
        for _, fr in facts_df[facts_df["predicate"].isin(trans_preds)].iterrows():
            state_transitions.append({
                "fact_id":    str(fr["fact_id"]),
                "predicate":  str(fr["predicate"]),
                "subject_id": str(fr["subject_id"]),
                "frame":      int(fr["start_frame_idx"]),
                "confidence": float(fr["confidence"]),
                "source":     str(fr.get("source_stage", "")),
            })
    state_transitions.sort(key=lambda t: t["frame"])

    # ── Why no active step explanation ───────────────────────────────────────
    why_no_active_step: Optional[str] = None
    if not active_subtasks:
        if achieved_subgoals:
            names = ", ".join(
                g.get("instance_name", g["name"]) for g in achieved_subgoals
            )
            transition_summary = ""
            if state_transitions:
                release_events = [t for t in state_transitions if t["predicate"] == "released"]
                if release_events:
                    rel_desc = ", ".join(
                        f"{t['subject_id']} at frame {t['frame']}" for t in release_events[:3]
                    )
                    transition_summary = f" Releases detected: {rel_desc}."
            why_no_active_step = (
                f"All detected subtasks are completed. "
                f"Achieved: {names}.{transition_summary} "
                f"Likely next: {[n['template_name'] for n in likely_next[:3]] or 'none identified'}."
            )
        else:
            why_no_active_step = "No subtask activity detected in this session."

    # ── Evidence summary ──────────────────────────────────────────────────────
    evidence_summary = {
        "total_active_facts":     len(active_facts),
        "total_active_subtasks":  len(active_subtasks),
        "total_achieved_subgoals": len(achieved_subgoals),
        "total_blocked":          len(blocked_subtasks),
    }

    return {
        "schema_version":          "1.0",
        "session_id":              session_id,
        "active_facts":            active_facts,
        "active_subtasks":         active_subtasks,
        "achieved_subgoals":       achieved_subgoals,
        "blocked_subgoals":        blocked_subgoals,
        "likely_next_subtasks":    likely_next,
        "current_assembly_phase":  current_phase,
        "why_no_active_step":      why_no_active_step,
        "state_transitions":       state_transitions,
        "constraint_satisfaction": constraint_sat,
        "unresolved_ambiguities":  ambiguities,
        "assembly_graph_ref":      "graphs/assembly_graph.json",
        "evidence_summary":        evidence_summary,
    }


# ── Helper ────────────────────────────────────────────────────────────────────

def _or_none(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val)
    return None if s.lower() in {"nan", "none", "", "null"} else s
