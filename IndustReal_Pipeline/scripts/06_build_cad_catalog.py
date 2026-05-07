#!/usr/bin/env python3
"""Build the CAD part/state catalogs for the current raw pilot slice."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cad_catalog import (
    build_cad_part_catalog,
    build_state_catalog,
    load_procedure_info,
    save_cad_artifacts,
)
from src.pilot_assets import load_latest_slice
from src.raw_cad_config import RawCadPaths, load_raw_cad_config, resolve_path


def _resolve_part_zip(cfg: dict, paths: RawCadPaths) -> Path | None:
    repo_zip = resolve_path(cfg["archives"].get("part_geometries_repo"), base=ROOT)
    working_zip = resolve_path(cfg["archives"].get("part_geometries_working"), base=ROOT)
    for candidate in (repo_zip, working_zip):
        if candidate is not None and candidate.exists():
            return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--slice-id", type=str, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    latest = load_latest_slice(paths)
    slice_id = args.slice_id or latest["slice_id"]
    proc_info = load_procedure_info(ROOT / "configs" / "procedure_info.json")
    part_zip = _resolve_part_zip(cfg, paths)
    asd_zip = paths.resolve_archive_path("asd_results_zip")
    if asd_zip is None or not asd_zip.exists():
        raise FileNotFoundError(f"missing ASD results zip: {asd_zip}")

    part_catalog = build_cad_part_catalog(cfg, part_geometries_zip=part_zip)
    state_catalog = build_state_catalog(cfg, procedure_info=proc_info, asd_results_zip=asd_zip)
    part_path, state_path = save_cad_artifacts(
        paths.slice_cad_dir(slice_id),
        part_catalog=part_catalog,
        state_catalog=state_catalog,
    )
    print(
        json.dumps(
            {
                "slice_id": slice_id,
                "part_catalog": str(part_path),
                "state_catalog": str(state_path),
                "part_geometries_zip": str(part_zip) if part_zip else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
