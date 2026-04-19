"""tests/test_assembly_graph.py — Unit tests for src/assembly_graph.py (Phase 4)."""
import pytest
import pandas as pd

from src.assembly_graph import build_assembly_graph


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _tracks(**overrides):
    data = dict(
        track_id=["trk_a"],
        start_frame_idx=[0], end_frame_idx=[30],
        semantic_class=["workpiece"], object_role=["workpiece"],
    )
    data.update(overrides)
    return pd.DataFrame(data)


def _facts(**overrides):
    data = dict(
        fact_id=["fact_0001"],
        predicate=["holding"],
        subject_id=["trk_hand"],
        object_id=["trk_a"],
        status=["active"],
        confidence=[0.8],
        start_frame_idx=[5], end_frame_idx=[12],
        source_stage=["operations"],
    )
    data.update(overrides)
    return pd.DataFrame(data)


def _subtasks(**overrides):
    data = dict(
        subtask_id=["sub_0001"],
        template_name=["pick_up_part"],
        status=["achieved"],
        agent_track_id=["trk_hand"],
        patient_track_id=["trk_a"],
        target_track_id=[None],
        confidence=[0.85],
        start_frame_idx=[5], end_frame_idx=[12],
        why_this_subtask=["PICK_UP op_001"],
        supporting_facts=["[]"],
        supporting_operations=["[\"op_001\"]"],
    )
    data.update(overrides)
    return pd.DataFrame(data)


class _FakeSubgoalTemplate:
    def __init__(self, name, achieved_by, predicate):
        self.name = name
        self.achieved_by = achieved_by
        self.predicate = predicate


class _FakeDomain:
    def __init__(self, subgoal_templates=None, dep_rules=None):
        self.subgoal_templates = subgoal_templates or []
        self.dependency_rules = dep_rules or []
        self.subtask_templates = []

    def subgoal_for_subtask(self, name):
        for sg in self.subgoal_templates:
            if sg.achieved_by == name:
                return sg
        return None

    def required_before(self, name):
        return [r.requires for r in self.dependency_rules if r.subtask == name]


class _FakeDepRule:
    def __init__(self, subtask, requires, description=""):
        self.subtask = subtask
        self.requires = requires
        self.description = description


# ── Empty inputs ───────────────────────────────────────────────────────────────

class TestEmptyInputs:
    def test_all_empty_returns_valid_graph(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        assert "nodes" in g
        assert "edges" in g
        assert "summary" in g

    def test_empty_graph_has_zero_nodes(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        assert g["summary"]["total_nodes"] == 0
        assert g["summary"]["total_edges"] == 0

    def test_schema_version_present(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        assert g["schema_version"] == "1.0"

    def test_session_id_propagated(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                                 session_id="sess_test")
        assert g["session_id"] == "sess_test"


# ── Object nodes ───────────────────────────────────────────────────────────────

class TestObjectNodes:
    def test_tracks_produce_object_nodes(self):
        g = build_assembly_graph(_tracks(), pd.DataFrame(), pd.DataFrame())
        obj_nodes = [n for n in g["nodes"] if n["node_type"] == "object"]
        assert len(obj_nodes) == 1

    def test_object_node_id_has_obj_prefix(self):
        g = build_assembly_graph(_tracks(), pd.DataFrame(), pd.DataFrame())
        obj_nodes = [n for n in g["nodes"] if n["node_type"] == "object"]
        assert obj_nodes[0]["node_id"].startswith("obj_")

    def test_egg_graph_objects_preferred_over_tracks(self):
        egg = {"objects": [
            {"track_id": "trk_egg", "class_label": "hand", "object_role": "hand"},
        ]}
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), egg_graph=egg)
        obj_ids = [n["node_id"] for n in g["nodes"] if n["node_type"] == "object"]
        assert "obj_trk_egg" in obj_ids

    def test_multiple_tracks_produce_multiple_object_nodes(self):
        tracks = pd.DataFrame({
            "track_id": ["trk_a", "trk_b"],
            "start_frame_idx": [0, 5], "end_frame_idx": [30, 40],
            "semantic_class": ["workpiece", "hand"],
            "object_role": ["workpiece", "hand"],
        })
        g = build_assembly_graph(tracks, pd.DataFrame(), pd.DataFrame())
        obj_nodes = [n for n in g["nodes"] if n["node_type"] == "object"]
        assert len(obj_nodes) == 2


# ── Relation-fact nodes ────────────────────────────────────────────────────────

class TestRelationFactNodes:
    def test_facts_produce_relation_fact_nodes(self):
        g = build_assembly_graph(pd.DataFrame(), _facts(), pd.DataFrame())
        fact_nodes = [n for n in g["nodes"] if n["node_type"] == "relation_fact"]
        assert len(fact_nodes) == 1

    def test_fact_node_has_correct_id(self):
        g = build_assembly_graph(pd.DataFrame(), _facts(), pd.DataFrame())
        fact_nodes = [n for n in g["nodes"] if n["node_type"] == "relation_fact"]
        assert fact_nodes[0]["node_id"] == "fact_0001"

    def test_fact_node_predicate_preserved(self):
        g = build_assembly_graph(pd.DataFrame(), _facts(), pd.DataFrame())
        fact_nodes = [n for n in g["nodes"] if n["node_type"] == "relation_fact"]
        assert fact_nodes[0]["predicate"] == "holding"


# ── Subtask nodes ──────────────────────────────────────────────────────────────

class TestSubtaskNodes:
    def test_subtasks_produce_subtask_nodes(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), _subtasks())
        sub_nodes = [n for n in g["nodes"] if n["node_type"] == "subtask"]
        assert len(sub_nodes) == 1

    def test_subtask_node_template_name_preserved(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), _subtasks())
        sub_nodes = [n for n in g["nodes"] if n["node_type"] == "subtask"]
        assert sub_nodes[0]["template_name"] == "pick_up_part"

    def test_subtask_node_status_preserved(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(),
                                 _subtasks(status=["in_progress"]))
        sub_nodes = [n for n in g["nodes"] if n["node_type"] == "subtask"]
        assert sub_nodes[0]["status"] == "in_progress"


# ── Edges ──────────────────────────────────────────────────────────────────────

class TestEdges:
    def test_involves_edge_subtask_to_object(self):
        tracks = _tracks(track_id=["trk_hand"],
                         semantic_class=["hand"], object_role=["hand"])
        subtasks = _subtasks(agent_track_id=["trk_hand"])
        g = build_assembly_graph(tracks, pd.DataFrame(), subtasks)
        edge_types = {e["edge_type"] for e in g["edges"]}
        assert "involves" in edge_types

    def test_supports_edge_fact_to_subtask(self):
        facts = _facts(fact_id=["fact_0001"])
        subtasks = _subtasks(supporting_facts=['["fact_0001"]'])
        g = build_assembly_graph(pd.DataFrame(), facts, subtasks)
        edge_types = {e["edge_type"] for e in g["edges"]}
        assert "supports" in edge_types

    def test_evidence_for_edge_op_to_subtask(self):
        subtasks = _subtasks(supporting_operations=['["op_001"]'])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), subtasks)
        edge_types = {e["edge_type"] for e in g["edges"]}
        assert "evidence_for" in edge_types

    def test_next_candidate_edge_between_consecutive_subtasks(self):
        subs = pd.DataFrame({
            "subtask_id": ["sub_0001", "sub_0002"],
            "template_name": ["pick_up_part", "place_part"],
            "status": ["achieved", "in_progress"],
            "agent_track_id": ["trk_hand", "trk_hand"],
            "patient_track_id": ["trk_a", "trk_a"],
            "target_track_id": [None, None],
            "confidence": [0.85, 0.75],
            "start_frame_idx": [5, 20],
            "end_frame_idx": [12, 30],
            "why_this_subtask": ["op_001", "op_002"],
            "supporting_facts": ["[]", "[]"],
            "supporting_operations": ["[]", "[]"],
        })
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), subs)
        edge_types = {e["edge_type"] for e in g["edges"]}
        assert "next_candidate" in edge_types

    def test_achieves_edge_subtask_to_subgoal(self):
        domain = _FakeDomain(subgoal_templates=[
            _FakeSubgoalTemplate("part_is_held", "pick_up_part", "holding"),
        ])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(),
                                 _subtasks(status=["achieved"]),
                                 domain_config=domain)
        edge_types = {e["edge_type"] for e in g["edges"]}
        assert "achieves" in edge_types

    def test_all_edge_ids_unique(self):
        subs = pd.DataFrame({
            "subtask_id": ["sub_0001", "sub_0002"],
            "template_name": ["pick_up_part", "place_part"],
            "status": ["achieved", "in_progress"],
            "agent_track_id": ["trk_hand", "trk_hand"],
            "patient_track_id": ["trk_a", "trk_a"],
            "target_track_id": [None, None],
            "confidence": [0.85, 0.75],
            "start_frame_idx": [5, 20],
            "end_frame_idx": [12, 30],
            "why_this_subtask": ["op_001", "op_002"],
            "supporting_facts": ["[]", "[]"],
            "supporting_operations": ["[]", "[]"],
        })
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), subs)
        edge_ids = [e["edge_id"] for e in g["edges"]]
        assert len(edge_ids) == len(set(edge_ids))


# ── Subgoal nodes ──────────────────────────────────────────────────────────────

class TestSubgoalNodes:
    def test_achieved_subtask_with_domain_produces_subgoal_node(self):
        domain = _FakeDomain(subgoal_templates=[
            _FakeSubgoalTemplate("part_is_held", "pick_up_part", "holding"),
        ])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(),
                                 _subtasks(status=["achieved"]),
                                 domain_config=domain)
        sg_nodes = [n for n in g["nodes"] if n["node_type"] == "subgoal"]
        assert len(sg_nodes) == 1
        assert sg_nodes[0]["status"] == "achieved"

    def test_non_achieved_subtask_no_subgoal(self):
        domain = _FakeDomain(subgoal_templates=[
            _FakeSubgoalTemplate("part_is_held", "pick_up_part", "holding"),
        ])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(),
                                 _subtasks(status=["in_progress"]),
                                 domain_config=domain)
        sg_nodes = [n for n in g["nodes"] if n["node_type"] == "subgoal"]
        assert len(sg_nodes) == 0


# ── Phase nodes ────────────────────────────────────────────────────────────────

class TestPhaseNodes:
    def _make_timeline(self):
        return {
            "phases": [{
                "phase_id": 1,
                "label": "manipulation",
                "start_frame_idx": 0,
                "end_frame_idx": 50,
                "confidence": 0.9,
                "dominant_operation": "PICK_UP",
            }]
        }

    def test_timeline_produces_phase_node(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                                 timeline=self._make_timeline())
        ph_nodes = [n for n in g["nodes"] if n["node_type"] == "phase"]
        assert len(ph_nodes) == 1

    def test_phase_node_has_correct_label(self):
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                                 timeline=self._make_timeline())
        ph_nodes = [n for n in g["nodes"] if n["node_type"] == "phase"]
        assert ph_nodes[0]["label"] == "manipulation"

    def test_belongs_to_phase_edge_for_overlapping_subtask(self):
        subs = _subtasks(start_frame_idx=[5], end_frame_idx=[15])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), subs,
                                 timeline=self._make_timeline())
        edge_types = {e["edge_type"] for e in g["edges"]}
        assert "belongs_to_phase" in edge_types


# ── Constraint nodes ───────────────────────────────────────────────────────────

class TestConstraintNodes:
    def test_dependency_rule_produces_constraint_node(self):
        domain = _FakeDomain(dep_rules=[
            _FakeDepRule("insert_part", "align_part", "must align before inserting"),
        ])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                                 domain_config=domain)
        con_nodes = [n for n in g["nodes"] if n["node_type"] == "constraint"]
        assert len(con_nodes) == 1

    def test_constraint_node_has_subtask_and_requires(self):
        domain = _FakeDomain(dep_rules=[
            _FakeDepRule("insert_part", "align_part", "must align before inserting"),
        ])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                                 domain_config=domain)
        con = [n for n in g["nodes"] if n["node_type"] == "constraint"][0]
        assert con["subtask"] == "insert_part"
        assert con["requires"] == "align_part"


# ── Summary ────────────────────────────────────────────────────────────────────

class TestSummary:
    def test_summary_total_counts_correct(self):
        g = build_assembly_graph(_tracks(), _facts(), _subtasks())
        s = g["summary"]
        assert s["total_nodes"] == len(g["nodes"])
        assert s["total_edges"] == len(g["edges"])

    def test_summary_achieved_subgoals_list(self):
        domain = _FakeDomain(subgoal_templates=[
            _FakeSubgoalTemplate("part_is_held", "pick_up_part", "holding"),
        ])
        g = build_assembly_graph(pd.DataFrame(), pd.DataFrame(),
                                 _subtasks(status=["achieved"]),
                                 domain_config=domain)
        assert isinstance(g["summary"]["achieved_subgoals"], list)
        assert "part_is_held" in g["summary"]["achieved_subgoals"]

    def test_summary_node_type_counts_match(self):
        g = build_assembly_graph(_tracks(), _facts(), _subtasks())
        s = g["summary"]
        computed = {}
        for n in g["nodes"]:
            t = n["node_type"]
            computed[t] = computed.get(t, 0) + 1
        assert s["node_type_counts"] == computed

    def test_no_duplicate_node_ids(self):
        g = build_assembly_graph(_tracks(), _facts(), _subtasks())
        ids = [n["node_id"] for n in g["nodes"]]
        assert len(ids) == len(set(ids))
