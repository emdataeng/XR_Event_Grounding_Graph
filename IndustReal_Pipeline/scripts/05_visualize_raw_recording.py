#!/usr/bin/env python3
"""Generate lightweight debug visuals for the raw IndustReal pilot slice."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config
from src.raw_loader import load_od_labels
from src.raw_manifest import POSE_COLUMNS
from src.raw_viz import (
    save_od_overlay,
    save_pose_trajectory,
    save_rgb_depth_preview,
    save_stereo_preview,
)


def _sample_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if len(df) <= n:
        return df
    indices = sorted({math.floor(i * (len(df) - 1) / max(1, n - 1)) for i in range(n)})
    return df.iloc[indices]


def _translations(df: pd.DataFrame) -> list[tuple[float, float, float]]:
    points = []
    for _, row in df.iterrows():
        flat = [float(row[col]) for col in POSE_COLUMNS]
        points.append((flat[3], flat[7], flat[11]))
    return points


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--slice-id", type=str, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    latest = load_latest_slice(paths)
    slice_id = args.slice_id or latest["slice_id"]
    manifests_dir = paths.slice_manifests_dir(slice_id)
    slice_dir = paths.slice_workdir(slice_id)
    visuals_dir = paths.slice_visuals_dir(slice_id)
    visuals_dir.mkdir(parents=True, exist_ok=True)

    output_summary = {"slice_id": slice_id, "clips": []}
    for manifest_path in sorted(manifests_dir.glob("*_raw_manifest.csv")):
        clip = manifest_path.name.replace("_raw_manifest.csv", "")
        clip_dir = slice_dir / clip
        df = pd.read_csv(manifest_path)
        od_labels = load_od_labels(clip_dir / "OD_labels.json")
        clip_visual_dir = visuals_dir / clip
        clip_visual_dir.mkdir(parents=True, exist_ok=True)
        for _, row in _sample_rows(df, int(cfg["visualization"]["n_samples_per_clip"])).iterrows():
            frame_name = str(row["frame_name"])
            label = od_labels.get(frame_name)
            gaze_xy = (int(row["gaze_x"]), int(row["gaze_y"])) if row["gaze_x"] or row["gaze_y"] else None
            save_rgb_depth_preview(
                Path(str(row["rgb_path"])),
                Path(str(row["depth_path"])),
                clip_visual_dir / f"{frame_name[:-4]}_rgb_depth.png",
                bbox_xyxy=(label or {}).get("bbox_xyxy"),
                bbox_label=(label or {}).get("state_name"),
                gaze_xy=gaze_xy,
                title=f"{clip} {frame_name}",
            )
            save_stereo_preview(
                Path(str(row["stereo_left_path"])),
                Path(str(row["stereo_right_path"])),
                clip_visual_dir / f"{frame_name[:-4]}_stereo.png",
                title=f"{clip} {frame_name}",
            )
            save_od_overlay(
                Path(str(row["rgb_path"])),
                clip_visual_dir / f"{frame_name[:-4]}_od_overlay.png",
                bbox_xyxy=(label or {}).get("bbox_xyxy"),
                state_name=(label or {}).get("state_name"),
                gaze_xy=gaze_xy,
            )
        save_pose_trajectory(
            _translations(df),
            clip_visual_dir / "pose_trajectory.png",
            title=f"{clip} camera trajectory",
        )
        output_summary["clips"].append(
            {"clip": clip, "visual_dir": str(clip_visual_dir), "n_frames": len(df)}
        )

    print(json.dumps(output_summary, indent=2))


if __name__ == "__main__":
    main()
