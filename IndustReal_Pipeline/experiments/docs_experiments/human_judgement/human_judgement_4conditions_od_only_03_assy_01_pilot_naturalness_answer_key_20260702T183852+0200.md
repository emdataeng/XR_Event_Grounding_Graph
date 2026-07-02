# Human Judgement Answer Key - 4 Conditions

Generated at: `2026-07-02T18:38:52+02:00`
Random seed: `20260702183852`
Clip name: `od_only_03_assy_01_pilot_naturalness`

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

- `steps_only`: `experiments\llm_guidance_ablation\outputs\responses_steps_only_od_only_03_assy_01_20260702T182949+0200.jsonl`
- `symbolic_domain`: `experiments\llm_guidance_ablation\outputs\responses_symbolic_domain_od_only_03_assy_01_20260702T183017+0200.jsonl`
- `graph_grounded`: `experiments\llm_guidance_ablation\outputs\responses_graph_grounded_od_only_03_assy_01_20260702T183133+0200.jsonl`
- `query_driven_graph`: `experiments\query_driven_graph\outputs\responses_query_driven_graph_od_only_03_assy_01_20260702T183230+0200.jsonl`

## Item Mapping

| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |
|---:|---|---|---|---|---|---:|
| 01 | `q19_reinstallation_guidance_after_removal` | `graph_grounded` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `7.867192` |
| 02 | `q09_root_component_alignment_exception` | `steps_only` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `4.380872` |
| 03 | `q21_why_accepted` | `query_driven_graph` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `15.193079` |
| 04 | `q03_direct_installation_target` | `graph_grounded` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `7.766271` |
| 05 | `q03_direct_installation_target` | `steps_only` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `6.313896` |
| 06 | `q27_unknown_step` | `graph_grounded` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `3.35495` |
| 07 | `q03_direct_installation_target` | `query_driven_graph` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `15.22032` |
| 08 | `q21_why_accepted` | `steps_only` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `4.305871` |
| 09 | `q19_reinstallation_guidance_after_removal` | `symbolic_domain` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `12.160306` |
| 10 | `q27_unknown_step` | `symbolic_domain` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `12.919483` |
| 11 | `q15_unsupported_tool_proposal` | `symbolic_domain` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `13.332594` |
| 12 | `q15_unsupported_tool_proposal` | `query_driven_graph` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `16.045423` |
| 13 | `q09_root_component_alignment_exception` | `query_driven_graph` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `15.184096` |
| 14 | `q21_why_accepted` | `graph_grounded` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `9.612422` |
| 15 | `q15_unsupported_tool_proposal` | `steps_only` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `4.524058` |
| 16 | `q03_direct_installation_target` | `symbolic_domain` | `step_6` | `scenario_a_dependency_and_prerequisite_checks` | `ok` | `12.578292` |
| 17 | `q09_root_component_alignment_exception` | `symbolic_domain` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `12.099762` |
| 18 | `q19_reinstallation_guidance_after_removal` | `steps_only` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `4.222952` |
| 19 | `q27_unknown_step` | `query_driven_graph` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `5.309438` |
| 20 | `q15_unsupported_tool_proposal` | `graph_grounded` | `step_4` | `scenario_c_safety_and_tool_constraints` | `ok` | `10.149581` |
| 21 | `q27_unknown_step` | `steps_only` | `step_999` | `scenario_f_missing_evidence_controls` | `ok` | `4.678868` |
| 22 | `q21_why_accepted` | `symbolic_domain` | `step_1` | `scenario_e_validation_status_provenance_and_relation_precision` | `ok` | `12.128169` |
| 23 | `q19_reinstallation_guidance_after_removal` | `query_driven_graph` | `step_9` | `scenario_d_state_lifecycle_and_error_recovery` | `ok` | `19.858251` |
| 24 | `q09_root_component_alignment_exception` | `graph_grounded` | `step_0` | `scenario_b_troubleshooting_implicit_conditions` | `ok` | `6.358142` |
