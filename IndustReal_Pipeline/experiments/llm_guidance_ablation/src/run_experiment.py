"""Entry point for running LLM guidance ablation conditions."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from context_builders import PromptCondition, build_context
from graph_loader import DatasetSelection, load_experiment_artifacts
from lm_client import LMClient, LMConfig


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for a placeholder experiment run."""
    parser = argparse.ArgumentParser(description="Run an LLM guidance ablation condition.")
    parser.add_argument("--config", default="experiments/llm_guidance_ablation/config.yaml")
    parser.add_argument("--condition", choices=[condition.value for condition in PromptCondition], required=True)
    parser.add_argument("--industreal", metavar="CLIP_ID", help="Run against an IndustReal clip id.")
    parser.add_argument("--dataset", help="Run against a non-IndustReal dataset identifier.")
    return parser.parse_args()


def load_config(config_path: str) -> dict[str, Any]:
    """Load experiment configuration from YAML."""
    with Path(config_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_lm_config(config: dict[str, Any]) -> LMConfig:
    """Extract LLM client configuration from the experiment config."""
    return LMConfig(
        api_base_url=config["api_base_url"],
        api_key=config["api_key"],
        model_name=config["model_name"],
        temperature=float(config["temperature"]),
        max_tokens=int(config["max_tokens"]),
    )


def select_dataset(args: argparse.Namespace, config: dict[str, Any]) -> DatasetSelection:
    """Resolve dataset selection from CLI arguments and config defaults."""
    if args.industreal:
        return DatasetSelection(kind="industreal", clip_id=args.industreal)
    if args.dataset:
        return DatasetSelection(kind=args.dataset)

    dataset_config = config.get("dataset", {})
    return DatasetSelection(
        kind=dataset_config.get("default_kind", "industreal"),
        clip_id=dataset_config.get("default_clip_id"),
    )


def run_placeholder_experiment(
    condition: PromptCondition,
    config: dict[str, Any],
    selection: DatasetSelection,
) -> None:
    """Define the high-level experiment flow without executing it yet."""
    artifacts = load_experiment_artifacts(config, selection)
    client = LMClient(build_lm_config(config))
    _ = build_context(condition, test_case={}, artifacts=artifacts)
    _ = client
    raise NotImplementedError("Experiment execution is not implemented yet.")


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    config = load_config(args.config)
    selection = select_dataset(args, config)
    condition = PromptCondition(args.condition)
    run_placeholder_experiment(condition, config, selection)


if __name__ == "__main__":
    main()
