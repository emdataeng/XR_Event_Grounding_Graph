#!/usr/bin/env python3
"""03_visualize_rgb_depth_pose.py — Sample RGB/depth visualizations and pose trajectory."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import numpy as np
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config
from src.io_utils import load_rgba, load_depth_npy, rgba_to_rgb
from src.viz import save_rgb_depth_overlay, save_pose_trajectory, save_point_cloud_screenshot
from src.geometry import deproject_depth_image, flat_to_matrix

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    n_samples: int = typer.Option(6, help="Number of sample frames to visualize"),
):
    """Save sample RGB/depth visualizations and pose trajectory."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    if not paths.frame_manifest.exists():
        console.print("[red]frame_manifest.csv not found. Run 01 first.[/red]")
        raise typer.Exit(1)

    df = pd.read_csv(paths.frame_manifest)
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]

    # Sample evenly across the session
    step = max(1, len(df) // n_samples)
    sample_rows = df.iloc[::step].head(n_samples)

    console.print(f"Visualizing {len(sample_rows)} sample frames...")

    for _, row in sample_rows.iterrows():
        fidx = int(row["frame_idx"])
        # Load RGB
        rp = _resolve(row["rgb_path"])
        try:
            rgba = load_rgba(rp, width=int(row["width"]), height=int(row["height"]))
            rgb = rgba_to_rgb(rgba)
        except Exception as e:
            console.print(f"  [yellow]WARN[/yellow] frame {fidx}: RGB load failed: {e}")
            continue

        # Load depth
        depth = None
        if row["depth_encoding"] not in ("none", "") and pd.notna(row["depth_path"]) and row["depth_path"]:
            dp = _resolve(row["depth_path"])
            depth = load_depth_npy(dp, width=int(row["width"]), height=int(row["height"]))

        out = paths.sample_vis_dir / f"frame_{fidx:06d}_rgb_depth.png"
        save_rgb_depth_overlay(rgb, depth, out, title=f"Frame {fidx} | ts={row['timestamp_ns']/1e9:.2f}s")
        console.print(f"  [green]✓[/green] {out.name}")

        # Point cloud for frames with depth
        if depth is not None:
            T = flat_to_matrix([row[c] for c in pose_cols])
            dh, dw = depth.shape
            # Use depth intrinsics (scale cx/cy to depth resolution)
            rgb_h, rgb_w = rgb.shape[:2]
            scale_x = dw / rgb_w
            scale_y = dh / rgb_h
            d_fx = float(row["fx"]) * scale_x
            d_fy = float(row["fy"]) * scale_y
            d_cx = float(row["cx"]) * scale_x
            d_cy = float(row["cy"]) * scale_y

            pts = deproject_depth_image(
                depth,
                fx=d_fx, fy=d_fy, cx=d_cx, cy=d_cy,
                T_world_cam=T,
                depth_min=0.1, depth_max=4.0, stride=4,
            )
            # Sample colors from RGB at matching scaled coordinates
            ys = np.arange(0, dh, 4)
            xs = np.arange(0, dw, 4)
            yy, xx = np.meshgrid(ys, xs, indexing="ij")
            d_sub = depth[yy, xx]
            valid = (d_sub > 0.1) & (d_sub < 4.0)
            # Map depth pixel coords back to rgb pixel coords for color
            rgb_yy = np.clip((yy[valid] / scale_y).astype(int), 0, rgb_h - 1)
            rgb_xx = np.clip((xx[valid] / scale_x).astype(int), 0, rgb_w - 1)
            colors = rgb[rgb_yy, rgb_xx]

            pc_out = paths.debug_pc_dir / f"frame_{fidx:06d}_pointcloud.png"
            save_point_cloud_screenshot(pts, pc_out, colors=colors, title=f"Frame {fidx} point cloud")
            console.print(f"  [green]✓[/green] {pc_out.name} ({len(pts):,} pts)")

    # Pose trajectory
    pose_flat_list = df[pose_cols].values.tolist()
    traj_out = paths.sample_vis_dir / "camera_trajectory.png"
    save_pose_trajectory(pose_flat_list, traj_out)
    console.print(f"[green]✓ Camera trajectory saved:[/green] {traj_out.name}")

    # Print pose range
    translations = df[["T_world_cam_03", "T_world_cam_07", "T_world_cam_11"]].values
    console.print(f"\nCamera position range:")
    for i, axis in enumerate("XYZ"):
        console.print(f"  {axis}: [{translations[:, i].min():.3f}, {translations[:, i].max():.3f}] m")


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return PROJECT_ROOT.parent / p


if __name__ == "__main__":
    app()
