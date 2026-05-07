#!/usr/bin/env python3
"""Prepare the deterministic raw IndustReal pilot slice under /tmp."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pilot_assets import prepare_pilot_assets
from src.raw_cad_config import RawCadPaths, load_raw_cad_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    summary = prepare_pilot_assets(cfg, paths=paths)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
