"""Deterministic retrieval-template selection and Cypher rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from query_validator import validate_read_only_cypher


@dataclass(frozen=True)
class QueryPlan:
    """A selected read-only graph query for one novice question."""

    retrieval_template: str
    description: str
    cypher: str
    params: dict[str, Any]


def load_query_template_config(path: str | Path) -> dict[str, Any]:
    """Load query template configuration from YAML."""
    template_path = Path(path)
    if not template_path.exists():
        raise FileNotFoundError(f"query_templates.yaml is missing: {template_path}")
    with template_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError(f"Expected query template config to be a mapping: {template_path}")
    return config


def build_query_plan(
    test_case: dict[str, Any],
    template_config: dict[str, Any],
    graph_name: str,
    row_limit: int,
    retrieval_config: dict[str, int],
) -> QueryPlan:
    """Select a deterministic query template and bind safe parameters."""
    retrieval_template = select_retrieval_template(test_case, template_config)
    templates = template_config.get("templates")
    if not isinstance(templates, dict) or retrieval_template not in templates:
        raise ValueError(f"Query template is missing for retrieval template: {retrieval_template}")

    template = templates[retrieval_template]
    if not isinstance(template, dict):
        raise ValueError(f"Expected query template to be a mapping for retrieval template: {retrieval_template}")
    cypher_template = str(template.get("cypher") or "").strip()
    cypher = (
        cypher_template.replace("{step_hops}", str(int(retrieval_config["step_hops"])))
        .replace("{evidence_hops}", str(int(retrieval_config["evidence_hops"])))
    )
    validate_read_only_cypher(cypher)

    step_id = str(test_case.get("step_id") or "").strip()
    if not step_id:
        raise ValueError("Test case is missing required field: step_id")

    return QueryPlan(
        retrieval_template=retrieval_template,
        description=str(template.get("description") or ""),
        cypher=cypher,
        params={
            "graph_name": graph_name,
            "step_id": canonical_step_id(step_id),
            "limit": int(row_limit),
        },
    )


def select_retrieval_template(test_case: dict[str, Any], template_config: dict[str, Any]) -> str:
    """Select a retrieval template from the test-case scenario."""
    scenario = str(test_case.get("scenario") or "")
    template_by_scenario = template_config.get("retrieval_template_by_scenario") or {}
    if isinstance(template_by_scenario, dict) and scenario in template_by_scenario:
        return str(template_by_scenario[scenario])
    return str(template_config.get("default_retrieval_template") or "current_step_context")


def canonical_step_id(value: Any) -> str:
    """Normalize test-case step ids to graph Step.step_id values."""
    text = str(value or "").strip()
    prefix, separator, suffix = text.rpartition("event_")
    if separator and suffix.isdigit():
        text = f"{prefix}{separator}{int(suffix)}"
    if not text.startswith("step::"):
        text = f"step::{text}"
    return text
