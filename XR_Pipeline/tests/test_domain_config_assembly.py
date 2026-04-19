"""tests/test_domain_config_assembly.py — Tests for new assembly fields in domain_config.py."""
import pytest

from src.domain_config import (
    DomainConfig,
    AssemblyPredicate,
    SubtaskTemplate,
    SubgoalTemplate,
    DependencyRule,
    load_domain_config,
)


# ── Dataclass construction ─────────────────────────────────────────────────────

class TestAssemblyPredicateDataclass:
    def test_name_required(self):
        ap = AssemblyPredicate(name="holding")
        assert ap.name == "holding"

    def test_description_defaults_empty(self):
        ap = AssemblyPredicate(name="near")
        assert ap.description == ""

    def test_full_construction(self):
        ap = AssemblyPredicate(name="in_contact", description="objects are touching")
        assert ap.description == "objects are touching"


class TestSubtaskTemplateDataclass:
    def test_basic_construction(self):
        tmpl = SubtaskTemplate(
            name="pick_up_part",
            trigger_operations=["PICK_UP", "HOLD"],
            trigger_predicates=[],
            agent_role="hand",
            patient_role="workpiece",
        )
        assert tmpl.name == "pick_up_part"
        assert "PICK_UP" in tmpl.trigger_operations
        assert tmpl.agent_role == "hand"

    def test_description_defaults_empty(self):
        tmpl = SubtaskTemplate(
            name="place_part", trigger_operations=["PUT_DOWN"],
            trigger_predicates=[], agent_role="hand", patient_role="workpiece",
        )
        assert tmpl.description == ""

    def test_trigger_predicates_can_be_non_empty(self):
        tmpl = SubtaskTemplate(
            name="insert_part",
            trigger_operations=["INSERT_CANDIDATE"],
            trigger_predicates=["aligned_with_candidate"],
            agent_role="hand",
            patient_role="workpiece",
        )
        assert "aligned_with_candidate" in tmpl.trigger_predicates


class TestSubgoalTemplateDataclass:
    def test_basic_construction(self):
        sg = SubgoalTemplate(name="part_is_held", achieved_by="pick_up_part", predicate="holding")
        assert sg.name == "part_is_held"
        assert sg.achieved_by == "pick_up_part"
        assert sg.predicate == "holding"

    def test_description_defaults_empty(self):
        sg = SubgoalTemplate(name="part_is_inserted", achieved_by="insert_part", predicate="inserted_into_candidate")
        assert sg.description == ""


class TestDependencyRuleDataclass:
    def test_basic_construction(self):
        rule = DependencyRule(subtask="insert_part", requires="align_part")
        assert rule.subtask == "insert_part"
        assert rule.requires == "align_part"

    def test_description_defaults_empty(self):
        rule = DependencyRule(subtask="attach_part", requires="align_part")
        assert rule.description == ""


# ── DomainConfig new fields ────────────────────────────────────────────────────

class TestDomainConfigAssemblyFields:
    def _make_domain(self, **overrides):
        defaults = dict(
            domain_name="test_domain",
            domain_version="1.0",
            description="test",
            object_classes=[],
            workflow_phases=[],
            enabled_operations=[],
            role_pairings=[],
            assembly_predicates=[],
            subtask_templates=[],
            subgoal_templates=[],
            dependency_rules=[],
            phase_hints={},
        )
        defaults.update(overrides)
        return DomainConfig(**defaults)

    def test_assembly_predicates_field_exists(self):
        domain = self._make_domain(assembly_predicates=[
            AssemblyPredicate(name="holding"),
        ])
        assert len(domain.assembly_predicates) == 1

    def test_subtask_templates_field_exists(self):
        domain = self._make_domain(subtask_templates=[
            SubtaskTemplate(
                name="pick_up_part", trigger_operations=["PICK_UP"],
                trigger_predicates=[], agent_role="hand", patient_role="workpiece",
            ),
        ])
        assert len(domain.subtask_templates) == 1

    def test_subgoal_templates_field_exists(self):
        domain = self._make_domain(subgoal_templates=[
            SubgoalTemplate(name="part_is_held", achieved_by="pick_up_part", predicate="holding"),
        ])
        assert len(domain.subgoal_templates) == 1

    def test_dependency_rules_field_exists(self):
        domain = self._make_domain(dependency_rules=[
            DependencyRule(subtask="insert_part", requires="align_part"),
        ])
        assert len(domain.dependency_rules) == 1

    def test_phase_hints_field_exists(self):
        domain = self._make_domain(phase_hints={"manipulation": ["pick_up_part"]})
        assert "manipulation" in domain.phase_hints

    def test_empty_defaults(self):
        domain = self._make_domain()
        assert domain.assembly_predicates == []
        assert domain.subtask_templates    == []
        assert domain.subgoal_templates    == []
        assert domain.dependency_rules     == []
        assert domain.phase_hints          == {}


# ── Helper methods ─────────────────────────────────────────────────────────────

class TestDomainConfigHelpers:
    def _make_full_domain(self):
        return DomainConfig(
            domain_name="test",
            domain_version="1.0",
            description="test",
            object_classes=[],
            workflow_phases=[],
            enabled_operations=[],
            role_pairings=[],
            assembly_predicates=[
                AssemblyPredicate(name="holding"),
                AssemblyPredicate(name="in_contact"),
            ],
            subtask_templates=[
                SubtaskTemplate(
                    name="pick_up_part", trigger_operations=["PICK_UP", "HOLD"],
                    trigger_predicates=[], agent_role="hand", patient_role="workpiece",
                ),
                SubtaskTemplate(
                    name="insert_part", trigger_operations=["INSERT_CANDIDATE"],
                    trigger_predicates=["aligned_with_candidate"],
                    agent_role="hand", patient_role="workpiece",
                ),
            ],
            subgoal_templates=[
                SubgoalTemplate(name="part_is_held", achieved_by="pick_up_part", predicate="holding"),
                SubgoalTemplate(name="part_is_inserted", achieved_by="insert_part", predicate="inserted_into_candidate"),
            ],
            dependency_rules=[
                DependencyRule(subtask="insert_part", requires="align_part", description="must align before inserting"),
            ],
            phase_hints={"manipulation": ["pick_up_part"], "assembly": ["insert_part"]},
        )

    def test_subtask_template_lookup_found(self):
        domain = self._make_full_domain()
        tmpl = domain.subtask_template("pick_up_part")
        assert tmpl is not None
        assert tmpl.name == "pick_up_part"

    def test_subtask_template_lookup_missing_returns_none(self):
        domain = self._make_full_domain()
        assert domain.subtask_template("nonexistent") is None

    def test_subgoal_for_subtask_found(self):
        domain = self._make_full_domain()
        sg = domain.subgoal_for_subtask("pick_up_part")
        assert sg is not None
        assert sg.name == "part_is_held"

    def test_subgoal_for_subtask_missing_returns_none(self):
        domain = self._make_full_domain()
        assert domain.subgoal_for_subtask("nonexistent") is None

    def test_required_before_returns_prerequisites(self):
        domain = self._make_full_domain()
        prereqs = domain.required_before("insert_part")
        assert "align_part" in prereqs

    def test_required_before_no_deps_returns_empty(self):
        domain = self._make_full_domain()
        prereqs = domain.required_before("pick_up_part")
        assert prereqs == []

    def test_assembly_predicate_names_returns_iterable(self):
        domain = self._make_full_domain()
        names = domain.assembly_predicate_names()
        assert hasattr(names, "__iter__")
        assert "holding" in names
        assert "in_contact" in names

    def test_assembly_predicate_names_empty_domain(self):
        domain = DomainConfig(
            domain_name="x", domain_version="1.0", description="",
            object_classes=[], workflow_phases=[],
            enabled_operations=[], role_pairings=[],
            assembly_predicates=[], subtask_templates=[], subgoal_templates=[],
            dependency_rules=[], phase_hints={},
        )
        assert list(domain.assembly_predicate_names()) == []


# ── YAML parsing (lego domain) ─────────────────────────────────────────────────

from pathlib import Path as _Path
_CONFIGS_DIR = _Path(__file__).resolve().parent.parent / "configs"


class TestYamlParsing:
    def test_lego_domain_loads(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        assert domain is not None

    def test_lego_domain_has_assembly_predicates(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        assert isinstance(domain.assembly_predicates, list)
        assert len(domain.assembly_predicates) >= 1

    def test_lego_domain_has_subtask_templates(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        assert len(domain.subtask_templates) >= 1

    def test_lego_domain_has_subgoal_templates(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        assert len(domain.subgoal_templates) >= 1

    def test_lego_dependency_rules_is_list(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        assert isinstance(domain.dependency_rules, list)

    def test_lego_phase_hints_is_dict(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        assert isinstance(domain.phase_hints, dict)

    def test_industrial_domain_loads(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_industrial_example.yaml")
        assert domain is not None

    def test_industrial_domain_has_dependency_rules(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_industrial_example.yaml")
        assert len(domain.dependency_rules) >= 1

    def test_industrial_domain_insert_requires_align(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_industrial_example.yaml")
        prereqs = domain.required_before("insert_part")
        assert "align_part" in prereqs

    def test_subtask_template_names_are_strings(self):
        domain = load_domain_config(path=_CONFIGS_DIR / "domain_lego.yaml")
        for tmpl in domain.subtask_templates:
            assert isinstance(tmpl.name, str)
            assert len(tmpl.name) > 0
