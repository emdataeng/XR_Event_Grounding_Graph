"""Prompt context builders for the LLM guidance ablation conditions."""

from __future__ import annotations

from enum import Enum
from typing import Any


class PromptCondition(str, Enum):
    """Supported experiment prompting conditions."""

    STEPS_ONLY = "steps_only"
    RAW_DOMAIN = "raw_domain"
    GRAPH_GROUNDED = "graph_grounded"


def build_steps_only_context(test_case: dict[str, Any], artifacts: dict[str, Any]) -> list[dict[str, str]]:
    """Build prompt messages using only generated procedural step context."""
    raise NotImplementedError("steps_only context construction is not implemented yet.")


def build_raw_domain_context(test_case: dict[str, Any], artifacts: dict[str, Any]) -> list[dict[str, str]]:
    """Build prompt messages using generated steps and raw domain artifacts."""
    raise NotImplementedError("raw_domain context construction is not implemented yet.")


def build_graph_grounded_context(test_case: dict[str, Any], artifacts: dict[str, Any]) -> list[dict[str, str]]:
    """Build prompt messages using generated steps and procedural graph context."""
    raise NotImplementedError("graph_grounded context construction is not implemented yet.")


def build_context(
    condition: PromptCondition,
    test_case: dict[str, Any],
    artifacts: dict[str, Any],
) -> list[dict[str, str]]:
    """Dispatch to the context builder for the selected ablation condition."""
    builders = {
        PromptCondition.STEPS_ONLY: build_steps_only_context,
        PromptCondition.RAW_DOMAIN: build_raw_domain_context,
        PromptCondition.GRAPH_GROUNDED: build_graph_grounded_context,
    }
    return builders[condition](test_case, artifacts)
