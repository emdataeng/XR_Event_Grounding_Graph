# Prompt Report: scenario_c_tools_materials_counts_and_orientation

Generated at: 2026-07-04T14:00:41+02:00

- Condition: `steps_only`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Cases in this report: `6`

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


## Case: q12_power_screwdriver_step_four

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Which tool do I need to drive the screws halfway in, and is its use observed or only required?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify power_screwdriver
  - state that Step 4 has usesTool(power_screwdriver)
  - state that Step 4 also has a requiresTool condition
  - distinguish observed tool use from required tool

## Case: q13_power_screwdriver_step_six

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: For fully tightening the screws, is the required power screwdriver confirmed, or is the uncertainty caused by something else?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now; step uncertain for non-tool reasons`
- Expected answer elements:
  - identify power_screwdriver as required and observed
  - state that tool support is present
  - state that uncertainty comes from missing screw alignment support

## Case: q14_threadlocker_material

- Step id: `step::pilot_rod_assembly::step_05`
- Operator question: What material is applied to the screws before final tightening, and what condition does it produce?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify threadlocker_loctite
  - identify applied_to(threadlocker_loctite, screw)
  - state that Step 6 requires this effect

## Case: q15_sleeve_count_and_orientation

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: What count and orientation checks are represented for the sleeves?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify count_verified(copper_sleeve, required_quantity_six)
  - identify count_verified(long_sleeve, required_quantity_five)
  - identify oriented(copper_sleeve, right_side)
  - avoid claiming individual sleeve instance tracking

## Case: q16_cleaning_materials

- Step id: `step::pilot_rod_assembly::step_07`
- Operator question: What should I clean with, and what should I avoid doing to the copper sleeve?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify ethanol and paper
  - identify cleaned_with(rod_assembly, ethanol)
  - identify avoided_contact_with(copper_sleeve, paper)
  - explain that the procedure says not to polish the copper part

## Case: q17_grease_application

- Step id: `step::pilot_rod_assembly::step_08`
- Operator question: Which sleeves get grease, what tool is used, and what should not get grease?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify silver_sleeve
  - identify sponge
  - identify grease
  - identify avoided_contact_with(copper_sleeve, grease)

