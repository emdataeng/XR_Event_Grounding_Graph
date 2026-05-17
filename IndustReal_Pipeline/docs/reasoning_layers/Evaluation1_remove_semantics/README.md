# Evaluation 1 Remove Semantics Evidence

This folder contains the post-change evidence for remove-action semantics. It is intentionally separate from `docs/reasoning_layers/Evaluation1/`, which remains the before-case baseline where the remove action was reported as unsupported rule coverage.

## Scope

This evidence checks the reasoning-layer artifact chain after adding remove rules and active-effect invalidation. It does not evaluate perception, object detection, step segmentation, or CAD-to-image alignment.

## Key Outputs

- `inferred_constraints.csv`: Layer 3 constraints, including remove precondition and removed effect.
- `rule_coverage_diagnostics.csv`: Layer 3 rule coverage diagnostics; the remove step is no longer `no_applicable_rule`.
- `validation_records.jsonl`, `step_validations.csv`, `explanation_traces.json`: Layer 4 validation artifacts.
- `effect_history_diagnostics.csv`: active/historical effect diagnostics and invalidation evidence.
- `procedural_reasoning_graph/`: graph JSON and node/edge CSV export.
- `graph_remove_semantics_check.csv`: remove-specific graph checks.
- `evaluation_report.md` and `evaluation_summary.csv`: human-readable and tabular post-change evaluation summary.
- `evidence/evaluation_results.json`: machine-readable remove-semantics evidence.

## Reproduction Commands

Run Layer 3, Layer 4, graph export, and the post-change evaluator from the repository root using the virtual environment Python.

```powershell
.venv\Scripts\python.exe scripts_run_layer3_inference.py --step-records resultseasoning_layersaw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\step_records.jsonl --predicates resultseasoning_layersaw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\predicates.jsonl --rules config	hesis_rules.yaml --output docseasoning_layers\Evaluation1_remove_semantics\inferred_constraints.csv
.venv\Scripts\python.exe scripts_run_layer4_validation.py --step-records resultseasoning_layersaw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\step_records.jsonl --predicates resultseasoning_layersaw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\predicates.jsonl --constraints docseasoning_layers\Evaluation1_remove_semantics\inferred_constraints.csv --rule-coverage docseasoning_layers\Evaluation1_remove_semanticsule_coverage_diagnostics.csv --output docseasoning_layers\Evaluation1_remove_semanticsalidation_records.jsonl
.venv\Scripts\python.exe scripts_build_procedural_reasoning_graph.py --validations docseasoning_layers\Evaluation1_remove_semanticsalidation_records.jsonl --step-records resultseasoning_layersaw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1\step_records.jsonl --output-dir docseasoning_layers\Evaluation1_remove_semantics\procedural_reasoning_graph
.venv\Scripts\python.exe scripts_evaluate_pipeline_artifact_correctness.py --project-root . --run-id raw_cad_dataset__all_test_clips --clip-result-id raw_cad_dataset__all_test_clips__sample_test_p1_03_assy_0_1 --reasoning-dir docseasoning_layers\Evaluation1_remove_semantics --graph-dir docseasoning_layers\Evaluation1_remove_semantics\procedural_reasoning_graph --output-dir docseasoning_layers\Evaluation1_remove_semantics
```
