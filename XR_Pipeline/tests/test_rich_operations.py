"""Tests for Phase 2 rich operation types in operation_events.py."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import pytest

from src.operation_events import detect_operation_events, _is_enabled, _empty_df, _pairing_allows_op


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


# ── C1: PUT_DOWN timing discrimination ───────────────────────────────────────

def _make_interaction_move_scenario(
    i_start=0, i_end=10, m_start=1, m_end=4,
):
    """Hand near workpiece (INTERACTION) while workpiece MOVE occurs."""
    frames = list(range(0, 12))
    wp_pos  = [(0.0, 0.0, 1.0)] * 12
    hand_pos = [(0.05, 0.0, 1.0)] * 12
    tracks = pd.concat([
        _make_track("trk_wp",   "workpiece", frames, wp_pos),
        _make_track("trk_hand", "hand",      frames, hand_pos),
    ])
    events = pd.DataFrame([
        _make_event("evt_int",  "INTERACTION", ["trk_hand", "trk_wp"], i_start, i_end),
        _make_event("evt_move", "MOVE",        ["trk_wp"],             m_start, m_end),
    ])
    return tracks, events


def test_pickup_when_move_starts_early():
    """MOVE starts near interaction onset → PICK_UP."""
    # i_start=0, m_start=1 (within pickup_link_frame_gap=10 of i_start=0)
    # m_end=4 (before i_end=10, but m_start is close to i_start → PICK_UP)
    tracks, events = _make_interaction_move_scenario(i_start=0, i_end=10, m_start=1, m_end=4)
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    assert "PICK_UP" in types


def test_putdown_when_move_ends_before_interaction_ends():
    """MOVE ends well before interaction end, but after interaction start → PUT_DOWN.

    PICK_UP condition: m_start <= i_start + pickup_gap(10) → 15 > 10 → NOT PICK_UP
    PUT_DOWN condition: m_end <= i_end + putdown_gap(8) AND m_end >= i_start → 18 <= 28 ✓
    """
    # i_start=5, i_end=20, m_start=15, m_end=18
    # m_start=15, i_start=5: 15 > 5+10=15 → is_pickup=True (borderline)
    # Use m_start=16 to be strictly outside pickup window
    tracks, events = _make_interaction_move_scenario(i_start=5, i_end=20, m_start=16, m_end=18)
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    assert "PUT_DOWN" in types


def test_putdown_not_emitted_when_disabled():
    """PUT_DOWN can be disabled."""
    tracks, events = _make_interaction_move_scenario(i_start=5, i_end=20, m_start=16, m_end=18)
    thr = {"operation_events": {"enabled_operations": {"PUT_DOWN": False}}}
    result = detect_operation_events(tracks, events, thr)
    assert "PUT_DOWN" not in result["operation_type"].tolist()


def test_pickup_not_putdown_when_move_precedes_interaction():
    """If MOVE starts before interaction onset, it's still PICK_UP (move and grab)."""
    # m_start=0, i_start=3: 0 <= 3+10=13 → is_pickup=True
    tracks, events = _make_interaction_move_scenario(i_start=3, i_end=10, m_start=0, m_end=5)
    result = detect_operation_events(tracks, events, _thr_defaults())
    types = result["operation_type"].tolist()
    assert "PICK_UP" in types
    assert "PUT_DOWN" not in types


# ── C4: Role pairing validation ───────────────────────────────────────────────

class _MockDomainConfig:
    """Minimal stand-in for DomainConfig for testing."""
    def __init__(self, pairings):
        self._pairings = pairings  # list of (agent_role, patient_role, valid_ops)

    def valid_operations_for_pairing(self, agent_role, patient_role):
        for a, p, ops in self._pairings:
            if a == agent_role and p == patient_role:
                return list(ops)
        return []


def test_pairing_allows_when_no_domain():
    assert _pairing_allows_op(None, "hand", "workpiece", "PICK_UP") is True


def test_pairing_allows_listed_op():
    dc = _MockDomainConfig([("hand", "workpiece", ["PICK_UP", "HOLD"])])
    assert _pairing_allows_op(dc, "hand", "workpiece", "PICK_UP") is True


def test_pairing_blocks_unlisted_op():
    dc = _MockDomainConfig([("hand", "workpiece", ["HOLD"])])
    # PICK_UP not in valid_operations for this pairing
    assert _pairing_allows_op(dc, "hand", "workpiece", "PICK_UP") is False


def test_pairing_permissive_when_pair_not_listed():
    """If the pairing isn't listed at all, permissive."""
    dc = _MockDomainConfig([("tool", "workpiece", ["USE_TOOL"])])
    assert _pairing_allows_op(dc, "hand", "workpiece", "PICK_UP") is True


def test_domain_config_blocks_pickup_emits_hold():
    """If PICK_UP is blocked by domain pairing, the same INTERACTION + MOVE should yield nothing
    (HOLD requires no move; here move exists so neither PICK_UP nor HOLD emits)."""
    tracks, events = _make_interaction_move_scenario(i_start=0, i_end=10, m_start=1, m_end=4)
    # Domain allows only HOLD for hand→workpiece, not PICK_UP
    dc = _MockDomainConfig([("hand", "workpiece", ["HOLD"])])
    result = detect_operation_events(tracks, events, _thr_defaults(), domain_config=dc)
    types = result["operation_type"].tolist()
    assert "PICK_UP" not in types


def test_domain_config_none_allows_all():
    """No domain config → PICK_UP emitted normally."""
    tracks, events = _make_interaction_move_scenario(i_start=0, i_end=10, m_start=1, m_end=4)
    result = detect_operation_events(tracks, events, _thr_defaults(), domain_config=None)
    types = result["operation_type"].tolist()
    assert "PICK_UP" in types
