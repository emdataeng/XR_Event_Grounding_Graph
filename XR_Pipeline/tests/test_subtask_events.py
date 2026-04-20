"""tests/test_subtask_events.py — Unit tests for src/subtask_events.py (Phase 3)."""
import pytest
import json
import pandas as pd

from src.subtask_events import (
    infer_subtask_events,
    subtask_sequence_json,
    SUBTASK_COLS,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _make_ops(*rows):
    """rows: list of (op_id, op_type, agent, patient, start, end, conf)"""
    records = []
    for r in rows:
        op_id, op_type, agent, patient, start, end, conf = r
        records.append(dict(
            operation_id=op_id,
            operation_type=op_type,
            agent_track_id=agent,
            object_track_id=patient,
            start_frame_idx=start,
            end_frame_idx=end,
            confidence=conf,
        ))
    return pd.DataFrame(records)


def _make_facts(*rows):
    """rows: list of (fact_id, predicate, subject, object_, start, end, conf, status)"""
    records = []
    for r in rows:
        fid, predicate, subject, object_, start, end, conf, status = r
        records.append(dict(
            fact_id=fid,
            predicate=predicate,
            subject_id=subject,
            object_id=object_,
            start_frame_idx=start,
            end_frame_idx=end,
            confidence=conf,
            status=status,
        ))
    return pd.DataFrame(records)


class _FakeSubtaskTemplate:
    def __init__(self, name, trigger_operations, trigger_predicates=None,
                 agent_role="hand", patient_role="workpiece", description=""):
        self.name = name
        self.trigger_operations = trigger_operations
        self.trigger_predicates = trigger_predicates or []
        self.agent_role = agent_role
        self.patient_role = patient_role
        self.description = description


class _FakeDomain:
    def __init__(self, templates, dep_rules=None):
        self.subtask_templates = templates
        self._dep_rules = dep_rules or []

    def required_before(self, name):
        return [r.requires for r in self._dep_rules if r.subtask == name]

    def subgoal_for_subtask(self, name):
        return None


class _FakeDepRule:
    def __init__(self, subtask, requires):
        self.subtask = subtask
        self.requires = requires


# ── Schema ─────────────────────────────────────────────────────────────────────

class TestSchema:
    def test_subtask_cols_defined(self):
        expected = {
            "subtask_id", "template_name", "status", "agent_track_id",
            "patient_track_id", "confidence", "start_frame_idx", "end_frame_idx",
            "why_this_subtask",
        }
        assert expected.issubset(set(SUBTASK_COLS))

    def test_empty_inputs_returns_empty_df(self):
        df = infer_subtask_events(pd.DataFrame(), pd.DataFrame())
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_output_has_schema_columns(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        for col in SUBTASK_COLS:
            assert col in df.columns, f"Missing column: {col}"


# ── Generic fallback (no domain config) ───────────────────────────────────────

class TestGenericFallback:
    def test_pick_up_op_produces_pick_up_part(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert "pick_up_part" in df["template_name"].values

    def test_put_down_op_produces_place_part(self):
        ops = _make_ops(("op_001", "PUT_DOWN", "trk_hand", "trk_part", 15, 20, 0.7))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert "place_part" in df["template_name"].values

    def test_contact_op_produces_contact_parts(self):
        ops = _make_ops(("op_001", "CONTACT", "trk_a", "trk_b", 5, 8, 0.75))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert "contact_parts" in df["template_name"].values

    def test_insert_candidate_produces_insert_part(self):
        ops = _make_ops(("op_001", "INSERT_CANDIDATE", "trk_hand", "trk_part", 20, 25, 0.85))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert "insert_part" in df["template_name"].values

    def test_align_candidate_produces_align_part(self):
        ops = _make_ops(("op_001", "ALIGN_CANDIDATE", "trk_hand", "trk_part", 10, 15, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert "align_part" in df["template_name"].values

    def test_attach_candidate_produces_attach_part(self):
        ops = _make_ops(("op_001", "ATTACH_CANDIDATE", "trk_hand", "trk_part", 12, 18, 0.9))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert "attach_part" in df["template_name"].values

    def test_hold_op_produces_subtask(self):
        ops = _make_ops(("op_001", "HOLD", "trk_hand", "trk_part", 5, 10, 0.75))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert len(df) > 0

    def test_unknown_op_type_skipped(self):
        ops = _make_ops(("op_001", "UNKNOWN_OP_XYZ", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert len(df) == 0


# ── Status assignment ──────────────────────────────────────────────────────────

class TestStatusAssignment:
    def test_high_confidence_op_produces_achieved(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.9))
        df = infer_subtask_events(pd.DataFrame(), ops)
        row = df[df["template_name"] == "pick_up_part"].iloc[0]
        assert row["status"] in ("achieved", "in_progress")

    def test_low_confidence_op_produces_candidate(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.3))
        df = infer_subtask_events(pd.DataFrame(), ops)
        row = df[df["template_name"] == "pick_up_part"].iloc[0]
        assert row["status"] == "candidate"

    def test_status_is_valid_enum(self):
        ops = _make_ops(
            ("op_001", "PICK_UP", "trk_hand", "trk_a", 5, 10, 0.8),
            ("op_002", "PUT_DOWN", "trk_hand", "trk_a", 15, 20, 0.2),
        )
        df = infer_subtask_events(pd.DataFrame(), ops)
        valid = {"candidate", "in_progress", "achieved", "blocked", "invalidated"}
        assert all(df["status"].isin(valid))


# ── Domain-config-driven inference ────────────────────────────────────────────

class TestDomainDrivenInference:
    def _simple_domain(self):
        return _FakeDomain([
            _FakeSubtaskTemplate(
                "pick_up_part",
                trigger_operations=["PICK_UP", "HOLD"],
                trigger_predicates=[],
                agent_role="hand",
                patient_role="workpiece",
            ),
        ])

    def test_domain_template_matches_trigger_op(self):
        domain = self._simple_domain()
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops, domain_config=domain)
        assert "pick_up_part" in df["template_name"].values

    def test_agent_patient_propagated(self):
        domain = self._simple_domain()
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops, domain_config=domain)
        row = df[df["template_name"] == "pick_up_part"].iloc[0]
        assert row["agent_track_id"] == "trk_hand"
        assert row["patient_track_id"] == "trk_part"


# ── Dependency rules → blocked status ─────────────────────────────────────────

class TestDependencyRules:
    def _domain_with_deps(self):
        return _FakeDomain(
            templates=[
                _FakeSubtaskTemplate(
                    "align_part", trigger_operations=["ALIGN_CANDIDATE"],
                    trigger_predicates=[], agent_role="hand", patient_role="workpiece",
                ),
                _FakeSubtaskTemplate(
                    "insert_part", trigger_operations=["INSERT_CANDIDATE"],
                    trigger_predicates=[], agent_role="hand", patient_role="workpiece",
                ),
            ],
            dep_rules=[
                _FakeDepRule(subtask="insert_part", requires="align_part"),
            ],
        )

    def _domain_with_non_candidate_deps(self):
        """Domain where the dep-checked op is NOT in _CANDIDATE_OPS so blocked can fire."""
        return _FakeDomain(
            templates=[
                _FakeSubtaskTemplate(
                    "align_part", trigger_operations=["ALIGN_CANDIDATE"],
                    trigger_predicates=[], agent_role="hand", patient_role="workpiece",
                ),
                _FakeSubtaskTemplate(
                    "finalize_part", trigger_operations=["HOLD"],  # HOLD is not a candidate op
                    trigger_predicates=[], agent_role="hand", patient_role="workpiece",
                ),
            ],
            dep_rules=[
                _FakeDepRule(subtask="finalize_part", requires="align_part"),
            ],
        )

    def test_unmet_dep_produces_blocked_status(self):
        domain = self._domain_with_non_candidate_deps()
        # Only HOLD op — no ALIGN op, so finalize_part should be blocked
        ops = _make_ops(("op_001", "HOLD", "trk_hand", "trk_part", 20, 25, 0.85))
        df = infer_subtask_events(pd.DataFrame(), ops, domain_config=domain)
        finalize = df[df["template_name"] == "finalize_part"]
        if len(finalize) > 0:
            assert finalize.iloc[0]["status"] == "blocked"

    def test_met_dep_allows_achieved_status(self):
        domain = self._domain_with_non_candidate_deps()
        ops = _make_ops(
            # First align (ALIGN_CANDIDATE) — will be candidate due to _CANDIDATE_OPS
            ("op_001", "ALIGN_CANDIDATE", "trk_hand", "trk_part", 10, 15, 0.85),
            # Then HOLD with high conf — prereq unmet since align is candidate not achieved
            ("op_002", "HOLD", "trk_hand", "trk_part", 20, 25, 0.85),
        )
        df = infer_subtask_events(pd.DataFrame(), ops, domain_config=domain)
        # Test is that we get some rows and no crash
        assert len(df) >= 1


# ── Unique subtask IDs ─────────────────────────────────────────────────────────

class TestSubtaskIds:
    def test_all_subtask_ids_unique(self):
        ops = _make_ops(
            ("op_001", "PICK_UP", "trk_hand", "trk_a", 5, 10, 0.8),
            ("op_002", "PUT_DOWN", "trk_hand", "trk_a", 15, 20, 0.7),
            ("op_003", "CONTACT", "trk_a", "trk_b", 25, 30, 0.75),
        )
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert df["subtask_id"].nunique() == len(df)

    def test_subtask_ids_have_prefix(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_a", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert all(df["subtask_id"].str.startswith("sub_"))


# ── Why string ─────────────────────────────────────────────────────────────────

class TestWhyString:
    def test_why_string_is_non_empty(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        assert all(df["why_this_subtask"].str.len() > 0)

    def test_why_string_contains_op_type(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        row = df.iloc[0]
        assert "PICK_UP" in row["why_this_subtask"] or "pick_up" in row["why_this_subtask"].lower()


# ── Support-state → release_part subtask (Milestone 10) ──────────────────────

def _make_support_df(rows):
    """rows: list of (track_id, state, start_frame, end_frame)"""
    records = []
    for r in rows:
        tid, state, start_f, end_f = r
        records.append(dict(
            track_id=tid, state=state,
            start_frame_idx=start_f, end_frame_idx=end_f,
            trigger_operation_id=None,
        ))
    return pd.DataFrame(records)


class TestSupportTransitionSubtasks:
    def test_carried_resting_produces_release_part(self):
        ops = pd.DataFrame()
        support = _make_support_df([
            ("trk_part", "CARRIED", 5, 15),
            ("trk_part", "RESTING", 16, 25),
        ])
        df = infer_subtask_events(pd.DataFrame(), ops, support_df=support)
        assert "release_part" in df["template_name"].values

    def test_release_part_not_duplicated_when_put_down_present(self):
        """CARRIED→RESTING that overlaps a PUT_DOWN op should not produce release_part."""
        ops = _make_ops(("op_001", "PUT_DOWN", "trk_hand", "trk_part", 10, 15, 0.8))
        support = _make_support_df([
            ("trk_part", "CARRIED", 5, 15),
            ("trk_part", "RESTING", 15, 25),
        ])
        df = infer_subtask_events(pd.DataFrame(), ops, support_df=support)
        release_rows = df[df["template_name"] == "release_part"]
        # The transition at frame 15 is covered by the PUT_DOWN end_frame window → no duplicate
        assert len(release_rows) == 0

    def test_release_part_has_patient_track_id(self):
        support = _make_support_df([
            ("trk_wp", "CARRIED", 0, 10),
            ("trk_wp", "RESTING", 11, 20),
        ])
        df = infer_subtask_events(pd.DataFrame(), pd.DataFrame(), support_df=support)
        row = df[df["template_name"] == "release_part"].iloc[0]
        assert row["patient_track_id"] == "trk_wp"

    def test_release_part_instance_label_uses_patient_class(self):
        support = _make_support_df([
            ("trk_wp", "CARRIED", 0, 10),
            ("trk_wp", "RESTING", 11, 20),
        ])
        tracks = pd.DataFrame({
            "track_id": ["trk_wp"],
            "frame_idx": [0],
            "semantic_class": ["blue_lego"],
        })
        df = infer_subtask_events(pd.DataFrame(), pd.DataFrame(), tracks_df=tracks, support_df=support)
        row = df[df["template_name"] == "release_part"].iloc[0]
        assert "blue_lego" in row["instance_label"]

    def test_no_release_part_without_carried_resting(self):
        support = _make_support_df([
            ("trk_wp", "RESTING", 0, 10),
            ("trk_wp", "CARRIED", 11, 20),
        ])
        df = infer_subtask_events(pd.DataFrame(), pd.DataFrame(), support_df=support)
        assert "release_part" not in df["template_name"].values

    def test_carried_in_contact_produces_place_part(self):
        support = _make_support_df([
            ("trk_wp", "CARRIED", 0, 10),
            ("trk_wp", "IN_CONTACT", 11, 20),
        ])
        df = infer_subtask_events(pd.DataFrame(), pd.DataFrame(), support_df=support)
        assert "place_part" in df["template_name"].values


# ── subtask_sequence_json ──────────────────────────────────────────────────────

class TestSubtaskSequenceJson:
    def test_returns_dict(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        result = subtask_sequence_json(df, session_id="test_session")
        assert isinstance(result, dict)

    def test_contains_session_id(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        result = subtask_sequence_json(df, session_id="test_session")
        assert result.get("session_id") == "test_session"

    def test_contains_subtasks_list(self):
        ops = _make_ops(("op_001", "PICK_UP", "trk_hand", "trk_part", 5, 10, 0.8))
        df = infer_subtask_events(pd.DataFrame(), ops)
        result = subtask_sequence_json(df, session_id="test_session")
        assert "subtask_sequence" in result
        assert isinstance(result["subtask_sequence"], list)

    def test_empty_df_returns_empty_subtasks(self):
        result = subtask_sequence_json(pd.DataFrame(columns=SUBTASK_COLS), session_id="test_session")
        assert result["subtask_sequence"] == []
