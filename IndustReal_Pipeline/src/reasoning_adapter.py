"""Adapt existing IndustReal graph CSVs into thesis Layer 1/2 records.

This module is intentionally downstream of the existing graph exporter. It
does not change the current assembly graph generation, Neo4j CSV export, or
Neo4j import path.
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_RUN_ID = "raw_cad_dataset__all_test_clips"
DEFAULT_CSV_DIR = Path(__file__).resolve().parent.parent / "results" / "neo4j" / DEFAULT_RUN_ID
DEFAULT_OUTPUT_ROOT = Path(__file__).resolve().parent.parent / "results" / "reasoning_layers"

EVENTS_CSV = "nodes_events.csv"
EVENT_COMPONENT_CSV = "edges_event_component.csv"
EVENT_NEXT_CSV = "edges_event_next.csv"
COMPONENTS_CSV = "nodes_components.csv"


@dataclass(frozen=True)
class AdapterInputs:
    csv_dir: Path
    run_id: str
    output_dir: Path
    clip_result_id: str | None = None
    mode: str | None = None
    archive_name: str | None = None
    clip: str | None = None
    evidence_root: Path | None = None


def build_reasoning_adapter_outputs(inputs: AdapterInputs) -> dict[str, Any]:
    """Build step_records.jsonl and predicates.jsonl from existing graph CSVs."""
    csv_dir = Path(inputs.csv_dir)
    output_dir = Path(inputs.output_dir)
    events = _read_csv(csv_dir / EVENTS_CSV)
    event_component_edges = _read_csv(csv_dir / EVENT_COMPONENT_CSV)
    event_next_edges = _read_csv(csv_dir / EVENT_NEXT_CSV)
    components = _read_csv(csv_dir / COMPONENTS_CSV)

    filtered_events = _filter_events(
        events,
        clip_result_id=inputs.clip_result_id,
        mode=inputs.mode,
        archive_name=inputs.archive_name,
        clip=inputs.clip,
    )
    event_ids = {_event_id(row) for row in filtered_events}
    component_by_id = {_component_id(row): row for row in components}
    edges_by_event: dict[str, list[dict[str, str]]] = {}
    for edge in event_component_edges:
        start_id = edge.get(":START_ID(AssemblyEvent)", "")
        if start_id in event_ids:
            edges_by_event.setdefault(start_id, []).append(edge)

    next_by_event = {
        edge.get(":START_ID(AssemblyEvent)", ""): edge.get(":END_ID(AssemblyEvent)", "")
        for edge in event_next_edges
        if edge.get(":START_ID(AssemblyEvent)", "") in event_ids
    }
    previous_by_event = {
        edge.get(":END_ID(AssemblyEvent)", ""): edge.get(":START_ID(AssemblyEvent)", "")
        for edge in event_next_edges
        if edge.get(":END_ID(AssemblyEvent)", "") in event_ids
    }

    ordered_events = sorted(
        filtered_events,
        key=lambda row: (
            row.get("clip_result_id", ""),
            _parse_int(row.get("local_event_id:int"), default=0),
            _parse_int(row.get("frame:int"), default=0),
            _event_id(row),
        ),
    )

    step_records: list[dict[str, Any]] = []
    predicates: list[dict[str, Any]] = []
    for row in ordered_events:
        step_record = _step_record(
            row,
            edges_by_event=edges_by_event,
            component_by_id=component_by_id,
            next_event_id=next_by_event.get(_event_id(row)),
            previous_event_id=previous_by_event.get(_event_id(row)),
            evidence_root=inputs.evidence_root,
        )
        step_records.append(step_record)
        predicates.extend(
            _predicates_for_step(
                step_record,
                row,
                edges_by_event=edges_by_event,
                component_by_id=component_by_id,
            )
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    step_path = output_dir / "step_records.jsonl"
    pred_path = output_dir / "predicates.jsonl"
    _write_jsonl(step_path, step_records)
    _write_jsonl(pred_path, predicates)

    return {
        "run_id": inputs.run_id,
        "csv_dir": str(csv_dir),
        "output_dir": str(output_dir),
        "step_records_path": str(step_path),
        "predicates_path": str(pred_path),
        "step_records": len(step_records),
        "predicates": len(predicates),
        "clip_result_ids": sorted({str(row.get("clip_result_id", "")) for row in ordered_events}),
        "missing_information": _missing_information_summary(step_records),
    }


def _step_record(
    row: dict[str, str],
    *,
    edges_by_event: dict[str, list[dict[str, str]]],
    component_by_id: dict[str, dict[str, str]],
    next_event_id: str | None,
    previous_event_id: str | None,
    evidence_root: Path | None,
) -> dict[str, Any]:
    event_id = _event_id(row)
    step_id = _step_id(event_id)
    frame = _parse_int(row.get("frame:int"))
    time_s = _parse_float(row.get("time_s:float"))
    component_refs = _component_refs(event_id, edges_by_event=edges_by_event, component_by_id=component_by_id)
    missing_inputs = ["time_window.end_frame", "time_window.end_s"]
    evidence_paths = _available_evidence_paths(row, evidence_root=evidence_root)
    if not evidence_paths:
        missing_inputs.extend(
            [
                "state_sequence.csv",
                "frame_evidence.jsonl",
                "smoothed_frame_evidence.jsonl",
            ]
        )

    return {
        "schema_version": "thesis_reasoning_adapter.v1",
        "record_type": "step_segment",
        "id": step_id,
        "source_event_id": event_id,
        "clip_result_id": _blank_to_none(row.get("clip_result_id")),
        "run_id": _blank_to_none(row.get("run_id")),
        "mode": _blank_to_none(row.get("mode")),
        "archive_name": _blank_to_none(row.get("archive_name")),
        "clip": _blank_to_none(row.get("clip")),
        "index": _parse_int(row.get("local_event_id:int")),
        "sequence": {
            "previous_event_id": previous_event_id,
            "next_event_id": next_event_id,
            "source": f"{EVENT_NEXT_CSV} when present; local_event_id:int otherwise",
        },
        "time_window": {
            "start_frame": frame,
            "end_frame": None,
            "start_s": time_s,
            "end_s": None,
            "source": f"{EVENTS_CSV}: frame:int/time_s:float",
            "notes": "Existing graph stores step instants, not durations.",
        },
        "action": {
            "name": _normalize_action(row),
            "event_type": _blank_to_none(row.get("event_type")),
            "description": _blank_to_none(row.get("action_desc")),
            "source": f"{EVENTS_CSV}: event_type/action_desc",
        },
        "objects": component_refs,
        "source_descriptions": [
            _source_description("display_name", row.get("display_name")),
            _source_description("name", row.get("name")),
            _source_description("action_desc", row.get("action_desc")),
        ],
        "confidence": _parse_float(row.get("conf:float")),
        "available_evidence_files": evidence_paths,
        "missing_inputs": sorted(set(missing_inputs)),
        "provenance": {
            "source": "existing_industreal_graph_csv",
            "source_files": [EVENTS_CSV, EVENT_COMPONENT_CSV, EVENT_NEXT_CSV, COMPONENTS_CSV],
        },
    }


def _predicates_for_step(
    step_record: dict[str, Any],
    row: dict[str, str],
    *,
    edges_by_event: dict[str, list[dict[str, str]]],
    component_by_id: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    event_id = str(step_record["source_event_id"])
    step_id = str(step_record["id"])
    conf = _parse_float(row.get("conf:float"))
    predicates = [
        _predicate(
            step_id,
            "hasAction",
            [step_id, step_record["action"]["name"]],
            conf,
            source_file=EVENTS_CSV,
            source_fields=["event_type", "action_desc"],
            notes=None if step_record["action"]["name"] is not None else "Action could not be normalized from event_type/action_desc.",
        ),
        _predicate(
            step_id,
            "hasTimeWindow",
            [
                step_id,
                step_record["time_window"]["start_s"],
                step_record["time_window"]["end_s"],
            ],
            conf,
            source_file=EVENTS_CSV,
            source_fields=["frame:int", "time_s:float"],
            notes="End time is null because the existing graph stores step instants, not durations.",
        ),
    ]
    for edge in edges_by_event.get(event_id, []):
        component_id = edge.get(":END_ID(Component)", "")
        component = component_by_id.get(component_id, {})
        component_label = _blank_to_none(component.get("name")) or _label_from_component_id(component_id)
        component_type = _blank_to_none(component.get("normalized_name")) or _normalize_token(component_label)
        edge_role = str(edge.get("role") or "component").lower()
        relation = "usesTool" if edge_role == "tool" else "usesObject"
        role_note = None
        if relation == "usesObject":
            role_note = "Existing graph marks this ACTS_ON edge as a component; no tool-specific role was available."
        predicates.append(
            _predicate(
                step_id,
                relation,
                [step_id, component_id],
                conf,
                source_file=EVENT_COMPONENT_CSV,
                source_fields=[":START_ID(AssemblyEvent)", ":END_ID(Component)", "role"],
                notes=role_note,
            )
        )
        predicates.append(
            _predicate(
                step_id,
                "isA",
                [component_id, component_type],
                conf,
                source_file=COMPONENTS_CSV,
                source_fields=["component_id:ID(Component)", "name", "normalized_name"],
                notes="Component type is derived from the existing component normalized_name, not from a richer ontology.",
            )
        )
        predicates.append(
            _predicate(
                step_id,
                "hasLabel",
                [component_id, component_label],
                conf,
                source_file=COMPONENTS_CSV,
                source_fields=["component_id:ID(Component)", "display_name", "name"],
                notes=None,
            )
        )
    return predicates


def _predicate(
    step_id: str,
    name: str,
    args: list[Any],
    conf: float | None,
    *,
    source_file: str,
    source_fields: list[str],
    notes: str | None,
) -> dict[str, Any]:
    suffix = _normalize_token("_".join(str(arg) for arg in args if arg is not None))[:96]
    return {
        "schema_version": "thesis_reasoning_adapter.v1",
        "record_type": "predicate",
        "id": f"{step_id}::p::{name}::{suffix}",
        "step_id": step_id,
        "name": name,
        "args": args,
        "conf": conf,
        "source": {
            "type": "existing_graph_csv",
            "file": source_file,
            "fields": source_fields,
        },
        "notes": notes,
    }


def _filter_events(
    rows: list[dict[str, str]],
    *,
    clip_result_id: str | None,
    mode: str | None,
    archive_name: str | None,
    clip: str | None,
) -> list[dict[str, str]]:
    output = []
    for row in rows:
        if clip_result_id and row.get("clip_result_id") != clip_result_id:
            continue
        if mode and row.get("mode") != mode:
            continue
        if archive_name and row.get("archive_name") != archive_name:
            continue
        if clip and row.get("clip") != clip:
            continue
        output.append(row)
    return output


def _component_refs(
    event_id: str,
    *,
    edges_by_event: dict[str, list[dict[str, str]]],
    component_by_id: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    refs = []
    for edge in edges_by_event.get(event_id, []):
        component_id = edge.get(":END_ID(Component)", "")
        component = component_by_id.get(component_id, {})
        refs.append(
            {
                "id": component_id or None,
                "label": _blank_to_none(component.get("name")) or _label_from_component_id(component_id),
                "type": _blank_to_none(component.get("normalized_name")),
                "role": _blank_to_none(edge.get("role")) or "component",
                "source_edge_type": _blank_to_none(edge.get(":TYPE")),
            }
        )
    return refs


def _available_evidence_paths(row: dict[str, str], *, evidence_root: Path | None) -> dict[str, str]:
    if evidence_root is None:
        return {}
    mode = row.get("mode")
    archive_name = row.get("archive_name")
    clip = row.get("clip")
    if not mode or not archive_name or not clip:
        return {}
    clip_dir = Path(evidence_root) / "modes" / mode / archive_name / clip
    candidates = {
        "state_sequence": clip_dir / "state_sequence.csv",
        "frame_evidence": clip_dir / "frame_evidence.jsonl",
        "smoothed_frame_evidence": clip_dir / "smoothed_frame_evidence.jsonl",
    }
    return {key: str(path) for key, path in candidates.items() if path.exists()}


def _normalize_action(row: dict[str, str]) -> str | None:
    event_type = str(row.get("event_type") or "").strip().lower()
    if event_type:
        return event_type
    action_desc = str(row.get("action_desc") or "").strip().lower()
    if not action_desc:
        return None
    return action_desc.split(maxsplit=1)[0]


def _source_description(kind: str, value: str | None) -> dict[str, Any]:
    return {
        "type": kind,
        "text": _blank_to_none(value),
        "source": EVENTS_CSV,
    }


def _missing_information_summary(step_records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in step_records:
        for item in record.get("missing_inputs", []):
            counts[str(item)] = counts.get(str(item), 0) + 1
    return dict(sorted(counts.items()))


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _event_id(row: dict[str, str]) -> str:
    return str(row.get("event_id:ID(AssemblyEvent)") or "")


def _component_id(row: dict[str, str]) -> str:
    return str(row.get("component_id:ID(Component)") or "")


def _step_id(event_id: str) -> str:
    return f"step::{event_id}"


def _label_from_component_id(component_id: str) -> str | None:
    if not component_id:
        return None
    return component_id.rsplit("::", 1)[-1].replace("_", " ")


def _normalize_token(value: Any) -> str:
    text = str(value or "unknown").lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return cleaned or "unknown"


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text != "" else None


def _parse_int(value: str | None, *, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    return int(float(value))


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
