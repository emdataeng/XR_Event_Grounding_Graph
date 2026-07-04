# Prompt Report: scenario_c_tools_materials_counts_and_orientation

Generated at: 2026-07-04T14:15:55+02:00

- Condition: `query_driven_graph`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
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
Which tool do I need to drive the screws halfway in, and is its use observed or only required?
```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q12_power_screwdriver_step_four

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Which tool do I need to drive the screws halfway in, and is its use observed or only required?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `2.86 s`

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

You need a power screwdriver to drive the screws halfway into all holes. Its use is both required and observed.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify power_screwdriver
  - state that Step 4 has usesTool(power_screwdriver)
  - state that Step 4 also has a requiresTool condition
  - distinguish observed tool use from required tool

## Case: q13_power_screwdriver_step_six

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: For fully tightening the screws, is the required power screwdriver confirmed, or is the uncertainty caused by something else?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `3.67 s`

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

The requirement for a power screwdriver is confirmed for this step. The uncertainty noted in the system is not related to the tool, but rather to the status of the step itself.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now; step uncertain for non-tool reasons`
- Expected answer elements:
  - identify power_screwdriver as required and observed
  - state that tool support is present
  - state that uncertainty comes from missing screw alignment support

## Case: q14_threadlocker_material

- Step id: `step::pilot_rod_assembly::step_05`
- Operator question: What material is applied to the screws before final tightening, and what condition does it produce?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `17.10 s`

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
  "step_id": "step::pilot_rod_assembly::step_05"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "apply"
    ],
    "neighbor_label": "hasAction(step_05, apply)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "hasObservedEffect(step_05, applied_to, threadlocker_loctite, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_05, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_05\", 376, 429]",
    "neighbor_label": "hasTimeWindow(step_05, 376, 429)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "threadlocker_loctite"
    ],
    "neighbor_label": "usesMaterial(step_05, threadlocker_loctite)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "screw"
    ],
    "neighbor_label": "usesObject(step_05, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
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
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "screw",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "precondition_required_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "precondition_required_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_05

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
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "apply"
    ],
    "neighbor_label": "hasAction(step_05, apply)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "hasObservedEffect(step_05, applied_to, threadlocker_loctite, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "neighbor_label": "hasRequiredCondition(step_05, partially_inserted_in, screw, rod_holes)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_05\", 376, 429]",
    "neighbor_label": "hasTimeWindow(step_05, 376, 429)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "threadlocker_loctite"
    ],
    "neighbor_label": "usesMaterial(step_05, threadlocker_loctite)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "screw"
    ],
    "neighbor_label": "usesObject(step_05, screw)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
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
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "neighbor_label": "produces applied_to(threadlocker_loctite, screw) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_05",
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
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "screw",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "precondition_required_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  },
  {
    "action_description": "The operator applies threadlocker (Loctite) to all partially inserted screws.",
    "action_name": "apply",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "precondition_required_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_05",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_05",
    "step_index": 5
  }
]
```

### Answer

The operator applies threadlocker (Loctite) to the screws. This produces the application of threadlocker (Loctite) to the screws.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify threadlocker_loctite
  - identify applied_to(threadlocker_loctite, screw)
  - state that Step 6 requires this effect

## Case: q15_sleeve_count_and_orientation

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: What count and orientation checks are represented for the sleeves?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `20.24 s`

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
  "step_id": "step::pilot_rod_assembly::step_02"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 1 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
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
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "neighbor_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "neighbor_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "neighbor_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "neighbor_label": "requires secured(metal_rod, workbench) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "slide"
    ],
    "neighbor_label": "hasAction(step_02, slide)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "neighbor_label": "hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "neighbor_label": "hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "neighbor_label": "hasObservedEffect(step_02, oriented, copper_sleeve, right_side)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "neighbor_label": "hasRequiredCondition(step_02, secured, metal_rod, workbench)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_02\", 15, 89]",
    "neighbor_label": "hasTimeWindow(step_02, 15, 89)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "copper_sleeve"
    ],
    "neighbor_label": "usesObject(step_02, copper_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "long_sleeve"
    ],
    "neighbor_label": "usesObject(step_02, long_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "metal_rod"
    ],
    "neighbor_label": "usesObject(step_02, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "short_sleeve"
    ],
    "neighbor_label": "usesObject(step_02, short_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeve"
    ],
    "neighbor_label": "usesObject(step_02, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 1 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
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
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "neighbor_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "neighbor_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "neighbor_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_02

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
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 1 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DEPENDS_ON",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
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
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "neighbor_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "neighbor_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "neighbor_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "neighbor_label": "requires secured(metal_rod, workbench) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "slide"
    ],
    "neighbor_label": "hasAction(step_02, slide)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "neighbor_label": "hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "neighbor_label": "hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "neighbor_label": "hasObservedEffect(step_02, oriented, copper_sleeve, right_side)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "neighbor_label": "hasRequiredCondition(step_02, secured, metal_rod, workbench)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_02\", 15, 89]",
    "neighbor_label": "hasTimeWindow(step_02, 15, 89)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "copper_sleeve"
    ],
    "neighbor_label": "usesObject(step_02, copper_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "long_sleeve"
    ],
    "neighbor_label": "usesObject(step_02, long_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "metal_rod"
    ],
    "neighbor_label": "usesObject(step_02, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "short_sleeve"
    ],
    "neighbor_label": "usesObject(step_02, short_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeve"
    ],
    "neighbor_label": "usesObject(step_02, sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "Step 1 [accepted]",
    "neighbor_labels": [
      "Step",
      "StepAccepted"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
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
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "neighbor_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "neighbor_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "neighbor_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "action_name": "slide",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_02",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "step_index": 2
  }
]
```

### Answer

For the sleeves, the following checks are represented:

*   **Count checks:**
    *   Verify that there are six copper sleeves.
    *   Verify that there are five long sleeves.
*   **Orientation check:**
    *   The copper sleeve must be oriented to the right side.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify count_verified(copper_sleeve, required_quantity_six)
  - identify count_verified(long_sleeve, required_quantity_five)
  - identify oriented(copper_sleeve, right_side)
  - avoid claiming individual sleeve instance tracking

## Case: q16_cleaning_materials

- Step id: `step::pilot_rod_assembly::step_07`
- Operator question: What should I clean with, and what should I avoid doing to the copper sleeve?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `16.91 s`

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
  "step_id": "step::pilot_rod_assembly::step_07"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "clean"
    ],
    "neighbor_label": "hasAction(step_07, clean)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "neighbor_label": "hasObservedEffect(step_07, avoided_contact_with, copper_sleeve, paper)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "hasObservedEffect(step_07, cleaned_with, rod_assembly, ethanol)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_07, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_07\", 531, 566]",
    "neighbor_label": "hasTimeWindow(step_07, 531, 566)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "ethanol"
    ],
    "neighbor_label": "usesMaterial(step_07, ethanol)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "paper"
    ],
    "neighbor_label": "usesMaterial(step_07, paper)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "rod_assembly"
    ],
    "neighbor_label": "usesObject(step_07, rod_assembly)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "rod_assembly",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_07

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
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "clean"
    ],
    "neighbor_label": "hasAction(step_07, clean)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "neighbor_label": "hasObservedEffect(step_07, avoided_contact_with, copper_sleeve, paper)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "hasObservedEffect(step_07, cleaned_with, rod_assembly, ethanol)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_07, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_07\", 531, 566]",
    "neighbor_label": "hasTimeWindow(step_07, 531, 566)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "ethanol"
    ],
    "neighbor_label": "usesMaterial(step_07, ethanol)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "paper"
    ],
    "neighbor_label": "usesMaterial(step_07, paper)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "rod_assembly"
    ],
    "neighbor_label": "usesObject(step_07, rod_assembly)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
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
    "relation": "NEXT",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "avoided_contact_with",
      "copper_sleeve",
      "paper"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, paper) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "produces cleaned_with(rod_assembly, ethanol) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_07",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "rod_assembly",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  },
  {
    "action_description": "The operator cleans the rod and sleeves with ethanol and paper.",
    "action_name": "clean",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "manual_symbolic_annotation:rod_assembly_steps.json",
    "neighbor_labels": [
      "Source"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_07",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_07",
    "step_index": 7
  }
]
```

### Answer

You should clean the rod and sleeves with ethanol and paper. When cleaning, avoid contact with the copper sleeve to ensure it is not polished.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify ethanol and paper
  - identify cleaned_with(rod_assembly, ethanol)
  - identify avoided_contact_with(copper_sleeve, paper)
  - explain that the procedure says not to polish the copper part

## Case: q17_grease_application

- Step id: `step::pilot_rod_assembly::step_08`
- Operator question: Which sleeves get grease, what tool is used, and what should not get grease?
- Retrieval template: `current_step_context`
- Retrieval template description: `Retrieve the current step and direct graph evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `18.89 s`

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
  "step_id": "step::pilot_rod_assembly::step_08"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
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
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
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
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "avoided_contact_with",
      "copper_sleeve",
      "grease"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricated_with",
      "silver_sleeve",
      "grease"
    ],
    "neighbor_label": "produces lubricated_with(silver_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "requires cleaned_with(rod_assembly, ethanol) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricate"
    ],
    "neighbor_label": "hasAction(step_08, lubricate)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "avoided_contact_with",
      "copper_sleeve",
      "grease"
    ],
    "neighbor_label": "hasObservedEffect(step_08, avoided_contact_with, copper_sleeve, grease)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricated_with",
      "silver_sleeve",
      "grease"
    ],
    "neighbor_label": "hasObservedEffect(step_08, lubricated_with, silver_sleeve, grease)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "hasRequiredCondition(step_08, cleaned_with, rod_assembly, ethanol)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_08, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_08\", 566, 642]",
    "neighbor_label": "hasTimeWindow(step_08, 566, 642)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "grease"
    ],
    "neighbor_label": "usesMaterial(step_08, grease)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "silver_sleeve"
    ],
    "neighbor_label": "usesObject(step_08, silver_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "sponge"
    ],
    "neighbor_label": "usesTool(step_08, sponge)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
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
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "avoided_contact_with",
      "copper_sleeve",
      "grease"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricated_with",
      "silver_sleeve",
      "grease"
    ],
    "neighbor_label": "produces lubricated_with(silver_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "requires cleaned_with(rod_assembly, ethanol) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "silver_sleeve",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "sponge",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_08

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
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
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
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
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
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "avoided_contact_with",
      "copper_sleeve",
      "grease"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricated_with",
      "silver_sleeve",
      "grease"
    ],
    "neighbor_label": "produces lubricated_with(silver_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "requires cleaned_with(rod_assembly, ethanol) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "HAS_CONSTRAINT",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricate"
    ],
    "neighbor_label": "hasAction(step_08, lubricate)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasAction",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "avoided_contact_with",
      "copper_sleeve",
      "grease"
    ],
    "neighbor_label": "hasObservedEffect(step_08, avoided_contact_with, copper_sleeve, grease)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricated_with",
      "silver_sleeve",
      "grease"
    ],
    "neighbor_label": "hasObservedEffect(step_08, lubricated_with, silver_sleeve, grease)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasObservedEffect",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "hasRequiredCondition(step_08, cleaned_with, rod_assembly, ethanol)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "hasRequiredCondition(step_08, secured, sleeve, metal_rod)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasRequiredCondition",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": "[\"step::pilot_rod_assembly::step_08\", 566, 642]",
    "neighbor_label": "hasTimeWindow(step_08, 566, 642)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "hasTimeWindow",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "grease"
    ],
    "neighbor_label": "usesMaterial(step_08, grease)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesMaterial",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "silver_sleeve"
    ],
    "neighbor_label": "usesObject(step_08, silver_sleeve)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesObject",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "sponge"
    ],
    "neighbor_label": "usesTool(step_08, sponge)",
    "neighbor_labels": [
      "Predicate"
    ],
    "neighbor_name": "usesTool",
    "object_labels": null,
    "relation": "HAS_PREDICATE",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
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
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "avoided_contact_with",
      "copper_sleeve",
      "grease"
    ],
    "neighbor_label": "produces avoided_contact_with(copper_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "lubricated_with",
      "silver_sleeve",
      "grease"
    ],
    "neighbor_label": "produces lubricated_with(silver_sleeve, grease) [observed]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "produces",
    "object_labels": null,
    "relation": "PRODUCES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "cleaned_with",
      "rod_assembly",
      "ethanol"
    ],
    "neighbor_label": "requires cleaned_with(rod_assembly, ethanol) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": [
      "step::pilot_rod_assembly::step_08",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "neighbor_label": "requires secured(sleeve, metal_rod) [supported]",
    "neighbor_labels": [
      "Constraint"
    ],
    "neighbor_name": "requires",
    "object_labels": null,
    "relation": "REQUIRES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "silver_sleeve",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 1,
    "neighbor_args": null,
    "neighbor_label": "sponge",
    "neighbor_labels": [
      "Entity"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "USES",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  },
  {
    "action_description": "The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves.",
    "action_name": "lubricate",
    "confidence": 1.0,
    "current_step_found": true,
    "evidence_distance": 2,
    "neighbor_args": null,
    "neighbor_label": "effect_observed_pilot_condition",
    "neighbor_labels": [
      "Rule"
    ],
    "neighbor_name": null,
    "object_labels": null,
    "relation": "DERIVED_FROM",
    "requested_step_id": "step::pilot_rod_assembly::step_08",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_08",
    "step_index": 8
  }
]
```

### Answer

The silver-colored sleeves should be lubricated with grease, and you should use a sponge to apply it. Do not get grease on the copper sleeves.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_c_tools_materials_counts_and_orientation`
- Scenario: `scenario_c_tools_materials_counts_and_orientation`
- Status: `Runnable now`
- Expected answer elements:
  - identify silver_sleeve
  - identify sponge
  - identify grease
  - identify avoided_contact_with(copper_sleeve, grease)

