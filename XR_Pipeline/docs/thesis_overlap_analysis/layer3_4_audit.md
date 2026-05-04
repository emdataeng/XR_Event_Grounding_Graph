# Layer 3/4 Reasoning Audit

Goal: verify whether the repository really implements reasoning comparable to the thesis design, rather than only data processing, thresholds, or pipeline orchestration.

Thesis Layer 3/4 target:
- Layer 3: explicit rules over predicates, predicate-to-constraint inference, compatibility/incompatibility logic, confidence propagation, traceable support.
- Layer 4: validation of candidate step hypotheses as accepted / uncertain / rejected, with explanation traces and procedural graph structure.

## Summary Verdict

The repository implements **partial symbolic assembly processing**, but it does **not** fully implement the thesis Layer 3/4 reasoning design.

It has:
- configured roles, subtask templates, subgoal templates, dependency rules;
- operation and subtask inference from events/facts;
- statuses such as `candidate`, `in_progress`, `achieved`, `blocked`;
- graph nodes/edges for facts, subtasks, subgoals, phases, constraints;
- query functions that return current/blocked/achieved/likely-next summaries and reasoning traces.

It does not clearly have:
- a general predicate-conjunction rule engine;
- formal predicate -> inferred constraint generation;
- compatibility rules that produce explicit incompatibility relations;
- accepted / uncertain / rejected validation of externally supplied step hypotheses;
- explanation traces structured around predicates, constraints, incompatibilities, aggregated confidence, and decision outcome.

## Audit Table

| Item | Status | Evidence | Match to thesis design |
|---|---|---|---|
| 1. Explicit rules: if-then logic, rule sets | Partial | `XR_Pipeline/src/domain_config.py:104` `SubtaskTemplate` has `trigger_operations` and `trigger_predicates`; `DependencyRule` at `domain_config.py:124`; `domain_lego.yaml` contains `role_pairings`, `subtask_templates`, `subgoal_templates`, `dependency_rules`; `subtask_events.py:143-148` checks required templates before a subtask. | The repo has rule-like templates and dependency checks, but these are not a general rule set over predicates. They mostly map operation/fact types to subtask templates and check ordering. This is closer to configured pipeline logic than thesis-style inference rules. |
| 2. Predicate -> constraint inference | Not found | `state_facts.py:59-83` maps events/operations/support states to predicates; `assembly_graph.py:237-246` creates `constraint` nodes from `domain_config.dependency_rules`; `assembly_state_package.py:197-205` checks dependency-rule satisfaction. | The repo creates facts and dependency constraint nodes, but there is no evidence of rules that consume predicate sets `P_t` and infer qualitative constraints `C_t` such as `canInsert` or `requiresAlignment`. Constraint nodes are dependency/order constraints, not inferred assembly constraints from predicate conjunctions. |
| 3. Uncertainty handling: confidence propagation, not just thresholds | Partial | `state_facts.py:94-98` defines `_ACTIVE_CONFIDENCE` and candidate predicates; `state_facts.py:151-152` maps confidence to `active`/`candidate`; `state_facts.py:356` uses `min(conf_a, conf_b) * 0.9` for `co_held`; `operation_events.py` assigns capped/scaled confidences, e.g. threshold-based candidate operations; `workflow_timeline.py:276` averages confidence. | There are confidence values and some propagation-like computations. However, most status decisions are threshold/cap heuristics (`conf >= 0.65`, `conf >= 0.45`, distance thresholds, confidence caps). This does not match the thesis design’s explicit confidence aggregation over supporting predicates into inferred constraints, except in limited local cases. |
| 4. Multiple hypothesis handling | Partial | `scene_state_package.py:18-24` describes candidate facts and hypotheses; `scene_state_package.py:383-406` sends candidate/low-confidence relations to `hypotheses`; `assembly_graph.py:293-332` creates candidate subgoal nodes for candidate subtasks; `assembly_state_package.py:212-224` records low-confidence facts and blocked subtasks as unresolved ambiguities. | The repo preserves some candidates and ambiguities. It does not maintain multiple competing procedural hypotheses as alternatives for the same transition in the thesis sense. There is no evidence of hypothesis sets `H_t` evaluated independently against `P_t` and `C_t`. |
| 5. Step validation: accepted / uncertain / rejected | Not found | `subtask_events.py:196-208` assigns `candidate`, `achieved`, `in_progress`, or `blocked`; `state_facts.py:43` uses `candidate`, `active`, `achieved`, `invalidated`; `assembly_graph.py:339-350` summarizes `achieved_subgoals`, `candidate_subgoals`, `active_subtasks`, `blocked_subtasks`. | The repo has statuses, but not the thesis decision taxonomy. It infers subtasks from operation/fact evidence and classifies status by confidence/prerequisites. It does not validate externally supplied step hypotheses as `accepted`, `uncertain`, or `rejected` based on expected effects, predicates, constraints, and incompatibilities. |
| 6. Explanation traces: why a decision was made | Partial | `subtask_events.py:218-242` writes `why_this_subtask`, `supporting_facts`, and `supporting_operations`; `assembly_reasoner.py:48-58` creates `reasoning_trace`; `_why_current_step` at `assembly_reasoner.py:436-463` collects `operation:` and `fact:` evidence; `_what_is_blocked` at `assembly_reasoner.py:226-263` reports blocked steps and violated constraints. | The repo has trace/reporting artifacts, especially for query answers. These are not full thesis explanation traces because they do not record a validation decision with supporting predicates, supporting inferred constraints, incompatibility relations, aggregation method, and accepted/uncertain/rejected outcome. |
| 7. Procedural structure: graph, sequence, dependencies | Present | `assembly_graph.py:1-23` lists graph node and edge types; `build_assembly_graph` at `assembly_graph.py:36`; `assembly_graph.py:166-207` adds `achieves`, `depends_on`, and `next_candidate` edges; `subtask_events.py:398` `subtask_sequence_json`; `assembly_state_package.py:161-177` computes likely-next subtasks from prerequisites. | The repo clearly has procedural structure. It is a subtask/subgoal/dependency graph built from inferred subtasks, not the thesis procedural graph over validated step hypotheses where accepted/uncertain nodes are retained and rejected nodes are discarded. |

## Strict Reasoning Assessment

### Data Processing

These components are primarily data processing:
- `events.py:20` `detect_event_windows`: converts tracks to event windows using movement/proximity thresholds.
- `state_facts.py:112` `compute_state_facts`: maps tracks/events/operations to time-scoped fact rows.
- `scene_state_package.py:112` `build_scene_state_package`: packages entities, relations, hypotheses, observations, provenance, and constraints into JSON.
- `egg.py:11` `build_egg_graph`: assembles graph JSON from objects/events/roles.

They are important, but they do not by themselves perform Layer 3/4 reasoning.

### Heuristics / Threshold Logic

These components look like reasoning but are mostly heuristic:
- `operation_events.py:150` `detect_operation_events`: uses hand/tool/workpiece roles, event types, contact thresholds, movement windows, placement proximity, and alignment tolerance to emit operation labels.
- `subtask_events.py:84` `infer_subtask_events`: maps operations/facts to subtask templates and assigns statuses based on confidence thresholds and prerequisite checks.
- `workflow_timeline.py:66` `build_workflow_timeline`: clusters operation events into phases.

These are not thesis-style reasoning because they do not evaluate formal predicate conjunctions to infer constraints and do not validate candidate hypotheses against predicate/constraint evidence.

### Actual Reasoning-Like Components

These components are closest to reasoning:
- `domain_config.py:142` `DomainConfig`: provides a structured domain layer with roles, predicates, templates, dependency rules, and relation rules.
- `assembly_state_package.py:27` `build_assembly_state_package`: computes active facts, active subtasks, achieved/blocked subgoals, likely next subtasks, constraint satisfaction, and ambiguities.
- `assembly_graph.py:36` `build_assembly_graph`: constructs typed graph nodes and support/evidence/dependency edges.
- `assembly_reasoner.py:26` `reason`: answers structured queries and builds `reasoning_trace`.

Even here, the implementation is query/report oriented. It reasons over already-computed statuses and graph edges rather than executing the thesis validation algorithm.

## Critical Findings

1. **Explicit rule structures exist, but mostly as templates and dependencies.**
   `SubtaskTemplate`, `SubgoalTemplate`, `DependencyRule`, and domain YAML sections are real. They do not amount to a general predicate-rule engine.

2. **No clear predicate-to-constraint inference engine was found.**
   The repo maps events and operations to predicates, and creates dependency constraint nodes. It does not show rules of the form:
   `aligned(o1,o2) + inside(o1,o2) + isA(o1,Peg) + isA(o2,Hole) -> canInsert(o1,o2)`.

3. **Uncertainty is represented, but mostly operationalized through thresholds.**
   Confidence values are carried through many tables, and some derived confidences use `min` or scaling. But confidence propagation is not systematically tied to rule firing and inferred constraints.

4. **Hypotheses exist as candidates, not as a formal competing hypothesis set.**
   The repo preserves candidate facts/subgoals, but does not show multiple candidate step hypotheses for the same state transition being evaluated independently.

5. **Step validation in the thesis sense is not implemented.**
   The closest module, `subtask_events.py`, infers subtasks and assigns statuses. It is not validating supplied hypotheses as accepted/uncertain/rejected.

6. **Explanation traces are useful but not decision-complete.**
   The repo can answer "why current step" with supporting facts/operations. It does not produce the thesis trace schema: predicates, constraints, incompatibility relations, aggregation, decision outcome.

7. **Procedural graph structure is present and should be treated as a real overlap.**
   The assembly graph has typed nodes and edges for facts, subtasks, subgoals, constraints, phases, evidence, and dependencies. This is the strongest Layer 4 overlap, even though the semantics differ.

## Positioning Implication

For thesis positioning, treat the repository as:

- a strong implementation of upstream perception/event grounding;
- a partial implementation of symbolic fact packaging;
- a heuristic assembly interpretation baseline;
- a graph/query layer that resembles procedural reasoning but does not implement the thesis validation algorithm.

The safest distinction is:

> The repository infers operation/subtask statuses from events, facts, templates, and thresholds. The thesis implements formal validation of candidate procedural hypotheses against predicate and constraint evidence, including incompatibility-based rejection and explicit accepted/uncertain/rejected explanation traces.

## Item-Level Risk

| Item | Originality risk | Reason |
|---|---|---|
| Explicit rules | Medium | Domain templates/dependencies overlap with rule-like structures. |
| Predicate -> constraint inference | Low | Not found as formal inference in repo. |
| Uncertainty handling | Medium | Confidence/status machinery exists, but not full thesis propagation. |
| Multiple hypotheses | Low to medium | Candidate facts/subgoals exist; formal competing step hypotheses not found. |
| Step validation | Low | Exact accepted/uncertain/rejected validation not found. |
| Explanation traces | Medium | Evidence traces and reasoning traces exist, but less complete than thesis design. |
| Procedural structure | Medium to high | Assembly graph/subtask/subgoal/dependency structure is a real overlap. |
