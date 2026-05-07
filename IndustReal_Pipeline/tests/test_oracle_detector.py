from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.detector_rgb import run_detector_for_clip
from src.raw_cad_config import load_raw_cad_config


def test_oracle_detector_converts_state_labels_to_component_evidence(tmp_path: Path) -> None:
    cfg = load_raw_cad_config()
    clip_dir = tmp_path / "clip"
    clip_dir.mkdir()
    (clip_dir / "OD_labels.json").write_text(
        json.dumps(
            {
                "categories": [
                    {"id": 1, "name": "background"},
                    {"id": 2, "name": "10000000000"},
                ],
                "images": [{"id": 0, "file_name": "000000.jpg", "width": 64, "height": 48}],
                "annotations": [{"id": 1, "image_id": 0, "category_id": 2, "bbox": [1, 2, 10, 8]}],
            }
        )
    )
    (clip_dir / "PSR_labels_with_errors.csv").write_text(
        "000000.jpg,4,Incorrectly installed front chassis\n000000.jpg,6,Install front chassis pin\n"
    )
    manifest_df = pd.DataFrame(
        [
            {
                "clip": "clip",
                "frame_idx": 0,
                "frame_name": "000000.jpg",
                "timestamp_ns": 0,
                "rgb_path": str(tmp_path / "rgb.jpg"),
            }
        ]
    )
    part_catalog = {
        "components": [
            {
                "key": "base",
                "display_name": "base",
                "detector_group": "structures",
                "prompts": ["base"],
                "aliases": [],
            }
        ],
        "context_components": [],
        "detector_vocabulary": {},
    }
    state_catalog = {
        "states": [
            {"state_name": "background", "component_keys": []},
            {"state_name": "10000000000", "component_keys": ["base"]},
            {"state_name": "error_state", "component_keys": []},
        ]
    }
    records = run_detector_for_clip(
        manifest_df,
        clip_dir=clip_dir,
        part_catalog=part_catalog,
        state_catalog=state_catalog,
        cfg=cfg,
        backend="oracle_od",
    )
    assert records[0]["source_state_name"] == "10000000000"
    assert [step["id"] for step in records[0]["source_error_steps"]] == [4, 6]
    assert records[0]["detections"] == []

    cfg["detector"]["oracle_mode"] = "components_legacy"
    records = run_detector_for_clip(
        manifest_df,
        clip_dir=clip_dir,
        part_catalog=part_catalog,
        state_catalog=state_catalog,
        cfg=cfg,
        backend="oracle_od",
    )
    assert records[0]["detections"][0]["canonical_component"] == "base"
