# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-03T14:37:30+02:00`
Random seed: `20260703143730`
Clip name: `od_plus_error_hints_08_assy_0_1`

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

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q26_unmodeled_torque` | `query_driven_graph` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `22.828424` |
| 02 | `q12_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.519733` |
| 03 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `28.474821` |
| 04 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `23.783486` |
| 05 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `12.028493` |
| 06 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.828028` |
| 07 | `q25_video_confirmation` | `steps_only` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `3.625302` |
| 08 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.801739` |
| 09 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.116998` |
| 10 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `5.810422` |
| 11 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `30.468976` |
| 12 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `25.451619` |
| 13 | `q23_relation_label_precision` | `symbolic_domain` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `20.489505` |
| 14 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.820402` |
| 15 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.934558` |
| 16 | `q03_direct_installation_target` | `query_driven_graph` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `21.963653` |
| 17 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.683067` |
| 18 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.148302` |
| 19 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.067295` |
| 20 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.865723` |
| 21 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `29.915231` |
| 22 | `q17_removal_precondition` | `steps_only` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `9.132815` |
| 23 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `17.090691` |
| 24 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.150295` |
| 25 | `q05_nested_prerequisite` | `query_driven_graph` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `24.311013` |
| 26 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `24.325767` |
| 27 | `q07_component_alignment` | `query_driven_graph` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `23.408769` |
| 28 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `27.506006` |
| 29 | `q03_direct_installation_target` | `symbolic_domain` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.045872` |
| 30 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `29.851691` |
| 31 | `q23_relation_label_precision` | `query_driven_graph` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `23.505822` |
| 32 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.360396` |
| 33 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `23.012916` |
| 34 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.287966` |
| 35 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.698923` |
| 36 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `12.17944` |
| 37 | `q12_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `24.96891` |
| 38 | `q23_relation_label_precision` | `steps_only` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.876014` |
| 39 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `9.041646` |
| 40 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.121707` |
| 41 | `q16_combined_requirements` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.509757` |
| 42 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.512584` |
| 43 | `q26_unmodeled_torque` | `steps_only` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `2.971652` |
| 44 | `q05_nested_prerequisite` | `symbolic_domain` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.754679` |
| 45 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.401356` |
| 46 | `q15_unsupported_tool_proposal` | `steps_only` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.578224` |
| 47 | `q17_removal_precondition` | `query_driven_graph` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `26.912051` |
| 48 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.805702` |
| 49 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.061196` |
| 50 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.539215` |
| 51 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.79496` |
| 52 | `q07_component_alignment` | `symbolic_domain` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.243966` |
| 53 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `26.226127` |
| 54 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `21.840341` |
| 55 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `3.15046` |
| 56 | `q12_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.918739` |
| 57 | `q03_direct_installation_target` | `steps_only` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.667878` |
| 58 | `q25_video_confirmation` | `query_driven_graph` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `24.931302` |
| 59 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.943197` |
| 60 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.967067` |
| 61 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `4.739137` |
| 62 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.618131` |
| 63 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `23.274235` |
| 64 | `q17_removal_precondition` | `symbolic_domain` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `20.35301` |
| 65 | `q25_video_confirmation` | `symbolic_domain` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `21.284303` |
| 66 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `30.203126` |
| 67 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `26.132234` |
| 68 | `q04_wrong_part_target_check` | `steps_only` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.714174` |
| 69 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `14.901555` |
| 70 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `23.661657` |
| 71 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `26.030459` |
| 72 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.692273` |
| 73 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.509677` |
| 74 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.410589` |
| 75 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.803541` |
| 76 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `9.394859` |
| 77 | `q07_component_alignment` | `steps_only` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `11.008463` |
| 78 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.160122` |
| 79 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `37.358403` |
| 80 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `16.95627` |
| 81 | `q05_nested_prerequisite` | `steps_only` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.12537` |
| 82 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `18.958964` |
| 83 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.091099` |
| 84 | `q26_unmodeled_torque` | `symbolic_domain` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `19.721624` |
