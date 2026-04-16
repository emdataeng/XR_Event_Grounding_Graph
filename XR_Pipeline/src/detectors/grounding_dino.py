"""Grounding DINO detection backend.

Wraps IDEA-Research/grounding-dino-base (or any compatible HF model) via the
transformers AutoModelForZeroShotObjectDetection API. Returns pixel-space boxes
in RGB image coordinates.

Requires: transformers, torch
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

import numpy as np

from .base import BaseDetector, DetectionResult


class GroundingDINODetector(BaseDetector):
    """Open-vocabulary detector using Grounding DINO.

    Args:
        model_id:       HuggingFace model ID.
        prompt:         Dot-separated detection prompt, e.g. "red lego. blue lego."
        box_threshold:  Minimum objectness score to keep a box.
        text_threshold: Minimum text-alignment score to assign a label.
    """

    def __init__(
        self,
        model_id: str = "IDEA-Research/grounding-dino-base",
        prompt: str = "object.",
        box_threshold: float = 0.30,
        text_threshold: float = 0.25,
    ):
        self._model_id = model_id
        self.prompt = prompt
        self.box_threshold = box_threshold
        self.text_threshold = text_threshold
        self._model = None
        self._processor = None
        self._device = None

    def _load(self):
        if self._model is not None:
            return
        try:
            from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
            import torch
        except ImportError as e:
            raise ImportError(
                "transformers and torch are required for grounding_dino backend. "
                "Run: pip install transformers torch"
            ) from e

        import torch
        self._processor = AutoProcessor.from_pretrained(self._model_id)
        self._model = AutoModelForZeroShotObjectDetection.from_pretrained(self._model_id)
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = self._model.to(self._device)
        self._model.eval()

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def source(self) -> str:
        return "grounding_dino"

    def detect(
        self,
        rgb: np.ndarray,
        depth: Optional[np.ndarray] = None,
        frame_context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectionResult]:
        """Detect objects in an RGB frame, returning pixel-space boxes."""
        import torch
        from PIL import Image

        self._load()

        pil_image = Image.fromarray(rgb)
        rgb_h, rgb_w = rgb.shape[:2]

        inputs = self._processor(
            images=pil_image,
            text=self.prompt,
            return_tensors="pt",
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)

        results = self._processor.post_process_grounded_object_detection(
            outputs,
            input_ids=inputs["input_ids"],
            threshold=self.box_threshold,
            text_threshold=self.text_threshold,
            target_sizes=[(rgb_h, rgb_w)],
        )

        if not results:
            return []

        result = results[0]
        boxes = result["boxes"].tolist()
        labels = result.get("text_labels", result.get("labels", []))
        scores = result["scores"].tolist()

        detections: List[DetectionResult] = []
        for box, label, score in zip(boxes, labels, scores):
            x1, y1, x2, y2 = box
            detections.append(DetectionResult(
                raw_label=label.strip().rstrip(".").strip(),
                score=float(score),
                bbox_xyxy=(float(x1), float(y1), float(x2), float(y2)),
                source=self.source,
                model_id=self._model_id,
                prompt=self.prompt,
                metadata={"bbox_space": "rgb"},
            ))

        return detections
