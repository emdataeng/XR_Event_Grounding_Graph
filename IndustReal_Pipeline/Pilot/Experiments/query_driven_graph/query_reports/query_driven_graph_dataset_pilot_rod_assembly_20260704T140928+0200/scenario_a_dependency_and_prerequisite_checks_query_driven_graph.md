# Prompt Report: scenario_a_dependency_and_prerequisite_checks

Generated at: 2026-07-04T14:15:55+02:00

- Condition: `query_driven_graph`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Cases in this report: `6`

## API Request Settings

- LLM config path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\llm_api_masoud.yaml`
- API base URL: `https://counseling-inspired-sizes-yellow.trycloudflare.com/v1`
- Model name: `google/gemma-4-26b-a4b-qat`
- Temperature: `0.0`
- Max tokens: `2048`
- Request timeout seconds: `3600.0`
- Max retries: `0`

## Run Timing Statistics

These statistics cover all successful prompt interactions in this experiment run.

- Completed interactions: `31`
- Failed interactions: `0`
- Minimum prompt time: `2.61 s`
- Maximum prompt time: `21.80 s`
- Average prompt time: `12.46 s`
- Total experiment time: `00h 06m 26.74s`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v1_pilot_rod_assembly.yaml`
- ID: `novice_questions_pilot_rod_assembly`
- Version: `v1`
- Case count: `31`
- SHA-256: `60a2ed6fae1d`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `not stored in response rows`
- Step-list artifact loaded: `True`
- Windowed predicates included: `no`
- Sequence step-hop radius: `not applicable`
- Semantic evidence-hop radius: `not applicable`
- Thesis rules included: `no`
- Procedural reasoning graph included: `yes`
- Query template selection mode: `deterministic`
- Neo4j row limit source: `experiment config`

The query-driven graph condition sends a deterministic Cypher query, its parameters, and returned Neo4j evidence for each case. Evaluation-only fields such as risk type, scenario, status, and expected answer elements are documented below but are not included as answer requirements.

## Graph Provenance

- Graph name: `procedural_reasoning_graph::pilot_rod_assembly`
- PRG id: `GraphManifest::procedural_reasoning_graph::pilot_rod_assembly`
- Graph schema version: `1.0`
- Graph built at: `2026-07-04T12:41:24+02:00`
- Graph builder: `src.procedural_reasoning_graph.build_procedural_reasoning_graph`
- Domain config: version `0.1.0`, sha256 `3db6578d1622`, path `Pilot\domain_config_pilot.yaml`
- Thesis rules: version `0.1.0`, sha256 `3b16bb8e6529`, path `Pilot\rules_pilot.yaml`
- Validation config: version `0.1.0`, sha256 `3b16bb8e6529`, path `Pilot\rules_pilot.yaml`

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### Actual System Message Sent

- Role: `system`

```text
You are an assistant helping a novice assembly operator perform a manufacturing task. Answer the operator's specific question directly, using only the information provided. Be concise, practical, and safety-aware. Do not use any knowledge beyond what is explicitly provided. If information is missing, uncertain, or conflicting, say so clearly rather than guessing. Write in plain language as if you were directly guiding the operator. Translate technical notation, predicate names, relation labels, graph terms, and internal system terminology into natural wording. Do not write predicate-like phrases such as "requires installed(...)", "produces installed(...)", "hasInstallTarget(...)", or relation labels such as "SUPPORTED_BY" or "DEPENDS_ON"; explain their meaning instead. You may mention step numbers, part names, tool names, and earlier actions when they help answer the operator's question or support the answer. If the question asks what happens next or what earlier action supports the current step, answer that using only the provided information. Do not expose internal labels unless they are necessary to identify a part, tool, or step. Keep the answer precise and directly useful. Do not add extra coaching, encouragement, or procedural advice unless it is supported by the provided information. End every response with the exact marker "(EOR)" on the final line.
```

### Frozen Procedural Step List

This block is inserted into the user message for every case when configured.

```text
Pilot rod assembly procedure:

Step 1 [0-15s]: The operator places a long metal rod on the workbench.

Step 2 [15-89s]: The operator slides a combination of long, short and copper sleeves onto the rod. The copper sleeve should face to the right. The procedure specifies six copper sleeves and five long sleeves, starting and finishing with copper sleeves.

Step 3 [89-196s]: The operator places O-rings in the holes on the rod and adjusts the sleeves over them.

Step 4 [196-376s]: The operator drives the screws halfway into all holes using a power screwdriver.

Step 5 [376-429s]: The operator applies threadlocker (Loctite) to all partially inserted screws.

Step 6 [429-531s]: The operator fully tightens all screws to secure the sleeves. The screws should go all the way into the sleeve, but not so far that they stick out.

Step 7 [531-566s]: The operator cleans the rod and sleeves with ethanol and paper. The copper part should not be polished.

Step 8 [566-642s]: The operator applies grease to a sponge and lubricates the silver-colored sleeves while avoiding the copper sleeves.


Operator question:
I am at the first step. What should I put where, and what does this make possible later?
```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q01_start_sequence_current_action

- Step id: `step::pilot_rod_assembly::step_01`
- Operator question: I am at the first step. What should I put where, and what does this make possible later?
- Retrieval template: `installation_check`
- Retrieval template description: `Retrieve requirements, produced effects, and support around the current step.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `19.67 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_01"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 2 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_01\", \"secured\", \"metal_rod\", \"workbench\"], \"condition\": {\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_01::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_01_secured_metal_rod_workbench\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_01\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "on",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces on(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces secured(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "place"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_01, place)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "on",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_01, on, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_01, secured, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_01\", 0, 15]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_01, 0, 15)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_01, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_01, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "on",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces on(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces secured(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 1 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 1 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_01

Selected retrieval template:
installation_check

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 2 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_01\", \"secured\", \"metal_rod\", \"workbench\"], \"condition\": {\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_01::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_01_secured_metal_rod_workbench\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_01\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "on",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces on(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces secured(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "place"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_01, place)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "on",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_01, on, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_01, secured, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_01\", 0, 15]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_01, 0, 15)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_01, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_01, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "on",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces on(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_01",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces secured(metal_rod, workbench) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 1 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 1 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "metal_rod",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places a long metal rod on the workbench.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "workbench",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_01",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Answer

You are currently at Step 1: "The operator places a long metal rod on the workbench."

**What to do:**
You should place the long metal rod on the workbench.

**What this makes possible later:**
This step is a prerequisite for Step 2, which involves sliding a combination of long, short, and copper sleeves onto the rod.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_a_dependency_and_prerequisite_checks`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Status: `Runnable now`
- Expected answer elements:
  - identify metal_rod and workbench
  - state that the rod is placed on the workbench
  - mention that secured(metal_rod, workbench) is available as expert-annotated support for later sleeve installation
  - distinguish on(metal_rod, workbench) from secured(metal_rod, workbench)

## Case: q02_step_two_readiness

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: Can I start sliding the sleeves onto the rod, or does something need to be true first?
- Retrieval template: `installation_check`
- Retrieval template description: `Retrieve requirements, produced effects, and support around the current step.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `18.38 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_02"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 1 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_01\", \"secured\", \"metal_rod\", \"workbench\"], \"condition\": {\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_01::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_01_secured_metal_rod_workbench\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_01\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_02\", \"sleeves_on\", \"sleeve\", \"metal_rod\"], \"condition\": {\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_02::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_02_sleeves_on_sleeve_metal_rod\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_02\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "slide"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_02, slide)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, oriented, copper_sleeve, right_side)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_02, secured, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_02\", 15, 89]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_02, 15, 89)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "copper_sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, copper_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "long_sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, long_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "short_sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, short_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "REQUIRES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 2 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_02

Selected retrieval template:
installation_check

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 1 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_01\", \"secured\", \"metal_rod\", \"workbench\"], \"condition\": {\"args\": [\"metal_rod\", \"workbench\"], \"name\": \"secured\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_01::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_01_secured_metal_rod_workbench\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_01\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_02\", \"sleeves_on\", \"sleeve\", \"metal_rod\"], \"condition\": {\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_02::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_02_sleeves_on_sleeve_metal_rod\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_02\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "slide"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_02, slide)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, oriented, copper_sleeve, right_side)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_02, secured, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_02\", 15, 89]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_02, 15, 89)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "copper_sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, copper_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "long_sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, long_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "short_sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, short_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_02, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "REQUIRES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 2 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Answer

Before you can start sliding the sleeves onto the rod, the metal rod must be secured to the workbench. This condition was established in Step 1.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_a_dependency_and_prerequisite_checks`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Status: `Runnable now`
- Expected answer elements:
  - identify required secured(metal_rod, workbench)
  - identify Step 1 as the supporting producer
  - state that the requirement is supported
  - avoid saying the domain default alone proves the condition

## Case: q03_step_three_dependency

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: Before placing the O-rings, what earlier sleeve condition must already hold?
- Retrieval template: `installation_check`
- Retrieval template description: `Retrieve requirements, produced effects, and support around the current step.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `19.12 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_03"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 2 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_02\", \"sleeves_on\", \"sleeve\", \"metal_rod\"], \"condition\": {\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_02::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_02_sleeves_on_sleeve_metal_rod\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_02\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"adjusted_over\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::2_0::produces::step__pilot_rod_assembly__step_03_adjusted_over_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"inserted_in\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_03_inserted_in_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_03_aligned_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::3_0::produces::step__pilot_rod_assembly__step_03_aligned_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_03, place)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_03, 89, 196)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_03, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_03, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_03

Selected retrieval template:
installation_check

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 2 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_02\", \"sleeves_on\", \"sleeve\", \"metal_rod\"], \"condition\": {\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"sleeves_on\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_02::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_02_sleeves_on_sleeve_metal_rod\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_02\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"adjusted_over\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::2_0::produces::step__pilot_rod_assembly__step_03_adjusted_over_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"inserted_in\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_03_inserted_in_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_03_aligned_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::3_0::produces::step__pilot_rod_assembly__step_03_aligned_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_03, place)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_03, 89, 196)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_03, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_03, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "supporting_effect": null
  }
]
```

### Answer

Before placing the O-rings, the sleeves must already be on the metal rod.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_a_dependency_and_prerequisite_checks`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Status: `Runnable now`
- Expected answer elements:
  - identify required sleeves_on(sleeve, metal_rod)
  - identify Step 2 as support
  - explain that Step 3 depends on Step 2

## Case: q04_step_four_readiness

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Before I drive the screws halfway in, what must already be done with the O-rings and sleeves?
- Retrieval template: `installation_check`
- Retrieval template description: `Retrieve requirements, produced effects, and support around the current step.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `21.79 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_04"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::3_0::produces::step__pilot_rod_assembly__step_03_aligned_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_03_aligned_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"adjusted_over\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::2_0::produces::step__pilot_rod_assembly__step_03_adjusted_over_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"inserted_in\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_03_inserted_in_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 5 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_04\", \"partially_inserted_in\", \"screw\", \"rod_holes\"], \"condition\": {\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_04::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_04_partially_inserted_in_screw_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_04\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 6 [uncertain]",
    "evidence_labels": [
      "Step",
      "StepUncertain"
    ],
    "evidence_name": null,
    "evidence_status": "uncertain",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_04\", \"partially_inserted_in\", \"screw\", \"rod_holes\"], \"condition\": {\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_04::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_04_partially_inserted_in_screw_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_04\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires aligned(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires aligned(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_distance": 1,
    "evidence_kind": "required_tool",
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "drive"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_04, drive)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_04\", 196, 376]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_04, 196, 376)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_04, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "supporting_effect": null
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_04

Selected retrieval template:
installation_check

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::3_0::produces::step__pilot_rod_assembly__step_03_aligned_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"aligned\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"aligned\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::1_0::produces::step__pilot_rod_assembly__step_03_aligned_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"adjusted_over\", \"sleeve\", \"o_ring\"], \"condition\": {\"args\": [\"sleeve\", \"o_ring\"], \"name\": \"adjusted_over\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::2_0::produces::step__pilot_rod_assembly__step_03_adjusted_over_sleeve_o_ring\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 3 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_03\", \"inserted_in\", \"o_ring\", \"rod_holes\"], \"condition\": {\"args\": [\"o_ring\", \"rod_holes\"], \"name\": \"inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_03::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_03_inserted_in_o_ring_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_03\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 5 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_04\", \"partially_inserted_in\", \"screw\", \"rod_holes\"], \"condition\": {\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_04::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_04_partially_inserted_in_screw_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_04\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 6 [uncertain]",
    "evidence_labels": [
      "Step",
      "StepUncertain"
    ],
    "evidence_name": null,
    "evidence_status": "uncertain",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_04\", \"partially_inserted_in\", \"screw\", \"rod_holes\"], \"condition\": {\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_04::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_04_partially_inserted_in_screw_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_04\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires aligned(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires aligned(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_distance": 1,
    "evidence_kind": "required_tool",
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "drive"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_04, drive)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_04\", 196, 376]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_04, 196, 376)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_04, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "supporting_effect": null
  }
]
```

### Answer

Before you drive the screws halfway into the holes, the following conditions must be met regarding the O-rings and sleeves:

*   The sleeve and O-ring must be aligned.
*   The sleeve must be adjusted over the O-ring.
*   The O-ring must be inserted into the rod holes.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_a_dependency_and_prerequisite_checks`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Status: `Runnable now`
- Expected answer elements:
  - identify inserted_in(o_ring, rod_holes)
  - identify aligned(o_ring, rod_holes)
  - identify adjusted_over(sleeve, o_ring)
  - identify aligned(sleeve, o_ring)
  - identify Step 3 as support for these requirements

## Case: q05_threadlocker_dependency

- Step id: `step::pilot_rod_assembly::step_05`
- Operator question: Can I apply Loctite now, and what earlier screw state supports that?
- Retrieval template: `installation_check`
- Retrieval template description: `Retrieve requirements, produced effects, and support around the current step.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `17.16 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_05"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_04\", \"partially_inserted_in\", \"screw\", \"rod_holes\"], \"condition\": {\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_04::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_04_partially_inserted_in_screw_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_04\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 6 [uncertain]",
    "evidence_labels": [
      "Step",
      "StepUncertain"
    ],
    "evidence_name": null,
    "evidence_status": "uncertain",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"threadlocker_loctite\", \"screw\"], \"name\": \"applied_to\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_05\", \"applied_to\", \"threadlocker_loctite\", \"screw\"], \"condition\": {\"args\": [\"threadlocker_loctite\", \"screw\"], \"name\": \"applied_to\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_05::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_05_applied_to_threadlocker_loctite_screw\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_05\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "apply"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_05, apply)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_05, applied_to, threadlocker_loctite, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_05, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_05\", 376, 429]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_05, 376, 429)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "threadlocker_loctite"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesMaterial(step_05, threadlocker_loctite)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesMaterial",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_05, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "REQUIRES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 5 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 5 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "rod_holes",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "rod_holes",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "rod_holes",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "threadlocker_loctite",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_05

Selected retrieval template:
installation_check

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 4 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_04\", \"partially_inserted_in\", \"screw\", \"rod_holes\"], \"condition\": {\"args\": [\"screw\", \"rod_holes\"], \"name\": \"partially_inserted_in\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_04::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_04_partially_inserted_in_screw_rod_holes\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_04\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 6 [uncertain]",
    "evidence_labels": [
      "Step",
      "StepUncertain"
    ],
    "evidence_name": null,
    "evidence_status": "uncertain",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"threadlocker_loctite\", \"screw\"], \"name\": \"applied_to\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_05\", \"applied_to\", \"threadlocker_loctite\", \"screw\"], \"condition\": {\"args\": [\"threadlocker_loctite\", \"screw\"], \"name\": \"applied_to\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_05::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_05_applied_to_threadlocker_loctite_screw\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_05\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "apply"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_05, apply)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_05, applied_to, threadlocker_loctite, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_05, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_05\", 376, 429]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_05, 376, 429)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "threadlocker_loctite"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesMaterial(step_05, threadlocker_loctite)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesMaterial",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_05, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "REQUIRES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 5 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 5 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "rod_holes",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "rod_holes",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "rod_holes",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "screw",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "threadlocker_loctite",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Answer

Yes, you can apply Loctite now. This is supported by Step 4, where the screws were driven halfway into all the rod holes.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_a_dependency_and_prerequisite_checks`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Status: `Runnable now`
- Expected answer elements:
  - identify partially_inserted_in(screw, rod_holes)
  - identify Step 4 as the supporting step
  - state that threadlocker is applied to the screw

## Case: q06_next_step_after_cleaning

- Step id: `step::pilot_rod_assembly::step_07`
- Operator question: After cleaning with ethanol and paper, what step comes next and what condition does cleaning support?
- Retrieval template: `installation_check`
- Retrieval template description: `Retrieve requirements, produced effects, and support around the current step.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `18.43 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_07"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 6 [uncertain]",
    "evidence_labels": [
      "Step",
      "StepUncertain"
    ],
    "evidence_name": null,
    "evidence_status": "uncertain",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"secured\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_06\", \"secured\", \"sleeve\", \"metal_rod\"], \"condition\": {\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"secured\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_06::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_06_secured_sleeve_metal_rod\", \"producer_status\": \"uncertain\", \"provisional\": true, \"step_id\": \"step::pilot_rod_assembly::step_06\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 8 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"rod_assembly\", \"ethanol\"], \"name\": \"cleaned_with\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_07\", \"cleaned_with\", \"rod_assembly\", \"ethanol\"], \"condition\": {\"args\": [\"rod_assembly\", \"ethanol\"], \"name\": \"cleaned_with\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_07::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_07_cleaned_with_rod_assembly_ethanol\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_07\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "clean"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_07, clean)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_07, avoided_contact_with, copper_sleeve, paper)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_07, cleaned_with, rod_assembly, ethanol)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_07, secured, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_07\", 531, 566]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_07, 531, 566)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesMaterial(step_07, ethanol)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesMaterial",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesMaterial(step_07, paper)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesMaterial",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "rod_assembly"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_07, rod_assembly)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "REQUIRES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 7 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 7 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 7 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "copper_sleeve",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "copper_sleeve",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "copper_sleeve",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "ethanol",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "ethanol",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "ethanol",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_07

Selected retrieval template:
installation_check

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_ENTITY|HAS_CONSTRAINT|REQUIRES|PRODUCES|DEPENDS_ON|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS rel
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.object_labels AS object_labels,
  s.status AS status,
  type(rel) AS relation,
  rel.required_condition AS required_condition,
  rel.supporting_effect AS supporting_effect,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.kind AS evidence_kind,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 6 [uncertain]",
    "evidence_labels": [
      "Step",
      "StepUncertain"
    ],
    "evidence_name": null,
    "evidence_status": "uncertain",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"secured\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_06\", \"secured\", \"sleeve\", \"metal_rod\"], \"condition\": {\"args\": [\"sleeve\", \"metal_rod\"], \"name\": \"secured\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_06::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_06_secured_sleeve_metal_rod\", \"producer_status\": \"uncertain\", \"provisional\": true, \"step_id\": \"step::pilot_rod_assembly::step_06\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "Step 8 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "required_condition": "{\"args\": [\"rod_assembly\", \"ethanol\"], \"name\": \"cleaned_with\"}",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": "{\"args\": [\"step::pilot_rod_assembly::step_07\", \"cleaned_with\", \"rod_assembly\", \"ethanol\"], \"condition\": {\"args\": [\"rod_assembly\", \"ethanol\"], \"name\": \"cleaned_with\"}, \"constraint_id\": \"step::pilot_rod_assembly::step_07::c::effect_observed_pilot_condition::0_0::produces::step__pilot_rod_assembly__step_07_cleaned_with_rod_assembly_ethanol\", \"producer_status\": \"accepted\", \"provisional\": false, \"step_id\": \"step::pilot_rod_assembly::step_07\", \"type\": \"previous_produced_effect\"}"
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "clean"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasAction(step_07, clean)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_07, avoided_contact_with, copper_sleeve, paper)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasObservedEffect(step_07, cleaned_with, rod_assembly, ethanol)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasRequiredCondition(step_07, secured, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": "[\"step::pilot_rod_assembly::step_07\", 531, 566]",
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "hasTimeWindow(step_07, 531, 566)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesMaterial(step_07, ethanol)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesMaterial",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesMaterial(step_07, paper)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesMaterial",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "rod_assembly"
    ],
    "evidence_distance": 1,
    "evidence_kind": null,
    "evidence_label": "usesObject(step_07, rod_assembly)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "evidence_distance": 1,
    "evidence_kind": "expected_effect",
    "evidence_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "object_labels": null,
    "relation": "PRODUCES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "observed",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_distance": 1,
    "evidence_kind": "inferred_precondition",
    "evidence_label": "requires secured(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "object_labels": null,
    "relation": "REQUIRES",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": "supported",
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 7 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 7 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "Step 7 [accepted]",
    "evidence_labels": [
      "Step",
      "StepAccepted"
    ],
    "evidence_name": null,
    "evidence_status": "accepted",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "copper_sleeve",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "copper_sleeve",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "copper_sleeve",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "ethanol",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "ethanol",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "evidence_args": null,
    "evidence_distance": 2,
    "evidence_kind": null,
    "evidence_label": "ethanol",
    "evidence_labels": [
      "Entity"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "object_labels": null,
    "relation": "HAS_ENTITY",
    "required_condition": null,
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "support_status": null,
    "supporting_effect": null
  }
]
```

### Answer

After cleaning with ethanol and paper (Step 7), the next step is Step 8, which involves applying grease to a sponge and lubricating the silver-colored sleeves while avoiding the copper sleeves.

Cleaning supports the following condition:
*   The rod assembly must be cleaned with ethanol.

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_a_dependency_and_prerequisite_checks`
- Scenario: `scenario_a_dependency_and_prerequisite_checks`
- Status: `Runnable now`
- Expected answer elements:
  - identify Step 8 as the next step
  - identify cleaned_with(rod_assembly, ethanol)
  - state that Step 8 requires the cleaned condition

