# Human Judgement Answer Key - 3 Conditions

Generated at: `2026-07-04T14:25:59+02:00`
Random seed: `20260704140928`
Clip name: `dataset_pilot_rod_assembly`
Question set path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v1_pilot_rod_assembly.yaml`

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

- `steps_only`: `Pilot\Experiments\llm_guidance_ablation\responses_steps_only_dataset_pilot_rod_assembly_20260704T135904+0200.jsonl`
- `symbolic_domain`: `Pilot\Experiments\llm_guidance_ablation\responses_symbolic_domain_dataset_pilot_rod_assembly_20260704T140041+0200.jsonl`
- `query_driven_graph`: `Pilot\Experiments\query_driven_graph\responses_query_driven_graph_dataset_pilot_rod_assembly_20260704T140928+0200.jsonl`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v1_pilot_rod_assembly.yaml`
- ID: `novice_questions_pilot_rod_assembly`
- Version: `v1`
- Case count: `31`
- SHA-256: `60a2ed6fae1de314ee9c3721e971a77c0a2de66be43ea1231ab2d294c1ea5bbf`

## Item Mapping

| Item | Case ID | Condition | Step | Step time window | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---|---:|
| 01 | `q15_sleeve_count_and_orientation` | `symbolic_domain` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `4.464785` |
| 02 | `q18_no_removal_action` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `4.466216` |
| 03 | `q27_unknown_step` | `steps_only` | `step_99` | `N/A` | `scenario_f_missing_evidence_controls` | `ok` | `3.519329` |
| 04 | `q17_grease_application` | `query_driven_graph` | `step_08` | `9 min 26.0 s - 10 min 42.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `18.885316` |
| 05 | `q24_relation_precision_targets` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.63067` |
| 06 | `q27_unknown_step` | `symbolic_domain` | `step_99` | `N/A` | `scenario_f_missing_evidence_controls` | `ok` | `7.491591` |
| 07 | `q12_power_screwdriver_step_four` | `steps_only` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.021485` |
| 08 | `q29_direct_video_confirmation` | `steps_only` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `2.803457` |
| 09 | `q23_expert_annotation_provenance` | `steps_only` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.945462` |
| 10 | `q16_cleaning_materials` | `symbolic_domain` | `step_07` | `8 min 51.0 s - 9 min 26.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.336003` |
| 11 | `q06_next_step_after_cleaning` | `steps_only` | `step_07` | `8 min 51.0 s - 9 min 26.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.940486` |
| 12 | `q11_rod_holes_belong_to_rod` | `symbolic_domain` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `2.652837` |
| 13 | `q24_relation_precision_targets` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.620781` |
| 14 | `q14_threadlocker_material` | `query_driven_graph` | `step_05` | `6 min 16.0 s - 7 min 9.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `17.101253` |
| 15 | `q11_rod_holes_belong_to_rod` | `query_driven_graph` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `16.601524` |
| 16 | `q06_next_step_after_cleaning` | `query_driven_graph` | `step_07` | `8 min 51.0 s - 9 min 26.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.434859` |
| 17 | `q08_sleeve_alignment_requirement` | `symbolic_domain` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `2.733023` |
| 18 | `q03_step_three_dependency` | `query_driven_graph` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.115617` |
| 19 | `q17_grease_application` | `symbolic_domain` | `step_08` | `9 min 26.0 s - 10 min 42.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `8.847923` |
| 20 | `q30_exact_instance_count` | `symbolic_domain` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `4.217758` |
| 21 | `q04_step_four_readiness` | `symbolic_domain` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `10.744168` |
| 22 | `q09_screw_alignment_before_tightening` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `10.233541` |
| 23 | `q20_historical_effects_after_uncertain_step` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `5.317808` |
| 24 | `q29_direct_video_confirmation` | `query_driven_graph` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `5.31511` |
| 25 | `q21_what_to_add_for_rework` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `3.891552` |
| 26 | `q23_expert_annotation_provenance` | `symbolic_domain` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.677543` |
| 27 | `q09_screw_alignment_before_tightening` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `18.80482` |
| 28 | `q01_start_sequence_current_action` | `steps_only` | `step_01` | `0 min 0.0 s - 0 min 15.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.399656` |
| 29 | `q15_sleeve_count_and_orientation` | `steps_only` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.012979` |
| 30 | `q27_unknown_step` | `query_driven_graph` | `step_99` | `N/A` | `scenario_f_missing_evidence_controls` | `ok` | `5.322305` |
| 31 | `q29_direct_video_confirmation` | `symbolic_domain` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `4.792989` |
| 32 | `q07_o_ring_alignment_requirement` | `query_driven_graph` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `18.191237` |
| 33 | `q17_grease_application` | `steps_only` | `step_08` | `9 min 26.0 s - 10 min 42.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `2.715928` |
| 34 | `q12_power_screwdriver_step_four` | `query_driven_graph` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `2.856759` |
| 35 | `q01_start_sequence_current_action` | `symbolic_domain` | `step_01` | `0 min 0.0 s - 0 min 15.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.460235` |
| 36 | `q05_threadlocker_dependency` | `query_driven_graph` | `step_05` | `6 min 16.0 s - 7 min 9.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `17.162003` |
| 37 | `q19_redo_o_ring_step` | `steps_only` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `2.962526` |
| 38 | `q08_sleeve_alignment_requirement` | `steps_only` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `2.739485` |
| 39 | `q13_power_screwdriver_step_six` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.321163` |
| 40 | `q21_what_to_add_for_rework` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `3.268196` |
| 41 | `q02_step_two_readiness` | `query_driven_graph` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `18.381622` |
| 42 | `q28_unmodeled_torque` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `3.697259` |
| 43 | `q28_unmodeled_torque` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `3.156147` |
| 44 | `q02_step_two_readiness` | `symbolic_domain` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `10.05248` |
| 45 | `q30_exact_instance_count` | `query_driven_graph` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `4.611308` |
| 46 | `q10_requirement_not_observation` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `2.952425` |
| 47 | `q10_requirement_not_observation` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `3.195816` |
| 48 | `q12_power_screwdriver_step_four` | `symbolic_domain` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `2.370406` |
| 49 | `q20_historical_effects_after_uncertain_step` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `3.294316` |
| 50 | `q16_cleaning_materials` | `query_driven_graph` | `step_07` | `8 min 51.0 s - 9 min 26.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `16.914112` |
| 51 | `q11_rod_holes_belong_to_rod` | `steps_only` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `2.667819` |
| 52 | `q01_start_sequence_current_action` | `query_driven_graph` | `step_01` | `0 min 0.0 s - 0 min 15.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `19.67246` |
| 53 | `q05_threadlocker_dependency` | `symbolic_domain` | `step_05` | `6 min 16.0 s - 7 min 9.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `10.187721` |
| 54 | `q25_why_step_three_accepted` | `steps_only` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.536319` |
| 55 | `q22_why_step_six_uncertain` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `20.818184` |
| 56 | `q31_ambiguous_okay_question` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `6.255476` |
| 57 | `q16_cleaning_materials` | `steps_only` | `step_07` | `8 min 51.0 s - 9 min 26.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `2.756208` |
| 58 | `q28_unmodeled_torque` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `2.679094` |
| 59 | `q14_threadlocker_material` | `symbolic_domain` | `step_05` | `6 min 16.0 s - 7 min 9.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `4.01798` |
| 60 | `q26_domain_default_not_fake_observation` | `steps_only` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `2.670158` |
| 61 | `q22_why_step_six_uncertain` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.482226` |
| 62 | `q04_step_four_readiness` | `steps_only` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `2.595224` |
| 63 | `q15_sleeve_count_and_orientation` | `query_driven_graph` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `20.244224` |
| 64 | `q03_step_three_dependency` | `symbolic_domain` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `9.529723` |
| 65 | `q23_expert_annotation_provenance` | `query_driven_graph` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `17.378312` |
| 66 | `q07_o_ring_alignment_requirement` | `symbolic_domain` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `4.702144` |
| 67 | `q24_relation_precision_targets` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.618511` |
| 68 | `q19_redo_o_ring_step` | `symbolic_domain` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `3.046955` |
| 69 | `q18_no_removal_action` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `3.000211` |
| 70 | `q05_threadlocker_dependency` | `steps_only` | `step_05` | `6 min 16.0 s - 7 min 9.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `2.614078` |
| 71 | `q30_exact_instance_count` | `steps_only` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `3.305383` |
| 72 | `q07_o_ring_alignment_requirement` | `steps_only` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `3.732657` |
| 73 | `q18_no_removal_action` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `4.216011` |
| 74 | `q06_next_step_after_cleaning` | `symbolic_domain` | `step_07` | `8 min 51.0 s - 9 min 26.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `11.665031` |
| 75 | `q21_what_to_add_for_rework` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `7.250945` |
| 76 | `q26_domain_default_not_fake_observation` | `query_driven_graph` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `21.371141` |
| 77 | `q19_redo_o_ring_step` | `query_driven_graph` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `2.874363` |
| 78 | `q13_power_screwdriver_step_six` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.187164` |
| 79 | `q31_ambiguous_okay_question` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `9.893375` |
| 80 | `q25_why_step_three_accepted` | `symbolic_domain` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.200226` |
| 81 | `q26_domain_default_not_fake_observation` | `symbolic_domain` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `3.801949` |
| 82 | `q10_requirement_not_observation` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `4.330092` |
| 83 | `q02_step_two_readiness` | `steps_only` | `step_02` | `0 min 15.0 s - 1 min 29.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `1.614875` |
| 84 | `q08_sleeve_alignment_requirement` | `query_driven_graph` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `2.605944` |
| 85 | `q13_power_screwdriver_step_six` | `query_driven_graph` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.668403` |
| 86 | `q31_ambiguous_okay_question` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_f_missing_evidence_controls` | `ok` | `3.85144` |
| 87 | `q20_historical_effects_after_uncertain_step` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_d_state_lifecycle_and_rework_limits` | `ok` | `2.904823` |
| 88 | `q22_why_step_six_uncertain` | `symbolic_domain` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `6.721225` |
| 89 | `q03_step_three_dependency` | `steps_only` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `3.665643` |
| 90 | `q04_step_four_readiness` | `query_driven_graph` | `step_04` | `3 min 16.0 s - 6 min 16.0 s` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `21.788471` |
| 91 | `q25_why_step_three_accepted` | `query_driven_graph` | `step_03` | `1 min 29.0 s - 3 min 16.0 s` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `21.800609` |
| 92 | `q09_screw_alignment_before_tightening` | `steps_only` | `step_06` | `7 min 9.0 s - 8 min 51.0 s` | `scenario_b_alignment_and_implicit_conditions` | `ok` | `4.537018` |
| 93 | `q14_threadlocker_material` | `steps_only` | `step_05` | `6 min 16.0 s - 7 min 9.0 s` | `scenario_c_tools_materials_counts_and_orientation` | `ok` | `3.004195` |
