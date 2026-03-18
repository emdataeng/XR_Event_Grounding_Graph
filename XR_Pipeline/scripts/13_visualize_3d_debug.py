#!/usr/bin/env python3
"""13_visualize_3d_debug.py — 3D debug visualizations: point clouds, object boxes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import numpy as np
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config
from src.io_utils import load_rgba, load_depth_npy, rgba_to_rgb
from src.geometry import deproject_depth_image, flat_to_matrix
from src.viz import save_point_cloud_screenshot, save_rgb_depth_overlay

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    n_frames: int = typer.Option(3, help="Number of frames to visualize"),
    try_open3d: bool = typer.Option(False, help="Attempt Open3D window (requires display)"),
):
    """Generate 3D debug visualizations from RGB-D frames."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    if not paths.frame_manifest.exists():
        console.print("[red]frame_manifest.csv not found. Run 01 first.[/red]")
        raise typer.Exit(1)

    df = pd.read_csv(paths.frame_manifest)
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]

    # Select frames with depth
    depth_rows = df[df["depth_encoding"] != "none"].reset_index(drop=True)
    if len(depth_rows) == 0:
        console.print("[yellow]No frames with depth. Cannot generate 3D debug.[/yellow]")
        return

    step = max(1, len(depth_rows) // n_frames)
    sample = depth_rows.iloc[::step].head(n_frames)
    console.print(f"Generating 3D debug for {len(sample)} frames...")

    all_points = []
    all_colors = []

    for _, row in sample.iterrows():
        fidx = int(row["frame_idx"])
        fx, fy = float(row["fx"]), float(row["fy"])
        cx, cy = float(row["cx"]), float(row["cy"])
        w, h = int(row["width"]), int(row["height"])
        T = flat_to_matrix([row[c] for c in pose_cols])

        rp = _resolve(row["rgb_path"])
        dp = _resolve(row["depth_path"])

        try:
            rgba = load_rgba(rp, width=w, height=h)
            rgb = rgba_to_rgb(rgba)
        except Exception as e:
            console.print(f"  [yellow]WARN[/yellow] frame {fidx}: RGB failed: {e}")
            continue

        depth = load_depth_npy(dp, width=w, height=h)
        if depth is None:
            console.print(f"  [yellow]WARN[/yellow] frame {fidx}: depth not available")
            continue

        dh, dw = depth.shape
        scale_x = dw / w
        scale_y = dh / h
        d_fx = fx * scale_x; d_fy = fy * scale_y
        d_cx = cx * scale_x; d_cy = cy * scale_y

        pts = deproject_depth_image(
            depth, fx=d_fx, fy=d_fy, cx=d_cx, cy=d_cy, T_world_cam=T,
            depth_min=0.1, depth_max=4.0, stride=3,
        )

        # Matching colors (sample from depth coordinates, map to rgb coordinates)
        ys = np.arange(0, dh, 3); xs = np.arange(0, dw, 3)
        yy, xx = np.meshgrid(ys, xs, indexing="ij")
        d_sub = depth[yy, xx]
        valid = (d_sub > 0.1) & (d_sub < 4.0)
        rgb_yy = np.clip((yy[valid] / scale_y).astype(int), 0, h - 1)
        rgb_xx = np.clip((xx[valid] / scale_x).astype(int), 0, w - 1)
        colors = rgb[rgb_yy, rgb_xx]

        console.print(f"  Frame {fidx}: {len(pts):,} points extracted")
        all_points.append(pts)
        all_colors.append(colors)

        # Per-frame matplotlib 3D screenshot
        out_pc = paths.debug_pc_dir / f"frame_{fidx:06d}_3d.png"
        save_point_cloud_screenshot(pts, out_pc, colors=colors, title=f"Frame {fidx} 3D")
        console.print(f"  [green]✓[/green] {out_pc.name}")

        # RGB-depth overlay
        out_rd = paths.debug_pc_dir / f"frame_{fidx:06d}_rgbd.png"
        save_rgb_depth_overlay(rgb, depth, out_rd, title=f"Frame {fidx}")
        console.print(f"  [green]✓[/green] {out_rd.name}")

    # Combined point cloud (first N frames merged)
    if all_points:
        merged_pts = np.concatenate(all_points, axis=0)
        merged_clr = np.concatenate(all_colors, axis=0)
        out_merged = paths.debug_pc_dir / "merged_pointcloud.png"
        save_point_cloud_screenshot(
            merged_pts, out_merged, colors=merged_clr,
            title=f"Merged point cloud ({len(merged_pts):,} pts, {len(all_points)} frames)"
        )
        console.print(f"[green]✓ Merged point cloud → {out_merged}[/green]")

    # Optional Open3D window
    if try_open3d and all_points:
        try:
            import open3d as o3d
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(merged_pts)
            pcd.colors = o3d.utility.Vector3dVector(merged_clr / 255.0)
            o3d.visualization.draw_geometries([pcd], window_name="EGG Debug Point Cloud")
        except Exception as e:
            console.print(f"[yellow]Open3D window failed: {e}[/yellow]")

    console.print("[bold green]3D debug complete.[/bold green]")


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return PROJECT_ROOT.parent / p


if __name__ == "__main__":
    app()
