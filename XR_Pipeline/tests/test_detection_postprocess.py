"""Tests for src/detection_postprocess.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.detectors.base import DetectionResult
from src.detection_postprocess import postprocess_detections, _iou, _class_aware_nms
from src.vocabulary import Vocabulary


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _vocab():
    return Vocabulary.from_config({
        "object_vocabulary": {
            "red_lego": {"prompts": ["red lego"], "aliases": ["red lego blue lego"]},
            "blue_lego": {"prompts": ["blue lego"]},
        }
    })


def _det(label, score, x1=0, y1=0, x2=100, y2=100, source="grounding_dino"):
    return DetectionResult(
        raw_label=label, score=score,
        bbox_xyxy=(float(x1), float(y1), float(x2), float(y2)),
        source=source, model_id="test",
    )


# ── IoU ───────────────────────────────────────────────────────────────────────

def test_iou_perfect_overlap():
    assert abs(_iou((0, 0, 100, 100), (0, 0, 100, 100)) - 1.0) < 1e-6


def test_iou_no_overlap():
    assert _iou((0, 0, 50, 50), (60, 60, 110, 110)) == 0.0


def test_iou_partial_overlap():
    # 50x50 overlap, areas 100x100 each → IoU = 2500 / (10000 + 10000 - 2500) = 0.143
    iou = _iou((0, 0, 100, 100), (50, 50, 150, 150))
    assert 0.10 < iou < 0.20


def test_iou_contained_box():
    # Small box completely inside large box
    iou = _iou((0, 0, 100, 100), (25, 25, 75, 75))
    # intersection = 50*50 = 2500; union = 10000 + 2500 - 2500 = 10000
    assert abs(iou - 0.25) < 1e-6


# ── Vocabulary mapping ────────────────────────────────────────────────────────

def test_postprocess_maps_known_label():
    v = _vocab()
    dets = [_det("red lego", 0.8)]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0)
    assert len(out) == 1
    assert out[0].metadata["canonical_class"] == "red_lego"


def test_postprocess_maps_alias_label():
    v = _vocab()
    dets = [_det("red lego blue lego", 0.7)]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0)
    assert len(out) == 1
    assert out[0].metadata["canonical_class"] == "red_lego"


def test_postprocess_rejects_unknown_with_vocab():
    v = _vocab()
    dets = [_det("table", 0.9)]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0)
    assert len(out) == 0


def test_postprocess_permissive_passes_all():
    v = Vocabulary.from_config({})  # empty = permissive
    dets = [_det("anything", 0.6), _det("whatever", 0.4)]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0)
    assert len(out) == 2


# ── Confidence filter ─────────────────────────────────────────────────────────

def test_postprocess_confidence_filter():
    v = Vocabulary.from_config({})
    # Use spatially separated boxes so NMS doesn't suppress any of them;
    # we're testing confidence filtering only.
    dets = [
        _det("x", 0.8, x1=0,   y1=0,  x2=50,  y2=50),   # kept (≥0.4)
        _det("x", 0.2, x1=100, y1=100, x2=150, y2=150),  # dropped (<0.4)
        _det("x", 0.5, x1=200, y1=0,  x2=250, y2=50),    # kept (≥0.4)
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.4)
    assert len(out) == 2
    assert all(d.score >= 0.4 for d in out)


# ── Area filter ───────────────────────────────────────────────────────────────

def test_postprocess_area_filter():
    v = Vocabulary.from_config({})
    dets = [
        _det("x", 0.9, x1=0, y1=0, x2=100, y2=100),   # area = 10000
        _det("x", 0.8, x1=0, y1=0, x2=5, y2=5),        # area = 25
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, min_area_px=100)
    assert len(out) == 1
    assert out[0].score == 0.9


# ── NMS ───────────────────────────────────────────────────────────────────────

def test_class_aware_nms_suppresses_duplicate():
    v = Vocabulary.from_config({})
    # Two nearly identical boxes for same class — lower score should be suppressed
    dets = [
        _det("x", 0.9, x1=0, y1=0, x2=100, y2=100),
        _det("x", 0.5, x1=5, y1=5, x2=105, y2=105),
    ]
    # Manually set canonical so NMS grouping works
    for d in dets:
        d.metadata["canonical_class"] = "x"
    out = _class_aware_nms(dets, iou_threshold=0.5)
    assert len(out) == 1
    assert out[0].score == 0.9


def test_class_aware_nms_keeps_different_classes():
    v = Vocabulary.from_config({})
    dets = [
        _det("red", 0.9, x1=0, y1=0, x2=100, y2=100),
        _det("blue", 0.8, x1=0, y1=0, x2=100, y2=100),  # same box, different class
    ]
    dets[0].metadata["canonical_class"] = "red"
    dets[1].metadata["canonical_class"] = "blue"
    out = _class_aware_nms(dets, iou_threshold=0.5)
    assert len(out) == 2


def test_class_aware_nms_keeps_non_overlapping():
    v = Vocabulary.from_config({})
    dets = [
        _det("x", 0.9, x1=0,   y1=0,  x2=50, y2=50),
        _det("x", 0.8, x1=100, y1=100, x2=150, y2=150),  # no overlap
    ]
    for d in dets:
        d.metadata["canonical_class"] = "x"
    out = _class_aware_nms(dets, iou_threshold=0.5)
    assert len(out) == 2


def test_postprocess_nms_via_main_function():
    v = Vocabulary.from_config({})
    dets = [
        _det("a", 0.9, x1=0, y1=0, x2=100, y2=100),
        _det("a", 0.5, x1=2, y1=2, x2=102, y2=102),
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, nms_iou_threshold=0.5)
    assert len(out) == 1


def test_postprocess_nms_disabled():
    v = Vocabulary.from_config({})
    dets = [
        _det("a", 0.9, x1=0, y1=0, x2=100, y2=100),
        _det("a", 0.5, x1=2, y1=2, x2=102, y2=102),
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.0, nms_iou_threshold=0.0)
    assert len(out) == 2


# ── Combined pipeline ─────────────────────────────────────────────────────────

def test_postprocess_full_pipeline():
    v = _vocab()
    dets = [
        _det("red lego", 0.85, x1=0,  y1=0,  x2=80,  y2=80),   # kept
        _det("red lego", 0.40, x1=5,  y1=5,  x2=85,  y2=85),   # NMS suppressed
        _det("blue lego", 0.70, x1=200, y1=10, x2=280, y2=90),  # kept
        _det("table",    0.90, x1=0,  y1=0,  x2=640, y2=240),  # unknown → rejected
        _det("red lego", 0.15, x1=300, y1=300, x2=320, y2=320), # below conf_min
    ]
    out = postprocess_detections(dets, vocab=v, conf_min=0.3, nms_iou_threshold=0.5)
    labels = [d.metadata["canonical_class"] for d in out]
    assert "red_lego" in labels
    assert "blue_lego" in labels
    assert len([l for l in labels if l == "red_lego"]) == 1  # NMS kept only the best
