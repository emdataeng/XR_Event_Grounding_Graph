import json

import pandas as pd

from src.thesis_constraint_reasoner import run_layer3_reasoning


def test_inference_rules_use_active_fact_intersections_as_intervals():
    facts = pd.DataFrame([
        {
            "fact_id": "fact_holding",
            "predicate": "holding",
            "subject_id": "trk_hand",
            "object_id": "trk_red",
            "confidence": 0.8,
            "start_frame_idx": 1,
            "end_frame_idx": 3,
            "source_stage": "operations",
        },
        {
            "fact_id": "fact_near",
            "predicate": "near",
            "subject_id": "trk_red",
            "object_id": "trk_blue",
            "confidence": 0.7,
            "start_frame_idx": 2,
            "end_frame_idx": 4,
            "source_stage": "events",
        },
    ])
    rules = {
        "inference_rules": [
            {
                "id": "r_can_place",
                "threshold": 0.6,
                "when": [
                    {"predicate": "holding", "args": ["?agent", "?part"]},
                    {"predicate": "near", "args": ["?part", "?target"]},
                ],
                "infer": {
                    "name": "can_place",
                    "args": ["?part", "?target"],
                },
            }
        ]
    }

    result = run_layer3_reasoning(facts, {}, {}, rules)

    assert len(result.constraints) == 1
    row = result.constraints.iloc[0]
    assert row["name"] == "can_place"
    assert json.loads(row["args"]) == ["trk_red", "trk_blue"]
    assert row["conf"] == 0.7
    assert row["start_frame_idx"] == 2
    assert row["end_frame_idx"] == 3
    assert json.loads(row["supporting_predicates"]) == ["fact_holding", "fact_near"]
    assert result.incompatibilities.empty


def test_compatibility_rules_can_use_domain_and_scene_metadata():
    facts = pd.DataFrame([
        {
            "fact_id": "fact_touch",
            "predicate": "touching_candidate",
            "subject_id": "trk_hand",
            "object_id": "trk_blue",
            "confidence": 0.9,
            "start_frame_idx": 4,
            "end_frame_idx": 6,
            "source_stage": "events",
        },
    ])
    ssp = {
        "entities": [
            {"entity_id": "trk_hand", "entity_type": "object", "class_label": "hand"},
            {"entity_id": "trk_blue", "entity_type": "object", "class_label": "blue_lego"},
        ]
    }
    domain = {
        "object_classes": [
            {"canonical": "hand", "role": "hand"},
            {"canonical": "blue_lego", "role": "workpiece"},
        ]
    }
    rules = {
        "compatibility_rules": [
            {
                "id": "r_no_hand_target",
                "threshold": 0.5,
                "when": [
                    {"predicate": "touching_candidate", "args": ["?agent", "?part"]},
                    {"var": "?agent", "role": "hand"},
                    {"var": "?part", "role": "workpiece"},
                ],
                "incompatible": {
                    "name": "invalid_attach_target",
                    "action": "ATTACH",
                    "args": ["?agent", "?part"],
                    "reason": "hand cannot be attached as an assembly part",
                },
            }
        ]
    }

    result = run_layer3_reasoning(facts, ssp, domain, rules)

    assert result.constraints.empty
    assert len(result.incompatibilities) == 1
    row = result.incompatibilities.iloc[0]
    assert row["name"] == "invalid_attach_target"
    assert row["action"] == "ATTACH"
    assert json.loads(row["args"]) == ["trk_hand", "trk_blue"]
    assert row["conf"] == 0.9
    assert row["start_frame_idx"] == 4
    assert row["end_frame_idx"] == 6


def test_thesis_yaml_shape_constraint_rules_are_supported():
    facts = pd.DataFrame([
        {
            "fact_id": "fact_aligned",
            "predicate": "aligned",
            "subject_id": "peg_1",
            "object_id": "hole_1",
            "confidence": 0.8,
            "start_frame_idx": 10,
            "end_frame_idx": 12,
            "source_stage": "test",
        },
        {
            "fact_id": "fact_inside",
            "predicate": "inside",
            "subject_id": "peg_1",
            "object_id": "hole_1",
            "confidence": 0.7,
            "start_frame_idx": 11,
            "end_frame_idx": 12,
            "source_stage": "test",
        },
        {
            "fact_id": "fact_touching",
            "predicate": "touching",
            "subject_id": "peg_1",
            "object_id": "hole_1",
            "confidence": 0.9,
            "start_frame_idx": 11,
            "end_frame_idx": 13,
            "source_stage": "test",
        },
        {
            "fact_id": "fact_peg",
            "predicate": "isA",
            "subject_id": "peg_1",
            "object_id": "Peg",
            "confidence": 1.0,
            "start_frame_idx": 1,
            "end_frame_idx": 20,
            "source_stage": "test",
        },
        {
            "fact_id": "fact_hole",
            "predicate": "isA",
            "subject_id": "hole_1",
            "object_id": "Hole",
            "confidence": 1.0,
            "start_frame_idx": 1,
            "end_frame_idx": 20,
            "source_stage": "test",
        },
    ])
    rules = {
        "constraint_rules": [
            {
                "rule_id": "can_insert_peg_hole",
                "antecedents": [
                    {"name": "aligned", "args": ["?x", "?y"]},
                    {"name": "inside", "args": ["?x", "?y"]},
                    {"name": "touching", "args": ["?x", "?y"]},
                    {"name": "isA", "args": ["?x", "Peg"]},
                    {"name": "isA", "args": ["?y", "Hole"]},
                ],
                "consequents": [
                    {"name": "canInsert", "args": ["?x", "?y"]},
                ],
                "threshold": 0.6,
                "aggregation": "min",
            }
        ]
    }

    result = run_layer3_reasoning(facts, {}, {}, rules)

    assert len(result.constraints) == 1
    row = result.constraints.iloc[0]
    assert row["rule_id"] == "can_insert_peg_hole"
    assert row["name"] == "canInsert"
    assert json.loads(row["args"]) == ["peg_1", "hole_1"]
    assert row["conf"] == 0.7
    assert row["start_frame_idx"] == 11
    assert row["end_frame_idx"] == 12


def test_virtual_isa_conditions_use_domain_semantic_type_metadata():
    facts = pd.DataFrame([
        {
            "fact_id": "fact_near",
            "predicate": "near",
            "subject_id": "trk_blue",
            "object_id": "trk_red",
            "confidence": 0.7,
            "start_frame_idx": 3,
            "end_frame_idx": 4,
            "source_stage": "test",
        },
    ])
    ssp = {
        "entities": [
            {
                "entity_id": "trk_blue",
                "entity_type": "object",
                "class_label": "blue_lego",
                "existence_confidence": 0.54,
            },
            {
                "entity_id": "trk_red",
                "entity_type": "object",
                "class_label": "red_lego",
                "existence_confidence": 0.53,
            },
        ]
    }
    domain = {
        "object_classes": [
            {"canonical": "blue_lego", "semantic_type": "LegoBrick", "role": "workpiece"},
            {"canonical": "red_lego", "semantic_type": "LegoBrick", "role": "workpiece"},
        ]
    }
    rules = {
        "constraint_rules": [
            {
                "rule_id": "near_blue_red",
                "antecedents": [
                    {"name": "near", "args": ["?x", "?y"]},
                    {"name": "isA", "args": ["?x", "LegoBrick"]},
                    {"name": "isA", "args": ["?y", "LegoBrick"]},
                ],
                "consequents": [
                    {"name": "candidatePair", "args": ["?x", "?y"]},
                ],
                "threshold": 0.6,
            }
        ]
    }

    result = run_layer3_reasoning(facts, ssp, domain, rules)

    assert len(result.constraints) == 1
    row = result.constraints.iloc[0]
    assert row["name"] == "candidatePair"
    assert json.loads(row["args"]) == ["trk_blue", "trk_red"]
    assert row["conf"] == 0.7
    assert json.loads(row["supporting_predicates"]) == ["fact_near"]


def test_disallowed_pair_compatibility_rules_are_supported():
    facts = pd.DataFrame([
        {
            "fact_id": "fact_ball",
            "predicate": "isA",
            "subject_id": "obj_ball",
            "object_id": "Ball",
            "confidence": 1.0,
            "start_frame_idx": 3,
            "end_frame_idx": 5,
            "source_stage": "test",
        },
        {
            "fact_id": "fact_plate",
            "predicate": "isA",
            "subject_id": "obj_plate",
            "object_id": "Plate",
            "confidence": 1.0,
            "start_frame_idx": 4,
            "end_frame_idx": 6,
            "source_stage": "test",
        },
    ])
    rules = {
        "compatibility_rules": [
            {
                "rule_id": "disallow_insert_ball_plate",
                "action": "insert",
                "disallowed_pairs": [["Ball", "Plate"]],
                "output": {
                    "name": "incompatibleAction",
                    "args": ["?x", "?y", "insert"],
                },
                "confidence": 1.0,
                "reason": "Ball cannot be inserted into Plate",
            }
        ]
    }

    result = run_layer3_reasoning(facts, {}, {}, rules)

    assert len(result.incompatibilities) == 1
    row = result.incompatibilities.iloc[0]
    assert row["rule_id"] == "disallow_insert_ball_plate"
    assert row["name"] == "incompatibleAction"
    assert row["action"] == "insert"
    assert json.loads(row["args"]) == ["obj_ball", "obj_plate", "insert"]
    assert row["start_frame_idx"] == 4
    assert row["end_frame_idx"] == 5
