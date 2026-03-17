"""IO utilities for Quest 3 capture files."""
from __future__ import annotations
import json
import struct
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np


# Windows FILETIME epoch offset to Unix epoch in 100ns ticks
# Windows FILETIME: 100ns ticks since 1601-01-01
# Unix epoch: seconds since 1970-01-01
# Difference: 11644473600 seconds = 116444736000000000 ticks
_WIN_TICK_TO_UNIX_NS_OFFSET = 116444736000000000 * 100  # in nanoseconds

# Actually: 1 tick = 100ns, so to get ns: ticks * 100
# To convert to Unix ns: (ticks - 116444736000000000) * 100


def ticks_to_ns(ticks: int, relative_to: Optional[int] = None) -> int:
    """Convert Windows FILETIME ticks to nanoseconds.

    If relative_to is given, returns ns relative to that tick value.
    Otherwise returns absolute Unix nanoseconds.
    """
    if relative_to is not None:
        return (ticks - relative_to) * 100
    return (ticks - 116444736000000000) * 100


def load_meta(meta_path: Path) -> Dict:
    """Load a frame metadata JSON file."""
    with open(meta_path, "r") as f:
        return json.load(f)


def load_rgba(rgba_path: Path, width: int = 0, height: int = 0) -> np.ndarray:
    """Load raw RGBA32 file and return uint8 array (H, W, 4).

    Auto-detects actual dimensions from file size if width/height not given or
    don't match the actual data. Quest 3 stores data at 2x the reported resolution.
    """
    raw = np.frombuffer(rgba_path.read_bytes(), dtype=np.uint8)
    n_pixels = len(raw) // 4  # 4 bytes per RGBA pixel
    # Use provided dims if they match
    if width > 0 and height > 0 and width * height == n_pixels:
        return raw.reshape(height, width, 4)
    # Auto-detect: assume 4:3 aspect ratio
    # n_pixels = w * h, w/h = 4/3 → w = 4k, h = 3k → 12k^2 = n_pixels
    import math
    k = math.sqrt(n_pixels / 12)
    h_det = round(3 * k)
    w_det = round(4 * k)
    if w_det * h_det == n_pixels:
        return raw.reshape(h_det, w_det, 4)
    # Fallback: try provided or default dims
    if width > 0 and height > 0:
        return raw.reshape(height, width, 4)
    return raw.reshape(240, 320, 4)


def rgba_to_rgb(rgba: np.ndarray) -> np.ndarray:
    """Extract RGB from RGBA array."""
    return rgba[:, :, :3]


def load_depth_npy(depth_path: Path, width: int = 0, height: int = 0) -> Optional[np.ndarray]:
    """Load .npy depth file and return float32 array (H, W) in meters.

    Auto-detects dimensions. Quest 3 depth is typically 640x320.
    """
    if not depth_path.exists():
        return None
    arr = np.load(str(depth_path)).astype(np.float32)
    if arr.ndim == 2:
        return arr
    if arr.ndim == 1:
        n = arr.shape[0]
        # Use provided dims if they match
        if width > 0 and height > 0 and width * height == n:
            return arr.reshape(height, width)
        # Auto-detect: try common depth resolutions
        for (h, w) in [(320, 640), (480, 640), (240, 320), (400, 512), (360, 640)]:
            if h * w == n:
                return arr.reshape(h, w)
        # Fallback: square-ish reshape
        import math
        s = int(math.sqrt(n))
        if s * s == n:
            return arr.reshape(s, s)
        if width > 0 and height > 0:
            return arr.reshape(height, width)
        return arr.reshape(320, 640)  # Quest 3 default
    return arr


def load_depth_f32(depth_path: Path, width: int = 320, height: int = 240) -> Optional[np.ndarray]:
    """Load raw .f32 depth file and return float32 array (H, W) in meters."""
    if not depth_path.exists():
        return None
    raw = np.frombuffer(depth_path.read_bytes(), dtype="<f4")  # little-endian float32
    if raw.size == 0:
        return None
    return raw.reshape(height, width)


def load_depth(frame_dir: Path, stem: str, width: int = 320, height: int = 240) -> Optional[np.ndarray]:
    """Try to load depth from .npy first, then .f32."""
    npy = frame_dir / f"{stem}_depth.npy"
    f32 = frame_dir / f"{stem}_depth.f32"
    d = load_depth_npy(npy, width, height)
    if d is not None:
        return d
    return load_depth_f32(f32, width, height)


def scan_quest_capture(capture_dir: Path) -> list[Dict]:
    """Scan a Quest 3 capture directory and return sorted list of frame dicts.

    Returns list of dicts with keys:
        frame_idx, ticks, stem, rgba_path, depth_npy_path, depth_f32_path, meta_path, meta
    """
    frames = []
    for meta_path in sorted(capture_dir.glob("*_meta.json")):
        meta = load_meta(meta_path)
        ticks = meta["ticks"]
        frame_idx = meta["frame_index"]
        # Derive stem: everything before _meta.json
        stem = meta_path.stem.replace("_meta", "")
        # Dynamically find the rgba file — suffix varies by capture (e.g. _320x240.rgba or _640x480.rgba)
        rgba_matches = list(capture_dir.glob(f"{stem}_*.rgba"))
        rgba_path = rgba_matches[0] if rgba_matches else capture_dir / f"{stem}_320x240.rgba"
        depth_npy = capture_dir / f"{stem}_depth.npy"
        depth_f32 = capture_dir / f"{stem}_depth.f32"
        frames.append({
            "frame_idx": frame_idx,
            "ticks": ticks,
            "stem": stem,
            "rgba_path": rgba_path,
            "depth_npy_path": depth_npy if depth_npy.exists() else None,
            "depth_f32_path": depth_f32 if depth_f32.exists() else None,
            "meta_path": meta_path,
            "meta": meta,
        })
    frames.sort(key=lambda x: x["ticks"])
    return frames
