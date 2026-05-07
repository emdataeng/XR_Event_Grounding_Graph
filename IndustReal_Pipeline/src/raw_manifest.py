"""Manifest generation and validation for raw IndustReal pilot clips."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .hl2_pose import is_valid_pose_flat
from .raw_loader import ROOT_METADATA_FILES, discover_clip_streams, load_clip_bundle


POSE_COLUMNS = [f"pose_{i:02d}" for i in range(16)]
MANIFEST_COLUMNS = [
    "clip",
    "slice_order",
    "frame_idx",
    "frame_name",
    "timestamp_ns",
    "rgb_path",
    "depth_path",
    "stereo_left_path",
    "stereo_right_path",
    "gaze_x",
    "gaze_y",
    "has_hands",
    "source_archive",
    "split",
    "notes",
] + POSE_COLUMNS


def build_raw_manifest(
    clip_dir: Path,
    *,
    source_archive: str,
    split: str,
) -> pd.DataFrame:
    bundle = load_clip_bundle(clip_dir)
    streams = bundle["streams"]
    rgb_frames = streams["rgb"]
    rows: list[dict[str, Any]] = []
    for slice_order, frame_idx in enumerate(sorted(rgb_frames)):
        frame_name = rgb_frames[frame_idx].name
        pose_flat = bundle["poses"].get(frame_name)
        if pose_flat is None:
            raise ValueError(f"missing pose row for {clip_dir.name}/{frame_name}")
        gaze_x, gaze_y = bundle["gaze"].get(frame_name, (0, 0))
        notes = [
            "non_metric_jpg",
            "depth_is_duplicated_possible=true",
        ]
        row = {
            "clip": clip_dir.name,
            "slice_order": slice_order,
            "frame_idx": frame_idx,
            "frame_name": frame_name,
            "timestamp_ns": int(frame_idx * 100_000_000),
            "rgb_path": str(rgb_frames[frame_idx]),
            "depth_path": str(streams["depth"].get(frame_idx, "")),
            "stereo_left_path": str(streams["stereo_left"].get(frame_idx, "")),
            "stereo_right_path": str(streams["stereo_right"].get(frame_idx, "")),
            "gaze_x": gaze_x,
            "gaze_y": gaze_y,
            "has_hands": bool(bundle["hands"].get(frame_name, False)),
            "source_archive": source_archive,
            "split": split,
            "notes": ";".join(notes),
        }
        for idx, value in enumerate(pose_flat):
            row[POSE_COLUMNS[idx]] = value
        rows.append(row)
    return pd.DataFrame(rows, columns=MANIFEST_COLUMNS)


def validate_raw_manifest(df: pd.DataFrame, clip_dir: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "clip": clip_dir.name,
        "n_rows": len(df),
        "required_metadata": {},
        "checks": {},
        "warnings": [],
        "errors": [],
    }
    for name in ROOT_METADATA_FILES:
        report["required_metadata"][name] = (clip_dir / name).exists()
    missing_metadata = [name for name, ok in report["required_metadata"].items() if not ok]
    if missing_metadata:
        report["warnings"].append(f"missing metadata files: {', '.join(missing_metadata)}")

    mono = bool(df["timestamp_ns"].is_monotonic_increasing)
    report["checks"]["timestamps_monotonic"] = mono
    if not mono:
        report["errors"].append("timestamps are not monotonically increasing")

    pose_valid = 0
    for _, row in df.iterrows():
        flat = [row[c] for c in POSE_COLUMNS]
        if is_valid_pose_flat(flat):
            pose_valid += 1
    report["checks"]["pose_valid_rows"] = pose_valid
    if pose_valid != len(df):
        report["errors"].append(f"{len(df) - pose_valid} invalid pose rows")

    for path_col in ("rgb_path", "depth_path", "stereo_left_path", "stereo_right_path"):
        missing = 0
        for path_str in df[path_col]:
            if path_str and not Path(path_str).exists():
                missing += 1
        report["checks"][f"{path_col}_missing"] = missing
        if path_col == "rgb_path" and missing:
            report["errors"].append(f"{missing} RGB paths are missing")
        elif missing:
            report["warnings"].append(f"{missing} {path_col} entries are missing")

    return report


def save_manifest(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def save_manifest_report(report: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
