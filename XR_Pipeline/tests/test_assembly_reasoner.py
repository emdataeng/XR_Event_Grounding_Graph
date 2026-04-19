"""tests/test_assembly_reasoner.py — Unit tests for src/assembly_reasoner.py (Phase 6)."""
import pytest

from src.assembly_reasoner import reason, answer_assembly_query


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _pkg(**overrides):
    base = {
        "session_id": "test_session",
        "active_facts": [],
        "active_subtasks": [],
        "achieved_subgoals": [],
        "blocked_subgoals": [],
        "likely_next_subtasks": [],
        "current_assembly_phase": "idle",
        "constraint_satisfaction": {},
        "unresolved_ambiguities": [],
        "evidence_summary": {
            "total_active_facts": 0,
            "total_active_subtasks": 0,
            "total_achieved_subgoals": 0,
            "total_blocked": 0,
        },
    }
    base.update(overrides)
    return base


def _subtask(sid="sub_0001", tmpl="pick_up_part", status="in_progress",
             conf=0.8, frames=None, why="PICK_UP op_001"):
    return {
        "subtask_id": sid,
        "template_name": tmpl,
        "status": status,
        "confidence": conf,
        "frames": frames or [5, 12],
        "agent": "trk_hand",
        "patient": "trk_part",
        "why": why,
    }


def _fact(fid="fact_0001", predicate="holding", subject="trk_hand", obj="trk_a",
          conf=0.8, frames=None):
    return {
        "fact_id": fid,
        "predicate": predicate,
        "subject_id": subject,
        "object_id": obj,
        "confidence": conf,
        "frames": frames or [5, 12],
        "source": "operations",
    }


def _graph_with_subtask(sid="sub_0001", tmpl="pick_up_part"):
    return {
        "nodes": [
            {
                "node_id": sid,
                "node_type": "subtask",
                "template_name": tmpl,
                "status": "in_progress",
                "confidence": 0.8,
                "start_frame": 5,
                "end_frame": 12,
                "agent": "trk_hand",
                "patient": "trk_part",
                "why": "PICK_UP op_001",
            }
        ],
        "edges": [],
        "summary": {"total_nodes": 1, "total_edges": 0},
    }


# ── Return structure ───────────────────────────────────────────────────────────

class TestReturnStructure:
    def test_reason_returns_dict(self):
        result = reason(_pkg())
        assert isinstance(result, dict)

    def test_full_report_has_all_keys(self):
        result = reason(_pkg(), query="full_report")
        for key in ("current_step", "achieved", "blocked", "recent_changes",
                    "likely_next", "current_step_evidence", "current_phase",
                    "constraint_status", "reasoning_trace"):
            assert key in result, f"Missing key: {key}"

    def test_session_id_propagated(self):
        result = reason(_pkg(session_id="my_session"))
        assert result["session_id"] == "my_session"

    def test_query_field_set(self):
        result = reason(_pkg(), query="what_step_now")
        assert result["query"] == "what_step_now"

    def test_reasoning_trace_is_list(self):
        result = reason(_pkg())
        assert isinstance(result["reasoning_trace"], list)

    def test_none_package_does_not_crash(self):
        result = reason(None)
        assert isinstance(result, dict)


# ── what_step_now ──────────────────────────────────────────────────────────────

class TestWhatStepNow:
    def test_no_active_subtasks_returns_none_step(self):
        result = reason(_pkg(), query="what_step_now")
        assert result.get("step") is None

    def test_active_subtask_returned(self):
        pkg = _pkg(active_subtasks=[_subtask()])
        result = reason(pkg, query="what_step_now")
        assert result["step"] is not None
        assert result["step"]["template_name"] == "pick_up_part"

    def test_most_recent_by_end_frame_selected(self):
        pkg = _pkg(active_subtasks=[
            _subtask(sid="sub_0001", tmpl="pick_up_part", frames=[5, 10]),
            _subtask(sid="sub_0002", tmpl="place_part", frames=[15, 25]),
        ])
        result = reason(pkg, query="what_step_now")
        assert result["step"]["template_name"] == "place_part"

    def test_answer_string_non_empty(self):
        pkg = _pkg(active_subtasks=[_subtask()])
        result = reason(pkg, query="what_step_now")
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0


# ── what_is_achieved ───────────────────────────────────────────────────────────

class TestWhatIsAchieved:
    def test_no_achieved_returns_empty_list(self):
        result = reason(_pkg(), query="what_is_achieved")
        assert result.get("achieved_subgoals") == []

    def test_achieved_subgoals_returned(self):
        pkg = _pkg(achieved_subgoals=[
            {"name": "part_is_held", "predicate": "holding", "achieved_by_subtask": "sub_0001"},
        ])
        result = reason(pkg, query="what_is_achieved")
        goals = result["achieved_subgoals"]
        assert len(goals) == 1
        assert goals[0]["name"] == "part_is_held"

    def test_answer_contains_subgoal_name(self):
        pkg = _pkg(achieved_subgoals=[
            {"name": "part_is_held", "predicate": "holding", "achieved_by_subtask": None},
        ])
        result = reason(pkg, query="what_is_achieved")
        assert "part_is_held" in result["answer"]


# ── what_is_blocked ────────────────────────────────────────────────────────────

class TestWhatIsBlocked:
    def test_no_blocked_returns_empty(self):
        result = reason(_pkg(), query="what_is_blocked")
        assert result["blocked_steps"] == []
        assert result["violated_constraints"] == []

    def test_blocked_subtask_returned(self):
        pkg = _pkg(active_subtasks=[
            _subtask(sid="sub_001", tmpl="insert_part", status="blocked"),
        ])
        result = reason(pkg, query="what_is_blocked")
        assert len(result["blocked_steps"]) == 1

    def test_violated_constraints_returned(self):
        pkg = _pkg(constraint_satisfaction={
            "insert_part_requires_align_part": {
                "satisfied": False,
                "subtask": "insert_part",
                "requires": "align_part",
                "description": "must align first",
            }
        })
        result = reason(pkg, query="what_is_blocked")
        assert "insert_part_requires_align_part" in result["violated_constraints"]


# ── what_changed ───────────────────────────────────────────────────────────────

class TestWhatChanged:
    def test_no_frames_returns_empty(self):
        result = reason(_pkg(), query="what_changed")
        assert result["recent_changes"] == []

    def test_recent_fact_detected(self):
        pkg = _pkg(active_facts=[
            _fact(fid="fact_0001", frames=[95, 105]),
            _fact(fid="fact_0002", frames=[50, 60]),  # old
        ])
        result = reason(pkg, query="what_changed", recent_frame_window=20)
        changes = result["recent_changes"]
        fact_changes = [c for c in changes if c["type"] == "fact"]
        assert len(fact_changes) >= 1

    def test_recent_subtask_detected(self):
        pkg = _pkg(active_subtasks=[
            _subtask(sid="sub_0001", frames=[90, 100]),
        ])
        result = reason(pkg, query="what_changed", recent_frame_window=20)
        changes = result["recent_changes"]
        sub_changes = [c for c in changes if c["type"] == "subtask"]
        assert len(sub_changes) >= 1

    def test_changes_sorted_newest_first(self):
        pkg = _pkg(active_facts=[
            _fact(fid="fact_0001", frames=[80, 90]),
            _fact(fid="fact_0002", frames=[95, 100]),
        ])
        result = reason(pkg, query="what_changed", recent_frame_window=30)
        changes = result["recent_changes"]
        if len(changes) >= 2:
            assert changes[0]["frame"] >= changes[1]["frame"]


# ── likely_next ────────────────────────────────────────────────────────────────

class TestLikelyNext:
    def test_empty_package_returns_empty(self):
        result = reason(_pkg(), query="likely_next")
        assert result["likely_next_subtasks"] == []

    def test_likely_next_returned_from_package(self):
        pkg = _pkg(likely_next_subtasks=[
            {"template_name": "align_part", "description": "align before insert", "prerequisites_met": []},
        ])
        result = reason(pkg, query="likely_next")
        nxt = result["likely_next_subtasks"]
        assert len(nxt) == 1
        assert nxt[0]["template_name"] == "align_part"

    def test_answer_contains_template_name(self):
        pkg = _pkg(likely_next_subtasks=[
            {"template_name": "align_part", "description": "", "prerequisites_met": []},
        ])
        result = reason(pkg, query="likely_next")
        assert "align_part" in result["answer"]


# ── why_current_step ───────────────────────────────────────────────────────────

class TestWhyCurrentStep:
    def test_no_active_step_returns_empty_evidence(self):
        result = reason(_pkg(), query="why_current_step")
        assert result["evidence"] == []

    def test_why_field_used_as_evidence(self):
        pkg = _pkg(active_subtasks=[
            _subtask(why="PICK_UP op_007 with holding(trk_hand, trk_part)"),
        ])
        result = reason(pkg, query="why_current_step")
        assert len(result["evidence"]) >= 1
        assert "op_007" in str(result["evidence"][0])

    def test_subtask_id_in_result(self):
        pkg = _pkg(active_subtasks=[_subtask(sid="sub_0042")])
        result = reason(pkg, query="why_current_step")
        assert result.get("subtask_id") == "sub_0042"

    def test_graph_evidence_for_edges_included(self):
        pkg = _pkg(active_subtasks=[_subtask(sid="sub_0001")])
        graph = {
            "nodes": [],
            "edges": [
                {"edge_id": "e_001", "edge_type": "evidence_for",
                 "source": "op_005", "target": "sub_0001"},
            ],
        }
        result = reason(pkg, graph, query="why_current_step")
        evidence_strs = [str(e) for e in result["evidence"]]
        assert any("op_005" in s for s in evidence_strs)


# ── constraint_status ──────────────────────────────────────────────────────────

class TestConstraintStatus:
    def test_empty_constraints_returns_zeros(self):
        result = reason(_pkg(), query="full_report")
        cs = result["constraint_status"]
        assert cs["satisfied"] == 0
        assert cs["violated"] == 0

    def test_satisfied_constraint_counted(self):
        pkg = _pkg(constraint_satisfaction={
            "pick_up_part_requires_nothing": {
                "satisfied": True,
                "subtask": "pick_up_part",
                "requires": "nothing",
                "description": "",
            }
        })
        result = reason(pkg, query="full_report")
        assert result["constraint_status"]["satisfied"] == 1

    def test_violated_constraint_counted(self):
        pkg = _pkg(constraint_satisfaction={
            "insert_part_requires_align_part": {
                "satisfied": False,
                "subtask": "insert_part",
                "requires": "align_part",
                "description": "",
            }
        })
        result = reason(pkg, query="full_report")
        assert result["constraint_status"]["violated"] == 1


# ── full_report ────────────────────────────────────────────────────────────────

class TestFullReport:
    def test_full_report_current_phase(self):
        pkg = _pkg(current_assembly_phase="manipulation")
        result = reason(pkg, query="full_report")
        assert result["current_phase"] == "manipulation"

    def test_full_report_integrates_all_queries(self):
        pkg = _pkg(
            active_subtasks=[_subtask()],
            achieved_subgoals=[{"name": "part_is_held", "predicate": "holding",
                                 "achieved_by_subtask": None}],
            current_assembly_phase="manipulation",
        )
        result = reason(pkg, query="full_report")
        assert result["current_step"]["step"] is not None
        assert len(result["achieved"]["achieved_subgoals"]) == 1

    def test_unknown_query_falls_back_to_full_report(self):
        result = reason(_pkg(), query="what_is_the_meaning_of_life")
        assert isinstance(result, dict)
        assert any("Unknown query" in t for t in result.get("reasoning_trace", []))


# ── answer_assembly_query (natural language) ──────────────────────────────────

class TestAnswerAssemblyQuery:
    def test_step_query(self):
        pkg = _pkg(active_subtasks=[_subtask()])
        answer = answer_assembly_query("What step is happening now?", pkg)
        assert isinstance(answer, str)
        assert "pick_up_part" in answer.lower() or "current" in answer.lower()

    def test_step_query_no_active(self):
        answer = answer_assembly_query("What step is active?", _pkg())
        assert "No active" in answer or "no" in answer.lower()

    def test_achieved_query(self):
        pkg = _pkg(achieved_subgoals=[
            {"name": "part_is_held", "predicate": "holding", "achieved_by_subtask": None}
        ])
        answer = answer_assembly_query("What has been assembled so far?", pkg)
        assert "part_is_held" in answer

    def test_achieved_query_empty(self):
        answer = answer_assembly_query("What is done?", _pkg())
        assert "No subgoals" in answer or "Nothing" in answer or "no" in answer.lower()

    def test_blocked_query(self):
        pkg = _pkg(active_subtasks=[
            _subtask(sid="sub_001", tmpl="insert_part", status="blocked"),
        ])
        answer = answer_assembly_query("What is blocked?", pkg)
        assert isinstance(answer, str)

    def test_next_query(self):
        pkg = _pkg(likely_next_subtasks=[
            {"template_name": "align_part", "description": "", "prerequisites_met": []}
        ])
        answer = answer_assembly_query("What comes next?", pkg)
        assert "align_part" in answer

    def test_evidence_query(self):
        pkg = _pkg(active_subtasks=[
            _subtask(why="PICK_UP op_007 detected near frame 10"),
        ])
        answer = answer_assembly_query("Why is this step active?", pkg)
        assert isinstance(answer, str)

    def test_changed_query(self):
        pkg = _pkg(active_facts=[_fact(frames=[95, 100])])
        answer = answer_assembly_query("What changed recently?", pkg)
        assert isinstance(answer, str)

    def test_fallback_query_returns_phase(self):
        pkg = _pkg(current_assembly_phase="contact")
        answer = answer_assembly_query("tell me everything", pkg)
        assert "contact" in answer.lower() or "phase" in answer.lower()
