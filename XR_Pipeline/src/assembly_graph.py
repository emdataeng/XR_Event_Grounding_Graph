"""assembly_graph.py — Assembly graph construction (Phase 4).

Builds a derived graph layered on top of the EGG graph.  The assembly graph
adds assembly-aware node types and edges for step/subgoal reasoning.

Node types
----------
object        — tracked objects (from egg_graph or tracks)
relation_fact — state facts (from state_facts.json)
subtask       — inferred assembly steps (from subtask_events.csv)
subgoal       — achieved subgoals (from domain subgoal_templates)
phase         — workflow phases (from workflow_timeline.json)
constraint    — dependency rules (from domain_config)

Edge types
----------
involves      — subtask → object      (subtask acts on this object)
supports      — fact → subtask        (fact is evidence for this subtask)
achieves      — subtask → subgoal     (subtask completion achieves subgoal)
requires      — subtask → constraint  (subtask must satisfy this constraint)
depends_on    — subtask_B → subtask_A (B requires A first)
evidence_for  — operation_id → subtask (operation is primary evidence)
next_candidate — subtask_A → subtask_B (B likely follows A in sequence)
belongs_to_phase — subtask → phase   (subtask is part of this phase)
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import pandas as pd


# ── Public API ────────────────────────────────────────────────────────────────

def build_assembly_graph(
    tracks_df: pd.DataFrame,
    facts_df: pd.DataFrame,
    subtasks_df: pd.DataFrame,
    egg_graph: Optional[Dict[str, Any]] = None,
    timeline: Optional[Dict[str, Any]] = None,
    domain_config=None,  # Optional[DomainConfig]
    session_id: str = "unknown",
) -> Dict[str, Any]:
    """Build the assembly graph from all upstream layers.

    Parameters
    ----------
    tracks_df   : object_tracks.csv
    facts_df    : state_facts.csv
    subtasks_df : subtask_events.csv
    egg_graph   : egg_graph.json dict (optional)
    timeline    : workflow_timeline.json dict (optional)
    domain_config : DomainConfig (optional)
    session_id  : session identifier

    Returns
    -------
    Assembly graph dict with schema_version, nodes, edges, summary.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    node_ids: set = set()
    edge_counter = [0]

    # Build track→class lookup for instance-aware naming
    track_classes: Dict[str, str] = {}
    if tracks_df is not None and not tracks_df.empty and "semantic_class" in tracks_df.columns:
        for tid, grp in tracks_df.groupby("track_id"):
            track_classes[str(tid)] = str(grp["semantic_class"].iloc[0])

    def _add_node(node: Dict) -> None:
        nid = node["node_id"]
        if nid not in node_ids:
            node_ids.add(nid)
            nodes.append(node)

    def _add_edge(src: str, tgt: str, edge_type: str, **props) -> None:
        edge_counter[0] += 1
        edges.append({
            "edge_id":   f"edge_{edge_counter[0]:04d}",
            "edge_type": edge_type,
            "source":    src,
            "target":    tgt,
            **props,
        })

    # ── 1. Object nodes (from EGG graph or tracks) ────────────────────────────
    _add_object_nodes(nodes, node_ids, tracks_df, egg_graph)

    # ── 2. Relation-fact nodes ────────────────────────────────────────────────
    if facts_df is not None and not facts_df.empty:
        for _, fr in facts_df.iterrows():
            fid = str(fr["fact_id"])
            _add_node({
                "node_id":    fid,
                "node_type":  "relation_fact",
                "predicate":  str(fr["predicate"]),
                "subject_id": str(fr["subject_id"]),
                "object_id":  _or_none(fr.get("object_id")),
                "status":     str(fr["status"]),
                "confidence": float(fr["confidence"]),
                "start_frame": int(fr["start_frame_idx"]),
                "end_frame":   int(fr["end_frame_idx"]),
                "source_stage": str(fr.get("source_stage", "")),
            })

    # ── 3. Subtask nodes + edges ──────────────────────────────────────────────
    subgoal_counter = [0]
    achieved_subtask_ids: Dict[str, str] = {}  # template_name → subtask_id (last achieved)
    # Track instance_name dedup: base_name → count of times seen
    subgoal_instance_counts: Dict[str, int] = {}

    if subtasks_df is not None and not subtasks_df.empty:
        subtasks_sorted = subtasks_df.sort_values("start_frame_idx").reset_index(drop=True)

        for _, sub in subtasks_sorted.iterrows():
            sid = str(sub["subtask_id"])
            tmpl = str(sub["template_name"])
            status = str(sub["status"])
            patient_str = _or_none(sub.get("patient_track_id"))
            patient_class = track_classes.get(patient_str, "") if patient_str else ""
            instance_label = str(sub.get("instance_label", tmpl)) if "instance_label" in sub.index else tmpl

            _add_node({
                "node_id":        sid,
                "node_type":      "subtask",
                "template_name":  tmpl,
                "instance_label": instance_label,
                "status":         status,
                "confidence":     float(sub["confidence"]),
                "start_frame":    int(sub["start_frame_idx"]),
                "end_frame":      int(sub["end_frame_idx"]),
                "agent":          _or_none(sub.get("agent_track_id")),
                "patient":        patient_str,
                "patient_class":  patient_class,
                "why":            str(sub.get("why_this_subtask", "")),
            })

            # involves edges: subtask → objects
            agent_str   = _or_none(sub.get("agent_track_id"))
            patient_str = _or_none(sub.get("patient_track_id"))
            if agent_str and f"obj_{agent_str}" in node_ids:
                _add_edge(sid, f"obj_{agent_str}", "involves", role="agent")
            if patient_str and f"obj_{patient_str}" in node_ids:
                _add_edge(sid, f"obj_{patient_str}", "involves", role="patient")

            # supports edges: facts → subtask
            try:
                sup_facts = json.loads(sub.get("supporting_facts", "[]") or "[]")
            except (json.JSONDecodeError, TypeError):
                sup_facts = []
            for fid in sup_facts:
                if fid and fid in node_ids:
                    _add_edge(fid, sid, "supports")

            # evidence_for edges: operations → subtask
            try:
                sup_ops = json.loads(sub.get("supporting_operations", "[]") or "[]")
            except (json.JSONDecodeError, TypeError):
                sup_ops = []
            for op_id in sup_ops:
                if op_id:
                    _add_edge(op_id, sid, "evidence_for")

            # achieves: subtask → subgoal (if status=achieved)
            if status == "achieved" and domain_config is not None:
                sg_tmpl = domain_config.subgoal_for_subtask(tmpl)
                if sg_tmpl is not None:
                    subgoal_counter[0] += 1
                    sg_id = f"sgoal_{subgoal_counter[0]:04d}"
                    # Build instance_name using patient object class
                    if patient_class and patient_class not in ("hand", ""):
                        base_instance = f"{sg_tmpl.name}({patient_class})"
                    else:
                        base_instance = sg_tmpl.name
                    # Deduplicate: append _2, _3, … for repeated instances
                    cnt = subgoal_instance_counts.get(base_instance, 0) + 1
                    subgoal_instance_counts[base_instance] = cnt
                    instance_name = base_instance if cnt == 1 else f"{base_instance}_{cnt}"
                    _add_node({
                        "node_id":            sg_id,
                        "node_type":          "subgoal",
                        "name":               sg_tmpl.name,
                        "instance_name":      instance_name,
                        "predicate":          sg_tmpl.predicate,
                        "patient_class":      patient_class,
                        "status":             "achieved",
                        "achieved_by_subtask": sid,
                    })
                    _add_edge(sid, sg_id, "achieves")

            if status == "achieved":
                achieved_subtask_ids[tmpl] = sid

            # depends_on edges
            if domain_config is not None:
                for req_tmpl in domain_config.required_before(tmpl):
                    req_sid = achieved_subtask_ids.get(req_tmpl)
                    if req_sid:
                        _add_edge(sid, req_sid, "depends_on",
                                  description=f"{tmpl} requires {req_tmpl}")

        # next_candidate edges: consecutive subtasks in temporal order
        slist = [str(r["subtask_id"]) for _, r in subtasks_sorted.iterrows()]
        for i in range(len(slist) - 1):
            _add_edge(slist[i], slist[i + 1], "next_candidate")

    # ── 4. Phase nodes + belongs_to_phase edges ───────────────────────────────
    if timeline is not None:
        for phase in timeline.get("phases", []):
            ph_id = f"ph_{phase['phase_id']}"
            _add_node({
                "node_id":     ph_id,
                "node_type":   "phase",
                "label":       phase["label"],
                "start_frame": phase["start_frame_idx"],
                "end_frame":   phase["end_frame_idx"],
                "confidence":  phase.get("confidence", 0.5),
                "dominant_op": phase.get("dominant_operation", ""),
            })
            # Link subtasks whose frame range overlaps this phase
            if subtasks_df is not None and not subtasks_df.empty:
                for _, sub in subtasks_df.iterrows():
                    if _overlaps(
                        int(sub["start_frame_idx"]), int(sub["end_frame_idx"]),
                        int(phase["start_frame_idx"]), int(phase["end_frame_idx"]),
                    ):
                        _add_edge(str(sub["subtask_id"]), ph_id, "belongs_to_phase")

    # ── 5. Constraint nodes from dependency rules ─────────────────────────────
    if domain_config is not None:
        for i, rule in enumerate(domain_config.dependency_rules):
            con_id = f"con_{i + 1:04d}"
            _add_node({
                "node_id":     con_id,
                "node_type":   "constraint",
                "subtask":     rule.subtask,
                "requires":    rule.requires,
                "description": rule.description,
            })
            # Link: all subtasks of template rule.subtask require this constraint
            if subtasks_df is not None and not subtasks_df.empty:
                for _, sub in subtasks_df[subtasks_df["template_name"] == rule.subtask].iterrows():
                    _add_edge(str(sub["subtask_id"]), con_id, "requires")

    # ── 6. Supersedes edges between consecutive support-state facts ───────────
    support_preds = {"resting", "carried", "released", "surface_contact", "support_changed"}
    support_facts_by_subject: Dict[str, List[Dict]] = {}
    for n in nodes:
        if n.get("node_type") == "relation_fact" and n.get("predicate") in support_preds:
            subj = str(n.get("subject_id", ""))
            if subj:
                support_facts_by_subject.setdefault(subj, []).append(n)
    for subj, sfacts in support_facts_by_subject.items():
        sfacts.sort(key=lambda n: n.get("start_frame", 0))
        for i in range(len(sfacts) - 1):
            _add_edge(sfacts[i]["node_id"], sfacts[i + 1]["node_id"], "supersedes")

    # ── 7. Invalidates edges: released fact → subgoal nodes ──────────────────
    released_facts = [
        n for n in nodes
        if n.get("node_type") == "relation_fact" and n.get("predicate") == "released"
    ]
    for rel_fact in released_facts:
        rel_subject = str(rel_fact.get("subject_id", ""))
        rel_frame   = int(rel_fact.get("start_frame", 0))
        for sg_node in [n for n in nodes if n.get("node_type") == "subgoal"]:
            sg_subtask_id = sg_node.get("achieved_by_subtask")
            if not sg_subtask_id:
                continue
            # Find the subtask node to get its patient_track_id
            sg_sub = next(
                (n for n in nodes if n.get("node_id") == sg_subtask_id), None
            )
            if sg_sub is None:
                continue
            patient = str(sg_sub.get("patient") or "")
            if patient != rel_subject:
                continue
            # Subgoal achievement frame (use subtask end_frame)
            achieved_frame = int(sg_sub.get("end_frame", 0))
            if rel_frame > achieved_frame:
                _add_edge(rel_fact["node_id"], sg_node["node_id"], "invalidates")
                sg_node["status"] = "achieved_then_released"
                sg_node["invalidated_at"] = rel_frame

    # ── Summary ───────────────────────────────────────────────────────────────
    achieved_subgoals = [
        n.get("instance_name", n["name"])
        for n in nodes
        if n["node_type"] == "subgoal" and n["status"] in ("achieved", "achieved_then_released")
    ]
    active_subtasks   = [n["node_id"] for n in nodes if n["node_type"] == "subtask" and n["status"] in ("in_progress", "candidate")]
    blocked_subtasks  = [n["node_id"] for n in nodes if n["node_type"] == "subtask" and n["status"] == "blocked"]
    invalidated_subgoals = [n.get("instance_name", n["name"]) for n in nodes if n["node_type"] == "subgoal" and n["status"] == "achieved_then_released"]

    return {
        "schema_version":  "1.0",
        "session_id":      session_id,
        "nodes":           nodes,
        "edges":           edges,
        "summary": {
            "total_nodes":           len(nodes),
            "total_edges":           len(edges),
            "achieved_subgoals":     achieved_subgoals,
            "invalidated_subgoals":  invalidated_subgoals,
            "active_subtasks":       active_subtasks,
            "blocked_subtasks":      blocked_subtasks,
            "node_type_counts":      _count_by(nodes, "node_type"),
            "edge_type_counts":      _count_by(edges, "edge_type"),
        },
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _add_object_nodes(
    nodes: List[Dict],
    node_ids: set,
    tracks_df: pd.DataFrame,
    egg_graph: Optional[Dict],
) -> None:
    """Populate object nodes from EGG graph and/or tracks."""
    seen_tids: set = set()

    # Prefer EGG graph objects (richer metadata)
    if egg_graph is not None:
        for obj in egg_graph.get("objects", []):
            tid = str(obj.get("track_id", obj.get("object_id", "")))
            if not tid or tid in seen_tids:
                continue
            seen_tids.add(tid)
            nid = f"obj_{tid}"
            if nid not in node_ids:
                node_ids.add(nid)
                nodes.append({
                    "node_id":      nid,
                    "node_type":    "object",
                    "track_id":     tid,
                    "class_label":  str(obj.get("class_label", obj.get("semantic_class", ""))),
                    "role":         str(obj.get("object_role", "")),
                })

    # Fill in any tracks not in EGG graph
    if tracks_df is not None and not tracks_df.empty:
        for tid, grp in tracks_df.groupby("track_id"):
            tid_str = str(tid)
            if tid_str in seen_tids:
                continue
            seen_tids.add(tid_str)
            nid = f"obj_{tid_str}"
            if nid not in node_ids:
                node_ids.add(nid)
                nodes.append({
                    "node_id":     nid,
                    "node_type":   "object",
                    "track_id":    tid_str,
                    "class_label": str(grp["semantic_class"].iloc[0]) if "semantic_class" in grp.columns else "",
                    "role":        str(grp["object_role"].iloc[0]) if "object_role" in grp.columns else "",
                })


def _or_none(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val)
    return None if s.lower() in {"nan", "none", "", "null"} else s


def _overlaps(s1: int, e1: int, s2: int, e2: int) -> bool:
    return s1 <= e2 and s2 <= e1


def _count_by(items: List[Dict], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        v = str(item.get(key, "unknown"))
        counts[v] = counts.get(v, 0) + 1
    return counts
