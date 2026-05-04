"""Milestone 1 hardening tests.

Covers the 6 issues identified in the hardening pass:
  1. Raw detector label preserved in observation
  2. Debug overlay reads V2 bbox fields with _u_* fallback
  3. Run metadata written by script 01 (tested via run_metadata module)
  4. Vocabulary prompt wired to load_detector
  5. ignore_for_object_tracks filters observations before tracking
  6. apply_vocab=False prevents vocabulary from rejecting depth_blobs/yolo labels
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
import pandas as pd

from src.detectors.base import DetectionResult, load_detector
from src.detection_postprocess import postprocess_detections
from src.vocabulary import Vocabulary
from src.objects import make_observation, OBSERVATION_COLUMNS


# ── Helpers ───────────────────────────────────────────────────────────────────

def _det(label, score=0.8, x1=0, y1=0, x2=100, y2=100, source="grounding_dino"):
    return DetectionResult(
        raw_label=label, score=score,
        bbox_xyxy=(float(x1), float(y1), float(x2), float(y2)),
        source=source, model_id="test",
    )


def _lego_vocab():
    return Vocabulary.from_config({
        "object_vocabulary": {
            "red_lego": {"prompts": ["a red lego brick", "red lego"]},
            "blue_lego": {"prompts": ["a blue lego brick", "blue lego"]},
            "hand": {"prompts": ["hand"], "ignore_for_object_tracks": True},
        }
    })


# ── Fix 1: Raw label preserved ────────────────────────────────────────────────

def test_raw_label_preserved_after_canonicalization():
    """semantic_class = canonical, label = raw detector output."""
    obs = make_observation(
        frame_idx=0, timestamp_ns=0,
        semantic_class="red_lego",
        label="red lego blue lego",    # raw detector output
        x=0.0, y=0.0, z=1.0,
    )
    assert obs["semantic_class"] == "red_lego"
    assert obs["label"] == "red lego blue lego"


def test_make_observation_label_defaults_to_semantic_class():
    """When label is not supplied, it defaults to semantic_class (backward compat)."""
    obs = make_observation(
        frame_idx=0, timestamp_ns=0,
        semantic_class="blue_lego",
        x=0.0, y=0.0, z=1.0,
    )
    assert obs["label"] == "blue_lego"


def test_observation_label_is_in_schema():
    assert "label" in OBSERVATION_COLUMNS


# ── Fix 2: Debug overlay bbox fallback ───────────────────────────────────────

def test_draw_detections_uses_v2_bbox(tmp_path):
    """draw_detections_on_rgb should use bbox_x1/y1/x2/y2 when present."""
    from src.viz import draw_detections_on_rgb

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    detections = [
        {
            "semantic_class": "red_lego",
            "label": "red lego",
            "confidence": 0.85,
            "bbox_x1": 10.0, "bbox_y1": 20.0,
            "bbox_x2": 80.0, "bbox_y2": 60.0,
            # No _u_min etc. — forces V2 path
        }
    ]
    out = tmp_path / "overlay.png"
    draw_detections_on_rgb(rgb, detections, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_draw_detections_falls_back_to_legacy_keys(tmp_path):
    """draw_detections_on_rgb should fall back to _u_min/_v_min keys."""
    from src.viz import draw_detections_on_rgb

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    detections = [
        {
            "semantic_class": "blue_lego",
            "label": "blue lego",
            "confidence": 0.70,
            # Old-style private keys, no V2 bbox fields
            "_u_min": 50, "_v_min": 30, "_u_max": 150, "_v_max": 90,
        }
    ]
    out = tmp_path / "overlay_legacy.png"
    draw_detections_on_rgb(rgb, detections, out)
    assert out.exists()


def test_draw_detections_shows_raw_label_when_different(tmp_path):
    """Label shown as 'raw (canonical)' when they differ."""
    from src.viz import draw_detections_on_rgb
    import matplotlib
    matplotlib.use("Agg")

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    detections = [
        {
            "semantic_class": "red_lego",
            "label": "red lego blue lego",  # raw differs from sem_class
            "confidence": 0.75,
            "bbox_x1": 0.0, "bbox_y1": 0.0, "bbox_x2": 100.0, "bbox_y2": 100.0,
        }
    ]
    out = tmp_path / "overlay_raw.png"
    draw_detections_on_rgb(rgb, detections, out)
    assert out.exists()


# ── Fix 3: run_metadata module ────────────────────────────────────────────────

def test_run_metadata_save_load_roundtrip(tmp_path):
    from src.run_metadata import build_run_metadata, save_run_metadata, load_run_metadata

    cfg = {"session_id": "test", "observations_source": "grounding_dino"}
    thr = {"detection": {"depth_min_m": 0.1}}
    meta = build_run_metadata(
        session_id="test_session",
        stage="01_build_frame_manifest",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={"n_frames": 42},
    )
    path = save_run_metadata(tmp_path, meta)
    loaded = load_run_metadata(tmp_path, "01_build_frame_manifest")

    assert path.parent == tmp_path / "logs"
    assert path.name == "run_metadata_01_build_frame_manifest.json"
    assert loaded is not None
    assert loaded["session_id"] == "test_session"
    assert loaded["n_frames"] == 42
    assert loaded["pipeline_config_hash"] == meta["pipeline_config_hash"]


def test_run_metadata_loads_legacy_root_file(tmp_path):
    from src.run_metadata import build_run_metadata, load_run_metadata

    cfg = {"session_id": "test"}
    thr = {}
    meta = build_run_metadata("test_session", "01_build_frame_manifest", cfg, thr)
    legacy_path = tmp_path / "run_metadata_01_build_frame_manifest.json"
    legacy_path.write_text(json.dumps(meta))

    loaded = load_run_metadata(tmp_path, "01_build_frame_manifest")

    assert loaded is not None
    assert loaded["session_id"] == "test_session"


def test_staleness_detected_on_config_change(tmp_path):
    from src.run_metadata import (
        build_run_metadata, save_run_metadata,
        check_staleness, StalenessWarning,
    )

    cfg_v1 = {"session_id": "s", "detection_prompt": "red lego."}
    thr = {}
    meta = build_run_metadata("s", "01_build_frame_manifest", cfg_v1, thr)
    save_run_metadata(tmp_path, meta)

    # Run with different config
    cfg_v2 = {"session_id": "s", "detection_prompt": "blue lego."}
    warnings = check_staleness(tmp_path, "01_build_frame_manifest", cfg_v2, thr)
    assert len(warnings) == 1
    assert "pipeline_config_hash" in warnings[0].field


def test_no_staleness_when_config_unchanged(tmp_path):
    from src.run_metadata import build_run_metadata, save_run_metadata, check_staleness

    cfg = {"session_id": "s", "k": "v"}
    thr = {"tracking": {"max_spatial_jump_m": 0.8}}
    meta = build_run_metadata("s", "01_build_frame_manifest", cfg, thr)
    save_run_metadata(tmp_path, meta)

    warnings = check_staleness(tmp_path, "01_build_frame_manifest", cfg, thr)
    assert warnings == []


# ── Fix 4: Vocabulary prompt wired to load_detector ──────────────────────────

def test_load_detector_uses_supplied_prompt():
    from src.detectors.base import load_detector
    det = load_detector(
        "grounding_dino",
        cfg={"grounding_dino_model": "IDEA-Research/grounding-dino-base"},
        thr={"grounding_dino": {"box_threshold": 0.3, "text_threshold": 0.25}},
        prompt="a red lego brick. a blue lego brick.",
    )
    assert det.prompt == "a red lego brick. a blue lego brick."


def test_load_detector_falls_back_to_cfg_prompt():
    from src.detectors.base import load_detector
    det = load_detector(
        "grounding_dino",
        cfg={
            "grounding_dino_model": "IDEA-Research/grounding-dino-base",
            "detection_prompt": "fallback prompt.",
        },
        thr={"grounding_dino": {}},
        prompt=None,  # no override
    )
    assert det.prompt == "fallback prompt."


def test_vocabulary_build_prompt_matches_expected():
    v = _lego_vocab()
    prompt = v.build_prompt()
    # Should use first prompt from each entry, period-separated
    assert "a red lego brick" in prompt
    assert "a blue lego brick" in prompt


# ── Fix 5: ignore_for_object_tracks filters before tracking ──────────────────

def test_ignore_for_object_tracks_filtering():
    """Observations with ignore_for_object_tracks=True classes are excluded."""
    v = _lego_vocab()
    ignore_classes = {e.canonical for e in v._entries if e.ignore_for_object_tracks}
    assert "hand" in ignore_classes

    obs_df = pd.DataFrame([
        {"canonical_class": "red_lego",  "semantic_class": "red_lego",  "frame_idx": 0, "confidence": 0.8},
        {"canonical_class": "blue_lego", "semantic_class": "blue_lego", "frame_idx": 0, "confidence": 0.7},
        {"canonical_class": "hand",      "semantic_class": "hand",      "frame_idx": 0, "confidence": 0.9},
    ])

    # Simulate the filtering logic from script 06
    class_col = "canonical_class"
    filtered = obs_df[~obs_df[class_col].isin(ignore_classes)].reset_index(drop=True)

    assert len(filtered) == 2
    assert "hand" not in filtered["canonical_class"].values


def test_ignore_for_object_tracks_keeps_non_ignored():
    """Observations of tracked classes are not filtered out."""
    v = _lego_vocab()
    ignore_classes = {e.canonical for e in v._entries if e.ignore_for_object_tracks}

    obs_df = pd.DataFrame([
        {"canonical_class": "red_lego", "frame_idx": 0},
        {"canonical_class": "blue_lego", "frame_idx": 1},
    ])
    filtered = obs_df[~obs_df["canonical_class"].isin(ignore_classes)]
    assert len(filtered) == 2


# ── Fix 6: apply_vocab=False for depth_blobs/yolo ────────────────────────────

def test_depth_blobs_labels_not_rejected_by_lego_vocab():
    """depth_blobs labels (object, surface) must not be dropped by a Lego vocab."""
    v = _lego_vocab()
    dets = [
        _det("object",       0.6, source="depth_blobs"),
        _det("surface",      0.5, source="depth_blobs"),
        _det("small_object", 0.7, source="depth_blobs"),
    ]
    # With apply_vocab=False (as script 05 sets for depth_blobs)
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, apply_vocab=False)
    assert len(out) == 3
    # canonical_class should equal raw_label in permissive mode (order not guaranteed)
    canonical_classes = {d.metadata["canonical_class"] for d in out}
    assert canonical_classes == {"object", "surface", "small_object"}


def test_depth_blobs_labels_would_be_rejected_if_apply_vocab_true():
    """Sanity check: same labels ARE rejected when apply_vocab=True."""
    v = _lego_vocab()
    dets = [_det("object", 0.6, source="depth_blobs")]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, apply_vocab=True)
    assert len(out) == 0


def test_yolo_labels_not_rejected_by_lego_vocab():
    """YOLO COCO labels should pass through when apply_vocab=False."""
    v = _lego_vocab()
    dets = [
        _det("person",  0.9, source="yolo"),
        _det("cup",     0.7, source="yolo"),
        _det("laptop",  0.6, source="yolo"),
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, apply_vocab=False)
    assert len(out) == 3


def test_apply_vocab_true_still_accepts_known_labels():
    """apply_vocab=True keeps labels that are in the vocabulary."""
    v = _lego_vocab()
    dets = [
        _det("red lego",  0.8, source="grounding_dino"),
        _det("blue lego", 0.7, source="grounding_dino"),
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, apply_vocab=True)
    assert len(out) == 2
    canonicals = {d.metadata["canonical_class"] for d in out}
    assert canonicals == {"red_lego", "blue_lego"}
