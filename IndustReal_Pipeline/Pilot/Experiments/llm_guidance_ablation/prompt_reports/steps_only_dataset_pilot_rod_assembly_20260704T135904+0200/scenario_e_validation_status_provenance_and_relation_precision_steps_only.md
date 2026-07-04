# Prompt Report: scenario_e_validation_status_provenance_and_relation_precision

Generated at: 2026-07-04T14:00:41+02:00

- Condition: `steps_only`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
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
- Minimum prompt time: `1.61 s`
- Maximum prompt time: `4.54 s`
- Average prompt time: `3.13 s`
- Total experiment time: `00h 01m 36.98s`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v1_pilot_rod_assembly.yaml`
- ID: `novice_questions_pilot_rod_assembly`
- Version: `v1`
- Case count: `31`
- SHA-256: `60a2ed6fae1d`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `Pilot\rod_assembly_step_list.txt`
- Step-list artifact loaded: `True`
- Windowed predicates included: `no`
- Sequence step-hop radius: `not applicable`
- Semantic evidence-hop radius: `not applicable`
- Thesis rules included: `no`
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



## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q22_why_step_six_uncertain

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: Why is the final tightening step uncertain even though the threadlocker and power screwdriver are present?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - identify supported applied_to(threadlocker_loctite, screw)
  - identify supported partially_inserted_in(screw, rod_holes)
  - identify supported required tool power_screwdriver
  - identify missing aligned(screw, rod_holes) and aligned(screw, o_ring)

## Case: q23_expert_annotation_provenance

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: The sleeve step depends on the rod being secured. Was that direct step text, a domain requirement, or an expert assumption?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - state that Step 2 requires secured(metal_rod, workbench) from pilot_domain_default
  - state that Step 1 produces secured(metal_rod, workbench) as manual_expert_annotation
  - distinguish this from direct text evidence on(metal_rod, workbench)

## Case: q24_relation_precision_targets

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: What is the screw installed into, what does it need to align with, and what does it eventually secure?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - installation target is rod_holes
  - alignment requirements are rod_holes and o_ring
  - final secured relation is secured(sleeve, metal_rod)
  - avoid conflating screw target with sleeve secured target

## Case: q25_why_step_three_accepted

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: Why is the O-ring placement step accepted? What earlier step makes it valid?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - identify required sleeves_on(sleeve, metal_rod)
  - identify Step 2 as support
  - identify Step 3 produced effects for O-ring insertion/alignment and sleeve adjustment/alignment

## Case: q26_domain_default_not_fake_observation

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Some requirements come from the domain model. How can I tell whether they were actually observed?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - use provenance to distinguish pilot_domain_default from manual_symbolic_annotation
  - check SUPPORTED_BY or produced effects
  - explain that requirements are not observations by themselves

