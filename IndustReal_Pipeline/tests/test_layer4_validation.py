import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.layer4_validation import Layer4Inputs, run_layer4_validation


def test_layer4_writes_thesis_records_and_uses_only_prior_effects_for_preconditions(tmp_path: Path) -> None:
    steps_path = tmp_path / "step_records.jsonl"
    predicates_path = tmp_path / "predicates.jsonl"
    constraints_path = tmp_path / "inferred_constraints.csv"
    config_path = tmp_path / "thesis_rules.yaml"
    output_path = tmp_path / "validation_records.jsonl"

    config_path.write_text(json.dumps({"validation": {"tau_acc": 0.7, "tau_unc": 0.35}}), encoding="utf-8")
    _write_jsonl(
        steps_path,
        [
            {"id": "s1", "index": 1},
            {"id": "s2", "index": 2},
            {"id": "s3", "index": 3},
            {"id": "s4", "index": 4},
        ],
    )
    _write_jsonl(
        predicates_path,
        [
            _predicate("p1", "s1", "hasAction", ["s1", "install"]),
            _predicate("p2", "s2", "hasAction", ["s2", "install"]),
            _predicate("p3", "s3", "hasAction", ["s3", "install"]),
            _predicate("p4", "s4", "hasAction", ["s4", "install"]),
            _predicate("p5", "s4", "usesTool", ["s4", "driver"]),
        ],
    )
    _write_constraints_csv(
        constraints_path,
        [
            _constraint("c1", "s1", "produces", "expected_effect", ["s1", "installed", "base", "workspace"]),
            _constraint("c2", "s2", "requires", "inferred_precondition", ["s2", "installed", "base", "workspace"]),
            _constraint("c3", "s2", "produces", "expected_effect", ["s2", "installed", "bracket", "base"]),
            _constraint("c4", "s3", "requires", "inferred_precondition", ["s3", "installed", "cover", "bracket"]),
            _constraint("c5", "s3", "produces", "expected_effect", ["s3", "installed", "cover", "bracket"]),
            _constraint("c6", "s4", "requires", "inferred_precondition", ["s4", "installed", "cover", "bracket"]),
            _constraint("c7", "s4", "requiresTool", "required_tool", ["s4", "driver"]),
        ],
    )

    result = run_layer4_validation(
        Layer4Inputs(
            step_records_path=steps_path,
            predicates_path=predicates_path,
            constraints_path=constraints_path,
            output_path=output_path,
            config_path=config_path,
        )
    )

    records = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    by_step = {record["step_id"]: record for record in records}
    assert result["validation_records"] == 4
    assert result["validation_config_path"] == str(config_path)
    assert result["tau_acc"] == 0.7
    assert result["tau_unc"] == 0.35
    assert (tmp_path / "step_validations.csv").exists()
    assert (tmp_path / "explanation_traces.json").exists()

    assert by_step["s2"]["status"] == "accepted"
    assert by_step["s2"]["dependency_support"] == [
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
    ]

    assert by_step["s3"]["status"] == "rejected"
    assert by_step["s3"]["missing_requirements"][0]["constraint_id"] == "c4"
    assert by_step["s3"]["missing_requirements"][0]["support"] is None
    assert by_step["s4"]["status"] == "uncertain"
    assert {item["constraint_id"] for item in by_step["s4"]["supported_requirements"]} == {"c7"}
    assert {item["constraint_id"] for item in by_step["s4"]["missing_requirements"]} == {"c6"}
    assert by_step["s1"]["evidence_constraints"][0]["support"] == {
        "type": "same_step_constraint",
        "notes": "Constraint observed in the step.",
    }

    traces = json.loads((tmp_path / "explanation_traces.json").read_text(encoding="utf-8"))
    trace = next(item for item in traces if item["step_id"] == "s2")
    assert set(trace) == {
        "step_id",
        "predicate_evidence",
        "constraint_evidence",
        "incompatibility_evidence",
        "dependency_evidence",
        "missing_requirements",
        "status",
        "confidence",
    }
    assert trace["dependency_evidence"] == by_step["s2"]["dependency_support"]
    assert trace["constraint_evidence"][0]["support"] == {
        "type": "same_step_constraint",
        "notes": "Constraint observed in the step.",
    }


def _predicate(predicate_id: str, step_id: str, name: str, args: list[str]) -> dict[str, object]:
    return {"id": predicate_id, "step_id": step_id, "name": name, "args": args, "conf": 0.9}


def _constraint(
    constraint_id: str,
    step_id: str,
    name: str,
    kind: str,
    args: list[str],
) -> dict[str, object]:
    return {
        "constraint_id": constraint_id,
        "step_id": step_id,
        "name": name,
        "kind": kind,
        "args": args,
        "conf": 0.9,
        "rule_id": "test_rule",
        "rule_type": kind,
        "threshold": 0.7,
        "aggregation": "min",
        "evidence_predicate_ids": [],
        "status": "inferred",
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _write_constraints_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "constraint_id",
        "step_id",
        "name",
        "kind",
        "args",
        "conf",
        "rule_id",
        "rule_type",
        "threshold",
        "aggregation",
        "evidence_predicate_ids",
        "status",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "args": json.dumps(row["args"]), "evidence_predicate_ids": "[]"})
