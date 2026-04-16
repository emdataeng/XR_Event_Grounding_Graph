"""Base interface for all detector backends.

Contract
--------
* detect(rgb, depth, frame_context) → List[DetectionResult]
* All bounding boxes are in **RGB image pixel space** (x1, y1, x2, y2).
* Depth back-projection to 3D world coordinates is NOT the detector's job.
* Detectors must not crash the pipeline on soft failures — raise only for
  fatal configuration errors (missing model file, wrong model_id format).
* frame_context is an optional dict for per-frame data that only some
  backends need (e.g. DepthBlobDetector needs intrinsics + pose).
  RGB detectors ignore it entirely.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class DetectionResult:
    """A single detection from any backend.

    Attributes:
        raw_label:    Label string exactly as returned by the detector.
        score:        Confidence in [0, 1].
        bbox_xyxy:    (x1, y1, x2, y2) in RGB image pixel space.
                      For depth_blobs the bbox is in depth image pixel space;
                      metadata['bbox_space'] = 'depth' in that case.
        source:       Backend name, e.g. "grounding_dino".
        model_id:     Model identifier, e.g. "IDEA-Research/grounding-dino-base".
        prompt:       Text prompt used (None for fixed-class detectors).
        metadata:     Backend-specific extras. Keys used by built-in backends:
                        'bbox_space'         "rgb" (default) | "depth"
                        'pre_computed_xyz'   [x,y,z] world centre (depth_blobs)
                        'pre_computed_extent'[w,h,d] world extent  (depth_blobs)
    """
    raw_label: str
    score: float
    bbox_xyxy: Tuple[float, float, float, float]
    source: str
    model_id: str
    prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def bbox_area_px(self) -> float:
        x1, y1, x2, y2 = self.bbox_xyxy
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


class BaseDetector(ABC):
    """Abstract base class for all detection backends.

    Subclasses must implement:
        detect(rgb, depth, frame_context) → List[DetectionResult]
        model_id  (property)
        source    (property)
    """

    @abstractmethod
    def detect(
        self,
        rgb: np.ndarray,
        depth: Optional[np.ndarray] = None,
        frame_context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectionResult]:
        """Run detection on a single RGB (and optionally depth) frame.

        Args:
            rgb:           HxWx3 uint8 array in RGB order.
            depth:         HxW float32 depth in metres, or None.
            frame_context: Optional per-frame data. Standard keys:
                             fx, fy, cx, cy  — camera intrinsics
                             T_world_cam     — 4x4 numpy pose matrix
                             rgb_h, rgb_w    — RGB image dimensions
                             depth_min_m     — valid depth minimum
                             depth_max_m     — valid depth maximum
        Returns:
            List of DetectionResult (may be empty, never raises on soft failure).
        """

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Human-readable model identifier for provenance logging."""

    @property
    @abstractmethod
    def source(self) -> str:
        """Backend name, e.g. 'grounding_dino'. Stored in DetectionResult.source."""


def load_detector(
    obs_source: str,
    cfg: Dict,
    thr: Dict,
    prompt: Optional[str] = None,
) -> BaseDetector:
    """Factory: instantiate the correct detector from pipeline config.

    Args:
        obs_source: value of pipeline.yaml observations_source
        cfg:        full pipeline config dict
        thr:        full thresholds config dict
        prompt:     Override the detection prompt.  When None, falls back to
                    cfg["detection_prompt"].  Callers should resolve this from
                    Vocabulary.build_prompt() when object_vocabulary is configured.
    """
    if obs_source == "grounding_dino":
        from .grounding_dino import GroundingDINODetector
        dino_cfg = thr.get("grounding_dino", {})
        resolved_prompt = prompt or cfg.get("detection_prompt", "object.")
        return GroundingDINODetector(
            model_id=cfg.get("grounding_dino_model", "IDEA-Research/grounding-dino-base"),
            prompt=resolved_prompt,
            box_threshold=float(dino_cfg.get("box_threshold", 0.30)),
            text_threshold=float(dino_cfg.get("text_threshold", 0.25)),
        )

    elif obs_source == "yolo":
        from .yolo import YOLODetector
        yolo_model = cfg.get("yolo_model")
        if not yolo_model:
            raise ValueError("observations_source=yolo but yolo_model not set in pipeline.yaml")
        return YOLODetector(model_path=yolo_model)

    elif obs_source == "depth_blobs":
        from .depth_blobs import DepthBlobDetector
        det_cfg = thr.get("detection", {})
        return DepthBlobDetector(
            depth_min=float(det_cfg.get("depth_min_m", 0.1)),
            depth_max=float(det_cfg.get("depth_max_m", 5.0)),
            min_blob_pixels=int(det_cfg.get("min_blob_pixels", 200)),
            max_blobs=int(det_cfg.get("max_blobs_per_frame", 20)),
        )

    else:
        raise ValueError(f"Unknown observations_source: {obs_source!r}")
