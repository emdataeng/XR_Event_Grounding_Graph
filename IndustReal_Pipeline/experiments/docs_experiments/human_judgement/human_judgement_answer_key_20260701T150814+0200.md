# Human Judgement Answer Key

Generated at: `2026-07-01T15:08:14+02:00`
Random seed: `20260701144534`

This file maps blind response labels back to experiment conditions. Do not share this file with judges before scoring.

## Source Files

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_20260701T141538+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_20260701T141811+0200.jsonl`
- `graph_grounded`: `experiments\llm_guidance_ablation\outputs\responses_graph_grounded_20260701T142734+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_20260701T144534+0200.jsonl`

## Mapping

### Item 01

- Case ID: `q20_high_confidence_but_uncertain_validation`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Step index: `step_2`
- Question: The detection confidence is high, so why is this step still uncertain?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `steps_only` | `ok` | `5.046479` |
| B | `symbolic_domain` | `ok` | `20.848349` |
| C | `query_driven_graph` | `ok` | `29.168529` |
| D | `graph_grounded` | `ok` | `19.423927` |

### Item 02

- Case ID: `q18_removal_invalidates_installed_state`
- Scenario: `scenario_d_state_lifecycle_and_error_recovery`
- Step index: `step_9`
- Question: After this removal, should the front wheel assembly still count as installed on the front chassis?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `8.294492` |
| B | `graph_grounded` | `ok` | `5.092609` |
| C | `steps_only` | `ok` | `3.089256` |
| D | `query_driven_graph` | `ok` | `22.788655` |

### Item 03

- Case ID: `q27_unknown_step`
- Scenario: `scenario_f_missing_evidence_controls`
- Step index: `step_999`
- Question: I cannot find this step. What should I do next?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `12.2697` |
| B | `query_driven_graph` | `ok` | `8.698665` |
| C | `symbolic_domain` | `ok` | `22.995052` |
| D | `steps_only` | `ok` | `6.364312` |

### Item 04

- Case ID: `q16_combined_requirements`
- Scenario: `scenario_c_safety_and_tool_constraints`
- Step index: `step_2`
- Question: For the current step, list the required tool, assembly conditions, and safety checks. Which are supported and which are still missing?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `steps_only` | `ok` | `7.274414` |
| B | `graph_grounded` | `ok` | `19.383835` |
| C | `query_driven_graph` | `ok` | `29.336552` |
| D | `symbolic_domain` | `ok` | `21.1586` |

### Item 05

- Case ID: `q14_required_tool_versus_observed_tool_use`
- Scenario: `scenario_c_safety_and_tool_constraints`
- Step index: `step_7`
- Question: Which tool is required for this step, and is that requirement supported by evidence that the tool was actually used?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `12.968009` |
| B | `symbolic_domain` | `ok` | `18.241447` |
| C | `query_driven_graph` | `ok` | `19.739897` |
| D | `steps_only` | `ok` | `3.931786` |

### Item 06

- Case ID: `q02_sequence_control_named_part_mismatch`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Step index: `step_2`
- Question: I picked up the front chassis. Does that match the current step?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `21.129067` |
| B | `steps_only` | `ok` | `6.640946` |
| C | `query_driven_graph` | `ok` | `21.739297` |
| D | `graph_grounded` | `ok` | `23.70828` |

### Item 07

- Case ID: `q09_root_component_alignment_exception`
- Scenario: `scenario_b_troubleshooting_implicit_conditions`
- Step index: `step_0`
- Question: Does the model require the base to be aligned with the workspace before installation?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `steps_only` | `ok` | `5.156753` |
| B | `symbolic_domain` | `ok` | `19.522689` |
| C | `graph_grounded` | `ok` | `10.968105` |
| D | `query_driven_graph` | `ok` | `21.085175` |

### Item 08

- Case ID: `q12_rear_chassis_pin_safety_prerequisites`
- Scenario: `scenario_c_safety_and_tool_constraints`
- Step index: `step_5`
- Question: I am about to install the rear rear chassis pin. Which safety conditions must be verified first, and does the current evidence support them?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `26.389045` |
| B | `symbolic_domain` | `ok` | `21.66697` |
| C | `steps_only` | `ok` | `3.93867` |
| D | `graph_grounded` | `ok` | `16.191459` |

### Item 09

- Case ID: `q19_reinstallation_guidance_after_removal`
- Scenario: `scenario_d_state_lifecycle_and_error_recovery`
- Step index: `step_9`
- Question: After removing the front wheel assembly, what exact new evidence would be needed before a later step can rely on it again?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `22.766535` |
| B | `graph_grounded` | `ok` | `14.940581` |
| C | `symbolic_domain` | `ok` | `17.750567` |
| D | `steps_only` | `ok` | `4.949155` |

### Item 10

- Case ID: `q11_front_chassis_pin_safety_prerequisites`
- Scenario: `scenario_c_safety_and_tool_constraints`
- Step index: `step_2`
- Question: Before I install this pin, which assemblies must already be secured, and what evidence says whether those safety conditions are satisfied?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `32.883839` |
| B | `steps_only` | `ok` | `7.550017` |
| C | `graph_grounded` | `ok` | `23.750671` |
| D | `symbolic_domain` | `ok` | `22.178523` |

### Item 11

- Case ID: `q17_removal_precondition`
- Scenario: `scenario_d_state_lifecycle_and_error_recovery`
- Step index: `step_9`
- Question: What condition must already be true before this wheel assembly can be removed, and which earlier step supports it?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `19.27851` |
| B | `graph_grounded` | `ok` | `11.018542` |
| C | `query_driven_graph` | `ok` | `23.014905` |
| D | `steps_only` | `ok` | `5.546591` |

### Item 12

- Case ID: `q04_wrong_part_target_check`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Step index: `step_5`
- Question: Can I use the rear chassis pin for the front bracket?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `19.161105` |
| B | `query_driven_graph` | `ok` | `23.264789` |
| C | `graph_grounded` | `ok` | `19.108265` |
| D | `steps_only` | `ok` | `6.445532` |

### Item 13

- Case ID: `q28_ambiguous_okay_question`
- Scenario: `scenario_f_missing_evidence_controls`
- Step index: `step_1`
- Question: Is this okay?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `7.896951` |
| B | `query_driven_graph` | `ok` | `26.384664` |
| C | `steps_only` | `ok` | `9.612705` |
| D | `symbolic_domain` | `ok` | `26.066062` |

### Item 14

- Case ID: `q06_front_rear_chassis_pin_readiness`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Step index: `step_2`
- Question: I have the front rear chassis pin ready. Can I install it now, or is anything still missing?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `17.502608` |
| B | `query_driven_graph` | `ok` | `26.790921` |
| C | `steps_only` | `ok` | `6.001869` |
| D | `symbolic_domain` | `ok` | `18.618974` |

### Item 15

- Case ID: `q01_sequence_control_current_and_next_action`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Step index: `step_1`
- Question: I have reached this step. What component should I work on now, and what action should I take?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `20.746448` |
| B | `query_driven_graph` | `ok` | `23.80459` |
| C | `steps_only` | `ok` | `7.549018` |
| D | `graph_grounded` | `ok` | `14.677976` |

### Item 16

- Case ID: `q25_video_confirmation`
- Scenario: `scenario_f_missing_evidence_controls`
- Step index: `step_4`
- Question: Can you confirm from the video that the pin is physically aligned?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `23.40335` |
| B | `steps_only` | `ok` | `3.623576` |
| C | `graph_grounded` | `ok` | `16.857086` |
| D | `query_driven_graph` | `ok` | `21.78065` |

### Item 17

- Case ID: `q03_direct_installation_target`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Step index: `step_6`
- Question: Which component is the front bracket supposed to be installed onto?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `22.942304` |
| B | `symbolic_domain` | `ok` | `15.997244` |
| C | `steps_only` | `ok` | `5.626696` |
| D | `graph_grounded` | `ok` | `13.447001` |

### Item 18

- Case ID: `q15_unsupported_tool_proposal`
- Scenario: `scenario_c_safety_and_tool_constraints`
- Step index: `step_4`
- Question: Should I use the screwdriver for this pin because it was required for the screw step?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `20.625006` |
| B | `steps_only` | `ok` | `4.207692` |
| C | `graph_grounded` | `ok` | `21.551332` |
| D | `symbolic_domain` | `ok` | `21.237989` |

### Item 19

- Case ID: `q24_multiple_missing_requirements`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Step index: `step_2`
- Question: I want to move on to the next step. What required conditions are still unresolved or missing?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `steps_only` | `ok` | `5.756523` |
| B | `graph_grounded` | `ok` | `18.160947` |
| C | `symbolic_domain` | `ok` | `22.055878` |
| D | `query_driven_graph` | `ok` | `27.717816` |

### Item 20

- Case ID: `q23_relation_label_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Step index: `step_7`
- Question: What is the screw installed onto? What tool does the screw require? What component supports the bracket?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `8.420409` |
| B | `steps_only` | `ok` | `5.588308` |
| C | `symbolic_domain` | `ok` | `18.479873` |
| D | `query_driven_graph` | `ok` | `22.32228` |

### Item 21

- Case ID: `q13_securing_is_not_installation`
- Scenario: `scenario_c_safety_and_tool_constraints`
- Step index: `step_2`
- Question: The rear chassis was installed earlier. Is that enough evidence that it was secured to the base?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `27.064794` |
| B | `query_driven_graph` | `ok` | `26.436973` |
| C | `steps_only` | `ok` | `5.569136` |
| D | `graph_grounded` | `ok` | `19.044194` |

### Item 22

- Case ID: `q08_front_bracket_screw_troubleshooting`
- Scenario: `scenario_b_troubleshooting_implicit_conditions`
- Step index: `step_7`
- Question: The front bracket screw is not going into the bracket correctly. What modeled condition should I check before using more force?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `8.375098` |
| B | `symbolic_domain` | `ok` | `20.111976` |
| C | `steps_only` | `ok` | `4.659985` |
| D | `query_driven_graph` | `ok` | `22.327804` |

### Item 23

- Case ID: `q26_unmodeled_torque`
- Scenario: `scenario_f_missing_evidence_controls`
- Step index: `step_7`
- Question: What torque should I use for the front bracket screw?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `20.01689` |
| B | `symbolic_domain` | `ok` | `15.979564` |
| C | `steps_only` | `ok` | `3.129475` |
| D | `graph_grounded` | `ok` | `15.034993` |

### Item 24

- Case ID: `q21_why_accepted`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Step index: `step_1`
- Question: Why is it okay to proceed with this step? What earlier completed action satisfies the requirement for this step?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `graph_grounded` | `ok` | `15.390144` |
| B | `query_driven_graph` | `ok` | `19.847823` |
| C | `steps_only` | `ok` | `3.454097` |
| D | `symbolic_domain` | `ok` | `19.686388` |

### Item 25

- Case ID: `q10_alignment_requirement_versus_satisfaction`
- Scenario: `scenario_b_troubleshooting_implicit_conditions`
- Step index: `step_4`
- Question: I know the pin needs to be aligned with the front chassis. Does the evidence show that this alignment has already been done?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `19.082048` |
| B | `steps_only` | `ok` | `5.441279` |
| C | `graph_grounded` | `ok` | `14.330787` |
| D | `query_driven_graph` | `ok` | `20.654575` |

### Item 26

- Case ID: `q07_component_alignment`
- Scenario: `scenario_b_troubleshooting_implicit_conditions`
- Step index: `step_8`
- Question: What must be aligned before I install the front wheel assembly, and what should it be aligned with?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `symbolic_domain` | `ok` | `18.596033` |
| B | `graph_grounded` | `ok` | `12.814545` |
| C | `steps_only` | `ok` | `6.779294` |
| D | `query_driven_graph` | `ok` | `20.733558` |

### Item 27

- Case ID: `q05_nested_prerequisite`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Step index: `step_7`
- Question: Before installing this screw, which component must already be installed, and what supports that component?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `20.40027` |
| B | `steps_only` | `ok` | `5.954463` |
| C | `graph_grounded` | `ok` | `13.062887` |
| D | `symbolic_domain` | `ok` | `15.691024` |

### Item 28

- Case ID: `q22_provenance_of_an_inferred_requirement`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Step index: `step_6`
- Question: Where did this requirement come from: the source event, the domain model, or an inference rule?

| Blind label | Experiment condition | Source response status | Duration seconds |
|---|---|---|---:|
| A | `query_driven_graph` | `ok` | `26.060446` |
| B | `symbolic_domain` | `ok` | `27.278671` |
| C | `steps_only` | `ok` | `3.874416` |
| D | `graph_grounded` | `ok` | `14.822206` |
