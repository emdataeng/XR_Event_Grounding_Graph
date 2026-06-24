# Domain Model and Rule Set Changelog

This document records semantic changes to:

- `config/domain_config.yaml`
- `config/thesis_rules.yaml`
- Supporting code that resolves domain expressions or converts explicit evidence into predicates

Git remains the source of truth for exact file changes. This changelog explains why
the reasoning semantics changed, what evidence is expected, and how generated
artifacts may be affected.

## Versioning

The domain model and rule set are versioned independently using semantic
versioning:

- **Patch**: descriptions, documentation, or corrections that do not change
  reasoning outcomes.
- **Minor**: backward-compatible predicates, requirements, resolvers, or rules
  that can produce new reasoning outcomes.
- **Major**: incompatible semantic changes, removed concepts, or changed meanings
  of existing predicates and constraints.

Current versions:

- Domain model: `1.1.0`
- Rule set: `1.1.0`

## 2026-06-24 — Explicit chassis securing

Versions:

- Domain model: `1.1.0`
- Rule set: `1.1.0`

Decision record:

- [`ADR-001: Model Securing as an Explicitly Observed Effect`](decisions/ADR-001-explicit-securing-evidence.md)

### Changed

- Added a generic `ChassisPin` safety requirement:

  ```text
  secured($installation_target, $installation_target_target)
  ```

- Added the `$installation_target_target` domain argument resolver.
- Added configurable `observed_effects` for components and component types.
- Added the `hasObservedEffect` predicate.
- Added the `effect_explicitly_observed_condition` rule, which converts an
  explicitly annotated observation into a produced effect.
- Configured `Chassis` annotations containing `secure`, `secured`, or `securing`
  to produce:

  ```text
  secured(chassis, chassis_installation_target)
  ```

### Annotation example

```text
Install and secure rear chassis
```

This produces:

```text
installed(rear_chassis, base)
secured(rear_chassis, base)
```

A plain annotation such as:

```text
Install rear chassis
```

produces only:

```text
installed(rear_chassis, base)
```

### Rationale

Installation and securing are distinct facts. A component must not be considered
secured merely because it was installed. Securing therefore requires explicit
annotation evidence.

The generic target-of-target expression allows every `ChassisPin` to require its
particular installation target to have been secured to that target's own support.
For example:

- `front_chassis_pin` requires `secured(front_chassis, base)`.
- `front_rear_chassis_pin` requires `secured(rear_chassis, base)`.
- `rear_rear_chassis_pin` requires `secured(rear_chassis, base)`.

### Impact

- Existing Layer 3, Layer 4, and procedural-reasoning graph artifacts must be
  rebuilt to use these semantics.
- Chassis-pin installation steps can have an additional missing safety
  requirement when no prior explicit securing observation exists.
- Editing an experiment step-list text file does not alter source graph evidence.
  The explicit wording must be present in the upstream event `action_desc`.

### Verification

- Added coverage in `tests/test_layer3_ontology_config.py`.
- Full test suite result at implementation time: `128 passed`.
