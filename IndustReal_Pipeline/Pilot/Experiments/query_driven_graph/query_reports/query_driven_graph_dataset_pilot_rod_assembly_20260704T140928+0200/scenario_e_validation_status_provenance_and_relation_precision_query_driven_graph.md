# Prompt Report: scenario_e_validation_status_provenance_and_relation_precision

Generated at: 2026-07-04T14:15:55+02:00

- Condition: `query_driven_graph`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
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
Why is the final tightening step uncertain even though the threadlocker and power screwdriver are present?
```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q22_why_step_six_uncertain

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: Why is the final tightening step uncertain even though the threadlocker and power screwdriver are present?
- Retrieval template: `evidence_confidence`
- Retrieval template description: `Retrieve confidence, status, warnings, and source/provenance evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `20.82 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
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
  "step_id": "step::pilot_rod_assembly::step_06"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_06, tighten)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_06, 429, 531)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_06, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_06

Selected retrieval template:
evidence_confidence

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_06, tighten)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_06, 429, 531)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_06, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  }
]
```

### Answer

The final tightening step is uncertain because the following required conditions have not been met:

*   The screws are not aligned with the O-rings.
*   The screws are not aligned with the rod holes.

While the use of a power screwdriver and the application of threadlocker to the screws are supported, these alignment issues must be addressed.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - identify supported applied_to(threadlocker_loctite, screw)
  - identify supported partially_inserted_in(screw, rod_holes)
  - identify supported required tool power_screwdriver
  - identify missing aligned(screw, rod_holes) and aligned(screw, o_ring)

## Case: q23_expert_annotation_provenance

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: The sleeve step depends on the rod being secured. Was that direct step text, a domain requirement, or an expert assumption?
- Retrieval template: `evidence_confidence`
- Retrieval template description: `Retrieve confidence, status, warnings, and source/provenance evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `17.38 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
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
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "slide"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_02, slide)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, oriented, copper_sleeve, right_side)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_02, secured, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_02\", 15, 89]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_02, 15, 89)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "copper_sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, copper_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "long_sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, long_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "short_sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, short_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_02

Selected retrieval template:
evidence_confidence

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "slide"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_02, slide)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, oriented, copper_sleeve, right_side)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_02, secured, metal_rod, workbench)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_02\", 15, 89]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_02, 15, 89)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "copper_sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, copper_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "long_sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, long_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "short_sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, short_sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_02, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "copper_sleeve",
      "required_quantity_six"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(copper_sleeve, required_quantity_six) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "count_verified",
      "long_sleeve",
      "required_quantity_five"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces count_verified(long_sleeve, required_quantity_five) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "oriented",
      "copper_sleeve",
      "right_side"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces oriented(copper_sleeve, right_side) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces sleeves_on(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_02",
      "secured",
      "metal_rod",
      "workbench"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires secured(metal_rod, workbench) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator slides a combination of long, short and copper sleeves onto the rod.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_02",
    "support_status": null,
    "warning_count": 0
  }
]
```

### Answer

The requirement that the metal rod must be secured to the workbench is a domain requirement.

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - state that Step 2 requires secured(metal_rod, workbench) from pilot_domain_default
  - state that Step 1 produces secured(metal_rod, workbench) as manual_expert_annotation
  - distinguish this from direct text evidence on(metal_rod, workbench)

## Case: q24_relation_precision_targets

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: What is the screw installed into, what does it need to align with, and what does it eventually secure?
- Retrieval template: `evidence_confidence`
- Retrieval template description: `Retrieve confidence, status, warnings, and source/provenance evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `4.62 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
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
  "step_id": "step::pilot_rod_assembly::step_06"
}
```

### Neo4j Query Result Sent To The LLM

```json
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_06, tighten)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_06, 429, 531)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_06, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_06

Selected retrieval template:
evidence_confidence

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "tighten"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_06, tighten)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, flush_with, screw, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_06, secured, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, aligned, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_06\", 429, 531]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_06, 429, 531)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_06, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesTool(step_06, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "flush_with",
      "screw",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces flush_with(screw, sleeve) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "secured",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces secured(sleeve, metal_rod) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, o_ring) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "aligned",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(screw, rod_holes) [missing]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "missing",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "applied_to",
      "threadlocker_loctite",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires applied_to(threadlocker_loctite, screw) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires partially_inserted_in(screw, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator fully tightens all screws to secure the sleeves.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_06",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "uncertain",
    "step_id": "step::pilot_rod_assembly::step_06",
    "support_status": "supported",
    "warning_count": 0
  }
]
```

### Answer

The screw is partially inserted into the rod holes. It needs to be aligned with the O-ring and the rod holes. Once fully tightened, the screw secures the sleeve to the metal rod.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - installation target is rod_holes
  - alignment requirements are rod_holes and o_ring
  - final secured relation is secured(sleeve, metal_rod)
  - avoid conflating screw target with sleeve secured target

## Case: q25_why_step_three_accepted

- Step id: `step::pilot_rod_assembly::step_03`
- Operator question: Why is the O-ring placement step accepted? What earlier step makes it valid?
- Retrieval template: `evidence_confidence`
- Retrieval template description: `Retrieve confidence, status, warnings, and source/provenance evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `21.80 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
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
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_03, place)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_03, 89, 196)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_03, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_03, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_03

Selected retrieval template:
evidence_confidence

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "place"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_03, place)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_03, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_03, sleeves_on, sleeve, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_03\", 89, 196]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_03, 89, 196)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_03, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeve"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_03, sleeve)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces adjusted_over(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces aligned(sleeve, o_ring) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces inserted_in(o_ring, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_03",
      "sleeves_on",
      "sleeve",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires sleeves_on(sleeve, metal_rod) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator places O-rings in the holes on the rod and adjusts the sleeves over them.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_03",
    "support_status": null,
    "warning_count": 0
  }
]
```

### Answer

The O-ring placement step is accepted because the following conditions have been observed:
*   The O-rings are inserted in the rod holes.
*   The O-rings are aligned with the rod holes.
*   The O-rings are aligned with the sleeves.
*   The sleeves are adjusted over the O-rings.

This step is valid because the sleeves are already on the metal rod, which is a required condition.

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - identify required sleeves_on(sleeve, metal_rod)
  - identify Step 2 as support
  - identify Step 3 produced effects for O-ring insertion/alignment and sleeve adjustment/alignment

## Case: q26_domain_default_not_fake_observation

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Some requirements come from the domain model. How can I tell whether they were actually observed?
- Retrieval template: `evidence_confidence`
- Retrieval template description: `Retrieve confidence, status, warnings, and source/provenance evidence.`
- Query status: `ok`
- LLM status: `ok`
- Interaction duration: `21.37 s`

### Cypher Query Executed

```cypher
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
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
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "drive"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_04, drive)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_04\", 196, 376]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_04, 196, 376)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_04, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  }
]
```

### Actual User Message Sent

- Role: `user`

```text
Current step id:
step::pilot_rod_assembly::step_04

Selected retrieval template:
evidence_confidence

Cypher query executed:
MATCH (s:Step {graph_name: $graph_name})
WHERE s.step_id = $step_id
OPTIONAL MATCH path = (s)-[:HAS_PREDICATE|HAS_CONSTRAINT|REQUIRES|PRODUCES|DERIVED_FROM|SUPPORTED_BY*0..2]-(n)
WHERE length(path) > 0
  AND all(intermediate IN nodes(path)[1..-1]
          WHERE intermediate:Predicate OR intermediate:Constraint)
WITH s, n, path, last(relationships(path)) AS r
RETURN
  s.step_id AS step_id,
  s.action_description AS action_description,
  s.status AS status,
  s.confidence AS confidence,
  s.warning_count AS warning_count,
  s.has_rule_coverage AS has_rule_coverage,
  s.has_expected_effect AS has_expected_effect,
  type(r) AS relation,
  labels(n) AS evidence_labels,
  n.display_label AS evidence_label,
  n.name AS evidence_name,
  n.args AS evidence_args,
  n.confidence AS evidence_confidence,
  n.status AS evidence_status,
  n.support_status AS support_status,
  length(path) AS evidence_distance
ORDER BY evidence_distance, relation, evidence_label
LIMIT $limit

Neo4j query result:
[
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_CONSTRAINT",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "drive"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasAction(step_04, drive)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasAction",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasObservedEffect",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "metal_rod"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasParentComponent(rod_holes, metal_rod)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasParentComponent",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, aligned, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, aligned, sleeve, o_ring)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredCondition",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasRequiredTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasRequiredTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": "[\"step::pilot_rod_assembly::step_04\", 196, 376]",
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "hasTimeWindow(step_04, 196, 376)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "hasTimeWindow",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "rod_holes",
      "RodHole"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "isA(rod_holes, RodHole)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "isA",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "screw"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesObject(step_04, screw)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesObject",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "usesTool(step_04, power_screwdriver)",
    "evidence_labels": [
      "Predicate"
    ],
    "evidence_name": "usesTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "HAS_PREDICATE",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "partially_inserted_in",
      "screw",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "produces partially_inserted_in(screw, rod_holes) [observed]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "produces",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "PRODUCES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "observed",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "adjusted_over",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires adjusted_over(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "aligned",
      "sleeve",
      "o_ring"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires aligned(sleeve, o_ring) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "inserted_in",
      "o_ring",
      "rod_holes"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires inserted_in(o_ring, rod_holes) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requires",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": [
      "step::pilot_rod_assembly::step_04",
      "power_screwdriver"
    ],
    "evidence_confidence": 1.0,
    "evidence_distance": 1,
    "evidence_label": "requires tool(power_screwdriver) [supported]",
    "evidence_labels": [
      "Constraint"
    ],
    "evidence_name": "requiresTool",
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "REQUIRES",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": "supported",
    "warning_count": 0
  },
  {
    "action_description": "The operator drives the screws halfway into all holes using a power screwdriver.",
    "confidence": 1.0,
    "evidence_args": null,
    "evidence_confidence": null,
    "evidence_distance": 2,
    "evidence_label": "effect_observed_pilot_condition",
    "evidence_labels": [
      "Rule"
    ],
    "evidence_name": null,
    "evidence_status": null,
    "has_expected_effect": true,
    "has_rule_coverage": true,
    "relation": "DERIVED_FROM",
    "status": "accepted",
    "step_id": "step::pilot_rod_assembly::step_04",
    "support_status": null,
    "warning_count": 0
  }
]
```

### Answer

To determine if a requirement was actually observed, you can look at the "support status" of the evidence. 

In the provided data, requirements (constraints) are labeled as either "supported" or "observed." For example, the requirement that the sleeve must be adjusted over the O-ring is listed as "supported," whereas the effect of the screws being partially inserted into the rod holes is listed as "observed."

(EOR)

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_e_validation_status_provenance_and_relation_precision`
- Scenario: `scenario_e_validation_status_provenance_and_relation_precision`
- Status: `Runnable now`
- Expected answer elements:
  - use provenance to distinguish pilot_domain_default from manual_symbolic_annotation
  - check SUPPORTED_BY or produced effects
  - explain that requirements are not observations by themselves

