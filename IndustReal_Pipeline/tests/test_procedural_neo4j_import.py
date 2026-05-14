from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.procedural_neo4j_import import (
    clear_graph_cypher,
    edge_import_cypher,
    load_procedural_graph,
    neo4j_identifier,
    normalize_graph,
    node_import_cypher,
)


def test_loads_csv_graph_and_normalizes_nested_properties(tmp_path: Path) -> None:
    nodes_path = tmp_path / "procedural_reasoning_graph_nodes.csv"
    edges_path = tmp_path / "procedural_reasoning_graph_edges.csv"
    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "type", "properties"])
        writer.writeheader()
        writer.writerow(
            {
                "id": "Step::a",
                "type": "Step",
                "properties": json.dumps({"step_id": "a", "args": ["base", "workspace"], "window": [70.9, 71.2]}),
            }
        )
        writer.writerow(
            {
                "id": "Constraint::c",
                "type": "Constraint",
                "properties": json.dumps({"support": {"type": "same_step_constraint"}}),
            }
        )
    with open(edges_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "type", "properties"])
        writer.writeheader()
        writer.writerow(
            {
                "source": "Step::a",
                "target": "Constraint::c",
                "type": "HAS_CONSTRAINT",
                "properties": json.dumps({"required_condition": {"name": "installed"}}),
            }
        )

    graph = load_procedural_graph(tmp_path)
    normalized = normalize_graph(graph)

    step = normalized["nodes"][0]
    constraint = normalized["nodes"][1]
    edge = normalized["edges"][0]
    assert step["props"]["args"] == ["base", "workspace"]
    assert json.loads(step["props"]["window"]) == [70.9, 71.2]
    assert json.loads(constraint["props"]["support"]) == {"type": "same_step_constraint"}
    assert json.loads(edge["props"]["required_condition"]) == {"name": "installed"}
    assert edge["props"]["edge_type"] == "HAS_CONSTRAINT"


def test_normalize_graph_carries_graph_metadata_to_nodes() -> None:
    normalized = normalize_graph(
        {
            "schema_version": "1.0",
            "graph_name": "procedural_reasoning_graph",
            "nodes": [{"id": "Step::s1", "type": "Step", "properties": {"step_id": "s1"}}],
            "edges": [],
        }
    )

    props = normalized["nodes"][0]["props"]
    assert props["graph_name"] == "procedural_reasoning_graph"
    assert props["schema_version"] == "1.0"
    assert props["node_type"] == "Step"
    assert props["prg_id"] == "Step::s1"


def test_rejects_unsafe_neo4j_identifiers() -> None:
    assert neo4j_identifier("HAS_CONSTRAINT") == "HAS_CONSTRAINT"
    with pytest.raises(ValueError):
        neo4j_identifier("Bad Label")


def test_import_cyphers_use_only_semantic_node_labels_and_graph_properties() -> None:
    assert "MERGE (n:Step {prg_id: r.id})" in node_import_cypher("Step")
    assert "ProceduralReasoningGraphNode" not in node_import_cypher("Step")
    assert "MATCH (a {graph_name: r.graph_name, prg_id: r.source})" in edge_import_cypher("DEPENDS_ON")
    assert "MATCH (b {graph_name: r.graph_name, prg_id: r.target})" in edge_import_cypher("DEPENDS_ON")
    assert "[rel:DEPENDS_ON" in edge_import_cypher("DEPENDS_ON")
    assert clear_graph_cypher() == "MATCH (n {graph_name: $graph_name}) DETACH DELETE n"
