#!/usr/bin/env python3
"""10e_build_assembly_graph.py — Build assembly graph.

Combines EGG graph, state facts, subtask events, workflow timeline, and domain
config into a derived assembly-aware graph with nodes (objects, facts, subtasks,
subgoals, phases, constraints) and typed edges.

Output
------
  graphs/assembly_graph.json
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.assembly_graph import build_assembly_graph
from src.domain_config import load_domain_config
from src.run_metadata import build_run_metadata, save_run_metadata

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Build the assembly graph from all upstream layers."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Load inputs ───────────────────────────────────────────────────────────
    tracks_df = pd.DataFrame()
    if paths.object_tracks.exists():
        tracks_df = pd.read_csv(paths.object_tracks)
        console.print(f"[dim]Tracks: {len(tracks_df)} rows[/dim]")

    facts_df = pd.DataFrame()
    if paths.state_facts_csv.exists():
        facts_df = pd.read_csv(paths.state_facts_csv)
        console.print(f"[dim]State facts: {len(facts_df)} rows[/dim]")
    else:
        console.print("[yellow]state_facts.csv not found — run 09c first[/yellow]")

    subtasks_df = pd.DataFrame()
    if paths.subtask_events.exists():
        subtasks_df = pd.read_csv(paths.subtask_events)
        console.print(f"[dim]Subtask events: {len(subtasks_df)} rows[/dim]")
    else:
        console.print("[yellow]subtask_events.csv not found — run 10d first[/yellow]")

    egg_graph = None
    if paths.egg_graph.exists():
        with open(paths.egg_graph) as f:
            egg_graph = json.load(f)
        console.print(f"[dim]EGG graph: {len(egg_graph.get('objects', []))} objects[/dim]")

    timeline = None
    if paths.workflow_timeline.exists():
        with open(paths.workflow_timeline) as f:
            timeline = json.load(f)
        console.print(
            f"[dim]Timeline: {timeline.get('summary', {}).get('total_phases', 0)} phases[/dim]"
        )

    domain = load_domain_config(cfg=cfg)
    if domain:
        console.print(f"[cyan]Domain '{domain.domain_name}' loaded[/cyan]")

    # ── Build graph ───────────────────────────────────────────────────────────
    graph = build_assembly_graph(
        tracks_df=tracks_df,
        facts_df=facts_df,
        subtasks_df=subtasks_df,
        egg_graph=egg_graph,
        timeline=timeline,
        domain_config=domain,
        session_id=session,
    )

    summary = graph["summary"]
    console.print(f"\n[bold]Assembly graph:[/bold]")
    console.print(f"  Nodes: {summary['total_nodes']}  Edges: {summary['total_edges']}")
    for ntype, cnt in summary["node_type_counts"].items():
        console.print(f"    {ntype}: {cnt}")
    console.print(f"  Achieved subgoals: {summary['achieved_subgoals']}")
    if summary["blocked_subtasks"]:
        console.print(f"  [yellow]Blocked subtasks: {len(summary['blocked_subtasks'])}[/yellow]")

    # ── Write output ──────────────────────────────────────────────────────────
    paths.assembly_graph.write_text(json.dumps(graph, indent=2))
    console.print(f"[green]✓ assembly_graph.json → {paths.assembly_graph}[/green]")

    # ── Run metadata ──────────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="10e_build_assembly_graph",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "total_nodes":       summary["total_nodes"],
            "total_edges":       summary["total_edges"],
            "node_type_counts":  summary["node_type_counts"],
            "achieved_subgoals": summary["achieved_subgoals"],
            "blocked_subtasks":  len(summary["blocked_subtasks"]),
            "domain_name":       domain.domain_name if domain else None,
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
