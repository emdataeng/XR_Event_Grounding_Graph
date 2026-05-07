"""Lightweight temporal smoothing for per-frame 2D detections."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def bbox_iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    if union <= 0.0:
        return 0.0
    return inter / union


def smooth_frame_evidence(
    frame_records: list[dict[str, Any]],
    *,
    iou_threshold: float,
    track_decay: float,
) -> list[dict[str, Any]]:
    last_by_component: dict[str, dict[str, Any]] = {}
    next_track_id = 1
    smoothed: list[dict[str, Any]] = []
    for frame in sorted(frame_records, key=lambda item: int(item["frame_idx"])):
        detections = []
        for det in frame.get("detections", []):
            component = str(det.get("canonical_component", ""))
            previous = last_by_component.get(component)
            det = dict(det)
            if previous is not None:
                overlap = bbox_iou(list(det["bbox_xyxy"]), list(previous["bbox_xyxy"]))
                if overlap >= iou_threshold:
                    det["track_id"] = previous["track_id"]
                    det["smoothed_confidence"] = max(
                        float(det["confidence"]),
                        float(previous["smoothed_confidence"]) * float(track_decay),
                    )
                else:
                    det["track_id"] = next_track_id
                    next_track_id += 1
                    det["smoothed_confidence"] = float(det["confidence"])
            else:
                det["track_id"] = next_track_id
                next_track_id += 1
                det["smoothed_confidence"] = float(det["confidence"])
            last_by_component[component] = {
                "track_id": det["track_id"],
                "bbox_xyxy": list(det["bbox_xyxy"]),
                "smoothed_confidence": det["smoothed_confidence"],
            }
            detections.append(det)
        smoothed.append({**frame, "detections": detections})
    return smoothed


def save_jsonl(records: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows
