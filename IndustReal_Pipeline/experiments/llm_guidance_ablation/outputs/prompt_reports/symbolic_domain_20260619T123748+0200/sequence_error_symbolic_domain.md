# Prompt Report: sequence_error

Generated at: 2026-06-19T11:03:28.802215+00:00

- Condition: `symbolic_domain`
- Risk type: `sequence_error`
- Cases in this report: `3`

## API Request Settings

- API base URL: `http://localhost:1234/v1`
- Model name: `mistralai/mistral-7b-instruct-v0.3`
- Temperature: `0.0`
- Max tokens: `512`

## Run Timing Statistics

These statistics cover all successful prompt interactions in this experiment run.

- Completed interactions: `19`
- Minimum prompt time: `20.39 s`
- Maximum prompt time: `120.46 s`
- Average prompt time: `51.01 s`
- Total experiment time: `00h 16m 09.28s`

## Prompt-Safe Context Sources

- Step-list artifact configured path: `experiments\llm_guidance_ablation\data\steps_od_only_test_p1_03_assy_0_1.txt`
- Step-list artifact loaded: `True`
- Windowed predicates included: `yes`
- Step-hop radius: `1`
- Thesis rules included: `yes`
- Procedural reasoning graph included: `no`

Both implemented conditions include the same frozen step-list artifact. The `symbolic_domain` condition additionally includes a deterministic predicate window around the current step and the complete `thesis_rules.yaml` file.

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### System Message

- Role: `system`

```text
You are an assistant helping a novice assembly operator. Answer using only the generated procedural steps, symbolic predicates, and thesis rules provided. Do not infer missing assembly information from general knowledge. Be concise, practical, and safety-aware. If the provided context is ambiguous or conflicting, say what is uncertain.
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

### Thesis Rules

This block is inserted into the user message for every case.

```yaml
{
  "adapter": {
    "predicates": {
      "event": {
        "has_action": {
          "name": "hasAction",
          "description": "Associates a step with its normalized action label.",
          "args": ["step_id", "action_name"],
          "enabled": true
        },
        "has_time_window": {
          "name": "hasTimeWindow",
          "description": "Associates a step with its start and end timestamps.",
          "args": ["step_id", "start_s", "end_s"],
          "enabled": true
        }
      },
      "object_interaction": {
        "uses_object": {
          "name": "usesObject",
          "description": "Associates a step with a non-tool component it acts on.",
          "args": ["step_id", "component_id"],
          "enabled": true
        },
        "uses_tool": {
          "name": "usesTool",
          "description": "Associates a step with a component whose edge role is tool.",
          "args": ["step_id", "component_id"],
          "enabled": true
        }
      },
      "entity_metadata": {
        "is_a": {
          "name": "isA",
          "description": "Associates a component with either its source normalized type or a domain generic type.",
          "args": ["component_id", "component_type"],
          "enabled": true
        },
        "has_label": {
          "name": "hasLabel",
          "description": "Associates a component with its source label.",
          "args": ["component_id", "component_label"],
          "enabled": true
        },
        "has_parent_component": {
          "name": "hasParentComponent",
          "description": "Associates a component with its parent component from the domain config.",
          "args": ["component_id", "parent_component_id"],
          "enabled": true
        },
        "has_install_target": {
          "name": "hasInstallTarget",
          "description": "Associates a component with its expected installation target from the domain config.",
          "args": ["component_id", "target_id"],
          "enabled": true
        },
        "requires_installed_before": {
          "name": "requiresInstalledBefore",
          "description": "States that a component installation requires its target to already be installed on another support.",
          "args": ["component_id", "target_id", "support_id"],
          "enabled": true
        },
        "has_required_condition": {
          "name": "hasRequiredCondition",
          "description": "Associates a component with a domain-required assembly condition.",
          "args": ["component_id", "condition_name", "arg_1", "arg_2"],
          "enabled": true
        },
        "has_safety_requirement": {
          "name": "hasSafetyRequirement",
          "description": "Associates a component with a domain-required safety condition.",
          "args": ["component_id", "condition_name", "arg_1", "arg_2"],
          "enabled": true
        },
        "has_required_tool": {
          "name": "hasRequiredTool",
          "description": "Associates a component with a tool required by the domain config.",
          "args": ["component_id", "tool_name"],
          "enabled": true
        }
      }
    }
  },
  "predicate_vocabulary": {
    "hasAction": {"arity": 2, "description": "Associates a step with its normalized action label."},
    "hasTimeWindow": {"arity": 3, "description": "Associates a step with its start and end timestamps."},
    "usesObject": {"arity": 2, "description": "Associates a step with a non-tool component it acts on."},
    "usesTool": {"arity": 2, "description": "Associates a step with a component whose edge role is tool."},
    "isA": {"arity": 2, "description": "Associates an individual with a generic class."},
    "hasLabel": {"arity": 2, "description": "Associates an individual with its display label."},
    "hasParentComponent": {"arity": 2, "description": "Associates a component with its parent component."},
    "hasInstallTarget": {"arity": 2, "description": "Associates a component with its expected installation target."},
    "requiresInstalledBefore": {"arity": 3, "description": "States that a component requires its target to be installed first."},
    "hasRequiredCondition": {"arity": 4, "description": "Associates a component with a required assembly condition."},
    "hasSafetyRequirement": {"arity": 4, "description": "Associates a component with a safety condition."},
    "hasRequiredTool": {"arity": 2, "description": "Associates a component with a required tool."},
    "requires": {"arity": 4, "description": "Layer 3 inferred precondition or assembly condition."},
    "produces": {"arity": 4, "description": "Layer 3 expected effect."},
    "requiresSafety": {"arity": 4, "description": "Layer 3 inferred safety requirement."},
    "requiresTool": {"arity": 2, "description": "Layer 3 inferred tool requirement."},
    "incompatibleAction": {"arity": 3, "description": "Layer 3 inferred incompatibility."}
  },
  "predicate_aliases": {
    "stepHasAction": "hasAction",
    "actsOn": "usesObject",
    "typeOf": "isA"
  },
  "defaults": {
    "threshold": 0.70,
    "aggregation": "min"
  },
  "validation": {
    "tau_acc": 0.70,
    "tau_unc": 0.35
  },
  "rule_types": {
    "inferred_precondition": "Derives conditions that should hold before a step is valid.",
    "expected_effect": "Derives effects that a step is expected to produce for later validation.",
    "safety_constraint": "Derives safety-related conditions that may be omitted from the step description.",
    "required_tool": "Infers tools required to perform a step.",
    "implicit_assembly_condition": "Derives technical assembly conditions required for an action to make sense.",
    "compatibility": "Identifies inadmissible action-object combinations as hard validity conditions."
  },
  "rules": [
    {
      "id": "precondition_install_requires_target_installed",
      "type": "inferred_precondition",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "install"]},
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "Component"]},
        {"name": "requiresInstalledBefore", "args": ["?component", "?target", "?support"]}
      ],
      "constraints": [
        {"name": "requires", "kind": "inferred_precondition", "args": ["?s", "installed", "?target", "?support"]}
      ]
    },
    {
      "id": "effect_install_component_on_target",
      "type": "expected_effect",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "install"]},
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "Component"]},
        {"name": "hasInstallTarget", "args": ["?component", "?target"]}
      ],
      "constraints": [
        {"name": "produces", "kind": "expected_effect", "args": ["?s", "installed", "?component", "?target"]}
      ]
    },
    {
      "id": "precondition_remove_requires_component_installed",
      "type": "inferred_precondition",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "remove"]},
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "Component"]},
        {"name": "hasInstallTarget", "args": ["?component", "?target"]}
      ],
      "constraints": [
        {"name": "requires", "kind": "inferred_precondition", "args": ["?s", "installed", "?component", "?target"]}
      ]
    },
    {
      "id": "effect_remove_component_from_target",
      "type": "expected_effect",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "remove"]},
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "Component"]},
        {"name": "hasInstallTarget", "args": ["?component", "?target"]}
      ],
      "constraints": [
        {"name": "produces", "kind": "expected_effect", "args": ["?s", "removed", "?component", "?target"]}
      ]
    },
    {
      "id": "implicit_domain_required_condition",
      "type": "implicit_assembly_condition",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "install"]},
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "ChassisPin"]},
        {"name": "hasRequiredCondition", "args": ["?component", "?condition", "?arg1", "?arg2"]}
      ],
      "constraints": [
        {"name": "requires", "kind": "implicit_assembly_condition", "args": ["?s", "?condition", "?arg1", "?arg2"]}
      ]
    },
    {
      "id": "safety_domain_requirement",
      "type": "safety_constraint",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "install"]},
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "ChassisPin"]},
        {"name": "hasSafetyRequirement", "args": ["?component", "?condition", "?arg1", "?arg2"]}
      ],
      "constraints": [
        {"name": "requiresSafety", "kind": "safety_constraint", "args": ["?s", "?condition", "?arg1", "?arg2"]}
      ]
    },
    {
      "id": "tool_domain_requirement",
      "type": "required_tool",
      "threshold": 0.70,
      "antecedents": [
        {"name": "usesObject", "args": ["?s", "?component"]},
        {"name": "isA", "args": ["?component", "Screw"]},
        {"name": "hasRequiredTool", "args": ["?component", "?tool"]}
      ],
      "constraints": [
        {"name": "requiresTool", "kind": "required_tool", "args": ["?s", "?tool"]}
      ]
    },
    {
      "id": "compat_error_action_marks_incompatibility",
      "type": "compatibility",
      "threshold": 0.70,
      "antecedents": [
        {"name": "hasAction", "args": ["?s", "error"]},
        {"name": "usesObject", "args": ["?s", "?o"]}
      ],
      "constraints": [
        {"name": "incompatibleAction", "kind": "compatibility", "args": ["?s", "?o", "error"]}
      ]
    }
  ]
}

```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.


## Case: case_001_missing_context

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_001`
- Operator question: I am not sure which part should be installed next. What should I do before continuing?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1
- step_hops: 1
- included_step_ids: ["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0", "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1", "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2"]

Selected predicates:
event_0: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0","install"] [conf=1.0]
event_0: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0",70.9,118.7] [conf=1.0]
event_0: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_0","base"] [conf=1.0]
event_0: hasLabel["base","base"] [conf=1.0]
event_0: isA["base","Base"] [conf=1.0]
event_0: isA["base","Component"] [conf=1.0]
event_0: hasInstallTarget["base","workspace"] [conf=1.0]
event_1: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1","install"] [conf=1.0]
event_1: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1",70.9,118.7] [conf=1.0]
event_1: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1","rear_chassis"] [conf=1.0]
event_1: hasLabel["rear_chassis","rear_chassis"] [conf=1.0]
event_1: isA["rear_chassis","Chassis"] [conf=1.0]
event_1: isA["rear_chassis","Component"] [conf=1.0]
event_1: hasInstallTarget["rear_chassis","base"] [conf=1.0]
event_1: requiresInstalledBefore["rear_chassis","base","workspace"] [conf=1.0]
event_2: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2","install"] [conf=1.0]
event_2: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2",70.9,118.7] [conf=1.0]
event_2: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2","front_rear_chassis_pin"] [conf=1.0]
event_2: hasLabel["front_rear_chassis_pin","front_rear_chassis_pin"] [conf=1.0]
event_2: isA["front_rear_chassis_pin","ChassisPin"] [conf=1.0]
event_2: isA["front_rear_chassis_pin","Fastener"] [conf=1.0]
event_2: isA["front_rear_chassis_pin","Component"] [conf=1.0]
event_2: hasParentComponent["front_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_2: hasInstallTarget["front_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_2: requiresInstalledBefore["front_rear_chassis_pin","rear_chassis","base"] [conf=1.0]
event_2: hasRequiredCondition["front_rear_chassis_pin","aligned","front_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_2: hasSafetyRequirement["front_rear_chassis_pin","secured","base","workspace"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `sequence_error`
- Expected answer elements:
  - identify the current procedural step
  - state the next required action
  - warn against skipping prerequisite steps

## Case: sequence_002_named_part_timing

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_002`
- Operator question: Am I supposed to install the front chassis now?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2
- step_hops: 1
- included_step_ids: ["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1", "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2", "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3"]

Selected predicates:
event_1: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1","install"] [conf=1.0]
event_1: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1",70.9,118.7] [conf=1.0]
event_1: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_1","rear_chassis"] [conf=1.0]
event_1: hasLabel["rear_chassis","rear_chassis"] [conf=1.0]
event_1: isA["rear_chassis","Chassis"] [conf=1.0]
event_1: isA["rear_chassis","Component"] [conf=1.0]
event_1: hasInstallTarget["rear_chassis","base"] [conf=1.0]
event_1: requiresInstalledBefore["rear_chassis","base","workspace"] [conf=1.0]
event_2: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2","install"] [conf=1.0]
event_2: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2",70.9,118.7] [conf=1.0]
event_2: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_2","front_rear_chassis_pin"] [conf=1.0]
event_2: hasLabel["front_rear_chassis_pin","front_rear_chassis_pin"] [conf=1.0]
event_2: isA["front_rear_chassis_pin","ChassisPin"] [conf=1.0]
event_2: isA["front_rear_chassis_pin","Fastener"] [conf=1.0]
event_2: isA["front_rear_chassis_pin","Component"] [conf=1.0]
event_2: hasParentComponent["front_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_2: hasInstallTarget["front_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_2: requiresInstalledBefore["front_rear_chassis_pin","rear_chassis","base"] [conf=1.0]
event_2: hasRequiredCondition["front_rear_chassis_pin","aligned","front_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_2: hasSafetyRequirement["front_rear_chassis_pin","secured","base","workspace"] [conf=1.0]
event_3: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3","install"] [conf=1.0]
event_3: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3",118.7,178.8] [conf=1.0]
event_3: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3","front_chassis"] [conf=1.0]
event_3: hasLabel["front_chassis","front_chassis"] [conf=1.0]
event_3: isA["front_chassis","Chassis"] [conf=1.0]
event_3: isA["front_chassis","Component"] [conf=1.0]
event_3: hasInstallTarget["front_chassis","base"] [conf=1.0]
event_3: requiresInstalledBefore["front_chassis","base","workspace"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `sequence_error`
- Expected answer elements:
  - compare the named part against the current step
  - state whether it matches the current step
  - refer to previous or next step when useful

## Case: sequence_003_after_previous_action

- Step id: `raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_004`
- Operator question: I finished the previous part and want to move on. Which step should I check before continuing?

### Selected Symbolic Predicates

```text
Predicate context window:
- center_step_id: step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4
- step_hops: 1
- included_step_ids: ["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3", "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4", "step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5"]

Selected predicates:
event_3: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3","install"] [conf=1.0]
event_3: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3",118.7,178.8] [conf=1.0]
event_3: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_3","front_chassis"] [conf=1.0]
event_3: hasLabel["front_chassis","front_chassis"] [conf=1.0]
event_3: isA["front_chassis","Chassis"] [conf=1.0]
event_3: isA["front_chassis","Component"] [conf=1.0]
event_3: hasInstallTarget["front_chassis","base"] [conf=1.0]
event_3: requiresInstalledBefore["front_chassis","base","workspace"] [conf=1.0]
event_4: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4","install"] [conf=1.0]
event_4: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4",118.7,178.8] [conf=1.0]
event_4: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_4","front_chassis_pin"] [conf=1.0]
event_4: hasLabel["front_chassis_pin","front_chassis_pin"] [conf=1.0]
event_4: isA["front_chassis_pin","ChassisPin"] [conf=1.0]
event_4: isA["front_chassis_pin","Fastener"] [conf=1.0]
event_4: isA["front_chassis_pin","Component"] [conf=1.0]
event_4: hasParentComponent["front_chassis_pin","front_chassis"] [conf=1.0]
event_4: hasInstallTarget["front_chassis_pin","front_chassis"] [conf=1.0]
event_4: requiresInstalledBefore["front_chassis_pin","front_chassis","base"] [conf=1.0]
event_4: hasRequiredCondition["front_chassis_pin","aligned","front_chassis_pin","front_chassis"] [conf=1.0]
event_4: hasSafetyRequirement["front_chassis_pin","secured","base","workspace"] [conf=1.0]
event_5: hasAction["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5","install"] [conf=1.0]
event_5: hasTimeWindow["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5",178.8,273.5] [conf=1.0]
event_5: usesObject["step::raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1::event_5","rear_rear_chassis_pin"] [conf=1.0]
event_5: hasLabel["rear_rear_chassis_pin","rear_rear_chassis_pin"] [conf=1.0]
event_5: isA["rear_rear_chassis_pin","ChassisPin"] [conf=1.0]
event_5: isA["rear_rear_chassis_pin","Fastener"] [conf=1.0]
event_5: isA["rear_rear_chassis_pin","Component"] [conf=1.0]
event_5: hasParentComponent["rear_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_5: hasInstallTarget["rear_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_5: requiresInstalledBefore["rear_rear_chassis_pin","rear_chassis","base"] [conf=1.0]
event_5: hasRequiredCondition["rear_rear_chassis_pin","aligned","rear_rear_chassis_pin","rear_chassis"] [conf=1.0]
event_5: hasSafetyRequirement["rear_rear_chassis_pin","secured","base","workspace"] [conf=1.0]
```


### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `sequence_error`
- Expected answer elements:
  - use current step id
  - mention previous and next step relationship
  - recommend confirming the current step before proceeding

