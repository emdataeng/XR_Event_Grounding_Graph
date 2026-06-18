"""Entry point for running LLM guidance ablation conditions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from context_builders import PromptCondition, build_context
from lm_client import ask_llm, set_config_path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for an experiment run."""
    parser = argparse.ArgumentParser(description="Run an LLM guidance ablation condition.")
    parser.add_argument("--config", default=str(EXPERIMENT_ROOT / "configs" / "config.yaml"))
    parser.add_argument("--condition", choices=[condition.value for condition in PromptCondition], required=True)
    parser.add_argument("--industreal", metavar="CLIP_ID", help="Run against an IndustReal clip id.")
    parser.add_argument("--dataset", help="Run against a non-IndustReal dataset identifier.")
    return parser.parse_args()


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load experiment configuration from YAML."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"config.yaml is missing: {path}")

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_test_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Load novice operator questions from the configured YAML file."""
    test_cases_path = resolve_configured_path(config["input_paths"]["test_cases"])
    if not test_cases_path.exists():
        raise FileNotFoundError(f"novice_questions.yaml is missing: {test_cases_path}")

    with test_cases_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    test_cases = data.get("test_cases")
    if not isinstance(test_cases, list):
        raise ValueError(f"Expected 'test_cases' to be a list in {test_cases_path}")
    return test_cases


def load_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Load optional artifacts needed by context builders.

    For this first milestone, missing placeholder paths are allowed. The
    steps-only condition can still run and will tell the model that no generated
    step artifact was found for the case.
    """
    artifacts = {"prompt_templates": load_prompt_templates(config)}
    generated_steps_path = resolve_configured_path(config["input_paths"]["generated_steps"])
    if not generated_steps_path.exists() or "PLACEHOLDER" in str(generated_steps_path):
        artifacts["generated_steps"] = {}
        return artifacts

    with generated_steps_path.open("r", encoding="utf-8") as handle:
        if generated_steps_path.suffix.lower() in {".yaml", ".yml"}:
            generated_steps = yaml.safe_load(handle)
        elif generated_steps_path.suffix.lower() == ".jsonl":
            generated_steps = [json.loads(line) for line in handle if line.strip()]
        else:
            generated_steps = json.load(handle)
    artifacts["generated_steps"] = generated_steps
    return artifacts


def load_prompt_templates(config: dict[str, Any]) -> dict[str, Any]:
    """Load all prompt templates from the configured prompt YAML file."""
    prompt_path = resolve_configured_path(config["prompt_paths"]["prompts"])
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template config is missing: {prompt_path}")

    with prompt_path.open("r", encoding="utf-8") as handle:
        prompts = yaml.safe_load(handle) or {}
    if not isinstance(prompts, dict):
        raise ValueError(f"Expected prompt template config to be a mapping: {prompt_path}")
    return prompts


def resolve_configured_path(path_value: str) -> Path:
    """Resolve config paths from common execution locations."""
    path = Path(path_value)
    if path.is_absolute():
        return path

    for base in (Path.cwd(), REPO_ROOT, EXPERIMENT_ROOT):
        candidate = base / path
        if candidate.exists():
            return candidate

    return REPO_ROOT / path


def output_path_for_run(config: dict[str, Any], condition: PromptCondition, timestamp: str) -> Path:
    """Create the output JSONL path for a run."""
    output_root = resolve_configured_path(config.get("output_paths", {}).get("root", "outputs"))
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root / f"responses_{condition.value}_{timestamp}.jsonl"


def run_experiment(condition: PromptCondition, config: dict[str, Any]) -> Path:
    """Run one prompting condition across all novice question test cases."""
    if condition is not PromptCondition.STEPS_ONLY:
        raise NotImplementedError(
            f"{condition.value} is not implemented yet. Use --condition steps_only for this milestone."
        )

    test_cases = load_test_cases(config)
    artifacts = load_artifacts(config)
    timestamp = local_timestamp_for_filename()
    output_path = output_path_for_run(config, condition, timestamp)

    with output_path.open("w", encoding="utf-8") as handle:
        for test_case in test_cases:
            context = build_context(condition, test_case, artifacts)
            response = ask_llm(context["system_prompt"], context["user_prompt"])
            row = {
                "case_id": test_case.get("case_id"),
                "condition": condition.value,
                "step_id": test_case.get("step_id"),
                "question": test_case.get("question"),
                "response": response,
                "risk_type": test_case.get("risk_type"),
                "expected_answer_elements": test_case.get("expected_answer_elements"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    return output_path


def local_timestamp_for_filename() -> str:
    """Return a local timestamp with timezone offset for output filenames."""
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def main() -> None:
    """CLI entry point."""
    try:
        args = parse_args()
        set_config_path(args.config)
        config = load_config(args.config)
        condition = PromptCondition(args.condition)
        output_path = run_experiment(condition, config)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except NotImplementedError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"Error: experiment failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Wrote responses to {output_path}")


if __name__ == "__main__":
    main()
