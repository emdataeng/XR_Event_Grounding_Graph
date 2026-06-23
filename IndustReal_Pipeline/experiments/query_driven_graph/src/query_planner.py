"""Deterministic intent selection and Cypher template rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from query_validator import validate_read_only_cypher


@dataclass(frozen=True)
class QueryPlan:
    """A selected read-only graph query for one novice question."""

    intent: str
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
) -> QueryPlan:
    """Select a deterministic query template and bind safe parameters."""
    intent = select_intent(test_case, template_config)
    templates = template_config.get("templates")
    if not isinstance(templates, dict) or intent not in templates:
        raise ValueError(f"Query template is missing for intent: {intent}")

    template = templates[intent]
    if not isinstance(template, dict):
        raise ValueError(f"Expected query template to be a mapping for intent: {intent}")
    cypher = str(template.get("cypher") or "").strip()
    validate_read_only_cypher(cypher)

    step_id = str(test_case.get("step_id") or "").strip()
    if not step_id:
        raise ValueError("Test case is missing required field: step_id")

    return QueryPlan(
        intent=intent,
        description=str(template.get("description") or ""),
        cypher=cypher,
        params={
            "graph_name": graph_name,
            "step_id": canonical_step_id(step_id),
            "limit": int(row_limit),
        },
    )


def select_intent(test_case: dict[str, Any], template_config: dict[str, Any]) -> str:
    """Select an intent from risk type with a few question-keyword overrides."""
    question = str(test_case.get("question") or "").lower()
    if any(term in question for term in ("tool", "screwdriver", "force")):
        return "tool_context"
    if any(term in question for term in ("confidence", "certain", "video", "evidence")):
        return "evidence_confidence"
    if any(term in question for term in ("remove", "removed", "rework", "take it off")):
        return "removal_or_rework_check"
    if any(term in question for term in ("next", "previous", "before continuing", "move on")):
        return "sequence_context"

    risk_type = str(test_case.get("risk_type") or "")
    intent_by_risk_type = template_config.get("intent_by_risk_type") or {}
    if isinstance(intent_by_risk_type, dict) and risk_type in intent_by_risk_type:
        return str(intent_by_risk_type[risk_type])

    if any(term in question for term in ("component", "part", "label", "assembly", "chassis")):
        return "component_check"
    if any(term in question for term in ("install", "seated", "target", "oriented", "alignment")):
        return "installation_check"
    return str(template_config.get("default_intent") or "current_step_context")


def canonical_step_id(value: Any) -> str:
    """Normalize test-case step ids to graph Step.step_id values."""
    text = str(value or "").strip()
    prefix, separator, suffix = text.rpartition("event_")
    if separator and suffix.isdigit():
        text = f"{prefix}{separator}{int(suffix)}"
    if not text.startswith("step::"):
        text = f"step::{text}"
    return text
