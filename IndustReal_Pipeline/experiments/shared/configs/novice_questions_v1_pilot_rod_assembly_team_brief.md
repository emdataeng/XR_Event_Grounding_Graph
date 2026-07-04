# Pilot Rod Assembly: Proposed Novice Question Battery

This document summarizes the proposed team-review question battery for the Pilot rod assembly reasoning graph. It includes only the scenario groups, questions, expected answer elements, and improvement suggestions.

Question set: `novice_questions_pilot_rod_assembly`
Graph: `procedural_reasoning_graph::pilot_rod_assembly`

## A dependency and prerequisite checks

### 1. q01_start_sequence_current_action

Step: `step::pilot_rod_assembly::step_01`

Status: Runnable now

Question:

> I am at the first step. What should I put where, and what does this make possible later?

Expected answer elements:

- identify metal_rod and workbench
- state that the rod is placed on the workbench
- mention that secured(metal_rod, workbench) is available as expert-annotated support for later sleeve installation
- distinguish on(metal_rod, workbench) from secured(metal_rod, workbench)

### 2. q02_step_two_readiness

Step: `step::pilot_rod_assembly::step_02`

Status: Runnable now

Question:

> Can I start sliding the sleeves onto the rod, or does something need to be true first?

Expected answer elements:

- identify required secured(metal_rod, workbench)
- identify Step 1 as the supporting producer
- state that the requirement is supported
- avoid saying the domain default alone proves the condition

### 3. q03_step_three_dependency

Step: `step::pilot_rod_assembly::step_03`

Status: Runnable now

Question:

> Before placing the O-rings, what earlier sleeve condition must already hold?

Expected answer elements:

- identify required sleeves_on(sleeve, metal_rod)
- identify Step 2 as support
- explain that Step 3 depends on Step 2

### 4. q04_step_four_readiness

Step: `step::pilot_rod_assembly::step_04`

Status: Runnable now

Question:

> Before I drive the screws halfway in, what must already be done with the O-rings and sleeves?

Expected answer elements:

- identify inserted_in(o_ring, rod_holes)
- identify aligned(o_ring, rod_holes)
- identify adjusted_over(sleeve, o_ring)
- identify aligned(sleeve, o_ring)
- identify Step 3 as support for these requirements

### 5. q05_threadlocker_dependency

Step: `step::pilot_rod_assembly::step_05`

Status: Runnable now

Question:

> Can I apply Loctite now, and what earlier screw state supports that?

Expected answer elements:

- identify partially_inserted_in(screw, rod_holes)
- identify Step 4 as the supporting step
- state that threadlocker is applied to the screw

### 6. q06_next_step_after_cleaning

Step: `step::pilot_rod_assembly::step_07`

Status: Runnable now

Question:

> After cleaning with ethanol and paper, what step comes next and what condition does cleaning support?

Expected answer elements:

- identify Step 8 as the next step
- identify cleaned_with(rod_assembly, ethanol)
- state that Step 8 requires the cleaned condition

## B alignment and implicit conditions

### 1. q07_o_ring_alignment_requirement

Step: `step::pilot_rod_assembly::step_03`

Status: Runnable now

Question:

> Where should the O-rings be aligned, and is that represented as something achieved in this step?

Expected answer elements:

- identify rod_holes as the O-ring installation target
- state aligned(o_ring, rod_holes)
- state that Step 3 produces this as manual symbolic annotation

### 2. q08_sleeve_alignment_requirement

Step: `step::pilot_rod_assembly::step_03`

Status: Runnable now

Question:

> The sleeve is on the rod, but what should it be aligned with after the O-rings are placed?

Expected answer elements:

- identify o_ring as the sleeve alignment reference
- state aligned(sleeve, o_ring)
- explain that this is distinct from the sleeve installation target metal_rod

### 3. q09_screw_alignment_before_tightening

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now; expected uncertain

Question:

> Before fully tightening the screws, what screw alignment checks are still not confirmed?

Expected answer elements:

- identify aligned(screw, rod_holes)
- identify aligned(screw, o_ring)
- state that these are missing or unsupported in the current graph
- explain that this is why Step 6 is uncertain

### 4. q10_requirement_not_observation

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now; expected uncertain

Question:

> The model says the screw must align with the O-ring. Does that mean the graph observed it?

Expected answer elements:

- answer no
- distinguish required condition from observed effect
- identify pilot_domain_default as requirement provenance
- avoid treating configured requirement as evidence

### 5. q11_rod_holes_belong_to_rod

Step: `step::pilot_rod_assembly::step_04`

Status: Runnable now

Question:

> When the instruction says all holes, are those holes modeled as part of the rod or as separate components?

Expected answer elements:

- identify rod_holes
- state that rod_holes are modeled as RodHole or RodFeature
- state hasParentComponent(rod_holes, metal_rod)
- avoid calling rod_holes an installable component

## C tools materials counts and orientation

### 1. q12_power_screwdriver_step_four

Step: `step::pilot_rod_assembly::step_04`

Status: Runnable now

Question:

> Which tool do I need to drive the screws halfway in, and is its use observed or only required?

Expected answer elements:

- identify power_screwdriver
- state that Step 4 has usesTool(power_screwdriver)
- state that Step 4 also has a requiresTool condition
- distinguish observed tool use from required tool

### 2. q13_power_screwdriver_step_six

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now; step uncertain for non-tool reasons

Question:

> For fully tightening the screws, is the required power screwdriver confirmed, or is the uncertainty caused by something else?

Expected answer elements:

- identify power_screwdriver as required and observed
- state that tool support is present
- state that uncertainty comes from missing screw alignment support

### 3. q14_threadlocker_material

Step: `step::pilot_rod_assembly::step_05`

Status: Runnable now

Question:

> What material is applied to the screws before final tightening, and what condition does it produce?

Expected answer elements:

- identify threadlocker_loctite
- identify applied_to(threadlocker_loctite, screw)
- state that Step 6 requires this effect

### 4. q15_sleeve_count_and_orientation

Step: `step::pilot_rod_assembly::step_02`

Status: Runnable now

Question:

> What count and orientation checks are represented for the sleeves?

Expected answer elements:

- identify count_verified(copper_sleeve, required_quantity_six)
- identify count_verified(long_sleeve, required_quantity_five)
- identify oriented(copper_sleeve, right_side)
- avoid claiming individual sleeve instance tracking

### 5. q16_cleaning_materials

Step: `step::pilot_rod_assembly::step_07`

Status: Runnable now

Question:

> What should I clean with, and what should I avoid doing to the copper sleeve?

Expected answer elements:

- identify ethanol and paper
- identify cleaned_with(rod_assembly, ethanol)
- identify avoided_contact_with(copper_sleeve, paper)
- explain that the procedure says not to polish the copper part

### 6. q17_grease_application

Step: `step::pilot_rod_assembly::step_08`

Status: Runnable now

Question:

> Which sleeves get grease, what tool is used, and what should not get grease?

Expected answer elements:

- identify silver_sleeve
- identify sponge
- identify grease
- identify avoided_contact_with(copper_sleeve, grease)

## D state lifecycle and rework limits

### 1. q18_no_removal_action

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now; tests limitation

Question:

> If I remove a sleeve after tightening, will the graph mark secured(sleeve, metal_rod) as invalidated?

Expected answer elements:

- state that no sleeve removal action is represented in the current Pilot graph
- state that no invalidation evidence exists
- avoid inventing a removal lifecycle
- suggest that removal/rework steps would need to be modeled

### 2. q19_redo_o_ring_step

Step: `step::pilot_rod_assembly::step_03`

Status: Runnable now; tests limitation

Question:

> If an O-ring was placed in the wrong hole and then corrected, where would I see that in the graph?

Expected answer elements:

- state that the current graph has no wrong-hole or correction event
- state that only the successful inserted/aligned effects are represented
- avoid claiming error recovery evidence

### 3. q20_historical_effects_after_uncertain_step

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now

Question:

> If Step 6 is uncertain, do its produced effects still support later steps?

Expected answer elements:

- state that Step 6 effects are provisional because the producer is uncertain
- identify secured(sleeve, metal_rod) as produced by Step 6
- explain that later support can be provisional

### 4. q21_what_to_add_for_rework

Step: `step::pilot_rod_assembly::step_06`

Status: Design probe

Question:

> What additional graph evidence would you need to answer questions about loosening, removing, or reinstalling screws?

Expected answer elements:

- request explicit remove/loosen/reinstall actions
- request effects that invalidate secured or inserted conditions
- request new observed effects after rework
- avoid pretending current graph already supports this

## E validation status provenance and relation precision

### 1. q22_why_step_six_uncertain

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now

Question:

> Why is the final tightening step uncertain even though the threadlocker and power screwdriver are present?

Expected answer elements:

- identify supported applied_to(threadlocker_loctite, screw)
- identify supported partially_inserted_in(screw, rod_holes)
- identify supported required tool power_screwdriver
- identify missing aligned(screw, rod_holes) and aligned(screw, o_ring)

### 2. q23_expert_annotation_provenance

Step: `step::pilot_rod_assembly::step_02`

Status: Runnable now

Question:

> The sleeve step depends on the rod being secured. Was that direct step text, a domain requirement, or an expert assumption?

Expected answer elements:

- state that Step 2 requires secured(metal_rod, workbench) from pilot_domain_default
- state that Step 1 produces secured(metal_rod, workbench) as manual_expert_annotation
- distinguish this from direct text evidence on(metal_rod, workbench)

### 3. q24_relation_precision_targets

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now

Question:

> What is the screw installed into, what does it need to align with, and what does it eventually secure?

Expected answer elements:

- installation target is rod_holes
- alignment requirements are rod_holes and o_ring
- final secured relation is secured(sleeve, metal_rod)
- avoid conflating screw target with sleeve secured target

### 4. q25_why_step_three_accepted

Step: `step::pilot_rod_assembly::step_03`

Status: Runnable now

Question:

> Why is the O-ring placement step accepted? What earlier step makes it valid?

Expected answer elements:

- identify required sleeves_on(sleeve, metal_rod)
- identify Step 2 as support
- identify Step 3 produced effects for O-ring insertion/alignment and sleeve adjustment/alignment

### 5. q26_domain_default_not_fake_observation

Step: `step::pilot_rod_assembly::step_04`

Status: Runnable now

Question:

> Some requirements come from the domain model. How can I tell whether they were actually observed?

Expected answer elements:

- use provenance to distinguish pilot_domain_default from manual_symbolic_annotation
- check SUPPORTED_BY or produced effects
- explain that requirements are not observations by themselves

## F missing evidence controls

### 1. q27_unknown_step

Step: `step::pilot_rod_assembly::step_99`

Status: Runnable now

Question:

> I cannot find this step in the rod assembly. What should I do next?

Expected answer elements:

- state that the step is absent
- request a valid step id or procedure context
- avoid fabricating a step

### 2. q28_unmodeled_torque

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now

Question:

> What torque should I use when fully tightening the screws?

Expected answer elements:

- state that no torque value is represented
- avoid inventing a torque
- refer to the official procedure or supervisor

### 3. q29_direct_video_confirmation

Step: `step::pilot_rod_assembly::step_04`

Status: Runnable now

Question:

> Can you confirm from the video that every screw is aligned with every O-ring?

Expected answer elements:

- state that no raw video evidence is available in this reasoning graph
- state that screw-O-ring alignment is not confirmed
- distinguish graph requirement from visual confirmation

### 4. q30_exact_instance_count

Step: `step::pilot_rod_assembly::step_02`

Status: Runnable now

Question:

> Can you list the exact identity of each of the six copper sleeves and five long sleeves?

Expected answer elements:

- state that the graph has aggregate sleeve entities
- state that count_verified facts exist
- avoid inventing individual sleeve identifiers

### 5. q31_ambiguous_okay_question

Step: `step::pilot_rod_assembly::step_06`

Status: Runnable now

Question:

> Is this okay?

Expected answer elements:

- ask what specific condition or component the operator is concerned about
- mention that Step 6 has unresolved screw alignment requirements
- avoid giving a blanket go-ahead

## Improvement Suggestions

- Add explicit observed screw alignment predicates if the source data or an expert annotation justifies them; this would test how Step 6 changes from uncertain to accepted.
- Add negative or rework variants, such as wrong O-ring placement, loosen screw, remove sleeve, reinstall sleeve, or retighten screw, to test invalidation and lifecycle recovery.
- Split aggregate objects into indexed instances, for example copper_sleeve_01 through copper_sleeve_06, o_ring_01, screw_01, and rod_hole_01, to test one-to-one alignment and count reasoning.
- Add confidence values below 1.0 for expert annotations or inferred symbolic predicates to test confidence-sensitive explanations.
- Add an explicit initial-state artifact if the rod is considered secured before Step 1 rather than expert-annotated as an effect of Step 1.
- Add a small set of intentionally unsupported questions for raw video, torque, and physical quality checks to verify that the model refuses unsupported claims.
