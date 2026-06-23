"""Preflight template-based Neo4j retrieval before running LLM calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

CURRENT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = CURRENT_DIR.parents[0]
REPO_ROOT = CURRENT_DIR.parents[2]
sys.path.insert(0, str(CURRENT_DIR))

from neo4j_client import client_from_config  # noqa: E402
from query_planner import build_query_plan, load_query_template_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(EXPERIMENT_ROOT / "configs" / "config_query_driven_graph.yaml"),
    )
    parser.add_argument("--fail-on-empty", action="store_true")
    return parser.parse_args()


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError(f"Expected config mapping: {config_path}")
    return config


def load_test_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    risk_groups = data.get("risk_groups")
    if not isinstance(risk_groups, dict):
        raise ValueError(f"Expected risk_groups in {path}")

    cases = []
    for risk_type, grouped_cases in risk_groups.items():
        for case in grouped_cases or []:
            flattened = dict(case)
            flattened.setdefault("risk_type", risk_type)
            cases.append(flattened)
    return cases


def resolve_configured_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    for base in (Path.cwd(), REPO_ROOT, EXPERIMENT_ROOT):
        candidate = base / path
        if candidate.exists():
            return candidate
    return REPO_ROOT / path


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    template_config = load_query_template_config(resolve_configured_path(config["prompt_paths"]["query_templates"]))
    test_cases = load_test_cases(resolve_configured_path(config["input_paths"]["test_cases"]))
    graph_name = str(config.get("neo4j", {}).get("graph_name") or "procedural_reasoning_graph")
    row_limit = int(config.get("neo4j", {}).get("row_limit", 25))

    client = client_from_config(config, REPO_ROOT)
    failures = []
    try:
        total_probe = client.run_read_query(
            "MATCH (n) RETURN count(n) AS node_count LIMIT 1",
            {},
        )
        graph_name_probe = client.run_read_query(
            "MATCH (n) WHERE n.graph_name IS NOT NULL RETURN n.graph_name AS graph_name, count(n) AS count ORDER BY count DESC LIMIT 20",
            {},
        )
        print("Database probe:")
        print(json.dumps(total_probe, indent=2, ensure_ascii=False, sort_keys=True))
        print("Available graph_name values:")
        print(json.dumps(graph_name_probe, indent=2, ensure_ascii=False, sort_keys=True))

        graph_probe = client.run_read_query(
            "MATCH (n {graph_name: $graph_name}) RETURN labels(n) AS labels, count(*) AS count LIMIT 10",
            {"graph_name": graph_name},
        )
        print(f"Configured graph probe ({graph_name}):")
        print(json.dumps(graph_probe, indent=2, ensure_ascii=False, sort_keys=True))
        if total_probe and total_probe[0].get("node_count") == 0:
            failures.append("Neo4j database is empty. Import the procedural graph before running the experiment.")
        if not graph_probe:
            failures.append("No nodes found for configured graph_name.")

        valid_step_ids = client.fetch_step_ids(graph_name)
        print(f"Valid Step.step_id count for configured graph: {len(valid_step_ids)}")
        if valid_step_ids:
            print("First valid step ids:")
            print(json.dumps(sorted(valid_step_ids)[:5], indent=2, ensure_ascii=False))

        for index, test_case in enumerate(test_cases, start=1):
            plan = build_query_plan(test_case, template_config, graph_name, row_limit)
            case_id = str(test_case.get("case_id") or "unknown")
            if plan.params["step_id"] not in valid_step_ids:
                print(
                    f"[{index:02d}] {case_id} | intent={plan.intent} | rows=diagnostic | "
                    f"missing_step_id={plan.params['step_id']}"
                )
                continue

            rows = client.run_read_query(plan.cypher, plan.params)
            print(f"[{index:02d}] {case_id} | intent={plan.intent} | rows={len(rows)} | step_id={plan.params['step_id']}")
            if not rows:
                failures.append(f"{case_id}: empty rows for intent={plan.intent}, step_id={plan.params['step_id']}")
    finally:
        client.close()

    if failures:
        print("\nPreflight failures:")
        for failure in failures:
            print(f"- {failure}")
        if args.fail_on_empty:
            raise SystemExit(1)
    else:
        print("\nPreflight passed: every test case returned at least one query row.")


if __name__ == "__main__":
    main()
