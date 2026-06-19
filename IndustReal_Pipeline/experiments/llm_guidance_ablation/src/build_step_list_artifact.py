"""Build the deterministic procedural step-list prompt artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from context_builders import render_step_list


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step-records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_step_records(path: Path) -> list[Any]:
    """Load JSONL step records in their source order."""
    if not path.exists():
        raise FileNotFoundError(f"Step records are missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    args = parse_args()
    rendered = render_step_list(load_step_records(args.step_records))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
