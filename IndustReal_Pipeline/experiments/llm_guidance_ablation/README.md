# LLM Guidance Ablation

This experiment framework compares prompting conditions for novice operator support. It is intended to test how different sources of procedural context change an LLM's answers to operator questions during assembly tasks.

This is an ablation study, not a direct competition between LLMs and knowledge graphs. The goal is to isolate the contribution of progressively richer grounding signals: generated steps, raw domain material, and procedural reasoning graph context.

## Prompting Conditions

The framework is organized around three conditions:

- `steps_only`: The LLM receives only the generated procedural step context for the selected case.
- `raw_domain`: The LLM receives generated procedural steps plus raw domain context such as domain configuration and rule text.
- `graph_grounded`: The LLM receives generated procedural steps plus context retrieved from the procedural reasoning graph.

Evaluation metadata such as `risk_type` and `expected_answer_elements` is used only after responses are generated. It must never be included in prompts sent to the LLM.

## Dataset Selection

The experiment should support IndustReal clips as well as future datasets. For an IndustReal run, the intended interface is:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition graph_grounded --industreal raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1
```

For another dataset, the runner should accept dataset-specific paths and configuration:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition raw_domain --dataset my_dataset --config experiments\llm_guidance_ablation\config.yaml
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

When a non-IndustReal dataset is selected, provide the corresponding `domain_config`, `thesis_rules`, generated steps, and graph artifact paths in `config.yaml`.

## Local LLM Server

The implementation is designed to be compatible with OpenAI-compatible APIs. LM Studio can be used as a local server by setting values such as:

```yaml
api_base_url: "http://localhost:1234/v1"
api_key: "lm-studio"
model_name: "local-model-name"
```

## Current Status

This folder currently contains placeholders for the experiment structure, configuration, context construction, LLM client integration, graph loading, experiment execution, and response evaluation. The full prompting and evaluation logic is intentionally not implemented yet.

## Planned Commands

Run all conditions:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition steps_only --config experiments\llm_guidance_ablation\config.yaml
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition raw_domain --config experiments\llm_guidance_ablation\config.yaml
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition graph_grounded --config experiments\llm_guidance_ablation\config.yaml
```

Evaluate generated responses:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\evaluate_responses.py --config experiments\llm_guidance_ablation\config.yaml
```
