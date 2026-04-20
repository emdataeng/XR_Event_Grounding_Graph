#!/usr/bin/env python3
"""11b_build_assembly_review.py — Assembly-focused review report.

Reads assembly_state_package.json + assembly_graph.json and produces:
  - reviews/assembly/assembly_review.json  — structured review dict
  - reviews/assembly/assembly_review.md    — human-readable summary

Output
------
  reviews/assembly/assembly_review.json
  reviews/assembly/assembly_review.md
"""
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.assembly_reasoner import reason
from src.run_metadata import build_run_metadata, save_run_metadata

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Build the assembly review report from state package and graph."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Load inputs ───────────────────────────────────────────────────────────
    pkg: Optional[Dict] = None
    if paths.assembly_state_package.exists():
        with open(paths.assembly_state_package) as f:
            pkg = json.load(f)
        ev = pkg.get("evidence_summary", {})
        console.print(
            f"[dim]State package: {ev.get('total_active_facts', 0)} facts, "
            f"{ev.get('total_active_subtasks', 0)} subtasks[/dim]"
        )
    else:
        console.print("[yellow]assembly_state_package.json not found — run 09d first[/yellow]")
        pkg = {}

    graph: Optional[Dict] = None
    if paths.assembly_graph.exists():
        with open(paths.assembly_graph) as f:
            graph = json.load(f)
        console.print(
            f"[dim]Assembly graph: {graph['summary']['total_nodes']} nodes, "
            f"{graph['summary']['total_edges']} edges[/dim]"
        )
    else:
        console.print("[yellow]assembly_graph.json not found — run 10e first[/yellow]")

    # ── Run full symbolic reasoning ────────────────────────────────────────────
    report = reason(pkg, graph, query="full_report")

    # ── Build review dict ─────────────────────────────────────────────────────
    review = _build_review(pkg, graph, report, session)

    # ── Print summary ─────────────────────────────────────────────────────────
    console.print(f"\n[bold]Assembly Review — {session}[/bold]")
    console.print(f"  Phase:             [cyan]{review['current_phase']}[/cyan]")
    console.print(f"  Active facts:      {review['active_fact_count']}")
    console.print(f"  Active subtasks:   {review['active_subtask_count']}")
    console.print(f"  Achieved subgoals: {review['achieved_subgoal_count']}")
    console.print(f"  Blocked subtasks:  {review['blocked_count']}")
    if review["likely_next"]:
        console.print(f"  Likely next:       {[n['template_name'] for n in review['likely_next']]}")
    if review.get("why_no_active_step"):
        from rich.markup import escape as _esc
        console.print(f"  [dim]{_esc(review['why_no_active_step'])}[/dim]")

    diag = review.get("diagnostics", {})
    if diag.get("weak_areas"):
        console.print("\n[yellow]Output quality warnings:[/yellow]")
        for w in diag["weak_areas"]:
            console.print(f"  [yellow]⚠ {w}[/yellow]")

    _print_subtask_table(review["subtask_timeline"])
    _print_constraint_table(review["constraint_status"])

    # ── Write JSON ────────────────────────────────────────────────────────────
    paths.assembly_reviews_dir.mkdir(parents=True, exist_ok=True)
    paths.assembly_review_json.write_text(json.dumps(review, indent=2))
    console.print(f"[green]✓ assembly_review.json → {paths.assembly_review_json}[/green]")

    # ── Write markdown ────────────────────────────────────────────────────────
    md = _render_markdown(review)
    paths.assembly_review_md.write_text(md)
    console.print(f"[green]✓ assembly_review.md → {paths.assembly_review_md}[/green]")

    # ── Run metadata ──────────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="11b_build_assembly_review",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "active_fact_count":     review["active_fact_count"],
            "active_subtask_count":  review["active_subtask_count"],
            "achieved_subgoal_count": review["achieved_subgoal_count"],
            "blocked_count":         review["blocked_count"],
            "current_phase":         review["current_phase"],
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


# ── Review builder ─────────────────────────────────────────────────────────────

def _build_review(
    pkg: Dict,
    graph: Optional[Dict],
    report: Dict,
    session_id: str,
) -> Dict[str, Any]:
    ev = pkg.get("evidence_summary", {})

    # Subtask timeline: all subtasks sorted by start frame
    subtask_timeline: List[Dict] = []
    all_subtasks = _all_subtask_nodes(graph) if graph else []
    for sub in sorted(all_subtasks, key=lambda s: s.get("start_frame", 0)):
        subtask_timeline.append({
            "subtask_id":    sub["node_id"],
            "template_name": sub.get("template_name", ""),
            "status":        sub.get("status", ""),
            "confidence":    sub.get("confidence", 0.0),
            "start_frame":   sub.get("start_frame", 0),
            "end_frame":     sub.get("end_frame", 0),
            "agent":         sub.get("agent"),
            "patient":       sub.get("patient"),
        })

    # Graph delta: node type distribution
    graph_delta: Dict[str, int] = {}
    if graph:
        graph_delta = graph["summary"].get("node_type_counts", {})

    constraint_status = report.get("constraint_status", {})

    # ── Diagnostics ───────────────────────────────────────────────────────────
    diagnostics = _build_diagnostics(pkg, subtask_timeline)

    return {
        "schema_version":        "1.0",
        "session_id":            session_id,
        "current_phase":         report.get("current_phase", "idle"),
        "active_fact_count":     ev.get("total_active_facts", 0),
        "active_subtask_count":  ev.get("total_active_subtasks", 0),
        "achieved_subgoal_count": ev.get("total_achieved_subgoals", 0),
        "blocked_count":         ev.get("total_blocked", 0),
        "achieved_subgoals":     pkg.get("achieved_subgoals", []),
        "candidate_subgoals":    pkg.get("candidate_subgoals", []),
        "object_relations":      pkg.get("object_relations", []),
        "state_transitions":     pkg.get("state_transitions", []),
        "blocked_subgoals":      pkg.get("blocked_subgoals", []),
        "likely_next":           pkg.get("likely_next_subtasks", []),
        "why_no_active_step":    pkg.get("why_no_active_step"),
        "subtask_timeline":      subtask_timeline,
        "graph_node_distribution": graph_delta,
        "constraint_status":     constraint_status,
        "reasoning_trace":       report.get("reasoning_trace", []),
        "unresolved_ambiguities": pkg.get("unresolved_ambiguities", []),
        "diagnostics":           diagnostics,
    }


def _all_subtask_nodes(graph: Dict) -> List[Dict]:
    return [n for n in graph.get("nodes", []) if n.get("node_type") == "subtask"]


def _build_diagnostics(pkg: Dict, subtask_timeline: List[Dict]) -> Dict[str, Any]:
    """Build diagnostic flags that highlight output quality issues."""
    diag: Dict[str, Any] = {}

    # Check for hold-heavy output (all subtasks same template)
    template_names = [s["template_name"] for s in subtask_timeline]
    unique_templates = list(dict.fromkeys(template_names))
    diag["hold_heavy"] = (
        len(template_names) > 1 and len(unique_templates) == 1 and unique_templates[0] == "hold_part"
    )
    diag["dominant_template"] = unique_templates[0] if len(unique_templates) == 1 else None

    # Check for generic/repetitive subgoals
    achieved = pkg.get("achieved_subgoals", [])
    subgoal_names = [g.get("instance_name", g.get("name", "")) for g in achieved]
    unique_subgoals = list(dict.fromkeys(subgoal_names))
    diag["generic_subgoals"] = len(subgoal_names) > len(unique_subgoals)
    diag["subgoal_variety"] = len(unique_subgoals)
    diag["subgoal_names"] = subgoal_names

    # Check for missing expected state changes
    active_facts = pkg.get("active_facts", [])
    predicates_seen = {f["predicate"] for f in active_facts}
    diag["has_holding_facts"]     = "holding" in predicates_seen
    diag["has_placement_facts"]   = any(p in predicates_seen for p in ("released", "resting", "placed_on_candidate"))
    diag["has_contact_facts"]     = any(p in predicates_seen for p in ("in_contact", "touching_candidate"))
    diag["has_candidate_facts"]   = any(f["predicate"] in ("touching_candidate", "near") for f in active_facts)

    # Inter-object relation diagnostics
    obj_rels = pkg.get("object_relations", [])
    diag["has_inter_object_relations"] = len(obj_rels) > 0
    diag["inter_object_relation_count"] = len(obj_rels)
    diag["co_held_count"]    = sum(1 for r in obj_rels if r["predicate"] == "co_held")
    diag["in_contact_count"] = sum(1 for r in obj_rels if r["predicate"] == "in_contact")
    cand_subgoals = pkg.get("candidate_subgoals", [])
    diag["candidate_subgoal_count"] = len(cand_subgoals)
    diag["has_candidate_subgoals"] = len(cand_subgoals) > 0

    # Main limitation summary
    limitations: List[str] = []
    if not diag["has_inter_object_relations"]:
        limitations.append("No inter-object relations detected — CONTACT operations absent and no co-held pairs found.")
    elif diag["co_held_count"] > 0 and diag["in_contact_count"] == 0:
        limitations.append(
            f"Only co_held evidence ({diag['co_held_count']} pair(s)) — no strong CONTACT operation detected. "
            "Assembly-level contact remains candidate."
        )
    if not diag["has_placement_facts"]:
        limitations.append("No placement facts — PUT_DOWN not detected; placement subgoals absent.")
    diag["main_limitations"] = limitations

    # Identify weak areas
    weak_areas: List[str] = []
    if diag["hold_heavy"]:
        weak_areas.append("All subtasks are hold_part — no PICK_UP/INSERT/ATTACH operations detected.")
    if diag["generic_subgoals"]:
        weak_areas.append(f"Repeated subgoal instances: {subgoal_names}")
    if not diag["has_placement_facts"]:
        weak_areas.append("No placement facts (released/resting after manipulation) — PUT_DOWN not detected.")
    if not diag["has_contact_facts"]:
        weak_areas.append("No contact facts — CONTACT/INTERACT operations not detected.")
    if not diag["has_inter_object_relations"]:
        weak_areas.append("No inter-object relations — relation-driven assembly progress not detectable.")
    diag["weak_areas"] = weak_areas

    return diag


# ── Rich console helpers ───────────────────────────────────────────────────────

def _print_subtask_table(timeline: List[Dict]) -> None:
    if not timeline:
        return
    table = Table(title="Subtask Timeline")
    table.add_column("ID");           table.add_column("Template")
    table.add_column("Status");       table.add_column("Frames")
    table.add_column("Conf")
    for sub in timeline:
        status_color = {
            "achieved": "green", "in_progress": "cyan",
            "candidate": "yellow", "blocked": "red",
        }.get(sub["status"], "white")
        table.add_row(
            sub["subtask_id"],
            sub["template_name"],
            f"[{status_color}]{sub['status']}[/{status_color}]",
            f"{sub['start_frame']}→{sub['end_frame']}",
            f"{sub['confidence']:.2f}",
        )
    console.print(table)


def _print_constraint_table(constraint_status: Dict) -> None:
    details = constraint_status.get("details", {})
    if not details:
        return
    table = Table(title="Constraint Satisfaction")
    table.add_column("Constraint");   table.add_column("Satisfied")
    table.add_column("Subtask");      table.add_column("Requires")
    for key, info in details.items():
        ok = info.get("satisfied", False)
        table.add_row(
            key,
            "[green]✓[/green]" if ok else "[red]✗[/red]",
            info.get("subtask", ""),
            info.get("requires", ""),
        )
    console.print(table)


# ── Markdown renderer ──────────────────────────────────────────────────────────

def _render_markdown(review: Dict) -> str:
    lines = [
        f"# Assembly Review — {review['session_id']}",
        "",
        "## Summary",
        f"- **Current phase:** {review['current_phase']}",
        f"- **Active facts:** {review['active_fact_count']}",
        f"- **Active subtasks:** {review['active_subtask_count']}",
        f"- **Achieved subgoals:** {review['achieved_subgoal_count']}",
        f"- **Blocked subtasks:** {review['blocked_count']}",
        "",
    ]

    if review.get("why_no_active_step"):
        lines += ["## Current Step", f"> {review['why_no_active_step']}", ""]

    if review["achieved_subgoals"]:
        lines.append("## Achieved Subgoals")
        for sg in review["achieved_subgoals"]:
            instance = sg.get("instance_name") or sg["name"]
            patient = f" ({sg['patient_class']})" if sg.get("patient_class") else ""
            lines.append(f"- **{instance}**{patient} — predicate: `{sg.get('predicate', '')}`")
        lines.append("")

    if review.get("candidate_subgoals"):
        lines.append("## Candidate Subgoals (inter-object, weak evidence)")
        for sg in review["candidate_subgoals"]:
            instance = sg.get("instance_name") or sg["name"]
            lines.append(f"- **{instance}** — predicate: `{sg.get('predicate', '')}` (candidate)")
        lines.append("")

    if review.get("object_relations"):
        lines.append("## Inter-Object Relations")
        for rel in review["object_relations"]:
            lines.append(
                f"- `{rel['predicate']}({rel['subject_id']}, {rel['object_id']})` "
                f"frames {rel['start_frame']}–{rel['end_frame']} "
                f"conf={rel['confidence']:.2f} [{rel['status']}]"
            )
        lines.append("")

    if review.get("state_transitions"):
        co_held_trans = [t for t in review["state_transitions"] if t["predicate"] in ("co_held_started", "co_held_ended")]
        if co_held_trans:
            lines.append("## Relation Transitions")
            for t in co_held_trans:
                obj_part = f"+{t['object_id']}" if t.get("object_id") else ""
                lines.append(f"- `{t['predicate']}({t['subject_id']}{obj_part})` at frame {t['frame']}")
            lines.append("")

    if review["blocked_subgoals"]:
        lines.append("## Blocked Subgoals")
        for sg in review["blocked_subgoals"]:
            lines.append(f"- {sg}")
        lines.append("")

    if review["likely_next"]:
        lines.append("## Likely Next Subtasks")
        for n in review["likely_next"]:
            prereqs = n.get("prerequisites_met", [])
            prereq_str = f" (prereqs: {prereqs})" if prereqs else ""
            lines.append(f"- **{n['template_name']}**{prereq_str}: {n.get('description', '')}")
        lines.append("")

    if review["subtask_timeline"]:
        lines += [
            "## Subtask Timeline",
            "",
            "| ID | Template | Status | Frames | Confidence |",
            "|----|----------|--------|--------|------------|",
        ]
        for sub in review["subtask_timeline"]:
            lines.append(
                f"| {sub['subtask_id']} | {sub['template_name']} "
                f"| {sub['status']} | {sub['start_frame']}→{sub['end_frame']} "
                f"| {sub['confidence']:.2f} |"
            )
        lines.append("")

    cs = review.get("constraint_status", {})
    details = cs.get("details", {})
    if details:
        lines += [
            "## Constraint Satisfaction",
            f"- Satisfied: {cs.get('satisfied', 0)}",
            f"- Violated: {cs.get('violated', 0)}",
            "",
        ]
        for key, info in details.items():
            mark = "✓" if info.get("satisfied") else "✗"
            lines.append(f"- {mark} `{key}`: {info.get('description', '')}")
        lines.append("")

    if review["graph_node_distribution"]:
        lines.append("## Graph Node Distribution")
        for ntype, count in review["graph_node_distribution"].items():
            lines.append(f"- {ntype}: {count}")
        lines.append("")

    if review["unresolved_ambiguities"]:
        lines.append("## Unresolved Ambiguities")
        for amb in review["unresolved_ambiguities"]:
            lines.append(f"- [{amb['type']}] {amb.get('predicate') or amb.get('subtask_id', '')} "
                         f"(conf={amb.get('confidence', 'N/A')})")
        lines.append("")

    diag = review.get("diagnostics", {})
    if diag:
        lines.append("## Output Quality Diagnostics")
        weak = diag.get("weak_areas", [])
        if weak:
            lines.append("### Weak Areas")
            for w in weak:
                lines.append(f"- ⚠ {w}")
            lines.append("")
        limits = diag.get("main_limitations", [])
        if limits:
            lines.append("### Main Limitations")
            for lim in limits:
                lines.append(f"- {lim}")
            lines.append("")
        lines += [
            "### Signal Coverage",
            f"- Holding facts: {'✓' if diag.get('has_holding_facts') else '✗'}",
            f"- Placement facts: {'✓' if diag.get('has_placement_facts') else '✗'}",
            f"- Contact facts: {'✓' if diag.get('has_contact_facts') else '✗'}",
            f"- Candidate/proximity facts: {'✓' if diag.get('has_candidate_facts') else '✗'}",
            f"- Inter-object relations: {'✓' if diag.get('has_inter_object_relations') else '✗'} ({diag.get('inter_object_relation_count', 0)} total, {diag.get('co_held_count', 0)} co_held)",
            f"- Candidate subgoals: {'✓' if diag.get('has_candidate_subgoals') else '✗'} ({diag.get('candidate_subgoal_count', 0)} total)",
            f"- Subgoal variety: {diag.get('subgoal_variety', 0)} unique instance(s)",
            "",
        ]

    if review["reasoning_trace"]:
        lines += ["## Reasoning Trace", ""]
        for step in review["reasoning_trace"]:
            lines.append(f"- {step}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    app()
