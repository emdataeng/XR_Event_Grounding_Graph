"""Evaluation helpers for the raw CAD pilot."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from .psr import _match_indices, evaluate
from .raw_loader import load_od_labels, load_step_labels_csv
from .track2d import load_jsonl


def evaluate_state_predictions(
    state_rows: list[dict[str, Any]],
    *,
    clip_dir: Path,
) -> dict[str, Any]:
    od_labels = load_od_labels(clip_dir / "OD_labels.json")
    total = 0
    correct = 0
    for row in state_rows:
        gt = od_labels.get(f"{int(row['frame_idx']):06d}.jpg")
        if gt is None:
            continue
        total += 1
        if str(row["predicted_state"]) == str(gt["state_name"]):
            correct += 1
    return {
        "state_frames_scored": total,
        "state_accuracy": (correct / total) if total else 0.0,
        "state_correct": correct,
    }


def error_window_recall(
    state_rows: list[dict[str, Any]],
    *,
    clip_dir: Path,
    pre: int = 120,
    post: int = 60,
) -> float | None:
    step_rows = load_step_labels_csv(clip_dir / "PSR_labels_with_errors.csv")
    error_steps = [row for row in step_rows if str(row["description"]).startswith("Incorrectly ")]
    if not error_steps:
        return None
    frame_set = {int(row["frame_idx"]) for row in state_rows}
    score_start_frame = None
    for row in state_rows:
        if str(row.get("state_origin", "")) != "seeded_initial_state":
            score_start_frame = int(row["frame_idx"])
            break
    filtered_error_steps = []
    for row in error_steps:
        if int(row["frame_idx"]) not in frame_set:
            continue
        if score_start_frame is not None and int(row["frame_idx"]) < score_start_frame:
            continue
        filtered_error_steps.append(row)
    if not filtered_error_steps:
        return None
    predicted_error_frames = {
        int(row["frame_idx"])
        for row in state_rows
        if str(row["predicted_state"]) == "error_state"
    }
    hits = 0
    for row in filtered_error_steps:
        start = max(0, int(row["frame_idx"]) - pre)
        end = int(row["frame_idx"]) + post
        if any(start <= frame <= end for frame in predicted_error_frames):
            hits += 1
    return hits / len(filtered_error_steps)


def detector_window_coverage(
    evidence_rows: list[dict[str, Any]],
    *,
    slice_summary: dict[str, Any],
    clip_name: str,
    score_start_frame: int | None = None,
) -> float | None:
    clip_info = next((item for item in slice_summary.get("clips", []) if item["clip"] == clip_name), None)
    if clip_info is None:
        return None
    event_windows = [
        window for window in clip_info.get("windows", [])
        if not any(reason.startswith("context_") for reason in window.get("reasons", []))
    ]
    if score_start_frame is not None:
        event_windows = [
            window for window in event_windows
            if int(window["end"]) >= int(score_start_frame)
        ]
    if not event_windows:
        return None
    frames_with_evidence = {
        int(row["frame_idx"])
        for row in evidence_rows
        if row.get("detections") or row.get("source_state_name") or row.get("source_error_steps")
    }
    hits = 0
    for window in event_windows:
        if any(int(window["start"]) <= frame <= int(window["end"]) for frame in frames_with_evidence):
            hits += 1
    return hits / len(event_windows)


def step_metrics(
    gt: list[dict[str, Any]],
    pred: list[dict[str, Any]],
    proc_info: list[dict[str, Any]],
) -> dict[str, Any]:
    if not gt:
        precision = 1.0 if not pred else 0.0
        return {
            "step_precision": precision,
            "step_recall": 1.0,
            "median_step_delay_frames": 0,
        }

    gt_times = np.array([e["frame"] for e in gt], dtype=int)
    gt_ids = np.array([e["id"] for e in gt], dtype=int)
    pred_times = np.array([e["frame"] for e in pred], dtype=int) if pred else np.array([], dtype=int)
    pred_ids = np.array([e["id"] for e in pred], dtype=int) if pred else np.array([], dtype=int)
    sys_fps = 0
    sys_fns = 0
    delays: list[int] = []
    for step in proc_info:
        sid = step["id"]
        ig = list(np.where(gt_ids == sid)[0])
        ip = list(np.where(pred_ids == sid)[0])
        if not ig and ip:
            sys_fps += len(ip)
        elif ig and not ip:
            sys_fns += len(ig)
        else:
            if len(ig) > len(ip):
                sys_fns += len(ig) - len(ip)
                ig = _match_indices(ig, gt_times, ip, pred_times)
            elif len(ip) > len(ig):
                sys_fps += len(ip) - len(ig)
                ip = _match_indices(ip, pred_times, ig, gt_times)
            for i_gt, i_pred in zip(ig, ip):
                delta = int(pred_times[i_pred]) - int(gt_times[i_gt])
                if delta < 0:
                    sys_fps += 1
                else:
                    delays.append(delta)
    sys_tps = max(0, len(pred_ids) - sys_fps)
    precision = sys_tps / (sys_tps + sys_fps) if (sys_tps + sys_fps) else 0.0
    recall = sys_tps / (sys_tps + sys_fns) if (sys_tps + sys_fns) else 0.0
    median_delay = int(np.median(delays)) if delays else None
    return {
        "step_precision": precision,
        "step_recall": recall,
        "median_step_delay_frames": median_delay,
    }


def load_slice_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def compile_clip_metrics(
    *,
    clip: str,
    clip_dir: Path,
    state_rows: list[dict[str, Any]],
    psr_gt: list[dict[str, Any]],
    psr_pred: list[dict[str, Any]],
    psr_pred_b3: list[dict[str, Any]],
    evidence_path: Path,
    slice_summary: dict[str, Any],
    proc_info: list[dict[str, Any]],
) -> dict[str, Any]:
    state_metrics = evaluate_state_predictions(state_rows, clip_dir=clip_dir)
    psr_metrics = evaluate(psr_gt, psr_pred, proc_info)
    diagnostic_metrics = evaluate(psr_gt, psr_pred_b3, proc_info)
    direct_step_metrics = step_metrics(psr_gt, psr_pred, proc_info)
    diagnostic_step_metrics = step_metrics(psr_gt, psr_pred_b3, proc_info)
    evidence_rows = load_jsonl(evidence_path)
    score_start_frame = None
    for row in state_rows:
        if str(row.get("state_origin", "")) != "seeded_initial_state":
            score_start_frame = int(row["frame_idx"])
            break
    coverage = detector_window_coverage(
        evidence_rows,
        slice_summary=slice_summary,
        clip_name=clip,
        score_start_frame=score_start_frame,
    )
    error_recall = error_window_recall(state_rows, clip_dir=clip_dir)
    return {
        "clip": clip,
        **state_metrics,
        "score_start_frame": score_start_frame,
        "scored_gt_steps": len(psr_gt),
        "predicted_steps": len(psr_pred),
        "diagnostic_predicted_steps": len(psr_pred_b3),
        "legal_state_rate": 1.0 if state_rows else 0.0,
        "error_window_recall": error_recall,
        "event_window_evidence_ratio": coverage,
        **direct_step_metrics,
        "psr_pos": psr_metrics["pos"],
        "psr_f1": psr_metrics["f1"],
        "psr_avg_delay_s": psr_metrics["avg_delay_s"],
        "psr_tps": psr_metrics["system_TPs"],
        "psr_fps": psr_metrics["system_FPs"],
        "psr_fns": psr_metrics["system_FNs"],
        "b3_diagnostic_step_precision": diagnostic_step_metrics["step_precision"],
        "b3_diagnostic_step_recall": diagnostic_step_metrics["step_recall"],
        "b3_diagnostic_median_delay_frames": diagnostic_step_metrics["median_step_delay_frames"],
        "b3_diagnostic_psr_pos": diagnostic_metrics["pos"],
        "b3_diagnostic_psr_f1": diagnostic_metrics["f1"],
        "b3_diagnostic_psr_avg_delay_s": diagnostic_metrics["avg_delay_s"],
    }


def save_metrics(metrics: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2))


def save_summary_csv(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        out_path.write_text("")
        return
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
