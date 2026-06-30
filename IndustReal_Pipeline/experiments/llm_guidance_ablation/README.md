# LLM Guidance Ablation

This experiment framework compares prompting conditions for novice operator support. It is intended to test how different sources of procedural context change an LLM's answers to operator questions during assembly tasks.

This is an ablation study, not a direct competition between LLMs and knowledge graphs. The goal is to isolate the contribution of progressively richer grounding signals: a frozen procedural step list, symbolic Layer 3 inputs, and procedural reasoning graph context.

## Experiments

The framework is organized around three prompting conditions. All three use the
same novice test cases and the same frozen procedural step-list artifact, so the
ablation isolates what changes when progressively richer grounding evidence is
added.

Evaluation metadata such as `risk_type` and `expected_answer_elements` is used only after responses are generated. It must never be included in prompts sent to the LLM.

### Experiment 1: `steps_only`

**Name:** `steps_only`

**Description:** Baseline condition. The LLM receives prompt instructions, the
current step id, the novice operator question, and the frozen procedural step
list. It does not receive symbolic predicates, thesis rules, inferred
constraints, validation records, or graph evidence.

**Data source:** The prompt context comes from `input_paths.step_list`, currently:

```yaml
input_paths:
  step_list: "experiments\\shared\\data\\steps_od_only_test_p1_03_assy_0_1.txt"
```

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

**How the data is obtained and prepared for the LLM:** Generate or refresh the
step-list artifact from `step_records.jsonl` with:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\build_step_list_artifact.py `
  --step-records results\reasoning_layers\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\step_records.jsonl `
  --output experiments\shared\data\steps_od_only_test_p1_03_assy_0_1.txt
```

The artifact is built from selected fields rather than copying raw JSONL records. Each rendered step includes:

- step index
- step id
- action description
- acted-on object or component
- previous and next step id when present
- `time_window.start_frame` and `time_window.end_frame`
- confidence

At run time, the runner reads this text file verbatim and inserts it into the
configured `steps_only` prompt template.

### Experiment 2: `symbolic_domain`

**Name:** `symbolic_domain`

**Description:** Symbolic-context condition. The LLM receives everything from
`steps_only`, plus a deterministic predicate window around the current step and
the complete raw text of `config/thesis_rules.yaml`. This tests whether explicit
symbolic Layer 3 evidence and domain rules improve novice-support answers over
the step-list baseline.

**Data source:** The prompt context comes from three configured artifacts:

```yaml
input_paths:
  step_list: "experiments\\shared\\data\\steps_od_only_test_p1_03_assy_0_1.txt"
  predicate_contexts: "experiments\\shared\\data\\predicate_contexts_od_only_test_p1_03_assy_0_1_h1.json"
  thesis_rules: "config\\thesis_rules.yaml"

graph_retrieval_config: "experiments\\shared\\configs\\graph_retrieval.yaml"
```

The step-list artifact is the same file used by `steps_only`. Predicate context
is prepared from `step_records.jsonl` and `predicates.jsonl`, which are Layer 3
input artifacts produced by the IndustReal adapter. The rules are loaded
verbatim from `thesis_rules.yaml`; `domain_config.yaml` is not sent because its
relevant knowledge has already been materialized into the predicates by the
adapter.

**How the data is obtained and prepared for the LLM:** First generate the shared
step-list artifact as described in Experiment 1. Then generate the
predicate-context artifact with the hop radius configured in the shared
`graph_retrieval.yaml` file:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\build_predicate_context_artifact.py `
  --step-records results\reasoning_layers\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\step_records.jsonl `
  --predicates results\reasoning_layers\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1\predicates.jsonl `
  --graph-retrieval-config experiments\shared\configs\graph_retrieval.yaml `
  --output experiments\shared\data\predicate_contexts_od_only_test_p1_03_assy_0_1_h1.json
```

With `step_hops: 1`, each context contains predicates for the current step, its
immediate predecessor, and its immediate successor when they exist. Boundary
steps naturally contain only two steps. A value of `0` selects only the current
step. Predicate records are projected deterministically to the fields used for
rule matching: `step_id`, `name`, `args`, and `conf`; verbose provenance, notes,
and record identifiers are excluded to stay within the model context limit.

At run time, the runner selects the precomputed predicate context for the
test-case `step_id`, renders it with the shared step list and the raw
`thesis_rules.yaml` text, and inserts those blocks into the configured
`symbolic_domain` prompt template.

### Experiment 3: `graph_grounded`

**Name:** `graph_grounded`

**Description:** Graph-grounded condition. The LLM receives everything from
`steps_only`, plus a deterministic local neighborhood retrieved from the
procedural reasoning graph around the current step. This tests whether structured
graph evidence improves novice-support answers over the shared step-list
baseline.

**Data source:** The prompt context comes from the shared step list and the
procedural reasoning graph:

```yaml
input_paths:
  step_list: "experiments\\shared\\data\\steps_od_only_test_p1_03_assy_0_1.txt"
  # Leave empty to derive the graph path from the selected dataset/clip id.
  procedural_reasoning_graph: ""

graph_retrieval_config: "experiments\\shared\\configs\\graph_retrieval.yaml"
```

If `input_paths.procedural_reasoning_graph` is empty, the runner derives the
graph path from the selected dataset or IndustReal clip id under
`results/procedural_reasoning_graph/`, replacing `::` separators in the dataset
id with `__` in the directory name.
For the default IndustReal clip, the graph is built by the pipeline after Layer
3 inference and Layer 4 validation.

**How the data is obtained and prepared for the LLM:** First generate the shared
step-list artifact as described in Experiment 1. Then build the procedural
reasoning graph using the normal pipeline:

```powershell
.venv\Scripts\python.exe scripts\14_build_layer3_reasoning_adapter.py
.venv\Scripts\python.exe scripts\15_run_layer3_inference.py
.venv\Scripts\python.exe scripts\16_run_layer4_validation.py
.venv\Scripts\python.exe scripts\17_build_procedural_reasoning_graph.py
```

At run time, the experiment loads the graph JSON, extracts a deterministic
subgraph for each test-case step, and serializes that subgraph into compact text
before inserting it into the prompt. The graph-grounded prompt does not send the
raw full graph.

#### Graph Retrieval Budgets

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
edges are deduplicated by source, relation, and target, and both hop limits come
from `experiments/shared/configs/graph_retrieval.yaml`. Graph-grounded prompt reports show the two budgets,
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

### Notes:

#### Why just a window?

Experiment 2 sends a predicate window around the current step rather than the
whole `predicates.jsonl` file for four reasons:

- **Relevance:** Each novice question is anchored to one current assembly step.
  The most useful symbolic evidence is usually the current step plus nearby
  sequence context, such as the previous and next step.
- **Context size:** The full predicate list can be large and repetitive. Sending
  every predicate would consume prompt budget with evidence unrelated to the
  operator's immediate question.
- **Fair comparison:** `symbolic_domain` uses the same sequence radius as
  `graph_grounded`'s `step_hops`. With `step_hops: 1`, both conditions cover the
  same previous/current/next procedural window, but in different
  representations.
- **Avoiding accidental leakage:** The full predicate list may include far-away
  future or unrelated procedure information. A local window better matches what
  an operator-support assistant should use for the current step.

In short, Experiment 2 sends the shared full step list, local symbolic evidence,
and full thesis rules. The step list provides broad procedural orientation,
while the predicate window provides detailed symbolic grounding only where it is
most relevant.

#### Layer 2 to Layer 3 Boundary

`step_records.jsonl` and `predicates.jsonl` are Layer 3 input artifacts. They are not outputs of Layer 3 inference.

For IndustReal, `scripts/14_build_layer3_reasoning_adapter.py` converts the relevant Layer 2 output into these two files:

```text
Layer 2 output
    -> scripts/14_build_layer3_reasoning_adapter.py
    -> step_records.jsonl + predicates.jsonl
    -> scripts/15_run_layer3_inference.py (Layer 3)
```

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

Run settings live in `configs/config.yaml`. Shared OpenAI-compatible API settings live in `experiments/shared/configs/llm_api.yaml`. Prompt templates live in `configs/prompts.yaml`, including the normal chat prompts and the LM Studio fallback message used when a model template rejects the `system` role.

Operator prompts for the novice test cases live in `experiments/shared/configs/novice_questions.yaml`. The current battery is grouped by `scenario` from `experiments/docs_experiments/battery_of_questions_v1.md` so scenario-level reports can be inspected directly. The `question` field is sent to the LLM as the operator question; `scenario`, `risk_type`, `status`, and `expected_answer_elements` are evaluation-only fields and must not be sent to the LLM.

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

To resume one condition after a partial run, pass the 1-based question index to start from. For example, if `symbolic_domain` completed questions 1-3, resume at question 4:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition symbolic_domain --start-index 4 --config experiments\llm_guidance_ablation\configs\config.yaml
```

To resume `symbolic_domain` and then automatically run the later condition without waiting to start it manually:

```powershell
.venv\Scripts\python.exe experiments\llm_guidance_ablation\src\run_experiment.py --condition symbolic_domain --start-index 4 --continue-with-next-conditions --config experiments\llm_guidance_ablation\configs\config.yaml
```

## Run Artifacts

The runner writes a timestamped JSONL response file under `outputs/`. Output filenames use local time with a timezone offset, for example:

```text
outputs/responses_steps_only_20260618T184039+0200.jsonl
```

Each condition gets a separate file because its name is part of the filename, for example `responses_symbolic_domain_20260618T184039+0200.jsonl`.

Each JSONL row includes `scenario`, `risk_type`, `status`, and `expected_answer_elements` for evaluation, but those fields are not included in prompts sent to the LLM.

Upstream identifiers are preserved in response artifacts for traceability, while
LLM-facing step lists, predicates, and graph evidence use compact aliases such
as `step_1`. Each response row also includes parsed `step_provenance` fields for
the run id, evidence mode, archive, clip id, and numeric step index.

While a run is active, the console shows the condition, current/total interaction count, risk group, case id, and elapsed time for each completed request.

Each run also writes a structured communication-flow log under `outputs/logs/`, using the condition and run timestamp in its filename:

```text
outputs/logs/communication_steps_only_20260618T184039+0200.log
```

The log contains timestamped `run_started`, `request_sent`, `response_received`, and `run_completed` events. If `runtime.continue_on_llm_error` is enabled, failed calls produce `interaction_failed` events, write a failed response row, and continue to the next question. If that setting is disabled, a failed call also produces `run_failed` and stops the run. The final event records the minimum, maximum, and average successful prompt time; total duration in seconds and `HHh MMm SS.ss` form; and the number of completed and failed interactions. Prompt and response bodies are deliberately excluded from this log.

Every successful experiment run automatically writes a matching prompt-report snapshot under `outputs/prompt_reports/` using the same condition and timestamp:

```text
outputs/prompt_reports/steps_only_20260618T184039+0200/
```

Those Markdown reports document the prompt content associated with the response file from that run. Reports are grouped by `scenario` when scenario metadata is present, otherwise by `risk_type` for older test-case files. To avoid repeating large invariant blocks, each file shows shared context once, followed by the step id, question, and selected predicates or graph evidence that vary by case.

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
