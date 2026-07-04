# Prompt Report: scenario_f_missing_evidence_controls

Generated at: 2026-07-04T14:06:37+02:00

- Condition: `graph_grounded`
- Scenario: `scenario_f_missing_evidence_controls`
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
- Minimum prompt time: `2.50 s`
- Maximum prompt time: `14.09 s`
- Average prompt time: `5.75 s`
- Total experiment time: `00h 02m 58.53s`

## Question Set

- Path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\experiments\shared\configs\novice_questions_v1_pilot_rod_assembly.yaml`
- ID: `novice_questions_pilot_rod_assembly`
- Version: `v1`
- Case count: `31`
- SHA-256: `60a2ed6fae1d`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `Pilot\rod_assembly_step_list.txt`
- Step-list artifact loaded: `True`
- Windowed predicates included: `no`
- Sequence step-hop radius: `1`
- Semantic evidence-hop radius: `2`
- Thesis rules included: `no`
- Procedural reasoning graph included: `yes`

All conditions include the same frozen step-list artifact. The `symbolic_domain` condition adds a deterministic predicate window and `thesis_rules.yaml`; `graph_grounded` adds a deterministic local graph neighborhood.

## Graph Provenance

- Graph path: `D:\Code\XR_Event_Grounding_Graph\IndustReal_Pipeline\Pilot\procedural_reasoning_graph\procedural_reasoning_graph.json`
- Graph name: `procedural_reasoning_graph::pilot_rod_assembly`
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

This block is inserted into the user message for every case.

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

```



## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: q27_unknown_step

- Step id: `step::pilot_rod_assembly::step_99`
- Operator question: I cannot find this step in the rod assembly. What should I do next?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `0`
- Selected edges: `0`

#### Nodes By Type

| Node type | Count |
|---|---:|
| None | 0 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| None | 0 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
No procedural reasoning graph evidence was found for this step.
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that the step is absent
  - request a valid step id or procedure context
  - avoid fabricating a step

## Case: q28_unmodeled_torque

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: What torque should I use when fully tightening the screws?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `39`
- Selected edges: `83`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 11 |
| Entity | 7 |
| Predicate | 11 |
| Rule | 3 |
| Source | 2 |
| Step | 5 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 4 |
| DERIVED_FROM | 18 |
| HAS_CONSTRAINT | 7 |
| HAS_ENTITY | 28 |
| HAS_PREDICATE | 11 |
| NEXT | 2 |
| PRODUCES | 2 |
| REQUIRES | 5 |
| SUPPORTED_BY | 4 |
| USES | 2 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (39 nodes, 83 edges):
Nodes:
- N1 [Constraint] produces partially_inserted_in(screw, rod_holes) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_04","partially_inserted_in","screw","rod_holes"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N2 [Constraint] produces applied_to(threadlocker_loctite, screw) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_05","applied_to","threadlocker_loctite","screw"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N3 [Constraint] produces secured(sleeve, metal_rod) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_06","secured","sleeve","metal_rod"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N4 [Constraint] produces flush_with(screw, sleeve) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_06","flush_with","screw","sleeve"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N5 [Constraint] requires applied_to(threadlocker_loctite, screw) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","applied_to","threadlocker_loctite","screw"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N6 [Constraint] requires partially_inserted_in(screw, rod_holes) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N7 [Constraint] requires aligned(screw, rod_holes) [missing]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","aligned","screw","rod_holes"]; support_status="missing"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N8 [Constraint] requires aligned(screw, o_ring) [missing]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","aligned","screw","o_ring"]; support_status="missing"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N9 [Constraint] requires tool(power_screwdriver) [supported]; kind="required_tool"; name="requiresTool"; args=["step::pilot_rod_assembly::step_06","power_screwdriver"]; support_status="supported"; rule_id="tool_required_by_pilot_step"; confidence=1.0
- N10 [Constraint] requires secured(sleeve, metal_rod) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_07","secured","sleeve","metal_rod"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N11 [Constraint] requires secured(sleeve, metal_rod) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_08","secured","sleeve","metal_rod"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N12 [Entity] metal_rod
- N13 [Entity] o_ring
- N14 [Entity] power_screwdriver
- N15 [Entity] rod_holes
- N16 [Entity] screw
- N17 [Entity] sleeve
- N18 [Entity] threadlocker_loctite
- N19 [Predicate] hasAction(step_06, tighten); name="hasAction"; args=["step::pilot_rod_assembly::step_06","tighten"]; confidence=1.0
- N20 [Predicate] hasObservedEffect(step_06, flush_with, screw, sleeve); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_06","flush_with","screw","sleeve"]; confidence=1.0
- N21 [Predicate] hasObservedEffect(step_06, secured, sleeve, metal_rod); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_06","secured","sleeve","metal_rod"]; confidence=1.0
- N22 [Predicate] usesObject(step_06, screw); name="usesObject"; args=["step::pilot_rod_assembly::step_06","screw"]; confidence=1.0
- N23 [Predicate] hasRequiredTool(step_06, power_screwdriver); name="hasRequiredTool"; args=["step::pilot_rod_assembly::step_06","power_screwdriver"]; confidence=1.0
- N24 [Predicate] hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"]; confidence=1.0
- N25 [Predicate] hasRequiredCondition(step_06, aligned, screw, o_ring); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","aligned","screw","o_ring"]; confidence=1.0
- N26 [Predicate] hasRequiredCondition(step_06, aligned, screw, rod_holes); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","aligned","screw","rod_holes"]; confidence=1.0
- N27 [Predicate] hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","applied_to","threadlocker_loctite","screw"]; confidence=1.0
- N28 [Predicate] hasTimeWindow(step_06, 429, 531); name="hasTimeWindow"; args=["step::pilot_rod_assembly::step_06",429,531]; confidence=1.0
- N29 [Predicate] usesTool(step_06, power_screwdriver); name="usesTool"; args=["step::pilot_rod_assembly::step_06","power_screwdriver"]; confidence=1.0
- N30 [Rule] effect_observed_pilot_condition; rule_id="effect_observed_pilot_condition"
- N31 [Rule] precondition_required_pilot_condition; rule_id="precondition_required_pilot_condition"
- N32 [Rule] tool_required_by_pilot_step; rule_id="tool_required_by_pilot_step"
- N33 [Source] pilot_domain_default:domain_config_pilot.yaml
- N34 [Source] manual_symbolic_annotation:rod_assembly_steps.json
- N35 [Step] Step 4 [accepted]; step_id="step::pilot_rod_assembly::step_04"; action_description="The operator drives the screws halfway into all holes using a power screwdriver."; status="accepted"; confidence=1.0; warning_count=0
- N36 [Step] Step 5 [accepted]; step_id="step::pilot_rod_assembly::step_05"; action_description="The operator applies threadlocker (Loctite) to all partially inserted screws."; status="accepted"; confidence=1.0; warning_count=0
- N37 [Step] [CURRENT] Step 6 [uncertain]; step_id="step::pilot_rod_assembly::step_06"; action_description="The operator fully tightens all screws to secure the sleeves."; status="uncertain"; confidence=1.0; warning_count=0
- N38 [Step] Step 7 [accepted]; step_id="step::pilot_rod_assembly::step_07"; action_description="The operator cleans the rod and sleeves with ethanol and paper."; status="accepted"; confidence=1.0; warning_count=0
- N39 [Step] Step 8 [accepted]; step_id="step::pilot_rod_assembly::step_08"; action_description="The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves."; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N37<Step:step::pilot_rod_assembly::step_06> -[DEPENDS_ON]-> N35<Step:step::pilot_rod_assembly::step_04>; required_condition={"args":["screw","rod_holes"],"name":"partially_inserted_in"}; supporting_effect={"condition":{"args":["screw","rod_holes"],"name":"partially_inserted_in"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_04","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N37<Step:step::pilot_rod_assembly::step_06> -[DEPENDS_ON]-> N36<Step:step::pilot_rod_assembly::step_05>; required_condition={"args":["threadlocker_loctite","screw"],"name":"applied_to"}; supporting_effect={"condition":{"args":["threadlocker_loctite","screw"],"name":"applied_to"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_05","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N38<Step:step::pilot_rod_assembly::step_07> -[DEPENDS_ON]-> N37<Step:step::pilot_rod_assembly::step_06>; required_condition={"args":["sleeve","metal_rod"],"name":"secured"}; supporting_effect={"condition":{"args":["sleeve","metal_rod"],"name":"secured"},"producer_status":"uncertain","provisional":true,"step_id":"step::pilot_rod_assembly::step_06","type":"previous_produced_effect"}; confidence=1.0; provisional=true
- N39<Step:step::pilot_rod_assembly::step_08> -[DEPENDS_ON]-> N37<Step:step::pilot_rod_assembly::step_06>; required_condition={"args":["sleeve","metal_rod"],"name":"secured"}; supporting_effect={"condition":{"args":["sleeve","metal_rod"],"name":"secured"},"producer_status":"uncertain","provisional":true,"step_id":"step::pilot_rod_assembly::step_06","type":"previous_produced_effect"}; confidence=1.0; provisional=true
- N3 -[DERIVED_FROM]-> N30
- N4 -[DERIVED_FROM]-> N30
- N5 -[DERIVED_FROM]-> N31
- N6 -[DERIVED_FROM]-> N31
- N7 -[DERIVED_FROM]-> N31
- N8 -[DERIVED_FROM]-> N31
- N9 -[DERIVED_FROM]-> N32
- N19 -[DERIVED_FROM]-> N34
- N20 -[DERIVED_FROM]-> N34
- N21 -[DERIVED_FROM]-> N34
- N22 -[DERIVED_FROM]-> N34
- N23 -[DERIVED_FROM]-> N34
- N24 -[DERIVED_FROM]-> N34
- N25 -[DERIVED_FROM]-> N33
- N26 -[DERIVED_FROM]-> N33
- N27 -[DERIVED_FROM]-> N34
- N28 -[DERIVED_FROM]-> N34
- N29 -[DERIVED_FROM]-> N34
- N37 -[HAS_CONSTRAINT]-> N3
- N37 -[HAS_CONSTRAINT]-> N4
- N37 -[HAS_CONSTRAINT]-> N5
- N37 -[HAS_CONSTRAINT]-> N6
- N37 -[HAS_CONSTRAINT]-> N7
- N37 -[HAS_CONSTRAINT]-> N8
- N37 -[HAS_CONSTRAINT]-> N9
- N3 -[HAS_ENTITY]-> N12
- N3 -[HAS_ENTITY]-> N17
- N4 -[HAS_ENTITY]-> N16
- N4 -[HAS_ENTITY]-> N17
- N5 -[HAS_ENTITY]-> N16
- N5 -[HAS_ENTITY]-> N18
- N6 -[HAS_ENTITY]-> N15
- N6 -[HAS_ENTITY]-> N16
- N7 -[HAS_ENTITY]-> N15
- N7 -[HAS_ENTITY]-> N16
- N8 -[HAS_ENTITY]-> N13
- N8 -[HAS_ENTITY]-> N16
- N9 -[HAS_ENTITY]-> N14
- N20 -[HAS_ENTITY]-> N16
- N20 -[HAS_ENTITY]-> N17
- N21 -[HAS_ENTITY]-> N12
- N21 -[HAS_ENTITY]-> N17
- N22 -[HAS_ENTITY]-> N16
- N23 -[HAS_ENTITY]-> N14
- N24 -[HAS_ENTITY]-> N15
- N24 -[HAS_ENTITY]-> N16
- N25 -[HAS_ENTITY]-> N13
- N25 -[HAS_ENTITY]-> N16
- N26 -[HAS_ENTITY]-> N15
- N26 -[HAS_ENTITY]-> N16
- N27 -[HAS_ENTITY]-> N16
- N27 -[HAS_ENTITY]-> N18
- N29 -[HAS_ENTITY]-> N14
- N37 -[HAS_PREDICATE]-> N19
- N37 -[HAS_PREDICATE]-> N20
- N37 -[HAS_PREDICATE]-> N21
- N37 -[HAS_PREDICATE]-> N22
- N37 -[HAS_PREDICATE]-> N23
- N37 -[HAS_PREDICATE]-> N24
- N37 -[HAS_PREDICATE]-> N25
- N37 -[HAS_PREDICATE]-> N26
- N37 -[HAS_PREDICATE]-> N27
- N37 -[HAS_PREDICATE]-> N28
- N37 -[HAS_PREDICATE]-> N29
- N36<Step:step::pilot_rod_assembly::step_05> -[NEXT]-> N37<Step:step::pilot_rod_assembly::step_06>
- N37<Step:step::pilot_rod_assembly::step_06> -[NEXT]-> N38<Step:step::pilot_rod_assembly::step_07>
- N37 -[PRODUCES]-> N3
- N37 -[PRODUCES]-> N4
- N37 -[REQUIRES]-> N5
- N37 -[REQUIRES]-> N6
- N37 -[REQUIRES]-> N7
- N37 -[REQUIRES]-> N8
- N37 -[REQUIRES]-> N9
- N5 -[SUPPORTED_BY]-> N2
- N6 -[SUPPORTED_BY]-> N1
- N10 -[SUPPORTED_BY]-> N3
- N11 -[SUPPORTED_BY]-> N3
- N37 -[USES]-> N14
- N37 -[USES]-> N16
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that no torque value is represented
  - avoid inventing a torque
  - refer to the official procedure or supervisor

## Case: q29_direct_video_confirmation

- Step id: `step::pilot_rod_assembly::step_04`
- Operator question: Can you confirm from the video that every screw is aligned with every O-ring?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `40`
- Selected edges: `82`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 12 |
| Entity | 6 |
| Predicate | 12 |
| Rule | 3 |
| Source | 3 |
| Step | 4 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 3 |
| DERIVED_FROM | 18 |
| HAS_CONSTRAINT | 6 |
| HAS_ENTITY | 27 |
| HAS_PREDICATE | 12 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 5 |
| SUPPORTED_BY | 6 |
| USES | 2 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (40 nodes, 82 edges):
Nodes:
- N1 [Constraint] produces inserted_in(o_ring, rod_holes) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_03","inserted_in","o_ring","rod_holes"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N2 [Constraint] produces aligned(o_ring, rod_holes) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_03","aligned","o_ring","rod_holes"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N3 [Constraint] produces adjusted_over(sleeve, o_ring) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_03","adjusted_over","sleeve","o_ring"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N4 [Constraint] produces aligned(sleeve, o_ring) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_03","aligned","sleeve","o_ring"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N5 [Constraint] produces partially_inserted_in(screw, rod_holes) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_04","partially_inserted_in","screw","rod_holes"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N6 [Constraint] requires inserted_in(o_ring, rod_holes) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_04","inserted_in","o_ring","rod_holes"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N7 [Constraint] requires aligned(o_ring, rod_holes) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_04","aligned","o_ring","rod_holes"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N8 [Constraint] requires adjusted_over(sleeve, o_ring) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_04","adjusted_over","sleeve","o_ring"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N9 [Constraint] requires aligned(sleeve, o_ring) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_04","aligned","sleeve","o_ring"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N10 [Constraint] requires tool(power_screwdriver) [supported]; kind="required_tool"; name="requiresTool"; args=["step::pilot_rod_assembly::step_04","power_screwdriver"]; support_status="supported"; rule_id="tool_required_by_pilot_step"; confidence=1.0
- N11 [Constraint] requires partially_inserted_in(screw, rod_holes) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_05","partially_inserted_in","screw","rod_holes"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N12 [Constraint] requires partially_inserted_in(screw, rod_holes) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N13 [Entity] metal_rod
- N14 [Entity] o_ring
- N15 [Entity] power_screwdriver
- N16 [Entity] rod_holes
- N17 [Entity] screw
- N18 [Entity] sleeve
- N19 [Predicate] hasAction(step_04, drive); name="hasAction"; args=["step::pilot_rod_assembly::step_04","drive"]; confidence=1.0
- N20 [Predicate] hasObservedEffect(step_04, partially_inserted_in, screw, rod_holes); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_04","partially_inserted_in","screw","rod_holes"]; confidence=1.0
- N21 [Predicate] usesObject(step_04, screw); name="usesObject"; args=["step::pilot_rod_assembly::step_04","screw"]; confidence=1.0
- N22 [Predicate] hasParentComponent(rod_holes, metal_rod); name="hasParentComponent"; args=["rod_holes","metal_rod"]; confidence=1.0
- N23 [Predicate] hasRequiredTool(step_04, power_screwdriver); name="hasRequiredTool"; args=["step::pilot_rod_assembly::step_04","power_screwdriver"]; confidence=1.0
- N24 [Predicate] hasRequiredCondition(step_04, aligned, o_ring, rod_holes); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_04","aligned","o_ring","rod_holes"]; confidence=1.0
- N25 [Predicate] hasRequiredCondition(step_04, inserted_in, o_ring, rod_holes); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_04","inserted_in","o_ring","rod_holes"]; confidence=1.0
- N26 [Predicate] hasRequiredCondition(step_04, aligned, sleeve, o_ring); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_04","aligned","sleeve","o_ring"]; confidence=1.0
- N27 [Predicate] hasRequiredCondition(step_04, adjusted_over, sleeve, o_ring); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_04","adjusted_over","sleeve","o_ring"]; confidence=1.0
- N28 [Predicate] hasTimeWindow(step_04, 196, 376); name="hasTimeWindow"; args=["step::pilot_rod_assembly::step_04",196,376]; confidence=1.0
- N29 [Predicate] usesTool(step_04, power_screwdriver); name="usesTool"; args=["step::pilot_rod_assembly::step_04","power_screwdriver"]; confidence=1.0
- N30 [Predicate] isA(rod_holes, RodHole); name="isA"; args=["rod_holes","RodHole"]; confidence=1.0
- N31 [Rule] effect_observed_pilot_condition; rule_id="effect_observed_pilot_condition"
- N32 [Rule] precondition_required_pilot_condition; rule_id="precondition_required_pilot_condition"
- N33 [Rule] tool_required_by_pilot_step; rule_id="tool_required_by_pilot_step"
- N34 [Source] pilot_domain_default:domain_config_pilot.yaml
- N35 [Source] manual_symbolic_annotation:rod_assembly_steps.json
- N36 [Source] pilot_domain_config:domain_config_pilot.yaml
- N37 [Step] Step 3 [accepted]; step_id="step::pilot_rod_assembly::step_03"; action_description="The operator places O-rings in the holes on the rod and adjusts the sleeves over them."; status="accepted"; confidence=1.0; warning_count=0
- N38 [Step] [CURRENT] Step 4 [accepted]; step_id="step::pilot_rod_assembly::step_04"; action_description="The operator drives the screws halfway into all holes using a power screwdriver."; status="accepted"; confidence=1.0; warning_count=0
- N39 [Step] Step 5 [accepted]; step_id="step::pilot_rod_assembly::step_05"; action_description="The operator applies threadlocker (Loctite) to all partially inserted screws."; status="accepted"; confidence=1.0; warning_count=0
- N40 [Step] Step 6 [uncertain]; step_id="step::pilot_rod_assembly::step_06"; action_description="The operator fully tightens all screws to secure the sleeves."; status="uncertain"; confidence=1.0; warning_count=0
Edges:
- N38<Step:step::pilot_rod_assembly::step_04> -[DEPENDS_ON]-> N37<Step:step::pilot_rod_assembly::step_03>; required_condition={"args":["o_ring","rod_holes"],"name":"aligned"}; supporting_effect={"condition":{"args":["o_ring","rod_holes"],"name":"aligned"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_03","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N39<Step:step::pilot_rod_assembly::step_05> -[DEPENDS_ON]-> N38<Step:step::pilot_rod_assembly::step_04>; required_condition={"args":["screw","rod_holes"],"name":"partially_inserted_in"}; supporting_effect={"condition":{"args":["screw","rod_holes"],"name":"partially_inserted_in"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_04","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N40<Step:step::pilot_rod_assembly::step_06> -[DEPENDS_ON]-> N38<Step:step::pilot_rod_assembly::step_04>; required_condition={"args":["screw","rod_holes"],"name":"partially_inserted_in"}; supporting_effect={"condition":{"args":["screw","rod_holes"],"name":"partially_inserted_in"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_04","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N5 -[DERIVED_FROM]-> N31
- N6 -[DERIVED_FROM]-> N32
- N7 -[DERIVED_FROM]-> N32
- N8 -[DERIVED_FROM]-> N32
- N9 -[DERIVED_FROM]-> N32
- N10 -[DERIVED_FROM]-> N33
- N19 -[DERIVED_FROM]-> N35
- N20 -[DERIVED_FROM]-> N35
- N21 -[DERIVED_FROM]-> N35
- N22 -[DERIVED_FROM]-> N36
- N23 -[DERIVED_FROM]-> N35
- N24 -[DERIVED_FROM]-> N34
- N25 -[DERIVED_FROM]-> N35
- N26 -[DERIVED_FROM]-> N34
- N27 -[DERIVED_FROM]-> N35
- N28 -[DERIVED_FROM]-> N35
- N29 -[DERIVED_FROM]-> N35
- N30 -[DERIVED_FROM]-> N36
- N38 -[HAS_CONSTRAINT]-> N5
- N38 -[HAS_CONSTRAINT]-> N6
- N38 -[HAS_CONSTRAINT]-> N7
- N38 -[HAS_CONSTRAINT]-> N8
- N38 -[HAS_CONSTRAINT]-> N9
- N38 -[HAS_CONSTRAINT]-> N10
- N5 -[HAS_ENTITY]-> N16
- N5 -[HAS_ENTITY]-> N17
- N6 -[HAS_ENTITY]-> N14
- N6 -[HAS_ENTITY]-> N16
- N7 -[HAS_ENTITY]-> N14
- N7 -[HAS_ENTITY]-> N16
- N8 -[HAS_ENTITY]-> N14
- N8 -[HAS_ENTITY]-> N18
- N9 -[HAS_ENTITY]-> N14
- N9 -[HAS_ENTITY]-> N18
- N10 -[HAS_ENTITY]-> N15
- N20 -[HAS_ENTITY]-> N16
- N20 -[HAS_ENTITY]-> N17
- N21 -[HAS_ENTITY]-> N17
- N22 -[HAS_ENTITY]-> N13
- N22 -[HAS_ENTITY]-> N16
- N23 -[HAS_ENTITY]-> N15
- N24 -[HAS_ENTITY]-> N14
- N24 -[HAS_ENTITY]-> N16
- N25 -[HAS_ENTITY]-> N14
- N25 -[HAS_ENTITY]-> N16
- N26 -[HAS_ENTITY]-> N14
- N26 -[HAS_ENTITY]-> N18
- N27 -[HAS_ENTITY]-> N14
- N27 -[HAS_ENTITY]-> N18
- N29 -[HAS_ENTITY]-> N15
- N30 -[HAS_ENTITY]-> N16
- N38 -[HAS_PREDICATE]-> N19
- N38 -[HAS_PREDICATE]-> N20
- N38 -[HAS_PREDICATE]-> N21
- N38 -[HAS_PREDICATE]-> N22
- N38 -[HAS_PREDICATE]-> N23
- N38 -[HAS_PREDICATE]-> N24
- N38 -[HAS_PREDICATE]-> N25
- N38 -[HAS_PREDICATE]-> N26
- N38 -[HAS_PREDICATE]-> N27
- N38 -[HAS_PREDICATE]-> N28
- N38 -[HAS_PREDICATE]-> N29
- N38 -[HAS_PREDICATE]-> N30
- N37<Step:step::pilot_rod_assembly::step_03> -[NEXT]-> N38<Step:step::pilot_rod_assembly::step_04>
- N38<Step:step::pilot_rod_assembly::step_04> -[NEXT]-> N39<Step:step::pilot_rod_assembly::step_05>
- N38 -[PRODUCES]-> N5
- N38 -[REQUIRES]-> N6
- N38 -[REQUIRES]-> N7
- N38 -[REQUIRES]-> N8
- N38 -[REQUIRES]-> N9
- N38 -[REQUIRES]-> N10
- N6 -[SUPPORTED_BY]-> N1
- N7 -[SUPPORTED_BY]-> N2
- N8 -[SUPPORTED_BY]-> N3
- N9 -[SUPPORTED_BY]-> N4
- N11 -[SUPPORTED_BY]-> N5
- N12 -[SUPPORTED_BY]-> N5
- N38 -[USES]-> N15
- N38 -[USES]-> N17
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that no raw video evidence is available in this reasoning graph
  - state that screw-O-ring alignment is not confirmed
  - distinguish graph requirement from visual confirmation

## Case: q30_exact_instance_count

- Step id: `step::pilot_rod_assembly::step_02`
- Operator question: Can you list the exact identity of each of the six copper sleeves and five long sleeves?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `35`
- Selected edges: `75`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 7 |
| Entity | 9 |
| Predicate | 12 |
| Rule | 2 |
| Source | 2 |
| Step | 3 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 2 |
| DERIVED_FROM | 17 |
| HAS_CONSTRAINT | 5 |
| HAS_ENTITY | 25 |
| HAS_PREDICATE | 12 |
| NEXT | 2 |
| PRODUCES | 4 |
| REQUIRES | 1 |
| SUPPORTED_BY | 2 |
| USES | 5 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (35 nodes, 75 edges):
Nodes:
- N1 [Constraint] produces secured(metal_rod, workbench) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_01","secured","metal_rod","workbench"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N2 [Constraint] produces sleeves_on(sleeve, metal_rod) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_02","sleeves_on","sleeve","metal_rod"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N3 [Constraint] produces oriented(copper_sleeve, right_side) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_02","oriented","copper_sleeve","right_side"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N4 [Constraint] produces count_verified(copper_sleeve, required_quantity_six) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_02","count_verified","copper_sleeve","required_quantity_six"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N5 [Constraint] produces count_verified(long_sleeve, required_quantity_five) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_02","count_verified","long_sleeve","required_quantity_five"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N6 [Constraint] requires secured(metal_rod, workbench) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_02","secured","metal_rod","workbench"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N7 [Constraint] requires sleeves_on(sleeve, metal_rod) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_03","sleeves_on","sleeve","metal_rod"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N8 [Entity] copper_sleeve
- N9 [Entity] long_sleeve
- N10 [Entity] metal_rod
- N11 [Entity] required_quantity_five
- N12 [Entity] required_quantity_six
- N13 [Entity] right_side
- N14 [Entity] short_sleeve
- N15 [Entity] sleeve
- N16 [Entity] workbench
- N17 [Predicate] hasAction(step_02, slide); name="hasAction"; args=["step::pilot_rod_assembly::step_02","slide"]; confidence=1.0
- N18 [Predicate] hasObservedEffect(step_02, count_verified, copper_sleeve, required_quantity_six); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_02","count_verified","copper_sleeve","required_quantity_six"]; confidence=1.0
- N19 [Predicate] hasObservedEffect(step_02, oriented, copper_sleeve, right_side); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_02","oriented","copper_sleeve","right_side"]; confidence=1.0
- N20 [Predicate] hasObservedEffect(step_02, count_verified, long_sleeve, required_quantity_five); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_02","count_verified","long_sleeve","required_quantity_five"]; confidence=1.0
- N21 [Predicate] hasObservedEffect(step_02, sleeves_on, sleeve, metal_rod); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_02","sleeves_on","sleeve","metal_rod"]; confidence=1.0
- N22 [Predicate] usesObject(step_02, copper_sleeve); name="usesObject"; args=["step::pilot_rod_assembly::step_02","copper_sleeve"]; confidence=1.0
- N23 [Predicate] usesObject(step_02, long_sleeve); name="usesObject"; args=["step::pilot_rod_assembly::step_02","long_sleeve"]; confidence=1.0
- N24 [Predicate] usesObject(step_02, metal_rod); name="usesObject"; args=["step::pilot_rod_assembly::step_02","metal_rod"]; confidence=1.0
- N25 [Predicate] usesObject(step_02, short_sleeve); name="usesObject"; args=["step::pilot_rod_assembly::step_02","short_sleeve"]; confidence=1.0
- N26 [Predicate] usesObject(step_02, sleeve); name="usesObject"; args=["step::pilot_rod_assembly::step_02","sleeve"]; confidence=1.0
- N27 [Predicate] hasRequiredCondition(step_02, secured, metal_rod, workbench); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_02","secured","metal_rod","workbench"]; confidence=1.0
- N28 [Predicate] hasTimeWindow(step_02, 15, 89); name="hasTimeWindow"; args=["step::pilot_rod_assembly::step_02",15,89]; confidence=1.0
- N29 [Rule] effect_observed_pilot_condition; rule_id="effect_observed_pilot_condition"
- N30 [Rule] precondition_required_pilot_condition; rule_id="precondition_required_pilot_condition"
- N31 [Source] pilot_domain_default:domain_config_pilot.yaml
- N32 [Source] manual_symbolic_annotation:rod_assembly_steps.json
- N33 [Step] Step 1 [accepted]; step_id="step::pilot_rod_assembly::step_01"; action_description="The operator places a long metal rod on the workbench."; status="accepted"; confidence=1.0; warning_count=0
- N34 [Step] [CURRENT] Step 2 [accepted]; step_id="step::pilot_rod_assembly::step_02"; action_description="The operator slides a combination of long, short and copper sleeves onto the rod."; status="accepted"; confidence=1.0; warning_count=0
- N35 [Step] Step 3 [accepted]; step_id="step::pilot_rod_assembly::step_03"; action_description="The operator places O-rings in the holes on the rod and adjusts the sleeves over them."; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N34<Step:step::pilot_rod_assembly::step_02> -[DEPENDS_ON]-> N33<Step:step::pilot_rod_assembly::step_01>; required_condition={"args":["metal_rod","workbench"],"name":"secured"}; supporting_effect={"condition":{"args":["metal_rod","workbench"],"name":"secured"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_01","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N35<Step:step::pilot_rod_assembly::step_03> -[DEPENDS_ON]-> N34<Step:step::pilot_rod_assembly::step_02>; required_condition={"args":["sleeve","metal_rod"],"name":"sleeves_on"}; supporting_effect={"condition":{"args":["sleeve","metal_rod"],"name":"sleeves_on"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_02","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N29
- N3 -[DERIVED_FROM]-> N29
- N4 -[DERIVED_FROM]-> N29
- N5 -[DERIVED_FROM]-> N29
- N6 -[DERIVED_FROM]-> N30
- N17 -[DERIVED_FROM]-> N32
- N18 -[DERIVED_FROM]-> N32
- N19 -[DERIVED_FROM]-> N32
- N20 -[DERIVED_FROM]-> N32
- N21 -[DERIVED_FROM]-> N32
- N22 -[DERIVED_FROM]-> N32
- N23 -[DERIVED_FROM]-> N32
- N24 -[DERIVED_FROM]-> N32
- N25 -[DERIVED_FROM]-> N32
- N26 -[DERIVED_FROM]-> N32
- N27 -[DERIVED_FROM]-> N31
- N28 -[DERIVED_FROM]-> N32
- N34 -[HAS_CONSTRAINT]-> N2
- N34 -[HAS_CONSTRAINT]-> N3
- N34 -[HAS_CONSTRAINT]-> N4
- N34 -[HAS_CONSTRAINT]-> N5
- N34 -[HAS_CONSTRAINT]-> N6
- N2 -[HAS_ENTITY]-> N10
- N2 -[HAS_ENTITY]-> N15
- N3 -[HAS_ENTITY]-> N8
- N3 -[HAS_ENTITY]-> N13
- N4 -[HAS_ENTITY]-> N8
- N4 -[HAS_ENTITY]-> N12
- N5 -[HAS_ENTITY]-> N9
- N5 -[HAS_ENTITY]-> N11
- N6 -[HAS_ENTITY]-> N10
- N6 -[HAS_ENTITY]-> N16
- N18 -[HAS_ENTITY]-> N8
- N18 -[HAS_ENTITY]-> N12
- N19 -[HAS_ENTITY]-> N8
- N19 -[HAS_ENTITY]-> N13
- N20 -[HAS_ENTITY]-> N9
- N20 -[HAS_ENTITY]-> N11
- N21 -[HAS_ENTITY]-> N10
- N21 -[HAS_ENTITY]-> N15
- N22 -[HAS_ENTITY]-> N8
- N23 -[HAS_ENTITY]-> N9
- N24 -[HAS_ENTITY]-> N10
- N25 -[HAS_ENTITY]-> N14
- N26 -[HAS_ENTITY]-> N15
- N27 -[HAS_ENTITY]-> N10
- N27 -[HAS_ENTITY]-> N16
- N34 -[HAS_PREDICATE]-> N17
- N34 -[HAS_PREDICATE]-> N18
- N34 -[HAS_PREDICATE]-> N19
- N34 -[HAS_PREDICATE]-> N20
- N34 -[HAS_PREDICATE]-> N21
- N34 -[HAS_PREDICATE]-> N22
- N34 -[HAS_PREDICATE]-> N23
- N34 -[HAS_PREDICATE]-> N24
- N34 -[HAS_PREDICATE]-> N25
- N34 -[HAS_PREDICATE]-> N26
- N34 -[HAS_PREDICATE]-> N27
- N34 -[HAS_PREDICATE]-> N28
- N33<Step:step::pilot_rod_assembly::step_01> -[NEXT]-> N34<Step:step::pilot_rod_assembly::step_02>
- N34<Step:step::pilot_rod_assembly::step_02> -[NEXT]-> N35<Step:step::pilot_rod_assembly::step_03>
- N34 -[PRODUCES]-> N2
- N34 -[PRODUCES]-> N3
- N34 -[PRODUCES]-> N4
- N34 -[PRODUCES]-> N5
- N34 -[REQUIRES]-> N6
- N6 -[SUPPORTED_BY]-> N1
- N7 -[SUPPORTED_BY]-> N2
- N34 -[USES]-> N8
- N34 -[USES]-> N9
- N34 -[USES]-> N10
- N34 -[USES]-> N14
- N34 -[USES]-> N15
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - state that the graph has aggregate sleeve entities
  - state that count_verified facts exist
  - avoid inventing individual sleeve identifiers

## Case: q31_ambiguous_okay_question

- Step id: `step::pilot_rod_assembly::step_06`
- Operator question: Is this okay?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `39`
- Selected edges: `83`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 11 |
| Entity | 7 |
| Predicate | 11 |
| Rule | 3 |
| Source | 2 |
| Step | 5 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 4 |
| DERIVED_FROM | 18 |
| HAS_CONSTRAINT | 7 |
| HAS_ENTITY | 28 |
| HAS_PREDICATE | 11 |
| NEXT | 2 |
| PRODUCES | 2 |
| REQUIRES | 5 |
| SUPPORTED_BY | 4 |
| USES | 2 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (39 nodes, 83 edges):
Nodes:
- N1 [Constraint] produces partially_inserted_in(screw, rod_holes) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_04","partially_inserted_in","screw","rod_holes"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N2 [Constraint] produces applied_to(threadlocker_loctite, screw) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_05","applied_to","threadlocker_loctite","screw"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N3 [Constraint] produces secured(sleeve, metal_rod) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_06","secured","sleeve","metal_rod"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N4 [Constraint] produces flush_with(screw, sleeve) [observed]; kind="expected_effect"; name="produces"; args=["step::pilot_rod_assembly::step_06","flush_with","screw","sleeve"]; support_status="observed"; rule_id="effect_observed_pilot_condition"; confidence=1.0
- N5 [Constraint] requires applied_to(threadlocker_loctite, screw) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","applied_to","threadlocker_loctite","screw"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N6 [Constraint] requires partially_inserted_in(screw, rod_holes) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N7 [Constraint] requires aligned(screw, rod_holes) [missing]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","aligned","screw","rod_holes"]; support_status="missing"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N8 [Constraint] requires aligned(screw, o_ring) [missing]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_06","aligned","screw","o_ring"]; support_status="missing"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N9 [Constraint] requires tool(power_screwdriver) [supported]; kind="required_tool"; name="requiresTool"; args=["step::pilot_rod_assembly::step_06","power_screwdriver"]; support_status="supported"; rule_id="tool_required_by_pilot_step"; confidence=1.0
- N10 [Constraint] requires secured(sleeve, metal_rod) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_07","secured","sleeve","metal_rod"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N11 [Constraint] requires secured(sleeve, metal_rod) [supported]; kind="inferred_precondition"; name="requires"; args=["step::pilot_rod_assembly::step_08","secured","sleeve","metal_rod"]; support_status="supported"; rule_id="precondition_required_pilot_condition"; confidence=1.0
- N12 [Entity] metal_rod
- N13 [Entity] o_ring
- N14 [Entity] power_screwdriver
- N15 [Entity] rod_holes
- N16 [Entity] screw
- N17 [Entity] sleeve
- N18 [Entity] threadlocker_loctite
- N19 [Predicate] hasAction(step_06, tighten); name="hasAction"; args=["step::pilot_rod_assembly::step_06","tighten"]; confidence=1.0
- N20 [Predicate] hasObservedEffect(step_06, flush_with, screw, sleeve); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_06","flush_with","screw","sleeve"]; confidence=1.0
- N21 [Predicate] hasObservedEffect(step_06, secured, sleeve, metal_rod); name="hasObservedEffect"; args=["step::pilot_rod_assembly::step_06","secured","sleeve","metal_rod"]; confidence=1.0
- N22 [Predicate] usesObject(step_06, screw); name="usesObject"; args=["step::pilot_rod_assembly::step_06","screw"]; confidence=1.0
- N23 [Predicate] hasRequiredTool(step_06, power_screwdriver); name="hasRequiredTool"; args=["step::pilot_rod_assembly::step_06","power_screwdriver"]; confidence=1.0
- N24 [Predicate] hasRequiredCondition(step_06, partially_inserted_in, screw, rod_holes); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","partially_inserted_in","screw","rod_holes"]; confidence=1.0
- N25 [Predicate] hasRequiredCondition(step_06, aligned, screw, o_ring); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","aligned","screw","o_ring"]; confidence=1.0
- N26 [Predicate] hasRequiredCondition(step_06, aligned, screw, rod_holes); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","aligned","screw","rod_holes"]; confidence=1.0
- N27 [Predicate] hasRequiredCondition(step_06, applied_to, threadlocker_loctite, screw); name="hasRequiredCondition"; args=["step::pilot_rod_assembly::step_06","applied_to","threadlocker_loctite","screw"]; confidence=1.0
- N28 [Predicate] hasTimeWindow(step_06, 429, 531); name="hasTimeWindow"; args=["step::pilot_rod_assembly::step_06",429,531]; confidence=1.0
- N29 [Predicate] usesTool(step_06, power_screwdriver); name="usesTool"; args=["step::pilot_rod_assembly::step_06","power_screwdriver"]; confidence=1.0
- N30 [Rule] effect_observed_pilot_condition; rule_id="effect_observed_pilot_condition"
- N31 [Rule] precondition_required_pilot_condition; rule_id="precondition_required_pilot_condition"
- N32 [Rule] tool_required_by_pilot_step; rule_id="tool_required_by_pilot_step"
- N33 [Source] pilot_domain_default:domain_config_pilot.yaml
- N34 [Source] manual_symbolic_annotation:rod_assembly_steps.json
- N35 [Step] Step 4 [accepted]; step_id="step::pilot_rod_assembly::step_04"; action_description="The operator drives the screws halfway into all holes using a power screwdriver."; status="accepted"; confidence=1.0; warning_count=0
- N36 [Step] Step 5 [accepted]; step_id="step::pilot_rod_assembly::step_05"; action_description="The operator applies threadlocker (Loctite) to all partially inserted screws."; status="accepted"; confidence=1.0; warning_count=0
- N37 [Step] [CURRENT] Step 6 [uncertain]; step_id="step::pilot_rod_assembly::step_06"; action_description="The operator fully tightens all screws to secure the sleeves."; status="uncertain"; confidence=1.0; warning_count=0
- N38 [Step] Step 7 [accepted]; step_id="step::pilot_rod_assembly::step_07"; action_description="The operator cleans the rod and sleeves with ethanol and paper."; status="accepted"; confidence=1.0; warning_count=0
- N39 [Step] Step 8 [accepted]; step_id="step::pilot_rod_assembly::step_08"; action_description="The operator applies grease to a sponge and lubricates the silver-colored sleeves, while avoiding the copper sleeves."; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N37<Step:step::pilot_rod_assembly::step_06> -[DEPENDS_ON]-> N35<Step:step::pilot_rod_assembly::step_04>; required_condition={"args":["screw","rod_holes"],"name":"partially_inserted_in"}; supporting_effect={"condition":{"args":["screw","rod_holes"],"name":"partially_inserted_in"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_04","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N37<Step:step::pilot_rod_assembly::step_06> -[DEPENDS_ON]-> N36<Step:step::pilot_rod_assembly::step_05>; required_condition={"args":["threadlocker_loctite","screw"],"name":"applied_to"}; supporting_effect={"condition":{"args":["threadlocker_loctite","screw"],"name":"applied_to"},"producer_status":"accepted","provisional":false,"step_id":"step::pilot_rod_assembly::step_05","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N38<Step:step::pilot_rod_assembly::step_07> -[DEPENDS_ON]-> N37<Step:step::pilot_rod_assembly::step_06>; required_condition={"args":["sleeve","metal_rod"],"name":"secured"}; supporting_effect={"condition":{"args":["sleeve","metal_rod"],"name":"secured"},"producer_status":"uncertain","provisional":true,"step_id":"step::pilot_rod_assembly::step_06","type":"previous_produced_effect"}; confidence=1.0; provisional=true
- N39<Step:step::pilot_rod_assembly::step_08> -[DEPENDS_ON]-> N37<Step:step::pilot_rod_assembly::step_06>; required_condition={"args":["sleeve","metal_rod"],"name":"secured"}; supporting_effect={"condition":{"args":["sleeve","metal_rod"],"name":"secured"},"producer_status":"uncertain","provisional":true,"step_id":"step::pilot_rod_assembly::step_06","type":"previous_produced_effect"}; confidence=1.0; provisional=true
- N3 -[DERIVED_FROM]-> N30
- N4 -[DERIVED_FROM]-> N30
- N5 -[DERIVED_FROM]-> N31
- N6 -[DERIVED_FROM]-> N31
- N7 -[DERIVED_FROM]-> N31
- N8 -[DERIVED_FROM]-> N31
- N9 -[DERIVED_FROM]-> N32
- N19 -[DERIVED_FROM]-> N34
- N20 -[DERIVED_FROM]-> N34
- N21 -[DERIVED_FROM]-> N34
- N22 -[DERIVED_FROM]-> N34
- N23 -[DERIVED_FROM]-> N34
- N24 -[DERIVED_FROM]-> N34
- N25 -[DERIVED_FROM]-> N33
- N26 -[DERIVED_FROM]-> N33
- N27 -[DERIVED_FROM]-> N34
- N28 -[DERIVED_FROM]-> N34
- N29 -[DERIVED_FROM]-> N34
- N37 -[HAS_CONSTRAINT]-> N3
- N37 -[HAS_CONSTRAINT]-> N4
- N37 -[HAS_CONSTRAINT]-> N5
- N37 -[HAS_CONSTRAINT]-> N6
- N37 -[HAS_CONSTRAINT]-> N7
- N37 -[HAS_CONSTRAINT]-> N8
- N37 -[HAS_CONSTRAINT]-> N9
- N3 -[HAS_ENTITY]-> N12
- N3 -[HAS_ENTITY]-> N17
- N4 -[HAS_ENTITY]-> N16
- N4 -[HAS_ENTITY]-> N17
- N5 -[HAS_ENTITY]-> N16
- N5 -[HAS_ENTITY]-> N18
- N6 -[HAS_ENTITY]-> N15
- N6 -[HAS_ENTITY]-> N16
- N7 -[HAS_ENTITY]-> N15
- N7 -[HAS_ENTITY]-> N16
- N8 -[HAS_ENTITY]-> N13
- N8 -[HAS_ENTITY]-> N16
- N9 -[HAS_ENTITY]-> N14
- N20 -[HAS_ENTITY]-> N16
- N20 -[HAS_ENTITY]-> N17
- N21 -[HAS_ENTITY]-> N12
- N21 -[HAS_ENTITY]-> N17
- N22 -[HAS_ENTITY]-> N16
- N23 -[HAS_ENTITY]-> N14
- N24 -[HAS_ENTITY]-> N15
- N24 -[HAS_ENTITY]-> N16
- N25 -[HAS_ENTITY]-> N13
- N25 -[HAS_ENTITY]-> N16
- N26 -[HAS_ENTITY]-> N15
- N26 -[HAS_ENTITY]-> N16
- N27 -[HAS_ENTITY]-> N16
- N27 -[HAS_ENTITY]-> N18
- N29 -[HAS_ENTITY]-> N14
- N37 -[HAS_PREDICATE]-> N19
- N37 -[HAS_PREDICATE]-> N20
- N37 -[HAS_PREDICATE]-> N21
- N37 -[HAS_PREDICATE]-> N22
- N37 -[HAS_PREDICATE]-> N23
- N37 -[HAS_PREDICATE]-> N24
- N37 -[HAS_PREDICATE]-> N25
- N37 -[HAS_PREDICATE]-> N26
- N37 -[HAS_PREDICATE]-> N27
- N37 -[HAS_PREDICATE]-> N28
- N37 -[HAS_PREDICATE]-> N29
- N36<Step:step::pilot_rod_assembly::step_05> -[NEXT]-> N37<Step:step::pilot_rod_assembly::step_06>
- N37<Step:step::pilot_rod_assembly::step_06> -[NEXT]-> N38<Step:step::pilot_rod_assembly::step_07>
- N37 -[PRODUCES]-> N3
- N37 -[PRODUCES]-> N4
- N37 -[REQUIRES]-> N5
- N37 -[REQUIRES]-> N6
- N37 -[REQUIRES]-> N7
- N37 -[REQUIRES]-> N8
- N37 -[REQUIRES]-> N9
- N5 -[SUPPORTED_BY]-> N2
- N6 -[SUPPORTED_BY]-> N1
- N10 -[SUPPORTED_BY]-> N3
- N11 -[SUPPORTED_BY]-> N3
- N37 -[USES]-> N14
- N37 -[USES]-> N16
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `scenario_f_missing_evidence_controls`
- Scenario: `scenario_f_missing_evidence_controls`
- Status: `Runnable now`
- Expected answer elements:
  - ask what specific condition or component the operator is concerned about
  - mention that Step 6 has unresolved screw alignment requirements
  - avoid giving a blanket go-ahead

