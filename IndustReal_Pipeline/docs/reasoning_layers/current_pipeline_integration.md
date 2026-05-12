# Current Reasoning Layer Integration Notes

This document describes how the current reasoning-layer implementation connects to the existing IndustReal pipeline. It is meant as a practical implementation note that can later be folded into a full pipeline README.

## Current Data Flow

The existing pipeline first builds an assembly graph and exports Neo4j-style CSV files under:

```text
results/neo4j/<run_id>/
```

The current reasoning-layer bridge starts from those exported CSV files. It does not replace the existing graph generation, Neo4j export, or Neo4j import path.

The flow is:

```text
existing graph CSVs
  -> Layer 3 reasoning adapter
  -> step_records.jsonl + predicates.jsonl
  -> Layer 3 rule inference
  -> inferred_constraints.csv
  -> Layer 4 validation
  -> validation_records.jsonl
```

Current scripts:

```text
scripts/14_build_layer3_reasoning_adapter.py
scripts/15_run_layer3_inference.py
scripts/16_run_layer4_validation.py
```

Current implementation modules:

```text
src/layer3_reasoning_adapter.py
src/layer3_inference.py
src/layer4_validation.py
```

Adapter runtime defaults are configured in:

```text
config/reasoning_adapter.yaml
```

That file defines the default run id, input CSV directory, output root, predicate/rule config path, domain config path, and the expected Neo4j CSV filenames consumed by the adapter. `scripts/14_build_layer3_reasoning_adapter.py` accepts `--adapter-config` to load a different adapter config.

## Adapter Role

The adapter turns existing graph CSV records into the JSONL inputs used by the reasoning layers.

It reads:

```text
nodes_events.csv
edges_event_component.csv
edges_event_next.csv
nodes_components.csv
```

It writes:

```text
step_records.jsonl
predicates.jsonl
```

`step_records.jsonl` contains one normalized step record per source assembly event.

`predicates.jsonl` contains symbolic facts derived from each step, such as the step action, time window, object use, and component metadata.

The upstream graph stores event instants. The adapter fills `time_window.start_s` and `start_frame` from the event row, and currently infers `end_s` and `end_frame` from the next distinct event timestamp in the same clip when one exists. The final timestamp group remains open-ended with null end values. This is a downstream fallback until upper-layer step segmentation provides explicit step windows.

## Predicate Configuration

Predicate names are configured in:

```text
config/thesis_rules.yaml
```

under:

```text
adapter.predicates
```

The current categories are:

```text
event
object_interaction
entity_metadata
```

Each configured predicate has a stable adapter key, an output name, an argument description, and an enabled flag.

Example:

```json
"has_action": {
  "name": "hasAction",
  "description": "Associates a step with its normalized action label.",
  "args": ["step_id", "action_name"],
  "enabled": true
}
```

The stable adapter key is used by Python code to decide which extraction path to run. The configured `name` is what appears in `predicates.jsonl` and what Layer 3 rules match against.

Predicate aliases are configured under `predicate_aliases`. Layer 3 normalizes predicate names before rule matching, so equivalent names such as `stepHasAction`, `actsOn`, and `typeOf` can be mapped to canonical names such as `hasAction`, `usesObject`, and `isA`.

Disabling a current predicate is also a config change:

```json
"enabled": false
```

## Upstream Boundary

The config controls the vocabulary for predicates that the adapter already knows how to generate.

The adapter still needs Python logic for each kind of predicate because each predicate depends on specific upstream data. For example:

```text
has_action
  reads event_type/action_desc from nodes_events.csv

uses_object
  reads event-component edges from edges_event_component.csv

is_a
  reads component metadata from nodes_components.csv
```

This is expected. A config file can say what a predicate is called, but it cannot invent source evidence that does not exist upstream.

So the extension rule is:

```text
Rename, recategorize, or disable an existing predicate:
  update config/thesis_rules.yaml

Add a new predicate using data the adapter does not currently read or derive:
  add a small generator path in src/layer3_reasoning_adapter.py
  add the predicate definition to config/thesis_rules.yaml
  add or update Layer 3 rules that consume the new predicate
```

For example, a future `isAfter(step_a, step_b)` predicate could be derived from `edges_event_next.csv`, but the adapter would need explicit code that converts those event-next edges into that predicate shape.

## Layer 3 Rule Inference

Layer 3 inference reads:

```text
step_records.jsonl
predicates.jsonl
config/thesis_rules.yaml
```

It writes:

```text
inferred_constraints.csv
```

Layer 4 validation reads:

```text
step_records.jsonl
predicates.jsonl
inferred_constraints.csv
```

It writes:

```text
validation_records.jsonl
```

Rules are also stored in `config/thesis_rules.yaml`, under:

```text
rules
```

Each rule matches predicate names and argument patterns. Rule outputs are defined under the `constraints` field. When the antecedents match and confidence passes the threshold, the rule emits one or more constraints.

The current rule categories follow the methodology draft:

```text
inferred_precondition
expected_effect
safety_constraint
required_tool
implicit_assembly_condition
compatibility
```

These categories use the rule evaluation structure from `Methodology_Design.tex`, Listing `lst:alg_rule_evaluation`. Non-compatibility rules are evaluated first: find bindings, collect supporting predicates, aggregate confidence, compare with the rule threshold, and instantiate configured constraints. Compatibility rules are evaluated in a separate pass and emit incompatibility constraints with provenance; these are interpreted as hard validity conditions during later validation.

Current examples use domain individual ids and generic class predicates:

```text
hasAction(step1, install) + usesObject(step1, base) + isA(base, Component)
  -> produces(step1, installed, base, workspace)

hasAction(step2, install) + usesObject(step2, rear_chassis) + isA(rear_chassis, Chassis)
  -> requires(step2, installed, base, workspace)
  -> produces(step2, installed, rear_chassis, base)

hasAction(step3, install) + usesObject(step3, front_rear_chassis_pin) + isA(front_rear_chassis_pin, ChassisPin)
  -> requires(step3, installed, rear_chassis, base)
  -> requires(step3, aligned, front_rear_chassis_pin, rear_chassis)
  -> produces(step3, installed, front_rear_chassis_pin, rear_chassis)

usesObject(step7, front_bracket_screw) + isA(front_bracket_screw, Screw)
  -> requiresTool(step, screwdriver)

hasAction(step, error) + usesObject(step, object)
  -> incompatibleAction(step, object, error)
```

Because rules match by predicate name after alias normalization, changing a predicate output name in `adapter.predicates` should either use a canonical vocabulary name or add an explicit alias to `predicate_aliases`.

## Layer 4 Validation

Layer 3 only infers requirements and expected effects. It does not decide whether a requirement is satisfied.

Layer 4 walks the ordered steps and maintains an accumulated history of previous `produces(...)` effects. For each step, it checks requirement constraints such as `requires(...)`, `requiresSafety(...)`, and `requiresTool(...)` against:

```text
same-step predicates
previous produced effects
future explicit annotation support, when available
```

If a requirement is supported by a previous effect, the validation record links it to the earlier producing constraint. If no support is found, the requirement is recorded as missing and the step is marked `uncertain`. Compatibility constraints still act as hard violations and mark a step `rejected`.

## Current Output Contract

Current predicate records include:

```text
schema_version
record_type
id
step_id
name
predicate_key
category
args
conf
source
notes
```

`name` is the configured predicate name used by Layer 3 matching.

`predicate_key` is the stable adapter key used to trace the predicate back to the adapter extraction path.

`category` comes from the config grouping under `adapter.predicates`.

`source` records which CSV file and fields produced the predicate.

The output file contract is unchanged: the adapter still writes `step_records.jsonl` and `predicates.jsonl`, Layer 3 still writes `inferred_constraints.csv`, and Layer 4 still writes `validation_records.jsonl`. The main semantic change is that configured domain components now use the domain individual `name` in predicate arguments, such as `base`, while generic classes stay class-like, such as `Base` or `Chassis`. Labels remain separate through `hasLabel(base, "base")`.

## Domain Configuration

Component-specific assembly knowledge is stored separately in:

```text
config/domain_config.yaml
```

This file maps source component ids to generic assembly roles and relations:

```text
component id/name
generic type
parent component
expected installation target
required tool
required assembly conditions
safety requirements
```

For example, the config maps both `front_chassis` and `rear_chassis` to `Chassis`, and maps chassis pins to `ChassisPin` with their parent chassis as the installation target.

The domain config now also carries lightweight ontology-style metadata:

```text
type_hierarchy
type_defaults
condition_vocabulary
predicate_aliases
```

`type_hierarchy` makes generic classes explicit. The adapter emits the configured class and its parents, for example `isA(front_bracket_screw, Screw)`, `isA(front_bracket_screw, Fastener)`, and `isA(front_bracket_screw, Component)`.

`type_defaults` provides common requirements for all components of a generic type unless the component overrides the field. For example, `Screw` defines `required_tool: screwdriver`, and `ChassisPin` defines aligned and secured requirements shared by all chassis pins.

`condition_vocabulary` controls condition names and arities used by `required_conditions` and `safety_requirements`. The adapter validates those configured conditions at load time and raises a clear error for unknown names or wrong argument counts.

The adapter materializes this domain config into predicates such as:

```text
isA(component, Chassis)
isA(component, Component)
hasInstallTarget(component, target)
requiresInstalledBefore(component, target, support)
hasParentComponent(component, parent)
hasRequiredCondition(component, aligned, component, target)
hasSafetyRequirement(component, secured, base, workspace)
hasRequiredTool(component, screwdriver)
```

Layer 3 rules then match these generic predicates. The rule engine does not hardcode specific component names; object-specific knowledge comes from `domain_config.yaml`.

In principle, this domain config can be generated from CAD metadata. A CAD-derived generator could inspect assembly hierarchy, mating constraints, fastener relationships, component names, and contact/constraint graphs to propose generic types, parent components, installation targets, and required tools. The current file is manually authored from the exported IndustReal component list.

## Practical Commands

Build adapter outputs for a filtered clip:

```powershell
python scripts\14_build_layer3_reasoning_adapter.py `
  --clip-result-id raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1 `
  --output-dir results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1
```

Run Layer 3 inference:

```powershell
python scripts\15_run_layer3_inference.py `
  --step-records results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\step_records.jsonl `
  --predicates results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\predicates.jsonl `
  --output results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\inferred_constraints.csv
```

Run Layer 4 validation:

```powershell
python scripts\16_run_layer4_validation.py `
  --step-records results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\step_records.jsonl `
  --predicates results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\predicates.jsonl `
  --constraints results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\inferred_constraints.csv `
  --output results\reasoning_layers\raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\validation_records.jsonl
```

Use a different predicate/rule config:

```powershell
python scripts\14_build_layer3_reasoning_adapter.py --predicate-config path\to\custom_rules.yaml
```

Use a different domain config:

```powershell
python scripts\14_build_layer3_reasoning_adapter.py --domain-config path\to\domain_config.yaml
```

## Notes For Future README Integration

This implementation currently treats the reasoning adapter as a downstream bridge from the existing graph export to thesis-style reasoning records.

The most important design point is the separation between:

```text
upstream evidence
  what the existing pipeline exports

adapter predicates
  symbolic facts derived from that evidence

Layer 3 rules
  procedural constraints inferred from symbolic facts
```

That separation is useful because it keeps provenance clear. If a later layer derives a constraint, it can be traced back to the rule, the matched predicates, and the original CSV fields that produced those predicates.
