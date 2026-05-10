#!/usr/bin/env python3
"""Run thesis Layer 4 validation over Layer 3 constraints."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.layer4_validation import Layer4Inputs, run_layer4_validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step-records", type=Path, required=True)
    parser.add_argument("--predicates", type=Path, required=True)
    parser.add_argument("--constraints", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = run_layer4_validation(
        Layer4Inputs(
            step_records_path=args.step_records,
            predicates_path=args.predicates,
            constraints_path=args.constraints,
            output_path=args.output,
        )
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
