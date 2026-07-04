# Pilot Reasoning Artifact Provenance

This note documents the sources and modeling decisions used to create the Pilot reasoning bundle. It is intended as a research-facing explanation of how the Pilot artifacts were derived from the available procedure data and adapted to the same reasoning-layer structure used for IndustReal.

## 1. Starting Point: IndustReal Reasoning Layer

The Pilot bundle was created after the IndustReal reasoning pipeline had already been established. IndustReal provided the reference structure for:

- a domain configuration file, represented in the main project as `config/domain_config.yaml`;
- a rule configuration file, represented in the main project as `config/thesis_rules.yaml`;
- a predicate-level symbolic input representation;
- Layer 3 inference from predicates into constraints such as `requires(...)`, `produces(...)`, and `requiresTool(...)`;
- Layer 4 validation, where a step is accepted, uncertain, or rejected depending on whether its requirements are supported by prior active effects or same-step evidence;
- the final procedural reasoning graph built from steps, predicates, inferred constraints, validations, dependencies, and provenance.

The Pilot artifacts therefore reuse the IndustReal reasoning pattern, but they are not derived from IndustReal data. They are a separate, reasoning-only symbolic adaptation for the rod assembly procedure.

## 2. Available Pilot Source Data

The only primary Pilot source used here is `Pilot/rod_assembly_steps.json`.

This file contains an exported instructional procedure for assembling a metal rod with sleeves, O-rings, screws, threadlocker, cleaning materials, and grease. It provides:

- instruction metadata;
- video duration;
- eight ordered procedural steps;
- start and end timestamps for each step;
- free-text notes and subtitles for each step.

No raw video, object detections, pose estimates, or CAD-derived graph edges were used for this Pilot bundle. The Pilot data is therefore treated as a symbolic, text-grounded procedure rather than as a perception-grounded dataset.

The eight source steps are:

1. Place the metal rod on the workbench.
2. Slide long, short, and copper sleeves onto the rod, with orientation and count requirements.
3. Place O-rings in the rod holes and adjust the sleeves over them.
4. Drive screws halfway into all holes using a power screwdriver.
5. Apply threadlocker to the partially inserted screws.
6. Fully tighten the screws to secure the sleeves.
7. Clean the rod and sleeves with ethanol and paper while avoiding polishing the copper part.
8. Apply grease to a sponge and lubricate the silver-colored sleeves while avoiding copper sleeves.

## 3. Pilot Domain Configuration

The domain model is stored in `Pilot/domain_config_pilot.yaml`.

This file was created as the Pilot equivalent of the IndustReal domain configuration. It defines the ontology, entities, components, installation targets, and domain-level required conditions for the rod assembly procedure.

### 3.1 Type Hierarchy

The Pilot domain defines the following main type families:

- `Component`: base class for physical components.
- `Rod`: the metal rod.
- `Sleeve`: long, short, copper, silver, and generic sleeves.
- `Fastener`: screws.
- `Sealing` and `ORing`: sealing components.
- `Assembly`: the final rod assembly.
- `Location`, `Workspace`, `RodFeature`, and `RodHole`: non-component locations or features.
- `Tool`: power screwdriver and sponge.
- `Material`: threadlocker, ethanol, paper, grease, and quantity markers.

The `RodHole` type was added because the procedure explicitly refers to holes on the rod. The domain needs to represent that `rod_holes` exist in the `metal_rod`; therefore `rod_holes` is modeled as a `RodHole` with `parent_component: metal_rod` and `located_in: metal_rod`.

### 3.2 Components and Installation Targets

The components were derived from the nouns and assembly roles in the Pilot step notes:

- `metal_rod` is a `Rod` installed on the `workbench`.
- `long_sleeve`, `short_sleeve`, `copper_sleeve`, `silver_sleeve`, and generic `sleeve` are `Sleeve` components installed on the `metal_rod`.
- `o_ring` is an `ORing` installed in `rod_holes`.
- `screw` is a `Fastener` installed in `rod_holes`.
- `rod_assembly` is the resulting assembly.

Earlier drafts considered an artificial aggregate such as `mixed_sleeves`, but it was removed because it does not appear in the source Pilot procedure. The current domain keeps only entities justified by the procedure or needed for reasoning.

### 3.3 Required Conditions in Type Defaults

Following the IndustReal pattern, some domain-level required conditions are encoded under `type_defaults`.

These defaults express requirements that are not necessarily observed effects. They are used to infer what must already hold for later steps to be valid.

The current Pilot defaults are:

- `Rod` requires `secured($self, $installation_target)`.
- `ORing` requires `aligned($self, $installation_target)`.
- `Sleeve` requires `aligned($self, "o_ring")`.
- `Fastener` requires `aligned($self, $installation_target)` and `aligned($self, "o_ring")`.

For this assembly, that means:

- the rod should be secured to the workbench;
- the O-rings should be aligned with the rod holes;
- sleeves should be aligned with the O-rings;
- screws should be aligned with both the rod holes and the O-rings.

These are domain requirements, not automatic observations.

### 3.4 Condition Vocabulary

The condition vocabulary was created from the Pilot procedure and the reasoning needs of the assembly:

- `on`
- `secured`
- `aligned`
- `sleeves_on`
- `oriented`
- `count_verified`
- `inserted_in`
- `adjusted_over`
- `partially_inserted_in`
- `applied_to`
- `flush_with`
- `cleaned_with`
- `lubricated_with`
- `avoided_contact_with`

The predicate `secured_to` was removed in favor of the single canonical predicate `secured`, matching the cleaner relation used elsewhere in the reasoning layer.

## 4. Pilot Procedure File

The procedure file is `Pilot/rod_assembly_steps.json`.

This is the source document for the Pilot step sequence. It was not invented for the reasoning layer; it is the input procedure from which the reasoning artifacts were derived.

For the research paper, this file should be described as the natural-language procedural source. The reasoning layer then converts the step text into symbolic predicates and domain constraints.

The file currently uses placeholder export timestamps from `2020-01-01T00:00:00Z`. These timestamps should be interpreted as source metadata rather than generated reasoning timestamps.

## 5. Pilot Predicates

The symbolic predicate input is stored in `Pilot/predicates.jsonl`.

This file is the Pilot equivalent of the predicate records that the IndustReal pipeline would normally derive from graph data and domain configuration. Because the Pilot dataset does not include perception or graph CSV assets, the predicates were manually authored from the step notes and domain model.

Each row is a JSON object with:

- a stable predicate id;
- a step id where applicable;
- a predicate name;
- predicate arguments;
- confidence;
- source provenance.

### 5.1 Predicate Categories

The Pilot predicates include:

- event predicates such as `hasAction(step, action)` and `hasTimeWindow(step, start, end)`;
- object interaction predicates such as `usesObject`, `usesTool`, and `usesMaterial`;
- domain metadata predicates such as `isA` and `hasParentComponent`;
- required-condition predicates such as `hasRequiredCondition(step, condition, arg1, arg2)`;
- observed-effect predicates such as `hasObservedEffect(step, condition, arg1, arg2)`;
- tool requirement predicates such as `hasRequiredTool(step, tool)`.

### 5.2 Provenance Labels

The Pilot predicates distinguish three important provenance types:

- `manual_symbolic_annotation`: a direct symbolic encoding of what the step text states.
- `manual_expert_annotation`: a domain-expert assumption or interpretation needed for reasoning, not literally stated in the source text.
- `pilot_domain_default`: a requirement or metadata assertion derived from `Pilot/domain_config_pilot.yaml`.

This distinction is important for research reporting. It allows the paper to separate direct procedure evidence from expert-added assumptions and from ontology-derived requirements.

For example:

- Step 1 states that the rod is placed on the workbench. This directly supports `on(metal_rod, workbench)` as a `manual_symbolic_annotation`.
- Step 1 is also treated as producing `secured(metal_rod, workbench)` as a `manual_expert_annotation`. This was added because subsequent sleeve installation requires the rod to be secured enough for assembly. It is not a literal phrase in the step note.
- Step 2 requires `secured(metal_rod, workbench)` as a `pilot_domain_default`, because `metal_rod` is a `Rod` whose required condition is `secured($self, $installation_target)`.

### 5.3 Observed Effects Versus Required Conditions

A central design decision was to keep observed effects separate from required effects or required conditions.

Observed effects are encoded only when the procedure text, or an explicit expert annotation, says a condition is achieved. These are represented as `hasObservedEffect`.

Required conditions are encoded when something must already hold for a step to be valid. These are represented as `hasRequiredCondition`.

This distinction follows the IndustReal reasoning design:

- `hasObservedEffect` can become a produced effect in Layer 3.
- `hasRequiredCondition` becomes a requirement in Layer 3.
- Layer 4 checks whether the requirement is supported by earlier active produced effects or appropriate same-step evidence.

The Pilot model therefore avoids treating every domain default as an observed effect. Domain defaults express requirements unless there is a specific observation or expert annotation that the condition was achieved.

### 5.4 Important Predicate Decisions

The following decisions are especially important:

- Step 1 produces `on(metal_rod, workbench)` from direct symbolic annotation.
- Step 1 also produces `secured(metal_rod, workbench)` from manual expert annotation.
- Step 2 produces `sleeves_on(sleeve, metal_rod)`, sleeve orientation, and count verification.
- Step 3 requires the sleeves to already be on the rod, then produces O-ring insertion, O-ring alignment with rod holes, sleeve adjustment over O-rings, and sleeve alignment with O-rings.
- Step 4 requires O-ring insertion/alignment and sleeve adjustment/alignment, uses a power screwdriver, and produces partial screw insertion.
- Step 5 requires partial screw insertion and produces threadlocker application.
- Step 6 requires threadlocker, partial screw insertion, screw alignment with rod holes, screw alignment with O-rings, and the power screwdriver. It produces the sleeve being secured to the rod and the screw being flush with the sleeve.
- Steps 7 and 8 require prior secured/cleaned conditions and produce cleaning, lubrication, and avoidance effects.

The screw alignment requirements in Step 6 are intentionally requirements, not Step 4 observed effects. This keeps the model strict: the current Pilot text says the screws are driven into holes, but the model does not automatically assert that both alignment conditions have been observed unless that is explicitly annotated.

## 6. Pilot Rules

The Pilot rule configuration is stored in `Pilot/rules_pilot.yaml`.

This file is the Pilot equivalent of `config/thesis_rules.yaml`, simplified for the reasoning-only Pilot input format.

It defines:

- predicate names and arities;
- default threshold and aggregation policy;
- validation thresholds;
- rule types;
- four generic Pilot rules.

### 6.1 Rule: Observed Effects Produce Effects

Rule id: `effect_observed_pilot_condition`

This rule maps an observed symbolic effect into a Layer 3 produced effect:

```text
hasAction(?s, ?action)
hasObservedEffect(?s, ?condition, ?arg1, ?arg2)
=> produces(?s, ?condition, ?arg1, ?arg2)
```

This is why observed Pilot effects become graph `PRODUCES` relations.

### 6.2 Rule: Required Conditions Become Requirements

Rule id: `precondition_required_pilot_condition`

This rule maps required symbolic conditions into Layer 3 requirements:

```text
hasAction(?s, ?action)
hasRequiredCondition(?s, ?condition, ?arg1, ?arg2)
=> requires(?s, ?condition, ?arg1, ?arg2)
```

This is how the pipeline checks whether a Pilot step is valid with respect to previous assembly state.

### 6.3 Rule: Tool Requirements

Rule id: `tool_required_by_pilot_step`

This rule maps an explicit tool requirement into a Layer 3 tool constraint:

```text
hasRequiredTool(?s, ?tool)
=> requiresTool(?s, ?tool)
```

For example, Steps 4 and 6 require the power screwdriver.

### 6.4 Rule: Compatibility Error

Rule id: `compatibility_error_action_marks_incompatibility`

This rule provides a minimal hook for marking symbolic error actions as incompatible:

```text
hasAction(?s, "error")
usesObject(?s, ?object)
=> incompatibleAction(?s, ?object, "error")
```

The current Pilot procedure does not include error steps, but the rule keeps the Pilot bundle structurally aligned with the validation machinery.

## 7. Adapter and Observation Contract

Two supporting configuration files describe how the Pilot bundle should be interpreted:

- `Pilot/reasoning_adapter_pilot.yaml`
- `Pilot/observation_contract_pilot.yaml`

The adapter file records the paths to the Pilot inputs and outputs. It also states that the Pilot path starts from hand-authored symbolic records rather than IndustReal graph CSVs.

The observation contract records that missing installation-target observations may be domain-assumed. This matters because the Pilot bundle lacks perception-derived target observations. The domain file therefore supplies installation targets such as `screw -> rod_holes` and `sleeve -> metal_rod`.

## 8. Generated Reasoning Artifacts

The following files are generated from the authored Pilot inputs:

- `Pilot/step_records.jsonl`
- `Pilot/inferred_constraints.csv`
- `Pilot/rule_coverage_diagnostics.csv`
- `Pilot/validation_records.jsonl`
- `Pilot/step_validations.csv`
- `Pilot/explanation_traces.json`
- `Pilot/effect_history_diagnostics.csv`
- `Pilot/procedural_reasoning_graph/procedural_reasoning_graph.json`
- `Pilot/procedural_reasoning_graph/procedural_reasoning_graph_nodes.csv`
- `Pilot/procedural_reasoning_graph/procedural_reasoning_graph_edges.csv`

These should be described as derived artifacts. The authored artifacts are the procedure, domain configuration, rules, adapter/contract, and predicate file.

At the current state of the Pilot bundle, Layer 4 validation reports:

```text
accepted: 7
uncertain: 1
rejected: 0
```

The remaining uncertain step is Step 6. It requires screw alignment with both `rod_holes` and `o_ring`, but those alignment conditions are not currently produced as observed effects. This is intentional under the strict separation between required conditions and observed effects.

## 9. Justification for the Research Paper

The Pilot bundle should be presented as a controlled transfer test of the IndustReal reasoning layers to a second real-world procedural dataset.

The justification is:

1. The source data consists of a real procedural assembly instruction with ordered steps and timestamps.
2. The reasoning layers do not require raw video when the research question concerns symbolic reasoning, dependency tracking, and validation behavior.
3. The Pilot procedure was converted into symbolic predicates using the same conceptual roles used in IndustReal: actions, objects, tools, materials, required conditions, and observed effects.
4. A small Pilot domain ontology was created to represent the assembly-specific entities and constraints.
5. Domain defaults were used only to infer requirements, not to fabricate observations.
6. Observed effects were kept separate from required conditions.
7. Expert-added assumptions were explicitly labeled with `manual_expert_annotation`.
8. The resulting graph preserves provenance, allowing the paper to distinguish direct step evidence, expert interpretation, and domain-derived requirements.
9. The validation outcome demonstrates that the pipeline can expose unsupported requirements, not merely accept all steps.

The most important methodological point is the separation of evidence from expectation:

- The procedure text and expert annotations provide evidence.
- The domain model provides expected requirements.
- The rule layer converts both into constraints.
- The validation layer tests whether requirements are supported by active prior effects.

This is the same reasoning principle used for IndustReal, adapted to a text-grounded Pilot procedure.

## 10. Limitations

The Pilot bundle has several limitations that should be stated clearly:

- It is reasoning-only and does not include raw video, object detections, pose estimates, or perception confidence.
- Predicate extraction is manually authored rather than automatically produced from a perception graph.
- Most confidences are set to `1.0`, so uncertainty mainly comes from missing support, not probabilistic evidence.
- Some predicates, such as `secured(metal_rod, workbench)`, are expert annotations rather than direct textual statements.
- The current model uses aggregate symbolic entities such as `sleeve`, `o_ring`, `screw`, and `rod_holes`, rather than individual numbered sleeves, O-rings, screws, and holes.
- The remaining Step 6 uncertainty reflects the choice not to assert screw alignment as observed without stronger evidence.

These limitations are acceptable for a reasoning-layer transfer test, but they should not be described as perception-level validation.

