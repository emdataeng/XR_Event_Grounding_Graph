"""Load and serialize procedural reasoning graph evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SEMANTIC_EDGE_TYPES = frozenset(
    {
        "DEPENDS_ON",
        "DERIVED_FROM",
        "HAS_CONSTRAINT",
        "HAS_ENTITY",
        "HAS_PREDICATE",
        "INVALIDATED_BY",
        "PRODUCES",
        "REQUIRES",
        "SUPPORTED_BY",
        "USES",
    }
)
EXPANDABLE_EVIDENCE_NODE_TYPES = frozenset({"Predicate", "Constraint"})


@dataclass(frozen=True)
class DatasetSelection:
    """Identifies the dataset and optional clip used for an experiment run."""

    kind: str
    clip_id: str | None = None


def load_experiment_artifacts(config: dict[str, Any], selection: DatasetSelection) -> dict[str, Any]:
    """Load the graph artifact for a selected dataset or clip."""
    configured_path = str(config.get("input_paths", {}).get("procedural_reasoning_graph") or "").strip()
    if configured_path and "PLACEHOLDER" not in configured_path:
        path = resolve_path(configured_path, REPO_ROOT)
    else:
        dataset_id = selection.clip_id or str(config.get("dataset", {}).get("default_clip_id") or "")
        root = REPO_ROOT / "results" / "procedural_reasoning_graph"
        path = graph_artifact_path(root, dataset_id)
    return {
        "procedural_reasoning_graph": load_procedural_reasoning_graph(path),
        "procedural_reasoning_graph_path": str(path),
    }


def resolve_path(path_value: str, base_dir: Path | None = None) -> Path:
    """Resolve a configured path relative to an optional base directory."""
    path = Path(path_value)
    if path.is_absolute() or base_dir is None:
        return path
    return base_dir / path


def load_procedural_reasoning_graph(path: str | Path) -> dict[str, Any]:
    """Load a procedural reasoning graph JSON artifact."""
    graph_path = Path(path)
    if not graph_path.exists():
        raise FileNotFoundError(f"Procedural reasoning graph is missing: {graph_path}")
    with graph_path.open("r", encoding="utf-8") as handle:
        graph = json.load(handle)
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), list) or not isinstance(graph.get("edges"), list):
        raise ValueError(f"Expected graph JSON with 'nodes' and 'edges' lists: {graph_path}")
    return graph


def graph_artifact_path(results_root: str | Path, dataset_id: str) -> Path:
    """Return the graph artifact path for a dataset or IndustReal clip id."""
    directory_name = dataset_id.strip().replace("::", "__")
    if not directory_name:
        raise ValueError("A dataset id is required to resolve the graph artifact path.")
    return Path(results_root) / directory_name / "procedural_reasoning_graph.json"


def extract_step_subgraph(
    graph: dict,
    step_id: str,
    hops: int,
    evidence_hops: int,
) -> dict:
    """Extract sequence and semantic neighborhoods around a selected step.

    ``hops`` traverses only ``NEXT`` edges between steps. ``evidence_hops``
    starts from the original current step and follows the semantic edge
    allowlist. Newly encountered steps, entities, rules, and sources are
    included but terminal; only predicates and constraints expand further.
    """
    if hops < 0 or evidence_hops < 0:
        raise ValueError("hops and evidence_hops must be zero or greater")

    nodes = [node for node in graph.get("nodes", []) if isinstance(node, dict) and node.get("id")]
    edges = sorted(
        (edge for edge in graph.get("edges", []) if isinstance(edge, dict)),
        key=_edge_sort_key,
    )
    nodes_by_id = {str(node["id"]): node for node in nodes}
    wanted_step = _canonical_step_id(step_id)
    selected_ids = {
        node_id
        for node_id, node in nodes_by_id.items()
        if _canonical_step_id(_node_step_id(node)) == wanted_step
    }
    if not selected_ids:
        return {"nodes": [], "edges": []}

    evidence_roots = set(selected_ids)
    selected_edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    frontier = set(selected_ids)
    for _ in range(hops):
        discovered: set[str] = set()
        for edge in edges:
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if edge.get("type") != "NEXT":
                continue
            if _node_type(nodes_by_id.get(source)) != "Step" or _node_type(nodes_by_id.get(target)) != "Step":
                continue
            if source not in frontier and target not in frontier:
                continue
            selected_edges.setdefault(_edge_identity(edge), edge)
            if source in nodes_by_id:
                discovered.add(source)
            if target in nodes_by_id:
                discovered.add(target)
        discovered -= selected_ids
        if not discovered:
            break
        selected_ids.update(discovered)
        frontier = discovered

    frontier = set(evidence_roots)
    for _ in range(evidence_hops):
        discovered: set[str] = set()
        next_frontier: set[str] = set()
        for edge in edges:
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if edge.get("type") not in SEMANTIC_EDGE_TYPES:
                continue
            if source not in frontier and target not in frontier:
                continue
            selected_edges.setdefault(_edge_identity(edge), edge)
            for node_id in (source, target):
                if node_id not in nodes_by_id or node_id in selected_ids:
                    continue
                discovered.add(node_id)
                if _node_type(nodes_by_id[node_id]) in EXPANDABLE_EVIDENCE_NODE_TYPES:
                    next_frontier.add(node_id)
        if not discovered:
            break
        selected_ids.update(discovered)
        frontier = next_frontier
        if not frontier:
            break

    return {
        "nodes": sorted(
            (node for node in nodes if str(node["id"]) in selected_ids),
            key=lambda node: str(node["id"]),
        ),
        "edges": sorted(selected_edges.values(), key=_edge_sort_key),
    }


def _node_type(node: dict[str, Any] | None) -> str:
    return str(node.get("type") or "") if isinstance(node, dict) else ""


def _edge_identity(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (str(edge.get("source", "")), str(edge.get("target", "")), str(edge.get("type", "")))


def _edge_sort_key(edge: dict[str, Any]) -> tuple[str, str, str, str]:
    source, target, edge_type = _edge_identity(edge)
    properties = json.dumps(edge.get("properties", {}), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (edge_type, source, target, properties)


def serialize_graph_evidence(subgraph: dict, current_step_id: str | None = None) -> str:
    """Render graph evidence as compact, stable text for an LLM prompt."""
    nodes = [node for node in subgraph.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in subgraph.get("edges", []) if isinstance(edge, dict)]
    if not nodes:
        return "No procedural reasoning graph evidence was found for this step."

    nodes_by_id = {str(node.get("id")): node for node in nodes}
    aliases = {str(node.get("id")): f"N{index}" for index, node in enumerate(nodes, start=1)}
    current_node_id = _find_step_node_id(nodes, current_step_id)
    lines = [f"Graph evidence ({len(nodes)} nodes, {len(edges)} edges):", "Nodes:"]
    for node in nodes:
        node_id = str(node.get("id", ""))
        node_type = str(node.get("type") or "Node")
        properties = node.get("properties") if isinstance(node.get("properties"), dict) else {}
        label = properties.get("display_label") or properties.get("action_description") or properties.get("short_id")
        detail_keys = (
            ("step_id", "action_description", "status", "confidence", "warning_count")
            if node_type == "Step"
            else ("kind", "name", "args", "status", "support_status", "rule_id", "confidence", "warning_count")
        )
        details = _selected_details(properties, detail_keys)
        summary = f"{aliases[node_id]} [{node_type}]"
        if node_id == current_node_id:
            summary += " [CURRENT]"
        if label:
            summary += f" {label}"
        if details:
            summary += f"; {details}"
        lines.append(f"- {summary}")

    lines.append("Edges:")
    for edge in edges:
        source_id = str(edge.get("source", ""))
        target_id = str(edge.get("target", ""))
        relation = str(edge.get("type") or "RELATED_TO")
        source = _edge_endpoint(aliases.get(source_id, source_id or "unknown"), nodes_by_id.get(source_id), relation)
        target = _edge_endpoint(aliases.get(target_id, target_id or "unknown"), nodes_by_id.get(target_id), relation)
        properties = edge.get("properties") if isinstance(edge.get("properties"), dict) else {}
        details = _selected_details(properties, ("required_condition", "supporting_effect", "confidence", "provisional"))
        line = f"- {source} -[{relation}]-> {target}"
        if details:
            line += f"; {details}"
        lines.append(line)
    return "\n".join(lines)


def _find_step_node_id(nodes: list[dict[str, Any]], step_id: str | None) -> str | None:
    wanted = _canonical_step_id(step_id)
    if not wanted:
        return None
    for node in nodes:
        if _node_type(node) == "Step" and _canonical_step_id(_node_step_id(node)) == wanted:
            return str(node.get("id"))
    return None


def _edge_endpoint(alias: str, node: dict[str, Any] | None, relation: str) -> str:
    """Add compact step identity only where relationship direction is central."""
    if relation not in {"NEXT", "DEPENDS_ON"} or _node_type(node) != "Step":
        return alias
    properties = node.get("properties") if isinstance(node.get("properties"), dict) else {}
    step_id = _short_step_reference(properties.get("step_id") or properties.get("source_event_id") or node.get("id"))
    return f"{alias}<Step:{step_id}>"


def _node_step_id(node: dict[str, Any]) -> str:
    properties = node.get("properties") if isinstance(node.get("properties"), dict) else {}
    return str(properties.get("step_id") or properties.get("source_event_id") or node.get("id") or "")


def _canonical_step_id(value: Any) -> str:
    text = str(value or "")
    for prefix in ("Step::step::", "Step::", "step::"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    prefix, separator, suffix = text.rpartition("event_")
    if separator and suffix.isdigit():
        return f"{prefix}{separator}{int(suffix)}"
    return text


def _selected_details(properties: dict[str, Any], keys: tuple[str, ...]) -> str:
    parts = []
    for key in keys:
        value = properties.get(key)
        if value is None or value == "" or value == [] or value == {}:
            continue
        value = _compact_detail_value(key, value)
        parts.append(f"{key}={json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}")
    return "; ".join(parts)


def _compact_detail_value(key: str, value: Any) -> Any:
    """Remove repeated identifiers while preserving decision-relevant evidence."""
    if key == "args" and isinstance(value, list):
        return [_short_step_reference(item) for item in value]
    if key == "step_id":
        return _short_step_reference(value)
    if key == "required_condition" and isinstance(value, dict):
        return {field: value[field] for field in ("name", "args") if field in value}
    if key == "supporting_effect" and isinstance(value, dict):
        compact = {
            field: value[field]
            for field in ("type", "condition", "producer_status", "provisional")
            if field in value
        }
        if "step_id" in value:
            compact["step_id"] = _short_step_reference(value["step_id"])
        return compact
    return value


def _short_step_reference(value: Any) -> Any:
    text = str(value)
    if "::event_" in text:
        return text.rpartition("::")[2]
    return value
