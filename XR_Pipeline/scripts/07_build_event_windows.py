#!/usr/bin/env python3
"""07_build_event_windows.py — Detect coarse event windows from object tracks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.events import detect_event_windows
from src.vocabulary import Vocabulary
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
    force: bool = typer.Option(False, "--force", help="Continue even if upstream output is stale."),
):
    """Detect coarse event windows from object tracks."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # Staleness guard: warn if tracks were built under a different config.
    warnings = check_staleness(paths.processed_root, "06_link_object_tracks", cfg, thr)
    if not emit_staleness_warnings(warnings, console=console, force=force):
        raise typer.Exit(1)

    if not paths.object_tracks.exists():
        console.print("[red]object_tracks.csv not found. Run 06 first.[/red]")
        raise typer.Exit(1)

    tracks_df = pd.read_csv(paths.object_tracks)
    console.print(f"[bold]Building event windows from {len(tracks_df)} track rows...[/bold]")

    if tracks_df.empty:
        console.print("[yellow]No tracks — writing empty event windows.[/yellow]")
        pd.DataFrame(columns=["event_id","event_type","start_frame_idx","end_frame_idx",
                               "start_ts_ns","end_ts_ns","primary_track_ids",
                               "room_id","trigger_reason","confidence"]
                    ).to_csv(paths.event_windows, index=False)
        return

    e_cfg = thr.get("events", {})
    room_id = cfg.get("default_room_id", "workstation_A")

    # Pass hand classes from taxonomy so INTERACTION detection is role-driven,
    # not hardcoded to semantic_class == "hands".
    vocab = Vocabulary.from_config(cfg)
    hand_classes = vocab.classes_with_role("hand") if not vocab.is_empty else None

    events_df = detect_event_windows(
        tracks_df,
        min_move_distance_m=float(e_cfg.get("min_move_distance_m", 0.05)),
        near_threshold_m=float(e_cfg.get("near_threshold_m", 0.3)),
        disappear_frames=int(e_cfg.get("disappear_frames", 3)),
        event_merge_gap_ns=int(e_cfg.get("event_merge_gap_ns", 2_000_000_000)),
        room_id=room_id,
        position_smooth_window=int(e_cfg.get("position_smooth_window", 1)),
        hand_classes=hand_classes if hand_classes else None,
    )

    events_df.to_csv(paths.event_windows, index=False)
    console.print(f"[green]✓ Wrote {len(events_df)} event windows → {paths.event_windows}[/green]")

    # Summary table
    type_counts = events_df["event_type"].value_counts()
    table = Table(title="Event Type Distribution")
    table.add_column("Event Type"); table.add_column("Count")
    for et, cnt in type_counts.items():
        table.add_row(str(et), str(cnt))
    console.print(table)

    # Write run metadata.
    meta = build_run_metadata(
        session_id=session,
        stage="07_build_event_windows",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={"n_events": len(events_df)},
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
