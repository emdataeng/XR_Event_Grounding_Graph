# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-03T15:08:39+02:00`
Random seed: `20260703150839`
Clip name: `od_plus_error_hints_03_assy_1_3`
Question set path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v4_od_plus_psr_error_hints_test_p1_03_assy_1_3.yaml`

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

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_od_plus_error_hints_03_assy_1_3_20260703T143418+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_od_plus_error_hints_03_assy_1_3_20260703T143628+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_od_plus_error_hints_03_assy_1_3_20260703T145314+0200.jsonl`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v4_od_plus_psr_error_hints_test_p1_03_assy_1_3.yaml`
- ID: `novice_questions_od_plus_psr_error_hints_test_p1_03_assy_1_3`
- Version: `v4`
- Case count: `28`
- SHA-256: `f0620a935a11a0c47bf3ff62c458eb9bffb8edda0d22e96e212ecf9b325a9cad`

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.106614` |
| 02 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `7.883394` |
| 03 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.84` |
| 04 | `q07_component_alignment` | `symbolic_domain` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `15.357056` |
| 05 | `q12_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_6` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.001557` |
| 06 | `q17_removal_precondition` | `query_driven_graph` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `23.250317` |
| 07 | `q25_video_confirmation` | `query_driven_graph` | `step_6` | `scenario_f_missing_evidence_controls` | `ok` | `19.935157` |
| 08 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `4.891931` |
| 09 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.492386` |
| 10 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `25.549376` |
| 11 | `q16_combined_requirements` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.99604` |
| 12 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_6` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.228317` |
| 13 | `q03_direct_installation_target` | `symbolic_domain` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.015871` |
| 14 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `16.791294` |
| 15 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.029132` |
| 16 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.532117` |
| 17 | `q23_relation_label_precision` | `steps_only` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.729815` |
| 18 | `q23_relation_label_precision` | `query_driven_graph` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.800364` |
| 19 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `6.246566` |
| 20 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.67706` |
| 21 | `q17_removal_precondition` | `symbolic_domain` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `15.348038` |
| 22 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `13.588994` |
| 23 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `8.899576` |
| 24 | `q26_unmodeled_torque` | `query_driven_graph` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `19.047987` |
| 25 | `q05_nested_prerequisite` | `steps_only` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.349247` |
| 26 | `q07_component_alignment` | `query_driven_graph` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.460151` |
| 27 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `7.204175` |
| 28 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_6` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.055577` |
| 29 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `20.770873` |
| 30 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.769276` |
| 31 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.802748` |
| 32 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `18.95989` |
| 33 | `q12_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_6` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.103351` |
| 34 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.738326` |
| 35 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.106955` |
| 36 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.803705` |
| 37 | `q25_video_confirmation` | `symbolic_domain` | `step_6` | `scenario_f_missing_evidence_controls` | `ok` | `5.82608` |
| 38 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.527616` |
| 39 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.513188` |
| 40 | `q17_removal_precondition` | `steps_only` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `6.473485` |
| 41 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.723686` |
| 42 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `20.164843` |
| 43 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `9.596668` |
| 44 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.506098` |
| 45 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_6` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.984655` |
| 46 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.275669` |
| 47 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_6` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.21416` |
| 48 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `5.189739` |
| 49 | `q05_nested_prerequisite` | `symbolic_domain` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.411994` |
| 50 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `6.981899` |
| 51 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `3.37608` |
| 52 | `q26_unmodeled_torque` | `symbolic_domain` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `4.646073` |
| 53 | `q15_unsupported_tool_proposal` | `steps_only` | `step_6` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.18124` |
| 54 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.643132` |
| 55 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `21.499859` |
| 56 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.86536` |
| 57 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.07879` |
| 58 | `q26_unmodeled_torque` | `steps_only` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `3.006437` |
| 59 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.099815` |
| 60 | `q12_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_6` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.44917` |
| 61 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `13.223543` |
| 62 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.461209` |
| 63 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.624295` |
| 64 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `11.674144` |
| 65 | `q25_video_confirmation` | `steps_only` | `step_6` | `scenario_f_missing_evidence_controls` | `ok` | `3.587434` |
| 66 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.685741` |
| 67 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `15.026944` |
| 68 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `7.037409` |
| 69 | `q05_nested_prerequisite` | `query_driven_graph` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `20.537888` |
| 70 | `q04_wrong_part_target_check` | `steps_only` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.082042` |
| 71 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `18.211727` |
| 72 | `q07_component_alignment` | `steps_only` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `6.445288` |
| 73 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.399638` |
| 74 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `6.656613` |
| 75 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.810733` |
| 76 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_6` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.233692` |
| 77 | `q23_relation_label_precision` | `symbolic_domain` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.696578` |
| 78 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.414994` |
| 79 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `9.228848` |
| 80 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.358954` |
| 81 | `q03_direct_installation_target` | `query_driven_graph` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `17.853517` |
| 82 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_15` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.697277` |
| 83 | `q03_direct_installation_target` | `steps_only` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.957666` |
| 84 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `21.701499` |
