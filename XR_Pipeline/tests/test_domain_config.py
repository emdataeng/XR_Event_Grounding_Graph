"""Tests for domain_config.py — Phase 4 domain adaptation layer."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
import pytest

from src.domain_config import (
    load_domain_config,
    validate_domain_config,
    DomainConfig,
    DomainConfigError,
    DomainObjectClass,
    DomainPhase,
    RolePairing,
    _parse_and_validate,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_yaml(tmp_path, data):
    p = tmp_path / "domain.yaml"
    p.write_text(yaml.dump(data))
    return p


def _minimal_raw():
    return {
        "domain_name": "test_domain",
        "object_classes": [
            {"canonical": "widget", "role": "workpiece"},
        ],
    }


def _full_raw():
    return {
        "domain_name":    "full_domain",
        "domain_version": "2.0",
        "description":    "Full test domain",
        "object_classes": [
            {"canonical": "component", "role": "workpiece", "description": "Part"},
            {"canonical": "hand",      "role": "hand",      "description": "Hand"},
            {"canonical": "fixture",   "role": "fixture",   "description": "Jig"},
        ],
        "workflow_phases": [
            {"label": "idle",          "description": "No activity"},
            {"label": "manipulation",  "description": "Active manipulation"},
        ],
        "enabled_operations": ["HOLD", "PICK_UP", "PLACE_ONTO_CANDIDATE"],
        "role_pairings": [
            {
                "agent_role":     "hand",
                "patient_role":   "workpiece",
                "valid_operations": ["HOLD", "PICK_UP"],
            },
            {
                "agent_role":     "workpiece",
                "patient_role":   "fixture",
                "valid_operations": ["PLACE_ONTO_CANDIDATE"],
            },
        ],
    }


# ── _parse_and_validate ───────────────────────────────────────────────────────

def test_minimal_config_parses():
    dc = _parse_and_validate(_minimal_raw())
    assert dc.domain_name == "test_domain"
    assert len(dc.object_classes) == 1


def test_full_config_parses():
    dc = _parse_and_validate(_full_raw())
    assert dc.domain_name == "full_domain"
    assert dc.domain_version == "2.0"
    assert len(dc.object_classes) == 3
    assert len(dc.workflow_phases) == 2
    assert len(dc.enabled_operations) == 3
    assert len(dc.role_pairings) == 2


def test_missing_domain_name_raises():
    raw = _minimal_raw()
    del raw["domain_name"]
    with pytest.raises(DomainConfigError, match="domain_name"):
        _parse_and_validate(raw)


def test_missing_object_classes_raises():
    raw = _minimal_raw()
    del raw["object_classes"]
    with pytest.raises(DomainConfigError, match="object_classes"):
        _parse_and_validate(raw)


def test_no_workpiece_raises():
    raw = _minimal_raw()
    raw["object_classes"] = [{"canonical": "hand", "role": "hand"}]
    with pytest.raises(DomainConfigError, match="workpiece"):
        _parse_and_validate(raw)


def test_invalid_role_raises():
    raw = _minimal_raw()
    raw["object_classes"] = [{"canonical": "widget", "role": "unicorn"}]
    with pytest.raises(DomainConfigError, match="Invalid role"):
        _parse_and_validate(raw)


def test_unknown_operation_raises():
    raw = _minimal_raw()
    raw["enabled_operations"] = ["HOLD", "TELEPORT"]
    with pytest.raises(DomainConfigError, match="Unknown operation"):
        _parse_and_validate(raw)


def test_invalid_pairing_role_raises():
    raw = _full_raw()
    raw["role_pairings"] = [{"agent_role": "ghost", "patient_role": "workpiece",
                              "valid_operations": ["HOLD"]}]
    with pytest.raises(DomainConfigError, match="Invalid agent_role"):
        _parse_and_validate(raw)


def test_empty_object_classes_raises():
    raw = _minimal_raw()
    raw["object_classes"] = []
    with pytest.raises(DomainConfigError, match="at least one"):
        _parse_and_validate(raw)


# ── DomainConfig methods ──────────────────────────────────────────────────────

def test_classes_with_role():
    dc = _parse_and_validate(_full_raw())
    workpieces = dc.classes_with_role("workpiece")
    assert "component" in workpieces
    hands = dc.classes_with_role("hand")
    assert "hand" in hands


def test_has_role():
    dc = _parse_and_validate(_full_raw())
    assert dc.has_role("hand") is True
    assert dc.has_role("tool") is False


def test_is_operation_enabled():
    dc = _parse_and_validate(_full_raw())
    assert dc.is_operation_enabled("HOLD") is True
    assert dc.is_operation_enabled("USE_TOOL") is False


def test_valid_operations_for_pairing():
    dc = _parse_and_validate(_full_raw())
    ops = dc.valid_operations_for_pairing("hand", "workpiece")
    assert "HOLD" in ops
    assert "PICK_UP" in ops


def test_valid_operations_unknown_pairing():
    dc = _parse_and_validate(_full_raw())
    ops = dc.valid_operations_for_pairing("tool", "machine_part")
    assert ops == []


def test_phase_labels():
    dc = _parse_and_validate(_full_raw())
    labels = dc.phase_labels()
    assert "idle" in labels
    assert "manipulation" in labels


# ── validate_domain_config warnings ──────────────────────────────────────────

def test_no_warnings_for_full_config():
    dc = _parse_and_validate(_full_raw())
    warnings = validate_domain_config(dc)
    assert warnings == []


def test_warning_no_workflow_phases():
    raw = _minimal_raw()
    dc = _parse_and_validate(raw)
    warnings = validate_domain_config(dc)
    assert any("workflow_phases" in w.lower() for w in warnings)


def test_warning_no_enabled_operations():
    raw = _minimal_raw()
    dc = _parse_and_validate(raw)
    warnings = validate_domain_config(dc)
    assert any("enabled_operations" in w.lower() for w in warnings)


def test_warning_pairing_role_missing_class():
    raw = _minimal_raw()
    # Pairing references "tool" role but no tool class defined
    raw["enabled_operations"] = ["USE_TOOL"]
    raw["role_pairings"] = [
        {"agent_role": "tool", "patient_role": "workpiece",
         "valid_operations": ["USE_TOOL"]}
    ]
    dc = _parse_and_validate(raw)
    warnings = validate_domain_config(dc)
    assert any("tool" in w for w in warnings)


# ── load_domain_config from file ──────────────────────────────────────────────

def test_load_from_path(tmp_path):
    p = _write_yaml(tmp_path, _full_raw())
    dc = load_domain_config(path=p)
    assert dc is not None
    assert dc.domain_name == "full_domain"


def test_load_none_when_no_path():
    dc = load_domain_config(path=None, cfg={})
    assert dc is None


def test_load_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_domain_config(path=Path("/nonexistent/domain.yaml"))


# ── Real config files ─────────────────────────────────────────────────────────

def test_lego_domain_config_valid():
    """Verify the shipped domain_lego.yaml parses without errors."""
    config_path = Path(__file__).resolve().parent.parent / "configs" / "domain_lego.yaml"
    if not config_path.exists():
        pytest.skip("domain_lego.yaml not found")
    dc = load_domain_config(path=config_path)
    assert dc is not None
    assert dc.has_role("workpiece")
    warnings = validate_domain_config(dc)
    assert warnings == []


def test_industrial_domain_config_valid():
    """Verify the shipped domain_industrial_example.yaml parses without errors."""
    config_path = (
        Path(__file__).resolve().parent.parent
        / "configs" / "domain_industrial_example.yaml"
    )
    if not config_path.exists():
        pytest.skip("domain_industrial_example.yaml not found")
    dc = load_domain_config(path=config_path)
    assert dc is not None
    assert dc.has_role("tool")
    assert dc.has_role("fixture")
    warnings = validate_domain_config(dc)
    assert warnings == []
