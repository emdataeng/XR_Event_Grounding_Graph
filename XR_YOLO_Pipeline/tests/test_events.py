"""Tests for event detection logic."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import pandas as pd
import pytest
from src.events import detect_event_windows, generate_event_summary


def _make_tracks():
    """Create a simple two-track DataFrame for testing."""
    rows = [
        # Track 1: moves from (0,0,1) to (0.3,0,1)
        {"track_id": "trk_0001", "observation_id": "obs_001",
         "frame_idx": 1, "timestamp_ns": 0, "semantic_class": "object",
         "x": 0.0, "y": 0.0, "z": 1.0, "w": 0.1, "h": 0.1, "d": 0.1, "yaw": 0.0,
         "is_first_in_track": True, "is_last_in_track": False, "linkage_score": 1.0},
        {"track_id": "trk_0001", "observation_id": "obs_002",
         "frame_idx": 5, "timestamp_ns": 500_000_000, "semantic_class": "object",
         "x": 0.3, "y": 0.0, "z": 1.0, "w": 0.1, "h": 0.1, "d": 0.1, "yaw": 0.0,
         "is_first_in_track": False, "is_last_in_track": True, "linkage_score": 0.8},
        # Track 2: stationary
        {"track_id": "trk_0002", "observation_id": "obs_003",
         "frame_idx": 1, "timestamp_ns": 0, "semantic_class": "surface",
         "x": 0.5, "y": 0.0, "z": 1.0, "w": 0.5, "h": 0.5, "d": 0.05, "yaw": 0.0,
         "is_first_in_track": True, "is_last_in_track": False, "linkage_score": 1.0},
        {"track_id": "trk_0002", "observation_id": "obs_004",
         "frame_idx": 5, "timestamp_ns": 500_000_000, "semantic_class": "surface",
         "x": 0.5, "y": 0.0, "z": 1.0, "w": 0.5, "h": 0.5, "d": 0.05, "yaw": 0.0,
         "is_first_in_track": False, "is_last_in_track": True, "linkage_score": 0.9},
    ]
    return pd.DataFrame(rows)


def test_detect_events_creates_appear():
    df = _make_tracks()
    events = detect_event_windows(df, min_move_distance_m=0.05)
    types = events["event_type"].tolist()
    assert "APPEAR" in types


def test_detect_events_creates_move():
    df = _make_tracks()
    events = detect_event_windows(df, min_move_distance_m=0.05)
    types = events["event_type"].tolist()
    assert "MOVE" in types


def test_generate_summary_move():
    df = _make_tracks()
    events = detect_event_windows(df, min_move_distance_m=0.05)
    move_events = events[events["event_type"] == "MOVE"]
    assert len(move_events) > 0
    ev = move_events.iloc[0]
    summary, roles = generate_event_summary(ev, df)
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert len(roles) > 0


def test_event_ids_unique():
    df = _make_tracks()
    events = detect_event_windows(df)
    assert events["event_id"].nunique() == len(events)
