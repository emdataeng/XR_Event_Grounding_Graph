"""Tests for src/detectors/mm_grounding_dino.py — MM-Grounding-DINO backend.

All tests mock out the HuggingFace model loading so no GPU or internet access
is required.  We test:
  - Detector construction and default values
  - Phrase-list → dot-separated prompt conversion
  - Factory loading via load_detector (including config key routing)
  - DetectionResult field contract (source, model_id, bbox_space, raw_label)
  - Postprocessing integration (apply_vocab=True for open-vocab backends)
  - Vocabulary prompt auto-resolution produces correct prompt for MM-GDINO
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from src.detectors.base import DetectionResult, load_detector
from src.detectors.mm_grounding_dino import MMGroundingDINODetector
from src.detection_postprocess import postprocess_detections
from src.vocabulary import Vocabulary


# ── Construction & defaults ───────────────────────────────────────────────────

def test_default_model_id():
    det = MMGroundingDINODetector()
    assert det.model_id == MMGroundingDINODetector.DEFAULT_MODEL
    assert "mm_grounding_dino" in det.model_id


def test_source_name():
    det = MMGroundingDINODetector()
    assert det.source == "mm_grounding_dino"


def test_prompt_stored_from_string():
    det = MMGroundingDINODetector(prompt="a red lego brick. a blue lego brick.")
    assert det.prompt == "a red lego brick. a blue lego brick."


def test_phrases_override_prompt():
    """When phrases list supplied, it should be joined into dot-separated prompt."""
    det = MMGroundingDINODetector(
        phrases=["a red lego brick", "a blue lego brick"]
    )
    # Both phrases must appear; prompt must end with "."
    assert "a red lego brick" in det.prompt
    assert "a blue lego brick" in det.prompt
    assert det.prompt.endswith(".")


def test_phrases_strips_extra_periods():
    """Phrases with trailing periods should not produce double-period artifacts."""
    det = MMGroundingDINODetector(phrases=["red lego.", "blue lego."])
    # Should NOT have ".." anywhere
    assert ".." not in det.prompt


def test_empty_phrases_falls_back_to_prompt():
    """Empty phrases list should behave as if phrases=None."""
    det = MMGroundingDINODetector(prompt="fallback.", phrases=[])
    assert det.prompt == "fallback."


def test_thresholds_stored():
    det = MMGroundingDINODetector(box_threshold=0.15, text_threshold=0.18)
    assert det.box_threshold == 0.15
    assert det.text_threshold == 0.18


# ── Factory: load_detector routing ───────────────────────────────────────────

def test_factory_creates_mm_grounding_dino():
    cfg = {"mm_grounding_dino_model": "openmmlab-community/mm_grounding_dino_base_all"}
    thr = {"mm_grounding_dino": {"box_threshold": 0.20, "text_threshold": 0.20}}
    det = load_detector("mm_grounding_dino", cfg, thr)
    assert isinstance(det, MMGroundingDINODetector)
    assert det.source == "mm_grounding_dino"


def test_factory_uses_default_model_when_not_in_cfg():
    det = load_detector("mm_grounding_dino", {}, {})
    assert isinstance(det, MMGroundingDINODetector)
    assert det.model_id == MMGroundingDINODetector.DEFAULT_MODEL


def test_factory_uses_custom_model_id():
    cfg = {"mm_grounding_dino_model": "custom/model"}
    det = load_detector("mm_grounding_dino", cfg, {})
    assert det.model_id == "custom/model"


def test_factory_applies_thresholds():
    thr = {"mm_grounding_dino": {"box_threshold": 0.10, "text_threshold": 0.12}}
    det = load_detector("mm_grounding_dino", {}, thr)
    assert det.box_threshold == 0.10
    assert det.text_threshold == 0.12


def test_factory_applies_prompt_override():
    det = load_detector("mm_grounding_dino", {}, {}, prompt="a red lego brick.")
    assert det.prompt == "a red lego brick."


def test_factory_falls_back_to_cfg_prompt():
    cfg = {"detection_prompt": "lego block."}
    det = load_detector("mm_grounding_dino", cfg, {})
    assert det.prompt == "lego block."


# ── detect() via mock model ───────────────────────────────────────────────────

def _make_mock_outputs(boxes_xyxy, labels, scores):
    """Build mock transformers processor/model outputs."""
    import torch
    mock_outputs = MagicMock()

    # processor.post_process_grounded_object_detection returns list of dicts
    result = {
        "boxes": torch.tensor(boxes_xyxy, dtype=torch.float32),
        "text_labels": labels,
        "scores": torch.tensor(scores, dtype=torch.float32),
    }
    return mock_outputs, [result]


def test_detect_returns_detection_results():
    det = MMGroundingDINODetector(prompt="red lego. blue lego.")
    det._device = "cpu"

    mock_outputs, mock_results = _make_mock_outputs(
        [[10, 20, 60, 80], [100, 50, 200, 150]],
        ["red lego", "blue lego"],
        [0.85, 0.72],
    )

    mock_model = MagicMock(return_value=mock_outputs)
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": MagicMock()}
    mock_processor.post_process_grounded_object_detection.return_value = mock_results

    det._model = mock_model
    det._processor = mock_processor

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb)

    assert len(results) == 2
    assert all(isinstance(r, DetectionResult) for r in results)


def test_detect_source_and_model_id():
    det = MMGroundingDINODetector(
        model_id="openmmlab-community/mm_grounding_dino_base_all",
        prompt="red lego.",
    )
    det._device = "cpu"

    mock_outputs, mock_results = _make_mock_outputs(
        [[0, 0, 50, 50]], ["red lego"], [0.9]
    )
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": MagicMock()}
    mock_processor.post_process_grounded_object_detection.return_value = mock_results

    det._model = MagicMock(return_value=mock_outputs)
    det._processor = mock_processor

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb)

    assert results[0].source == "mm_grounding_dino"
    assert results[0].model_id == "openmmlab-community/mm_grounding_dino_base_all"


def test_detect_bbox_space_is_rgb():
    det = MMGroundingDINODetector(prompt="lego.")
    det._device = "cpu"

    mock_outputs, mock_results = _make_mock_outputs(
        [[5, 5, 50, 50]], ["lego"], [0.8]
    )
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": MagicMock()}
    mock_processor.post_process_grounded_object_detection.return_value = mock_results

    det._model = MagicMock(return_value=mock_outputs)
    det._processor = mock_processor

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb)

    assert results[0].metadata["bbox_space"] == "rgb"


def test_detect_raw_label_strips_trailing_period():
    """Detector should strip trailing '.' from labels the model emits."""
    det = MMGroundingDINODetector(prompt="red lego.")
    det._device = "cpu"

    mock_outputs, mock_results = _make_mock_outputs(
        [[0, 0, 50, 50]], ["red lego."], [0.9]
    )
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": MagicMock()}
    mock_processor.post_process_grounded_object_detection.return_value = mock_results

    det._model = MagicMock(return_value=mock_outputs)
    det._processor = mock_processor

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb)

    assert results[0].raw_label == "red lego"


def test_detect_empty_result():
    det = MMGroundingDINODetector(prompt="nothing.")
    det._device = "cpu"

    mock_outputs = MagicMock()
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": MagicMock()}
    mock_processor.post_process_grounded_object_detection.return_value = []

    det._model = MagicMock(return_value=mock_outputs)
    det._processor = mock_processor

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    assert det.detect(rgb) == []


def test_detect_prompt_stored_on_result():
    det = MMGroundingDINODetector(prompt="red lego. blue lego.")
    det._device = "cpu"

    mock_outputs, mock_results = _make_mock_outputs(
        [[0, 0, 50, 50]], ["red lego"], [0.88]
    )
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": MagicMock()}
    mock_processor.post_process_grounded_object_detection.return_value = mock_results

    det._model = MagicMock(return_value=mock_outputs)
    det._processor = mock_processor

    rgb = np.zeros((240, 640, 3), dtype=np.uint8)
    results = det.detect(rgb)

    assert results[0].prompt == "red lego. blue lego."


# ── Postprocessing with mm_grounding_dino source ──────────────────────────────

def _mm_det(label, score, x1=0, y1=0, x2=100, y2=100):
    return DetectionResult(
        raw_label=label, score=score,
        bbox_xyxy=(x1, y1, x2, y2),
        source="mm_grounding_dino",
        model_id="openmmlab-community/mm_grounding_dino_base_all",
        prompt="red lego. blue lego.",
        metadata={"bbox_space": "rgb"},
    )


def test_postprocess_apply_vocab_true_for_mm_gdino():
    """mm_grounding_dino is an open-vocab backend; vocabulary rejection applies."""
    vocab = Vocabulary.from_config({"object_vocabulary": {
        "red_lego": {"prompts": ["red lego"], "aliases": []},
        "blue_lego": {"prompts": ["blue lego"], "aliases": []},
    }})
    dets = [
        _mm_det("red lego", 0.85, x1=0,   y1=0,  x2=100, y2=100),
        _mm_det("unknown thing", 0.80, x1=200, y1=0, x2=300, y2=100),
    ]
    out = postprocess_detections(dets, vocab, apply_vocab=True)
    canonical_classes = {d.metadata["canonical_class"] for d in out}
    # "unknown thing" should be rejected; "red lego" kept as red_lego
    assert "red_lego" in canonical_classes
    assert len(out) == 1


def test_postprocess_nms_removes_duplicate_for_mm_gdino():
    """Class-aware NMS should deduplicate overlapping same-class boxes."""
    vocab = Vocabulary.from_config({"object_vocabulary": {
        "red_lego": {"prompts": ["red lego"], "aliases": []},
    }})
    dets = [
        _mm_det("red lego", 0.90, x1=0,  y1=0,  x2=100, y2=100),
        _mm_det("red lego", 0.70, x1=10, y1=10, x2=110, y2=110),  # high IoU
    ]
    out = postprocess_detections(dets, vocab, nms_iou_threshold=0.5, apply_vocab=True)
    assert len(out) == 1
    assert out[0].score == 0.90


def test_postprocess_empty_vocab_passthrough_for_mm_gdino():
    """Empty vocabulary → every label passes (permissive mode)."""
    vocab = Vocabulary.from_config({"object_vocabulary": {}})
    dets = [
        _mm_det("widget", 0.75, x1=0,   y1=0,  x2=50, y2=50),
        _mm_det("gadget", 0.60, x1=100, y1=0,  x2=150, y2=50),
    ]
    out = postprocess_detections(dets, vocab, apply_vocab=True)
    assert len(out) == 2


# ── Vocabulary prompt auto-resolution ────────────────────────────────────────

def test_vocab_build_prompt_compatible_with_mm_gdino():
    """Prompt generated by Vocabulary.build_prompt() is usable as MM-GDINO input."""
    vocab = Vocabulary.from_config({"object_vocabulary": {
        "red_lego":  {"prompts": ["a red lego brick", "red lego"], "aliases": []},
        "blue_lego": {"prompts": ["a blue lego brick", "blue lego"], "aliases": []},
    }})
    prompt = vocab.build_prompt(separator=". ")
    det = MMGroundingDINODetector(prompt=prompt)
    # The prompt should be a non-empty string with the first phrase from each entry
    assert len(prompt) > 0
    assert det.prompt == prompt
