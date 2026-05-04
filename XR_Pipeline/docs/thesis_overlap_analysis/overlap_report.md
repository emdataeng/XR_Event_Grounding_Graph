# Thesis / Repository Overlap Report

Source note: the requested `./thesis_draft/ch3_ch4.txt` was found at `thesis_overlap_analysis/thesis_draft/ch3_ch4.txt`. This report uses that draft plus code evidence captured in `repo_map.md` and `evidence_matrix.md`.

## 1. Direct Overlaps

| Thesis architecture element | Repository overlap | Evidence | Assessment |
|---|---|---|---|
| Layer 1: perception abstraction with objects, poses, labels, confidence | Implemented substantially. The repo has detector outputs, object observations, depth/world projection, vocabulary mapping, and persistent tracks. | `XR_Pipeline/src/detectors/base.py:23` `DetectionResult`; `objects.py:58` `make_observation`; `tracking.py:45` `link_observations_to_tracks`; `geometry.py:41` `deproject_pixel_to_world`; `vocabulary.py:63` `Vocabulary`. | Direct overlap, but this is explicitly outside/adjacent to your thesis scope in the draft. |
| Layer 2: spatial predicates/facts with confidence and provenance | Implemented partially. The repo derives coarse spatial/event predicates and builds traceable scene/fact packages. | `geometry.py:110` `spatial_relation`; `events.py:20` `detect_event_windows`; `scene_state_package.py:1` says relations/hypotheses/provenance/constraints; `state_facts.py:1` lists time-scoped predicates. | Direct partial overlap. Predicate vocabulary differs from your draft. |
| Layer 2: hypotheses rather than hard truth | Implemented in SSP/facts. | `scene_state_package.py:18-24` says entities are candidate objects, relations are candidate facts, hypotheses can be promoted; `state_facts.py:43` defines `candidate`, `active`, `achieved`, `invalidated`. | Direct conceptual overlap. |
| Layer 3: domain config, roles, operations, templates, dependency rules | Implemented as configuration and dataclasses. | `domain_config.py:142` `DomainConfig`; `domain_lego.yaml` sections for `assembly_predicates`, `subtask_templates`, `subgoal_templates`, `dependency_rules`, `relation_rules`; evidence matrix rows for `domain_config.py`. | Direct structural overlap, but not the same as your formal predicate-to-constraint rule engine. |
| Layer 3: higher-level inference from lower-level events/facts | Implemented as operation/subtask inference. | `operation_events.py:150` `detect_operation_events`; `subtask_events.py:84` `infer_subtask_events`; `workflow_timeline.py:66` `build_workflow_timeline`. | Direct overlap in pipeline purpose; reasoning depth is limited/heuristic. |
| Layer 4: graph structure for objects, facts, subtasks, subgoals, phases, constraints | Implemented. | `assembly_graph.py:1` module docstring lists node/edge types; `build_assembly_graph` at `assembly_graph.py:36`. | Direct overlap in graph representation. |
| Layer 4: explanation/query layer | Implemented as query-oriented symbolic reasoner. | `assembly_reasoner.py:1` says deterministic symbolic rules and supported queries; `reason` at `assembly_reasoner.py:26`; `_why_current_step` at `assembly_reasoner.py:436`; `reasoning_trace` built at `:48-58`. | Direct overlap in explanation/reporting, but not exact step-hypothesis validation. |

## 2. Complementary Components

| Component | Why it aligns but does not replace the thesis contribution | Evidence |
|---|---|---|
| Detector backends and Quest capture processing | These provide upstream perception inputs matching your Layer 1 interface, but your draft says the specific sensing/tracking/classification methods are outside scope. | `DetectionResult`, `BaseDetector`, `load_detector`; `scan_quest_capture`; `link_observations_to_tracks`; draft Layer 1 says recognition methods are outside thesis scope. |
| EGG graph construction | The EGG graph gives object/event structure, but your procedural graph is defined over validated step hypotheses, predicates, and constraints. | `egg.py:11` `build_egg_graph`; `assembly_graph.py:1` separate derived graph with subtasks/subgoals/constraints. |
| Scene State Package | SSP is a useful Layer 2 interface with entities, relations, hypotheses, observations, provenance, and constraints. It does not by itself implement your Layer 3/4 validation policy. | `scene_state_package.py:1-24`; evidence matrix marks it as Layer 2. |
| Domain YAML files | They provide object roles, predicates, subtask templates, and relation rules, but are not a formal rule evaluator over `P_t -> C_t` with incompatibility relations. | `domain_config.py`; `domain_lego.yaml` sections; no evidence of `incompatibleAction` in code search. |
| IndustReal PSR pipeline | It provides a benchmark-style procedure recognition baseline, but it operates from ASD state predictions and procedure info rather than XR predicates/constraints. | `IndustReal_Pipeline/src/psr.py:194` `AccumulatedConfidencePSR`; `convert_states_to_steps` at `:112`; `egg_builder.py:103` graph builder. |

## 3. Missing Elements

| Thesis element | Repository status | Evidence / reason |
|---|---|---|
| Oriented bounding boxes and site-level regions such as surfaces, holes, edges | Missing or uncertain. Repo evidence shows axis-aligned boxes/centers and coarse world positions, not site-level interaction regions. | `geometry.py:88` `bbox3d_from_points` computes axis-aligned box; `objects.py` stores bbox/depth stats; no evidence in matrix for sites/hole/surface regions. |
| Unary semantic predicates of the form `isA(o,T)` with multiple competing semantic hypotheses per entity | Not clearly implemented. Repo maps labels to canonical classes/roles; SSP tracks class uncertainty, but evidence does not show multiple `isA` alternatives carried as predicates. | `Vocabulary` maps raw labels to canonical classes; `scene_state_package.py` mentions uncertainty, but evidence matrix does not show `isA` predicate construction. |
| Draft predicates `aligned`, `inside`, `touching` from OBB geometry | Partially missing. Repo has `NEAR`, `ABOVE`, `BELOW`, `LEFT_OF`, `RIGHT_OF`, `FAR`, plus event/fact names like `touching_candidate`. | `geometry.py:110` `spatial_relation`; `state_facts.py:18-33` predicate list. No code evidence for `inside` or exact `aligned` except candidate operation names. |
| Formal inference rules as conjunctions of predicates producing inferred constraints `C_t` | Not clearly implemented. The repo has templates, thresholds, and dependency rules, but no general rule evaluator matching the draft algorithm. | `operation_events.py` uses thresholds; `subtask_events.py` maps ops/facts to templates; `domain_config.py` has config dataclasses. No evidence of generic `P_t -> C_t` evaluator. |
| Separate compatibility rules producing `incompatibleAction(o_i,o_j,a)` | Missing. Role pairings allow operations, but the searched code does not show incompatibility relations as first-class outputs. | `_pairing_allows_op` exists at `operation_events.py:284`; search found no `incompatibleAction` or incompatibility relation implementation. |
| Confidence aggregation policy for constraints, especially minimum aggregation over supporting predicates | Partially present but not as formal Layer 3 constraint aggregation. | `state_facts.py:356` uses `min` for co-held confidence; `workflow_timeline.py:276` averages confidence; draft requires `min` aggregation for inferred constraints. |
| Layer 4 classification exactly into `accepted / uncertain / rejected` | Missing. Repo uses `candidate`, `in_progress`, `achieved`, `blocked`, `active`, `invalidated`, etc. | `subtask_events.py:196-208`; `state_facts.py:43`; `assembly_graph.py:339-350`; search shows no exact accepted/uncertain/rejected step taxonomy. |
| Step hypotheses supplied externally and validated independently against `P_t` and `C_t` | Missing or unclear. Repo infers subtasks internally from operations/facts; it does not clearly validate external candidate hypotheses. | `subtask_events.py:84` says it infers subtask candidates from facts + operation events + domain config. |
| Rejected hypotheses recorded with supporting/conflicting predicates and constraints | Missing. Repo reports blocked/violated constraints, but no evidence of rejected hypothesis nodes/traces. | `assembly_reasoner.py:226` `_what_is_blocked`; `assembly_state_package.py` stores blocked subtasks/ambiguities, not rejected step decisions. |
| Procedural graph containing accepted and uncertain hypothesis nodes while discarding rejected ones | Partially missing. Repo graph contains subtasks/subgoals with candidate/achieved/blocked statuses, not the draft’s accepted/uncertain/rejected hypothesis graph. | `assembly_graph.py:293-332` creates candidate subgoal nodes; no exact accepted/uncertain/rejected. |

## 4. Superficial Matches

| Repository component | Why it looks like Layer 3/4 | Why it is not true thesis-style reasoning |
|---|---|---|
| `operation_events.py` | It names high-level operations like `PICK_UP`, `CONTACT`, `INSERT_CANDIDATE`, `ATTACH_CANDIDATE`. | The evidence shows threshold and event-pattern logic: contact threshold, placement proximity, align tolerance, enabled operations, and confidence caps. This is heuristic event classification, not a predicate-conjunction rule engine producing explicit constraints and incompatibility relations. |
| `workflow_timeline.py` | It segments operations into phases, resembling procedural interpretation. | It clusters/labels operation events into workflow phases. It does not validate candidate step hypotheses against predicates and inferred constraints. |
| `subtask_events.py` | It creates subtask rows with statuses and supporting facts/operations. | It maps operation/fact types to templates and assigns `candidate`, `in_progress`, `achieved`, or `blocked`; this is not the draft’s accepted/uncertain/rejected decision policy over `P_t` and `C_t`. |
| `assembly_state_package.py` | It mentions constraint satisfaction, unresolved ambiguities, likely next subtasks. | Constraint satisfaction is based on dependency rules and achieved templates; no evidence of inferred qualitative constraints such as `canInsert` or compatibility-generated incompatibilities. |
| `assembly_reasoner.py` | It calls itself a symbolic reasoner and returns reasoning traces. | It answers queries over an already-built package/graph (`what_step_now`, `what_is_achieved`, `what_is_blocked`, `likely_next`). It is primarily reporting/query logic, not the Layer 4 validation algorithm that classifies each candidate hypothesis as accepted/uncertain/rejected. |
| `pruning.py` | It answers natural-language-like graph queries. | It filters EGG graph structures by time, room, semantic class, event type, etc.; this is retrieval, not procedural validation. |
| IndustReal `AccumulatedConfidencePSR` | It uses procedural constraints and produces steps. | It is a PSR baseline over ASD category predictions and procedure metadata, not the thesis architecture of XR predicates -> inferred constraints -> step-hypothesis validation. |

## 5. Risks To Originality

| Thesis area | Risk | Justification |
|---|---|---|
| Layer 1 perception abstraction | Low | The repo implements this strongly, but the draft states sensing, tracking, and classification methods are outside the thesis contribution. Position this as upstream input/complementary infrastructure. |
| Layer 2 predicate construction | Medium | The repo already builds SSP relations/hypotheses/provenance and `state_facts.csv`. However, your draft’s stronger claims around OBB-derived `aligned/inside/touching`, multiple semantic `isA` hypotheses, site relations, and semantic-spatial refinement are not implemented in the evidence. |
| Layer 3 rule-based inference | Medium | The repo has domain configs, role pairings, operation inference, subtask templates, dependency rules, and confidence statuses. Risk is real if your contribution is described broadly as "rule-based assembly inference." Risk is lower if framed specifically as formal predicate-to-constraint reasoning with compatibility/incompatibility outputs and explicit confidence aggregation. |
| Layer 4 procedural validation | Medium | The repo has `assembly_reasoner.py`, `assembly_state_package.py`, and `assembly_graph.py`, including achieved/blocked/candidate concepts and evidence traces. But it does not implement the draft’s exact accepted/uncertain/rejected validation of external step hypotheses against `P_t` and `C_t`. |
| Explanation traces | Medium | The repo records `reasoning_trace` and evidence for current step. Your draft’s trace is more specific: supporting predicates, supporting constraints, incompatibility relations, aggregated confidence, and decision outcome. |
| Procedural graph | Medium | The repo builds an assembly graph with subtask/subgoal/constraint nodes and edges. Your graph is specifically over validated step hypotheses, retains accepted/uncertain alternatives, and excludes rejected hypotheses. |
| Compatibility rules / hard invalidation | Low | Evidence shows role-pairing checks, but no first-class incompatibility relations or hard rejection path matching the draft algorithm. This remains a clearer originality point. |

## 6. Positioning Strategy

Position the repository as an upstream XR event-grounding and heuristic assembly pipeline, not as the thesis reasoning contribution.

Concise framing:

> This repository provides perception, tracking, event grounding, and a heuristic assembly-state pipeline that can supply inputs and comparison baselines for the thesis. The thesis contribution is the formal reasoning layer that separates predicates from inferred constraints, introduces compatibility-derived incompatibility relations, validates externally supplied step hypotheses as accepted/uncertain/rejected, and records explanation traces grounded in predicates and constraints.

Use the repo as:
- evidence that Layer 1 and parts of Layer 2 are feasible upstream inputs;
- a baseline for heuristic operation/subtask inference;
- a contrast case showing why threshold pipelines and query reports are not equivalent to formal procedural validation.

Do not claim as novel:
- object detection/tracking from Quest RGB-D;
- generic event graph construction;
- simple spatial predicates like `near`;
- subtask/status graphs in general.

Safer novelty claims:
- formal distinction between predicates, inferred constraints, compatibility rules, and incompatibility relations;
- confidence aggregation for inferred constraints from supporting predicates;
- local validation of candidate step hypotheses against both predicates and constraints;
- accepted/uncertain/rejected classification with explanation traces;
- procedural graph over validated hypotheses rather than over inferred operation events alone.
