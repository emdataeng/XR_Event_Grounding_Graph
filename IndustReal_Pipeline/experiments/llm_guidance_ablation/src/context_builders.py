"""Prompt context builders for the LLM guidance ablation conditions."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from graph_loader import extract_step_subgraph, serialize_graph_evidence


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
    step_context = _step_list_artifact(artifacts)
    has_step_context = bool(step_context)
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
    """Build prompts using the frozen step list, predicates, and rules."""
    artifacts = artifacts or {}
    step_id = str(test_case.get("step_id", "")).strip()
    question = str(test_case.get("question", "")).strip()
    if not step_id:
        raise ValueError("Test case is missing required field: step_id")
    if not question:
        raise ValueError("Test case is missing required field: question")

    predicates = predicate_context_for_step(step_id, artifacts)
    thesis_rules = _required_text_artifact(artifacts, "thesis_rules")
    step_context = _step_list_artifact(artifacts)
    has_step_context = bool(step_context)
    prompts = _condition_prompts(artifacts, "symbolic_domain")
    system_prompt = prompts["system_with_context"] if has_step_context else prompts["system_missing_context"]
    user_prompt = _render_template(
        prompts["user_template"],
        step_id=step_id,
        step_context=step_context,
        predicates=predicates,
        thesis_rules=thesis_rules,
        question=question,
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def build_graph_grounded_context(test_case: dict[str, Any], artifacts: dict[str, Any] | None = None) -> dict[str, str]:
    """Build prompts using generated steps plus local procedural graph evidence."""
    artifacts = artifacts or {}
    step_id = str(test_case.get("step_id", "")).strip()
    question = str(test_case.get("question", "")).strip()
    if not step_id:
        raise ValueError("Test case is missing required field: step_id")
    if not question:
        raise ValueError("Test case is missing required field: question")

    graph_evidence = graph_evidence_for_step(step_id, artifacts)
    step_context = _step_list_artifact(artifacts)
    prompts = _condition_prompts(artifacts, "graph_grounded")
    system_prompt = prompts["system_with_context"] if step_context else prompts["system_missing_context"]
    user_prompt = _render_template(
        prompts["user_template"],
        step_id=step_id,
        step_context=step_context,
        graph_evidence=graph_evidence,
        question=question,
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def graph_evidence_for_step(step_id: str, artifacts: dict[str, Any]) -> str:
    """Extract and serialize the exact graph evidence inserted into a prompt."""
    graph = artifacts.get("procedural_reasoning_graph")
    if not isinstance(graph, dict):
        raise ValueError("Required prompt artifact was not loaded: procedural_reasoning_graph")
    step_hops = int(artifacts.get("step_hops", 1))
    evidence_hops = int(artifacts.get("evidence_hops", 2))
    subgraph = extract_step_subgraph(graph, step_id, step_hops, evidence_hops)
    return (
        f"Retrieval policy: step_hops={step_hops}, evidence_hops={evidence_hops}\n"
        + serialize_graph_evidence(subgraph, current_step_id=step_id)
    )


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


def _required_text_artifact(artifacts: dict[str, Any], name: str) -> str:
    """Return a required raw-text artifact without parsing or rewriting it."""
    value = artifacts.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Required prompt artifact was not loaded: {name}")
    return value


def _step_list_artifact(artifacts: dict[str, Any]) -> str:
    """Return the frozen step-list artifact shared by prompt conditions."""
    value = artifacts.get("step_list")
    if isinstance(value, str) and value.strip():
        return value
    return ""


def predicate_context_for_step(step_id: str, artifacts: dict[str, Any]) -> str:
    """Render the precomputed predicate window for one test-case step."""
    artifact = artifacts.get("predicate_contexts")
    if not isinstance(artifact, dict):
        raise ValueError("Required prompt artifact was not loaded: predicate_contexts")

    expected_hops = artifacts.get("step_hops")
    artifact_hops = artifact.get("step_hops")
    if artifact_hops != expected_hops:
        raise ValueError(
            "Predicate context hop mismatch: "
            f"artifact uses {artifact_hops}, config requests {expected_hops}. Regenerate the artifact."
        )

    contexts = artifact.get("contexts")
    context = contexts.get(canonical_step_id(step_id)) if isinstance(contexts, dict) else None
    if not isinstance(context, dict):
        return f"No predicate context was found for current step id: {step_id}"

    included_step_ids = context.get("included_step_ids") or []
    predicate_lines = context.get("predicate_lines") or []
    return (
        "Predicate context window:\n"
        f"- center_step_id: {context.get('center_step_id')}\n"
        f"- step_hops: {artifact_hops}\n"
        f"- included_step_ids: {json.dumps(included_step_ids, ensure_ascii=False)}\n\n"
        "Selected predicates:\n"
        + "\n".join(str(line) for line in predicate_lines)
    )


def render_step_list(records: list[Any]) -> str:
    """Render Layer 3 input step records as an ordered, prompt-safe step list.

    For IndustReal, the reasoning adapter derives these records from Layer 2
    output before Layer 3 inference consumes them.
    """
    steps = [_normalize_step_record(record) for record in records if isinstance(record, dict)]
    steps = [step for step in steps if step["step_id"]]
    steps.sort(key=lambda step: step["index"] if step["index"] is not None else 10**9)

    if not steps:
        return "No generated step artifact was found for this step id."

    lines = ["Available assembly steps:"]
    for step in steps:
        lines.append(
            f"- Step {step['index']}: {step['action_description']}\n"
            f"  - step_id: {step['step_id']}\n"
            f"  - acted_on_object: {step['acted_on_object']}\n"
            f"  - previous_step_id: {step['previous_step_id']}\n"
            f"  - next_step_id: {step['next_step_id']}\n"
            f"  - time_window: start_frame={step['start_frame']}, end_frame={step['end_frame']}\n"
            f"  - confidence: {step['confidence']}"
        )

    return "\n".join(lines)


def _normalize_step_record(record: dict[str, Any]) -> dict[str, Any]:
    """Extract prompt-safe fields from one Layer 3 input step record."""
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
    return canonical_step_id(left) == canonical_step_id(right)


def canonical_step_id(value: Any) -> str:
    """Normalize event suffixes such as event_001 and event_1."""
    text = str(value or "")
    if text.startswith("step::"):
        text = text[len("step::") :]
    prefix, separator, suffix = text.rpartition("event_")
    if not separator or not suffix.isdigit():
        return text
    return f"{prefix}{separator}{int(suffix)}"


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
