"""Build CAD-grounded goal and phase hierarchy rows for IndustReal graphs."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_FINAL_STATE_INDEX = 22
DEFAULT_GOAL_NAME = "Reach final CAD assembly state"


@dataclass(frozen=True)
class CadGoal:
    goal_name: str
    target_state_index: int
    target_state_name: str
    target_state_kind: str
    target_state_asset: str
    target_component_keys: list[str]
    target_components: list[str]


@dataclass(frozen=True)
class PhaseRule:
    key: str
    name: str
    configured_order: int
    normalized_components: set[str]


@dataclass(frozen=True)
class PhaseRules:
    phases: list[PhaseRule]
    by_key: dict[str, PhaseRule]
    component_to_phase_key: dict[str, str]
    event_type_overrides: dict[str, str]
    default_phase_key: str


def normalize_name(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")
    return cleaned or "unknown"


def make_goal_id(clip_result_id: str) -> str:
    return f"{clip_result_id}::goal"


def make_phase_id(clip_result_id: str, phase_key: str) -> str:
    return f"{clip_result_id}::phase_{normalize_name(phase_key)}"


def load_cad_goal(
    cad_state_catalog_path: Path,
    *,
    cad_part_catalog_path: Path | None = None,
    final_state_index: int = DEFAULT_FINAL_STATE_INDEX,
    goal_name: str = DEFAULT_GOAL_NAME,
) -> CadGoal:
    """Load the final CAD state that defines the top-level assembly goal."""
    state_catalog = _load_json(cad_state_catalog_path)
    state = next(
        (item for item in state_catalog.get("states", []) if int(item.get("state_index", -1)) == final_state_index),
        None,
    )
    if state is None:
        raise ValueError(f"CAD state catalog has no state_index={final_state_index}: {cad_state_catalog_path}")

    component_keys = [str(key) for key in state.get("component_keys", [])]
    display_by_key = _component_display_lookup(cad_part_catalog_path)
    target_components = [display_by_key.get(key, key) for key in component_keys]

    return CadGoal(
        goal_name=goal_name,
        target_state_index=final_state_index,
        target_state_name=str(state.get("state_name") or ""),
        target_state_kind=str(state.get("kind") or ""),
        target_state_asset=str(state.get("state_asset_member") or ""),
        target_component_keys=component_keys,
        target_components=target_components,
    )


def load_phase_rules(path: Path) -> PhaseRules:
    data = _load_json(path)
    phases: list[PhaseRule] = []
    component_to_phase_key: dict[str, str] = {}
    for raw_phase in data.get("phases", []):
        key = str(raw_phase["key"])
        phase = PhaseRule(
            key=key,
            name=str(raw_phase["name"]),
            configured_order=int(raw_phase.get("configured_order", 0)),
            normalized_components={normalize_name(name) for name in raw_phase.get("components", [])},
        )
        phases.append(phase)
        for component in phase.normalized_components:
            component_to_phase_key[component] = key

    by_key = {phase.key: phase for phase in phases}
    event_type_overrides = {
        str(event_type).upper(): str(phase_key)
        for event_type, phase_key in data.get("event_type_overrides", {}).items()
    }
    default_phase_key = str(data.get("default_phase_key") or "other")
    if default_phase_key not in by_key:
        raise ValueError(f"default_phase_key={default_phase_key!r} is not present in phase rules: {path}")

    return PhaseRules(
        phases=sorted(phases, key=lambda phase: (phase.configured_order, phase.name)),
        by_key=by_key,
        component_to_phase_key=component_to_phase_key,
        event_type_overrides=event_type_overrides,
        default_phase_key=default_phase_key,
    )


def assign_event_phase(event: dict[str, Any], phase_rules: PhaseRules) -> PhaseRule:
    event_type = str(event.get("event_type") or "").upper()
    phase_key = phase_rules.event_type_overrides.get(event_type)
    if phase_key is None:
        component = normalize_name(str(event.get("component") or ""))
        phase_key = phase_rules.component_to_phase_key.get(component, phase_rules.default_phase_key)
    return phase_rules.by_key.get(phase_key, phase_rules.by_key[phase_rules.default_phase_key])


def summarize_event_phases(events: list[dict[str, Any]], phase_rules: PhaseRules) -> list[dict[str, Any]]:
    """Return non-empty phase summaries ordered by first observed event frame."""
    summaries: dict[str, dict[str, Any]] = {}
    for event in events:
        phase = assign_event_phase(event, phase_rules)
        frame = int(event.get("frame", 0))
        conf = _safe_float(event.get("conf", 1.0))
        summary = summaries.setdefault(
            phase.key,
            {
                "phase_key": phase.key,
                "phase_name": phase.name,
                "configured_order": phase.configured_order,
                "first_frame": frame,
                "last_frame": frame,
                "step_count": 0,
                "has_error": False,
                "_conf_sum": 0.0,
            },
        )
        summary["first_frame"] = min(int(summary["first_frame"]), frame)
        summary["last_frame"] = max(int(summary["last_frame"]), frame)
        summary["step_count"] = int(summary["step_count"]) + 1
        summary["has_error"] = bool(summary["has_error"]) or str(event.get("event_type") or "").upper() == "ERROR"
        summary["_conf_sum"] = float(summary["_conf_sum"]) + conf

    ordered = sorted(summaries.values(), key=lambda item: (int(item["first_frame"]), int(item["configured_order"]), str(item["phase_name"])))
    for order, summary in enumerate(ordered, start=1):
        step_count = int(summary["step_count"])
        summary["phase_order"] = order
        summary["mean_confidence"] = float(summary.pop("_conf_sum")) / step_count if step_count else None
        summary["status"] = "contains_error" if summary["has_error"] else "observed"
    return ordered


def _component_display_lookup(cad_part_catalog_path: Path | None) -> dict[str, str]:
    if cad_part_catalog_path is None or not Path(cad_part_catalog_path).exists():
        return {}
    part_catalog = _load_json(Path(cad_part_catalog_path))
    return {
        str(component.get("key")): str(component.get("display_name") or component.get("key"))
        for component in part_catalog.get("components", [])
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
