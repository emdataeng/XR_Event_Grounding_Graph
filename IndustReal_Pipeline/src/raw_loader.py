"""Readers for raw IndustReal clip folders and label files."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .hl2_pose import load_pose_csv


STREAM_NAMES = ("rgb", "depth", "stereo_left", "stereo_right")
ROOT_METADATA_FILES = (
    "pose.csv",
    "gaze.csv",
    "hands.csv",
    "OD_labels.json",
    "PSR_labels.csv",
    "PSR_labels_with_errors.csv",
    "PSR_labels_raw.csv",
    "AR_labels.csv",
)


def frame_name_to_idx(frame_name: str) -> int:
    return int(Path(frame_name).stem)


def idx_to_frame_name(frame_idx: int) -> str:
    return f"{int(frame_idx):06d}.jpg"


def discover_stream_frames(clip_dir: Path, stream: str) -> dict[int, Path]:
    stream_dir = clip_dir / stream
    if not stream_dir.exists():
        return {}
    return {frame_name_to_idx(p.name): p for p in sorted(stream_dir.glob("*.jpg"))}


def discover_clip_streams(clip_dir: Path) -> dict[str, dict[int, Path]]:
    return {stream: discover_stream_frames(clip_dir, stream) for stream in STREAM_NAMES}


def clip_frame_counts(clip_dir: Path) -> dict[str, int]:
    return {stream: len(frames) for stream, frames in discover_clip_streams(clip_dir).items()}


def load_gaze_csv(path: Path) -> dict[str, tuple[int, int]]:
    if not path.exists():
        return {}
    gaze: dict[str, tuple[int, int]] = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            gaze[row[0]] = (int(float(row[1])), int(float(row[2])))
    return gaze


def load_hands_csv(path: Path) -> dict[str, bool]:
    if not path.exists():
        return {}
    flags: dict[str, bool] = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            has_hands = any(float(value) != 0.0 for value in row[1:] if value)
            flags[row[0]] = has_hands
    return flags


def load_step_labels_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            rows.append(
                {
                    "frame_name": row[0],
                    "frame_idx": frame_name_to_idx(row[0]),
                    "id": int(row[1]),
                    "description": row[2],
                }
            )
    return rows


def load_od_labels(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    categories = {item["id"]: item["name"] for item in data.get("categories", [])}
    images = {item["id"]: item["file_name"] for item in data.get("images", [])}
    result: dict[str, dict[str, Any]] = {}
    for ann in data.get("annotations", []):
        frame_name = images.get(ann["image_id"])
        if frame_name is None:
            continue
        frame_state = categories.get(ann["category_id"], "unknown")
        bbox = ann.get("bbox", [0.0, 0.0, 0.0, 0.0])
        result[frame_name] = {
            "state_name": frame_state,
            "bbox_xywh": [float(v) for v in bbox],
            "bbox_xyxy": [
                float(bbox[0]),
                float(bbox[1]),
                float(bbox[0] + bbox[2]),
                float(bbox[1] + bbox[3]),
            ],
            "category_id": int(ann["category_id"]),
            "annotation_id": int(ann["id"]),
        }
    return result


def load_clip_bundle(clip_dir: Path) -> dict[str, Any]:
    return {
        "clip": clip_dir.name,
        "clip_dir": clip_dir,
        "streams": discover_clip_streams(clip_dir),
        "frame_counts": clip_frame_counts(clip_dir),
        "poses": load_pose_csv(clip_dir / "pose.csv"),
        "gaze": load_gaze_csv(clip_dir / "gaze.csv"),
        "hands": load_hands_csv(clip_dir / "hands.csv"),
        "od_labels": load_od_labels(clip_dir / "OD_labels.json"),
    }
