"""assembly_reasoner.py — Symbolic assembly reasoner (Phase 6).

Reads the assembly state package (and optionally the full assembly graph)
and answers structured assembly-awareness queries using deterministic
symbolic rules — no LLM calls, no model downloads.

Supported queries
-----------------
  what_step_now       — most recent active/candidate subtask
  what_is_achieved    — all achieved subgoals + their evidence
  what_is_blocked     — blocked subtasks + unmet dependencies
  what_changed        — facts/subtasks with start_frame in recent N frames
  likely_next         — pending subtasks with all prerequisites met
  why_current_step    — evidence chain for the active subtask
  full_report         — all of the above in one dict
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


# ── Public API ────────────────────────────────────────────────────────────────

def reason(
    assembly_state_package: Dict[str, Any],
    assembly_graph: Optional[Dict[str, Any]] = None,
    query: str = "full_report",
    recent_frame_window: int = 20,
) -> Dict[str, Any]:
    """Run symbolic reasoning over the assembly state package.

    Parameters
    ----------
    assembly_state_package : output of build_assembly_state_package()
    assembly_graph         : output of build_assembly_graph() (optional, for evidence traces)
    query                  : one of the supported query strings or 'full_report'
    recent_frame_window    : number of frames considered 'recent' for what_changed

    Returns
    -------
    Reasoning result dict with answers and reasoning_trace.
    """
    pkg   = assembly_state_package or {}
    graph = assembly_graph

    trace: List[str] = []

    # Build quick index structures
    subtask_nodes  = _subtask_nodes(graph)
    subgoal_nodes  = _subgoal_nodes(graph)
    edge_index     = _build_edge_index(graph)

    result: Dict[str, Any] = {
        "query":           query,
        "session_id":      pkg.get("session_id", "unknown"),
        "reasoning_trace": trace,
    }

    def _run(q: str) -> Dict[str, Any]:
        if q == "what_step_now":
            return _what_step_now(pkg, subtask_nodes, edge_index, trace)
        elif q == "what_is_achieved":
            return _what_is_achieved(pkg, subgoal_nodes, edge_index, trace)
        elif q == "what_is_blocked":
            return _what_is_blocked(pkg, subtask_nodes, trace)
        elif q == "what_changed":
            return _what_changed(pkg, recent_frame_window, trace)
        elif q == "likely_next":
            return _likely_next(pkg, trace)
        elif q == "why_current_step":
            return _why_current_step(pkg, subtask_nodes, edge_index, trace)
        else:
            trace.append(f"Unknown query '{q}' — running full_report")
            return {}

    if query == "full_report":
        result["current_step"]      = _what_step_now(pkg, subtask_nodes, edge_index, trace)
        result["achieved"]          = _what_is_achieved(pkg, subgoal_nodes, edge_index, trace)
        result["blocked"]           = _what_is_blocked(pkg, subtask_nodes, trace)
        result["recent_changes"]    = _what_changed(pkg, recent_frame_window, trace)
        result["likely_next"]       = _likely_next(pkg, trace)
        result["current_step_evidence"] = _why_current_step(pkg, subtask_nodes, edge_index, trace)
        result["current_phase"]     = pkg.get("current_assembly_phase", "idle")
        result["constraint_status"] = _constraint_status(pkg, trace)
    else:
        result.update(_run(query))

    return result


def answer_assembly_query(query: str, pkg: Dict, graph: Optional[Dict] = None) -> str:
    """Return a human-readable string answer for a natural-language-style query."""
    q = query.lower().strip()

    # Map natural language to structured query.
    # "next" is checked BEFORE "step" so "likely next step" routes correctly.
    if any(k in q for k in ("next", "upcoming", "after")):
        result = reason(pkg, graph, query="likely_next")
        nxt = result.get("likely_next_subtasks", [])
        if nxt:
            names = ", ".join(n["template_name"] for n in nxt)
            return f"Likely next: {names}"
        return "No likely next subtask determined."

    elif any(k in q for k in ("step", "happening", "active", "now")):
        result = reason(pkg, graph, query="what_step_now")
        step = result.get("step")
        if step:
            conf = step.get("confidence", 0)
            tmpl = step.get("template_name", "unknown")
            return f"Current step: {tmpl} (confidence {conf:.0%}, status={step.get('status')})"
        return "No active assembly step detected."

    elif any(k in q for k in ("achieved", "assembled", "done", "completed")):
        result = reason(pkg, graph, query="what_is_achieved")
        goals = result.get("achieved_subgoals", [])
        if goals:
            names = ", ".join(g["name"] for g in goals)
            return f"Achieved: {names}"
        return "No subgoals achieved yet."

    elif any(k in q for k in ("blocked", "blocking", "stuck")):
        result = reason(pkg, graph, query="what_is_blocked")
        blocked = result.get("blocked_steps", [])
        if blocked:
            return f"Blocked steps: {[b['subtask_id'] for b in blocked]}"
        return "No blocked steps."

    elif any(k in q for k in ("evidence", "why", "support")):
        result = reason(pkg, graph, query="why_current_step")
        ev = result.get("evidence", [])
        if ev:
            return f"Evidence: {'; '.join(str(e) for e in ev[:3])}"
        return "No supporting evidence available."

    elif any(k in q for k in ("changed", "change", "different")):
        result = reason(pkg, graph, query="what_changed")
        changes = result.get("recent_changes", [])
        if changes:
            return f"{len(changes)} recent change(s): {[c.get('description','') for c in changes[:3]]}"
        return "No recent changes detected."

    else:
        result = reason(pkg, graph, query="full_report")
        phase  = result.get("current_phase", "idle")
        step   = result.get("current_step", {}).get("step")
        step_s = f", step={step['template_name']}" if step else ""
        return f"Phase: {phase}{step_s}"


# ── Query implementations ─────────────────────────────────────────────────────

def _what_step_now(
    pkg: Dict, subtask_nodes: Dict, edge_index: Dict, trace: List[str]
) -> Dict[str, Any]:
    """Return the most recent active/candidate subtask."""
    active = pkg.get("active_subtasks", [])
    if not active:
        trace.append("what_step_now: no active subtasks in package")
        return {"step": None, "answer": "No active step."}

    # Most recent by end_frame
    best = max(active, key=lambda s: s["frames"][1] if s.get("frames") else 0)
    trace.append(f"what_step_now: selected {best['subtask_id']} ({best['template_name']}) conf={best['confidence']:.2f}")
    return {
        "step":   best,
        "answer": f"Current step: {best['template_name']} (conf={best['confidence']:.0%})",
    }


def _what_is_achieved(
    pkg: Dict, subgoal_nodes: Dict, edge_index: Dict, trace: List[str]
) -> Dict[str, Any]:
    """Return all achieved subgoals."""
    achieved = pkg.get("achieved_subgoals", [])
    trace.append(f"what_is_achieved: {len(achieved)} subgoal(s) achieved")
    return {
        "achieved_subgoals": achieved,
        "answer": (
            f"Achieved: {', '.join(g['name'] for g in achieved)}"
            if achieved else "Nothing achieved yet."
        ),
    }


def _what_is_blocked(
    pkg: Dict, subtask_nodes: Dict, trace: List[str]
) -> Dict[str, Any]:
    """Return blocked subtasks with unmet dependency info.

    Blocked subtasks are stored in the graph's subtask nodes (status='blocked'),
    not in pkg['active_subtasks'] (which only holds in_progress/candidate).
    We check both the graph nodes and the package's blocked_subgoals list.
    """
    # From graph nodes (most complete source)
    blocked_from_graph = [
        n for n in subtask_nodes.values() if n.get("status") == "blocked"
    ]
    # Also check active_subtasks in package (edge case: status may have been set there)
    blocked_from_pkg = [
        s for s in (pkg.get("active_subtasks") or []) if s.get("status") == "blocked"
    ]
    # Merge, deduplicate by subtask_id / node_id
    seen: set = set()
    blocked: List[Dict] = []
    for s in blocked_from_graph + blocked_from_pkg:
        sid = s.get("node_id") or s.get("subtask_id", "")
        if sid and sid not in seen:
            seen.add(sid)
            blocked.append(s)

    constraint_sat = pkg.get("constraint_satisfaction", {})

    violated = [k for k, v in constraint_sat.items() if not v.get("satisfied")]
    trace.append(f"what_is_blocked: {len(blocked)} blocked subtasks, {len(violated)} violated constraints")

    return {
        "blocked_steps":         blocked,
        "violated_constraints":  violated,
        "answer": (
            f"Blocked: {[b['subtask_id'] for b in blocked]}; "
            f"constraints violated: {violated}"
            if blocked or violated else "Nothing blocked."
        ),
    }


def _what_changed(
    pkg: Dict, window: int, trace: List[str]
) -> Dict[str, Any]:
    """Return facts and subtasks with recent start frames."""
    changes: List[Dict] = []

    # Find max frame across active facts
    all_frames = [f["frames"][0] for f in pkg.get("active_facts", []) if f.get("frames")]
    all_frames += [s["frames"][0] for s in pkg.get("active_subtasks", []) if s.get("frames")]
    if not all_frames:
        trace.append("what_changed: no frame data available")
        return {"recent_changes": [], "answer": "No frame data available."}

    max_f = max(all_frames)
    cutoff = max_f - window

    for fact in pkg.get("active_facts", []):
        fs = fact.get("frames", [0, 0])[0]
        if fs >= cutoff:
            changes.append({
                "type":        "fact",
                "description": f"{fact['predicate']}({fact['subject_id']},{fact.get('object_id', '')})",
                "frame":       fs,
                "confidence":  fact.get("confidence", 0),
            })

    for sub in pkg.get("active_subtasks", []):
        fs = sub.get("frames", [0, 0])[0]
        if fs >= cutoff:
            changes.append({
                "type":        "subtask",
                "description": f"{sub['template_name']} {sub.get('status', '')}",
                "frame":       fs,
                "confidence":  sub.get("confidence", 0),
            })

    changes.sort(key=lambda c: c["frame"], reverse=True)
    trace.append(f"what_changed: {len(changes)} change(s) in last {window} frames")

    return {
        "recent_changes": changes,
        "answer": (
            f"{len(changes)} change(s) in last {window} frames"
            if changes else "No recent changes."
        ),
    }


def _likely_next(pkg: Dict, trace: List[str]) -> Dict[str, Any]:
    """Return likely next subtasks from package."""
    nxt = pkg.get("likely_next_subtasks", [])
    trace.append(f"likely_next: {len(nxt)} candidate(s)")
    return {
        "likely_next_subtasks": nxt,
        "answer": (
            f"Likely next: {', '.join(n['template_name'] for n in nxt)}"
            if nxt else "No likely next subtask."
        ),
    }


def _why_current_step(
    pkg: Dict, subtask_nodes: Dict, edge_index: Dict, trace: List[str]
) -> Dict[str, Any]:
    """Trace evidence for the current active step."""
    active = pkg.get("active_subtasks", [])
    if not active:
        return {"evidence": [], "answer": "No active step to trace."}

    best = max(active, key=lambda s: s["frames"][1] if s.get("frames") else 0)
    sid  = best.get("subtask_id")
    why  = best.get("why", "")

    # Collect evidence from the graph's evidence_for edges
    evidence: List[str] = [why] if why else []
    if edge_index and sid:
        for tgt, etype, props in edge_index.get(sid, []):
            pass
        for src, tgt, etype, props in _all_edges_to(edge_index, sid):
            if etype == "evidence_for":
                evidence.append(f"operation: {src}")
            elif etype == "supports":
                evidence.append(f"fact: {src}")

    trace.append(f"why_current_step: {len(evidence)} evidence item(s) for {sid}")
    return {
        "subtask_id": sid,
        "evidence":   evidence[:8],
        "answer":     f"Evidence for {best.get('template_name')}: {'; '.join(evidence[:3])}" if evidence else f"No evidence trace for {sid}.",
    }


def _constraint_status(pkg: Dict, trace: List[str]) -> Dict[str, Any]:
    sat = pkg.get("constraint_satisfaction", {})
    n_ok  = sum(1 for v in sat.values() if v.get("satisfied"))
    n_bad = sum(1 for v in sat.values() if not v.get("satisfied"))
    trace.append(f"constraint_status: {n_ok} satisfied, {n_bad} violated")
    return {"satisfied": n_ok, "violated": n_bad, "details": sat}


# ── Graph index helpers ───────────────────────────────────────────────────────

def _subtask_nodes(graph: Optional[Dict]) -> Dict[str, Dict]:
    if not graph:
        return {}
    return {n["node_id"]: n for n in graph.get("nodes", []) if n["node_type"] == "subtask"}


def _subgoal_nodes(graph: Optional[Dict]) -> Dict[str, Dict]:
    if not graph:
        return {}
    return {n["node_id"]: n for n in graph.get("nodes", []) if n["node_type"] == "subgoal"}


def _build_edge_index(graph: Optional[Dict]) -> Dict[str, List]:
    """Build adjacency index: node_id → list of (target, edge_type, props)."""
    if not graph:
        return {}
    idx: Dict[str, List] = {}
    for edge in graph.get("edges", []):
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        etype = edge.get("edge_type", "")
        props = {k: v for k, v in edge.items() if k not in ("source", "target", "edge_type", "edge_id")}
        idx.setdefault(src, []).append((tgt, etype, props))
    return idx


def _all_edges_to(edge_index: Dict, target: str):
    """Return all (src, tgt, etype, props) tuples whose target == target."""
    result = []
    for src, edges in edge_index.items():
        for tgt, etype, props in edges:
            if tgt == target:
                result.append((src, tgt, etype, props))
    return result
