#!/usr/bin/env python3
"""08_generate_event_summaries.py — Generate human-readable event summaries and object roles."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
import numpy as np
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config
from src.events import generate_event_summary

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
):
    """Generate event summaries and object role assignments."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    if not paths.event_windows.exists():
        console.print("[red]event_windows.csv not found. Run 07 first.[/red]")
        raise typer.Exit(1)
    if not paths.object_tracks.exists():
        console.print("[red]object_tracks.csv not found. Run 06 first.[/red]")
        raise typer.Exit(1)

    ew_df = pd.read_csv(paths.event_windows)
    tracks_df = pd.read_csv(paths.object_tracks)
    console.print(f"[bold]Generating summaries for {len(ew_df)} events...[/bold]")

    # Compute mean position per event (average of involved track positions at that time)
    events_rows = []
    role_rows = []

    for _, ev in ew_df.iterrows():
        summary, roles = generate_event_summary(ev, tracks_df)

        # Compute event anchor position: mean of involved track positions near event time
        import json as _json
        try:
            tids = _json.loads(ev["primary_track_ids"])
        except Exception:
            tids = []

        positions = []
        for tid in tids:
            t_rows = tracks_df[tracks_df["track_id"] == tid]
            if not t_rows.empty:
                # Closest observation to event time
                t_rows = t_rows.copy()
                t_rows["ts_diff"] = abs(t_rows["timestamp_ns"] - ev["start_ts_ns"])
                nearest = t_rows.nsmallest(1, "ts_diff").iloc[0]
                x, y, z = nearest["x"], nearest["y"], nearest["z"]
                if not (pd.isna(x) or pd.isna(y) or pd.isna(z)):
                    positions.append([float(x), float(y), float(z)])

        if positions:
            pos = np.mean(positions, axis=0)
            px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
        else:
            px, py, pz = 0.0, 0.0, 0.0

        source = cfg.get("event_summary_source", "rules")
        events_rows.append({
            "event_id": ev["event_id"],
            "event_type": ev["event_type"],
            "summary": summary,
            "start_ts_ns": int(ev["start_ts_ns"]),
            "end_ts_ns": int(ev["end_ts_ns"]),
            "room_id": ev.get("room_id", cfg.get("default_room_id", "workstation_A")),
            "event_pos_x": px,
            "event_pos_y": py,
            "event_pos_z": pz,
            "source": source,
            "confidence": float(ev.get("confidence", 0.5)),
        })
        role_rows.extend(roles)

    events_df = pd.DataFrame(events_rows)
    roles_df = pd.DataFrame(role_rows) if role_rows else pd.DataFrame(
        columns=["event_id", "track_id", "role", "role_description"]
    )

    events_df.to_csv(paths.events_csv, index=False)
    roles_df.to_csv(paths.event_object_roles, index=False)

    console.print(f"[green]✓ Wrote {len(events_df)} events → {paths.events_csv}[/green]")
    console.print(f"[green]✓ Wrote {len(roles_df)} role rows → {paths.event_object_roles}[/green]")

    # Sample summaries
    console.print("\n[bold]Sample event summaries:[/bold]")
    for _, r in events_df.head(5).iterrows():
        console.print(f"  [{r['event_type']}] {r['summary']}")


if __name__ == "__main__":
    app()
