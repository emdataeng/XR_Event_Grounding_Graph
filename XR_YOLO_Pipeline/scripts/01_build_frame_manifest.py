#!/usr/bin/env python3
"""01_build_frame_manifest.py — Scan Quest 3 capture and build canonical frame_manifest.csv."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.progress import track as rich_track

from src.config import PipelinePaths, load_pipeline_config
from src.io_utils import scan_quest_capture, ticks_to_ns
from src.pose_utils import meta_to_pose_flat

app = typer.Typer()
console = Console()

# Consistent base for relative paths — must match what 02_validate_manifest uses (project_root.parent)
_PATH_BASE = Path(__file__).resolve().parent.parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001", help="Session ID"),
    config: str = typer.Option(None, help="Path to pipeline.yaml"),
):
    """Build canonical frame_manifest.csv from Quest 3 capture files."""
    cfg_path = Path(config) if config else None
    cfg = load_pipeline_config(cfg_path)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    raw_root = paths.raw_root
    console.print(f"[bold]Scanning Quest 3 capture:[/bold] {raw_root}")

    if not raw_root.exists():
        console.print(f"[red]ERROR: raw data directory not found: {raw_root}[/red]")
        raise typer.Exit(1)

    frames = scan_quest_capture(raw_root)
    if not frames:
        console.print("[red]ERROR: no frame metadata files found.[/red]")
        raise typer.Exit(1)

    console.print(f"Found [bold]{len(frames)}[/bold] frames")

    # Camera intrinsics from config (scaled to actual stored resolution)
    cam = cfg.get("camera", {})
    fx = float(cam.get("fx", 480.0))
    fy = float(cam.get("fy", 480.0))
    cx = float(cam.get("cx", 320.0))
    cy = float(cam.get("cy", 240.0))
    width = int(cam.get("width", 640))
    height = int(cam.get("height", 480))

    room_id = cfg.get("default_room_id", "workstation_A")

    # Use first frame ticks as reference for relative timestamps
    first_ticks = frames[0]["ticks"]

    rows = []
    for frame in rich_track(frames, description="Building manifest..."):
        meta = frame["meta"]
        ticks = frame["ticks"]
        ts_ns = ticks_to_ns(ticks, relative_to=first_ticks)

        rgba_path = frame["rgba_path"]
        depth_npy = frame["depth_npy_path"]
        depth_f32 = frame["depth_f32_path"]

        # Choose depth path and encoding
        if depth_npy is not None:
            depth_path = str(depth_npy.relative_to(_PATH_BASE)
                             if depth_npy.is_relative_to(_PATH_BASE)
                             else depth_npy)
            depth_encoding = "npy"
        elif depth_f32 is not None:
            depth_path = str(depth_f32.relative_to(_PATH_BASE)
                             if depth_f32.is_relative_to(_PATH_BASE)
                             else depth_f32)
            depth_encoding = "f32"
        else:
            depth_path = ""
            depth_encoding = "none"

        # Depth available check from metadata
        depth_count = meta.get("depth", {}).get("count", 0)
        if depth_count == 0:
            depth_path = ""
            depth_encoding = "none"

        rgb_path_rel = str(rgba_path.relative_to(_PATH_BASE)
                           if rgba_path.is_relative_to(_PATH_BASE)
                           else rgba_path)

        pose_flat = meta_to_pose_flat(meta)

        row = {
            "frame_idx": frame["frame_idx"],
            "timestamp_ns": ts_ns,
            "rgb_path": rgb_path_rel,
            "depth_path": depth_path,
            "depth_encoding": depth_encoding,
            "depth_scale": 1.0,
            "fx": fx, "fy": fy, "cx": cx, "cy": cy,
            "width": width, "height": height,
            "room_id": room_id,
            "source_stream": "quest3_capture",
            "notes": "",
        }
        # Add pose columns T_world_cam_00 ... T_world_cam_15
        for i, v in enumerate(pose_flat):
            row[f"T_world_cam_{i:02d}"] = v

        rows.append(row)

    df = pd.DataFrame(rows)

    # Reorder columns
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]
    base_cols = [
        "frame_idx", "timestamp_ns", "rgb_path", "depth_path",
        "depth_encoding", "depth_scale", "fx", "fy", "cx", "cy",
        "width", "height",
    ]
    all_cols = base_cols + pose_cols + ["room_id", "source_stream", "notes"]
    df = df[all_cols]

    out = paths.frame_manifest
    df.to_csv(out, index=False)
    console.print(f"[green]✓ Wrote frame_manifest.csv[/green] → {out}")
    console.print(f"  Rows: {len(df)}, Frames with depth: {(df['depth_encoding'] != 'none').sum()}")
    console.print(f"  Timestamp range: 0 → {df['timestamp_ns'].max():,} ns "
                  f"({df['timestamp_ns'].max()/1e9:.1f}s)")

    # Print a sample pose translation to sanity-check
    t = df[["T_world_cam_03", "T_world_cam_07", "T_world_cam_11"]].iloc[0].tolist()
    console.print(f"  First frame camera position: ({t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f})")


if __name__ == "__main__":
    app()
