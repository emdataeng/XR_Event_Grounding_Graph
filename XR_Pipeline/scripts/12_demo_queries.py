#!/usr/bin/env python3
"""12_demo_queries.py — Run demo queries against the EGG graph."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
from rich.console import Console
from rich.panel import Panel

from src.config import PipelinePaths, load_pipeline_config
from src.egg import load_egg
from src.pruning import answer_query

app = typer.Typer()
console = Console()

DEMO_QUERIES = [
    "What moved?",
    "What objects appeared?",
    "Which events happened in workstation_A?",
    "Where was the laptop last seen?",
    "Where was the mouse last seen?",
    "Where was the monitor last seen?",
    "Where was the hands last seen?",
]


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
):
    """Run demo queries against the EGG graph and display answers."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)

    if not paths.egg_graph.exists():
        console.print("[red]egg_graph.json not found. Run 09 first.[/red]")
        raise typer.Exit(1)

    graph = load_egg(paths.egg_graph)
    console.print(
        f"[bold]EGG Graph:[/bold] {len(graph['objects'])} objects, "
        f"{len(graph['events'])} events, {len(graph['rooms'])} rooms"
    )

    results = []
    for q in DEMO_QUERIES:
        subgraph, answer = answer_query(graph, q)
        results.append({"query": q, "answer": answer,
                        "subgraph_objects": len(subgraph["objects"]),
                        "subgraph_events": len(subgraph["events"])})
        console.print(Panel(
            f"[dim]Q:[/dim] {q}\n[bold green]A:[/bold green] {answer}\n"
            f"[dim]Subgraph: {len(subgraph['objects'])} objects, {len(subgraph['events'])} events[/dim]",
            title=f"Query {DEMO_QUERIES.index(q)+1}/{len(DEMO_QUERIES)}",
        ))

    # Save results
    out = paths.queries_dir / "demo_query_results.json"
    out.write_text(json.dumps(results, indent=2))
    console.print(f"[green]✓ Demo results → {out}[/green]")


if __name__ == "__main__":
    app()
