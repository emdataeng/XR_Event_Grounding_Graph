"""detection_postprocess.py — Post-processing pipeline for raw detections.

Applied after the detector backend, before depth backprojection:
  1. Vocabulary canonicalization — maps raw labels to canonical class names.
     Detections with no mapping (when vocabulary is non-empty) are dropped.
  2. Confidence filtering — drop detections below min confidence.
  3. Area filtering — drop detections with bbox area below min_area_px.
  4. Class-aware 2D NMS — within each class, suppress lower-score boxes
     whose IoU with a higher-score box exceeds the threshold.

The canonical_class is stored in det.metadata['canonical_class'] so that
script 05 can populate the V2 column without re-running vocabulary lookup.
"""
from __future__ import annotations
from typing import List, Optional

import numpy as np

from .detectors.base import DetectionResult
from .vocabulary import Vocabulary


def postprocess_detections(
    detections: List[DetectionResult],
    vocab: Vocabulary,
    conf_min: float = 0.0,
    min_area_px: float = 0.0,
    nms_iou_threshold: float = 0.5,
    apply_vocab: bool = True,
) -> List[DetectionResult]:
    """Apply vocabulary mapping, filtering, and NMS to a list of DetectionResults.

    Args:
        detections:        Raw results from a detector backend.
        vocab:             Vocabulary instance (may be empty / permissive).
        conf_min:          Drop detections with score < conf_min.
        min_area_px:       Drop detections with bbox area < min_area_px pixels.
        nms_iou_threshold: IoU threshold for class-aware NMS (0 = disabled).
        apply_vocab:       Whether to apply vocabulary canonicalization and
                           rejection.  Set False for fixed-class backends
                           (yolo, depth_blobs) so their native labels are never
                           dropped by a scene-specific vocabulary.

    Returns:
        Filtered and de-duplicated detections. canonical_class is stored in
        each result's metadata dict under key 'canonical_class'.
    """
    out: List[DetectionResult] = []

    for det in detections:
        # 1. Vocabulary mapping
        if apply_vocab:
            canonical = vocab.canonicalize(det.raw_label)
            if canonical is None:
                # Vocabulary is configured and this label has no mapping → reject
                continue
        else:
            # Fixed-class backend: raw label passes through as its own canonical
            canonical = det.raw_label
        det.metadata["canonical_class"] = canonical

        # 2. Confidence filter
        if det.score < conf_min:
            continue

        # 3. Area filter
        if min_area_px > 0 and det.bbox_area_px < min_area_px:
            continue

        out.append(det)

    # 4. Class-aware NMS
    if nms_iou_threshold > 0 and len(out) > 1:
        out = _class_aware_nms(out, iou_threshold=nms_iou_threshold)

    return out


# ── IoU helpers ───────────────────────────────────────────────────────────────

def _iou(box_a: tuple, box_b: tuple) -> float:
    """Intersection-over-Union for two (x1,y1,x2,y2) boxes."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter == 0.0:
        return 0.0

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _class_aware_nms(
    detections: List[DetectionResult],
    iou_threshold: float,
) -> List[DetectionResult]:
    """Greedy NMS per canonical class label.

    Within each class, sort by score descending. Suppress any box whose IoU
    with a higher-score box exceeds iou_threshold.
    """
    # Group by canonical class
    by_class: dict[str, List[DetectionResult]] = {}
    for det in detections:
        cls = det.metadata.get("canonical_class") or det.raw_label
        by_class.setdefault(cls, []).append(det)

    kept: List[DetectionResult] = []
    for cls, dets in by_class.items():
        sorted_dets = sorted(dets, key=lambda d: d.score, reverse=True)
        suppressed = [False] * len(sorted_dets)

        for i in range(len(sorted_dets)):
            if suppressed[i]:
                continue
            kept.append(sorted_dets[i])
            for j in range(i + 1, len(sorted_dets)):
                if suppressed[j]:
                    continue
                if _iou(sorted_dets[i].bbox_xyxy, sorted_dets[j].bbox_xyxy) > iou_threshold:
                    suppressed[j] = True

    # Re-sort to match original score-descending order across all classes
    kept.sort(key=lambda d: d.score, reverse=True)
    return kept
