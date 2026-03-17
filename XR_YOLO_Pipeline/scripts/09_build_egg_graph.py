#!/usr/bin/env python3
"""09_build_egg_graph.py — Build the EGG graph JSON from all pipeline outputs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config
from src.egg import build_egg_graph, save_egg, load_egg

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
):
    """Build egg_graph.json from tracks, events, and roles."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # Check prerequisites
    for name, p in [("object_tracks.csv", paths.object_tracks),
                    ("events.csv", paths.events_csv),
                    ("event_object_roles.csv", paths.event_object_roles)]:
        if not p.exists():
            console.print(f"[red]{name} not found. Run preceding scripts first.[/red]")
            raise typer.Exit(1)

    tracks_df = pd.read_csv(paths.object_tracks)
    events_df = pd.read_csv(paths.events_csv)
    roles_df = pd.read_csv(paths.event_object_roles)

    console.print(
        f"[bold]Building EGG graph[/bold] | "
        f"{tracks_df['track_id'].nunique()} tracks, "
        f"{len(events_df)} events, {len(roles_df)} roles"
    )

    room_id = cfg.get("default_room_id", "workstation_A")
    graph = build_egg_graph(
        session_id=session,
        tracks_df=tracks_df,
        events_df=events_df,
        event_object_roles_df=roles_df,
        room_id=room_id,
    )

    save_egg(graph, paths.egg_graph)
    console.print(f"[green]✓ egg_graph.json written → {paths.egg_graph}[/green]")

    # Verify round-trip
    loaded = load_egg(paths.egg_graph)
    assert len(loaded["objects"]) == len(graph["objects"])
    assert len(loaded["events"]) == len(graph["events"])

    console.print(f"  Rooms:          {len(graph['rooms'])}")
    console.print(f"  Objects:        {len(graph['objects'])}")
    console.print(f"  Events:         {len(graph['events'])}")
    console.print(f"  Event edges:    {len(graph['event_edges'])}")
    console.print(f"  Room edges:     {len(graph['room_edges'])}")
    console.print(f"  Temporal edges: {len(graph['temporal_edges'])}")
    console.print("[green]✓ Round-trip serialization verified.[/green]")


if __name__ == "__main__":
    app()
