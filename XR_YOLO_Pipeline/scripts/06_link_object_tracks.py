#!/usr/bin/env python3
"""06_link_object_tracks.py — Link observations into persistent object tracks."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.tracking import link_observations_to_tracks, build_track_summary

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
):
    """Link object observations into object tracks."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    if not paths.object_observations.exists():
        console.print("[red]object_observations.csv not found. Run 05 first.[/red]")
        raise typer.Exit(1)

    obs_df = pd.read_csv(paths.object_observations)
    console.print(f"[bold]Linking {len(obs_df)} observations into tracks...[/bold]")

    if obs_df.empty:
        console.print("[yellow]No observations — writing empty tracks.[/yellow]")
        pd.DataFrame(columns=["track_id","observation_id","frame_idx","timestamp_ns",
                               "semantic_class","x","y","z","w","h","d","yaw",
                               "is_first_in_track","is_last_in_track","linkage_score"]
                    ).to_csv(paths.object_tracks, index=False)
        return

    t_cfg = thr.get("tracking", {})
    tracks_df = link_observations_to_tracks(
        obs_df,
        max_spatial_jump=float(t_cfg.get("max_spatial_jump_m", 0.8)),
        max_time_gap_ns=int(t_cfg.get("max_time_gap_ns", 5_000_000_000)),
        size_ratio_threshold=float(t_cfg.get("size_ratio_threshold", 3.0)),
        class_must_match=bool(t_cfg.get("class_must_match", True)),
    )

    tracks_df.to_csv(paths.object_tracks, index=False)
    console.print(f"[green]✓ Wrote {len(tracks_df)} track rows → {paths.object_tracks}[/green]")

    summary_df = build_track_summary(tracks_df)
    summary_df.to_csv(paths.track_summary, index=False)

    # Print summary table
    table = Table(title=f"Track Summary ({len(summary_df)} tracks)")
    for col in ["track_id", "semantic_class", "n_observations", "first_frame", "last_frame",
                "duration_ns", "mean_x", "mean_y", "mean_z"]:
        table.add_column(col, overflow="fold")
    for _, r in summary_df.head(20).iterrows():
        table.add_row(
            str(r["track_id"]), str(r["semantic_class"]),
            str(r["n_observations"]), str(r["first_frame"]), str(r["last_frame"]),
            f"{r['duration_ns']/1e9:.2f}s",
            f"{r['mean_x']:.3f}", f"{r['mean_y']:.3f}", f"{r['mean_z']:.3f}",
        )
    console.print(table)

    # Save debug JSON
    debug = {
        "n_tracks": len(summary_df),
        "n_observations": len(tracks_df),
        "tracks": summary_df.to_dict(orient="records"),
    }
    paths.track_debug.write_text(json.dumps(debug, indent=2))
    console.print(f"[green]✓ Debug JSON → {paths.track_debug}[/green]")


if __name__ == "__main__":
    app()
