"""Build the procedural_reasoning_graph from Layer 4 validation records."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


GRAPH_NAME = "procedural_reasoning_graph"
SCHEMA_VERSION = "1.0"

NODE_FIELDS = ["id", "type", "properties"]
EDGE_FIELDS = ["source", "target", "type", "properties"]


@dataclass(frozen=True)
class ProceduralReasoningGraphInputs:
    validations_path: Path
    output_dir: Path
    step_records_path: Path | None = None
    predicates_path: Path | None = None
    constraints_path: Path | None = None
    exclude_rejected: bool = False


def build_procedural_reasoning_graph(inputs: ProceduralReasoningGraphInputs) -> dict[str, Any]:
    validations = _read_records(Path(inputs.validations_path))
    step_records_by_id = _read_step_records_by_id(inputs.step_records_path)
    included_records = [
        record
        for record in validations
        if not (inputs.exclude_rejected and str(record.get("status") or "") == "rejected")
    ]

    builder = _GraphBuilder()
    step_nodes: dict[str, str] = {}
    step_status: dict[str, str] = {}
    constraint_nodes: dict[str, str] = {}
    predicate_nodes: dict[str, str] = {}
    rule_nodes: dict[str, str] = {}
    source_nodes: dict[str, str] = {}
    entity_types: dict[str, set[str]] = {}
    condition_names = _collect_condition_names(included_records)

    for record in included_records:
        step_id = str(record.get("step_id") or record.get("id") or "")
        if not step_id:
            continue
        step_record = step_records_by_id.get(step_id, {})
        step_node_id = _node_id("Step", step_id)
        step_nodes[step_id] = step_node_id
        step_status[step_id] = str(record.get("status") or "")
        builder.add_node(
            step_node_id,
            "Step",
            _clean_properties(
                {
                    "step_id": step_id,
                    "clip_result_id": step_record.get("clip_result_id") or record.get("clip_result_id"),
                    "run_id": step_record.get("run_id") or record.get("run_id"),
                    "mode": step_record.get("mode") or record.get("mode"),
                    "archive_name": step_record.get("archive_name") or record.get("archive_name"),
                    "clip": step_record.get("clip") or record.get("clip"),
                    "source_event_id": record.get("source_event_id"),
                    "index": record.get("index"),
                    "status": record.get("status"),
                    "display_name": _step_display_name(record),
                    "display_label": _step_display_label(record),
                    "short_id": _short_event_id(record.get("source_event_id") or step_id),
                    "confidence": record.get("confidence"),
                    "conf": record.get("conf"),
                    "schema_version": record.get("schema_version"),
                }
            ),
        )

        predicates = _dedupe_items(_predicates_for_record(record), "predicate_id")
        for predicate in predicates:
            predicate_node_id = _predicate_node_id(predicate)
            predicate_nodes[str(predicate.get("predicate_id") or predicate_node_id)] = predicate_node_id
            builder.add_node(predicate_node_id, "Predicate", _predicate_properties(predicate))
            builder.add_edge(step_node_id, predicate_node_id, "HAS_PREDICATE", {})

            source = predicate.get("source")
            if isinstance(source, dict):
                source_node_id = _source_node_id(source)
                source_nodes[source_node_id] = source_node_id
                builder.add_node(source_node_id, "Source", _source_properties(source, source_node_id))
                builder.add_edge(predicate_node_id, source_node_id, "DERIVED_FROM", {})

            if predicate.get("name") == "isA":
                args = _args(predicate)
                if len(args) >= 2 and _is_entity_arg(args[0], condition_names):
                    entity_types.setdefault(str(args[0]), set()).add(str(args[1]))

            for entity in _predicate_entity_args(predicate, condition_names):
                entity_node_id = _node_id("Entity", entity)
                builder.add_node(entity_node_id, "Entity", _entity_properties(entity))
                builder.add_edge(predicate_node_id, entity_node_id, "HAS_ENTITY", {})
                if predicate.get("name") in {"usesObject", "usesTool"}:
                    builder.add_edge(
                        step_node_id,
                        entity_node_id,
                        "USES",
                        {"predicate_id": predicate.get("predicate_id"), "predicate_name": predicate.get("name")},
                    )

        constraints = _dedupe_items(_constraints_for_record(record), "constraint_id")
        for constraint in constraints:
            constraint_node_id = _constraint_node_id(constraint)
            constraint_key = str(constraint.get("constraint_id") or constraint_node_id)
            constraint_nodes[constraint_key] = constraint_node_id
            builder.add_node(
                constraint_node_id,
                "Constraint",
                _constraint_properties(constraint, _constraint_support_status(record, constraint)),
            )
            builder.add_edge(step_node_id, constraint_node_id, "HAS_CONSTRAINT", {})

            name = str(constraint.get("name") or "")
            if name == "produces":
                builder.add_edge(step_node_id, constraint_node_id, "PRODUCES", {})
            if name in {"requires", "requiresTool", "requiresSafety"}:
                builder.add_edge(step_node_id, constraint_node_id, "REQUIRES", {})

            rule_id = _blank_to_none(constraint.get("rule_id"))
            if rule_id:
                rule_node_id = _node_id("Rule", rule_id)
                rule_nodes[rule_id] = rule_node_id
                builder.add_node(
                    rule_node_id,
                    "Rule",
                    {
                        "rule_id": rule_id,
                        "display_name": rule_id,
                        "display_label": rule_id,
                        "short_id": rule_id,
                    },
                )
                builder.add_edge(constraint_node_id, rule_node_id, "DERIVED_FROM", {})

            for entity in _constraint_entity_args(constraint, condition_names):
                entity_node_id = _node_id("Entity", entity)
                builder.add_node(entity_node_id, "Entity", _entity_properties(entity))
                builder.add_edge(constraint_node_id, entity_node_id, "HAS_ENTITY", {})

            for evidence_id in _evidence_predicate_ids(constraint):
                target = predicate_nodes.get(evidence_id) or _node_id("Predicate", evidence_id)
                builder.add_edge(constraint_node_id, target, "SUPPORTED_BY", {"support_type": "evidence_predicate"})

        for dependency in _dependency_items(record):
            support = dependency.get("supporting_effect") if isinstance(dependency, dict) else None
            if not isinstance(support, dict):
                continue
            earlier_step_id = _blank_to_none(support.get("step_id"))
            if not earlier_step_id or earlier_step_id not in step_nodes:
                continue
            if step_status.get(earlier_step_id) == "rejected":
                continue
            required_condition = dependency.get("required_condition")
            supporting_effect = support
            builder.add_edge(
                step_node_id,
                step_nodes[earlier_step_id],
                "DEPENDS_ON",
                _clean_properties(
                    {
                        "required_condition": required_condition,
                        "supporting_effect": supporting_effect,
                        "confidence": record.get("confidence") if record.get("confidence") is not None else record.get("conf"),
                        "provisional": step_status.get(earlier_step_id) == "uncertain",
                    }
                ),
            )

            requiring_constraint_id = _matching_requirement_constraint_id(record, required_condition)
            supporting_constraint_id = _blank_to_none(support.get("constraint_id"))
            if requiring_constraint_id and supporting_constraint_id:
                requiring_node = constraint_nodes.get(requiring_constraint_id) or _node_id("Constraint", requiring_constraint_id)
                supporting_node = constraint_nodes.get(supporting_constraint_id) or _node_id("Constraint", supporting_constraint_id)
                builder.add_edge(
                    requiring_node,
                    supporting_node,
                    "SUPPORTED_BY",
                    {"support_type": "previous_produced_effect"},
                )

    for entity, types in entity_types.items():
        entity_node_id = _node_id("Entity", entity)
        builder.add_node(entity_node_id, "Entity", _entity_properties(entity, sorted(types)))

    for node in list(builder.nodes.values()):
        if node["type"] == "Entity" and not node["properties"]:
            entity_id = node["id"].split("::", 1)[1]
            node["properties"] = _entity_properties(entity_id)

    ordered_steps = sorted(
        [
            record
            for record in included_records
            if str(record.get("step_id") or record.get("id") or "") in step_nodes
        ],
        key=lambda record: (
            int(record.get("index") if record.get("index") is not None else 0),
            str(record.get("step_id") or record.get("id") or ""),
        ),
    )
    for previous, current in zip(ordered_steps, ordered_steps[1:]):
        previous_step_id = str(previous.get("step_id") or previous.get("id") or "")
        current_step_id = str(current.get("step_id") or current.get("id") or "")
        builder.add_edge(step_nodes[previous_step_id], step_nodes[current_step_id], "NEXT", {})

    graph = {
        "schema_version": SCHEMA_VERSION,
        "graph_name": GRAPH_NAME,
        "nodes": sorted(builder.nodes.values(), key=lambda item: (item["type"], item["id"])),
        "edges": sorted(builder.edges.values(), key=lambda item: (item["type"], item["source"], item["target"], _stable_json(item["properties"]))),
    }

    output_dir = Path(inputs.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    graph_path = output_dir / "procedural_reasoning_graph.json"
    nodes_csv_path = output_dir / "procedural_reasoning_graph_nodes.csv"
    edges_csv_path = output_dir / "procedural_reasoning_graph_edges.csv"
    _write_json(graph_path, graph)
    _write_nodes_csv(nodes_csv_path, graph["nodes"])
    _write_edges_csv(edges_csv_path, graph["edges"])

    counts = _graph_counts(graph, included_records)
    return {
        **counts,
        "schema_version": SCHEMA_VERSION,
        "graph_name": GRAPH_NAME,
        "validations_path": str(inputs.validations_path),
        "step_records_path": str(inputs.step_records_path) if inputs.step_records_path else None,
        "output_path": str(graph_path),
        "nodes_csv_path": str(nodes_csv_path),
        "edges_csv_path": str(edges_csv_path),
        "excluded_rejected": bool(inputs.exclude_rejected),
    }


class _GraphBuilder:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    def add_node(self, node_id: str, node_type: str, properties: dict[str, Any]) -> None:
        existing = self.nodes.get(node_id)
        if existing is None:
            self.nodes[node_id] = {"id": node_id, "type": node_type, "properties": properties}
            return
        merged = dict(existing.get("properties", {}))
        merged.update({key: value for key, value in properties.items() if value not in (None, "", [], {})})
        existing["properties"] = merged

    def add_edge(self, source: str, target: str, edge_type: str, properties: dict[str, Any]) -> None:
        key = (source, target, edge_type, _stable_json(_clean_properties(properties)))
        self.edges[key] = {
            "source": source,
            "target": target,
            "type": edge_type,
            "properties": _clean_properties(properties),
        }


def _predicates_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        *list(record.get("evidence_predicates", []) or []),
        *list(record.get("trace", {}).get("predicate_evidence", []) or []),
    ]


def _constraints_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    trace = record.get("trace", {}) if isinstance(record.get("trace"), dict) else {}
    return [
        *list(record.get("evidence_constraints", []) or []),
        *list(record.get("produced_effects", []) or []),
        *list(record.get("supported_requirements", []) or []),
        *list(record.get("missing_requirements", []) or []),
        *list(record.get("tool_requirements", []) or []),
        *list(record.get("safety_requirements", []) or []),
        *list(record.get("incompatibilities", []) or []),
        *list(trace.get("constraint_evidence", []) or []),
        *list(trace.get("missing_requirements", []) or []),
        *list(trace.get("incompatibility_evidence", []) or []),
    ]


def _dependency_items(record: dict[str, Any]) -> list[dict[str, Any]]:
    trace = record.get("trace", {}) if isinstance(record.get("trace"), dict) else {}
    return [
        *list(record.get("dependency_support", []) or []),
        *list(trace.get("dependency_evidence", []) or []),
    ]


def _dedupe_items(items: Iterable[dict[str, Any]], key_field: str) -> list[dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = str(item.get(key_field) or _stable_json(item))
        if key not in output:
            output[key] = dict(item)
            continue
        existing = output[key]
        existing.update({field: value for field, value in item.items() if value not in (None, "", [], {})})
        existing_support = existing.get("support")
        item_support = item.get("support")
        if isinstance(item_support, dict) and item_support.get("type") != "same_step_constraint":
            existing["support"] = item_support
        elif existing_support in (None, "", {}, []):
            existing["support"] = item_support
    return list(output.values())


def _predicate_properties(predicate: dict[str, Any]) -> dict[str, Any]:
    name = str(predicate.get("name") or "")
    args = _args(predicate)
    return _clean_properties(
        {
            "predicate_id": predicate.get("predicate_id"),
            "name": predicate.get("name"),
            "predicate_key": predicate.get("predicate_key"),
            "category": predicate.get("category"),
            "args": args,
            "display_name": name,
            "display_label": _call_label(name, _compact_args(args)),
            "short_id": _short_predicate_id(predicate),
            "confidence": predicate.get("confidence") if predicate.get("confidence") is not None else predicate.get("conf"),
            "conf": predicate.get("conf") if predicate.get("conf") is not None else predicate.get("confidence"),
            "source": predicate.get("source"),
            "notes": predicate.get("notes"),
        }
    )


def _constraint_properties(constraint: dict[str, Any], support_status: str | None) -> dict[str, Any]:
    name = str(constraint.get("name") or "")
    args = _args(constraint)
    display_name = _constraint_display_name(name, args)
    return _clean_properties(
        {
            "constraint_id": constraint.get("constraint_id"),
            "name": constraint.get("name"),
            "kind": constraint.get("kind"),
            "args": args,
            "display_name": display_name,
            "display_label": _constraint_display_label(display_name, args, support_status),
            "short_id": _short_constraint_id(constraint),
            "confidence": constraint.get("confidence") if constraint.get("confidence") is not None else constraint.get("conf"),
            "conf": constraint.get("conf") if constraint.get("conf") is not None else constraint.get("confidence"),
            "rule_id": constraint.get("rule_id"),
            "support": constraint.get("support"),
            "status": constraint.get("status"),
            "support_status": support_status,
        }
    )


def _source_properties(source: dict[str, Any], source_node_id: str) -> dict[str, Any]:
    source_id = source_node_id.split("::", 1)[1]
    display_name = _source_display_name(source, source_id)
    return _clean_properties(
        {
            "source_id": source_id,
            "source_type": source.get("type"),
            "file": source.get("file"),
            "fields": source.get("fields"),
            "display_name": display_name,
            "display_label": display_name,
            "short_id": source_id,
        }
    )


def _entity_properties(entity_id: str, entity_type: list[str] | None = None) -> dict[str, Any]:
    return _clean_properties(
        {
            "entity_id": entity_id,
            "entity_type": entity_type or [],
            "display_name": entity_id,
            "display_label": entity_id,
            "short_id": entity_id,
        }
    )


def _step_display_name(record: dict[str, Any]) -> str:
    index = record.get("index")
    return f"Step {index}" if index is not None else "Step"


def _step_display_label(record: dict[str, Any]) -> str:
    name = _step_display_name(record)
    status = _blank_to_none(record.get("status"))
    return f"{name} [{status}]" if status else name


def _constraint_display_name(name: str, args: list[Any]) -> str:
    if name == "requiresTool":
        return "requires tool"
    if name == "requiresSafety":
        condition = str(args[1]) if len(args) > 1 else ""
        return f"requires safety {condition}".strip()
    if name in {"requires", "produces"}:
        condition = str(args[1]) if len(args) > 1 else ""
        return f"{name} {condition}".strip()
    if name == "incompatibleAction":
        return "incompatible action"
    return _humanize_identifier(name)


def _constraint_display_label(display_name: str, args: list[Any], support_status: str | None) -> str:
    compact_args = _compact_args(args[2:] if len(args) > 2 else args[1:])
    label = _call_label(display_name, compact_args)
    return f"{label} [{support_status}]" if support_status else label


def _source_display_name(source: dict[str, Any], source_id: str) -> str:
    file_name = Path(str(source.get("file") or "")).name
    source_type = _blank_to_none(source.get("type"))
    if file_name and source_type:
        return f"{source_type}:{file_name}"
    if file_name:
        return file_name
    return source_type or source_id


def _call_label(name: str, args: list[Any]) -> str:
    if not args:
        return name
    return f"{name}({', '.join(str(arg) for arg in args)})"


def _compact_args(args: list[Any], max_args: int = 4) -> list[Any]:
    compact = [_compact_arg(arg) for arg in args[:max_args]]
    if len(args) > max_args:
        compact.append("...")
    return compact


def _compact_arg(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value.startswith("step::"):
        return _short_event_id(value)
    return value


def _short_event_id(value: Any) -> str:
    text = str(value or "")
    if not text:
        return ""
    return text.split("::")[-1]


def _short_predicate_id(predicate: dict[str, Any]) -> str | None:
    return _blank_to_none(predicate.get("predicate_id")) or _blank_to_none(predicate.get("id"))


def _short_constraint_id(constraint: dict[str, Any]) -> str | None:
    return _blank_to_none(constraint.get("constraint_id")) or _blank_to_none(constraint.get("id"))


def _humanize_identifier(value: str) -> str:
    text = str(value or "").replace("_", " ")
    output = []
    for index, char in enumerate(text):
        previous = text[index - 1] if index else ""
        if index and char.isupper() and (previous.islower() or previous.isdigit()):
            output.append(" ")
        output.append(char.lower())
    return "".join(output).strip()


def _constraint_support_status(record: dict[str, Any], constraint: dict[str, Any]) -> str | None:
    constraint_id = constraint.get("constraint_id")
    if not constraint_id:
        return None
    for item in list(record.get("supported_requirements", []) or []):
        if item.get("constraint_id") == constraint_id:
            return "supported"
    for item in list(record.get("missing_requirements", []) or []):
        if item.get("constraint_id") == constraint_id:
            return "missing"
    support = constraint.get("support")
    if isinstance(support, dict) and support.get("type") == "same_step_constraint":
        return "observed"
    return None


def _predicate_entity_args(predicate: dict[str, Any], condition_names: set[str]) -> list[str]:
    name = str(predicate.get("name") or "")
    args = _args(predicate)
    if name in {"hasAction", "hasTimeWindow"}:
        return []
    if name in {"usesObject", "usesTool"}:
        return _entity_values(args[1:], condition_names)
    if name == "isA":
        return _entity_values(args[:1], condition_names)
    if name == "hasLabel":
        return _entity_values(args[:1], condition_names)
    if name in {"hasRequiredCondition", "hasSafetyRequirement"}:
        return _entity_values([args[0], *args[2:]], condition_names)
    return _entity_values(args, condition_names)


def _constraint_entity_args(constraint: dict[str, Any], condition_names: set[str]) -> list[str]:
    name = str(constraint.get("name") or "")
    args = _args(constraint)
    if name in {"requires", "produces", "requiresSafety"}:
        return _entity_values(args[2:], condition_names)
    if name == "requiresTool":
        return _entity_values(args[1:], condition_names)
    if name == "incompatibleAction":
        return _entity_values(args[1:-1], condition_names)
    return _entity_values(args, condition_names)


def _entity_values(values: Iterable[Any], condition_names: set[str]) -> list[str]:
    output = []
    for value in values:
        if _is_entity_arg(value, condition_names):
            output.append(str(value))
    return output


def _is_entity_arg(value: Any, condition_names: set[str]) -> bool:
    if value is None or isinstance(value, bool) or isinstance(value, (int, float)):
        return False
    text = str(value)
    if not text or text.startswith("step::"):
        return False
    if text in condition_names:
        return False
    if text.lower() in {"install", "remove", "error", "accepted", "uncertain", "rejected"}:
        return False
    return True


def _collect_condition_names(records: list[dict[str, Any]]) -> set[str]:
    names = {"installed", "aligned", "secured", "requiresTool"}
    for record in records:
        for constraint in _constraints_for_record(record):
            args = _args(constraint)
            name = str(constraint.get("name") or "")
            if name in {"requires", "produces", "requiresSafety"} and len(args) > 1:
                names.add(str(args[1]))
        for predicate in _predicates_for_record(record):
            args = _args(predicate)
            if predicate.get("name") in {"hasRequiredCondition", "hasSafetyRequirement"} and len(args) > 1:
                names.add(str(args[1]))
    return names


def _evidence_predicate_ids(constraint: dict[str, Any]) -> list[str]:
    value = constraint.get("evidence_predicate_ids", [])
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = []
    return [str(item) for item in list(value or []) if item]


def _matching_requirement_constraint_id(record: dict[str, Any], required_condition: Any) -> str | None:
    if not isinstance(required_condition, dict):
        return None
    required_name = required_condition.get("name")
    required_args = list(required_condition.get("args", []) or [])
    for requirement in list(record.get("supported_requirements", []) or []):
        condition = _condition_ref(requirement)
        if condition.get("name") == required_name and condition.get("args") == required_args:
            return _blank_to_none(requirement.get("constraint_id"))
    return None


def _condition_ref(constraint: dict[str, Any]) -> dict[str, Any]:
    args = _args(constraint)
    if not args:
        return {"name": constraint.get("name"), "args": []}
    if constraint.get("name") == "requiresTool":
        return {"name": "requiresTool", "args": args[1:]}
    return {"name": args[1] if len(args) > 1 else constraint.get("name"), "args": args[2:]}


def _graph_counts(graph: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    node_counts = _count_by(graph["nodes"], "type")
    edge_counts = _count_by(graph["edges"], "type")
    status_counts: dict[str, int] = {}
    for record in records:
        status = str(record.get("status") or "")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "node_counts": node_counts,
        "edge_counts": edge_counts,
        "step_status_counts": dict(sorted(status_counts.items())),
    }


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "")
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _read_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with open(path, newline="", encoding="utf-8") as f:
        return [_parse_csv_record(row) for row in csv.DictReader(f)]


def _parse_csv_record(row: dict[str, str]) -> dict[str, Any]:
    parsed: dict[str, Any] = dict(row)
    for key in ("args", "source", "support", "evidence_predicate_ids"):
        if parsed.get(key):
            try:
                parsed[key] = json.loads(parsed[key])
            except json.JSONDecodeError:
                pass
    for key in ("conf", "confidence"):
        if key in parsed:
            parsed[key] = _parse_float(parsed[key])
    return parsed


def _read_step_records_by_id(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not Path(path).exists():
        return {}
    return {
        str(record.get("id")): record
        for record in _read_records(Path(path))
        if record.get("id")
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _write_nodes_csv(path: Path, nodes: list[dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=NODE_FIELDS)
        writer.writeheader()
        for node in nodes:
            writer.writerow({**node, "properties": json.dumps(node.get("properties", {}), ensure_ascii=False, sort_keys=True)})


def _write_edges_csv(path: Path, edges: list[dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EDGE_FIELDS)
        writer.writeheader()
        for edge in edges:
            writer.writerow({**edge, "properties": json.dumps(edge.get("properties", {}), ensure_ascii=False, sort_keys=True)})


def _predicate_node_id(predicate: dict[str, Any]) -> str:
    return _node_id("Predicate", str(predicate.get("predicate_id") or _stable_json(predicate)))


def _constraint_node_id(constraint: dict[str, Any]) -> str:
    return _node_id("Constraint", str(constraint.get("constraint_id") or _stable_json(constraint)))


def _source_node_id(source: dict[str, Any]) -> str:
    return _node_id("Source", _stable_hash(source))


def _node_id(node_type: str, raw_id: str) -> str:
    return f"{node_type}::{raw_id}"


def _args(item: dict[str, Any]) -> list[Any]:
    args = item.get("args", [])
    if isinstance(args, str):
        return json.loads(args) if args else []
    return list(args or [])


def _clean_properties(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in properties.items()
        if value is not None and value != "" and value != []
    }


def _stable_hash(value: Any) -> str:
    return hashlib.sha1(_stable_json(value).encode("utf-8")).hexdigest()[:16]


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _blank_to_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
