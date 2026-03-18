"""Object observation schemas and construction helpers."""
from __future__ import annotations
from typing import Optional, List
import uuid
import pandas as pd
import numpy as np


OBSERVATION_COLUMNS = [
    "observation_id", "frame_idx", "timestamp_ns",
    "raw_object_id", "track_hint",
    "semantic_class", "label", "confidence",
    "x", "y", "z", "w", "h", "d", "yaw",
    "room_id", "caption", "source", "mask_path", "notes",
]

TRACK_COLUMNS = [
    "track_id", "observation_id", "frame_idx", "timestamp_ns",
    "semantic_class", "x", "y", "z", "w", "h", "d", "yaw",
    "is_first_in_track", "is_last_in_track", "linkage_score",
]


def make_observation(
    frame_idx: int,
    timestamp_ns: int,
    semantic_class: str,
    x: float, y: float, z: float,
    w: float = 0.0, h: float = 0.0, d: float = 0.0,
    yaw: float = 0.0,
    confidence: float = 0.5,
    label: Optional[str] = None,
    raw_object_id: Optional[str] = None,
    room_id: str = "workstation_A",
    caption: Optional[str] = None,
    source: str = "depth_blobs",
    observation_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    return {
        "observation_id": observation_id or f"obs_{uuid.uuid4().hex[:8]}",
        "frame_idx": frame_idx,
        "timestamp_ns": timestamp_ns,
        "raw_object_id": raw_object_id,
        "track_hint": None,
        "semantic_class": semantic_class,
        "label": label or semantic_class,
        "confidence": confidence,
        "x": x, "y": y, "z": z,
        "w": w, "h": h, "d": d,
        "yaw": yaw,
        "room_id": room_id,
        "caption": caption,
        "source": source,
        "mask_path": None,
        "notes": notes,
    }


def classify_blob(blob: dict, blob_idx: int) -> str:
    """Assign a rough semantic class to a depth blob based on its properties.

    Uses heuristics: small + close = small_object, large = surface/wall, etc.
    This is a baseline; replace with YOLO detections when available.
    """
    area = blob["area_px"]
    depth = blob["depth_mean"]
    ext_h = blob.get("depth_max", depth) - blob.get("depth_min", depth)

    if depth < 0.6 and area < 5000:
        return "small_object"
    if depth < 1.5 and area < 15000:
        return "object"
    if area > 30000 or ext_h < 0.05:
        return "surface"
    return "object"


def load_observations(path) -> pd.DataFrame:
    import pandas as pd
    df = pd.read_csv(path)
    for col in OBSERVATION_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[OBSERVATION_COLUMNS]


def load_tracks(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in TRACK_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[TRACK_COLUMNS]
