"""Tests for operation_events.py — Milestone 3 coverage."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest

from src.operation_events import detect_operation_events, _empty_df


# ── Fixture helpers ───────────────────────────────────────────────────────────

def _make_workpiece_tracks(
    tid: str = "trk_0001",
    frames=(0, 5, 10),
    positions=((0.0, 0.0, 1.0), (0.0, 0.0, 1.0), (0.3, 0.0, 1.0)),
) -> pd.DataFrame:
    rows = []
    for i, (f, (x, y, z)) in enumerate(zip(frames, positions)):
        rows.append({
            "track_id": tid,
            "observation_id": f"obs_{tid}_{i}",
            "frame_idx": f,
            "timestamp_ns": f * 100_000_000,
            "semantic_class": "red_lego",
            "object_role": "workpiece",
            "x": x, "y": y, "z": z,
            "w": 0.05, "h": 0.05, "d": 0.05,
        })
    return pd.DataFrame(rows)


def _make_hand_tracks(
    tid: str = "trk_0002",
    frames=(0, 5, 10),
    positions=((0.1, 0.0, 1.0), (0.05, 0.0, 1.0), (0.1, 0.0, 1.0)),
) -> pd.DataFrame:
    rows = []
    for i, (f, (x, y, z)) in enumerate(zip(frames, positions)):
        rows.append({
            "track_id": tid,
            "observation_id": f"obs_{tid}_{i}",
            "frame_idx": f,
            "timestamp_ns": f * 100_000_000,
            "semantic_class": "hand",
            "object_role": "hand",
            "x": x, "y": y, "z": z,
            "w": 0.08, "h": 0.08, "d": 0.04,
        })
    return pd.DataFrame(rows)


def _make_move_event(tid: str = "trk_0001", start=5, end=10) -> pd.DataFrame:
    return pd.DataFrame([{
        "event_id": f"evt_move_{tid}",
        "event_type": "MOVE",
        "start_frame_idx": start,
        "end_frame_idx": end,
        "start_ts_ns": start * 100_000_000,
        "end_ts_ns": end * 100_000_000,
        "primary_track_ids": json.dumps([tid]),
        "confidence": 0.75,
    }])


def _make_interaction_event(
    h_tid: str = "trk_0002",
    o_tid: str = "trk_0001",
    start=0, end=10,
) -> pd.DataFrame:
    return pd.DataFrame([{
        "event_id": "evt_interact",
        "event_type": "INTERACTION",
        "start_frame_idx": start,
        "end_frame_idx": end,
        "start_ts_ns": start * 100_000_000,
        "end_ts_ns": end * 100_000_000,
        "primary_track_ids": json.dumps([h_tid, o_tid]),
        "confidence": 0.80,
    }])


def _make_coloc_event(
    tid_a: str = "trk_0001",
    tid_b: str = "trk_0003",
    start=3, end=5,
) -> pd.DataFrame:
    return pd.DataFrame([{
        "event_id": "evt_coloc",
        "event_type": "CO_LOCATE",
        "start_frame_idx": start,
        "end_frame_idx": end,
        "start_ts_ns": start * 100_000_000,
        "end_ts_ns": end * 100_000_000,
        "primary_track_ids": json.dumps([tid_a, tid_b]),
        "confidence": 0.70,
    }])


EMPTY_THR: dict = {}


# ── Output schema ─────────────────────────────────────────────────────────────

REQUIRED_COLUMNS = {
    "operation_id", "operation_type",
    "start_frame_idx", "end_frame_idx",
    "start_ts_ns", "end_ts_ns",
    "agent_track_id", "object_track_id", "secondary_track_id",
    "confidence", "evidence_event_ids", "notes",
}


def test_empty_df_has_correct_schema():
    df = _empty_df()
    assert set(df.columns) >= REQUIRED_COLUMNS


def test_output_schema_stable():
    """detect_operation_events always returns a DataFrame with required columns."""
    tracks = _make_workpiece_tracks()
    events = _make_move_event()
    result = detect_operation_events(tracks, events, EMPTY_THR)
    assert set(result.columns) >= REQUIRED_COLUMNS


def test_empty_inputs_return_empty():
    empty_tracks = pd.DataFrame()
    empty_events = pd.DataFrame()
    result = detect_operation_events(empty_tracks, empty_events, EMPTY_THR)
    assert result.empty


# ── TRANSFER detection (no hand vocab) ───────────────────────────────────────

def test_transfer_detected_without_hand():
    """MOVE of a workpiece with no hand-role tracks → TRANSFER."""
    tracks = _make_workpiece_tracks(
        frames=(0, 5, 10),
        positions=((0.0, 0.0, 1.0), (0.5, 0.0, 1.0), (1.0, 0.0, 1.0)),
    )
    events = _make_move_event()
    result = detect_operation_events(tracks, events, EMPTY_THR)
    assert not result.empty
    assert "TRANSFER" in result["operation_type"].values


def test_transfer_has_no_agent():
    """TRANSFER ops have no agent (no hand available)."""
    tracks = _make_workpiece_tracks()
    events = _make_move_event()
    result = detect_operation_events(tracks, events, EMPTY_THR)
    transfers = result[result["operation_type"] == "TRANSFER"]
    assert transfers["agent_track_id"].isna().all() or (
        transfers["agent_track_id"].astype(str).isin(["None", "nan", ""]).all()
    )


def test_no_transfer_when_hand_present_during_move():
    """MOVE + INTERACTION overlap → PICK_UP (not TRANSFER)."""
    tracks = pd.concat([
        _make_workpiece_tracks(
            frames=(0, 5, 10),
            positions=((0.0, 0.0, 1.0), (0.5, 0.0, 1.0), (1.0, 0.0, 1.0)),
        ),
        _make_hand_tracks(
            frames=(0, 5, 10),
            positions=((0.05, 0.0, 1.0), (0.5, 0.0, 1.0), (1.05, 0.0, 1.0)),
        ),
    ], ignore_index=True)

    events = pd.concat([
        _make_move_event(),
        _make_interaction_event(),
    ], ignore_index=True)

    result = detect_operation_events(tracks, events, EMPTY_THR)
    assert "TRANSFER" not in result["operation_type"].values


# ── No false HOLD/PICK_UP without hand-role objects ──────────────────────────

def test_no_hold_without_hand_role():
    """Pure workpiece + INTERACTION event with wrong roles → no HOLD."""
    # Two workpieces with an INTERACTION event — INTERACTION needs a hand-role track
    tracks = pd.concat([
        _make_workpiece_tracks("trk_0001"),
        _make_workpiece_tracks("trk_0002"),
    ], ignore_index=True)
    events = _make_interaction_event("trk_0001", "trk_0002")
    result = detect_operation_events(tracks, events, EMPTY_THR)
    assert "HOLD" not in result["operation_type"].values
    assert "PICK_UP" not in result["operation_type"].values


def test_no_pickup_without_hand_role():
    """MOVE of a workpiece without a hand → never emits PICK_UP (only TRANSFER)."""
    tracks = _make_workpiece_tracks(
        frames=(0, 5, 10),
        positions=((0.0, 0.0, 1.0), (0.5, 0.0, 1.0), (1.0, 0.0, 1.0)),
    )
    events = _make_move_event()
    result = detect_operation_events(tracks, events, EMPTY_THR)
    assert "PICK_UP" not in result["operation_type"].values


# ── HOLD detection ────────────────────────────────────────────────────────────

def test_hold_detected_with_hand_and_no_significant_move():
    """INTERACTION window (no linked MOVE) with sufficient duration → HOLD."""
    tracks = pd.concat([
        _make_workpiece_tracks(
            frames=(0, 5, 10),
            positions=((0.0, 0.0, 1.0), (0.01, 0.0, 1.0), (0.01, 0.0, 1.0)),  # tiny motion
        ),
        _make_hand_tracks(frames=(0, 5, 10)),
    ], ignore_index=True)

    # Long interaction window (10 frames ≥ hold_min default of 5)
    events = _make_interaction_event(start=0, end=10)
    result = detect_operation_events(tracks, events, EMPTY_THR)
    holds = result[result["operation_type"] == "HOLD"]
    assert not holds.empty
    assert holds.iloc[0]["agent_track_id"] == "trk_0002"
    assert holds.iloc[0]["object_track_id"] == "trk_0001"


def test_hold_confidence_capped():
    """HOLD confidence should be ≤ 0.80 (as coded)."""
    tracks = pd.concat([
        _make_workpiece_tracks(),
        _make_hand_tracks(),
    ], ignore_index=True)
    events = _make_interaction_event(start=0, end=10)
    result = detect_operation_events(tracks, events, EMPTY_THR)
    holds = result[result["operation_type"] == "HOLD"]
    if not holds.empty:
        assert holds["confidence"].max() <= 0.80


# ── PICK_UP detection ─────────────────────────────────────────────────────────

def test_pick_up_detected_with_hand_and_move():
    """INTERACTION + workpiece MOVE → PICK_UP."""
    tracks = pd.concat([
        _make_workpiece_tracks(
            frames=(0, 5, 10),
            positions=((0.0, 0.0, 1.0), (0.5, 0.0, 1.0), (1.0, 0.0, 1.0)),
        ),
        _make_hand_tracks(),
    ], ignore_index=True)
    events = pd.concat([
        _make_interaction_event(),
        _make_move_event(),
    ], ignore_index=True)
    result = detect_operation_events(tracks, events, EMPTY_THR)
    assert "PICK_UP" in result["operation_type"].values


# ── Evidence IDs ─────────────────────────────────────────────────────────────

def test_evidence_event_ids_are_json_list():
    """evidence_event_ids column is always a JSON-parseable list."""
    tracks = pd.concat([
        _make_workpiece_tracks(),
        _make_hand_tracks(),
    ], ignore_index=True)
    events = _make_interaction_event(start=0, end=10)
    result = detect_operation_events(tracks, events, EMPTY_THR)
    for _, row in result.iterrows():
        ids = json.loads(row["evidence_event_ids"])
        assert isinstance(ids, list)


# ── Threshold override via thr dict ──────────────────────────────────────────

def test_hold_suppressed_when_duration_below_custom_threshold():
    """Setting hold_min_frames=20 should suppress HOLD for a 10-frame interaction."""
    tracks = pd.concat([
        _make_workpiece_tracks(),
        _make_hand_tracks(),
    ], ignore_index=True)
    events = _make_interaction_event(start=0, end=10)
    thr_strict = {"operation_events": {"hold_min_frames": 20}}
    result = detect_operation_events(tracks, events, thr_strict)
    assert "HOLD" not in result["operation_type"].values


# ── Contact detection ─────────────────────────────────────────────────────────

def test_contact_detected_on_coloc_within_threshold():
    """CO_LOCATE with objects within contact_threshold_m → CONTACT."""
    # Two workpieces at 0.05m apart (below default 0.08m threshold)
    tracks = pd.concat([
        _make_workpiece_tracks("trk_0001", frames=(3,), positions=((0.0, 0.0, 1.0),)),
        _make_workpiece_tracks("trk_0003", frames=(3,), positions=((0.04, 0.0, 1.0),)),
    ], ignore_index=True)
    events = _make_coloc_event()
    result = detect_operation_events(tracks, events, EMPTY_THR)
    contacts = result[result["operation_type"] == "CONTACT"]
    assert not contacts.empty
