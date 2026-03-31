#!/usr/bin/env python3
"""09b_build_scene_state_package.py — Build the Scene State Package (SSP).

Produces a normalised reasoning-layer input contract from all upstream
pipeline outputs.  The SSP is a self-contained JSON document that the
reasoning layer can consume without knowing anything about the underlying
perception stack (GroundingDINO, YOLO, depth blobs, or any future backend).

Input prerequisites (must exist):
  object_tracks.csv         — 06_link_object_tracks.py
  object_observations.csv   — 05_build_object_observations.py
  event_windows.csv         — 07_build_event_windows.py
  events.csv                — 08_generate_event_summaries.py  (optional enrichment)
  event_object_roles.csv    — 08_generate_event_summaries.py

Output:
  graphs/scene_state_package.json   (Level-2 Traceable contract)

Contract compliance:
  Level 1 — Minimal reasoning-ready  : header + entities + relations
  Level 2 — Traceable reasoning      : + observations + hypotheses +
                                         provenance + constraints   ← this script

The reasoning layer should receive the SSP and NEVER consume raw masks,
free-form text, or detector-specific output formats directly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.scene_state_package import (
    build_scene_state_package,
    save_scene_state_package,
    load_scene_state_package,
)

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001", help="Session identifier"),
    config:  str = typer.Option(None,          help="Path to pipeline.yaml override"),
):
    """Build scene_state_package.json from all pipeline outputs."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Check prerequisites ───────────────────────────────────────────────────
    required = [
        ("object_tracks.csv",       paths.object_tracks),
        ("object_observations.csv", paths.object_observations),
        ("event_windows.csv",       paths.event_windows),
        ("event_object_roles.csv",  paths.event_object_roles),
    ]
    for name, p in required:
        if not p.exists():
            console.print(f"[red]{name} not found. Run preceding scripts first.[/red]")
            raise typer.Exit(1)

    # ── Load inputs ───────────────────────────────────────────────────────────
    tracks_df      = pd.read_csv(paths.object_tracks)
    obs_df         = pd.read_csv(paths.object_observations)
    roles_df       = pd.read_csv(paths.event_object_roles)

    # event_windows.csv carries primary_track_ids, frame indices, trigger_reason.
    # events.csv (from script 08) adds summary and event_pos fields.
    # Merge on event_id so the SSP builder gets all fields; fall back gracefully
    # if events.csv is absent (script 08 not yet run).
    events_df = pd.read_csv(paths.event_windows)
    if paths.events_csv.exists():
        enrichment = pd.read_csv(paths.events_csv)[
            ["event_id", "summary", "event_pos_x", "event_pos_y", "event_pos_z"]
        ]
        events_df = events_df.merge(enrichment, on="event_id", how="left")

    console.print(
        f"[bold]Building Scene State Package[/bold] | "
        f"{tracks_df['track_id'].nunique()} tracks  "
        f"{len(obs_df)} observations  "
        f"{len(events_df)} events"
    )

    # ── Build ─────────────────────────────────────────────────────────────────
    cfg["session_id"] = session   # make session_id available inside builders
    pkg = build_scene_state_package(
        session_id=session,
        tracks_df=tracks_df,
        obs_df=obs_df,
        events_df=events_df,
        roles_df=roles_df,
        cfg=cfg,
        thr=thr,
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    save_scene_state_package(pkg, paths.scene_state_package)
    console.print(
        f"[green]✓ scene_state_package.json written → "
        f"{paths.scene_state_package}[/green]"
    )

    # ── Verify round-trip ─────────────────────────────────────────────────────
    loaded = load_scene_state_package(paths.scene_state_package)
    assert loaded["schema_version"] == pkg["schema_version"]
    assert loaded["scene_id"] == pkg["scene_id"]
    console.print("[green]✓ Round-trip serialisation verified.[/green]")

    # ── Summary table ─────────────────────────────────────────────────────────
    n_entities     = len(pkg["entities"])
    n_relations    = len(pkg["relations"])
    n_hypotheses   = len(pkg["hypotheses"])
    n_observations = len(pkg["observations"])

    table = Table(title="Scene State Package — contract summary")
    table.add_column("Section",       style="bold cyan")
    table.add_column("Count",         justify="right")
    table.add_column("Notes",         style="dim")

    table.add_row("entities",     str(n_entities),
                  "persistent tracked objects")
    table.add_row("relations",    str(n_relations),
                  "accepted candidate facts (observed + derived)")
    table.add_row("hypotheses",   str(n_hypotheses),
                  "_CANDIDATE events + low-confidence relations")
    table.add_row("observations", str(n_observations),
                  "raw detector hits (for traceability)")

    console.print(table)

    # Active entities from state_summary
    active = pkg.get("state_summary", {}).get("active_entities", [])
    if active:
        console.print(f"  Active entities (last {5} frames): {active}")

    # Top salient relations
    salient = pkg.get("state_summary", {}).get("salient_relations", [])
    if salient:
        console.print("  Salient relations:")
        for s in salient:
            console.print(f"    {s}")

    console.print(
        f"\n  schema_version : {pkg['schema_version']}\n"
        f"  scene_id       : {pkg['scene_id']}\n"
        f"  timestamp      : {pkg['timestamp']}\n"
        f"  time_window    : {pkg['time_window']['start']}  →  "
        f"{pkg['time_window']['end']}\n"
        f"  frames         : {pkg['time_window']['frames_aggregated']}"
    )


if __name__ == "__main__":
    app()
