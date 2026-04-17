#!/usr/bin/env python3
"""12_demo_queries.py — Run demo queries against the EGG graph and operation layer."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.egg import load_egg
from src.pruning import answer_query
from src.scene_state_package import load_scene_state_package
from src.workflow_queries import answer_workflow_query
from src.domain_config import load_domain_config
from src.run_metadata import build_run_metadata, save_run_metadata

app = typer.Typer()
console = Console()

# ── Primitive graph queries (answered against EGG graph) ──────────────────────
GRAPH_QUERIES = [
    "What moved?",
    "What objects appeared?",
    "Which events happened in workstation_A?",
]

# ── Workflow queries (answered against operation_events.csv + SSP + timeline) ──
# These are the business-relevant questions for industrial process understanding.
WORKFLOW_QUERIES = [
    "What step is happening now?",
    "What object is being manipulated?",
    "What changed in the scene?",
    "Which operation has the strongest evidence?",
    "What is the current workflow phase?",
    # Phase 3 timeline-aware queries
    "How many phases were there?",
    "What phase transition just happened?",
    "What happened before this phase?",
]


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Run demo queries against the EGG graph and workflow operation layer."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)

    # D2: load domain config and build domain-aware query list
    domain = load_domain_config(cfg=cfg)
    workflow_queries = list(WORKFLOW_QUERIES)
    if domain:
        console.print(
            f"[cyan]Domain '{domain.domain_name}' v{domain.domain_version}: "
            f"adding {len(domain.workflow_phases)} phase queries[/cyan]"
        )
        for phase in domain.workflow_phases:
            workflow_queries.append(f"Was the '{phase.label}' phase reached?")
    else:
        console.print("[dim]No domain config — using generic workflow queries[/dim]")

    if not paths.egg_graph.exists():
        console.print("[red]egg_graph.json not found. Run 09 first.[/red]")
        raise typer.Exit(1)

    # ── Load EGG graph ────────────────────────────────────────────────────────
    graph = load_egg(paths.egg_graph)
    console.print(
        f"[bold]EGG Graph:[/bold] {len(graph['objects'])} objects, "
        f"{len(graph['events'])} events, {len(graph['rooms'])} rooms"
    )

    # ── Load operation events (optional) ─────────────────────────────────────
    ops_path = paths.objects_dir / "operation_events.csv"
    ops_df: pd.DataFrame | None = None
    if ops_path.exists():
        ops_df = pd.read_csv(ops_path)
        console.print(f"[dim]Operation events: {len(ops_df)} rows[/dim]")
    else:
        console.print(
            "[dim]operation_events.csv not found — "
            "workflow queries will give limited answers.[/dim]"
        )

    # ── Load SSP for workflow phase / state_summary ────────────────────────────
    ssp: dict | None = None
    if paths.scene_state_package.exists():
        ssp = load_scene_state_package(paths.scene_state_package)

    # ── Load workflow timeline (Phase 3 — optional) ───────────────────────────
    timeline: dict | None = None
    if paths.workflow_timeline.exists():
        with open(paths.workflow_timeline) as f:
            timeline = json.load(f)
        summary = timeline.get("summary", {})
        console.print(
            f"[dim]Workflow timeline: {summary.get('total_phases', 0)} phases, "
            f"dominant='{summary.get('dominant_phase', 'idle')}', "
            f"sequence={summary.get('phase_sequence', [])}[/dim]"
        )
    else:
        console.print(
            "[dim]workflow_timeline.json not found — "
            "run 10c for timeline-aware answers.[/dim]"
        )

    # ── Graph queries ─────────────────────────────────────────────────────────
    results = []
    console.print("\n[bold cyan]── Primitive graph queries ──[/bold cyan]")
    for q in GRAPH_QUERIES:
        subgraph, answer = answer_query(graph, q)
        results.append({
            "query": q,
            "layer": "graph",
            "answer": answer,
            "subgraph_objects": len(subgraph["objects"]),
            "subgraph_events": len(subgraph["events"]),
        })
        console.print(Panel(
            f"[dim]Q:[/dim] {q}\n[bold green]A:[/bold green] {answer}\n"
            f"[dim]Subgraph: {len(subgraph['objects'])} objects, "
            f"{len(subgraph['events'])} events[/dim]",
            title=f"Graph Query {GRAPH_QUERIES.index(q)+1}/{len(GRAPH_QUERIES)}",
        ))

    # ── Workflow queries ───────────────────────────────────────────────────────
    console.print("\n[bold cyan]── Workflow queries ──[/bold cyan]")
    for qi, q in enumerate(workflow_queries):
        answer = answer_workflow_query(q, ops_df, ssp, graph, timeline=timeline)
        results.append({
            "query": q,
            "layer": "workflow",
            "answer": answer,
        })
        console.print(Panel(
            f"[dim]Q:[/dim] {q}\n[bold green]A:[/bold green] {answer}",
            title=f"Workflow Query {qi + 1}/{len(workflow_queries)}",
        ))

    # ── Operation events table ────────────────────────────────────────────────
    if ops_df is not None and not ops_df.empty:
        table = Table(title="All Detected Operations")
        table.add_column("ID");      table.add_column("Type");     table.add_column("Agent")
        table.add_column("Object");  table.add_column("Frames");   table.add_column("Conf")
        for _, r in ops_df.iterrows():
            table.add_row(
                str(r["operation_id"]),
                str(r["operation_type"]),
                str(r["agent_track_id"] or "–"),
                str(r["object_track_id"] or "–"),
                f"{r['start_frame_idx']}→{r['end_frame_idx']}",
                f"{r['confidence']:.2f}",
            )
        console.print(table)

    # ── Save results ──────────────────────────────────────────────────────────
    out = paths.queries_dir / "demo_query_results.json"
    out.write_text(json.dumps(results, indent=2))
    console.print(f"[green]✓ Results → {out}[/green]")

    # ── Write run metadata ────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="12_demo_queries",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "n_graph_queries":    len(GRAPH_QUERIES),
            "n_workflow_queries": len(workflow_queries),
            "n_results":          len(results),
            "timeline_loaded":    timeline is not None,
            "domain_name":        domain.domain_name if domain else None,
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
