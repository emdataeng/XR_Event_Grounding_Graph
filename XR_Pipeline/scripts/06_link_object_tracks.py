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
from src.vocabulary import Vocabulary
from src.run_metadata import build_run_metadata, save_run_metadata

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
    console.print(f"[bold]Loaded {len(obs_df)} observations.[/bold]")

    # Filter out classes flagged ignore_for_object_tracks in object_vocabulary.
    # Those observations remain in object_observations.csv for downstream use
    # (e.g. event detection, future verifier), but do not feed into tracking.
    vocab = Vocabulary.from_config(cfg)
    if not vocab.is_empty:
        ignore_classes = {e.canonical for e in vocab._entries if e.ignore_for_object_tracks}
        if ignore_classes:
            # Use canonical_class column if present (V2 schema), else semantic_class
            class_col = "canonical_class" if "canonical_class" in obs_df.columns else "semantic_class"
            before = len(obs_df)
            obs_df = obs_df[~obs_df[class_col].isin(ignore_classes)].reset_index(drop=True)
            dropped = before - len(obs_df)
            if dropped:
                console.print(
                    f"[dim]Excluded {dropped} observations with "
                    f"ignore_for_object_tracks classes: {sorted(ignore_classes)}[/dim]"
                )

    if obs_df.empty:
        console.print("[yellow]No observations — writing empty tracks.[/yellow]")
        pd.DataFrame(columns=["track_id","observation_id","frame_idx","timestamp_ns",
                               "semantic_class","x","y","z","w","h","d","yaw",
                               "is_first_in_track","is_last_in_track","linkage_score"]
                    ).to_csv(paths.object_tracks, index=False)
        return

    # Per-frame, per-class deduplication: keep only the top-N detections by
    # confidence for each (frame, class) pair. Suppresses Grounding DINO
    # duplicate boxes where the same object is detected multiple times per frame.
    d_cfg = thr.get("detection", {})
    max_per_class = int(d_cfg.get("max_detections_per_class_per_frame", 0))
    if max_per_class > 0:
        obs_df = (
            obs_df
            .sort_values("confidence", ascending=False)
            .groupby(["frame_idx", "semantic_class"], sort=False)
            .head(max_per_class)
            .reset_index(drop=True)
        )
        console.print(
            f"[dim]After per-frame deduplication (top {max_per_class} per class): "
            f"{len(obs_df)} observations remain.[/dim]"
        )

    t_cfg = thr.get("tracking", {})
    tracks_df = link_observations_to_tracks(
        obs_df,
        max_spatial_jump=float(t_cfg.get("max_spatial_jump_m", 0.8)),
        max_time_gap_ns=int(t_cfg.get("max_time_gap_ns", 5_000_000_000)),
        reid_max_age_ns=int(t_cfg.get("reid_max_age_ns", 60_000_000_000)),
        size_ratio_threshold=float(t_cfg.get("size_ratio_threshold", 3.0)),
        class_must_match=bool(t_cfg.get("class_must_match", True)),
    )

    # Minimum observations filter: remove tracks that appear in too few frames.
    # Short-lived tracks are typically false positives from the detector rather
    # than real objects. This threshold is tuned in thresholds.yaml and applies
    # to every session — set to 0 to disable.
    min_obs = int(t_cfg.get("min_track_observations", 0))
    if min_obs > 0:
        obs_counts = tracks_df.groupby("track_id")["observation_id"].count()
        valid_tids = obs_counts[obs_counts >= min_obs].index
        removed = set(obs_counts.index) - set(valid_tids)
        if removed:
            console.print(
                f"[dim]Removed {len(removed)} short-lived track(s) "
                f"(< {min_obs} observations): {sorted(removed)}[/dim]"
            )
        tracks_df = tracks_df[tracks_df["track_id"].isin(valid_tids)].reset_index(drop=True)

    # Enrich tracks with object_role from vocabulary taxonomy.
    # This lets downstream stages (events, operation events, SSP) use
    # role-based logic instead of hardcoded class-name string matching.
    if not vocab.is_empty:
        class_col = "canonical_class" if "canonical_class" in tracks_df.columns else "semantic_class"
        tracks_df["object_role"] = tracks_df[class_col].map(
            lambda cls: vocab.object_role(cls)
        )
    else:
        tracks_df["object_role"] = "workpiece"

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

    # Write run metadata for staleness detection by downstream stages.
    meta = build_run_metadata(
        session_id=session,
        stage="06_link_object_tracks",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={"n_tracks": len(summary_df), "n_track_rows": len(tracks_df)},
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
