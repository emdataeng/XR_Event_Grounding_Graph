"""tests/test_state_facts.py — Unit tests for src/state_facts.py (Phase 1)."""
import pytest
import pandas as pd

from src.state_facts import (
    compute_state_facts,
    active_facts,
    facts_for_predicate,
    facts_to_json,
    FACT_COLS,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _make_tracks(**rows):
    defaults = dict(
        track_id=["trk_a"],
        frame_idx=[0],
        start_frame_idx=[0],
        end_frame_idx=[30],
        semantic_class=["workpiece"],
        object_role=["workpiece"],
        confidence=[0.9],
    )
    defaults.update(rows)
    return pd.DataFrame(defaults)


def _make_events(**rows):
    defaults = dict(
        event_id=["ev_001"],
        event_type=["MOVE"],
        primary_track_ids=['["trk_a"]'],
        start_frame_idx=[5],
        end_frame_idx=[10],
        confidence=[0.8],
    )
    defaults.update(rows)
    return pd.DataFrame(defaults)


def _make_ops(**rows):
    defaults = dict(
        operation_id=["op_001"],
        operation_type=["HOLD"],
        agent_track_id=["trk_hand"],
        object_track_id=["trk_a"],
        start_frame_idx=[5],
        end_frame_idx=[12],
        confidence=[0.75],
    )
    defaults.update(rows)
    return pd.DataFrame(defaults)


# ── Schema ─────────────────────────────────────────────────────────────────────

class TestSchema:
    def test_fact_cols_defined(self):
        expected = {
            "fact_id", "predicate", "subject_id", "object_id", "status",
            "confidence", "start_frame_idx", "end_frame_idx",
            "evidence_refs", "source_stage", "domain_relevance",
        }
        assert expected.issubset(set(FACT_COLS))

    def test_empty_inputs_returns_empty_df(self):
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_output_has_schema_columns(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        for col in FACT_COLS:
            assert col in df.columns, f"Missing column: {col}"


# ── Tracks → present facts ─────────────────────────────────────────────────────

class TestTrackFacts:
    def test_present_fact_for_each_track(self):
        tracks = _make_tracks(
            track_id=["trk_a", "trk_b"],
            frame_idx=[0, 5],
            start_frame_idx=[0, 5],
            end_frame_idx=[30, 40],
            semantic_class=["workpiece", "hand"],
            object_role=["workpiece", "hand"],
            confidence=[0.9, 0.95],
        )
        df = compute_state_facts(tracks, pd.DataFrame(), pd.DataFrame())
        present = df[df["predicate"] == "present"]
        assert len(present) == 2
        assert set(present["subject_id"]) == {"trk_a", "trk_b"}

    def test_present_fact_status_active(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        present = df[df["predicate"] == "present"]
        assert all(present["status"] == "active")

    def test_present_fact_frame_window(self):
        # Two rows for same track so min/max differ
        tracks = pd.DataFrame({
            "track_id": ["trk_a", "trk_a"],
            "frame_idx": [10, 50],
            "start_frame_idx": [10, 50], "end_frame_idx": [50, 50],
            "semantic_class": ["workpiece", "workpiece"],
            "object_role": ["workpiece", "workpiece"],
            "confidence": [0.9, 0.9],
        })
        df = compute_state_facts(tracks, pd.DataFrame(), pd.DataFrame())
        row = df[df["predicate"] == "present"].iloc[0]
        assert row["start_frame_idx"] == 10
        assert row["end_frame_idx"] == 50

    def test_source_stage_is_tracks(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        present = df[df["predicate"] == "present"]
        assert all(present["source_stage"] == "tracks")


# ── Events → facts ─────────────────────────────────────────────────────────────

class TestEventFacts:
    def test_move_event_produces_started_moving(self):
        events = _make_events(event_type=["MOVE"])
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        assert "started_moving" in df["predicate"].values

    def test_appear_event_produces_appeared(self):
        events = _make_events(event_type=["APPEAR"])
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        assert "appeared" in df["predicate"].values

    def test_disappear_event_produces_disappeared(self):
        events = _make_events(event_type=["DISAPPEAR"])
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        assert "disappeared" in df["predicate"].values

    def test_co_locate_event_produces_near(self):
        events = pd.DataFrame({
            "event_id": ["ev_001"],
            "event_type": ["CO_LOCATE"],
            "primary_track_ids": ['["trk_a", "trk_b"]'],
            "start_frame_idx": [5],
            "end_frame_idx": [10],
            "confidence": [0.8],
        })
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        assert "near" in df["predicate"].values

    def test_interaction_event_produces_touching_candidate(self):
        events = pd.DataFrame({
            "event_id": ["ev_001"],
            "event_type": ["INTERACTION"],
            "primary_track_ids": ['["trk_a", "trk_b"]'],
            "start_frame_idx": [5],
            "end_frame_idx": [10],
            "confidence": [0.7],
        })
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        assert "touching_candidate" in df["predicate"].values

    def test_unknown_event_type_is_skipped(self):
        events = _make_events(event_type=["UNKNOWN_XYZ"])
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        # Should not raise and should produce no fact with "unknown" predicate
        assert "UNKNOWN_XYZ" not in df["predicate"].values

    def test_source_stage_is_events(self):
        events = _make_events(event_type=["MOVE"])
        df = compute_state_facts(pd.DataFrame(), events, pd.DataFrame())
        ev_facts = df[df["source_stage"] == "events"]
        assert len(ev_facts) > 0


# ── Operations → facts ─────────────────────────────────────────────────────────

class TestOperationFacts:
    def test_hold_op_produces_holding(self):
        ops = _make_ops(operation_type=["HOLD"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "holding" in df["predicate"].values

    def test_pick_up_op_produces_holding(self):
        ops = _make_ops(operation_type=["PICK_UP"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "holding" in df["predicate"].values

    def test_put_down_op_produces_released(self):
        ops = _make_ops(operation_type=["PUT_DOWN"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "released" in df["predicate"].values

    def test_contact_op_produces_in_contact(self):
        ops = _make_ops(operation_type=["CONTACT"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "in_contact" in df["predicate"].values

    def test_insert_candidate_produces_inserted_into_candidate(self):
        ops = _make_ops(operation_type=["INSERT_CANDIDATE"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "inserted_into_candidate" in df["predicate"].values

    def test_place_onto_candidate_produces_placed_on_candidate(self):
        ops = _make_ops(operation_type=["PLACE_ONTO_CANDIDATE"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "placed_on_candidate" in df["predicate"].values

    def test_align_candidate_produces_aligned_with_candidate(self):
        ops = _make_ops(operation_type=["ALIGN_CANDIDATE"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "aligned_with_candidate" in df["predicate"].values

    def test_attach_candidate_produces_attached_to_candidate(self):
        ops = _make_ops(operation_type=["ATTACH_CANDIDATE"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert "attached_to_candidate" in df["predicate"].values

    def test_holding_fact_subject_is_agent(self):
        ops = _make_ops(operation_type=["HOLD"], agent_track_id=["trk_hand"], object_track_id=["trk_part"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        holding = df[df["predicate"] == "holding"]
        assert holding.iloc[0]["subject_id"] == "trk_hand"
        assert holding.iloc[0]["object_id"] == "trk_part"

    def test_op_evidence_ref_recorded(self):
        ops = _make_ops(operation_id=["op_007"], operation_type=["HOLD"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        holding = df[df["predicate"] == "holding"].iloc[0]
        assert "op_007" in str(holding["evidence_refs"])

    def test_source_stage_is_operations(self):
        ops = _make_ops(operation_type=["HOLD"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        op_facts = df[df["source_stage"] == "operations"]
        assert len(op_facts) > 0


# ── Support state → facts ──────────────────────────────────────────────────────

class TestSupportStateFacts:
    def _make_support(self, **overrides):
        data = dict(
            track_id=["trk_a"],
            state=["CARRIED"],
            start_frame_idx=[5],
            end_frame_idx=[15],
            trigger_operation_id=["op_001"],
        )
        data.update(overrides)
        return pd.DataFrame(data)

    def test_carried_produces_carried_fact(self):
        support = self._make_support(state=["CARRIED"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support)
        assert "carried" in df["predicate"].values

    def test_in_contact_produces_surface_contact(self):
        support = self._make_support(state=["IN_CONTACT"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support)
        assert "surface_contact" in df["predicate"].values

    def test_resting_produces_resting_fact(self):
        support = self._make_support(state=["RESTING"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support)
        assert "resting" in df["predicate"].values

    def test_source_stage_is_support_state(self):
        support = self._make_support(support_state=["CARRIED"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support)
        ss_facts = df[df["source_stage"] == "support_state"]
        assert len(ss_facts) > 0


# ── Domain relevance ───────────────────────────────────────────────────────────

class _FakePred:
    def __init__(self, name):
        self.name = name


class _FakeDomainRelevance:
    def __init__(self):
        self.assembly_predicates = [_FakePred("holding"), _FakePred("in_contact")]

    def assembly_predicate_names(self):
        return [p.name for p in self.assembly_predicates]


class TestDomainRelevance:

    def test_domain_relevance_set_for_matching_predicates(self):
        ops = _make_ops(operation_type=["HOLD"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops,
                                 domain_config=_FakeDomainRelevance())
        holding = df[df["predicate"] == "holding"].iloc[0]
        assert holding["domain_relevance"] == True  # noqa: E712

    def test_domain_relevance_false_for_non_domain_predicates(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame(),
                                 domain_config=_FakeDomainRelevance())
        present = df[df["predicate"] == "present"].iloc[0]
        assert present["domain_relevance"] == False  # noqa: E712

    def test_no_domain_config_relevance_defaults_to_true(self):
        # Without domain config all facts default to relevant (empty predicate set = match all)
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        assert all(df["domain_relevance"] == True)  # noqa: E712


# ── Unique fact IDs ────────────────────────────────────────────────────────────

class TestFactIds:
    def test_all_fact_ids_unique(self):
        tracks = _make_tracks(
            track_id=["trk_a", "trk_b"],
            frame_idx=[0, 5],
            start_frame_idx=[0, 5], end_frame_idx=[30, 40],
            semantic_class=["workpiece", "hand"],
            object_role=["workpiece", "hand"],
            confidence=[0.9, 0.95],
        )
        ops = _make_ops()
        df = compute_state_facts(tracks, pd.DataFrame(), ops)
        assert df["fact_id"].nunique() == len(df)


# ── Utility functions ──────────────────────────────────────────────────────────

# ── Support-state transition facts (Milestone 10) ─────────────────────────────

def _make_support(rows):
    """rows: list of (track_id, state, start_frame, end_frame, trigger_op_id)"""
    records = []
    for r in rows:
        tid, state, start_f, end_f, trig = r
        records.append(dict(
            track_id=tid, state=state,
            start_frame_idx=start_f, end_frame_idx=end_f,
            trigger_operation_id=trig,
        ))
    return pd.DataFrame(records)


class TestSupportTransitionFacts:
    def test_carried_resting_emits_released_fact(self):
        support = _make_support([
            ("trk_a", "CARRIED", 5, 10, "op_001"),
            ("trk_a", "RESTING", 11, 20, None),
        ])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support_df=support)
        released = df[df["predicate"] == "released"]
        assert len(released) > 0
        assert released.iloc[0]["subject_id"] == "trk_a"
        assert released.iloc[0]["status"] == "achieved"

    def test_carried_resting_emits_support_changed_fact(self):
        support = _make_support([
            ("trk_a", "CARRIED", 5, 10, "op_001"),
            ("trk_a", "RESTING", 11, 20, None),
        ])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support_df=support)
        changed = df[df["predicate"] == "support_changed"]
        assert len(changed) > 0

    def test_resting_carried_does_not_emit_released(self):
        support = _make_support([
            ("trk_a", "RESTING", 0, 5, None),
            ("trk_a", "CARRIED", 6, 15, "op_001"),
        ])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support_df=support)
        released = df[df["predicate"] == "released"]
        # RESTING→CARRIED should not produce a 'released' fact
        assert len(released) == 0

    def test_multiple_tracks_get_independent_transitions(self):
        support = _make_support([
            ("trk_a", "CARRIED", 5, 10, "op_001"),
            ("trk_a", "RESTING", 11, 20, None),
            ("trk_b", "CARRIED", 3, 8, "op_002"),
            ("trk_b", "RESTING", 9, 18, None),
        ])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), support_df=support)
        released = df[df["predicate"] == "released"]
        assert set(released["subject_id"]) == {"trk_a", "trk_b"}

    def test_no_support_df_produces_no_transition_facts(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        assert len(df[df["predicate"] == "released"]) == 0
        assert len(df[df["predicate"] == "support_changed"]) == 0


class TestUtilityFunctions:
    def test_active_facts_filters_active_status(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        act = active_facts(df)
        assert all(act["status"].isin({"active", "achieved"}))

    def test_facts_for_predicate_filters_correctly(self):
        ops = _make_ops(operation_type=["HOLD"])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        holding = facts_for_predicate(df, "holding")
        assert all(holding["predicate"] == "holding")
        assert len(holding) > 0


# ── Inter-object relation facts (Milestone 11) ────────────────────────────────

def _make_ops_multi(**rows):
    """Two HOLD ops by same agent on different objects with overlapping windows."""
    defaults = dict(
        operation_id=["op_001", "op_002"],
        operation_type=["HOLD", "HOLD"],
        agent_track_id=["trk_hand", "trk_hand"],
        object_track_id=["trk_a", "trk_b"],
        start_frame_idx=[5, 5],
        end_frame_idx=[15, 12],
        confidence=[0.8, 0.8],
    )
    defaults.update(rows)
    return pd.DataFrame(defaults)


class TestCoHeldFacts:
    def test_co_held_fact_generated_from_overlapping_hold_ops(self):
        ops = _make_ops_multi()
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        co = df[df["predicate"] == "co_held"]
        assert len(co) == 1
        row = co.iloc[0]
        assert row["subject_id"] in ("trk_a", "trk_b")
        assert row["object_id"] in ("trk_a", "trk_b")
        assert row["subject_id"] != row["object_id"]

    def test_co_held_overlap_window_is_correct(self):
        ops = _make_ops_multi(start_frame_idx=[5, 8], end_frame_idx=[20, 15])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        co = df[df["predicate"] == "co_held"]
        assert len(co) == 1
        row = co.iloc[0]
        assert row["start_frame_idx"] == 8   # max(5, 8)
        assert row["end_frame_idx"]   == 15  # min(20, 15)

    def test_co_held_started_and_ended_markers_emitted(self):
        ops = _make_ops_multi()
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert len(df[df["predicate"] == "co_held_started"]) == 1
        assert len(df[df["predicate"] == "co_held_ended"])   == 1

    def test_co_held_started_is_point_fact(self):
        ops = _make_ops_multi(start_frame_idx=[5, 5], end_frame_idx=[15, 12])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        started = df[df["predicate"] == "co_held_started"].iloc[0]
        assert started["start_frame_idx"] == started["end_frame_idx"]

    def test_co_held_not_generated_for_non_overlapping_windows(self):
        ops = _make_ops_multi(start_frame_idx=[5, 20], end_frame_idx=[15, 30])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert len(df[df["predicate"] == "co_held"]) == 0

    def test_co_held_not_generated_for_single_hold_op(self):
        ops = _make_ops()  # only one HOLD
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        assert len(df[df["predicate"] == "co_held"]) == 0

    def test_co_held_skips_hand_tracks(self):
        # Hand as one of the objects — should not be co_held with another hand object
        ops = pd.DataFrame({
            "operation_id":    ["op_001", "op_002"],
            "operation_type":  ["HOLD", "HOLD"],
            "agent_track_id":  ["trk_hand", "trk_hand"],
            "object_track_id": ["trk_hand2", "trk_a"],
            "start_frame_idx": [5, 5],
            "end_frame_idx":   [15, 15],
            "confidence":      [0.8, 0.8],
        })
        tracks = pd.DataFrame({
            "track_id":       ["trk_hand2", "trk_a"],
            "frame_idx":      [0, 0],
            "semantic_class": ["hand", "workpiece"],
        })
        df = compute_state_facts(tracks, pd.DataFrame(), ops)
        co = df[df["predicate"] == "co_held"]
        # trk_hand2 is a hand track, so it should be excluded
        assert len(co) == 0

    def test_co_held_status_is_active(self):
        ops = _make_ops_multi()
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        co = df[df["predicate"] == "co_held"]
        assert co.iloc[0]["status"] == "active"

    def test_co_held_confidence_downgraded_from_source_ops(self):
        ops = _make_ops_multi(confidence=[0.9, 0.8])
        df = compute_state_facts(pd.DataFrame(), pd.DataFrame(), ops)
        co = df[df["predicate"] == "co_held"]
        # Should be min(0.9, 0.8) * 0.9 = 0.72
        assert abs(co.iloc[0]["confidence"] - 0.72) < 0.01

    def test_facts_to_json_serialisable(self):
        df = compute_state_facts(_make_tracks(), pd.DataFrame(), pd.DataFrame())
        data = facts_to_json(df)
        assert isinstance(data, list)
        if data:
            assert "fact_id" in data[0]
            assert "predicate" in data[0]
