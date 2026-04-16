"""YOLO detection backend.

Wraps ultralytics YOLOv8/v11 models. Returns pixel-space boxes in RGB image
coordinates using the model's native class vocabulary.

Requires: ultralytics
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

import numpy as np

from .base import BaseDetector, DetectionResult


class YOLODetector(BaseDetector):
    """Fixed-class detector using an Ultralytics YOLO model.

    Args:
        model_path: Path to a .pt model file, or an Ultralytics model name
                    such as "yolov8n.pt".
    """

    def __init__(self, model_path: str):
        self._model_path = model_path
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        try:
            from ultralytics import YOLO
        except ImportError as e:
            raise ImportError(
                "ultralytics is required for yolo backend. "
                "Run: pip install ultralytics"
            ) from e
        self._model = YOLO(self._model_path)

    @property
    def model_id(self) -> str:
        return self._model_path

    @property
    def source(self) -> str:
        return "yolo"

    def detect(
        self,
        rgb: np.ndarray,
        depth: Optional[np.ndarray] = None,
        frame_context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectionResult]:
        """Detect objects using YOLO, returning pixel-space boxes."""
        self._load()

        results = self._model(rgb, verbose=False)
        detections: List[DetectionResult] = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                sem_class = self._model.names.get(cls_id, f"class_{cls_id}")

                detections.append(DetectionResult(
                    raw_label=sem_class,
                    score=conf,
                    bbox_xyxy=(float(x1), float(y1), float(x2), float(y2)),
                    source=self.source,
                    model_id=self._model_path,
                    prompt=None,
                    metadata={"bbox_space": "rgb"},
                ))

        return detections
