"""Depth decoding, filtering, and blob detection for object extraction."""
from __future__ import annotations
from typing import List, Optional, Tuple, Dict
import numpy as np


def clean_depth(
    depth: np.ndarray,
    depth_min: float = 0.1,
    depth_max: float = 5.0,
) -> np.ndarray:
    """Return depth with out-of-range values set to NaN."""
    d = depth.copy()
    d[(d < depth_min) | (d > depth_max)] = np.nan
    return d


def depth_to_colormap(depth: np.ndarray, depth_max: float = 3.0) -> np.ndarray:
    """Convert depth array (H,W) to uint8 RGB image for visualization."""
    import cv2  # type: ignore
    d_clipped = np.clip(depth, 0, depth_max)
    d_norm = (d_clipped / depth_max * 255).astype(np.uint8)
    # Replace NaN / 0 with 0
    d_norm = np.nan_to_num(d_norm, nan=0).astype(np.uint8)
    colored = cv2.applyColorMap(d_norm, cv2.COLORMAP_TURBO)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)


def extract_depth_blobs(
    depth: np.ndarray,
    depth_min: float = 0.1,
    depth_max: float = 5.0,
    min_blob_pixels: int = 200,
    max_blobs: int = 20,
    num_depth_bins: int = 8,
) -> List[Dict]:
    """Segment depth image into distance-based blobs.

    Bins the depth image into depth layers and finds connected components
    in each layer. Returns list of blob dicts with 2D and depth statistics.

    Each blob dict has:
        cx_px, cy_px : pixel centroid
        u_min, u_max, v_min, v_max : pixel bounding box
        depth_mean, depth_min, depth_max : depth stats in meters
        area_px : number of pixels
        layer_idx : which depth bin
    """
    import cv2  # type: ignore

    d_clean = clean_depth(depth, depth_min, depth_max)
    valid = ~np.isnan(d_clean)
    if valid.sum() == 0:
        return []

    d_vals = d_clean[valid]
    d_lo = float(d_vals.min())
    d_hi = float(d_vals.max())
    if d_hi - d_lo < 0.01:
        # Flat depth — single bin
        bin_edges = [d_lo, d_hi + 0.01]
    else:
        bin_edges = list(np.linspace(d_lo, d_hi, num_depth_bins + 1))

    blobs = []
    for i in range(len(bin_edges) - 1):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = valid & (d_clean >= lo) & (d_clean < hi)
        mask_u8 = mask.astype(np.uint8) * 255
        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)
        for label_id in range(1, n_labels):  # skip background (0)
            area = int(stats[label_id, cv2.CC_STAT_AREA])
            if area < min_blob_pixels:
                continue
            cx = float(centroids[label_id][0])
            cy = float(centroids[label_id][1])
            x = int(stats[label_id, cv2.CC_STAT_LEFT])
            y = int(stats[label_id, cv2.CC_STAT_TOP])
            w = int(stats[label_id, cv2.CC_STAT_WIDTH])
            h = int(stats[label_id, cv2.CC_STAT_HEIGHT])
            blob_pixels = d_clean[labels == label_id]
            blob_pixels = blob_pixels[~np.isnan(blob_pixels)]
            if blob_pixels.size == 0:
                continue
            blobs.append({
                "cx_px": cx, "cy_px": cy,
                "u_min": x, "u_max": x + w,
                "v_min": y, "v_max": y + h,
                "depth_mean": float(blob_pixels.mean()),
                "depth_min": float(blob_pixels.min()),
                "depth_max": float(blob_pixels.max()),
                "area_px": area,
                "layer_idx": i,
            })

    # Sort by area descending, keep top N
    blobs.sort(key=lambda b: b["area_px"], reverse=True)
    return blobs[:max_blobs]


def blob_to_world_box(
    blob: Dict,
    fx: float, fy: float, cx: float, cy: float,
    T_world_cam: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Project a blob's 2D bounding box at mean depth to world-frame center/extent.

    Returns (center_xyz, extent_whd) both as 1D float arrays.
    """
    from .geometry import deproject_pixel_to_world
    d_mean = blob["depth_mean"]
    u_c, v_c = blob["cx_px"], blob["cy_px"]
    center = deproject_pixel_to_world(u_c, v_c, d_mean, fx, fy, cx, cy, T_world_cam)

    # Estimate extent from pixel bbox at mean depth
    u_min, u_max = blob["u_min"], blob["u_max"]
    v_min, v_max = blob["v_min"], blob["v_max"]
    p0 = deproject_pixel_to_world(u_min, v_min, d_mean, fx, fy, cx, cy, T_world_cam)
    p1 = deproject_pixel_to_world(u_max, v_max, d_mean, fx, fy, cx, cy, T_world_cam)
    extent = np.abs(p1 - p0)
    # Add depth range as the z extent
    extent[2] = blob["depth_max"] - blob["depth_min"] + 0.01
    return center, extent
