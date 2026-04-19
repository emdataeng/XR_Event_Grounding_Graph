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

    return {
        "schema_version":        "1.0",
        "session_id":            session_id,
        "current_phase":         report.get("current_phase", "idle"),
        "active_fact_count":     ev.get("total_active_facts", 0),
        "active_subtask_count":  ev.get("total_active_subtasks", 0),
        "achieved_subgoal_count": ev.get("total_achieved_subgoals", 0),
        "blocked_count":         ev.get("total_blocked", 0),
        "achieved_subgoals":     pkg.get("achieved_subgoals", []),
        "blocked_subgoals":      pkg.get("blocked_subgoals", []),
        "likely_next":           pkg.get("likely_next_subtasks", []),
        "subtask_timeline":      subtask_timeline,
        "graph_node_distribution": graph_delta,
        "constraint_status":     constraint_status,
        "reasoning_trace":       report.get("reasoning_trace", []),
        "unresolved_ambiguities": pkg.get("unresolved_ambiguities", []),
    }


def _all_subtask_nodes(graph: Dict) -> List[Dict]:
    return [n for n in graph.get("nodes", []) if n.get("node_type") == "subtask"]


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

    if review["achieved_subgoals"]:
        lines.append("## Achieved Subgoals")
        for sg in review["achieved_subgoals"]:
            lines.append(f"- {sg['name']} (predicate: `{sg.get('predicate', '')}`)")
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

    if review["reasoning_trace"]:
        lines += ["## Reasoning Trace", ""]
        for step in review["reasoning_trace"]:
            lines.append(f"- {step}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    app()
