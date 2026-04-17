#!/usr/bin/env python3
"""10_prune_egg_graph.py — Query and prune the EGG graph."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
from rich.console import Console
from rich.panel import Panel

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.egg import load_egg, save_egg
from src.pruning import answer_query
from src.run_metadata import (
    build_run_metadata, save_run_metadata,
    check_staleness, emit_staleness_warnings,
)

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    query:  str = typer.Option("What moved?", help="Natural language query"),
    force:  bool = typer.Option(False, "--force",
                                help="Continue even if upstream output is stale."),
):
    """Prune the EGG graph according to a query and save subgraph + answer."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # Staleness guard
    warnings = check_staleness(paths.processed_root, "09_build_egg_graph", cfg, thr)
    if not emit_staleness_warnings(warnings, console=console, force=force):
        raise typer.Exit(1)

    if not paths.egg_graph.exists():
        console.print("[red]egg_graph.json not found. Run 09 first.[/red]")
        raise typer.Exit(1)

    graph = load_egg(paths.egg_graph)
    console.print(f"[bold]Graph loaded:[/bold] {len(graph['objects'])} objects, {len(graph['events'])} events")
    console.print(f"[bold]Query:[/bold] {query}")

    subgraph, answer = answer_query(graph, query)

    # Save outputs
    save_egg(subgraph, paths.pruned_subgraph)
    result = {
        "query": query,
        "answer": answer,
        "subgraph_objects": len(subgraph["objects"]),
        "subgraph_events": len(subgraph["events"]),
    }
    paths.query_answer.write_text(json.dumps(result, indent=2))

    console.print(Panel(f"[bold green]Answer:[/bold green]\n{answer}", title="Query Result"))
    console.print(f"  Subgraph: {len(subgraph['objects'])} objects, {len(subgraph['events'])} events")
    console.print(f"[green]✓ pruned_subgraph.json → {paths.pruned_subgraph}[/green]")
    console.print(f"[green]✓ query_answer.json → {paths.query_answer}[/green]")

    # Write run metadata
    meta = build_run_metadata(
        session_id=session,
        stage="10_prune_egg_graph",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "query": query,
            "subgraph_objects": len(subgraph["objects"]),
            "subgraph_events": len(subgraph["events"]),
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
