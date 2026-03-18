"""Tests for EGG graph construction, serialization, and pruning."""
import sys, json, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest
from src.egg import build_egg_graph, save_egg, load_egg
from src.pruning import answer_query, get_last_seen, prune_by_event_type


def _make_graph():
    tracks = pd.DataFrame([
        {"track_id": "trk_001", "observation_id": "obs_001",
         "frame_idx": 1, "timestamp_ns": 0, "semantic_class": "container",
         "x": 0.1, "y": 0.5, "z": 1.2, "w": 0.1, "h": 0.1, "d": 0.1, "yaw": 0.0,
         "is_first_in_track": True, "is_last_in_track": False, "linkage_score": 1.0},
        {"track_id": "trk_001", "observation_id": "obs_002",
         "frame_idx": 10, "timestamp_ns": 1_000_000_000, "semantic_class": "container",
         "x": 0.2, "y": 0.5, "z": 1.2, "w": 0.1, "h": 0.1, "d": 0.1, "yaw": 0.0,
         "is_first_in_track": False, "is_last_in_track": True, "linkage_score": 0.9},
    ])
    events = pd.DataFrame([
        {"event_id": "evt_001", "event_type": "MOVE",
         "summary": "Container moved.",
         "start_ts_ns": 0, "end_ts_ns": 1_000_000_000,
         "room_id": "workstation_A",
         "event_pos_x": 0.15, "event_pos_y": 0.5, "event_pos_z": 1.2,
         "source": "rules", "confidence": 0.8},
        {"event_id": "evt_002", "event_type": "APPEAR",
         "summary": "Container appeared.",
         "start_ts_ns": 0, "end_ts_ns": 0,
         "room_id": "workstation_A",
         "event_pos_x": 0.1, "event_pos_y": 0.5, "event_pos_z": 1.2,
         "source": "rules", "confidence": 0.9},
    ])
    roles = pd.DataFrame([
        {"event_id": "evt_001", "track_id": "trk_001",
         "role": "moving_object", "role_description": "Container moved."},
        {"event_id": "evt_002", "track_id": "trk_001",
         "role": "appearing_object", "role_description": "Container appeared."},
    ])
    return build_egg_graph("test_session", tracks, events, roles)


def test_graph_has_required_keys():
    g = _make_graph()
    for key in ["graph_metadata", "rooms", "objects", "events", "event_edges",
                "room_edges", "temporal_edges"]:
        assert key in g


def test_graph_object_count():
    g = _make_graph()
    assert len(g["objects"]) == 1
    assert g["objects"][0]["track_id"] == "trk_001"


def test_graph_event_count():
    g = _make_graph()
    assert len(g["events"]) == 2


def test_graph_temporal_edges():
    g = _make_graph()
    assert len(g["temporal_edges"]) == 1
    assert g["temporal_edges"][0]["relation"] == "BEFORE"


def test_save_load_roundtrip():
    g = _make_graph()
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "egg.json"
        save_egg(g, p)
        g2 = load_egg(p)
    assert len(g2["objects"]) == len(g["objects"])
    assert len(g2["events"]) == len(g["events"])


def test_prune_by_event_type():
    g = _make_graph()
    sub = prune_by_event_type(g, "MOVE")
    assert all(e["event_type"] == "MOVE" for e in sub["events"])


def test_answer_query_what_moved():
    g = _make_graph()
    _, answer = answer_query(g, "What moved?")
    assert "container" in answer.lower() or "move" in answer.lower()


def test_get_last_seen():
    g = _make_graph()
    result = get_last_seen(g, "container")
    assert result is not None
    assert result["track_id"] == "trk_001"
