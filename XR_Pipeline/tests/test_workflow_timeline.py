"""Tests for workflow_timeline.py — Phase 3 timeline construction."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest

from src.workflow_timeline import build_workflow_timeline, timeline_to_df


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_op(oid, op_type, start_f, end_f, agent=None, obj="trk_wp", conf=0.7):
    return {
        "operation_id":        oid,
        "operation_type":      op_type,
        "start_frame_idx":     start_f,
        "end_frame_idx":       end_f,
        "start_ts_ns":         start_f * 100_000_000,
        "end_ts_ns":           end_f   * 100_000_000,
        "agent_track_id":      agent,
        "object_track_id":     obj,
        "secondary_track_id":  None,
        "confidence":          conf,
        "evidence_event_ids":  "[]",
        "notes":               f"test op {oid}",
    }


def _make_ops_df(rows):
    return pd.DataFrame(rows)


# ── Empty / null input ────────────────────────────────────────────────────────

def test_empty_ops_returns_idle_timeline():
    tl = build_workflow_timeline(pd.DataFrame(), session_id="s001")
    assert tl["summary"]["total_phases"] == 0
    assert tl["summary"]["dominant_phase"] == "idle"
    assert tl["phases"] == []
    assert tl["phase_transitions"] == []


def test_none_ops_returns_idle_timeline():
    tl = build_workflow_timeline(None, session_id="s001")
    assert tl["summary"]["dominant_phase"] == "idle"


def test_schema_version_present():
    tl = build_workflow_timeline(pd.DataFrame(), session_id="s001")
    assert tl["schema_version"] == "1.0"


def test_session_id_preserved():
    tl = build_workflow_timeline(pd.DataFrame(), session_id="my_session")
    assert tl["session_id"] == "my_session"


# ── Single-phase timeline ─────────────────────────────────────────────────────

def test_single_cluster_produces_one_phase():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD", 0, 10, agent="trk_hand"),
        _make_op("op_0002", "HOLD", 5, 15, agent="trk_hand"),
    ])
    tl = build_workflow_timeline(ops)
    assert len(tl["phases"]) == 1


def test_hold_ops_label_hold_phase():
    ops = _make_ops_df([_make_op("op_0001", "HOLD", 0, 10, agent="trk_hand")])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "hold"


def test_pick_up_labels_manipulation():
    ops = _make_ops_df([_make_op("op_0001", "PICK_UP", 0, 5, agent="trk_hand")])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "manipulation"


def test_approach_labels_approach():
    ops = _make_ops_df([_make_op("op_0001", "APPROACH", 0, 6)])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "approach"


def test_place_onto_labels_placement():
    ops = _make_ops_df([_make_op("op_0001", "PLACE_ONTO_CANDIDATE", 0, 8)])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "placement"


def test_contact_labels_contact():
    ops = _make_ops_df([_make_op("op_0001", "CONTACT", 0, 3)])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "contact"


# ── Phase priority ────────────────────────────────────────────────────────────

def test_manipulation_priority_over_hold():
    """PICK_UP (priority 0) beats HOLD (priority 1) in the same cluster."""
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0, 10, agent="trk_hand"),
        _make_op("op_0002", "PICK_UP", 2,  7, agent="trk_hand"),
    ])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "manipulation"


def test_hold_priority_over_contact():
    ops = _make_ops_df([
        _make_op("op_0001", "CONTACT", 0, 5),
        _make_op("op_0002", "HOLD",    0, 5, agent="trk_hand"),
    ])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["label"] == "hold"


# ── Multi-phase timeline ──────────────────────────────────────────────────────

def test_two_clusters_produce_two_phases():
    """Operations separated by > 3s should produce separate phases."""
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",   0, 10),   # ts 0 – 1.0s
        # large gap: next op starts at frame 400 = 40s
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    assert len(tl["phases"]) == 2


def test_transitions_recorded():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0, 10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    assert len(tl["phase_transitions"]) == 1
    tr = tl["phase_transitions"][0]
    assert tr["from_label"] == "hold"
    assert tr["to_label"]   == "contact"


def test_phase_ids_sequential():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0, 10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["phase_id"] == "phase_0001"
    assert tl["phases"][1]["phase_id"] == "phase_0002"


def test_previous_phase_id_set():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0, 10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    assert tl["phases"][0]["previous_phase_id"] is None
    assert tl["phases"][1]["previous_phase_id"] == "phase_0001"


# ── Summary ───────────────────────────────────────────────────────────────────

def test_summary_total_operations():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD", 0, 10),
        _make_op("op_0002", "HOLD", 5, 12),
    ])
    tl = build_workflow_timeline(ops)
    assert tl["summary"]["total_operations"] == 2


def test_summary_dominant_phase():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0,  10),
        _make_op("op_0002", "HOLD",    5,  15),
        _make_op("op_0003", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    # Two hold phases vs one contact → dominant = hold
    assert tl["summary"]["dominant_phase"] == "hold"


def test_summary_manipulated_objects():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD", 0, 10, obj="trk_0001"),
        _make_op("op_0002", "HOLD", 5, 12, obj="trk_0002"),
    ])
    tl = build_workflow_timeline(ops)
    objects = set(tl["summary"]["manipulated_objects"])
    assert "trk_0001" in objects
    assert "trk_0002" in objects


def test_summary_candidate_count():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",               0, 10),
        _make_op("op_0002", "PICK_UP_CANDIDATE",  5, 10),
        _make_op("op_0003", "PUT_DOWN_CANDIDATE", 12, 18),
    ])
    tl = build_workflow_timeline(ops)
    assert tl["summary"]["unresolved_candidates"] == 2


# ── timeline_to_df ────────────────────────────────────────────────────────────

def test_timeline_to_df_columns():
    ops = _make_ops_df([_make_op("op_0001", "HOLD", 0, 10)])
    tl = build_workflow_timeline(ops)
    df = timeline_to_df(tl)
    assert "phase_id" in df.columns
    assert "label"    in df.columns
    assert "confidence" in df.columns


def test_timeline_to_df_empty():
    tl = build_workflow_timeline(pd.DataFrame())
    df = timeline_to_df(tl)
    assert df.empty


def test_timeline_to_df_one_row_per_phase():
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0,  10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    df = timeline_to_df(tl)
    assert len(df) == 2


# ── workflow_queries timeline integration ─────────────────────────────────────

def test_query_transition():
    from src.workflow_queries import answer_workflow_query
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0,  10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    answer = answer_workflow_query("What phase transition just happened?",
                                   ops, None, timeline=tl)
    assert "hold" in answer.lower()
    assert "contact" in answer.lower()


def test_query_previous_phase():
    from src.workflow_queries import answer_workflow_query
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0,  10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    answer = answer_workflow_query("What happened before this phase?",
                                   ops, None, timeline=tl)
    assert "hold" in answer.lower()


def test_query_phase_count():
    from src.workflow_queries import answer_workflow_query
    ops = _make_ops_df([
        _make_op("op_0001", "HOLD",    0,  10),
        _make_op("op_0002", "CONTACT", 400, 410),
    ])
    tl = build_workflow_timeline(ops)
    answer = answer_workflow_query("How many phases were there?",
                                   ops, None, timeline=tl)
    assert "2" in answer


def test_query_workflow_phase_uses_timeline():
    from src.workflow_queries import answer_workflow_query
    ops = _make_ops_df([_make_op("op_0001", "HOLD", 0, 10)])
    tl = build_workflow_timeline(ops)
    answer = answer_workflow_query("What is the current workflow phase?",
                                   ops, None, timeline=tl)
    assert "hold" in answer.lower()


def test_no_transition_on_single_phase():
    from src.workflow_queries import answer_workflow_query
    ops = _make_ops_df([_make_op("op_0001", "HOLD", 0, 10)])
    tl = build_workflow_timeline(ops)
    answer = answer_workflow_query("What phase transition just happened?",
                                   ops, None, timeline=tl)
    assert "no phase transition" in answer.lower() or "one phase" in answer.lower()
