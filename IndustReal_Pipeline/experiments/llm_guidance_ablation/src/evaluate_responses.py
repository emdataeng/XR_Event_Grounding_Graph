"""Placeholder evaluation entry point for generated novice-support responses."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for response evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate generated ablation responses.")
    parser.add_argument("--config", default="experiments/llm_guidance_ablation/config.yaml")
    return parser.parse_args()


def load_config(config_path: str) -> dict[str, Any]:
    """Load experiment configuration from YAML."""
    with Path(config_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def evaluate_responses(config: dict[str, Any]) -> None:
    """Evaluate responses against held-out evaluation metadata.

    The fields `risk_type` and `expected_answer_elements` may be used here, but
    must not be included in any prompt construction path.
    """
    _ = config
    raise NotImplementedError("Response evaluation is not implemented yet.")


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    evaluate_responses(load_config(args.config))


if __name__ == "__main__":
    main()
