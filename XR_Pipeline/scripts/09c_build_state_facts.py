#!/usr/bin/env python3
"""09c_build_state_facts.py — Build explicit state-facts layer.

Reads tracks, events, operation events, and support-state transitions and
converts them into a flat set of time-scoped, queryable facts.

Outputs
-------
  graphs/state_facts.json   — array of all facts (JSON)
  graphs/state_facts.csv    — flat table (CSV)
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.state_facts import compute_state_facts, facts_to_json
from src.domain_config import load_domain_config
from src.run_metadata import build_run_metadata, save_run_metadata

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Build the state-facts layer from tracks, events, and operations."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Load inputs ───────────────────────────────────────────────────────────
    tracks_df = pd.DataFrame()
    if paths.object_tracks.exists():
        tracks_df = pd.read_csv(paths.object_tracks)
        console.print(f"[dim]Tracks: {len(tracks_df)} rows[/dim]")
    else:
        console.print("[yellow]object_tracks.csv not found — presence facts will be empty[/yellow]")

    events_df = pd.DataFrame()
    # Prefer event_windows.csv — it has primary_track_ids, start/end frame columns
    # that state_facts.py relies on.  events.csv lacks those fields.
    if paths.event_windows.exists():
        events_df = pd.read_csv(paths.event_windows)
        console.print(f"[dim]Event windows: {len(events_df)} rows[/dim]")
    elif paths.events_csv.exists():
        events_df = pd.read_csv(paths.events_csv)
        console.print(f"[dim]Events (fallback): {len(events_df)} rows[/dim]")
    else:
        console.print("[yellow]No events file found — event facts will be empty[/yellow]")

    ops_df = pd.DataFrame()
    ops_path = paths.objects_dir / "operation_events.csv"
    if ops_path.exists():
        ops_df = pd.read_csv(ops_path)
        console.print(f"[dim]Operations: {len(ops_df)} rows[/dim]")
    else:
        console.print("[yellow]operation_events.csv not found — operation facts will be empty[/yellow]")

    support_df = None
    if paths.support_state_transitions.exists():
        support_df = pd.read_csv(paths.support_state_transitions)
        console.print(f"[dim]Support states: {len(support_df)} rows[/dim]")

    domain = load_domain_config(cfg=cfg)
    if domain:
        console.print(f"[cyan]Domain '{domain.domain_name}' loaded[/cyan]")
    else:
        console.print("[dim]No domain config — all predicates marked relevant[/dim]")

    # ── Compute facts ─────────────────────────────────────────────────────────
    facts_df = compute_state_facts(
        tracks_df=tracks_df,
        events_df=events_df,
        ops_df=ops_df,
        support_df=support_df,
        domain_config=domain,
    )
    console.print(f"\n[bold]State facts:[/bold] {len(facts_df)} total")

    if not facts_df.empty:
        counts = facts_df["predicate"].value_counts()
        for pred, cnt in counts.head(10).items():
            console.print(f"  {pred}: {cnt}")

    # ── Write outputs ─────────────────────────────────────────────────────────
    facts_df.to_csv(paths.state_facts_csv, index=False)
    console.print(f"[green]✓ state_facts.csv → {paths.state_facts_csv}[/green]")

    facts_list = facts_to_json(facts_df)
    pkg = {
        "schema_version": "1.0",
        "session_id":     session,
        "total_facts":    len(facts_list),
        "facts":          facts_list,
    }
    paths.state_facts_json.write_text(json.dumps(pkg, indent=2))
    console.print(f"[green]✓ state_facts.json → {paths.state_facts_json}[/green]")

    # ── Run metadata ──────────────────────────────────────────────────────────
    predicate_counts = facts_df["predicate"].value_counts().to_dict() if not facts_df.empty else {}
    meta = build_run_metadata(
        session_id=session,
        stage="09c_build_state_facts",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "total_facts":      len(facts_df),
            "predicate_counts": predicate_counts,
            "domain_name":      domain.domain_name if domain else None,
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
