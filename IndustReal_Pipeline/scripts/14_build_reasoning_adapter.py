#!/usr/bin/env python3
"""Build thesis Layer 1/2 adapter outputs from existing IndustReal graph CSVs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.reasoning_adapter import (
    DEFAULT_CSV_DIR,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_RUN_ID,
    AdapterInputs,
    build_reasoning_adapter_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", type=str, default=DEFAULT_RUN_ID)
    parser.add_argument("--csv-dir", type=Path, default=DEFAULT_CSV_DIR)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--clip-result-id", type=str, default=None)
    parser.add_argument("--mode", type=str, default=None)
    parser.add_argument("--archive", type=str, default=None)
    parser.add_argument("--clip", type=str, default=None)
    parser.add_argument("--evidence-root", type=Path, default=None)
    args = parser.parse_args()

    output_dir = args.output_dir or (args.output_root / args.run_id)
    result = build_reasoning_adapter_outputs(
        AdapterInputs(
            csv_dir=args.csv_dir,
            run_id=args.run_id,
            output_dir=output_dir,
            clip_result_id=args.clip_result_id,
            mode=args.mode,
            archive_name=args.archive,
            clip=args.clip,
            evidence_root=args.evidence_root,
        )
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
