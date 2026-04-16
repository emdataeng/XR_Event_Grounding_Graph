"""Depth blob segmentation backend.

Segments the depth image into distance-based connected components and returns
them as DetectionResult objects. Unlike RGB detectors, boxes are in **depth
image pixel space** (metadata['bbox_space'] = 'depth').

Since blobs can be back-projected to 3D inside this detector when intrinsics
and pose are available via frame_context, the pre-computed 3D centre and extent
are stored in metadata['pre_computed_xyz'] and metadata['pre_computed_extent'].
Script 05 uses these directly and skips the generic depth-sampling step.

Requires: opencv-python (cv2) — already a core dependency.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

import numpy as np

from .base import BaseDetector, DetectionResult


class DepthBlobDetector(BaseDetector):
    """Depth-based blob segmentation — no semantic labels, no ML model.

    Args:
        depth_min:        Minimum valid depth in metres.
        depth_max:        Maximum valid depth in metres.
        min_blob_pixels:  Blobs smaller than this are discarded.
        max_blobs:        Maximum blobs returned per frame.
    """

    def __init__(
        self,
        depth_min: float = 0.1,
        depth_max: float = 5.0,
        min_blob_pixels: int = 200,
        max_blobs: int = 20,
    ):
        self.depth_min = depth_min
        self.depth_max = depth_max
        self.min_blob_pixels = min_blob_pixels
        self.max_blobs = max_blobs

    @property
    def model_id(self) -> str:
        return "depth_blobs"

    @property
    def source(self) -> str:
        return "depth_blobs"

    def detect(
        self,
        rgb: Optional[np.ndarray],
        depth: Optional[np.ndarray] = None,
        frame_context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectionResult]:
        """Segment depth into blobs and return one DetectionResult per blob.

        frame_context may contain: fx, fy, cx, cy, T_world_cam
        If provided, pre-computed 3D centre and extent are stored in metadata.
        """
        if depth is None:
            return []

        from ..depth_utils import extract_depth_blobs, blob_to_world_box
        from ..objects import classify_blob

        blobs = extract_depth_blobs(
            depth,
            depth_min=self.depth_min,
            depth_max=self.depth_max,
            min_blob_pixels=self.min_blob_pixels,
            max_blobs=self.max_blobs,
        )

        detections: List[DetectionResult] = []

        for i, blob in enumerate(blobs):
            sem_class = classify_blob(blob, i)
            conf = min(0.9, 0.3 + blob["area_px"] / 50000)

            meta: Dict[str, Any] = {
                "bbox_space": "depth",
                "blob_depth_mean": blob["depth_mean"],
                "blob_depth_min": blob["depth_min"],
                "blob_depth_max": blob["depth_max"],
                "blob_area_px": blob["area_px"],
            }

            # Pre-compute 3D position if intrinsics + pose are available
            if frame_context:
                fx = frame_context.get("fx")
                fy = frame_context.get("fy")
                cx = frame_context.get("cx")
                cy = frame_context.get("cy")
                T = frame_context.get("T_world_cam")
                if all(v is not None for v in [fx, fy, cx, cy, T]):
                    try:
                        center, extent = blob_to_world_box(blob, fx, fy, cx, cy, T)
                        meta["pre_computed_xyz"] = center.tolist()
                        meta["pre_computed_extent"] = extent.tolist()
                    except Exception:
                        pass

            detections.append(DetectionResult(
                raw_label=sem_class,
                score=float(conf),
                bbox_xyxy=(
                    float(blob["u_min"]), float(blob["v_min"]),
                    float(blob["u_max"]), float(blob["v_max"]),
                ),
                source=self.source,
                model_id=self.model_id,
                prompt=None,
                metadata=meta,
            ))

        return detections
