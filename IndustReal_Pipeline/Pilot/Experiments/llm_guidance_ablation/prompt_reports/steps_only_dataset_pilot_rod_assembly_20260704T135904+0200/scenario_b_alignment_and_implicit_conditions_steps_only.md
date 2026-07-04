# Prompt Report: scenario_b_alignment_and_implicit_conditions

Generated at: 2026-07-04T14:00:41+02:00

- Condition: `steps_only`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
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


## Case: q07_o_ring_alignment_requirement

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: Where should the O-rings be aligned, and is that represented as something achieved in this step?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now`
- Expected answer elements:
  - identify rod_holes as the O-ring installation target
  - state aligned(o_ring, rod_holes)
  - state that Step 3 produces this as manual symbolic annotation

## Case: q08_sleeve_alignment_requirement

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: The sleeve is on the rod, but what should it be aligned with after the O-rings are placed?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now`
- Expected answer elements:
  - identify o_ring as the sleeve alignment reference
  - state aligned(sleeve, o_ring)
  - explain that this is distinct from the sleeve installation target metal_rod

## Case: q09_screw_alignment_before_tightening

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: Before fully tightening the screws, what screw alignment checks are still not confirmed?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now; expected uncertain`
- Expected answer elements:
  - identify aligned(screw, rod_holes)
  - identify aligned(screw, o_ring)
  - state that these are missing or unsupported in the current graph
  - explain that this is why Step 6 is uncertain

## Case: q10_requirement_not_observation

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: The model says the screw must align with the O-ring. Does that mean the graph observed it?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now; expected uncertain`
- Expected answer elements:
  - answer no
  - distinguish required condition from observed effect
  - identify pilot_domain_default as requirement provenance
  - avoid treating configured requirement as evidence

## Case: q11_rod_holes_belong_to_rod

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: When the instruction says all holes, are those holes modeled as part of the rod or as separate components?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now`
- Expected answer elements:
  - identify rod_holes
  - state that rod_holes are modeled as RodHole or RodFeature
  - state hasParentComponent(rod_holes, metal_rod)
  - avoid calling rod_holes an installable component

