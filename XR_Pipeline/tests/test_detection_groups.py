"""Tests for detection_groups.py — Phase 1 multi-pass detection."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.detection_groups import (
    parse_detection_groups,
    cross_pass_nms,
    _iou,
    _get_bbox,
)
from src.vocabulary import Vocabulary, VocabEntry


# ── Vocabulary fixtures ───────────────────────────────────────────────────────

def _make_vocab():
    """Full 3-class vocab: red_lego (workpiece), blue_lego (workpiece), hand (hand)."""
    return Vocabulary([
        VocabEntry(canonical="red_lego",  prompts=["red block"], object_role="workpiece"),
        VocabEntry(canonical="blue_lego", prompts=["blue block"], object_role="workpiece"),
        VocabEntry(canonical="hand",      prompts=["hand"],       object_role="hand"),
    ])


def _make_cfg_with_groups(**group_overrides):
    base = {
        "detection_groups": {
            "hands":      {"enabled": True,  "classes": ["hand"]},
            "workpieces": {"enabled": True,  "classes": ["red_lego", "blue_lego"]},
        }
    }
    base["detection_groups"].update(group_overrides)
    return base


# ── parse_detection_groups ────────────────────────────────────────────────────

def test_no_groups_returns_empty():
    vocab = _make_vocab()
    passes = parse_detection_groups({}, vocab)
    assert passes == []


def test_groups_parsed_count():
    vocab = _make_vocab()
    cfg = _make_cfg_with_groups()
    passes = parse_detection_groups(cfg, vocab)
    assert len(passes) == 2


def test_group_names():
    vocab = _make_vocab()
    cfg = _make_cfg_with_groups()
    passes = parse_detection_groups(cfg, vocab)
    names = [gp.group.name for gp in passes]
    assert "hands" in names
    assert "workpieces" in names


def test_disabled_group_excluded():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands":      {"enabled": False, "classes": ["hand"]},
        "workpieces": {"enabled": True,  "classes": ["red_lego", "blue_lego"]},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert len(passes) == 1
    assert passes[0].group.name == "workpieces"


def test_empty_classes_group_excluded():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "empty_group": {"enabled": True, "classes": []},
        "workpieces":  {"enabled": True, "classes": ["red_lego"]},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert len(passes) == 1
    assert passes[0].group.name == "workpieces"


def test_pass_ids_assigned():
    vocab = _make_vocab()
    cfg = _make_cfg_with_groups()
    passes = parse_detection_groups(cfg, vocab)
    pass_ids = [gp.group.pass_id for gp in passes]
    assert pass_ids == ["pass_00", "pass_01"]


def test_sub_vocab_contains_only_group_classes():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands": {"enabled": True, "classes": ["hand"]},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert len(passes) == 1
    sub_classes = passes[0].vocab.canonical_classes()
    assert sub_classes == ["hand"]


def test_prompt_built_from_sub_vocab():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands": {"enabled": True, "classes": ["hand"]},
    }}
    passes = parse_detection_groups(cfg, vocab)
    # Should contain "hand" prompt, not "red block" or "blue block"
    assert "hand" in passes[0].prompt
    assert "red" not in passes[0].prompt


def test_prompt_override_used():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands": {"enabled": True, "classes": ["hand"],
                  "prompt_override": "person's hand. fingers."},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert passes[0].prompt == "person's hand. fingers."


def test_unknown_class_warns(recwarn):
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "mystery": {"enabled": True, "classes": ["does_not_exist"]},
    }}
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        passes = parse_detection_groups(cfg, vocab)
        # Group is created but sub-vocab is empty → group has no entries
        assert len(passes) == 1  # group still parsed
        # Warning should have been raised
        assert any("does_not_exist" in str(warning.message) for warning in w)


# ── cross_pass_nms ────────────────────────────────────────────────────────────

def _make_obs(frame=0, cls="red_lego", conf=0.8, x1=10, y1=10, x2=60, y2=60,
              group="workpieces"):
    return {
        "frame_idx": frame, "canonical_class": cls, "semantic_class": cls,
        "confidence": conf,
        "bbox_x1": x1, "bbox_y1": y1, "bbox_x2": x2, "bbox_y2": y2,
        "detector_group": group,
    }


def test_no_duplicates_unchanged():
    obs_list = [
        _make_obs(frame=0, cls="red_lego",  conf=0.8, x1=10, y1=10, x2=50, y2=50, group="wp"),
        _make_obs(frame=0, cls="blue_lego", conf=0.7, x1=100, y1=100, x2=150, y2=150, group="wp"),
        _make_obs(frame=0, cls="hand",      conf=0.9, x1=200, y1=200, x2=260, y2=260, group="hands"),
    ]
    result = cross_pass_nms(obs_list, iou_threshold=0.5)
    assert len(result) == 3


def test_duplicate_high_iou_suppressed():
    # Two almost-identical red_lego boxes from different passes
    obs_list = [
        _make_obs(frame=0, cls="red_lego", conf=0.8, x1=10, y1=10, x2=60, y2=60, group="pass_a"),
        _make_obs(frame=0, cls="red_lego", conf=0.6, x1=12, y1=12, x2=62, y2=62, group="pass_b"),
    ]
    result = cross_pass_nms(obs_list, iou_threshold=0.5)
    # Lower-confidence duplicate should be suppressed
    assert len(result) == 1
    assert result[0]["confidence"] == 0.8


def test_different_classes_not_suppressed():
    obs_list = [
        _make_obs(frame=0, cls="red_lego", conf=0.8, x1=10, y1=10, x2=60, y2=60),
        _make_obs(frame=0, cls="hand",     conf=0.6, x1=10, y1=10, x2=60, y2=60),
    ]
    result = cross_pass_nms(obs_list, iou_threshold=0.5)
    # Different classes must never suppress each other
    assert len(result) == 2


def test_iou_zero_disables_nms():
    obs_list = [
        _make_obs(frame=0, cls="red_lego", conf=0.8, x1=10, y1=10, x2=60, y2=60),
        _make_obs(frame=0, cls="red_lego", conf=0.6, x1=10, y1=10, x2=60, y2=60),
    ]
    result = cross_pass_nms(obs_list, iou_threshold=0)
    assert len(result) == 2


def test_different_frames_not_suppressed():
    obs_list = [
        _make_obs(frame=0, cls="red_lego", conf=0.8, x1=10, y1=10, x2=60, y2=60),
        _make_obs(frame=1, cls="red_lego", conf=0.6, x1=10, y1=10, x2=60, y2=60),
    ]
    result = cross_pass_nms(obs_list, iou_threshold=0.5)
    assert len(result) == 2


# ── IoU helpers ───────────────────────────────────────────────────────────────

def test_iou_identical_boxes():
    assert _iou((0, 0, 10, 10), (0, 0, 10, 10)) == pytest.approx(1.0)


def test_iou_no_overlap():
    assert _iou((0, 0, 10, 10), (20, 20, 30, 30)) == pytest.approx(0.0)


def test_iou_partial_overlap():
    # Two 10x10 boxes overlapping by 5x5
    iou = _iou((0, 0, 10, 10), (5, 5, 15, 15))
    # intersection = 5*5 = 25; union = 100+100-25 = 175
    assert iou == pytest.approx(25 / 175, rel=1e-3)


def test_get_bbox_valid():
    obs = {"bbox_x1": 1.0, "bbox_y1": 2.0, "bbox_x2": 3.0, "bbox_y2": 4.0}
    assert _get_bbox(obs) == (1.0, 2.0, 3.0, 4.0)


def test_get_bbox_missing_returns_none():
    assert _get_bbox({"bbox_x1": 1.0}) is None


# ── Per-group thresholds ──────────────────────────────────────────────────────

def test_per_group_box_threshold_parsed():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands": {"enabled": True, "classes": ["hand"],
                  "box_threshold": 0.15, "text_threshold": 0.18},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert len(passes) == 1
    gp = passes[0]
    assert gp.box_threshold == pytest.approx(0.15)
    assert gp.text_threshold == pytest.approx(0.18)
    assert gp.group.box_threshold == pytest.approx(0.15)
    assert gp.group.text_threshold == pytest.approx(0.18)


def test_per_group_threshold_absent_is_none():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "workpieces": {"enabled": True, "classes": ["red_lego", "blue_lego"]},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert passes[0].box_threshold is None
    assert passes[0].text_threshold is None


def test_per_group_only_box_threshold():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands": {"enabled": True, "classes": ["hand"], "box_threshold": 0.20},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert passes[0].box_threshold == pytest.approx(0.20)
    assert passes[0].text_threshold is None


def test_per_group_thresholds_independent_across_groups():
    vocab = _make_vocab()
    cfg = {"detection_groups": {
        "hands":      {"enabled": True, "classes": ["hand"],
                       "box_threshold": 0.20, "text_threshold": 0.20},
        "workpieces": {"enabled": True, "classes": ["red_lego", "blue_lego"],
                       "box_threshold": 0.25, "text_threshold": 0.25},
    }}
    passes = parse_detection_groups(cfg, vocab)
    assert len(passes) == 2
    hand_pass = next(p for p in passes if p.group.name == "hands")
    wp_pass   = next(p for p in passes if p.group.name == "workpieces")
    assert hand_pass.box_threshold == pytest.approx(0.20)
    assert wp_pass.box_threshold   == pytest.approx(0.25)
