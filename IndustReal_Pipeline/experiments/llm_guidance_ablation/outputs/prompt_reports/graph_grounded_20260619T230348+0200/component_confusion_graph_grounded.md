# Prompt Report: component_confusion

Generated at: 2026-06-19T21:17:20.322608+00:00

- Condition: `graph_grounded`
- Risk type: `component_confusion`
- Cases in this report: `3`

## API Request Settings

- API base URL: `http://localhost:1234/v1`
- Model name: `mistralai/mistral-7b-instruct-v0.3`
- Temperature: `0.0`
- Max tokens: `512`

## Run Timing Statistics

These statistics cover all successful prompt interactions in this experiment run.

- Completed interactions: `19`
- Minimum prompt time: `21.35 s`
- Maximum prompt time: `69.23 s`
- Average prompt time: `42.72 s`
- Total experiment time: `00h 13m 31.76s`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `experiments\llm_guidance_ablation\data\steps_od_only_test_p1_03_assy_0_1.txt`
- Step-list artifact loaded: `True`
- Windowed predicates included: `no`
- Sequence step-hop radius: `1`
- Semantic evidence-hop radius: `2`
- Thesis rules included: `no`
- Procedural reasoning graph included: `yes`

All conditions include the same frozen step-list artifact. The `symbolic_domain` condition adds a deterministic predicate window and `thesis_rules.yaml`; `graph_grounded` adds a deterministic local graph neighborhood.

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### System Message

- Role: `system`

```text
You are an assistant helping a novice assembly operator. Answer using only the generated procedural steps and procedural reasoning graph evidence provided. Do not invent facts that are absent from that evidence. If any required condition is missing, do not recommend continuing. Mention relevant missing requirements, supported requirements, dependencies, incompatibilities, safety constraints, or trace evidence only when the provided graph evidence contains that information. Be concise, practical, and safety-aware.
```

### Frozen Procedural Step List

This block is inserted into the user message for every case.

```text
Available assembly steps:
- Step 0: Install base
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0
  - acted_on_object: base
  - previous_step_id: none
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
  - time_window: start_frame=709, end_frame=1187
  - confidence: 1.0
- Step 1: Install rear chassis
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
  - acted_on_object: rear chassis
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
  - time_window: start_frame=709, end_frame=1187
  - confidence: 1.0
- Step 2: Install front rear chassis pin
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
  - acted_on_object: front rear chassis pin
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3
  - time_window: start_frame=709, end_frame=1187
  - confidence: 1.0
- Step 3: Install front chassis
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3
  - acted_on_object: front chassis
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
  - time_window: start_frame=1187, end_frame=1788
  - confidence: 1.0
- Step 4: Install front chassis pin
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
  - acted_on_object: front chassis pin
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5
  - time_window: start_frame=1187, end_frame=1788
  - confidence: 1.0
- Step 5: Install rear rear chassis pin
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5
  - acted_on_object: rear rear chassis pin
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_6
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 6: Install front bracket
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_6
  - acted_on_object: front bracket
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_7
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 7: Install front bracket screw
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_7
  - acted_on_object: front bracket screw
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_6
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_8
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 8: Install front wheel assy
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_8
  - acted_on_object: front wheel assy
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_7
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_9
  - time_window: start_frame=1788, end_frame=2735
  - confidence: 1.0
- Step 9: Remove front wheel assy
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_9
  - acted_on_object: front wheel assy
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_8
  - next_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_10
  - time_window: start_frame=2735, end_frame=None
  - confidence: 1.0
- Step 10: Install rear wheel assy
  - step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_10
  - acted_on_object: rear wheel assy
  - previous_step_id: raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_9
  - next_step_id: none
  - time_window: start_frame=2735, end_frame=None
  - confidence: 1.0

```



## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: case_002_possible_wrong_part

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_002`
- Operator question: This part looks similar to another one. How can I check whether it is the correct component?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `37`
- Selected edges: `66`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 5 |
| Entity | 4 |
| Predicate | 12 |
| Rule | 4 |
| Source | 9 |
| Step | 3 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 1 |
| DERIVED_FROM | 16 |
| HAS_CONSTRAINT | 4 |
| HAS_ENTITY | 25 |
| HAS_PREDICATE | 12 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 3 |
| SUPPORTED_BY | 1 |
| USES | 1 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (37 nodes, 66 edges):
Sequence context:
- previous: event_1 | Install rear chassis
- current: event_2 | Install front rear chassis pin
- next: event_3 | Install front chassis
Nodes:
- N1 [Constraint] produces installed(rear_chassis, base) [observed]; kind="expected_effect"; name="produces"; args=["event_1","installed","rear_chassis","base"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] produces installed(front_rear_chassis_pin, rear_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_2","installed","front_rear_chassis_pin","rear_chassis"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N3 [Constraint] requires aligned(front_rear_chassis_pin, rear_chassis) [missing]; kind="implicit_assembly_condition"; name="requires"; args=["event_2","aligned","front_rear_chassis_pin","rear_chassis"]; support_status="missing"; rule_id="implicit_domain_required_condition"; confidence=1.0
- N4 [Constraint] requires installed(rear_chassis, base) [supported]; kind="inferred_precondition"; name="requires"; args=["event_2","installed","rear_chassis","base"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N5 [Constraint] requires safety secured(base, workspace) [missing]; kind="safety_constraint"; name="requiresSafety"; args=["event_2","secured","base","workspace"]; support_status="missing"; rule_id="safety_domain_requirement"; confidence=1.0
- N6 [Entity] base
- N7 [Entity] front_rear_chassis_pin
- N8 [Entity] rear_chassis
- N9 [Entity] workspace
- N10 [Predicate] hasAction(event_2, install); name="hasAction"; args=["event_2","install"]; confidence=1.0
- N11 [Predicate] hasInstallTarget(front_rear_chassis_pin, rear_chassis); name="hasInstallTarget"; args=["front_rear_chassis_pin","rear_chassis"]; confidence=1.0
- N12 [Predicate] hasLabel(front_rear_chassis_pin, front_rear_chassis_pin); name="hasLabel"; args=["front_rear_chassis_pin","front_rear_chassis_pin"]; confidence=1.0
- N13 [Predicate] hasParentComponent(front_rear_chassis_pin, rear_chassis); name="hasParentComponent"; args=["front_rear_chassis_pin","rear_chassis"]; confidence=1.0
- N14 [Predicate] hasRequiredCondition(front_rear_chassis_pin, aligned, front_rear_chassis_pin, rear_chassis); name="hasRequiredCondition"; args=["front_rear_chassis_pin","aligned","front_rear_chassis_pin","rear_chassis"]; confidence=1.0
- N15 [Predicate] hasSafetyRequirement(front_rear_chassis_pin, secured, base, workspace); name="hasSafetyRequirement"; args=["front_rear_chassis_pin","secured","base","workspace"]; confidence=1.0
- N16 [Predicate] hasTimeWindow(event_2, 70.9, 118.7); name="hasTimeWindow"; args=["event_2",70.9,118.7]; confidence=1.0
- N17 [Predicate] isA(front_rear_chassis_pin, ChassisPin); name="isA"; args=["front_rear_chassis_pin","ChassisPin"]; confidence=1.0
- N18 [Predicate] isA(front_rear_chassis_pin, Component); name="isA"; args=["front_rear_chassis_pin","Component"]; confidence=1.0
- N19 [Predicate] isA(front_rear_chassis_pin, Fastener); name="isA"; args=["front_rear_chassis_pin","Fastener"]; confidence=1.0
- N20 [Predicate] requiresInstalledBefore(front_rear_chassis_pin, rear_chassis, base); name="requiresInstalledBefore"; args=["front_rear_chassis_pin","rear_chassis","base"]; confidence=1.0
- N21 [Predicate] usesObject(event_2, front_rear_chassis_pin); name="usesObject"; args=["event_2","front_rear_chassis_pin"]; confidence=1.0
- N22 [Rule] effect_install_component_on_target; rule_id="effect_install_component_on_target"
- N23 [Rule] implicit_domain_required_condition; rule_id="implicit_domain_required_condition"
- N24 [Rule] precondition_install_requires_target_installed; rule_id="precondition_install_requires_target_installed"
- N25 [Rule] safety_domain_requirement; rule_id="safety_domain_requirement"
- N26 [Source] existing_graph_csv:domain_config.yaml
- N27 [Source] existing_graph_csv:domain_config.yaml
- N28 [Source] existing_graph_csv:edges_event_component.csv
- N29 [Source] existing_graph_csv:domain_config.yaml
- N30 [Source] existing_graph_csv:nodes_events.csv
- N31 [Source] existing_graph_csv:domain_config.yaml
- N32 [Source] existing_graph_csv:nodes_components.csv
- N33 [Source] existing_graph_csv:nodes_events.csv
- N34 [Source] existing_graph_csv:domain_config.yaml
- N35 [Step] Step 1 [accepted]; step_id="event_1"; action_description="Install rear chassis"; status="accepted"; confidence=1.0; warning_count=0
- N36 [Step] [CURRENT] Step 2 [uncertain]; step_id="event_2"; action_description="Install front rear chassis pin"; status="uncertain"; confidence=1.0; warning_count=0
- N37 [Step] Step 3 [accepted]; step_id="event_3"; action_description="Install front chassis"; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N36 -[DEPENDS_ON]-> N35; required_condition={"args":["rear_chassis","base"],"name":"installed"}; supporting_effect={"condition":{"args":["rear_chassis","base"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_1","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N22
- N3 -[DERIVED_FROM]-> N23
- N4 -[DERIVED_FROM]-> N24
- N5 -[DERIVED_FROM]-> N25
- N10 -[DERIVED_FROM]-> N30
- N11 -[DERIVED_FROM]-> N27
- N12 -[DERIVED_FROM]-> N32
- N13 -[DERIVED_FROM]-> N26
- N14 -[DERIVED_FROM]-> N34
- N15 -[DERIVED_FROM]-> N31
- N16 -[DERIVED_FROM]-> N33
- N17 -[DERIVED_FROM]-> N29
- N18 -[DERIVED_FROM]-> N29
- N19 -[DERIVED_FROM]-> N29
- N20 -[DERIVED_FROM]-> N27
- N21 -[DERIVED_FROM]-> N28
- N36 -[HAS_CONSTRAINT]-> N2
- N36 -[HAS_CONSTRAINT]-> N3
- N36 -[HAS_CONSTRAINT]-> N4
- N36 -[HAS_CONSTRAINT]-> N5
- N2 -[HAS_ENTITY]-> N7
- N2 -[HAS_ENTITY]-> N8
- N3 -[HAS_ENTITY]-> N7
- N3 -[HAS_ENTITY]-> N8
- N4 -[HAS_ENTITY]-> N6
- N4 -[HAS_ENTITY]-> N8
- N5 -[HAS_ENTITY]-> N6
- N5 -[HAS_ENTITY]-> N9
- N11 -[HAS_ENTITY]-> N7
- N11 -[HAS_ENTITY]-> N8
- N12 -[HAS_ENTITY]-> N7
- N13 -[HAS_ENTITY]-> N7
- N13 -[HAS_ENTITY]-> N8
- N14 -[HAS_ENTITY]-> N7
- N14 -[HAS_ENTITY]-> N8
- N15 -[HAS_ENTITY]-> N6
- N15 -[HAS_ENTITY]-> N7
- N15 -[HAS_ENTITY]-> N9
- N17 -[HAS_ENTITY]-> N7
- N18 -[HAS_ENTITY]-> N7
- N19 -[HAS_ENTITY]-> N7
- N20 -[HAS_ENTITY]-> N6
- N20 -[HAS_ENTITY]-> N7
- N20 -[HAS_ENTITY]-> N8
- N21 -[HAS_ENTITY]-> N7
- N36 -[HAS_PREDICATE]-> N10
- N36 -[HAS_PREDICATE]-> N11
- N36 -[HAS_PREDICATE]-> N12
- N36 -[HAS_PREDICATE]-> N13
- N36 -[HAS_PREDICATE]-> N14
- N36 -[HAS_PREDICATE]-> N15
- N36 -[HAS_PREDICATE]-> N16
- N36 -[HAS_PREDICATE]-> N17
- N36 -[HAS_PREDICATE]-> N18
- N36 -[HAS_PREDICATE]-> N19
- N36 -[HAS_PREDICATE]-> N20
- N36 -[HAS_PREDICATE]-> N21
- N35 -[NEXT]-> N36
- N36 -[NEXT]-> N37
- N36 -[PRODUCES]-> N2
- N36 -[REQUIRES]-> N3
- N36 -[REQUIRES]-> N4
- N36 -[REQUIRES]-> N5
- N4 -[SUPPORTED_BY]-> N1
- N36 -[USES]-> N7
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `component_confusion`
- Expected answer elements:
  - compare the component against the step requirement
  - use available identifiers or visual features
  - avoid installing an uncertain component

## Case: component_002_named_part_check

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_006`
- Operator question: Am I supposed to install the rear wheel assembly now?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `29`
- Selected edges: `46`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 4 |
| Entity | 3 |
| Predicate | 9 |
| Rule | 2 |
| Source | 7 |
| Step | 4 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 2 |
| DERIVED_FROM | 11 |
| HAS_CONSTRAINT | 2 |
| HAS_ENTITY | 15 |
| HAS_PREDICATE | 9 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 1 |
| SUPPORTED_BY | 2 |
| USES | 1 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (29 nodes, 46 edges):
Sequence context:
- previous: event_5 | Install rear rear chassis pin
- current: event_6 | Install front bracket
- next: event_7 | Install front bracket screw
Nodes:
- N1 [Constraint] produces installed(front_chassis, base) [observed]; kind="expected_effect"; name="produces"; args=["event_3","installed","front_chassis","base"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] produces installed(front_bracket, front_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_6","installed","front_bracket","front_chassis"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N3 [Constraint] requires installed(front_chassis, base) [supported]; kind="inferred_precondition"; name="requires"; args=["event_6","installed","front_chassis","base"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N4 [Constraint] requires installed(front_bracket, front_chassis) [supported]; kind="inferred_precondition"; name="requires"; args=["event_7","installed","front_bracket","front_chassis"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N5 [Entity] base
- N6 [Entity] front_bracket
- N7 [Entity] front_chassis
- N8 [Predicate] hasAction(event_6, install); name="hasAction"; args=["event_6","install"]; confidence=1.0
- N9 [Predicate] hasInstallTarget(front_bracket, front_chassis); name="hasInstallTarget"; args=["front_bracket","front_chassis"]; confidence=1.0
- N10 [Predicate] hasLabel(front_bracket, front_bracket); name="hasLabel"; args=["front_bracket","front_bracket"]; confidence=1.0
- N11 [Predicate] hasParentComponent(front_bracket, front_chassis); name="hasParentComponent"; args=["front_bracket","front_chassis"]; confidence=1.0
- N12 [Predicate] hasTimeWindow(event_6, 178.8, 273.5); name="hasTimeWindow"; args=["event_6",178.8,273.5]; confidence=1.0
- N13 [Predicate] isA(front_bracket, Bracket); name="isA"; args=["front_bracket","Bracket"]; confidence=1.0
- N14 [Predicate] isA(front_bracket, Component); name="isA"; args=["front_bracket","Component"]; confidence=1.0
- N15 [Predicate] requiresInstalledBefore(front_bracket, front_chassis, base); name="requiresInstalledBefore"; args=["front_bracket","front_chassis","base"]; confidence=1.0
- N16 [Predicate] usesObject(event_6, front_bracket); name="usesObject"; args=["event_6","front_bracket"]; confidence=1.0
- N17 [Rule] effect_install_component_on_target; rule_id="effect_install_component_on_target"
- N18 [Rule] precondition_install_requires_target_installed; rule_id="precondition_install_requires_target_installed"
- N19 [Source] existing_graph_csv:edges_event_component.csv
- N20 [Source] existing_graph_csv:domain_config.yaml
- N21 [Source] existing_graph_csv:nodes_events.csv
- N22 [Source] existing_graph_csv:domain_config.yaml
- N23 [Source] existing_graph_csv:nodes_components.csv
- N24 [Source] existing_graph_csv:domain_config.yaml
- N25 [Source] existing_graph_csv:nodes_events.csv
- N26 [Step] Step 3 [accepted]; step_id="event_3"; action_description="Install front chassis"; status="accepted"; confidence=1.0; warning_count=0
- N27 [Step] Step 5 [uncertain]; step_id="event_5"; action_description="Install rear rear chassis pin"; status="uncertain"; confidence=1.0; warning_count=0
- N28 [Step] [CURRENT] Step 6 [accepted]; step_id="event_6"; action_description="Install front bracket"; status="accepted"; confidence=1.0; warning_count=0
- N29 [Step] Step 7 [uncertain]; step_id="event_7"; action_description="Install front bracket screw"; status="uncertain"; confidence=1.0; warning_count=0
Edges:
- N28 -[DEPENDS_ON]-> N26; required_condition={"args":["front_chassis","base"],"name":"installed"}; supporting_effect={"condition":{"args":["front_chassis","base"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_3","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N29 -[DEPENDS_ON]-> N28; required_condition={"args":["front_bracket","front_chassis"],"name":"installed"}; supporting_effect={"condition":{"args":["front_bracket","front_chassis"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_6","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N17
- N3 -[DERIVED_FROM]-> N18
- N8 -[DERIVED_FROM]-> N21
- N9 -[DERIVED_FROM]-> N22
- N10 -[DERIVED_FROM]-> N23
- N11 -[DERIVED_FROM]-> N24
- N12 -[DERIVED_FROM]-> N25
- N13 -[DERIVED_FROM]-> N20
- N14 -[DERIVED_FROM]-> N20
- N15 -[DERIVED_FROM]-> N22
- N16 -[DERIVED_FROM]-> N19
- N28 -[HAS_CONSTRAINT]-> N2
- N28 -[HAS_CONSTRAINT]-> N3
- N2 -[HAS_ENTITY]-> N6
- N2 -[HAS_ENTITY]-> N7
- N3 -[HAS_ENTITY]-> N5
- N3 -[HAS_ENTITY]-> N7
- N9 -[HAS_ENTITY]-> N6
- N9 -[HAS_ENTITY]-> N7
- N10 -[HAS_ENTITY]-> N6
- N11 -[HAS_ENTITY]-> N6
- N11 -[HAS_ENTITY]-> N7
- N13 -[HAS_ENTITY]-> N6
- N14 -[HAS_ENTITY]-> N6
- N15 -[HAS_ENTITY]-> N5
- N15 -[HAS_ENTITY]-> N6
- N15 -[HAS_ENTITY]-> N7
- N16 -[HAS_ENTITY]-> N6
- N28 -[HAS_PREDICATE]-> N8
- N28 -[HAS_PREDICATE]-> N9
- N28 -[HAS_PREDICATE]-> N10
- N28 -[HAS_PREDICATE]-> N11
- N28 -[HAS_PREDICATE]-> N12
- N28 -[HAS_PREDICATE]-> N13
- N28 -[HAS_PREDICATE]-> N14
- N28 -[HAS_PREDICATE]-> N15
- N28 -[HAS_PREDICATE]-> N16
- N27 -[NEXT]-> N28
- N28 -[NEXT]-> N29
- N28 -[PRODUCES]-> N2
- N28 -[REQUIRES]-> N3
- N3 -[SUPPORTED_BY]-> N1
- N4 -[SUPPORTED_BY]-> N2
- N28 -[USES]-> N6
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `component_confusion`
- Expected answer elements:
  - compare the named component to the current step
  - state if the part belongs to another step
  - recommend following the ordered step list

## Case: component_003_part_label_uncertainty

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_007`
- Operator question: The label on the part is hard to read. What should I compare it against before installing it?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `33`
- Selected edges: `55`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 4 |
| Entity | 4 |
| Predicate | 11 |
| Rule | 3 |
| Source | 8 |
| Step | 3 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 1 |
| DERIVED_FROM | 14 |
| HAS_CONSTRAINT | 3 |
| HAS_ENTITY | 19 |
| HAS_PREDICATE | 11 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 2 |
| SUPPORTED_BY | 1 |
| USES | 1 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (33 nodes, 55 edges):
Sequence context:
- previous: event_6 | Install front bracket
- current: event_7 | Install front bracket screw
- next: event_8 | Install front wheel assy
Nodes:
- N1 [Constraint] produces installed(front_bracket, front_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_6","installed","front_bracket","front_chassis"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] produces installed(front_bracket_screw, front_bracket) [observed]; kind="expected_effect"; name="produces"; args=["event_7","installed","front_bracket_screw","front_bracket"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N3 [Constraint] requires installed(front_bracket, front_chassis) [supported]; kind="inferred_precondition"; name="requires"; args=["event_7","installed","front_bracket","front_chassis"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N4 [Constraint] requires tool(screwdriver) [missing]; kind="required_tool"; name="requiresTool"; args=["event_7","screwdriver"]; support_status="missing"; rule_id="tool_domain_requirement"; confidence=1.0
- N5 [Entity] front_bracket
- N6 [Entity] front_bracket_screw
- N7 [Entity] front_chassis
- N8 [Entity] screwdriver
- N9 [Predicate] hasAction(event_7, install); name="hasAction"; args=["event_7","install"]; confidence=1.0
- N10 [Predicate] hasInstallTarget(front_bracket_screw, front_bracket); name="hasInstallTarget"; args=["front_bracket_screw","front_bracket"]; confidence=1.0
- N11 [Predicate] hasLabel(front_bracket_screw, front_bracket_screw); name="hasLabel"; args=["front_bracket_screw","front_bracket_screw"]; confidence=1.0
- N12 [Predicate] hasParentComponent(front_bracket_screw, front_bracket); name="hasParentComponent"; args=["front_bracket_screw","front_bracket"]; confidence=1.0
- N13 [Predicate] hasRequiredTool(front_bracket_screw, screwdriver); name="hasRequiredTool"; args=["front_bracket_screw","screwdriver"]; confidence=1.0
- N14 [Predicate] hasTimeWindow(event_7, 178.8, 273.5); name="hasTimeWindow"; args=["event_7",178.8,273.5]; confidence=1.0
- N15 [Predicate] isA(front_bracket_screw, Component); name="isA"; args=["front_bracket_screw","Component"]; confidence=1.0
- N16 [Predicate] isA(front_bracket_screw, Fastener); name="isA"; args=["front_bracket_screw","Fastener"]; confidence=1.0
- N17 [Predicate] isA(front_bracket_screw, Screw); name="isA"; args=["front_bracket_screw","Screw"]; confidence=1.0
- N18 [Predicate] requiresInstalledBefore(front_bracket_screw, front_bracket, front_chassis); name="requiresInstalledBefore"; args=["front_bracket_screw","front_bracket","front_chassis"]; confidence=1.0
- N19 [Predicate] usesObject(event_7, front_bracket_screw); name="usesObject"; args=["event_7","front_bracket_screw"]; confidence=1.0
- N20 [Rule] effect_install_component_on_target; rule_id="effect_install_component_on_target"
- N21 [Rule] precondition_install_requires_target_installed; rule_id="precondition_install_requires_target_installed"
- N22 [Rule] tool_domain_requirement; rule_id="tool_domain_requirement"
- N23 [Source] existing_graph_csv:domain_config.yaml
- N24 [Source] existing_graph_csv:edges_event_component.csv
- N25 [Source] existing_graph_csv:domain_config.yaml
- N26 [Source] existing_graph_csv:nodes_events.csv
- N27 [Source] existing_graph_csv:nodes_components.csv
- N28 [Source] existing_graph_csv:domain_config.yaml
- N29 [Source] existing_graph_csv:nodes_events.csv
- N30 [Source] existing_graph_csv:domain_config.yaml
- N31 [Step] Step 6 [accepted]; step_id="event_6"; action_description="Install front bracket"; status="accepted"; confidence=1.0; warning_count=0
- N32 [Step] [CURRENT] Step 7 [uncertain]; step_id="event_7"; action_description="Install front bracket screw"; status="uncertain"; confidence=1.0; warning_count=0
- N33 [Step] Step 8 [accepted]; step_id="event_8"; action_description="Install front wheel assy"; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N32 -[DEPENDS_ON]-> N31; required_condition={"args":["front_bracket","front_chassis"],"name":"installed"}; supporting_effect={"condition":{"args":["front_bracket","front_chassis"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_6","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N20
- N3 -[DERIVED_FROM]-> N21
- N4 -[DERIVED_FROM]-> N22
- N9 -[DERIVED_FROM]-> N26
- N10 -[DERIVED_FROM]-> N25
- N11 -[DERIVED_FROM]-> N27
- N12 -[DERIVED_FROM]-> N30
- N13 -[DERIVED_FROM]-> N28
- N14 -[DERIVED_FROM]-> N29
- N15 -[DERIVED_FROM]-> N23
- N16 -[DERIVED_FROM]-> N23
- N17 -[DERIVED_FROM]-> N23
- N18 -[DERIVED_FROM]-> N25
- N19 -[DERIVED_FROM]-> N24
- N32 -[HAS_CONSTRAINT]-> N2
- N32 -[HAS_CONSTRAINT]-> N3
- N32 -[HAS_CONSTRAINT]-> N4
- N2 -[HAS_ENTITY]-> N5
- N2 -[HAS_ENTITY]-> N6
- N3 -[HAS_ENTITY]-> N5
- N3 -[HAS_ENTITY]-> N7
- N4 -[HAS_ENTITY]-> N8
- N10 -[HAS_ENTITY]-> N5
- N10 -[HAS_ENTITY]-> N6
- N11 -[HAS_ENTITY]-> N6
- N12 -[HAS_ENTITY]-> N5
- N12 -[HAS_ENTITY]-> N6
- N13 -[HAS_ENTITY]-> N6
- N13 -[HAS_ENTITY]-> N8
- N15 -[HAS_ENTITY]-> N6
- N16 -[HAS_ENTITY]-> N6
- N17 -[HAS_ENTITY]-> N6
- N18 -[HAS_ENTITY]-> N5
- N18 -[HAS_ENTITY]-> N6
- N18 -[HAS_ENTITY]-> N7
- N19 -[HAS_ENTITY]-> N6
- N32 -[HAS_PREDICATE]-> N9
- N32 -[HAS_PREDICATE]-> N10
- N32 -[HAS_PREDICATE]-> N11
- N32 -[HAS_PREDICATE]-> N12
- N32 -[HAS_PREDICATE]-> N13
- N32 -[HAS_PREDICATE]-> N14
- N32 -[HAS_PREDICATE]-> N15
- N32 -[HAS_PREDICATE]-> N16
- N32 -[HAS_PREDICATE]-> N17
- N32 -[HAS_PREDICATE]-> N18
- N32 -[HAS_PREDICATE]-> N19
- N31 -[NEXT]-> N32
- N32 -[NEXT]-> N33
- N32 -[PRODUCES]-> N2
- N32 -[REQUIRES]-> N3
- N32 -[REQUIRES]-> N4
- N3 -[SUPPORTED_BY]-> N1
- N32 -[USES]-> N6
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `component_confusion`
- Expected answer elements:
  - identify the acted-on object for the current step
  - compare label or visible features
  - do not proceed if the component identity is uncertain

