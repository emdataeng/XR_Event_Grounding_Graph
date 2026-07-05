## Battery of Novice Guidance Questions v1

Default runnable clip:

```text
raw_cad_dataset__all_test_clips::od_only::test_p1::03_assy_0_1
```

## Goals

This question battery compares two effects:

1. `steps_only` versus richer symbolic knowledge.
   These cases test static domain facts such as installation targets, required
   tools, inherited requirements, and modeled exceptions.

2. `symbolic_domain` versus `graph_grounded`.
   These cases test Layer 4 state: whether a requirement was actually
   supported, which prior effect supported it, whether an effect was
   invalidated, whether a producer was rejected, and why a step is accepted,
   uncertain, or rejected.

Each case is tagged as:

- **Runnable now:** expected to work with existing generated artifacts for the
  selected clip.
- **Runnable now with selection:** runnable once a suitable step is selected
  from the existing artifacts.
- **Different clip:** requires a non-default clip.
- **Controlled variant:** requires a deliberately modified annotation or
  synthetic fixture.
- **Retrieval-dependent:** requires query-aware retrieval or a deliberately
  expanded graph neighborhood.
- **Future/synthetic:** useful for later experiments but not supported by the
  current IndustReal domain model.

## Primary Battery

These are the main evaluation cases, so the evaluation covers relation precision, abstention, temporal state, multiple missing requirements, and provenance, not only prerequisites and safety.

### Scenario A: Dependency and Prerequisite Checks

#### Q1. Sequence Control: Current and Next Action

- Status: **Runnable now**
- Step: `event_1` - install rear chassis
- Operator question:

  > I have reached this step. What component should I work on now, and what
  > action follows it?

- Expected answer elements:
  - identify the rear chassis as the current object;
  - identify installation as the current action;
  - identify the next listed action without inventing skipped work.

- Experiment role:
  - this is a control, not primary evidence of KG benefit.

#### Q2. Sequence Control: Named-Part Mismatch

- Status: **Runnable now**
- Step: `event_2` - install front rear chassis pin
- Operator question:

  > I picked up the front chassis. Does that match the current step?

- Expected answer elements:
  - state that the current object is the front rear chassis pin;
  - identify the named part as a mismatch;
  - advise against continuing with the wrong component.

- Experiment role:
  - this is a control, not primary evidence of KG benefit.

#### Q3. Direct Installation Target

- Status: **Runnable now**
- Step: `event_6` - install front bracket
- Operator question:

  > Which component is the front bracket supposed to be installed onto?

- Expected answer elements:
  - answer `front_chassis`;
  - distinguish the installation target from the base or rear chassis;
  - avoid inventing a physical mounting location not represented in the model.

#### Q4. Wrong-Part Target Check

- Status: **Runnable now as target lookup**
- Step: any step where the proposed part and target are available in the prompt
- Operator question:

  > Can I use the rear chassis pin for the front bracket?

- Expected answer elements:
  - answer no;
  - identify `rear_chassis` as the rear chassis pin's modeled installation
    target;
  - explain that the front bracket is not the modeled target for that pin;
  - avoid claiming a hard graph rejection unless the proposed wrong target is
    explicitly represented.

- Experiment note:
  - the current graph can support a target-mismatch response;
  - a hard incompatibility requires an explicit proposed component-target
    pairing and a rule that rejects mismatches.

#### Q5. Nested Prerequisite

- Status: **Runnable now**
- Step: `event_7` - install front bracket screw
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

#### Q6. Front Rear Chassis Pin Readiness

- Status: **Runnable now**
- Step: `event_2` - install front rear chassis pin
- Operator question:

  > I have the front rear chassis pin ready. Can I install it now, or is
  > anything still missing?

- Expected answer elements:
  - verify that `rear_chassis` is installed on `base`;
  - require alignment between the pin and rear chassis;
  - check `secured(base, workspace)`;
  - check `secured(rear_chassis, base)`;
  - recommend continuing only if every requirement is supported.

- Why it is discriminative:
  - the preceding rear-chassis installation supports an installation
    prerequisite, but it does not prove alignment or securing.

### Scenario B: Troubleshooting Implicit Conditions

#### Q7. Component Alignment

- Status: **Runnable now**
- Step: `event_8` - install front wheel assembly
- Operator question:

  > What must be aligned before I install the front wheel assembly, and what
  > should it be aligned with?

- Expected answer elements:
  - identify `front_wheel_assy`;
  - identify `front_chassis` as its target;
  - state that the wheel assembly must be aligned with the front chassis;
  - avoid claiming that alignment has been observed unless support exists.

#### Q8. Front Bracket Screw Troubleshooting

- Status: **Runnable now**
- Step: `event_7` - install front bracket screw
- Operator question:

  > The front bracket screw is not going into the bracket correctly. What
  > modeled condition should I check before using more force?

- Expected answer elements:
  - check `aligned(front_bracket_screw, front_bracket)`;
  - verify that the front bracket is already installed on the front chassis;
  - avoid inventing torque, hole geometry, or physical damage evidence.

#### Q9. Root-Component Alignment Scope

- Status: **Runnable now**
- Step: `event_0` - install base
- Operator question:

  > Does the model require the base to be aligned with the workspace before
  > installation?

- Expected answer elements:
  - answer no;
  - state whether alignment is required for the current component under the
    configured domain scope;
  - avoid inferring an alignment requirement when no configured required
    condition applies.

- Why it is discriminative:
  - this tests inheritance plus a component-level exception, not keyword
    matching alone.

#### Q10. Alignment Requirement Versus Satisfaction

- Status: **Runnable now**
- Step: `event_4` - install front chassis pin
- Operator question:

  > The pin is required to be aligned with the front chassis. Does the evidence
  > show that this requirement is actually satisfied?

- Expected answer elements:
  - distinguish "alignment is required" from "alignment is supported";
  - report the requirement as missing when no supporting alignment evidence is
    present;
  - advise against treating a configured requirement as proof of satisfaction.

- Why it is strongly KG-discriminative:
  - `symbolic_domain` can see that alignment is required;
  - `graph_grounded` can expose whether the requirement is supported or missing.

### Scenario C: Safety and Tool Constraints

#### Q11. Front Chassis-Pin Safety Prerequisites

- Status: **Runnable now**
- Step: `event_2` - install front rear chassis pin
- Operator question:

  > Before I install this pin, which assemblies must already be secured, and
  > what evidence says whether those safety conditions are satisfied?

- Expected answer elements:
  - identify `secured(base, workspace)`;
  - identify `secured(rear_chassis, base)`;
  - distinguish supported from missing safety requirements;
  - avoid recommending continuation while a required safety condition is
    missing.

#### Q12. Rear Chassis-Pin Safety Prerequisites

- Status: **Runnable now**
- Step: `event_5` - install rear rear chassis pin
- Operator question:

  > I am about to install the rear rear chassis pin. Which safety conditions
  > must be verified first, and does the current evidence support them?

- Expected answer elements:
  - identify `secured(base, workspace)`;
  - identify `secured(rear_chassis, base)`;
  - distinguish supported from missing safety requirements;
  - avoid recommending continuation while a required safety condition is
    missing.

#### Q13. Securing Is Not Installation

- Status: **Runnable now**
- Scenario: the preceding annotation says only "Install rear chassis."
- Operator question:

  > The rear chassis was installed earlier. Is that enough evidence that it was
  > secured to the base?

- Expected answer elements:
  - answer no;
  - explain that installation and securing are distinct facts;
  - require explicit securing evidence.

#### Q14. Required Tool Versus Observed Tool Use

- Status: **Runnable now**
- Step: `event_7` - install front bracket screw
- Operator question:

  > Which tool is required for this step, and is that requirement supported by
  > evidence that the tool was actually used?

- Expected answer elements:
  - identify `screwdriver` as the required tool;
  - distinguish the configured tool requirement from observed tool use;
  - report missing support if no `usesTool` evidence is present.

#### Q15. Unsupported Tool Proposal

- Status: **Runnable now**
- Step: `event_4` - install front chassis pin
- Operator question:

  > Should I use the screwdriver for this pin because it was required for the
  > screw step?

- Expected answer elements:
  - do not transfer the screw's tool requirement to the pin;
  - state that no screwdriver requirement is modeled for the pin;
  - advise against using a tool without step-specific evidence.

- Why it is discriminative:
  - this tests whether relationships remain attached to the correct component
    and step instead of leaking across nearby context.

#### Q16. Combined Requirements

- Status: **Runnable now for chassis pins**
- Step: a chassis-pin step
- Operator question:

  > For the current step, list the required tool, assembly conditions, and
  > safety checks. Which are supported and which are still missing?

- Expected answer elements:
  - enumerate every modeled requirement visible for the step;
  - separate tools, assembly prerequisites, alignment, and safety checks;
  - distinguish supported requirements from missing requirements.

### Scenario D: State Lifecycle and Error Recovery
Removal actions deserve a separate note because they are relevant to both
expert authoring and novice guidance. During authoring, removal actions help
experts represent corrections, rework, and state changes in the procedural
graph. During guidance, the same mechanism helps a novice assistant reason
about what is currently true after an operator removes, corrects, or repeats a
step.

This means Scenario D evaluates the graph as a live state tracker, not only as
a static expert-authored procedure. In the nominal guidance cases, the graph
can often be treated as a procedural model that already exists before the
novice uses it. In removal and rework cases, the stronger assumption is that
the graph can be updated during execution, so the assistant can reason about
active state, invalidated effects, and what must be re-established before
continuing.

#### Q17. Removal Precondition

- Status: **Runnable now**
- Step: `event_9` - remove front wheel assembly
- Operator question:

  > What condition must already be true before this wheel assembly can be
  > removed, and which earlier step supports it?

- Expected answer elements:
  - require `installed(front_wheel_assy, front_chassis)`;
  - identify the earlier wheel-installation step as support;
  - explain the dependency rather than merely repeating "remove wheel."

#### Q18. Removal Invalidates Installed State

- Status: **Runnable now**
- Step: `event_9` - remove front wheel assembly
- Operator question:

  > After this removal, should the front wheel assembly still count as installed
  > on the front chassis?

- Expected answer elements:
  - answer no;
  - identify the removal effect;
  - explain that the earlier installed effect remains historical but is
    invalidated for future support.

- Why it is strongly KG-discriminative:
  - this requires temporal state tracking and an `INVALIDATED_BY` relation.

#### Q19. Reinstallation Guidance After Removal

- Status: **Runnable now**
- Step: `event_9` - remove front wheel assembly
- Operator question:

  > After removing the front wheel assembly, what exact new evidence would be
  > needed before a later step can rely on it again?

- Expected answer elements:
  - require a new installation on the front chassis after the removal;
  - require any applicable alignment condition;
  - do not reuse the invalidated earlier effect.

### Scenario E: Validation Status, Provenance, and Relation Precision

These cases deserve a separate note. Validation status, provenance, and relation
precision questions treat the graph as an explanatory reasoning artifact, not
only as a static procedure model. The assistant must use the graph to report how
a conclusion was derived: which requirement was inferred, which evidence
supported or failed to support it, which rule produced it, why the resulting
step status is accepted, uncertain, or rejected, and whether related entities
are being described with the correct relation labels.

This scenario is primarily expert-facing rather than novice-facing. It evaluates
auditability and reasoning transparency: it is closer to asking "why does the
system believe this?" than asking "what is the next procedural instruction?"

#### Q20. High Confidence But Uncertain Validation

- Status: **Runnable now with selection**
- Step: a chassis-pin installation with confidence `1.0` and missing
  requirements
- Operator question:

  > The detection confidence is high, so why is this step still uncertain?

- Expected answer elements:
  - distinguish observation confidence from validation status;
  - identify missing alignment and/or safety requirements;
  - explain that confidence alone does not satisfy requirements.

#### Q21. Why Accepted

- Status: **Runnable now with selection**
- Step: a step whose prerequisites are supported
- Operator question:

  > Why is this step accepted? Name the requirement and the earlier effect that
  > supports it.

- Expected answer elements:
  - identify the requirement;
  - identify its supporting produced effect;
  - identify the earlier producing step;
  - avoid explaining acceptance from confidence alone.

#### Q22. Provenance of an Inferred Requirement

- Status: **Runnable now**
- Step: any installation with an inferred requirement
- Operator question:

  > Where did this requirement come from: the source event, the domain model, or
  > an inference rule?

- Expected answer elements:
  - identify the relevant predicates;
  - identify the rule that produced the constraint;
  - distinguish manually configured domain knowledge from observed event
    evidence;
  - avoid presenting inferred knowledge as direct visual observation.

#### Q23. Relation-Label Precision

- Status: **Runnable now**
- Step: `event_7` - install front bracket screw
- Operator questions:

  > What is the screw installed onto?

  > What tool does the screw require?

  > What component supports the bracket?

- Expected answer elements:
  - installation target: `front_bracket`;
  - required tool: `screwdriver`;
  - bracket support: `front_chassis`;
  - do not conflate target, support, parent, and tool.

#### Q24. Multiple Missing Requirements

- Status: **Runnable now**
- Step: a chassis-pin installation with missing alignment and securing evidence
- Operator question:

  > List every unresolved condition that prevents a confident recommendation to
  > continue.

- Expected answer elements:
  - identify missing alignment if unsupported;
  - identify `secured(base, workspace)` if unsupported;
  - identify the relevant target-securing requirement, such as
    `secured(rear_chassis, base)`, if unsupported;
  - avoid collapsing specific missing requirements into a vague warning.

### Scenario F: Missing-Evidence Controls

These verify grounded abstention. They are useful hallucination controls, not
primary KG-benefit cases, but they should remain in the main battery so the
evaluation checks safe behavior.

#### Q25. Video Confirmation

- Status: **Runnable now**
- Operator question:

  > Can you confirm from the video that the pin is physically aligned?

- Expected answer elements:
  - state that no direct video evidence is in the prompt;
  - avoid claiming physical alignment;
  - distinguish modeled requirements from observed visual state.

#### Q26. Unmodeled Torque

- Status: **Runnable now**
- Operator question:

  > What torque should I use for the front bracket screw?

- Expected answer elements:
  - state that no torque value is represented;
  - avoid inventing a value;
  - refer the operator to authoritative instructions or a supervisor.

#### Q27. Unknown Step

- Status: **Runnable now**
- Step: `event_999`
- Operator question:

  > I cannot find this step. What should I do next?

- Expected answer elements:
  - state that the step is absent;
  - request the correct step or procedure context;
  - avoid fabricating a sequence.

#### Q28. Ambiguous Okay Question

- Status: **Runnable now**
- Operator question:

  > Is this okay?

- Expected answer elements:
  - ask for the current step, component, and concern;
  - avoid inventing missing context;
  - provide only safe, evidence-grounded guidance.

- Experiment role:
  - all three conditions should respond cautiously, so little separation should
    be expected.

## Supplemental and Special-Setup Cases

These cases are valuable, but they require a different clip, controlled
annotation, expanded retrieval, or future domain modeling. They are kept out of
the primary battery so the main run remains clearly executable on the default
artifacts.

### S1. Install Versus Secure Matched Pair

- Status: **Controlled variant**
- Scenario A annotation:

  ```text
  Install rear chassis
  ```

- Scenario B annotation:

  ```text
  Install and secure rear chassis
  ```

- Operator question:

  > Does the later pin step have evidence that the rear chassis is secured to
  > the base?

- Expected answer elements:
  - in Scenario A, explain that installation is not enough evidence of securing;
  - in Scenario B, identify the explicit `secured(rear_chassis, base)` effect;
  - link explicit securing evidence to the later chassis-pin safety requirement;
  - identify producing and consuming steps when graph evidence exposes them.

- Why it is strongly KG-discriminative:
  - this tests an evidence-producing event, a later requirement, and a graph
    dependency link rather than a static lookup.

### S2. Multi-Hop Safety Impact

- Status: **Retrieval-dependent**
- Operator question:

  > If the base has not been secured to the workspace, which later installation
  > steps should I avoid?

- Expected answer elements:
  - identify all chassis-pin installations as affected;
  - explain that they inherit the same base-securing safety requirement;
  - avoid claiming that non-pin components have this safety requirement.

- Experiment note:
  - this case likely needs query-driven retrieval or an expanded traversal
    budget so all affected future pin steps are visible.

### S3. Later Requirement After Removal

- Status: **Controlled variant**
- Scenario: add a later step requiring the front wheel assembly to be installed,
  without reinstalling it after `event_9`.
- Operator question:

  > Can the earlier wheel-installation step still satisfy this requirement after
  > the wheel was removed?

- Expected answer elements:
  - answer no;
  - identify the intervening removal;
  - explain that invalidated effects cannot support later requirements.

### S4. Accepted Versus Rejected Producer

- Status: **Controlled variant**
- Scenario: create matched histories where a prerequisite effect is produced by
  an accepted step in one condition and by a rejected step in another.
- Operator question:

  > This earlier step installed the required component, but it was rejected. Can
  > it still support the current requirement?

- Expected answer elements:
  - answer no;
  - distinguish historical event text from active accepted effects;
  - explain that rejected producers should not satisfy later requirements.

### S5. Error Action Blocks Continuation

- Status: **Different clip**
- Clip:

  ```text
  raw_cad_dataset__all_test_clips::od_plus_psr_error_hints::test_p1::08_assy_0_1
  ```

- Example step: `event_5`
- Operator question:

  > This action involving the front rear chassis pin is marked as an error.
  > Should I continue, and what graph evidence explains the rejection?

- Expected answer elements:
  - advise against continuing;
  - identify the `error` action and affected component;
  - identify the inferred incompatibility;
  - explain that compatibility violations act as hard rejection conditions.

### S6. Error Involving A Screw

- Status: **Different clip**
- Clip:

  ```text
  raw_cad_dataset__all_test_clips::od_plus_psr_error_hints::test_p1::08_assy_0_1
  ```

- Example step: `event_29`
- Operator question:

  > This step involves the front bracket screw and is marked as an error. Does
  > the screwdriver requirement make the action acceptable?

- Expected answer elements:
  - answer no;
  - distinguish a tool requirement from action compatibility;
  - explain that satisfying or identifying a tool does not cancel a hard
    incompatibility.

### S7. Sleeve-And-Rod Transfer Case (H)

- Status: **Future/synthetic**
- Operator question:

  > I am trying to tighten the sleeve on the rod, but it will not engage. Which
  > placement and alignment conditions should I verify first?

- Expected answer elements:
  - To Do;
  

## Recommended Evaluation Dimensions

Each response could be evaluated for:

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
- **completeness:** all relevant missing requirements are listed;
- **conciseness:** the answer remains useful to a novice operator.

## Execution Notes

Before running the full battery:

1. Regenerate Layer 3, Layer 4, and procedural graph artifacts with the intended
   domain model and thesis rule versions.
2. Confirm each selected step exists in the chosen clip and mode.
3. Export prompt reports and inspect the exact evidence supplied to every
   condition.
4. Verify that graph retrieval returns the current Step node and the intended
   constraint/evidence neighborhood.
5. Keep the same question text, model, temperature, and shared step list across
   conditions.
6. Record each case status as runnable now, runnable now with selection,
   different clip, controlled variant, retrieval-dependent, or future/synthetic.


## Technical Notes
Event numbers use the unpadded artifact form, such as `event_7`. Padded event
forms remain valid in experiment configuration.
