# Evaluation 1 Remove Semantics: Layer 3 Evidence

This folder preserves post-change Layer 3 evidence for the first safe remove-action semantics step.

The original baseline Evaluation 1 evidence remains in:

```text
docs/reasoning_layers/Evaluation1/
```

That baseline records the earlier unsupported remove-action rule coverage warning. This folder shows the Layer 3-only post-change behavior after adding config-driven remove rules.

## Scope

This evidence only covers Layer 3 rule inference for remove actions. It does not implement or evaluate Layer 4 active-effect invalidation, dependency support changes, or procedural graph invalidation behavior.

## Generated Files

- `inferred_constraints.csv`: Layer 3 constraints generated with the remove rules enabled.
- `rule_coverage_diagnostics.csv`: Per-step rule coverage diagnostics generated with the remove rules enabled.
- `layer3_remove_rule_check.md`: Human-readable summary of the remove-action rule check.
