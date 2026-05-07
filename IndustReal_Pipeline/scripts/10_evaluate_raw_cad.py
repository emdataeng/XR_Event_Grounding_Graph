#!/usr/bin/env python3
"""Evaluate the CAD-grounded raw pilot outputs clip by clip."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.eval_raw_cad import compile_clip_metrics, load_slice_summary, save_metrics, save_summary_csv
from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config
from src.cad_reasoner import load_state_sequence
from src.cad_catalog import load_procedure_info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--slice-id", type=str, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    latest = load_latest_slice(paths)
    slice_id = args.slice_id or latest["slice_id"]
    slice_summary = load_slice_summary(paths.slice_summary_path(slice_id))
    slice_dir = paths.slice_workdir(slice_id)
    proc_info = load_procedure_info(ROOT / "configs" / "procedure_info.json")

    summary_rows = []
    for clip_dir in sorted(paths.slice_results_dir(slice_id).iterdir()):
        if not clip_dir.is_dir() or clip_dir.name in {"cad", "manifests", "debug_visuals"}:
            continue
        clip = clip_dir.name
        state_path = clip_dir / "state_sequence.csv"
        psr_pred_path = clip_dir / "psr_pred.json"
        if not state_path.exists() or not psr_pred_path.exists():
            continue
        state_rows = load_state_sequence(state_path)
        psr_pred = json.loads(psr_pred_path.read_text())
        diagnostic_path = clip_dir / "psr_pred_b3_diagnostic.json"
        psr_pred_b3 = json.loads(diagnostic_path.read_text()) if diagnostic_path.exists() else []
        gt_path = clip_dir / "slice_gt_steps.json"
        psr_gt = json.loads(gt_path.read_text()) if gt_path.exists() else []
        metrics = compile_clip_metrics(
            clip=clip,
            clip_dir=slice_dir / clip,
            state_rows=state_rows,
            psr_gt=psr_gt,
            psr_pred=psr_pred,
            psr_pred_b3=psr_pred_b3,
            evidence_path=clip_dir / "smoothed_frame_evidence.jsonl",
            slice_summary=slice_summary,
            proc_info=proc_info,
        )
        save_metrics(metrics, clip_dir / "metrics.json")
        summary_rows.append(metrics)

    save_summary_csv(summary_rows, paths.slice_results_dir(slice_id) / "summary.csv")
    print(json.dumps({"slice_id": slice_id, "summary_rows": summary_rows}, indent=2))


if __name__ == "__main__":
    main()
