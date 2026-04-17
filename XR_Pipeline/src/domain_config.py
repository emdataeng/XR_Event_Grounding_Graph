"""domain_config.py — Domain adaptation layer (Phase 4).

Separates domain-specific knowledge from generic pipeline logic.  A domain
config file (YAML) describes the object classes, workflow phases, enabled
operations, and role relationships relevant to a particular industrial process
— without modifying any Python code.

Config format (configs/domain_*.yaml)
--------------------------------------
domain_name: "lego_assembly"
domain_version: "1.0"
description: "Two-color Lego brick assembly workflow"

object_classes:
  - canonical: "red_lego"
    role: workpiece
    description: "Red Lego brick"
  - canonical: "hand"
    role: hand
    description: "Operator hand"

workflow_phases:
  - label: "hold"
    description: "Object held by hand"

enabled_operations:
  - HOLD
  - PICK_UP
  - PUT_DOWN
  - CONTACT

role_pairings:
  - agent_role: hand
    patient_role: workpiece
    valid_operations: [HOLD, PICK_UP, PUT_DOWN]
  - agent_role: workpiece
    patient_role: fixture
    valid_operations: [PLACE_ONTO_CANDIDATE, INSERT_CANDIDATE]

Validation errors
------------------
DomainConfigError is raised if:
  - required keys are missing
  - an invalid role is referenced
  - an unknown operation type is listed
  - no workpiece-role class exists
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .vocabulary import VALID_ROLES

# All known operation types (Phase 2 expanded set)
KNOWN_OPERATIONS = frozenset({
    "PICK_UP", "PUT_DOWN", "HOLD", "CONTACT", "TRANSFER",
    "USE_TOOL", "APPROACH",
    "PICK_UP_CANDIDATE", "PUT_DOWN_CANDIDATE",
    "PLACE_ONTO_CANDIDATE", "INSERT_CANDIDATE",
    "ALIGN_CANDIDATE", "ATTACH_CANDIDATE",
})


class DomainConfigError(ValueError):
    """Raised when a domain config file fails validation."""


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class DomainObjectClass:
    canonical: str
    role: str
    description: str = ""


@dataclass
class DomainPhase:
    label: str
    description: str = ""


@dataclass
class RolePairing:
    agent_role: str
    patient_role: str
    valid_operations: List[str] = field(default_factory=list)


@dataclass
class DomainConfig:
    domain_name: str
    domain_version: str
    description: str
    object_classes: List[DomainObjectClass]
    workflow_phases: List[DomainPhase]
    enabled_operations: List[str]
    role_pairings: List[RolePairing]

    # Derived lookups (populated by validate_domain_config)
    _classes_by_role: Dict[str, List[str]] = field(default_factory=dict, repr=False)

    def classes_with_role(self, role: str) -> List[str]:
        return self._classes_by_role.get(role, [])

    def has_role(self, role: str) -> bool:
        return bool(self._classes_by_role.get(role))

    def is_operation_enabled(self, op_type: str) -> bool:
        return op_type in self.enabled_operations

    def valid_operations_for_pairing(
        self, agent_role: str, patient_role: str
    ) -> List[str]:
        for pairing in self.role_pairings:
            if pairing.agent_role == agent_role and pairing.patient_role == patient_role:
                return list(pairing.valid_operations)
        return []

    def phase_labels(self) -> List[str]:
        return [p.label for p in self.workflow_phases]


# ── Loader ────────────────────────────────────────────────────────────────────

def load_domain_config(
    path: Optional[Path] = None,
    cfg: Optional[Dict[str, Any]] = None,
) -> Optional[DomainConfig]:
    """Load and validate a domain config.

    Parameters
    ----------
    path : explicit YAML file path.  If None, looks for 'domain_config' key
           in the pipeline config dict ``cfg``.
    cfg  : pipeline config dict (used to find the domain config path).

    Returns
    -------
    DomainConfig if a domain config is found and valid; None if no domain
    config is configured (graceful degradation — pipeline runs without it).

    Raises
    ------
    DomainConfigError  on validation failure.
    FileNotFoundError  if path is specified but does not exist.
    """
    if path is None and cfg is not None:
        domain_path_str = cfg.get("domain_config")
        if not domain_path_str:
            return None
        from .config import PROJECT_ROOT
        path = (PROJECT_ROOT / domain_path_str).resolve()

    if path is None:
        return None

    if not Path(path).exists():
        raise FileNotFoundError(f"Domain config not found: {path}")

    with open(path, "r") as f:
        raw = yaml.safe_load(f) or {}

    return _parse_and_validate(raw, path)


# ── Parser ────────────────────────────────────────────────────────────────────

def _parse_and_validate(raw: Dict[str, Any], source: Any = None) -> DomainConfig:
    src = f" (from {source})" if source else ""

    # Required top-level keys
    for key in ("domain_name", "object_classes"):
        if key not in raw:
            raise DomainConfigError(f"Missing required key '{key}' in domain config{src}.")

    domain_name    = str(raw.get("domain_name", ""))
    domain_version = str(raw.get("domain_version", "1.0"))
    description    = str(raw.get("description", ""))

    # ── Object classes ────────────────────────────────────────────────────────
    object_classes: List[DomainObjectClass] = []
    for entry in raw.get("object_classes") or []:
        if not isinstance(entry, dict):
            raise DomainConfigError(f"object_classes entries must be dicts{src}.")
        canonical = str(entry.get("canonical", ""))
        if not canonical:
            raise DomainConfigError(f"object_classes entry missing 'canonical' field{src}.")
        role = str(entry.get("role", "workpiece")).lower()
        if role not in VALID_ROLES:
            raise DomainConfigError(
                f"Invalid role '{role}' for class '{canonical}'{src}. "
                f"Valid roles: {sorted(VALID_ROLES)}."
            )
        object_classes.append(DomainObjectClass(
            canonical=canonical,
            role=role,
            description=str(entry.get("description", "")),
        ))

    if not object_classes:
        raise DomainConfigError(f"domain config must define at least one object class{src}.")

    # Must have at least one workpiece
    roles_present = {c.role for c in object_classes}
    if "workpiece" not in roles_present:
        raise DomainConfigError(
            f"Domain config{src} must define at least one class with role='workpiece'."
        )

    # ── Workflow phases ───────────────────────────────────────────────────────
    workflow_phases: List[DomainPhase] = []
    for entry in raw.get("workflow_phases") or []:
        if isinstance(entry, str):
            workflow_phases.append(DomainPhase(label=entry))
        elif isinstance(entry, dict):
            label = str(entry.get("label", ""))
            if not label:
                raise DomainConfigError(f"workflow_phases entry missing 'label'{src}.")
            workflow_phases.append(DomainPhase(
                label=label,
                description=str(entry.get("description", "")),
            ))

    # ── Enabled operations ────────────────────────────────────────────────────
    enabled_operations: List[str] = []
    for op in raw.get("enabled_operations") or []:
        op_str = str(op).upper()
        if op_str not in KNOWN_OPERATIONS:
            raise DomainConfigError(
                f"Unknown operation type '{op_str}' in enabled_operations{src}. "
                f"Known: {sorted(KNOWN_OPERATIONS)}."
            )
        enabled_operations.append(op_str)

    # ── Role pairings ─────────────────────────────────────────────────────────
    role_pairings: List[RolePairing] = []
    for entry in raw.get("role_pairings") or []:
        if not isinstance(entry, dict):
            continue
        agent   = str(entry.get("agent_role",   "")).lower()
        patient = str(entry.get("patient_role", "")).lower()
        ops     = [str(o).upper() for o in entry.get("valid_operations") or []]

        if agent and agent not in VALID_ROLES:
            raise DomainConfigError(f"Invalid agent_role '{agent}' in role_pairings{src}.")
        if patient and patient not in VALID_ROLES:
            raise DomainConfigError(f"Invalid patient_role '{patient}' in role_pairings{src}.")
        for op in ops:
            if op not in KNOWN_OPERATIONS:
                raise DomainConfigError(
                    f"Unknown operation '{op}' in role_pairing "
                    f"({agent}→{patient}){src}."
                )
        role_pairings.append(RolePairing(
            agent_role=agent,
            patient_role=patient,
            valid_operations=ops,
        ))

    # ── Build derived lookup ──────────────────────────────────────────────────
    classes_by_role: Dict[str, List[str]] = {}
    for cls in object_classes:
        classes_by_role.setdefault(cls.role, []).append(cls.canonical)

    dc = DomainConfig(
        domain_name=domain_name,
        domain_version=domain_version,
        description=description,
        object_classes=object_classes,
        workflow_phases=workflow_phases,
        enabled_operations=enabled_operations,
        role_pairings=role_pairings,
    )
    dc._classes_by_role = classes_by_role
    return dc


def validate_domain_config(domain_cfg: DomainConfig) -> List[str]:
    """Return a list of validation warnings (non-fatal) for an already-loaded config.

    Raises DomainConfigError on fatal issues.
    Returns a (possibly empty) list of warning strings.
    """
    warnings: List[str] = []

    if not domain_cfg.workflow_phases:
        warnings.append(
            "No workflow_phases defined — phase labeling will use defaults."
        )

    if not domain_cfg.enabled_operations:
        warnings.append(
            "No enabled_operations defined — all operation types will be enabled."
        )

    if not domain_cfg.role_pairings:
        warnings.append(
            "No role_pairings defined — all role combinations will be considered valid."
        )

    # Check that every class referenced in pairings has a matching object class
    defined_roles = {c.role for c in domain_cfg.object_classes}
    for pairing in domain_cfg.role_pairings:
        for r in (pairing.agent_role, pairing.patient_role):
            if r and r not in defined_roles:
                warnings.append(
                    f"Role '{r}' in role_pairings has no matching object class."
                )

    return warnings
