from __future__ import annotations

import json
from pathlib import Path

from src.cad_reasoner import (
    direct_transition_steps_from_state_sequence,
    filter_steps_to_scored_slice,
    oracle_state_sequence_from_labels,
)


def _write_od_labels(path: Path) -> None:
    payload = {
        "categories": [
            {"id": 1, "name": "background"},
            {"id": 2, "name": "10000000000"},
            {"id": 3, "name": "11100000000"},
        ],
        "images": [
            {"id": 0, "file_name": "000000.jpg", "width": 64, "height": 48},
            {"id": 1, "file_name": "000070.jpg", "width": 64, "height": 48},
            {"id": 2, "file_name": "000090.jpg", "width": 64, "height": 48},
        ],
        "annotations": [
            {"id": 1, "image_id": 0, "category_id": 1, "bbox": [0, 0, 1, 1]},
            {"id": 2, "image_id": 1, "category_id": 2, "bbox": [0, 0, 1, 1]},
            {"id": 3, "image_id": 2, "category_id": 3, "bbox": [0, 0, 1, 1]},
        ],
    }
    path.write_text(json.dumps(payload))


def _write_error_step_labels(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "000085.jpg,4,Incorrectly installed front chassis",
                "000085.jpg,6,Install front chassis pin",
            ]
        )
        + "\n"
    )


def _state_catalog() -> dict:
    return {
        "states": [
            {"state_name": "background", "component_keys": []},
            {"state_name": "10000000000", "component_keys": ["base"]},
            {"state_name": "11100000000", "component_keys": ["base", "front_chassis", "front_chassis_pin"]},
            {"state_name": "error_state", "component_keys": []},
        ]
    }


def test_oracle_state_sequence_seeds_until_first_observed_label(tmp_path: Path) -> None:
    clip_dir = tmp_path / "clip"
    clip_dir.mkdir()
    _write_od_labels(clip_dir / "OD_labels.json")
    manifest_rows = [
        {"clip": "clip", "frame_idx": 50, "frame_name": "000050.jpg"},
        {"clip": "clip", "frame_idx": 60, "frame_name": "000060.jpg"},
        {"clip": "clip", "frame_idx": 70, "frame_name": "000070.jpg"},
        {"clip": "clip", "frame_idx": 80, "frame_name": "000080.jpg"},
        {"clip": "clip", "frame_idx": 90, "frame_name": "000090.jpg"},
    ]
    rows = oracle_state_sequence_from_labels(
        manifest_rows,
        clip_dir=clip_dir,
        state_catalog=_state_catalog(),
    )
    assert rows[0]["predicted_state"] == "10000000000"
    assert rows[0]["state_origin"] == "seeded_initial_state"
    assert rows[2]["state_origin"] == "observed_label"
    assert rows[3]["state_origin"] == "carried_forward_state"


def test_filter_steps_to_scored_slice_drops_seeded_context(tmp_path: Path) -> None:
    clip_dir = tmp_path / "clip"
    clip_dir.mkdir()
    _write_od_labels(clip_dir / "OD_labels.json")
    manifest_rows = [
        {"clip": "clip", "frame_idx": 50, "frame_name": "000050.jpg"},
        {"clip": "clip", "frame_idx": 60, "frame_name": "000060.jpg"},
        {"clip": "clip", "frame_idx": 70, "frame_name": "000070.jpg"},
    ]
    state_rows = oracle_state_sequence_from_labels(
        manifest_rows,
        clip_dir=clip_dir,
        state_catalog=_state_catalog(),
    )
    gt_steps = [
        {"frame": 60, "id": 0, "description": "Install base", "conf": 1.0},
        {"frame": 70, "id": 0, "description": "Install base", "conf": 1.0},
    ]
    filtered, score_start = filter_steps_to_scored_slice(gt_steps, state_rows=state_rows)
    assert score_start == 70
    assert [row["frame"] for row in filtered] == [70]


def test_direct_transition_steps_export_observed_changes() -> None:
    rows = [
        {
            "frame_idx": 50,
            "predicted_state": "10000000000",
            "state_origin": "seeded_initial_state",
        },
        {
            "frame_idx": 70,
            "predicted_state": "10000000000",
            "state_origin": "observed_label",
        },
        {
            "frame_idx": 90,
            "predicted_state": "11100000000",
            "state_origin": "observed_label",
        },
    ]
    proc_info = json.loads((Path(__file__).resolve().parent.parent / "configs" / "procedure_info.json").read_text())
    steps = direct_transition_steps_from_state_sequence(rows, proc_info=proc_info)
    assert [step["id"] for step in steps] == [3, 6]


def test_oracle_state_sequence_marks_explicit_error_frames(tmp_path: Path) -> None:
    clip_dir = tmp_path / "clip"
    clip_dir.mkdir()
    _write_od_labels(clip_dir / "OD_labels.json")
    _write_error_step_labels(clip_dir / "PSR_labels_with_errors.csv")
    manifest_rows = [
        {"clip": "clip", "frame_idx": 80, "frame_name": "000080.jpg"},
        {"clip": "clip", "frame_idx": 85, "frame_name": "000085.jpg"},
        {"clip": "clip", "frame_idx": 90, "frame_name": "000090.jpg"},
    ]
    rows = oracle_state_sequence_from_labels(
        manifest_rows,
        clip_dir=clip_dir,
        state_catalog=_state_catalog(),
    )
    assert rows[1]["predicted_state"] == "error_state"
    assert rows[1]["state_origin"] == "inferred_error_state"
    assert "explicit_error_step_label" in json.loads(rows[1]["reason_flags"])
    hints = json.loads(rows[1]["oracle_step_hints"])
    assert [hint["id"] for hint in hints] == [4, 6]
    assert rows[2]["predicted_state"] == "11100000000"


def test_direct_transition_steps_include_oracle_error_hints() -> None:
    rows = [
        {
            "frame_idx": 80,
            "predicted_state": "10000000000",
            "state_origin": "carried_forward_state",
            "oracle_step_hints": "[]",
        },
        {
            "frame_idx": 85,
            "predicted_state": "error_state",
            "state_origin": "inferred_error_state",
            "oracle_step_hints": json.dumps(
                [
                    {"frame": 85, "id": 4, "description": "Incorrectly installed front chassis", "conf": 1.0},
                    {"frame": 85, "id": 6, "description": "Install front chassis pin", "conf": 1.0},
                ]
            ),
        },
        {
            "frame_idx": 90,
            "predicted_state": "11100000000",
            "state_origin": "observed_label",
            "oracle_step_hints": "[]",
        },
    ]
    proc_info = json.loads((Path(__file__).resolve().parent.parent / "configs" / "procedure_info.json").read_text())
    steps = direct_transition_steps_from_state_sequence(rows, proc_info=proc_info)
    assert [(step["frame"], step["id"]) for step in steps] == [(85, 4), (85, 6)]
