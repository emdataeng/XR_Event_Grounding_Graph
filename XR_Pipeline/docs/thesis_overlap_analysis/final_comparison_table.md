# Final Comparison Table

Concise decision table for thesis positioning.

| Repository capability | Evidence (file/function) | Thesis layer | Overlap with my thesis | Complementarity | Risk level | Recommended positioning |
|---|---|---|---|---|---|---|
| Quest RGB-D ingestion and frame loading | `XR_Pipeline/src/io_utils.py`: `scan_quest_capture`, `load_rgba`, `load_depth` | Layer 1 | Low | yes | low | Treat as upstream data source, not thesis contribution. |
| Detector abstraction and model backends | `XR_Pipeline/src/detectors/base.py`: `DetectionResult`, `BaseDetector`, `load_detector`; backend classes | Layer 1 | Medium | yes | low | Use as perception provider; state that model/detector design is outside thesis scope. |
| Object vocabulary and canonical labels | `XR_Pipeline/src/vocabulary.py`: `Vocabulary`; `configs/pipeline.yaml` object vocabulary | Layer 1 | Medium | yes | low | Position as semantic input normalization, not semantic hypothesis reasoning. |
| Observation-to-track linking | `XR_Pipeline/src/tracking.py`: `compute_linkage_score`, `link_observations_to_tracks` | Layer 1 | Medium | yes | low | Use as stable object identity provider for downstream predicates. |
| Pixel/depth to world geometry | `XR_Pipeline/src/geometry.py`: `deproject_pixel_to_world`, `deproject_depth_image`, `bbox3d_from_points` | Layer 1/2 | Medium | yes | low | Treat as geometric preprocessing; note repo uses coarse/axis-aligned geometry, not thesis OBB/site abstraction. |
| Coarse spatial relation labels | `XR_Pipeline/src/geometry.py`: `spatial_relation` | Layer 2 | Medium | yes | medium | Acknowledge overlap for simple predicates like `near`; distinguish thesis predicates such as `aligned`, `inside`, `touching` from richer geometric abstraction. |
| Event window detection | `XR_Pipeline/src/events.py`: `detect_event_windows` | Layer 2 | Medium | yes | low | Position as event extraction / data processing, not rule-based reasoning. |
| EGG graph construction | `XR_Pipeline/src/egg.py`: `build_egg_graph` | Layer 2 | Medium | yes | medium | Use as event-grounded graph baseline; avoid claiming generic graph construction as novel. |
| Scene State Package | `XR_Pipeline/src/scene_state_package.py`: `build_scene_state_package` | Layer 2 | High | yes | medium | Treat as closest Layer 2 interface; distinguish thesis fact base by unary `isA`, OBB/site predicates, and multi-hypothesis semantics. |
| State facts / predicate table | `XR_Pipeline/src/state_facts.py`: `compute_state_facts`, `active_facts` | Layer 2 | High | yes | medium | Acknowledge direct predicate/fact overlap; position thesis as using predicates for formal constraint and validation reasoning. |
| Domain configuration schema | `XR_Pipeline/src/domain_config.py`: `DomainConfig`, `SubtaskTemplate`, `DependencyRule`; `configs/domain_lego.yaml` | Layer 3 | Medium | yes | medium | Treat as rule-like configuration baseline; thesis contribution is formal predicate-to-constraint and compatibility/incompatibility logic. |
| Operation event inference | `XR_Pipeline/src/operation_events.py`: `detect_operation_events`, `_pairing_allows_op` | Layer 3 | Medium | yes | medium | Call this heuristic operation inference; not equivalent to formal reasoning. Use as baseline/contrast. |
| Workflow phase segmentation | `XR_Pipeline/src/workflow_timeline.py`: `build_workflow_timeline` | Layer 3 | Low | yes | low | Position as temporal summarization, not procedural validation. |
| Subtask inference from facts/operations | `XR_Pipeline/src/subtask_events.py`: `infer_subtask_events` | Layer 3/4 | High | yes | medium | High conceptual overlap; distinguish repo status assignment (`candidate/in_progress/achieved/blocked`) from thesis step validation (`accepted/uncertain/rejected`). |
| Assembly state package | `XR_Pipeline/src/assembly_state_package.py`: `build_assembly_state_package` | Layer 3/4 | Medium | yes | medium | Treat as reasoner-ready aggregation; thesis differs by validating external hypotheses against predicates and inferred constraints. |
| Assembly graph structure | `XR_Pipeline/src/assembly_graph.py`: `build_assembly_graph` | Layer 4 | High | no | medium/high | Real overlap. Position thesis graph as over validated hypotheses with rejected alternatives excluded, not inferred subtask/subgoal status graph. |
| Query-oriented symbolic reasoner | `XR_Pipeline/src/assembly_reasoner.py`: `reason`, `answer_assembly_query`, `_why_current_step` | Layer 4 | Medium | yes | medium | Acknowledge explanation/query overlap; distinguish from decision-making validation algorithm. |
| Explanation/evidence traces | `XR_Pipeline/src/assembly_reasoner.py`: `reasoning_trace`; `subtask_events.py`: `why_this_subtask`, `supporting_facts` | Layer 4 | Medium | yes | medium | Position thesis trace as stricter: predicates + constraints + incompatibilities + aggregation + decision outcome. |
| Graph pruning and simple QA | `XR_Pipeline/src/pruning.py`: `answer_query`, `get_last_seen` | Layer 4 | Low | yes | low | Treat as retrieval/query utility, not reasoning. |
| Neo4j export/import | `XR_Pipeline/src/neo4j_export.py`: `export_neo4j_csvs`; scripts `11`, `14` | Layer 4/support | Low | yes | low | Use as persistence/query infrastructure only. |
| Detection evaluation / bakeoff | `XR_Pipeline/evaluation/metrics.py`: `match_detections_to_annotations` | Layer 4/support | Low | yes | low | Evaluation support; not part of thesis reasoning contribution. |
| IndustReal PSR baseline | `IndustReal_Pipeline/src/psr.py`: `AccumulatedConfidencePSR`, `convert_states_to_steps`, `evaluate` | Layer 3/4 | Medium | yes | medium | Position as external procedural recognition baseline, not XR predicate-constraint validation. |
| IndustReal assembly graph | `IndustReal_Pipeline/src/egg_builder.py`: `AssemblyGraph`, `build_assembly_graph`, `diff_graphs` | Layer 4 | Medium | yes | medium | Use as comparison graph; thesis graph should be framed around validated hypotheses and explanation traces. |
| Predicate-to-constraint inference | Not found; closest: `state_facts.py` predicate mapping, `assembly_graph.py` dependency constraints | Layer 3 | Low | no | low | Strong novelty point: implement formal `P_t -> C_t` rule inference. |
| Compatibility-derived incompatibility relations | Not found; closest: `_pairing_allows_op` in `operation_events.py` | Layer 3/4 | Low | no | low | Strong novelty point: first-class incompatibility relations and hard rejection. |
| Accepted / uncertain / rejected step validation | Not found; repo uses `candidate/in_progress/achieved/blocked` | Layer 4 | Low | no | low | Strong novelty point: validate externally supplied hypotheses with explicit decision taxonomy. |

## Actionable Positioning

Use the repository as:
- upstream perception and event-grounding infrastructure;
- a baseline for heuristic operation/subtask inference;
- a comparison point for graph and explanation outputs.

Protect thesis originality by emphasizing:
- formal predicate-to-constraint inference;
- compatibility rules that generate incompatibility relations;
- accepted / uncertain / rejected validation of candidate step hypotheses;
- explanation traces tied to predicates, constraints, incompatibilities, confidence aggregation, and decision outcome.
