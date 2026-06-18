# LLM Guidance Ablation

This experiment framework compares prompting conditions for novice operator support. It is intended to test how different sources of procedural context change an LLM's answers to operator questions during assembly tasks.

This is an ablation study, not a direct competition between LLMs and knowledge graphs. The goal is to isolate the contribution of progressively richer grounding signals: generated steps, raw domain material, and procedural reasoning graph context.

## Prompting Conditions

The framework is organized around three conditions:

- `steps_only`: The LLM receives only the generated procedural step context for the selected case.
- `symbolic_domain`: The LLM receives generated procedural steps plus symbolic domain facts such as predicates derived from `predicates.jsonl`.
- `graph_grounded`: The LLM receives generated procedural steps plus context retrieved from the procedural reasoning graph.

Evaluation metadata such as `risk_type` and `expected_answer_elements` is used only after responses are generated. It must never be included in prompts sent to the LLM.

For the current `steps_only` implementation, `input_paths.generated_steps` should point to a Layer 3 `step_records.jsonl` file, for example:

```yaml
input_paths:
  generated_steps: "results\\reasoning_layers\\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\\step_records.jsonl"
```

The prompt is built from selected fields only, not the raw JSONL record. Each step includes:

- step index
- step id
- action description
- acted-on object or component
- previous and next step id when present
- `time_window.start_frame` and `time_window.end_frame`
- confidence

## Dataset Selection

The experiment should support IndustReal clips as well as future datasets. For an IndustReal run, the intended interface is:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition graph_grounded --industreal raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1
```

For another dataset, the runner should accept dataset-specific paths and configuration:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition symbolic_domain --dataset my_dataset --config experiments\llm_guidance_ablation\configs\config.yaml
```

Before running the LLM experiment, the selected dataset is expected to have the derived thesis artifacts built by running the existing pipeline stages:

```powershell
.venv\Scripts\python.exe scripts\14_build_layer3_reasoning_adapter.py
.venv\Scripts\python.exe scripts\15_run_layer3_inference.py
.venv\Scripts\python.exe scripts\16_run_layer4_validation.py
.venv\Scripts\python.exe scripts\17_build_procedural_reasoning_graph.py
.venv\Scripts\python.exe scripts\18_import_procedural_reasoning_graph_neo4j.py
.venv\Scripts\python.exe scripts\19_build_graph_data_js.py
```

When a non-IndustReal dataset is selected, provide the corresponding `domain_config`, `thesis_rules`, generated steps, and graph artifact paths in `configs/config.yaml`.

## Local LLM Server

The implementation is designed to be compatible with OpenAI-compatible APIs. LM Studio can be used as a local server by setting values such as:

```yaml
api_base_url: "http://localhost:1234/v1"
api_key: "lm-studio"
model_name: "local-model-name"
```

## Current Status

This folder currently contains the first working runner for the `steps_only` condition. The `symbolic_domain` and `graph_grounded` context builders are present as placeholders for later milestones.

Run settings live in `configs/config.yaml`. Prompt templates live in `configs/prompts.yaml`, including the normal chat prompts and the LM Studio fallback message used when a model template rejects the `system` role.

## Planned Commands

From `experiments/llm_guidance_ablation`, run the first implemented condition:

```powershell
python src/run_experiment.py --condition steps_only
```

From the repository root, the equivalent command is:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition steps_only --config experiments\llm_guidance_ablation\configs\config.yaml
```

The runner writes a timestamped JSONL file under `outputs/`. Output filenames use local time with a timezone offset, for example `responses_steps_only_20260618T184039+0200.jsonl`. Each row includes `risk_type` and `expected_answer_elements` for evaluation, but those fields are not included in prompts sent to the LLM.

Export report-ready Markdown files showing the prompt content for each test case:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\export_prompt_reports.py --condition steps_only --config experiments\llm_guidance_ablation\configs\config.yaml
```

Planned future conditions:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition symbolic_domain --config experiments\llm_guidance_ablation\configs\config.yaml
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition graph_grounded --config experiments\llm_guidance_ablation\configs\config.yaml
```

Evaluate generated responses:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\evaluate_responses.py --config experiments\llm_guidance_ablation\configs\config.yaml
```
