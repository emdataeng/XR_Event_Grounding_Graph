#!/usr/bin/env python3
"""Run the whole-dataset oracle batch pipeline over configured IndustReal archives."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.raw_cad_config import RawCadPaths, configure_runtime_environment, load_raw_cad_config


def _optional_set(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    return {value for value in values if value}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "raw_cad_dataset.json")
    parser.add_argument("--run-id", type=str, default=None)
    parser.add_argument("--archives", nargs="*", default=None)
    parser.add_argument("--clips", nargs="*", default=None)
    parser.add_argument("--modes", nargs="*", default=None)
    parser.add_argument("--download-missing", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    configure_runtime_environment(paths)
    from src.dataset_batch import run_oracle_dataset_batch

    result = run_oracle_dataset_batch(
        cfg,
        paths=paths,
        run_id=args.run_id,
        archive_filters=_optional_set(args.archives),
        clip_filters=_optional_set(args.clips),
        mode_filters=_optional_set(args.modes),
        download_missing=args.download_missing,
        resume=False if args.no_resume else None,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
