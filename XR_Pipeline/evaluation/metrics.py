"""evaluation/metrics.py — Detection precision/recall/F1 and IoU metrics.

Used by the bakeoff script to compare detector configurations. Ground-truth
annotations are JSON files in evaluation/annotations/.

Annotation format (one JSON file per session):
{
  "session_id": "session_003",
  "frames": [
    {
      "frame_idx": 14,
      "objects": [
        {"class": "red_lego", "bbox": [x1, y1, x2, y2]},
        {"class": "blue_lego", "bbox": [x1, y1, x2, y2]}
      ]
    }
  ]
}
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class AnnotatedBox:
    frame_idx: int
    cls: str
    bbox: Tuple[float, float, float, float]  # (x1,y1,x2,y2)


@dataclass
class DetectedBox:
    frame_idx: int
    cls: str          # canonical_class (or semantic_class as fallback)
    bbox: Tuple[float, float, float, float]
    score: float


@dataclass
class PerClassMetrics:
    cls: str
    tp: int = 0
    fp: int = 0
    fn: int = 0
    iou_sum: float = 0.0
    matched_count: int = 0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom > 0 else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    @property
    def mean_iou(self) -> float:
        return self.iou_sum / self.matched_count if self.matched_count > 0 else 0.0


# ── Annotation loading ────────────────────────────────────────────────────────

def load_annotations(annotation_path: Path) -> List[AnnotatedBox]:
    """Load ground-truth boxes from an annotation JSON file."""
    data = json.loads(annotation_path.read_text())
    boxes: List[AnnotatedBox] = []
    for frame_data in data.get("frames", []):
        fidx = int(frame_data["frame_idx"])
        for obj in frame_data.get("objects", []):
            boxes.append(AnnotatedBox(
                frame_idx=fidx,
                cls=obj["class"],
                bbox=tuple(obj["bbox"]),
            ))
    return boxes


def load_detections_from_csv(observations_csv: Path) -> List[DetectedBox]:
    """Load detections from an object_observations.csv file.

    Uses canonical_class if available, falls back to semantic_class.
    Only includes rows that have bbox_x1 populated (V2 schema).
    """
    df = pd.read_csv(observations_csv)
    boxes: List[DetectedBox] = []
    for _, row in df.iterrows():
        # Skip rows without bbox data
        if pd.isna(row.get("bbox_x1")):
            continue
        cls = row.get("canonical_class") or row.get("semantic_class", "unknown")
        if pd.isna(cls):
            continue
        boxes.append(DetectedBox(
            frame_idx=int(row["frame_idx"]),
            cls=str(cls),
            bbox=(float(row["bbox_x1"]), float(row["bbox_y1"]),
                  float(row["bbox_x2"]), float(row["bbox_y2"])),
            score=float(row.get("confidence", 0.0)),
        ))
    return boxes


# ── IoU ───────────────────────────────────────────────────────────────────────

def box_iou(a: tuple, b: tuple) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter == 0.0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


# ── Matching ──────────────────────────────────────────────────────────────────

def match_detections_to_annotations(
    detections: List[DetectedBox],
    annotations: List[AnnotatedBox],
    iou_threshold: float = 0.5,
) -> Dict[str, PerClassMetrics]:
    """Greedy matching of detections to ground-truth boxes.

    Matches are made per (frame, class) group. Within each group, detections
    are sorted by score descending and greedily matched to the highest-IoU
    annotation box.

    Returns a dict of canonical_class → PerClassMetrics.
    """
    # Group annotations by (frame, class)
    ann_by_fc: Dict[Tuple[int, str], List[AnnotatedBox]] = {}
    for ann in annotations:
        key = (ann.frame_idx, ann.cls)
        ann_by_fc.setdefault(key, []).append(ann)

    # Group detections by (frame, class)
    det_by_fc: Dict[Tuple[int, str], List[DetectedBox]] = {}
    for det in detections:
        key = (det.frame_idx, det.cls)
        det_by_fc.setdefault(key, []).append(det)

    # Collect all classes seen in either set
    all_classes = set()
    for ann in annotations:
        all_classes.add(ann.cls)
    for det in detections:
        all_classes.add(det.cls)

    metrics: Dict[str, PerClassMetrics] = {cls: PerClassMetrics(cls=cls) for cls in all_classes}

    all_frames = set(a.frame_idx for a in annotations) | set(d.frame_idx for d in detections)

    for fidx in all_frames:
        for cls in all_classes:
            key = (fidx, cls)
            anns = ann_by_fc.get(key, [])
            dets = sorted(det_by_fc.get(key, []), key=lambda d: d.score, reverse=True)

            matched_ann_indices = set()
            m = metrics[cls]

            for det in dets:
                best_iou = 0.0
                best_ann_idx = -1
                for ai, ann in enumerate(anns):
                    if ai in matched_ann_indices:
                        continue
                    iou = box_iou(det.bbox, ann.bbox)
                    if iou > best_iou:
                        best_iou = iou
                        best_ann_idx = ai

                if best_ann_idx >= 0 and best_iou >= iou_threshold:
                    m.tp += 1
                    m.iou_sum += best_iou
                    m.matched_count += 1
                    matched_ann_indices.add(best_ann_idx)
                else:
                    m.fp += 1

            # Unmatched annotations → false negatives
            m.fn += len(anns) - len(matched_ann_indices)

    return metrics


# ── Summary helpers ───────────────────────────────────────────────────────────

def metrics_to_dataframe(metrics: Dict[str, PerClassMetrics]) -> pd.DataFrame:
    rows = []
    for cls, m in metrics.items():
        rows.append({
            "class": cls,
            "tp": m.tp, "fp": m.fp, "fn": m.fn,
            "precision": round(m.precision, 4),
            "recall": round(m.recall, 4),
            "f1": round(m.f1, 4),
            "mean_iou": round(m.mean_iou, 4),
            "matched": m.matched_count,
        })
    return pd.DataFrame(rows).sort_values("class").reset_index(drop=True)


def print_metrics_table(metrics: Dict[str, PerClassMetrics], title: str = ""):
    """Print a formatted metrics table (requires rich)."""
    try:
        from rich.table import Table
        from rich.console import Console
        console = Console()
        table = Table(title=title or "Detection Metrics", show_lines=False)
        for col in ["class", "tp", "fp", "fn", "precision", "recall", "f1", "mean_iou"]:
            table.add_column(col, justify="right" if col != "class" else "left")
        for cls, m in sorted(metrics.items()):
            table.add_row(
                cls, str(m.tp), str(m.fp), str(m.fn),
                f"{m.precision:.3f}", f"{m.recall:.3f}", f"{m.f1:.3f}",
                f"{m.mean_iou:.3f}",
            )
        console.print(table)
    except ImportError:
        print(f"\n{title}")
        for cls, m in sorted(metrics.items()):
            print(f"  {cls:20s}  P={m.precision:.3f}  R={m.recall:.3f}  "
                  f"F1={m.f1:.3f}  mIoU={m.mean_iou:.3f}")
