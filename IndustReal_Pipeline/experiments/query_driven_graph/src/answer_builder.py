"""Build final answer prompts from query-driven graph evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

SHARED_EXPERIMENTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SHARED_EXPERIMENTS_DIR))

from shared.id_compaction import compact_prompt_text, compact_prompt_value, compact_step_id  # noqa: E402


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
    system_prompt = _compose_system_prompt(
        str(prompts.get("shared_system_prompt") or ""),
        str(answer_prompts[system_key]),
    )
    user_template = str(answer_prompts["user_template"])
    source_step_id = str(test_case.get("step_id") or "")
    compact_query_rows = compact_prompt_value(query_rows, source_step_id)
    user_prompt = user_template.format_map(
        {
            "step_id": compact_step_id(source_step_id),
            "question": str(test_case.get("question") or ""),
            "retrieval_template": query_plan.retrieval_template,
            "cypher": query_plan.cypher,
            "query_result": json.dumps(compact_query_rows, indent=2, ensure_ascii=False, sort_keys=True),
            "step_context": compact_prompt_text(step_context, source_step_id),
        }
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def _compose_system_prompt(shared_prompt: str, specific_prompt: str) -> str:
    """Compose shared answer behavior with the experiment-specific evidence rule."""
    return "\n\n".join(part.strip() for part in (shared_prompt, specific_prompt) if part.strip())
