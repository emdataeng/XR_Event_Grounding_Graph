# Prompt Report: sequence_error

Generated at: 2026-06-19T11:03:28.797598+00:00

- Condition: `steps_only`
- Risk type: `sequence_error`
- Cases in this report: `3`

## API Request Settings

- API base URL: `http://localhost:1234/v1`
- Model name: `mistralai/mistral-7b-instruct-v0.3`
- Temperature: `0.0`
- Max tokens: `512`

## Run Timing Statistics

These statistics cover all successful prompt interactions in this experiment run.

- Completed interactions: `19`
- Minimum prompt time: `13.47 s`
- Maximum prompt time: `37.16 s`
- Average prompt time: `19.70 s`
- Total experiment time: `00h 06m 14.27s`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `experiments\llm_guidance_ablation\data\steps_od_only_test_p1_03_assy_0_1.txt`
- Step-list artifact loaded: `True`
- Windowed predicates included: `no`
- Step-hop radius: `not applicable`
- Thesis rules included: `no`
- Procedural reasoning graph included: `no`

Both implemented conditions include the same frozen step-list artifact. The `symbolic_domain` condition additionally includes a deterministic predicate window around the current step and the complete `thesis_rules.yaml` file.

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### System Message

- Role: `system`

```text
You are an assistant helping a novice assembly operator. Answer using only the procedural step context provided. Do not infer missing assembly steps from general knowledge. Be concise, practical, and safety-aware. If the provided step context is ambiguous, say what is uncertain.
```

### Frozen Procedural Step List

This block is inserted into the user message for every case.

```text
Available assembly steps:
- Step 0: Install base
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0
  - acted_on_object: base
  - previous_step_id: none
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
  - time_window: start_frame=709, end_frame=1187
  - confidence: 1.0
- Step 1: Install rear chassis
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
  - acted_on_object: rear chassis
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
  - time_window: start_frame=709, end_frame=1187
  - confidence: 1.0
- Step 2: Install front rear chassis pin
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
  - acted_on_object: front rear chassis pin
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3
  - time_window: start_frame=709, end_frame=1187
  - confidence: 1.0
- Step 3: Install front chassis
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3
  - acted_on_object: front chassis
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
  - time_window: start_frame=1187, end_frame=1788
  - confidence: 1.0
- Step 4: Install front chassis pin
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
  - acted_on_object: front chassis pin
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5
  - time_window: start_frame=1187, end_frame=1788
  - confidence: 1.0
- Step 5: Install rear rear chassis pin
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5
  - acted_on_object: rear rear chassis pin
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_6
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 6: Install front bracket
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_6
  - acted_on_object: front bracket
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_7
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 7: Install front bracket screw
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_7
  - acted_on_object: front bracket screw
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_6
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_8
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 8: Install front wheel assy
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_8
  - acted_on_object: front wheel assy
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_7
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_9
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 9: Remove front wheel assy
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_9
  - acted_on_object: front wheel assy
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_8
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_10
  - time_window: start_frame=2735, end_frame=None
  - confidence: 1.0
- Step 10: Install rear wheel assy
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_10
  - acted_on_object: rear wheel assy
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_9
  - next_step_id: none
  - time_window: start_frame=2735, end_frame=None
  - confidence: 1.0

```



## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: case_001_missing_context

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_001`
- Operator question: I am not sure which part should be installed next. What should I do before continuing?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `sequence_error`
- Expected answer elements:
  - identify the current procedural step
  - state the next required action
  - warn against skipping prerequisite steps

## Case: sequence_002_named_part_timing

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_002`
- Operator question: Am I supposed to install the front chassis now?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `sequence_error`
- Expected answer elements:
  - compare the named part against the current step
  - state whether it matches the current step
  - refer to previous or next step when useful

## Case: sequence_003_after_previous_action

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_004`
- Operator question: I finished the previous part and want to move on. Which step should I check before continuing?


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `sequence_error`
- Expected answer elements:
  - use current step id
  - mention previous and next step relationship
  - recommend confirming the current step before proceeding

