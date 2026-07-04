# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-04T13:13:03+02:00`
Random seed: `20260703151334`
Clip name: `od_plus_error_hints_08_assy_0_1`
Question set path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v4_od_plus_psr_error_hints_test_p1_08_assy_0_1.yaml`

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

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_od_plus_error_hints_08_assy_0_1_20260703T140405+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_od_plus_error_hints_08_assy_0_1_20260703T140639+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_od_plus_error_hints_08_assy_0_1_20260703T142119+0200.jsonl`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v4_od_plus_psr_error_hints_test_p1_08_assy_0_1.yaml`
- ID: `novice_questions_od_plus_psr_error_hints_test_p1_08_assy_0_1`
- Version: `v4`
- Case count: `28`
- SHA-256: `a4abb6f6d93c13e99eaeeb587aed45b9dffa2bb3b185edb52284f774df17d80c`

## Item Mapping

| Item | Case ID | Condition | Step | Step time window | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---|---:|
| 01 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `25.451619` |
| 02 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_f_missing_evidence_controls` | `ok` | `4.739137` |
| 03 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `23.783486` |
| 04 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.360396` |
| 05 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `21.840341` |
| 06 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.150295` |
| 07 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.943197` |
| 08 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.865723` |
| 09 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `29.915231` |
| 10 | `q23_relation_label_precision` | `symbolic_domain` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `20.489505` |
| 11 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `5.810422` |
| 12 | `q25_video_confirmation` | `query_driven_graph` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `24.931302` |
| 13 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.121707` |
| 14 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `9.394859` |
| 15 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.401356` |
| 16 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.828028` |
| 17 | `q05_nested_prerequisite` | `query_driven_graph` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `24.311013` |
| 18 | `q26_unmodeled_torque` | `query_driven_graph` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `22.828424` |
| 19 | `q17_removal_precondition` | `symbolic_domain` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `20.35301` |
| 20 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `29.851691` |
| 21 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_10` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.061196` |
| 22 | `q21_why_accepted` | `steps_only` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.091099` |
| 23 | `q12_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.519733` |
| 24 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.692273` |
| 25 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.116998` |
| 26 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.803541` |
| 27 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_10` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `37.358403` |
| 28 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `26.030459` |
| 29 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.067295` |
| 30 | `q25_video_confirmation` | `steps_only` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `3.625302` |
| 31 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.79496` |
| 32 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.801739` |
| 33 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.934558` |
| 34 | `q26_unmodeled_torque` | `symbolic_domain` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `19.721624` |
| 35 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.901555` |
| 36 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `24.325767` |
| 37 | `q07_component_alignment` | `symbolic_domain` | `step_12` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.243966` |
| 38 | `q17_removal_precondition` | `query_driven_graph` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `26.912051` |
| 39 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_10` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.618131` |
| 40 | `q03_direct_installation_target` | `query_driven_graph` | `step_10` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `21.963653` |
| 41 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `12.17944` |
| 42 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `` | `scenario_f_missing_evidence_controls` | `ok` | `12.028493` |
| 43 | `q04_wrong_part_target_check` | `steps_only` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.714174` |
| 44 | `q17_removal_precondition` | `steps_only` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `9.132815` |
| 45 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.410589` |
| 46 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.287966` |
| 47 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_20` | `3 min 37.2 s - 4 min 7.4 s` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.805702` |
| 48 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `27.506006` |
| 49 | `q23_relation_label_precision` | `steps_only` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.876014` |
| 50 | `q05_nested_prerequisite` | `symbolic_domain` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.754679` |
| 51 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.683067` |
| 52 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.148302` |
| 53 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.820402` |
| 54 | `q16_combined_requirements` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.509757` |
| 55 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.509677` |
| 56 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.967067` |
| 57 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `23.012916` |
| 58 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_f_missing_evidence_controls` | `ok` | `3.15046` |
| 59 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `26.132234` |
| 60 | `q26_unmodeled_torque` | `steps_only` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `2.971652` |
| 61 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `16.95627` |
| 62 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.698923` |
| 63 | `q05_nested_prerequisite` | `steps_only` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.12537` |
| 64 | `q23_relation_label_precision` | `query_driven_graph` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `23.505822` |
| 65 | `q07_component_alignment` | `steps_only` | `step_12` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `11.008463` |
| 66 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `23.274235` |
| 67 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `30.468976` |
| 68 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.539215` |
| 69 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `` | `scenario_f_missing_evidence_controls` | `ok` | `17.090691` |
| 70 | `q03_direct_installation_target` | `steps_only` | `step_10` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.667878` |
| 71 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `28.474821` |
| 72 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_f_missing_evidence_controls` | `ok` | `26.226127` |
| 73 | `q12_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `24.96891` |
| 74 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.160122` |
| 75 | `q25_video_confirmation` | `symbolic_domain` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `21.284303` |
| 76 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `18.958964` |
| 77 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `30.203126` |
| 78 | `q15_unsupported_tool_proposal` | `steps_only` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.578224` |
| 79 | `q12_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_7` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.918739` |
| 80 | `q07_component_alignment` | `query_driven_graph` | `step_12` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `23.408769` |
| 81 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `1 min 1.8 s - 2 min 10.9 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.512584` |
| 82 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_11` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_c_safety_and_tool_constraints` | `ok` | `23.661657` |
| 83 | `q27_unknown_step` | `steps_only` | `step_999` | `` | `scenario_f_missing_evidence_controls` | `ok` | `9.041646` |
| 84 | `q03_direct_installation_target` | `symbolic_domain` | `step_10` | `2 min 15.6 s - 2 min 34.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.045872` |
