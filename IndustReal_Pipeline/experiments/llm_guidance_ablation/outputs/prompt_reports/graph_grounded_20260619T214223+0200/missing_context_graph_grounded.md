# Prompt Report: missing_context

Generated at: 2026-06-19T19:55:37.373541+00:00

- Condition: `graph_grounded`
- Risk type: `missing_context`
- Cases in this report: `3`

## API Request Settings

- API base URL: `http://localhost:1234/v1`
- Model name: `mistralai/mistral-7b-instruct-v0.3`
- Temperature: `0.0`
- Max tokens: `512`

## Run Timing Statistics

These statistics cover all successful prompt interactions in this experiment run.

- Completed interactions: `19`
- Minimum prompt time: `20.71 s`
- Maximum prompt time: `71.91 s`
- Average prompt time: `41.76 s`
- Total experiment time: `00h 13m 13.62s`

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


## Case: context_001_no_visible_step

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_999`
- Operator question: I cannot find this step in the instructions. What should I do?

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

- Risk type: `missing_context`
- Expected answer elements:
  - state that the step id is not found
  - ask for the correct step or instruction list
  - avoid giving procedural advice without context

## Case: context_002_ambiguous_question

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_001`
- Operator question: Is this okay?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `30`
- Selected edges: `46`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 6 |
| Entity | 3 |
| Predicate | 8 |
| Rule | 2 |
| Source | 6 |
| Step | 5 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 4 |
| DERIVED_FROM | 10 |
| HAS_CONSTRAINT | 2 |
| HAS_ENTITY | 13 |
| HAS_PREDICATE | 8 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 1 |
| SUPPORTED_BY | 4 |
| USES | 1 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (30 nodes, 46 edges):
Nodes:
- N1 [Constraint] produces installed(base, workspace) [observed]; kind="expected_effect"; name="produces"; args=["event_0","installed","base","workspace"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] requires installed(rear_chassis, base) [supported]; kind="inferred_precondition"; name="requires"; args=["event_10","installed","rear_chassis","base"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N3 [Constraint] produces installed(rear_chassis, base) [observed]; kind="expected_effect"; name="produces"; args=["event_1","installed","rear_chassis","base"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N4 [Constraint] requires installed(base, workspace) [supported]; kind="inferred_precondition"; name="requires"; args=["event_1","installed","base","workspace"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N5 [Constraint] requires installed(rear_chassis, base) [supported]; kind="inferred_precondition"; name="requires"; args=["event_2","installed","rear_chassis","base"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N6 [Constraint] requires installed(rear_chassis, base) [supported]; kind="inferred_precondition"; name="requires"; args=["event_5","installed","rear_chassis","base"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N7 [Entity] base
- N8 [Entity] rear_chassis
- N9 [Entity] workspace
- N10 [Predicate] hasAction(event_1, install); name="hasAction"; args=["event_1","install"]; confidence=1.0
- N11 [Predicate] hasInstallTarget(rear_chassis, base); name="hasInstallTarget"; args=["rear_chassis","base"]; confidence=1.0
- N12 [Predicate] hasLabel(rear_chassis, rear_chassis); name="hasLabel"; args=["rear_chassis","rear_chassis"]; confidence=1.0
- N13 [Predicate] hasTimeWindow(event_1, 70.9, 118.7); name="hasTimeWindow"; args=["event_1",70.9,118.7]; confidence=1.0
- N14 [Predicate] isA(rear_chassis, Chassis); name="isA"; args=["rear_chassis","Chassis"]; confidence=1.0
- N15 [Predicate] isA(rear_chassis, Component); name="isA"; args=["rear_chassis","Component"]; confidence=1.0
- N16 [Predicate] requiresInstalledBefore(rear_chassis, base, workspace); name="requiresInstalledBefore"; args=["rear_chassis","base","workspace"]; confidence=1.0
- N17 [Predicate] usesObject(event_1, rear_chassis); name="usesObject"; args=["event_1","rear_chassis"]; confidence=1.0
- N18 [Rule] effect_install_component_on_target; rule_id="effect_install_component_on_target"
- N19 [Rule] precondition_install_requires_target_installed; rule_id="precondition_install_requires_target_installed"
- N20 [Source] existing_graph_csv:edges_event_component.csv
- N21 [Source] existing_graph_csv:nodes_events.csv
- N22 [Source] existing_graph_csv:domain_config.yaml
- N23 [Source] existing_graph_csv:domain_config.yaml
- N24 [Source] existing_graph_csv:nodes_components.csv
- N25 [Source] existing_graph_csv:nodes_events.csv
- N26 [Step] Step 0 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N27 [Step] Step 1 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N28 [Step] Step 10 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N29 [Step] Step 2 [uncertain]; status="uncertain"; confidence=1.0; warning_count=0
- N30 [Step] Step 5 [uncertain]; status="uncertain"; confidence=1.0; warning_count=0
Edges:
- N27 -[DEPENDS_ON]-> N26; required_condition={"args":["base","workspace"],"name":"installed"}; supporting_effect={"condition":{"args":["base","workspace"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_0","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N28 -[DEPENDS_ON]-> N27; required_condition={"args":["rear_chassis","base"],"name":"installed"}; supporting_effect={"condition":{"args":["rear_chassis","base"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_1","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N29 -[DEPENDS_ON]-> N27; required_condition={"args":["rear_chassis","base"],"name":"installed"}; supporting_effect={"condition":{"args":["rear_chassis","base"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_1","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N30 -[DEPENDS_ON]-> N27; required_condition={"args":["rear_chassis","base"],"name":"installed"}; supporting_effect={"condition":{"args":["rear_chassis","base"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_1","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N3 -[DERIVED_FROM]-> N18
- N4 -[DERIVED_FROM]-> N19
- N10 -[DERIVED_FROM]-> N21
- N11 -[DERIVED_FROM]-> N23
- N12 -[DERIVED_FROM]-> N24
- N13 -[DERIVED_FROM]-> N25
- N14 -[DERIVED_FROM]-> N22
- N15 -[DERIVED_FROM]-> N22
- N16 -[DERIVED_FROM]-> N23
- N17 -[DERIVED_FROM]-> N20
- N27 -[HAS_CONSTRAINT]-> N3
- N27 -[HAS_CONSTRAINT]-> N4
- N3 -[HAS_ENTITY]-> N7
- N3 -[HAS_ENTITY]-> N8
- N4 -[HAS_ENTITY]-> N7
- N4 -[HAS_ENTITY]-> N9
- N11 -[HAS_ENTITY]-> N7
- N11 -[HAS_ENTITY]-> N8
- N12 -[HAS_ENTITY]-> N8
- N14 -[HAS_ENTITY]-> N8
- N15 -[HAS_ENTITY]-> N8
- N16 -[HAS_ENTITY]-> N7
- N16 -[HAS_ENTITY]-> N8
- N16 -[HAS_ENTITY]-> N9
- N17 -[HAS_ENTITY]-> N8
- N27 -[HAS_PREDICATE]-> N10
- N27 -[HAS_PREDICATE]-> N11
- N27 -[HAS_PREDICATE]-> N12
- N27 -[HAS_PREDICATE]-> N13
- N27 -[HAS_PREDICATE]-> N14
- N27 -[HAS_PREDICATE]-> N15
- N27 -[HAS_PREDICATE]-> N16
- N27 -[HAS_PREDICATE]-> N17
- N26 -[NEXT]-> N27
- N27 -[NEXT]-> N29
- N27 -[PRODUCES]-> N3
- N27 -[REQUIRES]-> N4
- N2 -[SUPPORTED_BY]-> N3
- N4 -[SUPPORTED_BY]-> N1
- N5 -[SUPPORTED_BY]-> N3
- N6 -[SUPPORTED_BY]-> N3
- N27 -[USES]-> N8
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `missing_context`
- Expected answer elements:
  - state that the question is underspecified
  - ask what component or action is being checked
  - refer to the current step context

## Case: context_003_need_current_state

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_005`
- Operator question: I lost track of where I am in the assembly. How should I recover?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `38`
- Selected edges: `66`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 5 |
| Entity | 4 |
| Predicate | 12 |
| Rule | 4 |
| Source | 9 |
| Step | 4 |

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
Graph evidence (38 nodes, 66 edges):
Nodes:
- N1 [Constraint] produces installed(rear_chassis, base) [observed]; kind="expected_effect"; name="produces"; args=["event_1","installed","rear_chassis","base"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] produces installed(rear_rear_chassis_pin, rear_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_5","installed","rear_rear_chassis_pin","rear_chassis"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N3 [Constraint] requires aligned(rear_rear_chassis_pin, rear_chassis) [missing]; kind="implicit_assembly_condition"; name="requires"; args=["event_5","aligned","rear_rear_chassis_pin","rear_chassis"]; support_status="missing"; rule_id="implicit_domain_required_condition"; confidence=1.0
- N4 [Constraint] requires installed(rear_chassis, base) [supported]; kind="inferred_precondition"; name="requires"; args=["event_5","installed","rear_chassis","base"]; support_status="supported"; rule_id="precondition_install_requires_target_installed"; confidence=1.0
- N5 [Constraint] requires safety secured(base, workspace) [missing]; kind="safety_constraint"; name="requiresSafety"; args=["event_5","secured","base","workspace"]; support_status="missing"; rule_id="safety_domain_requirement"; confidence=1.0
- N6 [Entity] base
- N7 [Entity] rear_chassis
- N8 [Entity] rear_rear_chassis_pin
- N9 [Entity] workspace
- N10 [Predicate] hasAction(event_5, install); name="hasAction"; args=["event_5","install"]; confidence=1.0
- N11 [Predicate] hasInstallTarget(rear_rear_chassis_pin, rear_chassis); name="hasInstallTarget"; args=["rear_rear_chassis_pin","rear_chassis"]; confidence=1.0
- N12 [Predicate] hasLabel(rear_rear_chassis_pin, rear_rear_chassis_pin); name="hasLabel"; args=["rear_rear_chassis_pin","rear_rear_chassis_pin"]; confidence=1.0
- N13 [Predicate] hasParentComponent(rear_rear_chassis_pin, rear_chassis); name="hasParentComponent"; args=["rear_rear_chassis_pin","rear_chassis"]; confidence=1.0
- N14 [Predicate] hasRequiredCondition(rear_rear_chassis_pin, aligned, rear_rear_chassis_pin, rear_chassis); name="hasRequiredCondition"; args=["rear_rear_chassis_pin","aligned","rear_rear_chassis_pin","rear_chassis"]; confidence=1.0
- N15 [Predicate] hasSafetyRequirement(rear_rear_chassis_pin, secured, base, workspace); name="hasSafetyRequirement"; args=["rear_rear_chassis_pin","secured","base","workspace"]; confidence=1.0
- N16 [Predicate] hasTimeWindow(event_5, 178.8, 273.5); name="hasTimeWindow"; args=["event_5",178.8,273.5]; confidence=1.0
- N17 [Predicate] isA(rear_rear_chassis_pin, ChassisPin); name="isA"; args=["rear_rear_chassis_pin","ChassisPin"]; confidence=1.0
- N18 [Predicate] isA(rear_rear_chassis_pin, Component); name="isA"; args=["rear_rear_chassis_pin","Component"]; confidence=1.0
- N19 [Predicate] isA(rear_rear_chassis_pin, Fastener); name="isA"; args=["rear_rear_chassis_pin","Fastener"]; confidence=1.0
- N20 [Predicate] requiresInstalledBefore(rear_rear_chassis_pin, rear_chassis, base); name="requiresInstalledBefore"; args=["rear_rear_chassis_pin","rear_chassis","base"]; confidence=1.0
- N21 [Predicate] usesObject(event_5, rear_rear_chassis_pin); name="usesObject"; args=["event_5","rear_rear_chassis_pin"]; confidence=1.0
- N22 [Rule] effect_install_component_on_target; rule_id="effect_install_component_on_target"
- N23 [Rule] implicit_domain_required_condition; rule_id="implicit_domain_required_condition"
- N24 [Rule] precondition_install_requires_target_installed; rule_id="precondition_install_requires_target_installed"
- N25 [Rule] safety_domain_requirement; rule_id="safety_domain_requirement"
- N26 [Source] existing_graph_csv:edges_event_component.csv
- N27 [Source] existing_graph_csv:nodes_events.csv
- N28 [Source] existing_graph_csv:domain_config.yaml
- N29 [Source] existing_graph_csv:domain_config.yaml
- N30 [Source] existing_graph_csv:nodes_components.csv
- N31 [Source] existing_graph_csv:nodes_events.csv
- N32 [Source] existing_graph_csv:domain_config.yaml
- N33 [Source] existing_graph_csv:domain_config.yaml
- N34 [Source] existing_graph_csv:domain_config.yaml
- N35 [Step] Step 1 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N36 [Step] Step 4 [uncertain]; status="uncertain"; confidence=1.0; warning_count=0
- N37 [Step] Step 5 [uncertain]; status="uncertain"; confidence=1.0; warning_count=0
- N38 [Step] Step 6 [accepted]; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N37 -[DEPENDS_ON]-> N35; required_condition={"args":["rear_chassis","base"],"name":"installed"}; supporting_effect={"condition":{"args":["rear_chassis","base"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_1","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N22
- N3 -[DERIVED_FROM]-> N23
- N4 -[DERIVED_FROM]-> N24
- N5 -[DERIVED_FROM]-> N25
- N10 -[DERIVED_FROM]-> N27
- N11 -[DERIVED_FROM]-> N28
- N12 -[DERIVED_FROM]-> N30
- N13 -[DERIVED_FROM]-> N33
- N14 -[DERIVED_FROM]-> N34
- N15 -[DERIVED_FROM]-> N32
- N16 -[DERIVED_FROM]-> N31
- N17 -[DERIVED_FROM]-> N29
- N18 -[DERIVED_FROM]-> N29
- N19 -[DERIVED_FROM]-> N29
- N20 -[DERIVED_FROM]-> N28
- N21 -[DERIVED_FROM]-> N26
- N37 -[HAS_CONSTRAINT]-> N2
- N37 -[HAS_CONSTRAINT]-> N3
- N37 -[HAS_CONSTRAINT]-> N4
- N37 -[HAS_CONSTRAINT]-> N5
- N2 -[HAS_ENTITY]-> N7
- N2 -[HAS_ENTITY]-> N8
- N3 -[HAS_ENTITY]-> N7
- N3 -[HAS_ENTITY]-> N8
- N4 -[HAS_ENTITY]-> N6
- N4 -[HAS_ENTITY]-> N7
- N5 -[HAS_ENTITY]-> N6
- N5 -[HAS_ENTITY]-> N9
- N11 -[HAS_ENTITY]-> N7
- N11 -[HAS_ENTITY]-> N8
- N12 -[HAS_ENTITY]-> N8
- N13 -[HAS_ENTITY]-> N7
- N13 -[HAS_ENTITY]-> N8
- N14 -[HAS_ENTITY]-> N7
- N14 -[HAS_ENTITY]-> N8
- N15 -[HAS_ENTITY]-> N6
- N15 -[HAS_ENTITY]-> N8
- N15 -[HAS_ENTITY]-> N9
- N17 -[HAS_ENTITY]-> N8
- N18 -[HAS_ENTITY]-> N8
- N19 -[HAS_ENTITY]-> N8
- N20 -[HAS_ENTITY]-> N6
- N20 -[HAS_ENTITY]-> N7
- N20 -[HAS_ENTITY]-> N8
- N21 -[HAS_ENTITY]-> N8
- N37 -[HAS_PREDICATE]-> N10
- N37 -[HAS_PREDICATE]-> N11
- N37 -[HAS_PREDICATE]-> N12
- N37 -[HAS_PREDICATE]-> N13
- N37 -[HAS_PREDICATE]-> N14
- N37 -[HAS_PREDICATE]-> N15
- N37 -[HAS_PREDICATE]-> N16
- N37 -[HAS_PREDICATE]-> N17
- N37 -[HAS_PREDICATE]-> N18
- N37 -[HAS_PREDICATE]-> N19
- N37 -[HAS_PREDICATE]-> N20
- N37 -[HAS_PREDICATE]-> N21
- N36 -[NEXT]-> N37
- N37 -[NEXT]-> N38
- N37 -[PRODUCES]-> N2
- N37 -[REQUIRES]-> N3
- N37 -[REQUIRES]-> N4
- N37 -[REQUIRES]-> N5
- N4 -[SUPPORTED_BY]-> N1
- N37 -[USES]-> N8
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `missing_context`
- Expected answer elements:
  - use current step and nearby sequence context
  - recommend checking completed previous steps
  - avoid guessing the operator's actual physical state

