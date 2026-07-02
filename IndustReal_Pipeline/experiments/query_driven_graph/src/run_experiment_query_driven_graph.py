"""Run the template-based query-driven graph experiment."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

CURRENT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = CURRENT_DIR.parents[0]
REPO_ROOT = CURRENT_DIR.parents[2]
LLM_ABLATION_SRC = REPO_ROOT / "experiments" / "llm_guidance_ablation" / "src"
SHARED_EXPERIMENTS_DIR = REPO_ROOT / "experiments"
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(LLM_ABLATION_SRC))
sys.path.insert(0, str(SHARED_EXPERIMENTS_DIR))

from answer_builder import build_answer_prompt, load_prompt_templates  # noqa: E402
from export_query_reports import export_query_reports  # noqa: E402
from lm_client import ask_llm, load_lm_metadata, set_config_path  # noqa: E402
from neo4j_client import client_from_config  # noqa: E402
from query_planner import build_query_plan, canonical_step_id, load_query_template_config  # noqa: E402
from shared.graph_retrieval_config import load_graph_retrieval_config  # noqa: E402
from shared.id_compaction import step_provenance  # noqa: E402
from shared.question_set_manifest import build_question_set_manifest  # noqa: E402


CONDITION = "query_driven_graph"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(EXPERIMENT_ROOT / "configs" / "config_query_driven_graph.yaml"),
    )
    parser.add_argument("--dry-run", action="store_true", help="Run queries and reports without calling the LLM.")
    return parser.parse_args()


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load experiment configuration from YAML."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"config_query_driven_graph.yaml is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError(f"Expected config to be a mapping: {path}")
    return config


def load_test_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Load novice operator questions from YAML."""
    path = resolve_configured_path(config["input_paths"]["test_cases"])
    if not path.exists():
        raise FileNotFoundError(f"novice_questions.yaml is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if isinstance(data.get("test_cases"), list):
        return list(data["test_cases"])
    scenario_groups = data.get("scenario_groups")
    if isinstance(scenario_groups, dict):
        return flatten_grouped_cases(scenario_groups, group_field="scenario")

    risk_groups = data.get("risk_groups")
    if not isinstance(risk_groups, dict):
        raise ValueError(f"Expected 'test_cases' list, 'scenario_groups' mapping, or 'risk_groups' mapping in {path}")

    return flatten_grouped_cases(risk_groups, group_field="risk_type")


def flatten_grouped_cases(groups: dict[str, Any], group_field: str) -> list[dict[str, Any]]:
    """Flatten grouped cases while preserving the group as evaluation metadata."""
    cases: list[dict[str, Any]] = []
    for group_name, grouped_cases in groups.items():
        if isinstance(grouped_cases, dict) and "cases" in grouped_cases:
            grouped_cases = grouped_cases["cases"]
        if not isinstance(grouped_cases, list):
            raise ValueError(f"Expected {group_field} group '{group_name}' to contain a list.")
        for case in grouped_cases:
            if not isinstance(case, dict):
                raise ValueError(f"Expected each case in {group_field} group '{group_name}' to be a mapping.")
            flattened = dict(case)
            flattened.setdefault(group_field, group_name)
            if group_field == "scenario":
                flattened.setdefault("risk_type", group_name)
            cases.append(flattened)
    return cases


def load_step_context(config: dict[str, Any]) -> str:
    """Load the shared procedural step-list artifact when configured."""
    configured = config.get("input_paths", {}).get("step_list")
    if not configured:
        return ""
    path = resolve_configured_path(str(configured))
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def local_timestamp_for_filename() -> str:
    """Return a local timestamp with timezone offset for output filenames."""
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def clip_output_label(dataset_id: str | None) -> str:
    """Return a compact clip label for filenames and report directories."""
    if not dataset_id:
        return "unknown_clip"
    parts = str(dataset_id).split("::")
    mode = parts[-3] if len(parts) >= 3 else "dataset"
    clip = parts[-1] if parts else str(dataset_id)
    mode_labels = {
        "od_plus_psr_error_hints": "od_plus_error_hints",
    }
    clip_labels = {
        "03_assy_0_1": "03_assy_01",
    }
    label = f"{mode_labels.get(mode, mode)}_{clip_labels.get(clip, clip)}"
    return "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in label).strip("_")


def output_paths(config: dict[str, Any], timestamp: str) -> dict[str, Path]:
    """Create run output paths."""
    root = resolve_configured_path(config.get("output_paths", {}).get("root", "outputs"))
    log_root = root / "logs"
    clip_label = clip_output_label(config.get("dataset", {}).get("default_clip_id"))
    report_root = root / "query_reports" / f"{CONDITION}_{clip_label}_{timestamp}"
    root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)
    return {
        "responses": root / f"responses_{CONDITION}_{clip_label}_{timestamp}.jsonl",
        "log": log_root / f"communication_{CONDITION}_{clip_label}_{timestamp}.log",
        "reports": report_root,
    }


def write_log_event(handle: Any, event: str, **fields: Any) -> None:
    """Write and flush one structured event using the filename's local timezone."""
    handle.write(
        json.dumps(
            {"timestamp": datetime.now().astimezone().isoformat(), "event": event, **fields},
            ensure_ascii=False,
        )
        + "\n"
    )
    handle.flush()


def format_duration_hms(seconds: float) -> str:
    """Format elapsed seconds as hours, minutes, and seconds."""
    hours, remainder = divmod(max(0.0, seconds), 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {remaining_seconds:05.2f}s"


def run_experiment(config: dict[str, Any], dry_run: bool = False) -> dict[str, Path]:
    """Run the query-driven graph experiment."""
    test_cases = load_test_cases(config)
    question_set_path = resolve_configured_path(config["input_paths"]["test_cases"])
    question_set_manifest = build_question_set_manifest(question_set_path, len(test_cases))
    step_context = load_step_context(config)
    prompt_path = resolve_configured_path(config["prompt_paths"]["prompts"])
    template_path = resolve_configured_path(config["prompt_paths"]["query_templates"])
    prompts = load_prompt_templates(prompt_path)
    template_config = load_query_template_config(template_path)
    retrieval_config = load_graph_retrieval_config(
        resolve_configured_path(config["graph_retrieval_config"])
    )
    active_config_path = resolve_configured_path(config_path_from_active_run(config))
    llm_metadata = load_lm_metadata(active_config_path)
    graph_name = str(config.get("neo4j", {}).get("graph_name") or "procedural_reasoning_graph")
    row_limit = int(config.get("neo4j", {}).get("row_limit", 25))
    timestamp = local_timestamp_for_filename()
    paths = output_paths(config, timestamp)
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    interaction_durations: list[float] = []
    client = None

    if not dry_run:
        set_config_path(active_config_path)

    try:
        client = client_from_config(config, REPO_ROOT)
        valid_step_ids = client.fetch_step_ids(graph_name)
        graph_manifest = fetch_graph_manifest(client, graph_name)
        print(f"Starting {CONDITION}: {len(test_cases)} graph queries and answer-generation checks")
        print(f"Communication log: {paths['log']}")
        with paths["log"].open("w", encoding="utf-8") as log_handle, paths["responses"].open(
            "w", encoding="utf-8"
        ) as output_handle:
            write_log_event(
                log_handle,
                "run_started",
                condition=CONDITION,
                dry_run=dry_run,
                total_interactions=len(test_cases),
                question_set=question_set_manifest,
                llm=llm_metadata,
                graph_name=graph_name,
                graph_manifest_found=graph_manifest is not None,
                graph_retrieval=retrieval_config,
            )
            for index, test_case in enumerate(test_cases, start=1):
                case_id = str(test_case.get("case_id") or "unknown")
                risk_type = str(test_case.get("risk_type") or "unclassified")
                print(f"[{index}/{len(test_cases)}] {risk_type} | {case_id}: querying graph")
                case_started = time.perf_counter()
                plan = build_query_plan(
                    test_case,
                    template_config,
                    graph_name,
                    row_limit,
                    retrieval_config,
                )
                prompt = None
                write_log_event(
                    log_handle,
                    "query_selected",
                    condition=CONDITION,
                    interaction=index,
                    case_id=case_id,
                    risk_type=risk_type,
                    retrieval_template=plan.retrieval_template,
                )
                try:
                    if plan.params["step_id"] not in valid_step_ids:
                        query_rows = [missing_step_row(plan.params["step_id"], valid_step_ids)]
                        query_status = "missing_step"
                        query_error = None
                        write_log_event(
                            log_handle,
                            "step_id_not_found",
                            condition=CONDITION,
                            interaction=index,
                            case_id=case_id,
                            risk_type=risk_type,
                            step_id=plan.params["step_id"],
                        )
                    else:
                        query_rows = client.run_read_query(plan.cypher, plan.params)
                        query_status = "ok"
                        query_error = None
                except Exception as exc:
                    query_rows = []
                    query_status = "failed"
                    query_error = f"{type(exc).__name__}: {exc}"
                    write_log_event(
                        log_handle,
                        "query_failed",
                        condition=CONDITION,
                        interaction=index,
                        case_id=case_id,
                        risk_type=risk_type,
                        retrieval_template=plan.retrieval_template,
                        error_type=type(exc).__name__,
                    )

                skip_reason = llm_skip_reason(query_status, query_error, query_rows)
                if skip_reason:
                    response = f"LLM call skipped: {skip_reason}"
                    llm_status = "skipped"
                    llm_error = None
                    write_log_event(
                        log_handle,
                        "llm_call_skipped",
                        condition=CONDITION,
                        interaction=index,
                        case_id=case_id,
                        risk_type=risk_type,
                        retrieval_template=plan.retrieval_template,
                        reason=skip_reason,
                    )
                elif dry_run:
                    response = "[dry-run] LLM answer generation skipped."
                    llm_status = "dry_run"
                    llm_error = None
                else:
                    try:
                        prompt = build_answer_prompt(test_case, plan, query_rows, step_context, prompts)
                        response = ask_llm(prompt["system_prompt"], prompt["user_prompt"])
                        llm_status = "ok"
                        llm_error = None
                    except Exception as exc:
                        llm_error = f"{type(exc).__name__}: {exc}"
                        llm_status = "failed"
                        response = f"LLM answer generation failed: {llm_error}"
                        write_log_event(
                            log_handle,
                            "llm_call_failed",
                            condition=CONDITION,
                            interaction=index,
                            case_id=case_id,
                            risk_type=risk_type,
                            retrieval_template=plan.retrieval_template,
                            error_type=type(exc).__name__,
                            error_message=str(exc),
                        )
                        print(
                            f"[{index}/{len(test_cases)}] {case_id}: "
                            f"LLM call failed; continuing with the next question: {llm_error}",
                            file=sys.stderr,
                        )

                duration = time.perf_counter() - case_started
                interaction_durations.append(duration)
                row = {
                    "case_id": test_case.get("case_id"),
                    "condition": CONDITION,
                    "step_id": test_case.get("step_id"),
                    "step_provenance": step_provenance(test_case.get("step_id")),
                    "question": test_case.get("question"),
                    "question_set": question_set_manifest,
                    "llm": llm_metadata,
                    "retrieval_template": plan.retrieval_template,
                    "retrieval_template_description": plan.description,
                    "cypher": plan.cypher,
                    "query_params": plan.params,
                    "graph_retrieval": retrieval_config,
                    "graph_manifest": graph_manifest,
                    "query_status": query_status,
                    "query_error": query_error,
                    "query_rows": query_rows,
                    "prompt": prompt,
                    "response": response,
                    "llm_status": llm_status,
                    "llm_error": llm_error,
                    "scenario": test_case.get("scenario"),
                    "risk_type": test_case.get("risk_type"),
                    "status": test_case.get("status"),
                    "expected_answer_elements": test_case.get("expected_answer_elements"),
                    "duration_seconds": round(duration, 6),
                    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
                rows.append(row)
                output_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                output_handle.flush()
                status_bits = f"query={query_status}, llm={llm_status}"
                if llm_status == "failed":
                    print(f"[{index}/{len(test_cases)}] failed in {duration:.2f}s ({status_bits})")
                elif llm_status in {"skipped", "dry_run"}:
                    print(f"[{index}/{len(test_cases)}] completed in {duration:.2f}s ({status_bits})")
                else:
                    print(f"[{index}/{len(test_cases)}] completed in {duration:.2f}s ({status_bits})")
                write_log_event(
                    log_handle,
                    "interaction_completed",
                    condition=CONDITION,
                    interaction=index,
                    case_id=case_id,
                    risk_type=risk_type,
                    retrieval_template=plan.retrieval_template,
                    query_status=query_status,
                    llm_status=llm_status,
                    duration_seconds=round(duration, 6),
                )

            total_duration = time.perf_counter() - started
            min_seconds = min(interaction_durations) if interaction_durations else None
            max_seconds = max(interaction_durations) if interaction_durations else None
            avg_seconds = (
                sum(interaction_durations) / len(interaction_durations)
                if interaction_durations
                else None
            )
            run_statistics = {
                "completed_interactions": len(rows),
                "failed_interactions": sum(row["llm_status"] == "failed" for row in rows),
                "min_interaction_seconds": round(min_seconds, 6) if min_seconds is not None else None,
                "max_interaction_seconds": round(max_seconds, 6) if max_seconds is not None else None,
                "avg_interaction_seconds": round(avg_seconds, 6) if avg_seconds is not None else None,
                "total_duration_hms": format_duration_hms(total_duration),
            }
            export_query_reports(rows, paths["reports"], run_statistics=run_statistics)
            write_log_event(
                log_handle,
                "run_completed",
                condition=CONDITION,
                completed_interactions=len(rows),
                failed_llm_interactions=run_statistics["failed_interactions"],
                total_interactions=len(test_cases),
                min_interaction_seconds=run_statistics["min_interaction_seconds"],
                max_interaction_seconds=run_statistics["max_interaction_seconds"],
                avg_interaction_seconds=run_statistics["avg_interaction_seconds"],
                total_duration_seconds=round(total_duration, 6),
                total_duration_hms=run_statistics["total_duration_hms"],
                responses_path=str(paths["responses"]),
                query_reports_path=str(paths["reports"]),
            )
            min_label = f"{min_seconds:.2f}s" if min_seconds is not None else "n/a"
            max_label = f"{max_seconds:.2f}s" if max_seconds is not None else "n/a"
            avg_label = f"{avg_seconds:.2f}s" if avg_seconds is not None else "n/a"
            print(f"Completed {CONDITION}: {len(rows)}/{len(test_cases)} interactions")
            print(f"Timing: min={min_label} | max={max_label} | avg={avg_label}")
            print(f"Total time: {format_duration_hms(total_duration)}")
    finally:
        if client is not None:
            client.close()
    return paths


def fetch_graph_manifest(client: Any, graph_name: str) -> dict[str, Any] | None:
    """Return the imported graph manifest for this Neo4j graph, when present."""
    rows = client.run_read_query(
        (
            "MATCH (m:GraphManifest {graph_name: $graph_name}) "
            "RETURN properties(m) AS manifest "
            "LIMIT 1"
        ),
        {"graph_name": graph_name},
    )
    if not rows:
        return None
    manifest = rows[0].get("manifest")
    return manifest if isinstance(manifest, dict) else None


def llm_skip_reason(query_status: str, query_error: str | None, query_rows: list[dict[str, Any]]) -> str | None:
    """Return the reason an LLM call should be skipped, if any."""
    if query_error:
        return f"Neo4j query failed before answer generation: {query_error}"
    if query_status == "failed":
        return "Neo4j query failed before answer generation."
    if query_status == "missing_step":
        return None
    if not query_rows:
        return "Neo4j query returned 0 rows for an existing step, so no grounded evidence was available."
    return None


def missing_step_row(step_id: str, valid_step_ids: set[str]) -> dict[str, Any]:
    """Build an explicit evidence row for a test case whose step is not in Neo4j."""
    return {
        "requested_step_id": step_id,
        "current_step_found": False,
        "available_step_count": len(valid_step_ids),
        "nearest_step_ids": nearest_step_ids(step_id, valid_step_ids),
        "diagnostic": "The requested step_id is not present in the imported procedural reasoning graph.",
    }


def nearest_step_ids(step_id: str, valid_step_ids: set[str], radius: int = 2) -> list[str]:
    """Return nearby event ids when the missing step has a numeric suffix."""
    prefix, separator, suffix = step_id.rpartition("event_")
    if not separator or not suffix.isdigit():
        return sorted(valid_step_ids)[: min(5, len(valid_step_ids))]

    center = int(suffix)
    candidates = []
    for event_index in range(max(0, center - radius), center + radius + 1):
        candidate = canonical_step_id(f"{prefix}{separator}{event_index}")
        if candidate in valid_step_ids:
            candidates.append(candidate)
    return candidates


def config_path_from_active_run(config: dict[str, Any]) -> str:
    """Return the path stashed by main for lm_client compatibility."""
    return str(config.get("_config_path") or EXPERIMENT_ROOT / "configs" / "config_query_driven_graph.yaml")


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    try:
        config = load_config(args.config)
        config["_config_path"] = str(Path(args.config))
        paths = run_experiment(config, dry_run=args.dry_run)
    except Exception as exc:
        print(f"Error: query-driven graph experiment failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Wrote responses to {paths['responses']}")
    print(f"Wrote communication log to {paths['log']}")
    print(f"Wrote query reports to {paths['reports']}")


if __name__ == "__main__":
    main()
