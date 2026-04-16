"""Object observation schemas and construction helpers.

V2 schema adds detector provenance, bounding box, depth stats, and canonical
class on top of the original V1 columns. Old CSVs load with None for new
columns via load_observations().
"""
from __future__ import annotations
from typing import Optional, List
import uuid
import pandas as pd
import numpy as np


# ── Column definitions ────────────────────────────────────────────────────────

# Original V1 columns — preserved as-is for backward compatibility
_V1_COLUMNS = [
    "observation_id", "frame_idx", "timestamp_ns",
    "raw_object_id", "track_hint",
    "semantic_class", "label", "confidence",
    "x", "y", "z", "w", "h", "d", "yaw",
    "room_id", "caption", "source", "mask_path", "notes",
]

# V2 additions: detector provenance + bbox + depth stats + canonical class
_V2_COLUMNS = [
    # Canonical class after vocabulary mapping (None = unmapped / rejected)
    "canonical_class",
    # Pixel-space bounding box in the RGB image (may be None for depth_blobs)
    "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2",
    # Bounding box area in pixels; used for NMS and area filters
    "bbox_area_px",
    # Detector provenance
    "detector_backend",   # e.g. "grounding_dino", "yolo", "depth_blobs"
    "detector_model",     # e.g. "IDEA-Research/grounding-dino-base"
    "detector_prompt",    # text prompt used (None for fixed-class detectors)
    # Depth statistics sampled from the depth ROI for this detection
    "depth_median",       # median depth of valid pixels in the bbox ROI (metres)
    "depth_min",          # minimum valid depth in ROI
    "depth_max",          # maximum valid depth in ROI
    "depth_valid_px",     # number of valid (non-NaN) depth pixels in ROI
]

OBSERVATION_COLUMNS = _V1_COLUMNS + _V2_COLUMNS

TRACK_COLUMNS = [
    "track_id", "observation_id", "frame_idx", "timestamp_ns",
    "semantic_class", "x", "y", "z", "w", "h", "d", "yaw",
    "is_first_in_track", "is_last_in_track", "linkage_score",
]


# ── Constructors ──────────────────────────────────────────────────────────────

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
    # V2 fields — all optional so existing call sites continue to work
    canonical_class: Optional[str] = None,
    bbox_x1: Optional[float] = None,
    bbox_y1: Optional[float] = None,
    bbox_x2: Optional[float] = None,
    bbox_y2: Optional[float] = None,
    bbox_area_px: Optional[float] = None,
    detector_backend: Optional[str] = None,
    detector_model: Optional[str] = None,
    detector_prompt: Optional[str] = None,
    depth_median: Optional[float] = None,
    depth_min: Optional[float] = None,
    depth_max: Optional[float] = None,
    depth_valid_px: Optional[int] = None,
) -> dict:
    return {
        # V1 fields
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
        # V2 fields
        "canonical_class": canonical_class,
        "bbox_x1": bbox_x1,
        "bbox_y1": bbox_y1,
        "bbox_x2": bbox_x2,
        "bbox_y2": bbox_y2,
        "bbox_area_px": bbox_area_px,
        "detector_backend": detector_backend or source,
        "detector_model": detector_model,
        "detector_prompt": detector_prompt,
        "depth_median": depth_median,
        "depth_min": depth_min,
        "depth_max": depth_max,
        "depth_valid_px": depth_valid_px,
    }


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_observations(path) -> pd.DataFrame:
    """Load object_observations.csv, backfilling any missing V2 columns with None."""
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


# ── Depth stats helper ────────────────────────────────────────────────────────

def compute_depth_stats(
    depth: np.ndarray,
    x1: float, y1: float, x2: float, y2: float,
    depth_min_m: float = 0.1,
    depth_max_m: float = 5.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
) -> dict:
    """Sample depth stats from a bbox ROI (given in RGB pixel space).

    scale_x / scale_y convert RGB bbox coords to depth image coords.
    Returns a dict with keys: depth_median, depth_min, depth_max, depth_valid_px,
    plus the sampled depth value best suited for backprojection (depth_for_proj).
    """
    dh, dw = depth.shape
    dx1 = int(np.clip(x1 * scale_x, 0, dw))
    dy1 = int(np.clip(y1 * scale_y, 0, dh))
    dx2 = int(np.clip(x2 * scale_x, 0, dw))
    dy2 = int(np.clip(y2 * scale_y, 0, dh))

    roi = depth[dy1:dy2, dx1:dx2]
    valid = roi[(roi > depth_min_m) & (roi < depth_max_m)]

    if valid.size == 0:
        return {
            "depth_median": None, "depth_min": None,
            "depth_max": None, "depth_valid_px": 0,
            "depth_for_proj": None,
        }

    return {
        "depth_median": float(np.median(valid)),
        "depth_min": float(valid.min()),
        "depth_max": float(valid.max()),
        "depth_valid_px": int(valid.size),
        "depth_for_proj": float(np.median(valid)),
    }


# ── Blob helpers (depth_blobs backend) ───────────────────────────────────────

def classify_blob(blob: dict, blob_idx: int) -> str:
    """Assign a rough semantic class to a depth blob based on its properties."""
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
