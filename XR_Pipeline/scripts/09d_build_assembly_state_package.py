#!/usr/bin/env python3
"""09d_build_assembly_state_package.py — Build assembly state package.

Consolidates state facts, subtask events, assembly graph, and workflow timeline
into a single reasoning-layer input package.

Output
------
  graphs/assembly_state_package.json
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.assembly_state_package import build_assembly_state_package
from src.domain_config import load_domain_config
from src.run_metadata import build_run_metadata, save_run_metadata

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Build the assembly state package for the reasoning layer."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Load inputs ───────────────────────────────────────────────────────────
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

    assembly_graph = None
    if paths.assembly_graph.exists():
        with open(paths.assembly_graph) as f:
            assembly_graph = json.load(f)
        console.print(f"[dim]Assembly graph: {assembly_graph['summary']['total_nodes']} nodes[/dim]")
    else:
        console.print("[yellow]assembly_graph.json not found — run 10e first[/yellow]")

    timeline = None
    if paths.workflow_timeline.exists():
        with open(paths.workflow_timeline) as f:
            timeline = json.load(f)

    domain = load_domain_config(cfg=cfg)
    if domain:
        console.print(f"[cyan]Domain '{domain.domain_name}' loaded[/cyan]")

    # ── Build package ─────────────────────────────────────────────────────────
    pkg = build_assembly_state_package(
        facts_df=facts_df,
        subtasks_df=subtasks_df,
        assembly_graph=assembly_graph,
        timeline=timeline,
        domain_config=domain,
        session_id=session,
    )

    ev = pkg["evidence_summary"]
    console.print(f"\n[bold]Assembly state package:[/bold]")
    console.print(f"  Active facts:      {ev['total_active_facts']}")
    console.print(f"  Active subtasks:   {ev['total_active_subtasks']}")
    console.print(f"  Achieved subgoals: {ev['total_achieved_subgoals']}")
    console.print(f"  Blocked:           {ev['total_blocked']}")
    console.print(f"  Current phase:     [cyan]{pkg['current_assembly_phase']}[/cyan]")
    if pkg["likely_next_subtasks"]:
        console.print(f"  Likely next: {[t['template_name'] for t in pkg['likely_next_subtasks']]}")

    # ── Write output ──────────────────────────────────────────────────────────
    paths.assembly_state_package.write_text(json.dumps(pkg, indent=2))
    console.print(f"[green]✓ assembly_state_package.json → {paths.assembly_state_package}[/green]")

    # ── Run metadata ──────────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="09d_build_assembly_state_package",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            **ev,
            "current_phase": pkg["current_assembly_phase"],
            "domain_name":   domain.domain_name if domain else None,
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
