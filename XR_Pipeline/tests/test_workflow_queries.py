"""Tests for src/workflow_queries.py."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest

from src.workflow_queries import answer_workflow_query


# ── Fixture helpers ───────────────────────────────────────────────────────────

def _make_ops(op_type="HOLD", confidence=0.80, n=1) -> pd.DataFrame:
    rows = []
    for i in range(n):
        rows.append({
            "operation_id":       f"op_{i+1:04d}",
            "operation_type":     op_type,
            "start_frame_idx":    i * 10,
            "end_frame_idx":      i * 10 + 9,
            "start_ts_ns":        i * 1_000_000_000,
            "end_ts_ns":          (i * 10 + 9) * 100_000_000,
            "agent_track_id":     "trk_hand",
            "object_track_id":    f"trk_wp_{i}",
            "secondary_track_id": None,
            "confidence":         confidence,
            "evidence_event_ids": json.dumps([f"evt_{i+1:04d}"]),
            "notes":              f"Test operation {i+1}.",
        })
    return pd.DataFrame(rows)


def _make_candidate_ops() -> pd.DataFrame:
    return pd.DataFrame([{
        "operation_id":       "op_0099",
        "operation_type":     "PICK_UP_CANDIDATE",
        "start_frame_idx":    5,
        "end_frame_idx":      10,
        "start_ts_ns":        500_000_000,
        "end_ts_ns":          1_000_000_000,
        "agent_track_id":     None,
        "object_track_id":    "trk_wp_0",
        "secondary_track_id": None,
        "confidence":         0.30,
        "evidence_event_ids": json.dumps(["evt_0001"]),
        "notes":              "Object moved from rest; no hand detected.",
    }])


def _make_ssp(phase_label="hold", phase_conf=1.0) -> dict:
    return {
        "state_summary": {
            "workflow_phase": {
                "label":      phase_label,
                "confidence": phase_conf,
                "evidence":   "2 HOLD events",
            },
            "active_operations": [
                {
                    "operation_id":   "op_0001",
                    "operation_type": "HOLD",
                    "agent":          "trk_hand",
                    "object":         "trk_wp_0",
                    "confidence":     0.80,
                }
            ],
        }
    }


# ── "What step is happening now?" ─────────────────────────────────────────────

def test_active_step_from_ssp():
    ssp = _make_ssp()
    ans = answer_workflow_query("What step is happening now?", None, ssp)
    assert "HOLD" in ans
    assert "trk_hand" in ans


def test_active_step_from_ops_when_no_ssp():
    ops = _make_ops()
    ans = answer_workflow_query("What step is happening now?", ops, None)
    assert "HOLD" in ans or "operation" in ans.lower()


def test_active_step_no_data():
    ans = answer_workflow_query("What step is happening now?", None, None)
    assert "no operation" in ans.lower() or "run 10b" in ans.lower()


# ── "What object is being manipulated?" ──────────────────────────────────────

def test_manipulated_object_returned():
    ops = _make_ops()
    ans = answer_workflow_query("What object is being manipulated?", ops, None)
    assert "trk_wp_0" in ans


def test_manipulated_object_no_ops():
    ans = answer_workflow_query("What object is being manipulated?", None, None)
    assert "no manipulation" in ans.lower()


# ── "What is the current workflow phase?" ────────────────────────────────────

def test_workflow_phase_from_ssp():
    ssp = _make_ssp(phase_label="hold", phase_conf=0.90)
    ans = answer_workflow_query("What is the current workflow phase?", None, ssp)
    assert "hold" in ans.lower()
    assert "0.90" in ans


def test_workflow_phase_from_ops_when_no_ssp():
    ops = _make_ops(op_type="PICK_UP", n=3)
    ans = answer_workflow_query("What is the current workflow phase?", ops, None)
    assert "PICK_UP" in ans or "pick_up" in ans.lower()


def test_workflow_phase_no_data():
    ans = answer_workflow_query("What is the current workflow phase?", None, None)
    assert "no operation" in ans.lower() or "available" in ans.lower()


# ── "Why do you think this step is happening?" ───────────────────────────────

def test_why_returns_evidence_from_ssp():
    ssp = _make_ssp()
    ops = _make_ops()
    ans = answer_workflow_query("Why do you think this step is happening?", ops, ssp)
    assert "hold" in ans.lower()
    assert len(ans) > 20


def test_why_no_data():
    ans = answer_workflow_query("Why do you think this step is happening?", None, None)
    assert "no evidence" in ans.lower()


# ── "Which tracks contributed to this operation?" ────────────────────────────

def test_contributing_tracks_listed():
    ops = _make_ops(n=2)
    ans = answer_workflow_query("Which tracks contributed to this operation?", ops, None)
    assert "trk_hand" in ans
    assert "agent" in ans.lower()


def test_contributing_tracks_no_ops():
    ans = answer_workflow_query("Which tracks contributed to this operation?", None, None)
    assert "no operation" in ans.lower()


# ── "What candidate operations were considered but not promoted?" ─────────────

def test_candidate_operations_listed():
    ops = _make_candidate_ops()
    ans = answer_workflow_query(
        "What candidate operations were considered but not promoted?", ops, None
    )
    assert "PICK_UP_CANDIDATE" in ans
    assert "trk_wp_0" in ans


def test_no_candidates_when_all_promoted():
    ops = _make_ops(op_type="HOLD")
    ans = answer_workflow_query(
        "What candidate operations were considered but not promoted?", ops, None
    )
    assert "no candidate" in ans.lower()


def test_candidate_operations_no_ops():
    ans = answer_workflow_query(
        "What candidate operations were considered but not promoted?", None, None
    )
    assert "no operation" in ans.lower()


# ── "Show the evidence for the current workflow phase" ───────────────────────

def test_evidence_for_phase_lists_event_ids():
    ops = _make_ops(n=3)
    ans = answer_workflow_query(
        "Show the evidence for the current workflow phase.", ops, None
    )
    assert "evt_" in ans or "event" in ans.lower()
    assert "HOLD" in ans or "hold" in ans.lower()


# ── "Which operation has the strongest evidence?" ────────────────────────────

def test_strongest_evidence_identified():
    ops = pd.concat([
        _make_ops(op_type="HOLD",    confidence=0.80),
        _make_ops(op_type="CONTACT", confidence=0.55),
    ], ignore_index=True)
    ans = answer_workflow_query(
        "Which operation has the strongest evidence?", ops, None
    )
    assert "HOLD" in ans
    assert "0.80" in ans


# ── Unmatched query ───────────────────────────────────────────────────────────

def test_unmatched_query_returns_fallback():
    ans = answer_workflow_query("How many unicorns are in the scene?", None, None)
    assert "not specifically matched" in ans.lower()
