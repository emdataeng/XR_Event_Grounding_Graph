#!/usr/bin/env python3
"""Build per-clip raw manifests for the current pilot slice."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config
from src.raw_manifest import build_raw_manifest, save_manifest, save_manifest_report, validate_raw_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--slice-id", type=str, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    latest = load_latest_slice(paths)
    slice_id = args.slice_id or latest["slice_id"]
    slice_dir = paths.slice_workdir(slice_id)
    summary = json.loads(paths.slice_summary_path(slice_id).read_text())
    manifests_dir = paths.slice_manifests_dir(slice_id)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for clip_meta in summary["clips"]:
        clip = clip_meta["clip"]
        clip_dir = slice_dir / clip
        df = build_raw_manifest(
            clip_dir,
            source_archive=clip_meta["source_archive"],
            split=clip_meta["split"],
        )
        manifest_path = manifests_dir / f"{clip}_raw_manifest.csv"
        report_path = manifests_dir / f"{clip}_raw_manifest_report.json"
        save_manifest(df, manifest_path)
        report = validate_raw_manifest(df, clip_dir)
        save_manifest_report(report, report_path)
        outputs.append(
            {
                "clip": clip,
                "manifest_path": str(manifest_path),
                "report_path": str(report_path),
                "n_rows": len(df),
            }
        )
    print(json.dumps({"slice_id": slice_id, "manifests": outputs}, indent=2))


if __name__ == "__main__":
    main()
