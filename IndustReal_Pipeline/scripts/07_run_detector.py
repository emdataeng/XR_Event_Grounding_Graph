#!/usr/bin/env python3
"""Run the raw detector backend and temporal smoothing on the current slice."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cad_catalog import load_cad_artifacts
from src.detector_rgb import run_detector_for_clip
from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config
from src.track2d import save_jsonl, smooth_frame_evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--slice-id", type=str, default=None)
    parser.add_argument("--backend", type=str, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    latest = load_latest_slice(paths)
    slice_id = args.slice_id or latest["slice_id"]
    cad_dir = paths.slice_cad_dir(slice_id)
    part_catalog, state_catalog = load_cad_artifacts(cad_dir)
    manifests_dir = paths.slice_manifests_dir(slice_id)
    slice_dir = paths.slice_workdir(slice_id)

    outputs = []
    for manifest_path in sorted(manifests_dir.glob("*_raw_manifest.csv")):
        clip = manifest_path.name.replace("_raw_manifest.csv", "")
        manifest_df = pd.read_csv(manifest_path)
        clip_dir = slice_dir / clip
        raw_records = run_detector_for_clip(
            manifest_df,
            clip_dir=clip_dir,
            part_catalog=part_catalog,
            state_catalog=state_catalog,
            cfg=cfg,
            backend=args.backend,
        )
        smoothed = smooth_frame_evidence(
            raw_records,
            iou_threshold=float(cfg["detector"]["iou_smoothing_threshold"]),
            track_decay=float(cfg["detector"]["track_decay"]),
        )
        clip_result_dir = paths.clip_result_dir(slice_id, clip)
        raw_path = clip_result_dir / "frame_evidence.jsonl"
        smoothed_path = clip_result_dir / "smoothed_frame_evidence.jsonl"
        save_jsonl(raw_records, raw_path)
        save_jsonl(smoothed, smoothed_path)
        outputs.append(
            {
                "clip": clip,
                "backend": args.backend or cfg["detector"]["default_backend"],
                "frame_evidence_path": str(raw_path),
                "smoothed_frame_evidence_path": str(smoothed_path),
                "n_frames": len(raw_records),
                "n_frames_with_evidence": sum(
                    1
                    for row in smoothed
                    if row.get("detections") or row.get("source_state_name") or row.get("source_error_steps")
                ),
            }
        )
    print(json.dumps({"slice_id": slice_id, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
