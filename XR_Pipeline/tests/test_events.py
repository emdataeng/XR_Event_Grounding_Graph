"""Tests for event detection logic."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import pandas as pd
import pytest
from src.events import detect_event_windows, generate_event_summary, compute_track_motion_debug


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


# ── Role-aware MOVE threshold ─────────────────────────────────────────────────

def _make_tracks_with_roles(displacement=0.10):
    """Two tracks: one workpiece that moves 'displacement' m, one hand that moves 0.05 m."""
    rows = [
        # Workpiece track: displacement
        {"track_id": "trk_wp", "frame_idx": 1, "timestamp_ns": 0,
         "semantic_class": "red_lego", "object_role": "workpiece",
         "x": 0.0, "y": 0.0, "z": 1.0},
        {"track_id": "trk_wp", "frame_idx": 2, "timestamp_ns": 100_000_000,
         "semantic_class": "red_lego", "object_role": "workpiece",
         "x": displacement, "y": 0.0, "z": 1.0},
        # Hand track: moves 0.05 m (small)
        {"track_id": "trk_hand", "frame_idx": 1, "timestamp_ns": 0,
         "semantic_class": "hand", "object_role": "hand",
         "x": 0.5, "y": 0.0, "z": 1.0},
        {"track_id": "trk_hand", "frame_idx": 2, "timestamp_ns": 100_000_000,
         "semantic_class": "hand", "object_role": "hand",
         "x": 0.55, "y": 0.0, "z": 1.0},
    ]
    return pd.DataFrame(rows)


def test_role_aware_workpiece_threshold_lower():
    """Workpiece with 0.10 m displacement fires MOVE under workpiece threshold (0.08) but not global (0.20)."""
    df = _make_tracks_with_roles(displacement=0.10)
    move_by_role = {"workpiece": 0.08, "hand": 0.15}

    events_global = detect_event_windows(df, min_move_distance_m=0.20)
    events_role   = detect_event_windows(df, min_move_distance_m=0.20,
                                         min_move_distance_by_role=move_by_role)

    global_move_trks = set(
        json.loads(r["primary_track_ids"])[0]
        for _, r in events_global.iterrows() if r["event_type"] == "MOVE"
    )
    role_move_trks = set(
        json.loads(r["primary_track_ids"])[0]
        for _, r in events_role.iterrows() if r["event_type"] == "MOVE"
    )

    # Global (0.20 threshold) should not fire for workpiece (0.10 < 0.20)
    assert "trk_wp" not in global_move_trks
    # Role-aware (workpiece: 0.08) should fire (0.10 >= 0.08)
    assert "trk_wp" in role_move_trks


def test_role_aware_hand_threshold_suppresses_small_motion():
    """Hand moving 0.05 m should NOT fire MOVE under hand threshold of 0.15."""
    df = _make_tracks_with_roles(displacement=0.10)
    move_by_role = {"workpiece": 0.08, "hand": 0.15}

    events_role = detect_event_windows(df, min_move_distance_m=0.20,
                                        min_move_distance_by_role=move_by_role)
    hand_move = [r for _, r in events_role.iterrows()
                 if r["event_type"] == "MOVE" and
                 json.loads(r["primary_track_ids"])[0] == "trk_hand"]

    # Hand moved 0.05 m < 0.15 hand threshold → should not fire
    assert len(hand_move) == 0


def test_trigger_reason_includes_role():
    df = _make_tracks_with_roles(displacement=0.10)
    move_by_role = {"workpiece": 0.08, "hand": 0.15}

    events_role = detect_event_windows(df, min_move_distance_m=0.20,
                                        min_move_distance_by_role=move_by_role)
    wp_moves = events_role[events_role["event_type"] == "MOVE"]
    assert len(wp_moves) > 0
    assert "workpiece" in wp_moves.iloc[0]["trigger_reason"]


def test_unknown_role_falls_back_to_global():
    """Track with an unlisted role uses min_move_distance_m as fallback."""
    df = _make_tracks_with_roles(displacement=0.10)
    # Override roles to something not in move_by_role
    df["object_role"] = "container"
    move_by_role = {"workpiece": 0.08, "hand": 0.15}

    events = detect_event_windows(df, min_move_distance_m=0.20,
                                   min_move_distance_by_role=move_by_role)
    moves = events[events["event_type"] == "MOVE"]
    # 0.10 m < 0.20 global fallback → should NOT fire
    assert len(moves) == 0


# ── compute_track_motion_debug ────────────────────────────────────────────────

def test_motion_debug_columns():
    df = _make_tracks_with_roles(displacement=0.10)
    debug = compute_track_motion_debug(df, min_move_distance_m=0.20)
    expected_cols = {"track_id", "semantic_class", "object_role", "frame_idx",
                     "displacement_m", "move_threshold_m", "would_fire_move"}
    assert expected_cols.issubset(set(debug.columns))


def test_motion_debug_row_count():
    df = _make_tracks_with_roles()
    debug = compute_track_motion_debug(df)
    assert len(debug) == len(df)


def test_motion_debug_first_row_no_displacement():
    df = _make_tracks_with_roles()
    debug = compute_track_motion_debug(df)
    # First observation of each track has no previous → displacement_m is NaN/None
    first_rows = debug[debug["frame_idx"] == 1]
    for _, r in first_rows.iterrows():
        assert r["displacement_m"] is None or (r["displacement_m"] != r["displacement_m"])  # NaN


def test_motion_debug_would_fire_move():
    df = _make_tracks_with_roles(displacement=0.10)
    move_by_role = {"workpiece": 0.08, "hand": 0.15}
    debug = compute_track_motion_debug(
        df, min_move_distance_m=0.20, min_move_distance_by_role=move_by_role,
    )
    wp_second = debug[(debug["track_id"] == "trk_wp") & (debug["frame_idx"] == 2)]
    assert len(wp_second) == 1
    assert wp_second.iloc[0]["would_fire_move"] == True  # noqa: E712  (np.True_ comparison)


def test_motion_debug_below_threshold_by_m():
    df = _make_tracks_with_roles(displacement=0.10)
    # Global threshold = 0.20; displacement = 0.10 → below by 0.10
    debug = compute_track_motion_debug(df, min_move_distance_m=0.20)
    wp_second = debug[(debug["track_id"] == "trk_wp") & (debug["frame_idx"] == 2)]
    assert len(wp_second) == 1
    row = wp_second.iloc[0]
    assert row["would_fire_move"] == False  # noqa: E712
    assert row["below_threshold_by_m"] == pytest.approx(0.10, abs=0.005)


def test_motion_debug_empty_tracks():
    debug = compute_track_motion_debug(pd.DataFrame())
    assert len(debug) == 0


def test_motion_debug_role_aware_threshold_recorded():
    df = _make_tracks_with_roles()
    move_by_role = {"workpiece": 0.08, "hand": 0.15}
    debug = compute_track_motion_debug(
        df, min_move_distance_m=0.20, min_move_distance_by_role=move_by_role,
    )
    wp_rows = debug[debug["track_id"] == "trk_wp"]
    assert all(row["move_threshold_m"] == pytest.approx(0.08) for _, row in wp_rows.iterrows())
    hand_rows = debug[debug["track_id"] == "trk_hand"]
    assert all(row["move_threshold_m"] == pytest.approx(0.15) for _, row in hand_rows.iterrows())


# ── B3: 2D bbox motion columns ────────────────────────────────────────────────

def _make_tracks_with_bbox(displacement_px=30.0):
    """Tracks with bbox columns for 2D motion testing."""
    rows = [
        {"track_id": "trk_wp", "frame_idx": 1, "timestamp_ns": 0,
         "observation_id": "obs_001",
         "semantic_class": "red_lego", "object_role": "workpiece",
         "x": 0.0, "y": 0.0, "z": 1.0,
         "bbox_x1": 100.0, "bbox_y1": 100.0, "bbox_x2": 150.0, "bbox_y2": 150.0},
        {"track_id": "trk_wp", "frame_idx": 2, "timestamp_ns": 100_000_000,
         "observation_id": "obs_002",
         "semantic_class": "red_lego", "object_role": "workpiece",
         "x": 0.01, "y": 0.0, "z": 1.0,  # tiny 3D motion
         "bbox_x1": 100.0 + displacement_px, "bbox_y1": 100.0,
         "bbox_x2": 150.0 + displacement_px, "bbox_y2": 150.0},
    ]
    return pd.DataFrame(rows)


def _make_obs_df_for_bbox():
    """Minimal observations CSV with bbox columns."""
    rows = [
        {"observation_id": "obs_001", "frame_idx": 1,
         "bbox_x1": 100.0, "bbox_y1": 100.0, "bbox_x2": 150.0, "bbox_y2": 150.0},
        {"observation_id": "obs_002", "frame_idx": 2,
         "bbox_x1": 130.0, "bbox_y1": 100.0, "bbox_x2": 180.0, "bbox_y2": 150.0},
    ]
    return pd.DataFrame(rows)


def test_motion_debug_2d_columns_present_without_obs():
    """2D columns always present in debug output (None without obs_df)."""
    df = _make_tracks_with_roles()
    debug = compute_track_motion_debug(df)
    for col in ("bbox_cx", "bbox_cy", "bbox_area_px", "bbox_disp_2d_px", "bbox_area_change_pct"):
        assert col in debug.columns


def test_motion_debug_2d_disp_computed_from_obs():
    """bbox_disp_2d_px is populated when obs_df provides bbox data via observation_id."""
    df = _make_tracks_with_bbox(displacement_px=30.0)
    obs = _make_obs_df_for_bbox()
    debug = compute_track_motion_debug(df, obs_df=obs)
    second_row = debug[(debug["track_id"] == "trk_wp") & (debug["frame_idx"] == 2)]
    assert len(second_row) == 1
    disp = second_row.iloc[0]["bbox_disp_2d_px"]
    assert disp is not None
    assert disp == pytest.approx(30.0, abs=1.0)


def test_motion_debug_2d_none_when_no_obs():
    """bbox_disp_2d_px is None when obs_df not provided."""
    df = _make_tracks_with_bbox()
    debug = compute_track_motion_debug(df)
    second_row = debug[(debug["track_id"] == "trk_wp") & (debug["frame_idx"] == 2)]
    assert second_row.iloc[0]["bbox_disp_2d_px"] is None


def test_2d_fallback_move_fires_when_3d_below_threshold():
    """2D fallback MOVE fires when bbox displacement >= min_2d_disp_px and 3D is below threshold."""
    df = _make_tracks_with_bbox(displacement_px=30.0)
    # 3D displacement is 0.01 m (tiny) — well below any reasonable threshold
    events = detect_event_windows(
        df,
        min_move_distance_m=0.50,  # high threshold so 3D won't fire
        min_2d_disp_px=20.0,
    )
    move_events = events[events["event_type"] == "MOVE"]
    assert len(move_events) > 0
    assert "2D" in move_events.iloc[0]["trigger_reason"]


def test_2d_fallback_disabled_when_zero():
    """2D fallback does not fire when min_2d_disp_px=0."""
    df = _make_tracks_with_bbox(displacement_px=100.0)
    events = detect_event_windows(df, min_move_distance_m=0.50, min_2d_disp_px=0.0)
    move_events = events[events["event_type"] == "MOVE"]
    assert len(move_events) == 0
