#!/usr/bin/env python3
"""Aggregate raw manifest validation for the current slice."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config
from src.raw_manifest import validate_raw_manifest


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
    manifests_dir = paths.slice_manifests_dir(slice_id)
    reports = []
    for manifest_path in sorted(manifests_dir.glob("*_raw_manifest.csv")):
        clip = manifest_path.name.replace("_raw_manifest.csv", "")
        df = pd.read_csv(manifest_path)
        report = validate_raw_manifest(df, slice_dir / clip)
        report["manifest_path"] = str(manifest_path)
        reports.append(report)
    print(json.dumps({"slice_id": slice_id, "reports": reports}, indent=2))


if __name__ == "__main__":
    main()
