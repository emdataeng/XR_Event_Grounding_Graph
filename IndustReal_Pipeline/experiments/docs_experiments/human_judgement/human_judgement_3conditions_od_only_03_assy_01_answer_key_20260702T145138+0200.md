# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-02T14:51:38+02:00`
Random seed: `20260702135724`
Clip name: `03_assy_0_1`

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

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_20260702T133617+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_20260702T133758+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_20260702T135724+0200.jsonl`

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q04_wrong_part_target_check` | `steps_only` | `step_5` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `4.157492` |
| 02 | `q25_video_confirmation` | `symbolic_domain` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `6.070201` |
| 03 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.231241` |
| 04 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.504217` |
| 05 | `q03_direct_installation_target` | `steps_only` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `4.404126` |
| 06 | `q05_nested_prerequisite` | `steps_only` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `4.686673` |
| 07 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `16.129486` |
| 08 | `q17_removal_precondition` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `20.255841` |
| 09 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.397175` |
| 10 | `q26_unmodeled_torque` | `symbolic_domain` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `3.151976` |
| 11 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.222264` |
| 12 | `q25_video_confirmation` | `steps_only` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `2.86006` |
| 13 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.0309` |
| 14 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `12.038814` |
| 15 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `6.570708` |
| 16 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.308949` |
| 17 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.713583` |
| 18 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `13.09839` |
| 19 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `7.231275` |
| 20 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.754596` |
| 21 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `15.105146` |
| 22 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.726032` |
| 23 | `q23_relation_label_precision` | `query_driven_graph` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.690734` |
| 24 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `17.550843` |
| 25 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.829766` |
| 26 | `q03_direct_installation_target` | `symbolic_domain` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `11.861103` |
| 27 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `8.827565` |
| 28 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `8.417265` |
| 29 | `q12_rear_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_5` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.0111` |
| 30 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.097886` |
| 31 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.415793` |
| 32 | `q15_unsupported_tool_proposal` | `steps_only` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `2.956146` |
| 33 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `8.613783` |
| 34 | `q05_nested_prerequisite` | `symbolic_domain` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `12.320487` |
| 35 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.714377` |
| 36 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.394082` |
| 37 | `q12_rear_chassis_pin_safety_prerequisites` | `steps_only` | `step_5` | `scenario_c_safety_and_tool_constraints` | `ok` | `2.704531` |
| 38 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `8.35189` |
| 39 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `5.335939` |
| 40 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.120136` |
| 41 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.595347` |
| 42 | `q26_unmodeled_torque` | `steps_only` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `2.588354` |
| 43 | `q12_rear_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_5` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.962359` |
| 44 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.530445` |
| 45 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.865477` |
| 46 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `14.695836` |
| 47 | `q07_component_alignment` | `symbolic_domain` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.444139` |
| 48 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `6.797026` |
| 49 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `13.266968` |
| 50 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.833671` |
| 51 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `17.498036` |
| 52 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `15.98098` |
| 53 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `4.492433` |
| 54 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.895425` |
| 55 | `q26_unmodeled_torque` | `query_driven_graph` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `14.806508` |
| 56 | `q17_removal_precondition` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `13.31688` |
| 57 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `16.435917` |
| 58 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `11.004903` |
| 59 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `1.750724` |
| 60 | `q07_component_alignment` | `steps_only` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.332071` |
| 61 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `8.85994` |
| 62 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.515323` |
| 63 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `4.570047` |
| 64 | `q07_component_alignment` | `query_driven_graph` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `14.834733` |
| 65 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `3.268396` |
| 66 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `2.882212` |
| 67 | `q16_combined_requirements` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.420449` |
| 68 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.771975` |
| 69 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `7.208539` |
| 70 | `q23_relation_label_precision` | `steps_only` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.976365` |
| 71 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.705634` |
| 72 | `q05_nested_prerequisite` | `query_driven_graph` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.433242` |
| 73 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.614715` |
| 74 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `2.810537` |
| 75 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_5` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `17.444332` |
| 76 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `9.499733` |
| 77 | `q23_relation_label_precision` | `symbolic_domain` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.673211` |
| 78 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `5.173417` |
| 79 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `15.6751` |
| 80 | `q25_video_confirmation` | `query_driven_graph` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `15.686124` |
| 81 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_5` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `13.539108` |
| 82 | `q03_direct_installation_target` | `query_driven_graph` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.233732` |
| 83 | `q17_removal_precondition` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.981563` |
| 84 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `13.679193` |
