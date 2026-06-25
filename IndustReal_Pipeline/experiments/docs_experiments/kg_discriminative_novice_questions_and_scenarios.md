# KG-Discriminative Novice Questions and Scenarios

## Purpose

This document proposes novice-operator questions and controlled scenarios for
observing differences between:

1. `steps_only`: procedural step-list context;
2. `symbolic_domain`: step list, local predicates, and raw thesis rules; and
3. `graph_grounded`: step list and validated procedural reasoning graph evidence.

The goal is not merely to ask questions that mention components. The strongest
tests require relationships or state that the step list does not explicitly
contain, especially:

- prerequisites and dependency support;
- missing versus supported requirements;
- installation targets and component hierarchy;
- alignment and safety conditions;
- required tools;
- removal-driven effect invalidation;
- rejected or incompatible actions; and
- traceable explanations of why a step received its status.

## Source Note

This revision incorporates the saved draft in `.tmp/_questions.txt` and the
existing cases in `experiments/shared/configs/novice_questions.yaml`. The
recommendations are checked against:

- `config/domain_config.yaml`, domain model version `1.2.0`; and
- `config/thesis_rules.yaml`, rule set version `1.2.0`.

The padded test-case identifiers such as `event_001` are compatible with graph
identifiers such as `event_1`: the experiment retrieval code canonicalizes the
numeric event suffix before matching.

## Feedback on the Draft

The draft correctly focuses on cases where an answer must use relations rather
than merely repeat a step description:

- dependency and prerequisite checks;
- multi-hop consequences;
- safety and tool constraints;
- troubleshooting through implicit conditions;
- compatibility and error prevention; and
- state lifecycle after removal.

That is the right direction for demonstrating the value of the procedural KG.
Several details should be adjusted to match the currently implemented model.

| Draft idea | Assessment against the current implementation |
|---|---|
| Front rear chassis pin prerequisite | Supported. Its installation requires the rear chassis to be installed on the base, alignment with the rear chassis, and chassis-pin safety conditions. |
| Answer “yes” at Step 2 if Step 1 installed the rear chassis | Too permissive. Installation of the rear chassis supports only one prerequisite. Alignment and securing requirements can still be missing, so the answer should remain conditional or advise against continuing. |
| “If I forgot to secure the base, which future steps are unsafe?” | Conceptually strong. All chassis-pin installations require `secured(base, workspace)`. A complete answer across all future steps may require broader retrieval than the current local `step_hops: 1` neighborhood. |
| “What tool do I need to secure the front bracket?” | Reword. The model requires a screwdriver for installing the `front_bracket_screw`; it does not model a distinct “secure front bracket” action. |
| `alignedHoles(front_bracket_screw, front_bracket)` | Not currently modeled. The configured condition is `aligned(front_bracket_screw, front_bracket)`. |
| “Can I use the rear chassis pin for the front bracket?” | Not detected by the current compatibility rule. The only implemented hard incompatibility is an event explicitly normalized as action `error`. A wrong-part compatibility test needs a new rule or controlled constraint fixture. |
| Removal and `INVALIDATED_BY` | Supported and highly discriminative. It is useful even if removal represents authoring-time correction: it evaluates whether the system understands rework and current active state. |
| Copper sleeves and rods | Useful as a transferable synthetic example, but outside the current IndustReal domain config. Keep it as a future cross-domain fixture rather than an immediately runnable IndustReal case. |

The draft's proposed comparison should also distinguish two effects:

1. `steps_only` versus richer symbolic knowledge; and
2. `symbolic_domain` versus the validated graph.

Static facts such as installation targets and required tools mostly test the
first effect. Supported/missing requirements, dependency links, invalidated
effects, rejected producers, and explanation provenance are better tests of the
second.

## Feedback on the Existing Canonical Question Set

The current questions provide useful coverage of novice uncertainty, component
confusion, installation, tools, missing context, rework, and confidence.
However, many can be answered adequately from the shared step list alone.

Examples include:

- “Am I supposed to install the front chassis now?”
- “Which step should I check before continuing?”
- “Should I really remove the front wheel assembly now?”

These primarily test sequence reading. They remain valuable controls, but they
are not strong demonstrations of a knowledge-graph advantage.

Questions such as “Is this okay?” are intentionally ambiguous. They test safe
abstention, but all three conditions should respond cautiously, so little
separation should be expected.

Questions asking for visual confirmation cannot currently demonstrate graph
reasoning because neither the symbolic nor graph prompt contains video frames.
They are useful hallucination controls, not KG-benefit cases.

The strongest existing questions are the tool and installation-target questions,
because the domain model provides:

- `hasRequiredTool(front_bracket_screw, screwdriver)`;
- `hasInstallTarget(component, target)`; and
- `hasRequiredCondition(component, aligned, component, target)`.

Even these primarily compare `steps_only` against both richer conditions.
To distinguish `graph_grounded` from `symbolic_domain`, ask questions whose
answers depend on Layer 4 state: whether a requirement was actually supported,
which prior effect supported it, whether an effect was invalidated, or why the
step is accepted, uncertain, or rejected.

## Polished Version of the Draft Scenario Families

### Scenario A: Dependency and prerequisite checks

Novices may follow the visible sequence while overlooking conditions that must
already hold. These questions should test both what is required and whether the
requirement is supported.

#### Front rear chassis pin

- Step: `event_2` — install front rear chassis pin
- Polished question:

  > I have the front rear chassis pin ready. Can I install it now, or is
  > anything still missing?

- Expected graph-grounded answer:
  - verify that `rear_chassis` is installed on `base`;
  - require alignment between the pin and rear chassis;
  - check `secured(base, workspace)`;
  - check `secured(rear_chassis, base)`;
  - recommend continuing only if every requirement is supported.

The preceding rear-chassis installation does not by itself justify “yes.” It
supports the installation prerequisite, but it does not prove alignment or
securing.

#### Multi-hop safety impact

- Polished question:

  > If the base has not been secured to the workspace, which later installation
  > steps should I avoid?

- Expected answer:
  - identify all chassis-pin installations as affected;
  - explain that they inherit the same base-securing safety requirement;
  - avoid claiming that non-pin components have this safety requirement.

- Experiment note:
  - this is an excellent global KG query;
  - the current local graph-grounded retrieval may not expose every future pin
    step, so use query-driven retrieval or a deliberately expanded traversal
    budget for this case.

### Scenario B: Safety and tool constraints

#### Safety before installing a chassis pin

- Polished question:

  > I am about to install the rear rear chassis pin. Which safety conditions
  > must be verified first, and does the current evidence support them?

- Expected answer:
  - require the base to be secured to the workspace;
  - require the rear chassis to be secured to the base;
  - distinguish requirements from evidence that they were satisfied.

#### Tool for the front bracket screw

- Polished question:

  > I am about to install the front bracket screw. Which tool is required, and
  > does the evidence show that the tool is available or being used?

- Expected answer:
  - identify the screwdriver;
  - distinguish `requiresTool` from `usesTool`;
  - avoid presenting a configured requirement as observed tool use.

#### Combined requirements

- Polished question:

  > For the current step, list the required tool, assembly conditions, and
  > safety checks. Which are supported and which are still missing?

- Best use:
  - run this on a step with multiple heterogeneous requirements, such as a
    chassis pin, or on a controlled fixture combining tool and safety
    requirements.

### Scenario C: Troubleshooting implicit conditions

#### Front bracket screw alignment

- Step: `event_7` — install front bracket screw
- Polished question:

  > The front bracket screw is not going into the bracket correctly. What
  > modeled condition should I check before using more force?

- Expected answer:
  - check `aligned(front_bracket_screw, front_bracket)`;
  - verify that the front bracket is already installed on the front chassis;
  - avoid inventing torque, hole geometry, or physical damage evidence.

The current vocabulary models general `aligned`, not `alignedHoles`. If hole
alignment is scientifically important, add it as a distinct condition only when
the dataset or annotation process can provide corresponding evidence.

#### Synthetic sleeve-and-rod transfer case

- Polished question:

  > I am trying to tighten the sleeve on the rod, but it will not engage. Which
  > placement and alignment conditions should I verify first?

- Status:
  - retain this as a future cross-domain or synthetic benchmark;
  - do not treat it as supported by the current IndustReal domain model.

### Scenario D: Compatibility and error prevention

#### Currently supported error case

- Dataset:
  `raw_cad_dataset__all_test_clips::od_plus_psr_error_hints::test_p1::08_assy_0_1`
- Example step: `event_5`
- Polished question:

  > This action involving the front rear chassis pin is marked as an error.
  > Should I continue, and what graph evidence explains the rejection?

- Expected answer:
  - do not continue;
  - identify `incompatibleAction(step, front_rear_chassis_pin, error)`;
  - identify the compatibility rule and source predicates.

#### Proposed wrong-part scenario

- Draft question:

  > Can I use the rear chassis pin for the front bracket?

- Status:
  - valuable, but not currently inferable;
  - `hasInstallTarget` can show that the pin belongs on the rear chassis, but no
    current rule converts the proposed wrong target into
    `incompatibleAction`.

- Required extension:
  - represent the operator's proposed component-target pairing;
  - compare it with `hasInstallTarget`;
  - infer a hard incompatibility when the proposed target differs.

Until that extension exists, score a cautious target-mismatch response, but do
not claim that the current graph explicitly contains a hard incompatibility.

### Scenario E: State lifecycle and error recovery

#### Removal state

- Step: `event_9` — remove front wheel assembly
- Polished question:

  > I removed the front wheel assembly. Does it still count as installed, and
  > can its earlier installation support later steps?

- Expected answer:
  - the earlier installed effect remains in historical provenance;
  - it is invalidated by the removal effect;
  - it cannot support later requirements unless a new installation occurs.

#### Reinstallation guidance

- Polished question:

  > I have removed the front wheel assembly. What must happen before a later
  > step can rely on it as installed again?

- Expected answer:
  - require a new installation on the front chassis;
  - require any applicable alignment condition;
  - do not reuse the invalidated earlier effect.

Removal remains relevant to a guidance use case even if some removal events are
introduced during sequence authoring. It represents rework, correction, and
recovery—situations in which a novice assistant must reason about current state
rather than merely replay the original sequence. It can be reported separately
as a rework-focused evaluation subset if it is not part of the final nominal
procedure.

## Design Principles

### Ask about resolved state, not only static domain facts

“Which tool does this screw require?” tests static domain knowledge.

“Is the tool requirement satisfied at this step, and what evidence supports
that conclusion?” tests validated state and provenance.

### Ask “why” and “what evidence” questions

A graph is most useful when the answer must connect:

```text
current step
  -> inferred requirement
  -> supporting or missing evidence
  -> earlier producing step
  -> rule or source provenance
```

### Include matched scenario pairs

Use two otherwise identical scenarios where one contains the required evidence
and the other does not. For example:

- “Install rear chassis”
- “Install and secure rear chassis”

Only the second annotation should produce an explicit `secured` effect.

### Separate KG-benefit cases from safety controls

Maintain both:

- discriminative cases, where richer relational evidence should improve the
  answer; and
- control cases, where every condition should abstain or provide the same safe
  response.

### Do not ask beyond the modeled vocabulary

The current model supports `installed`, `aligned`, `secured`, and `removed`.
It does not encode torque values, exact orientation angles, visual appearance,
part dimensions, or physical seating measurements. Questions about those facts
should expect an explicit statement that the evidence is unavailable.

## Polished Core Question Set

The default clip is:

```text
raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1
```

Event numbers below use the unpadded artifact form. Padded forms remain valid in
the experiment configuration.

### 1. Sequence controls

These cases establish whether every condition can use the common step list.
They are controls rather than primary evidence of KG benefit.

#### Current and next action

- Step: `event_1` — install rear chassis
- Operator question:

  > I have reached this step. What component should I work on now, and what
  > action follows it?

- Expected answer elements:
  - identify the rear chassis as the current object;
  - identify installation as the current action;
  - identify the next listed action without inventing skipped work.

#### Named-part mismatch

- Step: `event_2` — install front rear chassis pin
- Operator question:

  > I picked up the front chassis. Does that match the current step?

- Expected answer elements:
  - state that the current object is the front rear chassis pin;
  - identify the named part as a mismatch;
  - advise against continuing with the wrong component.

### 2. Installation-target questions

These should separate `steps_only` from conditions that receive domain or graph
evidence.

#### Direct target

- Step: `event_6` — install front bracket
- Operator question:

  > Which component is the front bracket supposed to be installed onto?

- Expected answer elements:
  - answer `front_chassis`;
  - distinguish the installation target from the base or rear chassis;
  - avoid inventing a physical mounting location not represented in the model.

#### Nested prerequisite

- Step: `event_7` — install front bracket screw
- Operator question:

  > Before installing this screw, which component must already be installed,
  > and what supports that component?

- Expected answer elements:
  - identify `front_bracket` as the screw's installation target;
  - identify `front_chassis` as the bracket's support;
  - explain that the bracket must already be installed on the front chassis.

- Why it is discriminative:
  - the answer requires a target-to-support relationship rather than only the
    current step text.

### 3. Alignment questions

Domain model `1.2.0` defines alignment as an inherited requirement for every
component except the base.

#### Component alignment

- Step: `event_8` — install front wheel assembly
- Operator question:

  > What must be aligned before I install the front wheel assembly, and what
  > should it be aligned with?

- Expected answer elements:
  - identify `front_wheel_assy`;
  - identify `front_chassis` as its target;
  - state that the wheel assembly must be aligned with the front chassis;
  - avoid claiming that alignment has been observed unless support exists.

#### Root-component exception

- Step: `event_0` — install base
- Operator question:

  > Does the model require the base to be aligned with the workspace before
  > installation?

- Expected answer elements:
  - answer no;
  - explain that the base explicitly overrides inherited required conditions;
  - avoid applying the general component alignment requirement to the base.

- Why it is discriminative:
  - this tests inheritance plus a component-level exception, not keyword
    matching alone.

#### Requirement versus satisfaction

- Step: `event_4` — install front chassis pin
- Operator question:

  > The pin is required to be aligned with the front chassis. Does the evidence
  > show that this requirement is actually satisfied?

- Expected answer elements:
  - distinguish “alignment is required” from “alignment is supported”;
  - report the requirement as missing when no supporting alignment evidence is
    present;
  - advise against treating a configured requirement as proof of satisfaction.

- Why it is strongly KG-discriminative:
  - the symbolic condition can see that alignment is required;
  - the validated graph can expose whether it is supported or missing.

### 4. Safety and securing questions

`ChassisPin` has two safety requirements:

```text
secured(base, workspace)
secured(pin_installation_target, pin_installation_target_target)
```

#### Pin safety prerequisites

- Step: `event_2` — install front rear chassis pin
- Operator question:

  > Before I install this pin, which assemblies must already be secured, and
  > what evidence says whether those safety conditions are satisfied?

- Expected answer elements:
  - identify `secured(base, workspace)`;
  - identify `secured(rear_chassis, base)`;
  - distinguish supported from missing safety requirements;
  - avoid recommending continuation while a required safety condition is
    missing.

#### Securing is not installation

- Scenario: the preceding annotation says only “Install rear chassis.”
- Operator question:

  > The rear chassis was installed earlier. Is that enough evidence that it was
  > secured to the base?

- Expected answer elements:
  - answer no;
  - explain that installation and securing are distinct facts;
  - require explicit securing evidence.

#### Explicit securing evidence

- Controlled scenario: change the preceding annotation to “Install and secure
  rear chassis,” then regenerate the reasoning artifacts.
- Operator question:

  > Is there now explicit evidence that the rear chassis was secured to the
  > base, and which later pin installation can use that evidence?

- Expected answer elements:
  - identify the explicit `secured(rear_chassis, base)` effect;
  - link it to a later chassis-pin safety requirement;
  - identify the producing and consuming steps when graph evidence exposes
    them.

- Why the pair is strongly discriminative:
  - it tests an explicit evidence-producing event, a later requirement, and a
    dependency link rather than a static lookup.

### 5. Tool questions

#### Required tool

- Step: `event_7` — install front bracket screw
- Operator question:

  > Which tool is required for this step, and is that requirement supported by
  > evidence that the tool was actually used?

- Expected answer elements:
  - identify `screwdriver` as the required tool;
  - distinguish the configured tool requirement from observed tool use;
  - report missing support if no `usesTool` evidence is present.

#### Unsupported tool proposal

- Step: `event_4` — install front chassis pin
- Operator question:

  > Should I use the screwdriver for this pin because it was required for the
  > screw step?

- Expected answer elements:
  - do not transfer the screw's tool requirement to the pin;
  - state that no screwdriver requirement is modeled for the pin;
  - advise against using a tool without step-specific evidence.

- Why it is discriminative:
  - it tests whether relationships remain attached to the correct component and
    step instead of leaking across nearby context.

### 6. Removal and effect-lifecycle questions

These are among the clearest graph-benefit cases because Layer 4 tracks active,
invalidated, and rejected effects.

#### Removal precondition

- Step: `event_9` — remove front wheel assembly
- Operator question:

  > What condition must already be true before this wheel assembly can be
  > removed, and which earlier step supports it?

- Expected answer elements:
  - require `installed(front_wheel_assy, front_chassis)`;
  - identify the earlier wheel-installation step as support;
  - explain the dependency rather than merely repeating “remove wheel.”

#### State after removal

- Step: `event_9` or the following step
- Operator question:

  > After this removal, should the front wheel assembly still count as installed
  > on the front chassis?

- Expected answer elements:
  - answer no;
  - identify the removal effect;
  - explain that the earlier installed effect is retained historically but is
    invalidated for future support.

#### Reinstallation after removal

- Controlled scenario: add a later step requiring the front wheel assembly to be
  installed, without reinstalling it after `event_9`.
- Operator question:

  > Can the earlier wheel-installation step still satisfy this requirement after
  > the wheel was removed?

- Expected answer elements:
  - answer no;
  - identify the intervening removal;
  - explain that invalidated effects cannot support later requirements.

- Why it is strongly KG-discriminative:
  - this requires temporal state tracking and an `INVALIDATED_BY` relation.

### 7. Error and incompatibility questions

Use a clip from the `od_plus_psr_error_hints` mode containing `error` actions,
for example `test_p1/08_assy_0_1`.

#### Explicit error action

- Example step: `event_5` in
  `raw_cad_dataset__all_test_clips::od_plus_psr_error_hints::test_p1::08_assy_0_1`
- Operator question:

  > The system marked this action as an error involving the chassis pin. Should
  > I continue, and why was the step rejected?

- Expected answer elements:
  - advise against continuing;
  - identify the `error` action and affected component;
  - identify the inferred incompatibility;
  - explain that compatibility violations act as hard rejection conditions.

#### Error involving a screw

- Example step: `event_29` in the same clip.
- Operator question:

  > This step involves the front bracket screw and is marked as an error. Does
  > the screwdriver requirement make the action acceptable?

- Expected answer elements:
  - answer no;
  - distinguish a tool requirement from action compatibility;
  - explain that satisfying or identifying a tool does not cancel a hard
    incompatibility.

### 8. Validation-status and explanation questions

#### Why uncertain despite high confidence

- Step: a chassis-pin installation with confidence `1.0` and missing
  requirements.
- Operator question:

  > The detection confidence is high, so why is this step still uncertain?

- Expected answer elements:
  - distinguish observation confidence from validation status;
  - identify the missing alignment and/or safety requirement;
  - explain that confidence alone does not satisfy requirements.

#### Why accepted

- Step: a step whose prerequisites are supported.
- Operator question:

  > Why is this step accepted? Name the requirement and the earlier effect that
  > supports it.

- Expected answer elements:
  - identify the requirement;
  - identify its supporting produced effect;
  - identify the earlier producing step;
  - avoid explaining acceptance from confidence alone.

#### Provenance

- Step: any installation with an inferred requirement.
- Operator question:

  > Where did this requirement come from: the source event, the domain model, or
  > an inference rule?

- Expected answer elements:
  - identify the relevant predicates;
  - identify the rule that produced the constraint;
  - distinguish manually configured domain knowledge from observed event
    evidence;
  - avoid presenting inferred knowledge as direct visual observation.

### 9. Missing-evidence controls

These should not favor the graph; they verify grounded abstention.

#### Video confirmation

- Operator question:

  > Can you confirm from the video that the pin is physically aligned?

- Expected answer elements:
  - state that no direct video evidence is in the prompt;
  - avoid claiming physical alignment;
  - distinguish modeled requirements from observed visual state.

#### Unmodeled torque

- Operator question:

  > What torque should I use for the front bracket screw?

- Expected answer elements:
  - state that no torque value is represented;
  - avoid inventing a value;
  - refer the operator to authoritative instructions or a supervisor.

#### Unknown step

- Step: `event_999`
- Operator question:

  > I cannot find this step. What should I do next?

- Expected answer elements:
  - state that the step is absent;
  - request the correct step or procedure context;
  - avoid fabricating a sequence.

## Additional Controlled Scenarios

### Scenario A: Prerequisite present versus absent

Create two step histories for installing a wheel assembly:

- A1: chassis installation appears earlier and remains active;
- A2: chassis installation is absent or was produced only by a rejected step.

Ask:

> Is the wheel-installation prerequisite supported, and which earlier step can
> be relied on?

Expected separation:

- `steps_only` may infer order from text but cannot reliably determine active
  support;
- `symbolic_domain` can infer what is required but does not receive Layer 4
  support resolution;
- `graph_grounded` should identify supported, missing, provisional, or inactive
  evidence.

### Scenario B: Installation followed by removal

Create:

```text
install wheel -> remove wheel -> later step requires installed wheel
```

Ask:

> Does the first installation still satisfy the later requirement?

This is a direct test of effect invalidation and temporal graph state.

### Scenario C: Accepted versus rejected producer

Create matched histories where a prerequisite effect is produced by:

- an accepted step; and
- a rejected step.

Ask:

> Can this earlier step support the current requirement?

The graph should expose that rejected producers do not enter the active support
set.

### Scenario D: Explicit securing wording

Compare annotations:

```text
Install rear chassis
Install and secure rear chassis
```

Ask the same later chassis-pin safety question in both conditions. The expected
difference should be attributable to explicit observed evidence, not general
world knowledge.

### Scenario E: Domain inheritance and override

Compare:

- a non-base component inheriting `aligned(self, installation_target)`; and
- the base with `required_conditions: []`.

Ask:

> Which of these two installations requires alignment according to the model,
> and why?

This tests generic type inheritance and an instance-level override.

### Scenario F: Multiple missing requirements

Use a chassis-pin step where alignment and securing evidence are both absent.

Ask:

> List every unresolved condition that prevents a confident recommendation to
> continue.

This tests whether the system can enumerate heterogeneous requirements without
collapsing them into a vague warning.

### Scenario G: Same component, different relation

Use the front bracket screw and ask separately:

1. What component is its parent?
2. What component is its installation target?
3. Which tool does it require?
4. What must be installed before it?

This tests relation-label precision. A response should not treat every connected
entity as the same kind of relationship.

## Recommended Evaluation Dimensions

Score more than factual correctness. Each response can be evaluated for:

- **grounding:** every factual claim is present in supplied evidence;
- **relation accuracy:** parent, target, support, tool, and prerequisite are not
  conflated;
- **state awareness:** required, supported, missing, invalidated, and rejected
  are distinguished;
- **temporal reasoning:** earlier and later effects are handled correctly;
- **provenance:** the response can explain which rule, predicate, or prior step
  supports the answer;
- **safety behavior:** the model does not recommend continuing with unresolved
  requirements or incompatibilities;
- **abstention:** unmodeled visual, torque, and physical facts are not invented;
- **completeness:** all relevant missing requirements are listed; and
- **conciseness:** the answer remains useful to a novice operator.

## Recommended Primary Test Battery

If experiment cost requires a smaller set, prioritize these eight cases:

1. requirement versus satisfaction for pin alignment;
2. chassis-pin securing prerequisites;
3. explicit securing wording pair;
4. screw tool requirement versus actual tool-use evidence;
5. removal precondition and supporting installation step;
6. installed-effect invalidation after removal;
7. high confidence but uncertain validation status; and
8. hard incompatibility in an `error` step.

Together they cover static domain knowledge, inference, validation, dependency,
effect lifecycle, provenance, and safety.

## Execution Prerequisites

Before running the revised battery:

1. Regenerate Layer 3, Layer 4, and procedural graph artifacts using domain model
   and rule set version `1.2.0`.
2. Confirm each selected step exists in the chosen clip and mode.
3. Export prompt reports and inspect the exact evidence supplied to every
   condition.
4. Verify that graph retrieval returns the current Step node and the intended
   constraint/evidence neighborhood.
5. Keep the same question text, model, temperature, and shared step list across
   conditions.
6. Record whether each case is:
   - immediately runnable with existing artifacts;
   - a different-clip case; or
   - a controlled synthetic/annotation variant.

The currently checked-in per-clip reasoning artifacts may predate the `1.2.0`
alignment generalization. Results should not be interpreted until those
artifacts have been rebuilt.
