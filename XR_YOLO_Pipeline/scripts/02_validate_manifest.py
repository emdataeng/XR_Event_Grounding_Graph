#!/usr/bin/env python3
"""02_validate_manifest.py — Validate frame_manifest.csv completeness and correctness."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config
from src.pose_utils import is_valid_pose, poses_are_plausible
from src.io_utils import load_rgba, load_depth_npy

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    sample_size: int = typer.Option(5, help="Number of frames to sample for deep check"),
):
    """Validate frame_manifest.csv."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)

    if not paths.frame_manifest.exists():
        console.print("[red]ERROR: frame_manifest.csv not found. Run 01_build_frame_manifest.py first.[/red]")
        raise typer.Exit(1)

    df = pd.read_csv(paths.frame_manifest)
    console.print(f"[bold]Validating manifest[/bold] ({len(df)} rows)")

    report = {
        "total_frames": len(df),
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    # 1. Required columns
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]
    required = ["frame_idx", "timestamp_ns", "rgb_path", "depth_path",
                "fx", "fy", "cx", "cy", "width", "height"] + pose_cols
    missing_cols = [c for c in required if c not in df.columns]
    report["checks"]["required_columns"] = "PASS" if not missing_cols else f"FAIL: {missing_cols}"

    # 2. Timestamps monotonic
    mono = bool(df["timestamp_ns"].is_monotonic_increasing)
    report["checks"]["timestamps_monotonic"] = "PASS" if mono else "WARN"
    if not mono:
        report["warnings"].append("Timestamps are not monotonically increasing.")

    # 3. RGB files exist (check subset)
    sample_idx = df.sample(min(sample_size, len(df)), random_state=42).index
    raw_root = paths.raw_root
    project_root = Path(__file__).resolve().parent.parent

    rgb_ok = 0
    for idx in sample_idx:
        rp = df.loc[idx, "rgb_path"]
        p = Path(rp) if Path(rp).is_absolute() else project_root.parent / rp
        if p.exists():
            rgb_ok += 1
    report["checks"]["rgb_files_sample"] = f"{rgb_ok}/{len(sample_idx)} accessible"

    # 4. Depth files exist where encoding != none
    depth_rows = df[df["depth_encoding"] != "none"]
    n_with_depth = len(depth_rows)
    depth_ok = 0
    for idx in depth_rows.sample(min(sample_size, n_with_depth), random_state=42).index:
        dp = df.loc[idx, "depth_path"]
        p = Path(dp) if Path(dp).is_absolute() else project_root.parent / dp
        if p.exists():
            depth_ok += 1
    report["checks"]["depth_files_sample"] = (
        f"{depth_ok}/{min(sample_size, n_with_depth)} accessible ({n_with_depth} total with depth)"
    )

    # 5. Pose matrices valid
    pose_flat_all = []
    invalid_poses = 0
    for idx, row in df.iterrows():
        flat = [row[c] for c in pose_cols]
        if not is_valid_pose(flat):
            invalid_poses += 1
        else:
            pose_flat_all.append(flat)
    report["checks"]["pose_matrices_valid"] = (
        f"PASS ({len(df) - invalid_poses}/{len(df)} valid)"
        if invalid_poses == 0
        else f"WARN: {invalid_poses} invalid poses"
    )

    # 6. Pose plausibility
    if len(pose_flat_all) > 1:
        plausible = poses_are_plausible(pose_flat_all[:50])  # check first 50
        report["checks"]["pose_plausibility"] = "PASS" if plausible else "WARN: large jumps detected"
    else:
        report["checks"]["pose_plausibility"] = "SKIP: too few poses"

    # 7. Sample decode RGB + depth
    sample_decode_ok = 0
    for idx in list(sample_idx)[:3]:
        try:
            rp = df.loc[idx, "rgb_path"]
            p = Path(rp) if Path(rp).is_absolute() else project_root.parent / rp
            img = load_rgba(p)
            assert img.ndim == 3 and img.shape[2] == 4, f"Unexpected shape {img.shape}"
            assert img.shape[0] > 0 and img.shape[1] > 0
            sample_decode_ok += 1
        except Exception as e:
            report["warnings"].append(f"RGB decode failed for row {idx}: {e}")

    depth_decode_ok = 0
    for idx in list(depth_rows.sample(min(3, n_with_depth), random_state=0).index):
        try:
            dp = df.loc[idx, "depth_path"]
            p = Path(dp) if Path(dp).is_absolute() else project_root.parent / dp
            d = load_depth_npy(p)
            assert d is not None and d.ndim == 2
            assert np.nanmin(d) >= 0
            depth_decode_ok += 1
        except Exception as e:
            report["warnings"].append(f"Depth decode failed for row {idx}: {e}")

    report["checks"]["rgb_decode_sample"] = f"{sample_decode_ok}/3 decoded successfully"
    report["checks"]["depth_decode_sample"] = f"{depth_decode_ok}/3 decoded successfully"

    # ---- Print report ----
    table = Table(title="Manifest Validation")
    table.add_column("Check", style="bold")
    table.add_column("Result")
    for k, v in report["checks"].items():
        color = "green" if "PASS" in str(v) else ("yellow" if "WARN" in str(v) else "red")
        table.add_row(k, f"[{color}]{v}[/{color}]")
    console.print(table)

    for w in report["warnings"]:
        console.print(f"  [yellow]WARN[/yellow] {w}")
    for e in report["errors"]:
        console.print(f"  [red]ERROR[/red] {e}")

    # Save report
    out = paths.manifest_validation
    out.write_text(json.dumps(report, indent=2))
    console.print(f"\n[green]✓ Validation report saved:[/green] {out}")

    if report["errors"]:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
