"""Layer 4 validation over Layer 3 constraints and accumulated effects."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Layer4Inputs:
    step_records_path: Path
    predicates_path: Path
    constraints_path: Path
    output_path: Path


def run_layer4_validation(inputs: Layer4Inputs) -> dict[str, Any]:
    steps = _read_records(Path(inputs.step_records_path))
    predicates = _read_records(Path(inputs.predicates_path))
    constraints = _read_records(Path(inputs.constraints_path))

    predicates_by_step = _group_by_step(predicates)
    constraints_by_step = _group_by_step(constraints)
    ordered_steps = sorted(steps, key=_step_sort_key)

    validation_records: list[dict[str, Any]] = []
    effect_history: dict[tuple[Any, ...], dict[str, Any]] = {}
    for step in ordered_steps:
        step_id = str(step.get("id") or step.get("step_id") or "")
        if not step_id:
            continue
        step_predicates = predicates_by_step.get(step_id, [])
        step_constraints = constraints_by_step.get(step_id, [])
        record = _validate_step(step, step_predicates, step_constraints, effect_history)
        validation_records.append(record)
        for constraint in step_constraints:
            if constraint.get("name") == "produces":
                effect_history[_condition_key(constraint)] = constraint

    _write_jsonl(Path(inputs.output_path), validation_records)
    return {
        "step_records": len(steps),
        "predicates": len(predicates),
        "constraints": len(constraints),
        "validation_records": len(validation_records),
        "output_path": str(inputs.output_path),
        "status_counts": _count_by(validation_records, "status"),
        "supported_requires": sum(len(item.get("supported_requires", [])) for item in validation_records),
        "missing_requires": sum(len(item.get("missing_requires", [])) for item in validation_records),
        "history_effects": len(effect_history),
    }


def _validate_step(
    step: dict[str, Any],
    predicates: list[dict[str, Any]],
    constraints: list[dict[str, Any]],
    effect_history: dict[tuple[Any, ...], dict[str, Any]],
) -> dict[str, Any]:
    step_id = str(step.get("id") or step.get("step_id") or "")
    requirements = [
        item
        for item in constraints
        if item.get("name") in {"requires", "requiresSafety", "requiresTool"}
    ]
    incompatibilities = [
        item
        for item in constraints
        if item.get("name") == "incompatibleAction" or item.get("status") == "incompatibility"
    ]
    supported_requires = []
    missing_requires = []
    for constraint in requirements:
        support = _support_for_required_condition(constraint, predicates, effect_history)
        if support is None:
            missing_requires.append(_constraint_ref(constraint, support=None))
        else:
            supported_requires.append(_constraint_ref(constraint, support=support))

    if incompatibilities:
        status = "rejected"
    elif missing_requires:
        status = "uncertain"
    else:
        status = "accepted"

    confidence_values = [
        _parse_float(item.get("conf"))
        for item in [*constraints, *predicates]
        if _parse_float(item.get("conf")) is not None
    ]
    conf = min(confidence_values) if confidence_values else None
    return {
        "schema_version": "thesis_layer4_validation.v1",
        "record_type": "validation_record",
        "step_id": step_id,
        "source_event_id": step.get("source_event_id"),
        "index": step.get("index"),
        "status": status,
        "conf": conf,
        "supported_requires": supported_requires,
        "missing_requires": missing_requires,
        "produced_effects": [
            _constraint_ref(item, support=None)
            for item in constraints
            if item.get("name") == "produces"
        ],
        "safety_requirements": [_constraint_ref(item, support=None) for item in constraints if item.get("name") == "requiresSafety"],
        "tool_requirements": [_constraint_ref(item, support=None) for item in constraints if item.get("name") == "requiresTool"],
        "incompatibilities": [_constraint_ref(item, support=None) for item in incompatibilities],
        "trace": {
            "predicate_ids": [str(item.get("id")) for item in predicates],
            "constraint_ids": [str(item.get("constraint_id")) for item in constraints],
        },
    }


def _support_for_required_condition(
    constraint: dict[str, Any],
    predicates: list[dict[str, Any]],
    effect_history: dict[tuple[Any, ...], dict[str, Any]],
) -> dict[str, Any] | None:
    key = _condition_key(constraint)
    if key in effect_history:
        effect = effect_history[key]
        return {
            "type": "previous_produced_effect",
            "constraint_id": effect.get("constraint_id"),
            "step_id": effect.get("step_id"),
            "args": _constraint_args(effect),
        }
    for predicate in predicates:
        if _predicate_supports_condition(predicate, key):
            return {
                "type": "same_step_predicate",
                "predicate_id": predicate.get("id"),
                "step_id": predicate.get("step_id"),
                "args": _predicate_args(predicate),
            }
    return None


def _predicate_supports_condition(predicate: dict[str, Any], condition_key: tuple[Any, ...]) -> bool:
    _ = predicate
    _ = condition_key
    return False


def _condition_key(constraint: dict[str, Any]) -> tuple[Any, ...]:
    args = _constraint_args(constraint)
    if not args:
        return ()
    return tuple(args[1:])


def _constraint_ref(constraint: dict[str, Any], *, support: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "constraint_id": constraint.get("constraint_id"),
        "name": constraint.get("name"),
        "kind": constraint.get("kind"),
        "args": _constraint_args(constraint),
        "conf": _parse_float(constraint.get("conf")),
        "rule_id": constraint.get("rule_id"),
        "support": support,
    }


def _group_by_step(rows: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        step_id = str(row.get("step_id") or "")
        if step_id:
            grouped.setdefault(step_id, []).append(row)
    return grouped


def _step_sort_key(step: dict[str, Any]) -> tuple[str, int, str]:
    return (
        str(step.get("clip_result_id") or ""),
        int(step.get("index") if step.get("index") is not None else 0),
        str(step.get("id") or ""),
    )


def _read_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with open(path, newline="", encoding="utf-8") as f:
        return [_parse_csv_record(row) for row in csv.DictReader(f)]


def _parse_csv_record(row: dict[str, str]) -> dict[str, Any]:
    parsed: dict[str, Any] = dict(row)
    for key in ("args", "evidence_predicate_ids"):
        if parsed.get(key):
            parsed[key] = json.loads(parsed[key])
    for key in ("conf", "threshold"):
        if key in parsed:
            parsed[key] = _parse_float(parsed[key])
    return parsed


def _constraint_args(constraint: dict[str, Any]) -> list[Any]:
    args = constraint.get("args", [])
    if isinstance(args, str):
        return json.loads(args) if args else []
    return list(args or [])


def _predicate_args(predicate: dict[str, Any]) -> list[Any]:
    args = predicate.get("args", [])
    if isinstance(args, str):
        return json.loads(args) if args else []
    return list(args or [])


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
