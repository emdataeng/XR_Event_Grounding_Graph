# Prompt Report: scenario_b_alignment_and_implicit_conditions

Generated at: 2026-07-04T14:15:55+02:00

- Condition: `query_driven_graph`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Cases in this report: `5`

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
Where should the O-rings be aligned, and is that represented as something achieved in this step?
```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q07_o_ring_alignment_requirement

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: Where should the O-rings be aligned, and is that represented as something achieved in this step?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `18.19 s`

### Cypher Query Executed

```cypher
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
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
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces aligned(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "neighbor_label": "hasAction(step_03, place)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "metal_rod"
    ],
    "neighbor_label": "hasParentComponent(rod_holes, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasParentComponent",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "neighbor_label": "hasTimeWindow(step_03, 89, 196)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "RodHole"
    ],
    "neighbor_label": "isA(rod_holes, RodHole)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "isA",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "neighbor_label": "usesObject(step_03, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "neighbor_label": "usesObject(step_03, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_03

Selected retrieval template:
current_step_context

Cypher query executed:
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces aligned(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "neighbor_label": "hasAction(step_03, place)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "metal_rod"
    ],
    "neighbor_label": "hasParentComponent(rod_holes, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasParentComponent",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "neighbor_label": "hasTimeWindow(step_03, 89, 196)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "RodHole"
    ],
    "neighbor_label": "isA(rod_holes, RodHole)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "isA",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "neighbor_label": "usesObject(step_03, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "neighbor_label": "usesObject(step_03, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  }
]
```

### Answer

The O-rings should be aligned with the rod holes. This is represented as an observed effect achieved in this step.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now`
- Expected answer elements:
  - identify rod_holes as the O-ring installation target
  - state aligned(o_ring, rod_holes)
  - state that Step 3 produces this as manual symbolic annotation

## Case: q08_sleeve_alignment_requirement

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: The sleeve is on the rod, but what should it be aligned with after the O-rings are placed?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `2.61 s`

### Cypher Query Executed

```cypher
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
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
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces aligned(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "neighbor_label": "hasAction(step_03, place)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "metal_rod"
    ],
    "neighbor_label": "hasParentComponent(rod_holes, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasParentComponent",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "neighbor_label": "hasTimeWindow(step_03, 89, 196)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "RodHole"
    ],
    "neighbor_label": "isA(rod_holes, RodHole)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "isA",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "neighbor_label": "usesObject(step_03, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "neighbor_label": "usesObject(step_03, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_03

Selected retrieval template:
current_step_context

Cypher query executed:
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces aligned(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "neighbor_label": "hasAction(step_03, place)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "metal_rod"
    ],
    "neighbor_label": "hasParentComponent(rod_holes, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasParentComponent",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "neighbor_label": "hasTimeWindow(step_03, 89, 196)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "RodHole"
    ],
    "neighbor_label": "isA(rod_holes, RodHole)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "isA",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "neighbor_label": "usesObject(step_03, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "neighbor_label": "usesObject(step_03, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 2 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "action_name": "place",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "produces aligned(o_ring, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_03",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "step_index": 3
  }
]
```

### Answer

After the O-rings are placed, the sleeve should be aligned with the O-ring.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now`
- Expected answer elements:
  - identify o_ring as the sleeve alignment reference
  - state aligned(sleeve, o_ring)
  - explain that this is distinct from the sleeve installation target metal_rod

## Case: q09_screw_alignment_before_tightening

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: Before fully tightening the screws, what screw alignment checks are still not confirmed?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `18.80 s`

### Cypher Query Executed

```cypher
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_06"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 8 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces secured(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "requires aligned(screw, o_ring) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires aligned(screw, rod_holes) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "requires tool(power_screwdriver) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requiresTool",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "neighbor_label": "hasAction(step_06, tighten)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "hasRequiredTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "neighbor_label": "hasTimeWindow(step_06, 429, 531)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "neighbor_label": "usesObject(step_06, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "usesTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_06

Selected retrieval template:
current_step_context

Cypher query executed:
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 8 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces secured(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "requires aligned(screw, o_ring) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires aligned(screw, rod_holes) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "requires tool(power_screwdriver) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requiresTool",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "neighbor_label": "hasAction(step_06, tighten)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "hasRequiredTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "neighbor_label": "hasTimeWindow(step_06, 429, 531)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "neighbor_label": "usesObject(step_06, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "usesTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  }
]
```

### Answer

Before fully tightening the screws, the following screw alignment checks are not confirmed:

*   The screw must be aligned with the O-ring.
*   The screw must be aligned with the rod holes.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now; expected uncertain`
- Expected answer elements:
  - identify aligned(screw, rod_holes)
  - identify aligned(screw, o_ring)
  - state that these are missing or unsupported in the current graph
  - explain that this is why Step 6 is uncertain

## Case: q10_requirement_not_observation

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: The model says the screw must align with the O-ring. Does that mean the graph observed it?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `4.33 s`

### Cypher Query Executed

```cypher
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit
```

### Query Parameters

```json
{
  "graph_name": "procedural_reasoning_graph::pilot_rod_assembly",
  "limit": 25,
  "step_id": "step::pilot_rod_assembly::step_06"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 8 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces secured(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "requires aligned(screw, o_ring) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires aligned(screw, rod_holes) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "requires tool(power_screwdriver) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requiresTool",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "neighbor_label": "hasAction(step_06, tighten)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "hasRequiredTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "neighbor_label": "hasTimeWindow(step_06, 429, 531)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "neighbor_label": "usesObject(step_06, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "usesTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_06

Selected retrieval template:
current_step_context

Cypher query executed:
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 4 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 8 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces secured(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "requires aligned(screw, o_ring) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires aligned(screw, rod_holes) [missing]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "requires tool(power_screwdriver) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requiresTool",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "neighbor_label": "hasAction(step_06, tighten)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "hasRequiredTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "neighbor_label": "hasTimeWindow(step_06, 429, 531)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "neighbor_label": "usesObject(step_06, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "neighbor_label": "usesTool(step_06, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 7 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "action_name": "tighten",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "neighbor_label": "produces flush_with(screw, sleeve) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_06",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "step_index": 6
  }
]
```

### Answer

No, the graph does not show that the screw is aligned with the O-ring. While the system identifies that the screw must be aligned with the O-ring as a required condition for this step, this specific condition is currently listed as missing.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now; expected uncertain`
- Expected answer elements:
  - answer no
  - distinguish required condition from observed effect
  - identify pilot_domain_default as requirement provenance
  - avoid treating configured requirement as evidence

## Case: q11_rod_holes_belong_to_rod

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: When the instruction says all holes, are those holes modeled as part of the rod or as separate components?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `16.60 s`

### Cypher Query Executed

```cypher
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
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
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 6 [uncertain]",
    "neighbor_labels": [
      "Step",
      "StepUncertain"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "requires aligned(o_ring, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "requires aligned(sleeve, o_ring) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "neighbor_label": "requires tool(power_screwdriver) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requiresTool",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "drive"
    ],
    "neighbor_label": "hasAction(step_04, drive)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "metal_rod"
    ],
    "neighbor_label": "hasParentComponent(rod_holes, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasParentComponent",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, aligned, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, aligned, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "neighbor_label": "hasRequiredTool(step_04, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_04\", 196, 376]",
    "neighbor_label": "hasTimeWindow(step_04, 196, 376)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "RodHole"
    ],
    "neighbor_label": "isA(rod_holes, RodHole)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "isA",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "screw"
    ],
    "neighbor_label": "usesObject(step_04, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "neighbor_label": "usesTool(step_04, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_04

Selected retrieval template:
current_step_context

Cypher query executed:
OPTIONAL MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  $step_id AS requested_step_id,
  s IS NOT NULL AS current_step_found,
  s.step_id AS step_id,
  s.index AS step_index,
  s.action_description AS action_description,
  s.action_name AS action_name,
  s.object_labels AS object_labels,
  s.status AS status,
  s.confidence AS confidence,
  type(r) AS relation,
  labels(n) AS neighbor_labels,
  n.display_label AS neighbor_label,
  n.name AS neighbor_name,
  n.args AS neighbor_args,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, neighbor_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 5 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 6 [uncertain]",
    "neighbor_labels": [
      "Step",
      "StepUncertain"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "requires aligned(o_ring, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "requires aligned(sleeve, o_ring) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "neighbor_label": "requires tool(power_screwdriver) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requiresTool",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "drive"
    ],
    "neighbor_label": "hasAction(step_04, drive)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "metal_rod"
    ],
    "neighbor_label": "hasParentComponent(rod_holes, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasParentComponent",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, aligned, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, aligned, sleeve, o_ring)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "neighbor_label": "hasRequiredTool(step_04, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_04\", 196, 376]",
    "neighbor_label": "hasTimeWindow(step_04, 196, 376)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "rod_holes",
      "RodHole"
    ],
    "neighbor_label": "isA(rod_holes, RodHole)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "isA",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "screw"
    ],
    "neighbor_label": "usesObject(step_04, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "neighbor_label": "usesTool(step_04, power_screwdriver)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "action_name": "drive",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 3 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_04",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "step_index": 4
  }
]
```

### Answer

The rod holes are modeled as part of the metal rod.

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_b_alignment_and_implicit_conditions`
- Scenario: `scenario_b_alignment_and_implicit_conditions`
- Status: `Runnable now`
- Expected answer elements:
  - identify rod_holes
  - state that rod_holes are modeled as RodHole or RodFeature
  - state hasParentComponent(rod_holes, metal_rod)
  - avoid calling rod_holes an installable component

