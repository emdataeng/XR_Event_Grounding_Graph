"""Tests for Phase 2 rich operation types in operation_events.py."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import pytest

from src.operation_events import detect_operation_events, _is_enabled, _empty_df


# ── Shared fixture helpers ────────────────────────────────────────────────────

def _thr_defaults():
    return {}  # use all _DEFAULTS


def _make_track(tid, role, frames, positions):
    rows = []
    for i, (f, (x, y, z)) in enumerate(zip(frames, positions)):
        rows.append({
            "track_id": tid,
            "observation_id": f"obs_{tid}_{i}",
            "frame_idx": f,
            "timestamp_ns": f * 100_000_000,
            "semantic_class": "obj",
            "object_role": role,
            "x": x, "y": y, "z": z,
            "w": 0.05, "h": 0.05, "d": 0.05,
        })
    return pd.DataFrame(rows)


def _make_event(eid, etype, tids, start, end):
    return {
        "event_id": eid,
        "event_type": etype,
        "primary_track_ids": json.dumps(tids),
        "start_frame_idx": start,
        "end_frame_idx": end,
        "start_ts_ns": start * 100_000_000,
        "end_ts_ns": end * 100_000_000,
        "confidence": 0.7,
    }


# ── _is_enabled ───────────────────────────────────────────────────────────────

def test_is_enabled_default_true():
    assert _is_enabled({}, "HOLD") is True
    assert _is_enabled({}, "APPROACH") is True


def test_is_enabled_can_be_disabled():
    thr = {"operation_events": {"enabled_operations": {"APPROACH": False}}}
    assert _is_enabled(thr, "APPROACH") is False


def test_is_enabled_unknown_op_true():
    assert _is_enabled({}, "FUTURE_OP_XYZ") is True


# ── APPROACH detection ────────────────────────────────────────────────────────

def _make_approaching_scenario():
    """Workpiece converges toward a fixture over 7 frames."""
    # Workpiece starts at 0.4m from fixture, ends at 0.05m
    frames = list(range(0, 7))
    wp_positions = [(0.4 - i * 0.05, 0.0, 1.0) for i in range(7)]
    fix_positions = [(0.0, 0.0, 1.0)] * 7
    tracks = pd.concat([
        _make_track("trk_wp",  "workpiece", frames, wp_positions),
        _make_track("trk_fix", "fixture",   frames, fix_positions),
    ])
    events = pd.DataFrame([])
    return tracks, events


def test_approach_detected():
    tracks, events = _make_approaching_scenario()
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    assert "APPROACH" in types


def test_approach_correct_tracks():
    tracks, events = _make_approaching_scenario()
    result = detect_operation_events(tracks, events, _thr_defaults())
    ap = result[result["operation_type"] == "APPROACH"].iloc[0]
    assert ap["object_track_id"] == "trk_wp"
    assert ap["secondary_track_id"] == "trk_fix"


def test_approach_disabled_by_toggle():
    tracks, events = _make_approaching_scenario()
    thr = {"operation_events": {"enabled_operations": {"APPROACH": False}}}
    result = detect_operation_events(tracks, events, thr)
    assert "APPROACH" not in result["operation_type"].tolist()


def test_no_approach_when_diverging():
    """If distance is increasing, APPROACH should NOT be emitted."""
    frames = list(range(0, 7))
    wp_positions = [(i * 0.05, 0.0, 1.0) for i in range(7)]  # moving away
    fix_positions = [(0.0, 0.0, 1.0)] * 7
    tracks = pd.concat([
        _make_track("trk_wp",  "workpiece", frames, wp_positions),
        _make_track("trk_fix", "fixture",   frames, fix_positions),
    ])
    events = pd.DataFrame([])
    result = detect_operation_events(tracks, events, _thr_defaults())
    assert "APPROACH" not in result["operation_type"].tolist()


def test_no_approach_without_fixture():
    """APPROACH requires fixture_tids — no fixture, no APPROACH."""
    frames = list(range(0, 7))
    wp_positions = [(0.4 - i * 0.05, 0.0, 1.0) for i in range(7)]
    tracks = _make_track("trk_wp", "workpiece", frames, wp_positions)
    events = pd.DataFrame([])
    result = detect_operation_events(tracks, events, _thr_defaults())
    assert "APPROACH" not in result["operation_type"].tolist()


# ── PLACE_ONTO_CANDIDATE detection ───────────────────────────────────────────

def _make_placement_scenario(final_dist=0.10):
    """Workpiece moves and ends up near fixture."""
    frames = [0, 5, 10]
    fix_pos = (0.0, 0.0, 1.0)
    wp_positions = [(0.5, 0.0, 1.0), (0.3, 0.0, 1.0), (final_dist, 0.0, 1.0)]
    tracks = pd.concat([
        _make_track("trk_wp",  "workpiece", frames, wp_positions),
        _make_track("trk_fix", "fixture",   frames, [fix_pos] * 3),
    ])
    events = pd.DataFrame([
        _make_event("evt_move1", "MOVE", ["trk_wp"], 0, 10),
    ])
    return tracks, events


def test_place_onto_candidate_detected():
    tracks, events = _make_placement_scenario(final_dist=0.10)
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    # 0.10m is within placement_proximity_m (0.15) but beyond align/contact thresholds
    assert "PLACE_ONTO_CANDIDATE" in types


def test_insert_candidate_at_contact_range():
    """dist between align_tol (0.05) and contact_thr (0.08) → INSERT_CANDIDATE."""
    # 0.06 > align_tol (0.05) and 0.06 ≤ contact_thr (0.08) → INSERT_CANDIDATE
    tracks, events = _make_placement_scenario(final_dist=0.06)
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    assert "INSERT_CANDIDATE" in types
    assert "PLACE_ONTO_CANDIDATE" not in types
    assert "ALIGN_CANDIDATE" not in types


def test_align_candidate_at_align_range():
    """dist ≤ align_tolerance_m (0.05) → ALIGN_CANDIDATE (tightest threshold)."""
    # align_tol=0.05; dist=0.04 ≤ 0.05 → ALIGN_CANDIDATE
    tracks, events = _make_placement_scenario(final_dist=0.04)
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    assert "ALIGN_CANDIDATE" in types
    assert "INSERT_CANDIDATE" not in types


def test_placement_disabled_by_toggle():
    tracks, events = _make_placement_scenario(final_dist=0.10)
    thr = {"operation_events": {"enabled_operations": {
        "PLACE_ONTO_CANDIDATE": False,
        "INSERT_CANDIDATE": False,
        "ALIGN_CANDIDATE": False,
    }}}
    result = detect_operation_events(tracks, events, thr)
    for op in ("PLACE_ONTO_CANDIDATE", "INSERT_CANDIDATE", "ALIGN_CANDIDATE"):
        assert op not in result["operation_type"].tolist()


def test_no_placement_when_far():
    """Endpoint > placement_proximity_m → no placement candidates."""
    tracks, events = _make_placement_scenario(final_dist=0.30)
    result = detect_operation_events(tracks, events, _thr_defaults())
    for op in ("PLACE_ONTO_CANDIDATE", "INSERT_CANDIDATE", "ALIGN_CANDIDATE"):
        assert op not in result["operation_type"].tolist()


# ── ATTACH_CANDIDATE detection ────────────────────────────────────────────────

def _make_attach_scenario(duration=10):
    """Workpiece moves, then has sustained CO_LOCATE with fixture."""
    frames = list(range(0, 20))
    wp_positions = [(0.5, 0.0, 1.0)] * 5 + [(0.05, 0.0, 1.0)] * 15
    fix_positions = [(0.0, 0.0, 1.0)] * 20
    tracks = pd.concat([
        _make_track("trk_wp",  "workpiece", frames, wp_positions),
        _make_track("trk_fix", "fixture",   frames, fix_positions),
    ])
    events = pd.DataFrame([
        _make_event("evt_move1",  "MOVE",      ["trk_wp"],           0, 5),
        _make_event("evt_coloc1", "CO_LOCATE", ["trk_wp", "trk_fix"], 5, 5 + duration),
    ])
    return tracks, events


def test_attach_candidate_detected():
    tracks, events = _make_attach_scenario(duration=10)
    result = detect_operation_events(tracks, events, _thr_defaults())
    assert "ATTACH_CANDIDATE" in result["operation_type"].tolist()


def test_attach_candidate_needs_prior_move():
    """CO_LOCATE without a prior MOVE should NOT emit ATTACH_CANDIDATE."""
    frames = list(range(0, 20))
    wp_positions = [(0.05, 0.0, 1.0)] * 20
    fix_positions = [(0.0, 0.0, 1.0)] * 20
    tracks = pd.concat([
        _make_track("trk_wp",  "workpiece", frames, wp_positions),
        _make_track("trk_fix", "fixture",   frames, fix_positions),
    ])
    events = pd.DataFrame([
        # CO_LOCATE but NO preceding MOVE
        _make_event("evt_coloc1", "CO_LOCATE", ["trk_wp", "trk_fix"], 5, 15),
    ])
    result = detect_operation_events(tracks, events, _thr_defaults())
    assert "ATTACH_CANDIDATE" not in result["operation_type"].tolist()


def test_attach_candidate_needs_min_frames():
    """CO_LOCATE shorter than attachment_min_frames (8) should not emit."""
    tracks, events = _make_attach_scenario(duration=4)
    result = detect_operation_events(tracks, events, _thr_defaults())
    assert "ATTACH_CANDIDATE" not in result["operation_type"].tolist()


def test_attach_disabled_by_toggle():
    tracks, events = _make_attach_scenario(duration=10)
    thr = {"operation_events": {"enabled_operations": {"ATTACH_CANDIDATE": False}}}
    result = detect_operation_events(tracks, events, thr)
    assert "ATTACH_CANDIDATE" not in result["operation_type"].tolist()


# ── Existing operations still work with new toggle infra ─────────────────────

def test_hold_still_detected_with_toggles():
    """Verify HOLD still works when we only disable new ops."""
    frames = list(range(0, 10))
    wp_positions = [(0.0, 0.0, 1.0)] * 10
    hand_positions = [(0.05, 0.0, 1.0)] * 10
    tracks = pd.concat([
        _make_track("trk_wp",   "workpiece", frames, wp_positions),
        _make_track("trk_hand", "hand",      frames, hand_positions),
    ])
    events = pd.DataFrame([
        _make_event("evt_int1", "INTERACTION", ["trk_hand", "trk_wp"], 0, 8),
    ])
    thr = {"operation_events": {"enabled_operations": {
        "APPROACH": False, "PLACE_ONTO_CANDIDATE": False,
    }}}
    result = detect_operation_events(tracks, events, thr)
    assert "HOLD" in result["operation_type"].tolist()


def test_contact_disabled():
    """CONTACT can be disabled by toggle."""
    frames = [0, 1, 2]
    positions_a = [(0.0, 0.0, 1.0)] * 3
    positions_b = [(0.03, 0.0, 1.0)] * 3
    tracks = pd.concat([
        _make_track("trk_a", "workpiece", frames, positions_a),
        _make_track("trk_b", "fixture",   frames, positions_b),
    ])
    events = pd.DataFrame([
        _make_event("evt_co1", "CO_LOCATE", ["trk_a", "trk_b"], 0, 2),
    ])
    thr = {"operation_events": {"enabled_operations": {"CONTACT": False}}}
    result = detect_operation_events(tracks, events, thr)
    assert "CONTACT" not in result["operation_type"].tolist()
