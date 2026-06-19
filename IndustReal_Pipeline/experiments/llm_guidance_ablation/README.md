# LLM Guidance Ablation

This experiment framework compares prompting conditions for novice operator support. It is intended to test how different sources of procedural context change an LLM's answers to operator questions during assembly tasks.

This is an ablation study, not a direct competition between LLMs and knowledge graphs. The goal is to isolate the contribution of progressively richer grounding signals: a frozen procedural step list, symbolic Layer 3 inputs, and procedural reasoning graph context.

## Prompting Conditions

The framework is organized around three conditions:

- `steps_only`: The LLM receives the frozen procedural step-list artifact together with the novice question.
- `symbolic_domain`: The LLM receives the same frozen step-list artifact, a deterministic predicate window around the current step, and the complete raw text of `thesis_rules.yaml`.
- `graph_grounded`: The LLM receives the frozen procedural step list plus a local neighborhood retrieved from the procedural reasoning graph.

Evaluation metadata such as `risk_type` and `expected_answer_elements` is used only after responses are generated. It must never be included in prompts sent to the LLM.

### `steps_only` Data Source

For the `steps_only` condition, the procedural step list sent to the LLM is
loaded verbatim from `input_paths.step_list`. That text artifact is generated
deterministically from `step_records.jsonl` before the experiment runs. The
current step id is supplied separately by each test case and does not alter the
shared list.

The `steps_only` step list does **not** use `predicates.jsonl`,
`domain_config.yaml`, `thesis_rules.yaml`, inferred constraints, Layer 4
validation records, or the procedural reasoning graph. Apart from the rendered
step-list artifact, the prompt contains only the prompt instructions, current step id,
and novice question.

All three conditions use the same `input_paths.step_list` artifact. This is the fairness invariant for the ablation: the grounded conditions differ only in the additional evidence they provide.

```yaml
input_paths:
  step_list: "experiments\\llm_guidance_ablation\\data\\steps_od_only_test_p1_03_assy_0_1.txt"
  predicate_contexts: "experiments\\llm_guidance_ablation\\data\\predicate_contexts_od_only_test_p1_03_assy_0_1_h1.json"
  thesis_rules: "config\\thesis_rules.yaml"

context_retrieval:
  step_hops: 1
  evidence_hops: 2
```

Generate or refresh the step-list artifact from `step_records.jsonl` with:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\build_step_list_artifact.py `
  --step-records results\reasoning_layers\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\step_records.jsonl `
  --output experiments\llm_guidance_ablation\data\steps_od_only_test_p1_03_assy_0_1.txt
```

The artifact is built from selected fields rather than copying raw JSONL records. Each rendered step includes:

- step index
- step id
- action description
- acted-on object or component
- previous and next step id when present
- `time_window.start_frame` and `time_window.end_frame`
- confidence

Generate the predicate-context artifact with the same hop radius configured in
`context_retrieval.step_hops`:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\build_predicate_context_artifact.py `
  --step-records results\reasoning_layers\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\step_records.jsonl `
  --predicates results\reasoning_layers\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\predicates.jsonl `
  --hops 1 `
  --output experiments\llm_guidance_ablation\data\predicate_contexts_od_only_test_p1_03_assy_0_1_h1.json
```

With `step_hops: 1`, each context contains predicates for the current step, its
immediate predecessor, and its immediate successor when they exist. Boundary
steps naturally contain only two steps. A value of `0` selects only the current
step. Predicate records are projected deterministically to the fields used for
rule matching: `step_id`, `name`, `args`, and `conf`; verbose provenance, notes,
and record identifiers are excluded to stay within the model context limit.

### Graph Retrieval Budgets

The `graph_grounded` condition uses two deterministic traversal budgets:

- `step_hops` follows only `NEXT` edges between `Step` nodes. It uses the same
  radius as the `symbolic_domain` predicate artifact, so both conditions cover
  the same previous/current/next sequence window.
- `evidence_hops` follows semantic relations from the original current step.
  With the default value `2`, this includes paths such as
  `Step -> Predicate -> Source` and `Step -> Constraint -> Rule`.

The semantic edge allowlist includes `HAS_PREDICATE`, `HAS_CONSTRAINT`,
`REQUIRES`, `PRODUCES`, `SUPPORTED_BY`, `DERIVED_FROM`, `USES`, `HAS_ENTITY`,
`INVALIDATED_BY`, and `DEPENDS_ON`. Sequence neighbors and any other discovered
`Step` nodes are included but not expanded semantically. `Entity`, `Rule`, and
`Source` nodes are also terminal. This prevents `NEXT` chains, shared entities,
and provenance branches from pulling unrelated portions of the graph into the
prompt.

Traversal is reproducible: nodes and edges are processed in sorted order,
edges are deduplicated by source, relation, and target, and both hop limits are
fixed in `config.yaml`. Graph-grounded prompt reports show the two budgets,
node and relationship counts, and the exact serialized evidence sent to the
LLM.

The graph serializer uses a hybrid edge format. Every node is defined once with
a compact alias such as `N27`. Most high-volume semantic edges use those aliases
to control prompt size, for example `N27 -[HAS_PREDICATE]-> N10`. For `NEXT` and
`DEPENDS_ON`, the endpoints also include short step identifiers, for example
`N27<Step:event_1> -[NEXT]-> N29<Step:event_2>`. Direction and step identity are
especially important for these ordering relationships, while expanding every
predicate, constraint, entity, rule, and source label on every edge would add
substantial repetition. The serializer does not generate a separate interpreted
sequence summary; the graph relationships remain the authoritative evidence.

### Layer 2 to Layer 3 Boundary

`step_records.jsonl` and `predicates.jsonl` are Layer 3 input artifacts. They are not outputs of Layer 3 inference.

For IndustReal, `scripts/14_build_layer3_reasoning_adapter.py` converts the relevant Layer 2 output into these two files:

```text
Layer 2 output
    -> scripts/14_build_layer3_reasoning_adapter.py
    -> step_records.jsonl + predicates.jsonl
    -> scripts/15_run_layer3_inference.py (Layer 3)
```

The artifact-building scripts read `step_records.jsonl` and `predicates.jsonl`; experiment runs read the resulting frozen artifacts instead. `symbolic_domain` additionally sends the selected predicate window and `thesis_rules.yaml`. It does not send `domain_config.yaml`, whose relevant knowledge has already been materialized into the predicates by the adapter.

## Dataset Selection

The experiment should support IndustReal clips as well as future datasets. For an IndustReal run, the intended interface is:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition graph_grounded --industreal raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1
```

For another dataset, the runner should accept dataset-specific paths and configuration:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition symbolic_domain --dataset my_dataset --config experiments\llm_guidance_ablation\configs\config.yaml
```

Before running the LLM experiment, the selected dataset is expected to have the required artifacts built by the existing pipeline stages. For IndustReal, the adapter first creates the Layer 3 inputs from Layer 2 output; Layer 3 inference then consumes those inputs:

```powershell
.venv\Scripts\python.exe scripts\14_build_layer3_reasoning_adapter.py
.venv\Scripts\python.exe scripts\15_run_layer3_inference.py
.venv\Scripts\python.exe scripts\16_run_layer4_validation.py
.venv\Scripts\python.exe scripts\17_build_procedural_reasoning_graph.py
.venv\Scripts\python.exe scripts\18_import_procedural_reasoning_graph_neo4j.py
.venv\Scripts\python.exe scripts\19_build_graph_data_js.py
```

When a non-IndustReal dataset is selected, generate equivalent frozen step-list and predicate-context artifacts, then provide those artifacts plus the corresponding `thesis_rules` and graph paths in `configs/config.yaml`.

## Local LLM Server

The implementation is designed to be compatible with OpenAI-compatible APIs. LM Studio can be used as a local server by setting values such as:

```yaml
api_base_url: "http://localhost:1234/v1"
api_key: "lm-studio"
model_name: "local-model-name"
temperature: 0.0
```

The checked-in configuration uses temperature `0.0` to minimize sampling variation between otherwise identical runs.

## Current Status

This folder contains working runners for `steps_only`, `symbolic_domain`, and `graph_grounded`.

The `symbolic_domain` condition uses deterministic sequence-window retrieval rather than summarization: it selects predicates for the current step and configured neighboring steps, projects only rule-matching fields, and includes `thesis_rules.yaml` verbatim. This avoids introducing a separate summarization model into the ablation.

Run settings live in `configs/config.yaml`. Prompt templates live in `configs/prompts.yaml`, including the normal chat prompts and the LM Studio fallback message used when a model template rejects the `system` role.

Operator prompts for the novice test cases live in `configs/novice_questions.yaml`. They are grouped by `risk_type` so cases can be removed or curated easily. The `question` field is sent to the LLM as the operator question; `risk_type` and `expected_answer_elements` are evaluation-only fields and must not be sent to the LLM.

## Run Commands

Run all three conditions sequentially with one command:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition all --config experiments\llm_guidance_ablation\configs\config.yaml
```

This runs `steps_only`, `symbolic_domain`, and `graph_grounded` in that order. Each condition receives its own timestamped response file, prompt-report directory, and communication log.

From `experiments/llm_guidance_ablation`, run any condition with:

```powershell
python src/run_experiment.py --condition steps_only
python src/run_experiment.py --condition symbolic_domain
python src/run_experiment.py --condition graph_grounded
```

From the repository root, the equivalent command is:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition steps_only --config experiments\llm_guidance_ablation\configs\config.yaml
```

From the repository root, run with windowed symbolic predicates and full rules:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition symbolic_domain --config experiments\llm_guidance_ablation\configs\config.yaml
```

## Run Artifacts

The runner writes a timestamped JSONL response file under `outputs/`. Output filenames use local time with a timezone offset, for example:

```text
outputs/responses_steps_only_20260618T184039+0200.jsonl
```

Each condition gets a separate file because its name is part of the filename, for example `responses_symbolic_domain_20260618T184039+0200.jsonl`.

Each JSONL row includes `risk_type` and `expected_answer_elements` for evaluation, but those fields are not included in prompts sent to the LLM.

While a run is active, the console shows the condition, current/total interaction count, risk group, case id, and elapsed time for each completed request.

Each run also writes a structured communication-flow log under `outputs/logs/`, using the condition and run timestamp in its filename:

```text
outputs/logs/communication_steps_only_20260618T184039+0200.log
```

The log contains timestamped `run_started`, `request_sent`, `response_received`, and `run_completed` events. Failed calls produce `interaction_failed` and `run_failed` events. The final event records the minimum, maximum, and average successful prompt time; total duration in seconds and `HHh MMm SS.ss` form; and the number of completed interactions. Prompt and response bodies are deliberately excluded from this log.

Every successful experiment run automatically writes a matching prompt-report snapshot under `outputs/prompt_reports/` using the same condition and timestamp:

```text
outputs/prompt_reports/steps_only_20260618T184039+0200/
```

Those Markdown reports document the prompt content associated with the response file from that run. Reports are grouped by `risk_type`. To avoid repeating large invariant blocks, each file shows shared context once, followed by the step id, question, and selected predicates or graph evidence that vary by case.

Reports generated as part of a run also include the run-wide minimum, maximum, and average prompt interaction times and total experiment time. Standalone report exports state that runtime timing statistics are unavailable.

The standalone exporter below can still be used when you want to regenerate prompt reports without calling the LLM. By default, it writes to `outputs/prompt_reports/` rather than a timestamped run folder:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\export_prompt_reports.py --condition steps_only --config experiments\llm_guidance_ablation\configs\config.yaml
```

The same exporter supports `--condition symbolic_domain` and `--condition graph_grounded`.

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\export_prompt_reports.py --condition graph_grounded --config experiments\llm_guidance_ablation\configs\config.yaml
```

Evaluate generated responses:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\evaluate_responses.py --config experiments\llm_guidance_ablation\configs\config.yaml
```
