# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-01T16:40:15+02:00`
Random seed: `20260701150814`
Clip name: `03_assy_0_1`

Do not share this file with judges before scoring.

## Source Files

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_20260701T141538+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_20260701T141811+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_20260701T144534+0200.jsonl`

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q08_front_bracket_screw_troubleshooting` | `query_driven_graph` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `22.327804` |
| 02 | `q03_direct_installation_target` | `symbolic_domain` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.997244` |
| 03 | `q02_sequence_control_named_part_mismatch` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `21.739297` |
| 04 | `q17_removal_precondition` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `23.014905` |
| 05 | `q17_removal_precondition` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `5.546591` |
| 06 | `q18_removal_invalidates_installed_state` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `3.089256` |
| 07 | `q28_ambiguous_okay_question` | `steps_only` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `9.612705` |
| 08 | `q20_high_confidence_but_uncertain_validation` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `20.848349` |
| 09 | `q13_securing_is_not_installation` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `27.064794` |
| 10 | `q17_removal_precondition` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `19.27851` |
| 11 | `q01_sequence_control_current_and_next_action` | `steps_only` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `7.549018` |
| 12 | `q12_rear_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_5` | `scenario_c_safety_and_tool_constraints` | `ok` | `26.389045` |
| 13 | `q23_relation_label_precision` | `symbolic_domain` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `18.479873` |
| 14 | `q16_combined_requirements` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `29.336552` |
| 15 | `q12_rear_chassis_pin_safety_prerequisites` | `steps_only` | `step_5` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.93867` |
| 16 | `q14_required_tool_versus_observed_tool_use` | `query_driven_graph` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `19.739897` |
| 17 | `q08_front_bracket_screw_troubleshooting` | `steps_only` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.659985` |
| 18 | `q06_front_rear_chassis_pin_readiness` | `query_driven_graph` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `26.790921` |
| 19 | `q10_alignment_requirement_versus_satisfaction` | `steps_only` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `5.441279` |
| 20 | `q10_alignment_requirement_versus_satisfaction` | `query_driven_graph` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.654575` |
| 21 | `q18_removal_invalidates_installed_state` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `8.294492` |
| 22 | `q14_required_tool_versus_observed_tool_use` | `symbolic_domain` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `18.241447` |
| 23 | `q18_removal_invalidates_installed_state` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `22.788655` |
| 24 | `q14_required_tool_versus_observed_tool_use` | `steps_only` | `step_7` | `scenario_c_safety_and_tool_constraints` | `ok` | `3.931786` |
| 25 | `q15_unsupported_tool_proposal` | `steps_only` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.207692` |
| 26 | `q22_provenance_of_an_inferred_requirement` | `steps_only` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.874416` |
| 27 | `q05_nested_prerequisite` | `symbolic_domain` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.691024` |
| 28 | `q25_video_confirmation` | `steps_only` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `3.623576` |
| 29 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `6.364312` |
| 30 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.686388` |
| 31 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `22.995052` |
| 32 | `q07_component_alignment` | `query_driven_graph` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.733558` |
| 33 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.522689` |
| 34 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `17.750567` |
| 35 | `q28_ambiguous_okay_question` | `query_driven_graph` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `26.384664` |
| 36 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `19.847823` |
| 37 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `21.085175` |
| 38 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.454097` |
| 39 | `q16_combined_requirements` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.1586` |
| 40 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `5.156753` |
| 41 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `20.625006` |
| 42 | `q02_sequence_control_named_part_mismatch` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.640946` |
| 43 | `q24_multiple_missing_requirements` | `symbolic_domain` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.055878` |
| 44 | `q07_component_alignment` | `symbolic_domain` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `18.596033` |
| 45 | `q26_unmodeled_torque` | `steps_only` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `3.129475` |
| 46 | `q26_unmodeled_torque` | `symbolic_domain` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `15.979564` |
| 47 | `q13_securing_is_not_installation` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `5.569136` |
| 48 | `q04_wrong_part_target_check` | `query_driven_graph` | `step_5` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.264789` |
| 49 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.237989` |
| 50 | `q22_provenance_of_an_inferred_requirement` | `symbolic_domain` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `27.278671` |
| 51 | `q23_relation_label_precision` | `query_driven_graph` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `22.32228` |
| 52 | `q08_front_bracket_screw_troubleshooting` | `symbolic_domain` | `step_7` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `20.111976` |
| 53 | `q01_sequence_control_current_and_next_action` | `query_driven_graph` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `23.80459` |
| 54 | `q11_front_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `22.178523` |
| 55 | `q23_relation_label_precision` | `steps_only` | `step_7` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.588308` |
| 56 | `q25_video_confirmation` | `symbolic_domain` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `23.40335` |
| 57 | `q02_sequence_control_named_part_mismatch` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `21.129067` |
| 58 | `q01_sequence_control_current_and_next_action` | `symbolic_domain` | `step_1` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `20.746448` |
| 59 | `q16_combined_requirements` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `7.274414` |
| 60 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `22.766535` |
| 61 | `q26_unmodeled_torque` | `query_driven_graph` | `step_7` | `scenario_f_missing_evidence_controls` | `ok` | `20.01689` |
| 62 | `q04_wrong_part_target_check` | `steps_only` | `step_5` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.445532` |
| 63 | `q03_direct_installation_target` | `query_driven_graph` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `22.942304` |
| 64 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.949155` |
| 65 | `q07_component_alignment` | `steps_only` | `step_8` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `6.779294` |
| 66 | `q11_front_chassis_pin_safety_prerequisites` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `32.883839` |
| 67 | `q20_high_confidence_but_uncertain_validation` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `29.168529` |
| 68 | `q20_high_confidence_but_uncertain_validation` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.046479` |
| 69 | `q28_ambiguous_okay_question` | `symbolic_domain` | `step_1` | `scenario_f_missing_evidence_controls` | `ok` | `26.066062` |
| 70 | `q13_securing_is_not_installation` | `query_driven_graph` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `26.436973` |
| 71 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `8.698665` |
| 72 | `q12_rear_chassis_pin_safety_prerequisites` | `symbolic_domain` | `step_5` | `scenario_c_safety_and_tool_constraints` | `ok` | `21.66697` |
| 73 | `q10_alignment_requirement_versus_satisfaction` | `symbolic_domain` | `step_4` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `19.082048` |
| 74 | `q24_multiple_missing_requirements` | `steps_only` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `5.756523` |
| 75 | `q06_front_rear_chassis_pin_readiness` | `symbolic_domain` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.618974` |
| 76 | `q03_direct_installation_target` | `steps_only` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.626696` |
| 77 | `q04_wrong_part_target_check` | `symbolic_domain` | `step_5` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.161105` |
| 78 | `q05_nested_prerequisite` | `steps_only` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `5.954463` |
| 79 | `q05_nested_prerequisite` | `query_driven_graph` | `step_7` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `20.40027` |
| 80 | `q24_multiple_missing_requirements` | `query_driven_graph` | `step_2` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `27.717816` |
| 81 | `q11_front_chassis_pin_safety_prerequisites` | `steps_only` | `step_2` | `scenario_c_safety_and_tool_constraints` | `ok` | `7.550017` |
| 82 | `q25_video_confirmation` | `query_driven_graph` | `step_4` | `scenario_f_missing_evidence_controls` | `ok` | `21.78065` |
| 83 | `q22_provenance_of_an_inferred_requirement` | `query_driven_graph` | `step_6` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `26.060446` |
| 84 | `q06_front_rear_chassis_pin_readiness` | `steps_only` | `step_2` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.001869` |
