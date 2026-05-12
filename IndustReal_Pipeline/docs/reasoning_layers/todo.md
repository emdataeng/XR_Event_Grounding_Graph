# Reasoning Layers TODO

This document tracks implementation follow-ups for the reasoning-layer prototype.

## TODO

- [ ] Generate `config/domain_config.yaml` from CAD-derived structure.
  - Infer generic component types from CAD names, hierarchy, metadata, and geometry.
  - Infer parent components and expected installation targets from assembly hierarchy and mating/contact constraints.
  - Detect fasteners and required tools where possible.
  - Emit confidence/provenance for generated domain facts so manual overrides can be distinguished from CAD-derived facts.

- [ ] Add manual override support for CAD-derived domain facts.

- [ ] Extend Layer 4 support checks beyond previous `produces(...)` effects.
  - Check same-step predicates.
  - Check explicit annotations/source descriptions.
  - Check perception-derived spatial predicates when available.

- [ ] Add rules/effects for remove actions.

- [ ] Move step time-window boundaries upstream.
  - Step `end_s`/`end_frame` should come from upper-layer segmentation when available.
  - The reasoning adapter currently infers end boundaries from the next distinct event timestamp only as a downstream fallback.

- [ ] Add graph export for validation records, constraints, produced effects, and dependency links.

- [ ] Add tests for domain-config predicate generation, Layer 3 generic rule matching, and Layer 4 history validation.
