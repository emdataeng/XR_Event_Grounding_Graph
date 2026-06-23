"""Build final answer prompts from query-driven graph evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def load_prompt_templates(path: str | Path) -> dict[str, Any]:
    """Load query-driven prompt templates."""
    prompt_path = Path(path)
    if not prompt_path.exists():
        raise FileNotFoundError(f"prompts_query_driven_graph.yaml is missing: {prompt_path}")
    with prompt_path.open("r", encoding="utf-8") as handle:
        prompts = yaml.safe_load(handle) or {}
    if not isinstance(prompts, dict):
        raise ValueError(f"Expected prompt config to be a mapping: {prompt_path}")
    return prompts


def build_answer_prompt(
    test_case: dict[str, Any],
    query_plan: Any,
    query_rows: list[dict[str, Any]],
    step_context: str,
    prompts: dict[str, Any],
) -> dict[str, str]:
    """Build the answer-generation LLM messages."""
    answer_prompts = prompts.get("answer_generation")
    if not isinstance(answer_prompts, dict):
        raise ValueError("Prompt config missing answer_generation section.")

    system_key = "system_with_evidence" if query_rows else "system_missing_evidence"
    system_prompt = str(answer_prompts[system_key])
    user_template = str(answer_prompts["user_template"])
    user_prompt = user_template.format_map(
        {
            "step_id": str(test_case.get("step_id") or ""),
            "question": str(test_case.get("question") or ""),
            "intent": query_plan.intent,
            "cypher": query_plan.cypher,
            "query_result": json.dumps(query_rows, indent=2, ensure_ascii=False, sort_keys=True),
            "step_context": step_context,
        }
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}

