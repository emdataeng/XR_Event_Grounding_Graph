#!/usr/bin/env python3
"""Run CAD-grounded state reasoning for each clip in the current slice."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cad_catalog import load_cad_artifacts
from src.cad_reasoner import (
    oracle_state_sequence_from_labels,
    reason_state_sequence,
    save_state_sequence,
)
from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config
from src.track2d import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--slice-id", type=str, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    latest = load_latest_slice(paths)
    slice_id = args.slice_id or latest["slice_id"]
    _, state_catalog = load_cad_artifacts(paths.slice_cad_dir(slice_id))
    slice_dir = paths.slice_workdir(slice_id)
    oracle_mode = str(cfg["detector"].get("oracle_mode", "state_labels"))
    default_backend = str(cfg["detector"].get("default_backend", "oracle_od"))

    outputs = []
    for clip_dir in sorted(paths.slice_results_dir(slice_id).iterdir()):
        if not clip_dir.is_dir() or clip_dir.name in {"cad", "manifests", "debug_visuals"}:
            continue
        manifest_path = paths.slice_manifests_dir(slice_id) / f"{clip_dir.name}_raw_manifest.csv"
        if not manifest_path.exists():
            continue
        manifest_df = pd.read_csv(manifest_path)
        if default_backend == "oracle_od" and oracle_mode == "state_labels":
            rows = oracle_state_sequence_from_labels(
                manifest_df.to_dict("records"),
                clip_dir=slice_dir / clip_dir.name,
                state_catalog=state_catalog,
            )
        else:
            smoothed_path = clip_dir / "smoothed_frame_evidence.jsonl"
            if not smoothed_path.exists():
                continue
            rows = reason_state_sequence(
                load_jsonl(smoothed_path),
                state_catalog=state_catalog,
                cfg=cfg,
            )
        out_path = clip_dir / "state_sequence.csv"
        save_state_sequence(rows, out_path)
        outputs.append(
            {
                "clip": clip_dir.name,
                "state_sequence_path": str(out_path),
                "n_rows": len(rows),
                "state_mode": oracle_mode if default_backend == "oracle_od" else "reasoner_viterbi",
            }
        )
    print(json.dumps({"slice_id": slice_id, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
