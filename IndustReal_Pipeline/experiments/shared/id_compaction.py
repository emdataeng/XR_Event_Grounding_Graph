"""Compact upstream IndustReal identifiers at the LLM prompt boundary."""

from __future__ import annotations

import re
from typing import Any


_STEP_PREFIXES = ("Step::step::", "Step::", "step::")


def parse_step_id(value: Any) -> dict[str, Any]:
    """Decompose an upstream step id into provenance fields."""
    text = str(value or "").strip()
    for prefix in _STEP_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break

    parts = text.split("::")
    if len(parts) != 5 or not parts[-1].startswith("event_"):
        raise ValueError(f"Unsupported IndustReal step id: {value}")
    event_suffix = parts[-1][len("event_") :]
    if not event_suffix.isdigit():
        raise ValueError(f"Step id has a non-numeric event suffix: {value}")

    return {
        "run_id": parts[0],
        "evidence_mode": parts[1],
        "archive": parts[2],
        "clip_id": parts[3],
        "step_index": int(event_suffix),
        "clip_result_id": "::".join(parts[:4]),
    }


def step_provenance(value: Any) -> dict[str, Any] | None:
    """Return parsed provenance when the value is an upstream IndustReal id."""
    try:
        return parse_step_id(value)
    except ValueError:
        return None


def compact_step_id(value: Any) -> str:
    """Return the prompt alias for an upstream step id."""
    provenance = step_provenance(value)
    if provenance is None:
        return str(value or "").strip()
    return f"step_{provenance['step_index']}"


def compact_prompt_text(value: Any, reference_step_id: Any) -> str:
    """Replace same-clip upstream event ids with compact prompt aliases."""
    text = str(value or "")
    try:
        clip_result_id = str(parse_step_id(reference_step_id)["clip_result_id"])
    except ValueError:
        return text

    event_pattern = re.compile(
        rf"(?:(?:Step::)?step::|Step::)?{re.escape(clip_result_id)}::event_(\d+)"
    )
    return event_pattern.sub(lambda match: f"step_{int(match.group(1))}", text)


def compact_prompt_value(value: Any, reference_step_id: Any) -> Any:
    """Recursively compact same-clip identifiers in prompt-bound data."""
    if isinstance(value, str):
        return compact_prompt_text(value, reference_step_id)
    if isinstance(value, list):
        return [compact_prompt_value(item, reference_step_id) for item in value]
    if isinstance(value, tuple):
        return tuple(compact_prompt_value(item, reference_step_id) for item in value)
    if isinstance(value, dict):
        return {
            key: compact_prompt_value(item, reference_step_id)
            for key, item in value.items()
        }
    return value
