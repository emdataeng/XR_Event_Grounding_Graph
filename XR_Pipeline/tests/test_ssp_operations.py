"""Tests for SSP operation layer — workflow_phase, active_ops, recent_ops."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import pytest

from src.scene_state_package import build_scene_state_package


# ── Fixture helpers ───────────────────────────────────────────────────────────

_CFG = {
    "session_id": "test_session",
    "observations_source": "grounding_dino",
    "default_room_id": "workstation_A",
}
_THR = {
    "events": {"near_threshold_m": 0.3},
    "confidence": {"min_observation": 0.3, "min_track": 0.4, "min_event": 0.5},
}


def _make_tracks(n_frames=20) -> pd.DataFrame:
    rows = []
    for f in range(n_frames):
        rows.append({
            "track_id": "trk_0001", "observation_id": f"obs_r_{f}",
            "frame_idx": f, "timestamp_ns": f * 100_000_000,
            "semantic_class": "red_lego", "object_role": "workpiece",
            "x": 0.1, "y": 0.0, "z": 1.0, "w": 0.05, "h": 0.05, "d": 0.05,
            "is_first_in_track": f == 0, "is_last_in_track": f == n_frames - 1,
            "linkage_score": 0.9,
        })
        rows.append({
            "track_id": "trk_0002", "observation_id": f"obs_h_{f}",
            "frame_idx": f, "timestamp_ns": f * 100_000_000,
            "semantic_class": "hand", "object_role": "hand",
            "x": 0.15, "y": 0.0, "z": 1.0, "w": 0.08, "h": 0.08, "d": 0.04,
            "is_first_in_track": f == 0, "is_last_in_track": f == n_frames - 1,
            "linkage_score": 0.8,
        })
    return pd.DataFrame(rows)


def _make_obs(tracks_df: pd.DataFrame) -> pd.DataFrame:
    obs_rows = []
    for _, row in tracks_df.drop_duplicates(subset=["observation_id"]).iterrows():
        obs_rows.append({
            "observation_id": row["observation_id"],
            "frame_idx": row["frame_idx"],
            "timestamp_ns": row["timestamp_ns"],
            "semantic_class": row["semantic_class"],
            "source": "grounding_dino",
            "confidence": 0.75,
            "x": row["x"], "y": row["y"], "z": row["z"],
            "bbox_x1": 10.0, "bbox_y1": 10.0, "bbox_x2": 60.0, "bbox_y2": 60.0,
        })
    return pd.DataFrame(obs_rows)


def _make_events(tracks_df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{
        "event_id": "evt_0001",
        "event_type": "INTERACTION",
        "start_frame_idx": 10,
        "end_frame_idx": 19,
        "start_ts_ns": 1_000_000_000,
        "end_ts_ns": 1_900_000_000,
        "primary_track_ids": json.dumps(["trk_0002", "trk_0001"]),
        "room_id": "workstation_A",
        "trigger_reason": "hand near red_lego",
        "confidence": 0.80,
    }])


def _make_roles() -> pd.DataFrame:
    return pd.DataFrame([
        {"event_id": "evt_0001", "track_id": "trk_0002", "role": "interacting_hand",
         "role_description": "hand acted as interacting_hand"},
        {"event_id": "evt_0001", "track_id": "trk_0001", "role": "target_object",
         "role_description": "red_lego acted as target_object"},
    ])


def _make_ops() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "operation_id":       "op_0001",
            "operation_type":     "HOLD",
            "start_frame_idx":    10,
            "end_frame_idx":      19,
            "start_ts_ns":        1_000_000_000,
            "end_ts_ns":          1_900_000_000,
            "agent_track_id":     "trk_0002",
            "object_track_id":    "trk_0001",
            "secondary_track_id": None,
            "confidence":         0.80,
            "evidence_event_ids": json.dumps(["evt_0001"]),
            "notes":              "Hand trk_0002 held trk_0001 for 10 frames.",
        },
        {
            "operation_id":       "op_0002",
            "operation_type":     "CONTACT",
            "start_frame_idx":    5,
            "end_frame_idx":      8,
            "start_ts_ns":        500_000_000,
            "end_ts_ns":          800_000_000,
            "agent_track_id":     None,
            "object_track_id":    "trk_0001",
            "secondary_track_id": "trk_0002",
            "confidence":         0.55,
            "evidence_event_ids": json.dumps(["evt_0002"]),
            "notes":              "Contact between trk_0001 and trk_0002.",
        },
    ])


# ── SSP without ops_df ────────────────────────────────────────────────────────

def test_ssp_builds_without_ops():
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR,
    )
    assert pkg["schema_version"] == "1.0"
    assert "state_summary" in pkg
    # Without ops_df, operation keys should not be present
    ss = pkg["state_summary"]
    assert "workflow_phase" not in ss
    assert "active_operations" not in ss


# ── SSP with ops_df ───────────────────────────────────────────────────────────

def test_ssp_state_summary_has_workflow_phase():
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    ss = pkg["state_summary"]
    assert "workflow_phase" in ss
    wf = ss["workflow_phase"]
    assert "label" in wf
    assert "confidence" in wf
    assert 0.0 <= wf["confidence"] <= 1.0


def test_ssp_workflow_phase_label_is_dominant_op():
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    # HOLD has higher confidence×count score than CONTACT
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    wf = pkg["state_summary"]["workflow_phase"]
    # HOLD: count=1, conf=0.80 → score=0.80  |  CONTACT: count=1, conf=0.55 → score=0.55
    assert wf["label"] == "hold"


def test_ssp_active_operations_present():
    tracks = _make_tracks(n_frames=20)
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    ss = pkg["state_summary"]
    assert "active_operations" in ss
    # HOLD ends at frame 19 == global_max_frame (19) — within ACTIVE_FRAME_WINDOW=5
    active = ss["active_operations"]
    assert any(op["operation_type"] == "HOLD" for op in active)


def test_ssp_active_op_agent_not_none():
    """After _is_nan fix, agent and object fields are populated from track IDs."""
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    active = pkg["state_summary"]["active_operations"]
    hold_ops = [op for op in active if op["operation_type"] == "HOLD"]
    assert hold_ops, "Expected at least one HOLD in active_operations"
    assert hold_ops[0]["agent"] == "trk_0002"
    assert hold_ops[0]["object"] == "trk_0001"


def test_ssp_recent_completed_operations_present():
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    ss = pkg["state_summary"]
    assert "recent_completed_operations" in ss
    recent = ss["recent_completed_operations"]
    assert len(recent) <= 5
    assert all("operation_type" in op for op in recent)


def test_ssp_tool_workpiece_relations_present():
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    ss = pkg["state_summary"]
    assert "tool_workpiece_relations" in ss
    # No USE_TOOL ops in fixture → empty list
    assert isinstance(ss["tool_workpiece_relations"], list)


def test_ssp_tool_workpiece_populated_for_use_tool():
    """USE_TOOL operation → tool_workpiece_relations has an entry."""
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops = pd.DataFrame([{
        "operation_id":       "op_0010",
        "operation_type":     "USE_TOOL",
        "start_frame_idx":    5, "end_frame_idx": 10,
        "start_ts_ns":        500_000_000, "end_ts_ns": 1_000_000_000,
        "agent_track_id":     "trk_0002",
        "object_track_id":    "trk_0001",
        "secondary_track_id": None,
        "confidence":         0.70,
        "evidence_event_ids": json.dumps(["evt_0001"]),
        "notes":              "Tool near workpiece.",
    }])
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    tw = pkg["state_summary"]["tool_workpiece_relations"]
    assert len(tw) == 1
    assert tw[0]["tool"] == "trk_0002"
    assert tw[0]["workpiece"] == "trk_0001"


# ── Round-trip serialisation ──────────────────────────────────────────────────

def test_ssp_json_roundtrip(tmp_path):
    from src.scene_state_package import save_scene_state_package, load_scene_state_package
    tracks = _make_tracks()
    obs    = _make_obs(tracks)
    events = _make_events(tracks)
    roles  = _make_roles()
    ops    = _make_ops()
    pkg = build_scene_state_package(
        session_id="test_session",
        tracks_df=tracks, obs_df=obs, events_df=events, roles_df=roles,
        cfg=_CFG, thr=_THR, ops_df=ops,
    )
    path = tmp_path / "ssp.json"
    save_scene_state_package(pkg, path)
    loaded = load_scene_state_package(path)
    assert loaded["schema_version"] == pkg["schema_version"]
    assert loaded["state_summary"]["workflow_phase"]["label"] == \
           pkg["state_summary"]["workflow_phase"]["label"]
