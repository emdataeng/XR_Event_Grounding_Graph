# Prompt Report: removal_or_rework_error

Generated at: 2026-06-19T19:55:37.392204+00:00

- Condition: `graph_grounded`
- Risk type: `removal_or_rework_error`
- Cases in this report: `2`

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


## Case: rework_001_remove_step_confusion

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_009`
- Operator question: This step says remove the front wheel assembly. Should I really take it off now?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `27`
- Selected edges: `45`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 3 |
| Entity | 3 |
| Predicate | 9 |
| Rule | 2 |
| Source | 7 |
| Step | 3 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 1 |
| DERIVED_FROM | 11 |
| HAS_CONSTRAINT | 2 |
| HAS_ENTITY | 15 |
| HAS_PREDICATE | 9 |
| INVALIDATED_BY | 1 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 1 |
| SUPPORTED_BY | 1 |
| USES | 1 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (27 nodes, 45 edges):
Nodes:
- N1 [Constraint] produces installed(front_wheel_assy, front_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_8","installed","front_wheel_assy","front_chassis"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] produces removed(front_wheel_assy, front_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_9","removed","front_wheel_assy","front_chassis"]; support_status="observed"; rule_id="effect_remove_component_from_target"; confidence=1.0
- N3 [Constraint] requires installed(front_wheel_assy, front_chassis) [supported]; kind="inferred_precondition"; name="requires"; args=["event_9","installed","front_wheel_assy","front_chassis"]; support_status="supported"; rule_id="precondition_remove_requires_component_installed"; confidence=1.0
- N4 [Entity] base
- N5 [Entity] front_chassis
- N6 [Entity] front_wheel_assy
- N7 [Predicate] hasAction(event_9, remove); name="hasAction"; args=["event_9","remove"]; confidence=1.0
- N8 [Predicate] hasInstallTarget(front_wheel_assy, front_chassis); name="hasInstallTarget"; args=["front_wheel_assy","front_chassis"]; confidence=1.0
- N9 [Predicate] hasLabel(front_wheel_assy, front_wheel_assy); name="hasLabel"; args=["front_wheel_assy","front_wheel_assy"]; confidence=1.0
- N10 [Predicate] hasParentComponent(front_wheel_assy, front_chassis); name="hasParentComponent"; args=["front_wheel_assy","front_chassis"]; confidence=1.0
- N11 [Predicate] hasTimeWindow(event_9, 273.5, None); name="hasTimeWindow"; args=["event_9",273.5,null]; confidence=1.0
- N12 [Predicate] isA(front_wheel_assy, Component); name="isA"; args=["front_wheel_assy","Component"]; confidence=1.0
- N13 [Predicate] isA(front_wheel_assy, WheelAssembly); name="isA"; args=["front_wheel_assy","WheelAssembly"]; confidence=1.0
- N14 [Predicate] requiresInstalledBefore(front_wheel_assy, front_chassis, base); name="requiresInstalledBefore"; args=["front_wheel_assy","front_chassis","base"]; confidence=1.0
- N15 [Predicate] usesObject(event_9, front_wheel_assy); name="usesObject"; args=["event_9","front_wheel_assy"]; confidence=1.0
- N16 [Rule] effect_remove_component_from_target; rule_id="effect_remove_component_from_target"
- N17 [Rule] precondition_remove_requires_component_installed; rule_id="precondition_remove_requires_component_installed"
- N18 [Source] existing_graph_csv:edges_event_component.csv
- N19 [Source] existing_graph_csv:domain_config.yaml
- N20 [Source] existing_graph_csv:nodes_events.csv
- N21 [Source] existing_graph_csv:domain_config.yaml
- N22 [Source] existing_graph_csv:nodes_components.csv
- N23 [Source] existing_graph_csv:nodes_events.csv
- N24 [Source] existing_graph_csv:domain_config.yaml
- N25 [Step] Step 10 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N26 [Step] Step 8 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N27 [Step] Step 9 [accepted]; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N27 -[DEPENDS_ON]-> N26; required_condition={"args":["front_wheel_assy","front_chassis"],"name":"installed"}; supporting_effect={"condition":{"args":["front_wheel_assy","front_chassis"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_8","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N16
- N3 -[DERIVED_FROM]-> N17
- N7 -[DERIVED_FROM]-> N20
- N8 -[DERIVED_FROM]-> N19
- N9 -[DERIVED_FROM]-> N22
- N10 -[DERIVED_FROM]-> N21
- N11 -[DERIVED_FROM]-> N23
- N12 -[DERIVED_FROM]-> N24
- N13 -[DERIVED_FROM]-> N24
- N14 -[DERIVED_FROM]-> N19
- N15 -[DERIVED_FROM]-> N18
- N27 -[HAS_CONSTRAINT]-> N2
- N27 -[HAS_CONSTRAINT]-> N3
- N2 -[HAS_ENTITY]-> N5
- N2 -[HAS_ENTITY]-> N6
- N3 -[HAS_ENTITY]-> N5
- N3 -[HAS_ENTITY]-> N6
- N8 -[HAS_ENTITY]-> N5
- N8 -[HAS_ENTITY]-> N6
- N9 -[HAS_ENTITY]-> N6
- N10 -[HAS_ENTITY]-> N5
- N10 -[HAS_ENTITY]-> N6
- N12 -[HAS_ENTITY]-> N6
- N13 -[HAS_ENTITY]-> N6
- N14 -[HAS_ENTITY]-> N4
- N14 -[HAS_ENTITY]-> N5
- N14 -[HAS_ENTITY]-> N6
- N15 -[HAS_ENTITY]-> N6
- N27 -[HAS_PREDICATE]-> N7
- N27 -[HAS_PREDICATE]-> N8
- N27 -[HAS_PREDICATE]-> N9
- N27 -[HAS_PREDICATE]-> N10
- N27 -[HAS_PREDICATE]-> N11
- N27 -[HAS_PREDICATE]-> N12
- N27 -[HAS_PREDICATE]-> N13
- N27 -[HAS_PREDICATE]-> N14
- N27 -[HAS_PREDICATE]-> N15
- N1 -[INVALIDATED_BY]-> N2
- N26 -[NEXT]-> N27
- N27 -[NEXT]-> N25
- N27 -[PRODUCES]-> N2
- N27 -[REQUIRES]-> N3
- N3 -[SUPPORTED_BY]-> N1
- N27 -[USES]-> N6
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `removal_or_rework_error`
- Expected answer elements:
  - identify that the current action is remove
  - confirm the acted-on object
  - recommend following the current step if it matches the instructions

## Case: rework_002_removed_wrong_part

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_009`
- Operator question: I may have removed the wrong part. What should I check before continuing?

### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `1`
- Semantic evidence hops: `2`
- Selected nodes: `27`
- Selected edges: `45`

#### Nodes By Type

| Node type | Count |
|---|---:|
| Constraint | 3 |
| Entity | 3 |
| Predicate | 9 |
| Rule | 2 |
| Source | 7 |
| Step | 3 |

#### Relationships By Type

| Relationship | Count |
|---|---:|
| DEPENDS_ON | 1 |
| DERIVED_FROM | 11 |
| HAS_CONSTRAINT | 2 |
| HAS_ENTITY | 15 |
| HAS_PREDICATE | 9 |
| INVALIDATED_BY | 1 |
| NEXT | 2 |
| PRODUCES | 1 |
| REQUIRES | 1 |
| SUPPORTED_BY | 1 |
| USES | 1 |

#### Exact Graph Evidence Sent To The LLM

```text
Retrieval policy: step_hops=1, evidence_hops=2
Graph evidence (27 nodes, 45 edges):
Nodes:
- N1 [Constraint] produces installed(front_wheel_assy, front_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_8","installed","front_wheel_assy","front_chassis"]; support_status="observed"; rule_id="effect_install_component_on_target"; confidence=1.0
- N2 [Constraint] produces removed(front_wheel_assy, front_chassis) [observed]; kind="expected_effect"; name="produces"; args=["event_9","removed","front_wheel_assy","front_chassis"]; support_status="observed"; rule_id="effect_remove_component_from_target"; confidence=1.0
- N3 [Constraint] requires installed(front_wheel_assy, front_chassis) [supported]; kind="inferred_precondition"; name="requires"; args=["event_9","installed","front_wheel_assy","front_chassis"]; support_status="supported"; rule_id="precondition_remove_requires_component_installed"; confidence=1.0
- N4 [Entity] base
- N5 [Entity] front_chassis
- N6 [Entity] front_wheel_assy
- N7 [Predicate] hasAction(event_9, remove); name="hasAction"; args=["event_9","remove"]; confidence=1.0
- N8 [Predicate] hasInstallTarget(front_wheel_assy, front_chassis); name="hasInstallTarget"; args=["front_wheel_assy","front_chassis"]; confidence=1.0
- N9 [Predicate] hasLabel(front_wheel_assy, front_wheel_assy); name="hasLabel"; args=["front_wheel_assy","front_wheel_assy"]; confidence=1.0
- N10 [Predicate] hasParentComponent(front_wheel_assy, front_chassis); name="hasParentComponent"; args=["front_wheel_assy","front_chassis"]; confidence=1.0
- N11 [Predicate] hasTimeWindow(event_9, 273.5, None); name="hasTimeWindow"; args=["event_9",273.5,null]; confidence=1.0
- N12 [Predicate] isA(front_wheel_assy, Component); name="isA"; args=["front_wheel_assy","Component"]; confidence=1.0
- N13 [Predicate] isA(front_wheel_assy, WheelAssembly); name="isA"; args=["front_wheel_assy","WheelAssembly"]; confidence=1.0
- N14 [Predicate] requiresInstalledBefore(front_wheel_assy, front_chassis, base); name="requiresInstalledBefore"; args=["front_wheel_assy","front_chassis","base"]; confidence=1.0
- N15 [Predicate] usesObject(event_9, front_wheel_assy); name="usesObject"; args=["event_9","front_wheel_assy"]; confidence=1.0
- N16 [Rule] effect_remove_component_from_target; rule_id="effect_remove_component_from_target"
- N17 [Rule] precondition_remove_requires_component_installed; rule_id="precondition_remove_requires_component_installed"
- N18 [Source] existing_graph_csv:edges_event_component.csv
- N19 [Source] existing_graph_csv:domain_config.yaml
- N20 [Source] existing_graph_csv:nodes_events.csv
- N21 [Source] existing_graph_csv:domain_config.yaml
- N22 [Source] existing_graph_csv:nodes_components.csv
- N23 [Source] existing_graph_csv:nodes_events.csv
- N24 [Source] existing_graph_csv:domain_config.yaml
- N25 [Step] Step 10 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N26 [Step] Step 8 [accepted]; status="accepted"; confidence=1.0; warning_count=0
- N27 [Step] Step 9 [accepted]; status="accepted"; confidence=1.0; warning_count=0
Edges:
- N27 -[DEPENDS_ON]-> N26; required_condition={"args":["front_wheel_assy","front_chassis"],"name":"installed"}; supporting_effect={"condition":{"args":["front_wheel_assy","front_chassis"],"name":"installed"},"producer_status":"accepted","provisional":false,"step_id":"event_8","type":"previous_produced_effect"}; confidence=1.0; provisional=false
- N2 -[DERIVED_FROM]-> N16
- N3 -[DERIVED_FROM]-> N17
- N7 -[DERIVED_FROM]-> N20
- N8 -[DERIVED_FROM]-> N19
- N9 -[DERIVED_FROM]-> N22
- N10 -[DERIVED_FROM]-> N21
- N11 -[DERIVED_FROM]-> N23
- N12 -[DERIVED_FROM]-> N24
- N13 -[DERIVED_FROM]-> N24
- N14 -[DERIVED_FROM]-> N19
- N15 -[DERIVED_FROM]-> N18
- N27 -[HAS_CONSTRAINT]-> N2
- N27 -[HAS_CONSTRAINT]-> N3
- N2 -[HAS_ENTITY]-> N5
- N2 -[HAS_ENTITY]-> N6
- N3 -[HAS_ENTITY]-> N5
- N3 -[HAS_ENTITY]-> N6
- N8 -[HAS_ENTITY]-> N5
- N8 -[HAS_ENTITY]-> N6
- N9 -[HAS_ENTITY]-> N6
- N10 -[HAS_ENTITY]-> N5
- N10 -[HAS_ENTITY]-> N6
- N12 -[HAS_ENTITY]-> N6
- N13 -[HAS_ENTITY]-> N6
- N14 -[HAS_ENTITY]-> N4
- N14 -[HAS_ENTITY]-> N5
- N14 -[HAS_ENTITY]-> N6
- N15 -[HAS_ENTITY]-> N6
- N27 -[HAS_PREDICATE]-> N7
- N27 -[HAS_PREDICATE]-> N8
- N27 -[HAS_PREDICATE]-> N9
- N27 -[HAS_PREDICATE]-> N10
- N27 -[HAS_PREDICATE]-> N11
- N27 -[HAS_PREDICATE]-> N12
- N27 -[HAS_PREDICATE]-> N13
- N27 -[HAS_PREDICATE]-> N14
- N27 -[HAS_PREDICATE]-> N15
- N1 -[INVALIDATED_BY]-> N2
- N26 -[NEXT]-> N27
- N27 -[NEXT]-> N25
- N27 -[PRODUCES]-> N2
- N27 -[REQUIRES]-> N3
- N3 -[SUPPORTED_BY]-> N1
- N27 -[USES]-> N6
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `removal_or_rework_error`
- Expected answer elements:
  - identify the intended acted-on object
  - compare the removed part with the current step
  - recommend resolving the mismatch before proceeding

