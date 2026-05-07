from __future__ import annotations

from src.cad_reasoner import reason_state_sequence, state_sequence_to_asd_frames
from src.raw_cad_config import load_raw_cad_config
from src.track2d import smooth_frame_evidence


def _toy_state_catalog() -> dict:
    component_order = [
        "base",
        "front_chassis",
        "front_chassis_pin",
        "rear_chassis",
        "short_rear_chassis",
        "front_rear_chassis_pin",
        "rear_rear_chassis_pin",
        "front_bracket",
        "front_bracket_screw",
        "front_wheel_assy",
        "rear_wheel_assy",
    ]
    return {
        "component_order": component_order,
        "states": [
            {"state_index": 0, "state_name": "background", "component_keys": []},
            {"state_index": 1, "state_name": "10000000000", "component_keys": ["base"]},
            {"state_index": 23, "state_name": "error_state", "component_keys": []},
        ],
        "transitions": {
            "background": ["background", "10000000000", "error_state"],
            "10000000000": ["10000000000", "background", "error_state"],
            "error_state": ["error_state", "background", "10000000000"],
        },
    }


def test_track_smoothing_and_reasoner_emit_legal_states() -> None:
    cfg = load_raw_cad_config()
    frames = [
        {
            "clip": "toy",
            "frame_idx": 0,
            "frame_name": "000000.jpg",
            "timestamp_ns": 0,
            "detections": [
                {
                    "raw_label": "base",
                    "canonical_component": "base",
                    "bbox_xyxy": [0.0, 0.0, 10.0, 10.0],
                    "confidence": 0.9,
                    "detector_group": "structures",
                    "backend": "oracle_od",
                }
            ],
        },
        {
            "clip": "toy",
            "frame_idx": 1,
            "frame_name": "000001.jpg",
            "timestamp_ns": 100_000_000,
            "detections": [
                {
                    "raw_label": "base",
                    "canonical_component": "base",
                    "bbox_xyxy": [0.0, 0.0, 10.0, 10.0],
                    "confidence": 0.4,
                    "detector_group": "structures",
                    "backend": "oracle_od",
                }
            ],
        },
    ]
    smoothed = smooth_frame_evidence(frames, iou_threshold=0.3, track_decay=0.8)
    assert smoothed[0]["detections"][0]["track_id"] == smoothed[1]["detections"][0]["track_id"]
    assert smoothed[1]["detections"][0]["smoothed_confidence"] > 0.4

    rows = reason_state_sequence(smoothed, state_catalog=_toy_state_catalog(), cfg=cfg)
    assert all(row["predicted_state"] in {"background", "10000000000", "error_state"} for row in rows)
    assert rows[0]["predicted_state"] == "10000000000"

    asd_frames = state_sequence_to_asd_frames(rows, state_catalog=_toy_state_catalog())
    assert asd_frames[0][0][0] == 1
