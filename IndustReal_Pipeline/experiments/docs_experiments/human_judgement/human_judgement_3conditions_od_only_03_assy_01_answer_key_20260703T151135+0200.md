# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-03T15:11:35+02:00`
Random seed: `20260703151135`
Clip name: `od_only_03_assy_01`
Question set path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v4_od_only_test_p1_03_assy_0_1.yaml`

Do not share this file with judges before scoring.

## How to Score

Use the criteria from `Evaluator Instructions.pdf`. Score each answer independently on its own merits, without trying to infer which condition produced it and without comparing it to other answers. Use the full task reference material as the source of truth.

Assign a score from `1` to `5` for each criterion:

| Criterion | What to evaluate |
|---|---|
| Correctness | Whether the answer is technically accurate, consistent with the reference material, and free of false or misleading claims. |
| Completeness | Whether the answer covers all relevant information needed to address the operator's question. |
| Safety | Whether the answer mentions relevant risks, warnings, missing checks, or precautions, and avoids forcing irrelevant safety content when safety is not applicable. |
| Actionability / Usefulness | Whether a novice operator could act on the answer immediately without needing a follow-up question. |
| Explainability | Whether the answer explains the reasoning behind the instruction when that explanation would help the operator. Do not penalize brief factual answers that genuinely need little explanation. |

Score anchors: `1` means poor or unusable for that criterion, `3` means partially adequate with noticeable gaps, and `5` means fully satisfactory. Scores across criteria may differ for the same answer. Add notes for edge cases or uncertain judgements.


## Source Files

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_od_only_03_assy_01_20260703T134410+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_od_only_03_assy_01_20260703T134615+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_od_only_03_assy_01_20260703T135325+0200.jsonl`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v4_od_only_test_p1_03_assy_0_1.yaml`
- ID: `novice_questions_od_only_test_p1_03_assy_0_1`
- Version: `v4`
- Case count: `28`
- SHA-256: `777b9be54b1e716f8108e0a217f3522fe97aa267cefc19c59fa245808e058681`

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q23_relation_label_precision` | `steps_only` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.677559` |
| 02 | `q25_video_confirmation` | `symbolic_domain` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `5.325087` |
| 03 | `q07_component_alignment` | `query_driven_graph` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `17.136423` |
| 04 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.309827` |
| 05 | `q26_unmodeled_torque` | `query_driven_graph` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `16.503921` |
| 06 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.664579` |
| 07 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.755714` |
| 08 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `6.072239` |
| 09 | `q07_component_alignment` | `steps_only` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `5.969468` |
| 10 | `q25_video_confirmation` | `steps_only` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `3.456799` |
| 11 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.928665` |
| 12 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.718911` |
| 13 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.131221` |
| 14 | `q05_nested_prerequisite` | `query_driven_graph` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `17.637421` |
| 15 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.7755` |
| 16 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.390081` |
| 17 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.481748` |
| 18 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.390957` |
| 19 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.676657` |
| 20 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.5734` |
| 21 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.628848` |
| 22 | `q05_nested_prerequisite` | `steps_only` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.349377` |
| 23 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.275439` |
| 24 | `q05_nested_prerequisite` | `symbolic_domain` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.324166` |
| 25 | `q03_direct_installation_target` | `steps_only` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.309943` |
| 26 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.397199` |
| 27 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `6.020144` |
| 28 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.954454` |
| 29 | `q25_video_confirmation` | `query_driven_graph` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `18.229335` |
| 30 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.398527` |
| 31 | `q03_direct_installation_target` | `query_driven_graph` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `16.122519` |
| 32 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.502343` |
| 33 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.402383` |
| 34 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `11.640722` |
| 35 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.523106` |
| 36 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.838767` |
| 37 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `12.466248` |
| 38 | `q15_unsupported_tool_proposal` | `steps_only` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.793747` |
| 39 | `q12_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.260501` |
| 40 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `7.176963` |
| 41 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.25475` |
| 42 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.177732` |
| 43 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `17.693269` |
| 44 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.72265` |
| 45 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.479213` |
| 46 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.302237` |
| 47 | `q12_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.441477` |
| 48 | `q23_relation_label_precision` | `query_driven_graph` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.960482` |
| 49 | `q17_removal_precondition` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `14.332746` |
| 50 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.042441` |
| 51 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.013959` |
| 52 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `8.227211` |
| 53 | `q23_relation_label_precision` | `symbolic_domain` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.370792` |
| 54 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `21.43846` |
| 55 | `q16_combined_requirements` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.90974` |
| 56 | `q17_removal_precondition` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `20.797662` |
| 57 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `17.706185` |
| 58 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `18.843136` |
| 59 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `17.444377` |
| 60 | `q12_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.102548` |
| 61 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `17.091397` |
| 62 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_4` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.916115` |
| 63 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.891545` |
| 64 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `7.704249` |
| 65 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `7.772618` |
| 66 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.502967` |
| 67 | `q07_component_alignment` | `symbolic_domain` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.620544` |
| 68 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `3.254128` |
| 69 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `6.473118` |
| 70 | `q26_unmodeled_torque` | `symbolic_domain` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `3.455305` |
| 71 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.031935` |
| 72 | `q26_unmodeled_torque` | `steps_only` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `3.047595` |
| 73 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.269378` |
| 74 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `16.036926` |
| 75 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.085025` |
| 76 | `q17_removal_precondition` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `5.867824` |
| 77 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.461057` |
| 78 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `9.490967` |
| 79 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.299029` |
| 80 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.22287` |
| 81 | `q04_wrong_part_target_check` | `steps_only` | `step_4` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.752183` |
| 82 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `9.96024` |
| 83 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_4` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.944216` |
| 84 | `q03_direct_installation_target` | `symbolic_domain` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.070185` |
