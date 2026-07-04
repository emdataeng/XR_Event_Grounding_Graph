# Prompt Report: scenario_f_missing_evidence_controls

Generated at: 2026-07-04T14:03:39+02:00

- Condition: `symbolic_domain`
- Scenario: `scenario_f_missing_evidence_controls`
- Cases in this report: `5`

## API Request Settings

- LLM config path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\llm_api_masoud.yaml`
- API base URL: `https://counseling-inspired-sizes-yellow.trycloudflare.com/v1`
- Model name: `google/gemma-4-26b-a4b-qat`
- Temperature: `0.0`
- Max tokens: `2048`
- Request timeout seconds: `3600.0`
- Max retries: `0`

## Run Timing Statistics

These statistics cover all successful prompt interactions in this experiment run.

- Completed interactions: `31`
- Failed interactions: `0`
- Minimum prompt time: `2.37 s`
- Maximum prompt time: `11.67 s`
- Average prompt time: `5.74 s`
- Total experiment time: `00h 02m 58.06s`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v1_pilot_rod_assembly.yaml`
- ID: `novice_questions_pilot_rod_assembly`
- Version: `v1`
- Case count: `31`
- SHA-256: `60a2ed6fae1d`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `Pilot\rod_assembly_step_list.txt`
- Step-list artifact loaded: `True`
- Windowed predicates included: `yes`
- Sequence step-hop radius: `1`
- Semantic evidence-hop radius: `not applicable`
- Thesis rules included: `yes`
- Procedural reasoning graph included: `no`

All conditions include the same frozen step-list artifact. The `symbolic_domain` condition adds a deterministic predicate window and `thesis_rules.yaml`; `graph_grounded` adds a deterministic local graph neighborhood.

## Graph Provenance

- Graph provenance: `not applicable to this condition`

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### Actual System Message Sent

- Role: `system`

```text
You are an assistant helping a novice assembly operator perform a manufacturing task. Answer the operator's specific question directly, using only the information provided. Be concise, practical, and safety-aware. Do not use any knowledge beyond what is explicitly provided. If information is missing, uncertain, or conflicting, say so clearly rather than guessing. Write in plain language as if you were directly guiding the operator. Translate technical notation, predicate names, relation labels, graph terms, and internal system terminology into natural wording. Do not write predicate-like phrases such as "requires installed(...)", "produces installed(...)", "hasInstallTarget(...)", or relation labels such as "SUPPORTED_BY" or "DEPENDS_ON"; explain their meaning instead. You may mention step numbers, part names, tool names, and earlier actions when they help answer the operator's question or support the answer. If the question asks what happens next or what earlier action supports the current step, answer that using only the provided information. Do not expose internal labels unless they are necessary to identify a part, tool, or step. Keep the answer precise and directly useful. Do not add extra coaching, encouragement, or procedural advice unless it is supported by the provided information. End every response with the exact marker "(EOR)" on the final line.
```

### Frozen Procedural Step List

This block is inserted into the user message for every case.

```text
Pilot rod assembly procedure:

Step 1 [0-15s]: The operator places a long metal rod on the workbench.

Step 2 [15-89s]: The operator slides a combination of long, short and copper sleeves onto the rod. The copper sleeve should face to the right. The procedure specifies six copper sleeves and five long sleeves, starting and finishing with copper sleeves.

Step 3 [89-196s]: The operator places O-rings in the holes on the rod and adjusts the sleeves over them.

Step 4 [196-376s]: The operator drives the screws halfway into all holes using a power screwdriver.

Step 5 [376-429s]: The operator applies threadlocker (Loctite) to all partially inserted screws.

Step 6 [429-531s]: The operator fully tightens all screws to secure the sleeves. The screws should go all the way into the sleeve, but not so far that they stick out.

Step 7 [531-566s]: The operator cleans the rod and sleeves with ethanol and paper. The copper part should not be polished.

Step 8 [566-642s]: The operator applies grease to a sponge and lubricates the silver-colored sleeves while avoiding the copper sleeves.

```

### Thesis Rules

This block is inserted into the user message for every case.

```yaml
schema_version: pilot_thesis_rules.v1
rule_set_version: "0.1.0"
domain_name: rod_assembly

adapter:
  predicates:
    event:
      has_action:
        name: hasAction
        description: "Associates a step with its normalized action label."
        args: [step_id, action_name]
        enabled: true
      has_time_window:
        name: hasTimeWindow
        description: "Associates a step with its start and end timestamps."
        args: [step_id, start_s, end_s]
        enabled: true
    object_interaction:
      uses_object:
        name: usesObject
        description: "Associates a step with an object it acts on."
        args: [step_id, object_id]
        enabled: true
      uses_tool:
        name: usesTool
        description: "Associates a step with a tool it uses."
        args: [step_id, tool_id]
        enabled: true
      uses_material:
        name: usesMaterial
        description: "Associates a step with a material it uses."
        args: [step_id, material_id]
        enabled: true
    entity_metadata:
      is_a:
        name: isA
        description: "Associates an individual with a generic class."
        args: [individual_id, type_name]
        enabled: true
      has_label:
        name: hasLabel
        description: "Associates an individual with its display label."
        args: [individual_id, label]
        enabled: true
      has_parent_component:
        name: hasParentComponent
        description: "Associates a feature or component with the component it belongs to."
        args: [individual_id, parent_component_id]
        enabled: true
      has_required_condition:
        name: hasRequiredCondition
        description: "Associates a step with a condition that must already hold."
        args: [step_id, condition_name, arg_1, arg_2]
        enabled: true
      has_observed_effect:
        name: hasObservedEffect
        description: "Associates a step with an effect explicitly stated in the Pilot procedure."
        args: [step_id, condition_name, arg_1, arg_2]
        enabled: true
      has_required_tool:
        name: hasRequiredTool
        description: "Associates a step with a tool required by the procedure."
        args: [step_id, tool_id]
        enabled: true

predicate_vocabulary:
  hasAction: {arity: 2, description: "Associates a step with its normalized action label."}
  hasTimeWindow: {arity: 3, description: "Associates a step with its start and end timestamps."}
  usesObject: {arity: 2, description: "Associates a step with an object it acts on."}
  usesTool: {arity: 2, description: "Associates a step with a tool it uses."}
  usesMaterial: {arity: 2, description: "Associates a step with a material it uses."}
  isA: {arity: 2, description: "Associates an individual with a generic class."}
  hasLabel: {arity: 2, description: "Associates an individual with its display label."}
  hasParentComponent: {arity: 2, description: "Associates a feature or component with the component it belongs to."}
  hasRequiredCondition: {arity: 4, description: "Associates a step with a condition that must already hold."}
  hasObservedEffect: {arity: 4, description: "Associates a step with an explicitly annotated effect."}
  hasRequiredTool: {arity: 2, description: "Associates a step with a required tool."}
  requires: {arity: 4, description: "Layer 3 inferred precondition."}
  produces: {arity: 4, description: "Layer 3 expected effect."}
  requiresTool: {arity: 2, description: "Layer 3 inferred tool requirement."}
  incompatibleAction: {arity: 3, description: "Layer 3 inferred incompatibility."}

predicate_aliases:
  stepHasAction: hasAction
  actsOn: usesObject
  typeOf: isA
  has_action: hasAction
  acts_on: usesObject
  uses_tool: usesTool
  uses_material: usesMaterial

defaults:
  threshold: 0.70
  aggregation: min

validation:
  tau_acc: 0.70
  tau_unc: 0.35

rule_types:
  inferred_precondition: "Derives conditions that must hold before a step is accepted."
  expected_effect: "Derives the symbolic effects produced by accepted steps."
  required_tool: "Infers a tool requirement for a step."
  compatibility: "Identifies inadmissible symbolic steps."

rules:
  - id: effect_observed_pilot_condition
    type: expected_effect
    threshold: 0.70
    antecedents:
      - {name: hasAction, args: ["?s", "?action"]}
      - {name: hasObservedEffect, args: ["?s", "?condition", "?arg1", "?arg2"]}
    constraints:
      - {name: produces, kind: expected_effect, args: ["?s", "?condition", "?arg1", "?arg2"]}

  - id: precondition_required_pilot_condition
    type: inferred_precondition
    threshold: 0.70
    antecedents:
      - {name: hasAction, args: ["?s", "?action"]}
      - {name: hasRequiredCondition, args: ["?s", "?condition", "?arg1", "?arg2"]}
    constraints:
      - {name: requires, kind: inferred_precondition, args: ["?s", "?condition", "?arg1", "?arg2"]}

  - id: tool_required_by_pilot_step
    type: required_tool
    threshold: 0.70
    antecedents:
      - {name: hasRequiredTool, args: ["?s", "?tool"]}
    constraints:
      - {name: requiresTool, kind: required_tool, args: ["?s", "?tool"]}

  - id: compatibility_error_action_marks_incompatibility
    type: compatibility
    threshold: 0.70
    antecedents:
      - {name: hasAction, args: ["?s", "error"]}
      - {name: usesObject, args: ["?s", "?object"]}
    constraints:
      - {name: incompatibleAction, kind: compatibility, args: ["?s", "?object", "error"]}

```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q27_unknown_step

- Step id: `step::pilot_rod_assembly::step_99`
- Operator question: I cannot find this step in the rod assembly. What should I do next?

### Selected Symbolic Predicates

```text
No predicate context was found for current step id: step::pilot_rod_assembly::step_99
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that the step is absent
  - request a valid step id or procedure context
  - avoid fabricating a step

## Case: q28_unmodeled_torque

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: What torque should I use when fully tightening the screws?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::pilot_rod_assembly::step_06
- step_hops: 1
- included_step_ids: ["step::pilot_rod_assembly::step_05", "step::pilot_rod_assembly::step_06", "step::pilot_rod_assembly::step_07"]

Selected predicates:
step_05: hasAction["step::pilot_rod_assembly::step_05","apply"] [conf=1.0]
step_05: hasTimeWindow["step::pilot_rod_assembly::step_05",376,429] [conf=1.0]
step_05: usesObject["step::pilot_rod_assembly::step_05","screw"] [conf=1.0]
step_05: usesMaterial["step::pilot_rod_assembly::step_05","threadlocker_loctite"] [conf=1.0]
step_05: hasRequiredCondition["step::pilot_rod_assembly::step_05","partially_inserted_in","screw","rod_holes"] [conf=1.0]
step_05: hasObservedEffect["step::pilot_rod_assembly::step_05","applied_to","threadlocker_loctite","screw"] [conf=1.0]
step_06: hasAction["step::pilot_rod_assembly::step_06","tighten"] [conf=1.0]
step_06: hasTimeWindow["step::pilot_rod_assembly::step_06",429,531] [conf=1.0]
step_06: usesObject["step::pilot_rod_assembly::step_06","screw"] [conf=1.0]
step_06: usesTool["step::pilot_rod_assembly::step_06","power_screwdriver"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","applied_to","threadlocker_loctite","screw"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","aligned","screw","rod_holes"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","aligned","screw","o_ring"] [conf=1.0]
step_06: hasRequiredTool["step::pilot_rod_assembly::step_06","power_screwdriver"] [conf=1.0]
step_06: hasObservedEffect["step::pilot_rod_assembly::step_06","secured","sleeve","metal_rod"] [conf=1.0]
step_06: hasObservedEffect["step::pilot_rod_assembly::step_06","flush_with","screw","sleeve"] [conf=1.0]
step_07: hasAction["step::pilot_rod_assembly::step_07","clean"] [conf=1.0]
step_07: hasTimeWindow["step::pilot_rod_assembly::step_07",531,566] [conf=1.0]
step_07: usesObject["step::pilot_rod_assembly::step_07","rod_assembly"] [conf=1.0]
step_07: usesMaterial["step::pilot_rod_assembly::step_07","ethanol"] [conf=1.0]
step_07: usesMaterial["step::pilot_rod_assembly::step_07","paper"] [conf=1.0]
step_07: hasRequiredCondition["step::pilot_rod_assembly::step_07","secured","sleeve","metal_rod"] [conf=1.0]
step_07: hasObservedEffect["step::pilot_rod_assembly::step_07","cleaned_with","rod_assembly","ethanol"] [conf=1.0]
step_07: hasObservedEffect["step::pilot_rod_assembly::step_07","avoided_contact_with","copper_sleeve","paper"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that no torque value is represented
  - avoid inventing a torque
  - refer to the official procedure or supervisor

## Case: q29_direct_video_confirmation

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Can you confirm from the video that every screw is aligned with every O-ring?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::pilot_rod_assembly::step_04
- step_hops: 1
- included_step_ids: ["step::pilot_rod_assembly::step_03", "step::pilot_rod_assembly::step_04", "step::pilot_rod_assembly::step_05"]

Selected predicates:
step_03: hasAction["step::pilot_rod_assembly::step_03","place"] [conf=1.0]
step_03: hasTimeWindow["step::pilot_rod_assembly::step_03",89,196] [conf=1.0]
step_03: usesObject["step::pilot_rod_assembly::step_03","o_ring"] [conf=1.0]
step_03: usesObject["step::pilot_rod_assembly::step_03","sleeve"] [conf=1.0]
step_03: isA["rod_holes","RodHole"] [conf=1.0]
step_03: hasParentComponent["rod_holes","metal_rod"] [conf=1.0]
step_03: hasRequiredCondition["step::pilot_rod_assembly::step_03","sleeves_on","sleeve","metal_rod"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","inserted_in","o_ring","rod_holes"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","aligned","o_ring","rod_holes"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","adjusted_over","sleeve","o_ring"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","aligned","sleeve","o_ring"] [conf=1.0]
step_04: hasAction["step::pilot_rod_assembly::step_04","drive"] [conf=1.0]
step_04: hasTimeWindow["step::pilot_rod_assembly::step_04",196,376] [conf=1.0]
step_04: usesObject["step::pilot_rod_assembly::step_04","screw"] [conf=1.0]
step_04: usesTool["step::pilot_rod_assembly::step_04","power_screwdriver"] [conf=1.0]
step_04: isA["rod_holes","RodHole"] [conf=1.0]
step_04: hasParentComponent["rod_holes","metal_rod"] [conf=1.0]
step_04: hasRequiredCondition["step::pilot_rod_assembly::step_04","inserted_in","o_ring","rod_holes"] [conf=1.0]
step_04: hasRequiredCondition["step::pilot_rod_assembly::step_04","aligned","o_ring","rod_holes"] [conf=1.0]
step_04: hasRequiredCondition["step::pilot_rod_assembly::step_04","adjusted_over","sleeve","o_ring"] [conf=1.0]
step_04: hasRequiredCondition["step::pilot_rod_assembly::step_04","aligned","sleeve","o_ring"] [conf=1.0]
step_04: hasRequiredTool["step::pilot_rod_assembly::step_04","power_screwdriver"] [conf=1.0]
step_04: hasObservedEffect["step::pilot_rod_assembly::step_04","partially_inserted_in","screw","rod_holes"] [conf=1.0]
step_05: hasAction["step::pilot_rod_assembly::step_05","apply"] [conf=1.0]
step_05: hasTimeWindow["step::pilot_rod_assembly::step_05",376,429] [conf=1.0]
step_05: usesObject["step::pilot_rod_assembly::step_05","screw"] [conf=1.0]
step_05: usesMaterial["step::pilot_rod_assembly::step_05","threadlocker_loctite"] [conf=1.0]
step_05: hasRequiredCondition["step::pilot_rod_assembly::step_05","partially_inserted_in","screw","rod_holes"] [conf=1.0]
step_05: hasObservedEffect["step::pilot_rod_assembly::step_05","applied_to","threadlocker_loctite","screw"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that no raw video evidence is available in this reasoning graph
  - state that screw-O-ring alignment is not confirmed
  - distinguish graph requirement from visual confirmation

## Case: q30_exact_instance_count

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: Can you list the exact identity of each of the six copper sleeves and five long sleeves?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::pilot_rod_assembly::step_02
- step_hops: 1
- included_step_ids: ["step::pilot_rod_assembly::step_01", "step::pilot_rod_assembly::step_02", "step::pilot_rod_assembly::step_03"]

Selected predicates:
step_01: hasAction["step::pilot_rod_assembly::step_01","place"] [conf=1.0]
step_01: hasTimeWindow["step::pilot_rod_assembly::step_01",0,15] [conf=1.0]
step_01: usesObject["step::pilot_rod_assembly::step_01","metal_rod"] [conf=1.0]
step_01: usesObject["step::pilot_rod_assembly::step_01","workbench"] [conf=1.0]
step_01: hasObservedEffect["step::pilot_rod_assembly::step_01","on","metal_rod","workbench"] [conf=1.0]
step_01: hasObservedEffect["step::pilot_rod_assembly::step_01","secured","metal_rod","workbench"] [conf=1.0]
step_02: hasAction["step::pilot_rod_assembly::step_02","slide"] [conf=1.0]
step_02: hasTimeWindow["step::pilot_rod_assembly::step_02",15,89] [conf=1.0]
step_02: usesObject["step::pilot_rod_assembly::step_02","sleeve"] [conf=1.0]
step_02: usesObject["step::pilot_rod_assembly::step_02","long_sleeve"] [conf=1.0]
step_02: usesObject["step::pilot_rod_assembly::step_02","short_sleeve"] [conf=1.0]
step_02: usesObject["step::pilot_rod_assembly::step_02","copper_sleeve"] [conf=1.0]
step_02: usesObject["step::pilot_rod_assembly::step_02","metal_rod"] [conf=1.0]
step_02: hasRequiredCondition["step::pilot_rod_assembly::step_02","secured","metal_rod","workbench"] [conf=1.0]
step_02: hasObservedEffect["step::pilot_rod_assembly::step_02","sleeves_on","sleeve","metal_rod"] [conf=1.0]
step_02: hasObservedEffect["step::pilot_rod_assembly::step_02","oriented","copper_sleeve","right_side"] [conf=1.0]
step_02: hasObservedEffect["step::pilot_rod_assembly::step_02","count_verified","copper_sleeve","required_quantity_six"] [conf=1.0]
step_02: hasObservedEffect["step::pilot_rod_assembly::step_02","count_verified","long_sleeve","required_quantity_five"] [conf=1.0]
step_03: hasAction["step::pilot_rod_assembly::step_03","place"] [conf=1.0]
step_03: hasTimeWindow["step::pilot_rod_assembly::step_03",89,196] [conf=1.0]
step_03: usesObject["step::pilot_rod_assembly::step_03","o_ring"] [conf=1.0]
step_03: usesObject["step::pilot_rod_assembly::step_03","sleeve"] [conf=1.0]
step_03: isA["rod_holes","RodHole"] [conf=1.0]
step_03: hasParentComponent["rod_holes","metal_rod"] [conf=1.0]
step_03: hasRequiredCondition["step::pilot_rod_assembly::step_03","sleeves_on","sleeve","metal_rod"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","inserted_in","o_ring","rod_holes"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","aligned","o_ring","rod_holes"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","adjusted_over","sleeve","o_ring"] [conf=1.0]
step_03: hasObservedEffect["step::pilot_rod_assembly::step_03","aligned","sleeve","o_ring"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that the graph has aggregate sleeve entities
  - state that count_verified facts exist
  - avoid inventing individual sleeve identifiers

## Case: q31_ambiguous_okay_question

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: Is this okay?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::pilot_rod_assembly::step_06
- step_hops: 1
- included_step_ids: ["step::pilot_rod_assembly::step_05", "step::pilot_rod_assembly::step_06", "step::pilot_rod_assembly::step_07"]

Selected predicates:
step_05: hasAction["step::pilot_rod_assembly::step_05","apply"] [conf=1.0]
step_05: hasTimeWindow["step::pilot_rod_assembly::step_05",376,429] [conf=1.0]
step_05: usesObject["step::pilot_rod_assembly::step_05","screw"] [conf=1.0]
step_05: usesMaterial["step::pilot_rod_assembly::step_05","threadlocker_loctite"] [conf=1.0]
step_05: hasRequiredCondition["step::pilot_rod_assembly::step_05","partially_inserted_in","screw","rod_holes"] [conf=1.0]
step_05: hasObservedEffect["step::pilot_rod_assembly::step_05","applied_to","threadlocker_loctite","screw"] [conf=1.0]
step_06: hasAction["step::pilot_rod_assembly::step_06","tighten"] [conf=1.0]
step_06: hasTimeWindow["step::pilot_rod_assembly::step_06",429,531] [conf=1.0]
step_06: usesObject["step::pilot_rod_assembly::step_06","screw"] [conf=1.0]
step_06: usesTool["step::pilot_rod_assembly::step_06","power_screwdriver"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","applied_to","threadlocker_loctite","screw"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","aligned","screw","rod_holes"] [conf=1.0]
step_06: hasRequiredCondition["step::pilot_rod_assembly::step_06","aligned","screw","o_ring"] [conf=1.0]
step_06: hasRequiredTool["step::pilot_rod_assembly::step_06","power_screwdriver"] [conf=1.0]
step_06: hasObservedEffect["step::pilot_rod_assembly::step_06","secured","sleeve","metal_rod"] [conf=1.0]
step_06: hasObservedEffect["step::pilot_rod_assembly::step_06","flush_with","screw","sleeve"] [conf=1.0]
step_07: hasAction["step::pilot_rod_assembly::step_07","clean"] [conf=1.0]
step_07: hasTimeWindow["step::pilot_rod_assembly::step_07",531,566] [conf=1.0]
step_07: usesObject["step::pilot_rod_assembly::step_07","rod_assembly"] [conf=1.0]
step_07: usesMaterial["step::pilot_rod_assembly::step_07","ethanol"] [conf=1.0]
step_07: usesMaterial["step::pilot_rod_assembly::step_07","paper"] [conf=1.0]
step_07: hasRequiredCondition["step::pilot_rod_assembly::step_07","secured","sleeve","metal_rod"] [conf=1.0]
step_07: hasObservedEffect["step::pilot_rod_assembly::step_07","cleaned_with","rod_assembly","ethanol"] [conf=1.0]
step_07: hasObservedEffect["step::pilot_rod_assembly::step_07","avoided_contact_with","copper_sleeve","paper"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - ask what specific condition or component the operator is concerned about
  - mention that Step 6 has unresolved screw alignment requirements
  - avoid giving a blanket go-ahead

