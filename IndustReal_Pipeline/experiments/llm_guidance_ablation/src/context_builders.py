"""Prompt context builders for the LLM guidance ablation conditions."""

from __future__ import annotations

from enum import Enum
from typing import Any


class PromptCondition(str, Enum):
    """Supported experiment prompting conditions."""

    STEPS_ONLY = "steps_only"
    SYMBOLIC_DOMAIN = "symbolic_domain"
    GRAPH_GROUNDED = "graph_grounded"


def build_steps_only_context(test_case: dict[str, Any], artifacts: dict[str, Any] | None = None) -> dict[str, str]:
    """Build prompts using only generated procedural step context.

    Evaluation-only fields such as ``risk_type`` and
    ``expected_answer_elements`` are intentionally not read here.
    """
    artifacts = artifacts or {}
    step_id = str(test_case.get("step_id", "")).strip()
    question = str(test_case.get("question", "")).strip()
    step_context = _lookup_generated_step(step_id, artifacts)
    has_step_context = _has_generated_step(step_id, artifacts)
    prompts = _condition_prompts(artifacts, "steps_only")

    if not step_id:
        raise ValueError("Test case is missing required field: step_id")
    if not question:
        raise ValueError("Test case is missing required field: question")

    system_prompt = prompts["system_with_context"] if has_step_context else prompts["system_missing_context"]
    user_prompt = _render_template(
        prompts["user_template"],
        step_id=step_id,
        step_context=step_context,
        question=question,
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def build_symbolic_domain_context(test_case: dict[str, Any], artifacts: dict[str, Any] | None = None) -> dict[str, str]:
    """Build prompts using generated steps plus symbolic domain artifacts.

    Placeholder for the next milestone. It currently returns a minimal prompt
    with a clear marker that symbolic domain grounding has not been implemented.
    """
    base_context = build_steps_only_context(test_case, artifacts)
    prompts = _condition_prompts(artifacts or {}, "symbolic_domain")
    base_context["user_prompt"] += prompts["user_suffix_placeholder"]
    return base_context


def build_graph_grounded_context(test_case: dict[str, Any], artifacts: dict[str, Any] | None = None) -> dict[str, str]:
    """Build prompts using generated steps plus procedural graph context.

    Placeholder for the next milestone. It currently returns a minimal prompt
    with a clear marker that graph grounding has not been implemented.
    """
    base_context = build_steps_only_context(test_case, artifacts)
    prompts = _condition_prompts(artifacts or {}, "graph_grounded")
    base_context["user_prompt"] += prompts["user_suffix_placeholder"]
    return base_context


def build_context(
    condition: PromptCondition,
    test_case: dict[str, Any],
    artifacts: dict[str, Any],
) -> dict[str, str]:
    """Dispatch to the context builder for the selected ablation condition."""
    builders = {
        PromptCondition.STEPS_ONLY: build_steps_only_context,
        PromptCondition.SYMBOLIC_DOMAIN: build_symbolic_domain_context,
        PromptCondition.GRAPH_GROUNDED: build_graph_grounded_context,
    }
    return builders[condition](test_case, artifacts)


def _lookup_generated_step(step_id: str, artifacts: dict[str, Any]) -> str:
    """Find generated step text in optional artifacts."""
    generated_steps = artifacts.get("generated_steps")
    if isinstance(generated_steps, dict):
        value = generated_steps.get(step_id)
        return _format_step_value(value)

    if isinstance(generated_steps, list):
        return _format_step_records(generated_steps, step_id)

    return "No generated step artifact was found for this step id."


def _has_generated_step(step_id: str, artifacts: dict[str, Any]) -> bool:
    """Return whether a prompt-safe generated step exists for this step id."""
    generated_steps = artifacts.get("generated_steps")
    if isinstance(generated_steps, dict):
        return bool(generated_steps.get(step_id))

    if isinstance(generated_steps, list):
        for item in generated_steps:
            if not isinstance(item, dict):
                continue
            item_id = item.get("step_id") or item.get("id")
            if _same_step_id(item_id, step_id):
                return True

    return False


def _format_step_records(records: list[Any], current_step_id: str) -> str:
    """Render Layer 3 step records as an ordered, prompt-safe step list."""
    steps = [_normalize_step_record(record) for record in records if isinstance(record, dict)]
    steps = [step for step in steps if step["step_id"]]
    steps.sort(key=lambda step: step["index"] if step["index"] is not None else 10**9)

    if not steps:
        return "No generated step artifact was found for this step id."

    lines = ["Available assembly steps:"]
    for step in steps:
        current_marker = " [CURRENT]" if _same_step_id(step["step_id"], current_step_id) else ""
        lines.append(
            f"- Step {step['index']}: {step['action_description']}{current_marker}\n"
            f"  - step_id: {step['step_id']}\n"
            f"  - acted_on_object: {step['acted_on_object']}\n"
            f"  - previous_step_id: {step['previous_step_id']}\n"
            f"  - next_step_id: {step['next_step_id']}\n"
            f"  - time_window: start_frame={step['start_frame']}, end_frame={step['end_frame']}\n"
            f"  - confidence: {step['confidence']}"
        )

    if not any(_same_step_id(step["step_id"], current_step_id) for step in steps):
        lines.append("")
        lines.append("Current step warning: the requested step id was not found in the generated step records.")

    return "\n".join(lines)


def _normalize_step_record(record: dict[str, Any]) -> dict[str, Any]:
    """Extract the prompt-safe fields from one Layer 3 step record."""
    action = record.get("action") if isinstance(record.get("action"), dict) else {}
    sequence = record.get("sequence") if isinstance(record.get("sequence"), dict) else {}
    time_window = record.get("time_window") if isinstance(record.get("time_window"), dict) else {}
    return {
        "index": record.get("index"),
        "step_id": record.get("id") or record.get("step_id"),
        "action_description": action.get("description") or record.get("description") or "unknown action",
        "acted_on_object": _format_acted_on_objects(record.get("objects")),
        "previous_step_id": sequence.get("previous_event_id") or "none",
        "next_step_id": sequence.get("next_event_id") or "none",
        "start_frame": time_window.get("start_frame"),
        "end_frame": time_window.get("end_frame"),
        "confidence": record.get("confidence"),
    }


def _format_acted_on_objects(objects: Any) -> str:
    """Render acted-on objects/components from a step record."""
    if not isinstance(objects, list) or not objects:
        return "none"

    labels = []
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        label = obj.get("label") or obj.get("id") or obj.get("type")
        if label:
            labels.append(str(label))
    return ", ".join(labels) if labels else "none"


def _same_step_id(left: Any, right: Any) -> bool:
    """Compare step ids while tolerating zero-padded event ids."""
    return _canonical_step_id(left) == _canonical_step_id(right)


def _canonical_step_id(value: Any) -> str:
    """Normalize event suffixes such as event_001 and event_1."""
    text = str(value or "")
    if text.startswith("step::"):
        text = text[len("step::") :]
    prefix, separator, suffix = text.rpartition("event_")
    if not separator or not suffix.isdigit():
        return text
    return f"{prefix}{separator}{int(suffix)}"


def _format_step_value(value: Any) -> str:
    """Convert a generated-step value into prompt text."""
    if value is None:
        return "No generated step artifact was found for this step id."
    if isinstance(value, str):
        return value.strip() or "Generated step artifact is empty."
    if isinstance(value, dict):
        for key in ("text", "description", "instruction", "action", "step_text"):
            if value.get(key):
                return str(value[key]).strip()
        return str(value)
    return str(value)


def _condition_prompts(artifacts: dict[str, Any], condition_name: str) -> dict[str, str]:
    """Return prompt templates for one condition from loaded config."""
    all_prompts = artifacts.get("prompt_templates")
    if not isinstance(all_prompts, dict):
        raise ValueError("Prompt templates were not loaded. Check prompt_paths.prompts in config.")

    condition_prompts = all_prompts.get(condition_name)
    if not isinstance(condition_prompts, dict):
        raise ValueError(f"Prompt templates missing section: {condition_name}")
    return condition_prompts


def _render_template(template: str, **values: Any) -> str:
    """Render a prompt template using named fields."""
    return template.format_map({key: str(value) for key, value in values.items()})
