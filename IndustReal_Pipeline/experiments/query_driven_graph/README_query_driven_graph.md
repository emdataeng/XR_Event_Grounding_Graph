# Query-Driven Graph Experiment

This experiment evaluates an active retrieval architecture for novice operator
support. Unlike `llm_guidance_ablation`, which compares fixed prompt-grounding
conditions, this workflow selects a Cypher query template from the operator
question, executes that query against Neo4j, and asks the LLM to answer using
only the returned graph evidence.

## First Milestone

The first milestone uses deterministic template-based Cypher retrieval:

```text
┌───────────────────┐     ┌───────────────────┐
│ Novice question   │     │ Risk type         │
└─────────┬─────────┘     └─────────┬─────────┘
          └──────────────┬───────────┘
                         ▼
              ┌─────────────────────┐
              │ Rule-based intent   │
              │ selection           │
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │ Predefined read-only│
              │ Cypher template     │
              └──────────┬──────────┘
                         │
┌───────────────────┐    │    ┌───────────────────┐
│ Current step ID   ├────┼────┤ Graph name        │
└───────────────────┘    │    └───────────────────┘
                         ▼
              ┌─────────────────────┐
              │ Parameterized       │
              │ Neo4j query         │
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │ Neo4j query result  │
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │ LLM answer grounded │
              │ in retrieved rows   │
              └─────────────────────┘
```

This keeps query retrieval inspectable before adding LLM-generated Cypher.

Shared novice questions and frozen step-list artifacts live under
`experiments/shared/` so this experiment and `llm_guidance_ablation` use the same
test cases and procedural baseline.
Shared OpenAI-compatible API settings live in
`experiments/shared/configs/llm_api.yaml`.
Shared sequence and semantic graph-traversal budgets live in
`experiments/shared/configs/graph_retrieval.yaml`; this experiment renders those
values into its validated read-only Cypher templates.

## Run Prerequisites

Start a local Neo4j instance and set connection variables in `.env`:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=industreal123
```

Build and import the procedural reasoning graph:

```powershell
.venv\Scripts\python.exe scripts\17_build_procedural_reasoning_graph.py
.venv\Scripts\python.exe scripts\18_import_procedural_reasoning_graph_neo4j.py `
  --graph results\procedural_reasoning_graph\raw_cad_dataset__all_test_clips__od_only__test_p1__03_assy_0_1 `
  --env-file experiments\query_driven_graph\.env.local
```

## Query Guards and Preflight

The experiment is designed to query Neo4j before spending any LLM calls. Run the
preflight check first:

```powershell
.venv\Scripts\python.exe experiments\query_driven_graph\src\preflight_neo4j_queries.py `
  --config experiments\query_driven_graph\configs\config_query_driven_graph.yaml `
  --fail-on-empty
```

The preflight performs these checks:

- Confirms Neo4j is reachable.
- Reports the total node count in the database.
- Lists available `graph_name` values.
- Verifies that the configured `neo4j.graph_name` has imported nodes.
- Queries all valid `Step.step_id` values for the configured graph.
- Runs each selected Cypher template against each novice test case.
- Fails before any LLM run if a valid step produces zero query rows.

The main runner uses the same safeguards:

- If the requested step id is not present in Neo4j, the runner does not waste a
  normal template query. It creates a diagnostic evidence row with
  `current_step_found=false`, `requested_step_id`, `available_step_count`, and
  nearby valid step ids when available. This diagnostic row may still be sent to
  the LLM because it is useful evidence for missing-context questions.
- If a valid step query returns zero rows, the LLM call is skipped. The JSONL
  `response` field records that no LLM call was made because Neo4j returned no
  grounded evidence.
- If query execution fails, the LLM call is skipped. The JSONL `query_status`
  becomes `failed`, `query_error` stores the technical error, and `response`
  explains that answer generation was skipped.

`query_status` is the machine-readable outcome (`ok`, `missing_step`, or
`failed`). `query_error` is `null` unless Neo4j or the Python driver raised an
exception.

## Run Command

From the repository root:

```powershell
.venv\Scripts\python.exe experiments\query_driven_graph\src\run_experiment_query_driven_graph.py `
  --config experiments\query_driven_graph\configs\config_query_driven_graph.yaml
```

Use `--dry-run` to validate template selection and output artifacts without
calling the LLM:

```powershell
.venv\Scripts\python.exe experiments\query_driven_graph\src\run_experiment_query_driven_graph.py `
  --config experiments\query_driven_graph\configs\config_query_driven_graph.yaml `
  --dry-run
```

## Outputs

Each run writes:

- `outputs/responses_query_driven_graph_<timestamp>.jsonl`
- `outputs/logs/communication_query_driven_graph_<timestamp>.log`
- `outputs/query_reports/query_driven_graph_<timestamp>/`

Each JSONL response row includes the selected intent, Cypher query, query
parameters, query rows, and final answer. Evaluation metadata is saved for later
analysis but is not sent to the LLM.

## Prompt Identifier Compaction

Upstream graph identifiers remain unchanged for Neo4j queries, stored query
parameters, and traceability. At the LLM prompt boundary, identifiers belonging
to the active clip are rendered as compact aliases such as `step_1`.

Response rows retain the original `step_id` and add `step_provenance`, containing
the parsed run id, evidence mode, archive, clip id, and numeric step index.
