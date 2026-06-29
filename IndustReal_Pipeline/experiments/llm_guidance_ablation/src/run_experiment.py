"""Entry point for running LLM guidance ablation conditions."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

SHARED_EXPERIMENTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SHARED_EXPERIMENTS_DIR))

from context_builders import PromptCondition, build_context
from export_prompt_reports import export_prompt_reports
from graph_loader import graph_artifact_path, load_procedural_reasoning_graph
from lm_client import ask_llm, set_config_path
from shared.graph_retrieval_config import load_graph_retrieval_config
from shared.id_compaction import step_provenance


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
ALL_CONDITIONS = "all"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for an experiment run."""
    parser = argparse.ArgumentParser(description="Run an LLM guidance ablation condition.")
    parser.add_argument("--config", default=str(EXPERIMENT_ROOT / "configs" / "config.yaml"))
    condition_choices = [condition.value for condition in PromptCondition] + [ALL_CONDITIONS]
    parser.add_argument("--condition", choices=condition_choices, required=True)
    dataset_group = parser.add_mutually_exclusive_group()
    dataset_group.add_argument("--industreal", metavar="CLIP_ID", help="Run against an IndustReal clip id.")
    dataset_group.add_argument("--dataset", help="Run against a non-IndustReal dataset identifier.")
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
    if isinstance(test_cases, list):
        return test_cases

    scenario_groups = data.get("scenario_groups")
    if isinstance(scenario_groups, dict):
        return flatten_grouped_cases(scenario_groups, group_field="scenario")

    risk_groups = data.get("risk_groups")
    if isinstance(risk_groups, dict):
        return flatten_grouped_cases(risk_groups, group_field="risk_type")

    raise ValueError(
        f"Expected 'test_cases' list, 'scenario_groups' mapping, or 'risk_groups' mapping in {test_cases_path}"
    )


def flatten_grouped_cases(groups: dict[str, Any], group_field: str) -> list[dict[str, Any]]:
    """Flatten grouped test cases while preserving the group as metadata."""
    test_cases = []
    for group_name, grouped_cases in groups.items():
        if not isinstance(grouped_cases, list):
            raise ValueError(f"Expected {group_field} group '{group_name}' to contain a list of cases.")

        for test_case in grouped_cases:
            if not isinstance(test_case, dict):
                raise ValueError(f"Expected each case in {group_field} group '{group_name}' to be a mapping.")
            flattened_case = dict(test_case)
            flattened_case.setdefault(group_field, group_name)
            if group_field == "scenario":
                flattened_case.setdefault("risk_type", group_name)
            test_cases.append(flattened_case)
    return test_cases


def load_artifacts(
    config: dict[str, Any],
    dataset_id: str | None = None,
    condition: PromptCondition | None = None,
) -> dict[str, Any]:
    """Load the frozen step list and optional condition-specific artifacts."""
    artifacts = {"prompt_templates": load_prompt_templates(config)}
    # The frozen step list is shared verbatim so conditions differ only in the
    # additional symbolic context they receive.
    for artifact_name in ("step_list", "thesis_rules"):
        configured_path = config.get("input_paths", {}).get(artifact_name)
        if not configured_path:
            artifacts[artifact_name] = ""
            continue
        artifact_path = resolve_configured_path(configured_path)
        if not artifact_path.exists() or "PLACEHOLDER" in str(artifact_path):
            artifacts[artifact_name] = ""
            continue
        artifacts[artifact_name] = artifact_path.read_text(encoding="utf-8")

    if condition in {None, PromptCondition.SYMBOLIC_DOMAIN}:
        predicate_context_path = resolve_configured_path(config["input_paths"]["predicate_contexts"])
        if not predicate_context_path.exists():
            raise FileNotFoundError(f"Predicate context artifact is missing: {predicate_context_path}")
        with predicate_context_path.open("r", encoding="utf-8") as handle:
            artifacts["predicate_contexts"] = json.load(handle)
    retrieval_path = resolve_configured_path(config["graph_retrieval_config"])
    artifacts.update(load_graph_retrieval_config(retrieval_path))

    if condition in {None, PromptCondition.GRAPH_GROUNDED}:
        configured_graph_path = str(config.get("input_paths", {}).get("procedural_reasoning_graph") or "").strip()
        if configured_graph_path and "PLACEHOLDER" not in configured_graph_path:
            graph_path = resolve_configured_path(configured_graph_path)
        else:
            selected_dataset = dataset_id or str(config.get("dataset", {}).get("default_clip_id") or "").strip()
            graph_root = REPO_ROOT / "results" / "procedural_reasoning_graph"
            graph_path = graph_artifact_path(graph_root, selected_dataset)
        artifacts["procedural_reasoning_graph"] = load_procedural_reasoning_graph(graph_path)
        artifacts["procedural_reasoning_graph_path"] = str(graph_path)

    # TODO: Filter rules by matched action or predicate vocabulary if the full
    # rule file becomes too large. Predicate context is already step-windowed.
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


def prompt_report_dir_for_run(config: dict[str, Any], condition: PromptCondition, timestamp: str) -> Path:
    """Create the prompt report directory for a run."""
    output_root = resolve_configured_path(config.get("output_paths", {}).get("root", "outputs"))
    return output_root / "prompt_reports" / f"{condition.value}_{timestamp}"


def log_path_for_run(config: dict[str, Any], condition: PromptCondition, timestamp: str) -> Path:
    """Create the communication-flow log path for a run."""
    output_root = resolve_configured_path(config.get("output_paths", {}).get("root", "outputs"))
    log_root = output_root / "logs"
    log_root.mkdir(parents=True, exist_ok=True)
    return log_root / f"communication_{condition.value}_{timestamp}.log"


def _write_log_event(handle: Any, event: str, **fields: Any) -> None:
    """Write a structured event in the same local timezone as its filename."""
    record = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "event": event,
        **fields,
    }
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    handle.flush()


def format_duration_hms(seconds: float) -> str:
    """Format elapsed seconds as hours, minutes, and seconds."""
    hours, remainder = divmod(max(0.0, seconds), 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {remaining_seconds:05.2f}s"


def build_run_statistics(durations: list[float], total_seconds: float) -> dict[str, Any]:
    """Build reproducible summary fields for completed LLM interactions."""
    return {
        "completed_interactions": len(durations),
        "min_interaction_seconds": round(min(durations), 6) if durations else None,
        "max_interaction_seconds": round(max(durations), 6) if durations else None,
        "avg_interaction_seconds": round(sum(durations) / len(durations), 6) if durations else None,
        "total_duration_seconds": round(total_seconds, 6),
        "total_duration_hms": format_duration_hms(total_seconds),
    }


def run_experiment(
    condition: PromptCondition,
    config: dict[str, Any],
    dataset_id: str | None = None,
) -> tuple[Path, Path, Path]:
    """Run one prompting condition across all novice question test cases."""
    test_cases = load_test_cases(config)
    artifacts = load_artifacts(config, dataset_id=dataset_id, condition=condition)
    timestamp = local_timestamp_for_filename()
    output_path = output_path_for_run(config, condition, timestamp)
    prompt_report_dir = prompt_report_dir_for_run(config, condition, timestamp)
    log_path = log_path_for_run(config, condition, timestamp)
    total_cases = len(test_cases)
    completed_cases = 0
    interaction_durations: list[float] = []
    run_started = time.perf_counter()

    print(f"Starting {condition.value}: {total_cases} LLM interactions")
    print(f"Communication log: {log_path}")
    with log_path.open("w", encoding="utf-8") as log_handle:
        _write_log_event(
            log_handle,
            "run_started",
            condition=condition.value,
            total_interactions=total_cases,
            graph_retrieval={
                "step_hops": artifacts["step_hops"],
                "evidence_hops": artifacts["evidence_hops"],
            },
        )
        try:
            with output_path.open("w", encoding="utf-8") as output_handle:
                for index, test_case in enumerate(test_cases, start=1):
                    case_id = str(test_case.get("case_id") or "unknown")
                    risk_type = str(test_case.get("risk_type") or "unclassified")
                    progress = f"[{index}/{total_cases}]"
                    context = build_context(condition, test_case, artifacts)
                    print(f"{progress} {condition.value} | {risk_type} | {case_id}: sending request")
                    interaction_started = time.perf_counter()
                    _write_log_event(
                        log_handle,
                        "request_sent",
                        condition=condition.value,
                        interaction=index,
                        total_interactions=total_cases,
                        risk_type=risk_type,
                        case_id=case_id,
                    )
                    try:
                        response = ask_llm(context["system_prompt"], context["user_prompt"])
                    except Exception as exc:
                        interaction_duration = time.perf_counter() - interaction_started
                        _write_log_event(
                            log_handle,
                            "interaction_failed",
                            condition=condition.value,
                            interaction=index,
                            risk_type=risk_type,
                            case_id=case_id,
                            duration_seconds=round(interaction_duration, 6),
                            error_type=type(exc).__name__,
                        )
                        raise

                    interaction_duration = time.perf_counter() - interaction_started
                    completed_cases += 1
                    interaction_durations.append(interaction_duration)
                    _write_log_event(
                        log_handle,
                        "response_received",
                        condition=condition.value,
                        interaction=index,
                        total_interactions=total_cases,
                        risk_type=risk_type,
                        case_id=case_id,
                        duration_seconds=round(interaction_duration, 6),
                    )
                    print(f"{progress} completed in {interaction_duration:.2f}s")
                    row = {
                        "case_id": test_case.get("case_id"),
                        "condition": condition.value,
                        "step_id": test_case.get("step_id"),
                        "step_provenance": step_provenance(test_case.get("step_id")),
                        "graph_retrieval": {
                            "step_hops": artifacts["step_hops"],
                            "evidence_hops": artifacts["evidence_hops"],
                        },
                        "question": test_case.get("question"),
                        "response": response,
                        "scenario": test_case.get("scenario"),
                        "risk_type": test_case.get("risk_type"),
                        "status": test_case.get("status"),
                        "expected_answer_elements": test_case.get("expected_answer_elements"),
                        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                    }
                    output_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                    output_handle.flush()

            total_duration = time.perf_counter() - run_started
            run_statistics = build_run_statistics(interaction_durations, total_duration)
            export_prompt_reports(
                config,
                condition,
                prompt_report_dir,
                test_cases,
                artifacts,
                run_statistics=run_statistics,
            )
        except Exception as exc:
            total_duration = time.perf_counter() - run_started
            _write_log_event(
                log_handle,
                "run_failed",
                condition=condition.value,
                completed_interactions=completed_cases,
                total_interactions=total_cases,
                total_duration_seconds=round(total_duration, 6),
                total_duration_hms=format_duration_hms(total_duration),
                error_type=type(exc).__name__,
            )
            raise

        _write_log_event(
            log_handle,
            "run_completed",
            condition=condition.value,
            **run_statistics,
            total_interactions=total_cases,
            responses_path=str(output_path),
            prompt_reports_path=str(prompt_report_dir),
        )

    print(f"Completed {condition.value}: {completed_cases}/{total_cases} interactions")
    print(
        "Prompt timing: "
        f"min={run_statistics['min_interaction_seconds']:.2f}s | "
        f"max={run_statistics['max_interaction_seconds']:.2f}s | "
        f"avg={run_statistics['avg_interaction_seconds']:.2f}s"
    )
    print(f"Total time: {run_statistics['total_duration_hms']}")
    return output_path, prompt_report_dir, log_path


def local_timestamp_for_filename() -> str:
    """Return a local timestamp with timezone offset for output filenames."""
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def selected_conditions(value: str) -> list[PromptCondition]:
    """Expand the CLI condition value into the sequential runs to execute."""
    if value == ALL_CONDITIONS:
        return list(PromptCondition)
    return [PromptCondition(value)]


def main() -> None:
    """CLI entry point."""
    try:
        args = parse_args()
        set_config_path(args.config)
        config = load_config(args.config)
        dataset_id = args.industreal or args.dataset or config.get("dataset", {}).get("default_clip_id")
        run_outputs = []
        for condition in selected_conditions(args.condition):
            run_outputs.append((condition, *run_experiment(condition, config, dataset_id=dataset_id)))
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

    for condition, output_path, prompt_report_dir, log_path in run_outputs:
        print(f"{condition.value}: wrote responses to {output_path}")
        print(f"{condition.value}: wrote prompt reports to {prompt_report_dir}")
        print(f"{condition.value}: wrote communication log to {log_path}")


if __name__ == "__main__":
    main()
