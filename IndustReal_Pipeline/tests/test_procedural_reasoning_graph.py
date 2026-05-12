import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.procedural_reasoning_graph import (
    ProceduralReasoningGraphInputs,
    build_procedural_reasoning_graph,
)


def test_builds_procedural_reasoning_graph_from_validation_records(tmp_path: Path) -> None:
    validations_path = tmp_path / "validation_records.jsonl"
    output_dir = tmp_path / "graph"
    _write_jsonl(
        validations_path,
        [
            {
                "schema_version": "thesis_layer4_validation.v1",
                "step_id": "s1",
                "source_event_id": "event_1",
                "index": 1,
                "status": "accepted",
                "confidence": 0.9,
                "conf": 0.9,
                "evidence_predicates": [
                    _predicate("p1", "s1", "hasAction", ["s1", "install"]),
                    _predicate("p2", "s1", "usesObject", ["s1", "base"]),
                    _predicate("p3", "s1", "isA", ["base", "Base"]),
                ],
                "evidence_constraints": [
                    _constraint("c1", "produces", "expected_effect", ["s1", "installed", "base", "workspace"])
                ],
                "produced_effects": [
                    _constraint("c1", "produces", "expected_effect", ["s1", "installed", "base", "workspace"])
                ],
                "supported_requirements": [],
                "missing_requirements": [],
                "dependency_support": [],
                "incompatibilities": [],
                "tool_requirements": [],
                "safety_requirements": [],
                "trace": {"predicate_evidence": [], "constraint_evidence": [], "dependency_evidence": []},
            },
            {
                "schema_version": "thesis_layer4_validation.v1",
                "step_id": "s2",
                "source_event_id": "event_2",
                "index": 2,
                "status": "uncertain",
                "confidence": 0.8,
                "conf": 0.8,
                "evidence_predicates": [
                    _predicate("p4", "s2", "hasAction", ["s2", "install"]),
                    _predicate("p5", "s2", "usesObject", ["s2", "bracket"]),
                ],
                "evidence_constraints": [
                    _constraint("c2", "requires", "inferred_precondition", ["s2", "installed", "base", "workspace"]),
                    _constraint("c3", "produces", "expected_effect", ["s2", "installed", "bracket", "base"]),
                ],
                "produced_effects": [
                    _constraint("c3", "produces", "expected_effect", ["s2", "installed", "bracket", "base"])
                ],
                "supported_requirements": [
                    {
                        **_constraint("c2", "requires", "inferred_precondition", ["s2", "installed", "base", "workspace"]),
                        "support": {
                            "type": "previous_produced_effect",
                            "constraint_id": "c1",
                            "step_id": "s1",
                            "args": ["s1", "installed", "base", "workspace"],
                            "condition": {"name": "installed", "args": ["base", "workspace"]},
                        },
                    }
                ],
                "missing_requirements": [],
                "dependency_support": [
                    {
                        "required_condition": {"name": "installed", "args": ["base", "workspace"]},
                        "supporting_effect": {
                            "type": "previous_produced_effect",
                            "constraint_id": "c1",
                            "step_id": "s1",
                            "args": ["s1", "installed", "base", "workspace"],
                            "condition": {"name": "installed", "args": ["base", "workspace"]},
                        },
                    }
                ],
                "incompatibilities": [],
                "tool_requirements": [],
                "safety_requirements": [],
                "trace": {"predicate_evidence": [], "constraint_evidence": [], "dependency_evidence": []},
            },
        ],
    )

    result = build_procedural_reasoning_graph(
        ProceduralReasoningGraphInputs(validations_path=validations_path, output_dir=output_dir)
    )

    graph = json.loads((output_dir / "procedural_reasoning_graph.json").read_text(encoding="utf-8"))
    assert graph["graph_name"] == "procedural_reasoning_graph"
    assert result["node_counts"]["Step"] == 2
    assert result["node_counts"]["Rule"] == 2
    assert result["edge_counts"]["NEXT"] == 1
    assert result["edge_counts"]["DEPENDS_ON"] == 1
    assert result["edge_counts"]["PRODUCES"] == 2
    assert result["edge_counts"]["REQUIRES"] == 1
    assert result["edge_counts"]["SUPPORTED_BY"] == 1
    assert result["step_status_counts"] == {"accepted": 1, "uncertain": 1}
    assert (output_dir / "procedural_reasoning_graph_nodes.csv").exists()
    assert (output_dir / "procedural_reasoning_graph_edges.csv").exists()


def _predicate(predicate_id: str, step_id: str, name: str, args: list[object]) -> dict[str, object]:
    return {
        "predicate_id": predicate_id,
        "step_id": step_id,
        "name": name,
        "args": args,
        "conf": 0.9,
        "source": {"type": "test", "file": "test.csv", "fields": ["a"]},
    }


def _constraint(constraint_id: str, name: str, kind: str, args: list[object]) -> dict[str, object]:
    return {
        "constraint_id": constraint_id,
        "name": name,
        "kind": kind,
        "args": args,
        "conf": 0.9,
        "rule_id": f"rule_{kind}",
        "support": {"type": "same_step_constraint", "notes": "Constraint observed in the step."},
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
