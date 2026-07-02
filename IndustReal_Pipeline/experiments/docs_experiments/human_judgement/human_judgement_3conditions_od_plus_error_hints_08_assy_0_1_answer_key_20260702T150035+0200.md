# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-02T15:00:35+02:00`
Random seed: `20260702144626`
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

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_od_plus_error_hints_08_assy_0_1_20260702T143120+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_od_plus_error_hints_08_assy_0_1_20260702T143350+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_od_plus_error_hints_08_assy_0_1_20260702T144626+0200.jsonl`

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q03_direct_installation_target` | `query_driven_graph` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.150958` |
| 02 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `18.825635` |
| 03 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.964333` |
| 04 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.635944` |
| 05 | `q16_combined_requirements` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.522422` |
| 06 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.295974` |
| 07 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `8.310256` |
| 08 | `q23_relation_label_precision` | `symbolic_domain` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `17.390226` |
| 09 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `21.509959` |
| 10 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.499983` |
| 11 | `q17_removal_precondition` | `query_driven_graph` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `23.413834` |
| 12 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `28.361856` |
| 13 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `9.539656` |
| 14 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.635762` |
| 15 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.160543` |
| 16 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `24.16617` |
| 17 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `17.241167` |
| 18 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.866774` |
| 19 | `q04_wrong_part_target_check` | `steps_only` | `step_3` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `11.243536` |
| 20 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `8.006753` |
| 21 | `q23_relation_label_precision` | `steps_only` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.999438` |
| 22 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.003041` |
| 23 | `q07_component_alignment` | `symbolic_domain` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `12.586298` |
| 24 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.603754` |
| 25 | `q15_unsupported_tool_proposal` | `steps_only` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.157566` |
| 26 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `16.368283` |
| 27 | `q26_unmodeled_torque` | `symbolic_domain` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `2.547136` |
| 28 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `18.617982` |
| 29 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.446803` |
| 30 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `2.991102` |
| 31 | `q12_rear_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_3` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.322242` |
| 32 | `q17_removal_precondition` | `steps_only` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `9.406035` |
| 33 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.202914` |
| 34 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.788788` |
| 35 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `7.129384` |
| 36 | `q25_video_confirmation` | `symbolic_domain` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `5.009772` |
| 37 | `q12_rear_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_3` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.002249` |
| 38 | `q03_direct_installation_target` | `steps_only` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.047685` |
| 39 | `q05_nested_prerequisite` | `symbolic_domain` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `13.016847` |
| 40 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.512252` |
| 41 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `13.770173` |
| 42 | `q12_rear_chassis_pin_safety_prerequisites` | `steps_only` | `step_3` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.549137` |
| 43 | `q17_removal_precondition` | `symbolic_domain` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `18.172073` |
| 44 | `q23_relation_label_precision` | `query_driven_graph` | `step_11` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `21.240759` |
| 45 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `24.774999` |
| 46 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_11` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.462668` |
| 47 | `q26_unmodeled_torque` | `query_driven_graph` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `19.484618` |
| 48 | `q25_video_confirmation` | `steps_only` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `3.412183` |
| 49 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.883817` |
| 50 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.452434` |
| 51 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_11` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `3.766328` |
| 52 | `q07_component_alignment` | `steps_only` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `7.802515` |
| 53 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `22.280473` |
| 54 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.362248` |
| 55 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_3` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `20.769673` |
| 56 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.446715` |
| 57 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.446691` |
| 58 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_3` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.422302` |
| 59 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.125243` |
| 60 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.754556` |
| 61 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `8.395141` |
| 62 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.785513` |
| 63 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.084947` |
| 64 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.139979` |
| 65 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.504138` |
| 66 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_20` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.870167` |
| 67 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.465994` |
| 68 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `25.268329` |
| 69 | `q05_nested_prerequisite` | `steps_only` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `8.231943` |
| 70 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `23.538913` |
| 71 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.123067` |
| 72 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `8.483516` |
| 73 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `2.933764` |
| 74 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `16.92532` |
| 75 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `23.44924` |
| 76 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `8.772145` |
| 77 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.760529` |
| 78 | `q26_unmodeled_torque` | `steps_only` | `step_11` | `scenario_f_missing_evidence_controls` | `ok` | `2.759758` |
| 79 | `q03_direct_installation_target` | `symbolic_domain` | `step_10` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `12.506615` |
| 80 | `q07_component_alignment` | `query_driven_graph` | `step_12` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `17.974124` |
| 81 | `q05_nested_prerequisite` | `query_driven_graph` | `step_11` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.717165` |
| 82 | `q25_video_confirmation` | `query_driven_graph` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `19.502208` |
| 83 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `11.256615` |
| 84 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_10` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `20.230019` |
