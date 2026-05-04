# Repository Map

Evidence used: root `README.md`, `XR_Pipeline/README.md`, `XR_Pipeline/docs/scripts_guide.md`, schema/config files, source filenames, imports, comments, and visible class/function names.

Layer legend:
- Layer 1 = perception / raw input abstraction
- Layer 2 = symbolic predicates / spatial facts
- Layer 3 = rule-based inference / constraints
- Layer 4 = procedural validation / reasoning / explanation
- uncertain = support or mixed-role module where one layer is not clear from evidence

## Top-Level Structure

| Folder / module | Purpose | Main inputs | Main outputs | Key classes/functions | External dependencies | Layer |
|---|---|---|---|---|---|---|
| `Quest_Capture/` | Raw Meta Quest 3 capture data; flat per-frame RGB/depth/meta files are the documented data source. | `*.png`, `*.rgba`, `*_depth.npy`, `*_depth.f32`, `*_meta.json` | Raw frames consumed by XR pipeline. | none | none visible | Layer 1 |
| `XR_Pipeline/` | Main sensor-log-first pipeline from Quest RGB-D + pose to EGG graph, assembly reasoning outputs, Neo4j export. | Quest capture folder, YAML configs. | `data/processed/<session>/` artifacts, EGG graph, assembly graph, Neo4j CSVs. | see sections below | see `requirements.txt` | uncertain |
| `IndustReal_Pipeline/` | Standalone IndustReal benchmark sub-pipeline; loads ASD/GT CSVs, runs PSR algorithms, builds EGG-style assembly graph. | IndustReal ASD result CSVs, `procedure_info.json`. | `results/*.json`, `results/summary.csv`, assembly graphs. | `load_recording`, `run_psr`, `evaluate`, `build_assembly_graph`, `diff_graphs` | `numpy`, `pandas` | Layer 3 |
| `Instructions/` | Implementation guide notebook. | uncertain | uncertain | none visible | Jupyter notebook format | uncertain |
| `thesis_overlap_analysis/` | Analysis workspace for thesis overlap artifacts. | repository evidence | `repo_map.md` | none | none visible | uncertain |

## XR_Pipeline Folders

| Folder / module | Purpose | Main inputs | Main outputs | Key classes/functions | External dependencies | Layer |
|---|---|---|---|---|---|---|
| `XR_Pipeline/configs/` | Pipeline, threshold, Neo4j, and domain configuration; domain configs define object classes, roles, workflow phases, enabled operations, predicates, subtask templates, subgoals, dependency/rule hints. | YAML config files. | Runtime parameters and domain rules. | none | YAML | Layer 3 |
| `XR_Pipeline/scripts/` | CLI stages that orchestrate the documented pipeline from bootstrap through import/review. | Configs and prior stage artifacts. | Manifest CSVs, observations, tracks, events, graphs, reviews, Neo4j outputs. | `main` in each stage script | `typer`, `rich`, `dotenv`, pipeline modules | uncertain |
| `XR_Pipeline/src/` | Core implementation modules for config, detection, tracking, events, graph assembly, symbolic facts, assembly reasoning, export, visualization. | Pipeline artifacts and configs. | DataFrames, JSON packages/graphs, CSV exports, query answers. | see source-module sections below | `pandas`, `numpy`, `pyyaml`, others by submodule | uncertain |
| `XR_Pipeline/src/detectors/` | Detector backend abstraction and implementations: Grounding DINO, MM-Grounding-DINO, YOLO, depth blobs. | RGB images, prompts/vocabulary, depth blobs where applicable. | `DetectionResult` lists / observations. | `DetectionResult`, `BaseDetector`, `load_detector`, `GroundingDINODetector`, `MMGroundingDINODetector`, `YOLODetector`, `DepthBlobDetector` | `numpy`, optional `transformers`, `torch`, `ultralytics` | Layer 1 |
| `XR_Pipeline/docs/` | Human documentation, schema docs, pipeline diagram, design notes. | Existing pipeline design and scripts. | Markdown schemas, Mermaid/PNG pipeline docs. | none | none visible | uncertain |
| `XR_Pipeline/evaluation/` | Detection evaluation and bakeoff tooling. | Annotation JSON, detection CSVs. | Per-class metrics and printed tables/dataframes. | `AnnotatedBox`, `DetectedBox`, `PerClassMetrics`, `load_annotations`, `load_detections_from_csv`, `box_iou`, `match_detections_to_annotations`, `metrics_to_dataframe`, `print_metrics_table`, `main` | `numpy`, `pandas`, `typer`, `rich` | Layer 4 |
| `XR_Pipeline/tests/` | Unit tests for workflow, vocabulary, events, facts, detection, geometry, assembly graph/reasoner, etc. | Test fixtures and source modules. | Test pass/fail results. | test functions | `pytest` implied by README | Layer 4 |
| `XR_Pipeline/neo4j/` | Neo4j Cypher import script. | Neo4j CSV exports. | Database import commands. | none | Neo4j/Cypher | Layer 4 |

## XR_Pipeline Source Modules

| Module | Purpose | Main inputs | Main outputs | Key classes/functions | External dependencies | Layer |
|---|---|---|---|---|---|---|
| `config.py` | Load pipeline/threshold/Neo4j config and define processed-data paths. | YAML files, session id. | Config dicts, `PipelinePaths`. | `PipelinePaths`, `load_pipeline_config`, `load_thresholds`, `load_neo4j_config` | `pyyaml` | uncertain |
| `io_utils.py` | Scan Quest capture and load meta/RGBA/depth files. | Capture directory, frame files. | Frame records, arrays, metadata dicts. | `scan_quest_capture`, `load_meta`, `load_rgba`, `rgba_to_rgb`, `load_depth_npy`, `load_depth_f32`, `load_depth`, `ticks_to_ns` | `numpy` | Layer 1 |
| `depth_utils.py` | Clean depth, visualize depth, extract depth blobs, convert blobs to world boxes. | Depth arrays, pose/intrinsics. | Clean depth maps, colormaps, blob/world-box data. | `clean_depth`, `depth_to_colormap`, `extract_depth_blobs`, `blob_to_world_box` | `numpy` | Layer 1 |
| `pose_utils.py` | Convert metadata pose to flat pose and validate pose sequences. | Meta pose dicts / pose lists. | Flat poses and validity checks. | `meta_to_pose_flat`, `is_valid_pose`, `poses_are_plausible` | `numpy` | Layer 1 |
| `geometry.py` | Camera/world geometry and spatial relation helpers. | Pose, depth, pixel, 3D coordinates. | World coordinates, distances, relation labels. | `quaternion_to_rotation_matrix`, `pose_to_matrix`, `deproject_pixel_to_world`, `deproject_depth_image`, `bbox3d_from_points`, `distance_3d`, `are_near`, `spatial_relation` | `numpy` | Layer 2 |
| `vocabulary.py` | Object vocabulary management and canonical labels/roles. | Configured vocabulary entries, raw labels. | Canonical object classes/prompts/roles. | `VocabEntry`, `Vocabulary`, `_normalise` | none visible | Layer 1 |
| `detection_groups.py` | Multi-pass detection groups by role/classes and cross-pass NMS. | Detection group config, base vocabulary, observations. | Group prompts, filtered detections. | `DetectionGroup`, `GroupPass`, `parse_detection_groups`, `cross_pass_nms` | none visible | Layer 1 |
| `detection_postprocess.py` | Confidence filtering and class-aware NMS for detections. | `DetectionResult` values, thresholds, vocabulary. | Filtered detections. | `postprocess_detections`, `_class_aware_nms` | `numpy` | Layer 1 |
| `objects.py` | Observation table helpers and depth stats/classification wrappers. | Detection rows, depth arrays, CSVs. | Observation records/dataframes, track dataframes. | `make_observation`, `load_observations`, `load_tracks`, `compute_depth_stats`, `classify_blob` | `pandas`, `numpy` | Layer 1 |
| `tracking.py` | Link per-frame observations into persistent object tracks. | `object_observations.csv` dataframe, thresholds. | `object_tracks.csv`, track summaries/debug. | `compute_linkage_score`, `link_observations_to_tracks`, `build_track_summary` | `pandas`, `numpy` | Layer 1 |
| `events.py` | Detect event windows and generate event summaries from tracks. | Object tracks and thresholds. | MOVE/APPEAR/DISAPPEAR/CO_LOCATE/SEPARATE/INTERACTION event rows/summaries. | `detect_event_windows`, `compute_track_motion_debug`, `generate_event_summary` | `pandas`, `numpy` | Layer 2 |
| `egg.py` | Assemble Event-Grounded Graph JSON and load/save it. | Object tracks, events, event-object roles. | `egg_graph.json`. | `build_egg_graph`, `save_egg`, `load_egg` | `pandas`, `numpy` | Layer 2 |
| `scene_state_package.py` | Build normalized Scene State Package with entities, relations, hypotheses, observations, provenance, constraints. | Tracks, observations, event windows, events, roles, config/thresholds. | `scene_state_package.json`. | `build_scene_state_package`, `save_scene_state_package`, `load_scene_state_package` | `pandas`, `numpy` | Layer 2 |
| `state_facts.py` | Compute formal time-scoped symbolic predicates and query active/predicate-specific facts. | Scene state package, operation events, event facts. | `state_facts.csv` / fact JSON. | `compute_state_facts`, `facts_to_json`, `active_facts`, `facts_for_predicate` | `pandas` | Layer 2 |
| `domain_config.py` | Load and validate domain-specific roles, operations, predicates, templates, dependency/rule configs. | Domain YAML. | `DomainConfig` and validation messages. | `DomainConfigError`, `DomainObjectClass`, `DomainPhase`, `RolePairing`, `AssemblyPredicate`, `SubtaskTemplate`, `SubgoalTemplate`, `DependencyRule`, `RelationRule`, `DomainConfig`, `load_domain_config`, `validate_domain_config` | `pyyaml` | Layer 3 |
| `operation_events.py` | Infer higher-level operation events from tracks/events/domain rules. | Tracks, events, event roles, thresholds, domain config. | `operation_events.csv`, support-state transitions. | `detect_operation_events`, `compute_support_state_transitions` | `pandas`, `numpy` | Layer 3 |
| `workflow_timeline.py` | Segment operation clusters into workflow phases. | Operation events, domain phase labels. | `workflow_timeline.json` / dataframe. | `build_workflow_timeline`, `timeline_to_df` | `pandas` | Layer 3 |
| `subtask_events.py` | Infer assembly subtasks from facts, operations, and domain templates. | State facts, operation events, domain config. | `subtask_events.csv`, sequence JSON. | `infer_subtask_events`, `subtask_sequence_json` | `pandas` | Layer 3 |
| `assembly_state_package.py` | Consolidate reasoning inputs: active facts, achieved subgoals, blocked subtasks, constraints. | State facts, subtask events, workflow timeline, domain config. | `assembly_state_package.json`. | `build_assembly_state_package` | `pandas` | Layer 3 |
| `assembly_graph.py` | Build typed assembly graph with objects, relation facts, subtasks, subgoals, phases, constraints. | Assembly state package, facts, subtasks, timeline. | `assembly_graph.json`. | `build_assembly_graph` | `pandas` | Layer 3 |
| `assembly_reasoner.py` | Symbolic assembly reasoner for queries about current step, achieved/blocked state, likely next, evidence traces. | Assembly state package, optional assembly graph. | Query result dicts/text reports. | `reason`, `answer_assembly_query` | none visible | Layer 4 |
| `workflow_queries.py` | Workflow query helper functions over operations/timeline. | Query string, operation events, timeline. | Text answers. | `answer_workflow_query` | `pandas` | Layer 4 |
| `pruning.py` | Query-driven EGG subgraph retrieval and simple answers. | EGG graph and query/time/room/class/event filters. | Pruned graph and answer text. | `prune_by_time`, `prune_by_room`, `prune_by_semantic_class`, `prune_by_event_type`, `get_last_seen`, `answer_query` | `re` | Layer 4 |
| `neo4j_export.py` | Export EGG graph to Neo4j-ready CSVs. | EGG graph JSON/dict. | Neo4j node/edge CSVs. | `export_neo4j_csvs` | `pandas` | Layer 4 |
| `run_metadata.py` | Track run metadata, file/config hashes, git commit, and stale upstream artifacts. | Files/config dicts/stage metadata. | Metadata JSON and staleness warnings. | `StalenessWarning`, `build_run_metadata`, `save_run_metadata`, `load_run_metadata`, `check_staleness`, `emit_staleness_warnings` | `subprocess` | Layer 4 |
| `viz.py` | Save RGB/depth overlays, pose trajectory, detection/blob drawings, point-cloud screenshots. | Images, depth/blobs/detections/poses. | Debug PNGs. | `save_rgb_depth_overlay`, `save_pose_trajectory`, `draw_detections_on_rgb`, `draw_blobs_on_rgb`, `save_point_cloud_screenshot` | `numpy`, visible docs imply plotting/image libs | Layer 1 |

## XR_Pipeline Script Groups

| Script group | Purpose | Main inputs | Main outputs | Key classes/functions | External dependencies | Layer |
|---|---|---|---|---|---|---|
| `00_bootstrap_repo.py` | Create output folders, schema docs, design notes, `.env.example`. | Repo paths. | Directory structure/docs/template. | `main` | `typer` | uncertain |
| `01`-`03` ingest/validation/visualization | Build and validate frame manifest; produce RGB/depth/pose visual checks. | Quest capture files, `pipeline.yaml`. | `frame_manifest.csv`, `manifest_validation.json`, visualization PNGs. | `main` | `typer`, pipeline modules | Layer 1 |
| `04`-`06` observations/tracking | Legacy spatialobjects ingest, object detection/backprojection, object track linking. | Manifest, raw frames/depth, detector config, observations. | `object_observations.csv`, debug boxes, `object_tracks.csv`, track summaries/debug. | `main` | `typer`, detector dependencies | Layer 1 |
| `07`-`09b` events/EGG/SSP | Build event windows/summaries, EGG graph, Scene State Package. | Tracks, events, roles. | `event_windows.csv`, `events.csv`, `event_object_roles.csv`, `egg_graph.json`, `scene_state_package.json`. | `main` | `typer`, `pandas` via modules | Layer 2 |
| `09c`-`10e` assembly inference | Build state facts, operation events, workflow timeline, subtask events, assembly state package, assembly graph. | SSP, events, tracks, operation/fact/domain config artifacts. | `state_facts.csv`, `operation_events.csv`, `workflow_timeline.json`, `subtask_events.csv`, `assembly_state_package.json`, `assembly_graph.json`. | `main` | `typer`, pipeline modules | Layer 3 |
| `10`, `11`, `11b`, `12`, `14` query/review/export/import | Prune/query EGG, export/import Neo4j CSVs, build operation/assembly reviews, run demo queries. | EGG/assembly graph/packages, Neo4j CSV/config/env. | Query JSON, review JSON, Neo4j CSVs/imported database. | `main` | `typer`, `neo4j`, `dotenv`, `rich` | Layer 4 |
| `13_visualize_3d_debug.py`, `sweep_grounding_dino.py`, `check_env.py` | Debug point clouds, detector threshold/prompt sweeps, environment checks. | Manifest/raw files, detector config, environment. | Debug PNGs, sweep CSVs, console checks. | `main` | `typer`, detector/visualization dependencies | Layer 4 |

## IndustReal_Pipeline Modules

| Module | Purpose | Main inputs | Main outputs | Key classes/functions | External dependencies | Layer |
|---|---|---|---|---|---|---|
| `configs/procedure_info.json` | Procedure/action-step metadata for IndustReal demo. | JSON config. | Procedure info consumed by loader/PSR/demo. | none | JSON | Layer 3 |
| `data/` | IndustReal ASD results, labels, zipped datasets. | CSV/ZIP dataset files. | Inputs to demo and loader. | none | none visible | Layer 1 |
| `src/data_loader.py` | Load IndustReal clips and derive PSR labels from ASD/GT CSVs. | Prediction CSV, GT CSV, procedure info. | Recording dict with frames, state lists, PSR GT. | `load_recording` | standard `csv`, `Path` | Layer 1 |
| `src/psr.py` | Procedure Step Recognition algorithms and evaluation. | ASD predictions, procedure info, GT/pred step lists. | PSR step predictions and metrics. | `NaivePSR`, `AccumulatedConfidencePSR`, `procedure_order_similarity`, `state_string_to_list`, `convert_states_to_steps`, `make_entry`, `get_highest_conf_prediction`, `evaluate`, `run_psr` | `numpy` | Layer 3 |
| `src/egg_builder.py` | Convert PSR step predictions into EGG-style state events and assembly graph; diff graphs. | Clip id, frame count, PSR steps, procedure info. | `AssemblyGraph`, state events, diff text. | `StateEvent`, `AssemblyGraph`, `build_assembly_graph`, `diff_graphs` | dataclasses | Layer 3 |
| `scripts/01_run_demo.py` | End-to-end IndustReal proof-of-concept demo; loads recordings, runs PSR B3, evaluates, builds graphs, saves summaries. | ASD result CSVs, `procedure_info.json`. | Per-clip JSON results and summary CSV. | `main` | `csv`, `json`, IndustReal modules | Layer 4 |
| `tests/test_psr.py` | Tests for PSR behavior. | PSR module/test fixtures. | Test pass/fail results. | test functions | `pytest` implied | Layer 4 |

## Layer Summary

| Layer | Evidence-backed modules |
|---|---|
| Layer 1 | `Quest_Capture/`, XR ingest/detection/tracking modules (`io_utils`, `depth_utils`, `pose_utils`, `detectors`, `detection_groups`, `detection_postprocess`, `objects`, `tracking`, `viz`), IndustReal `data_loader`/`data`. |
| Layer 2 | XR spatial/event/fact abstraction modules (`geometry`, `events`, `egg`, `scene_state_package`, `state_facts`). |
| Layer 3 | XR domain/rule/assembly construction modules (`configs/domain_*.yaml`, `domain_config`, `operation_events`, `workflow_timeline`, `subtask_events`, `assembly_state_package`, `assembly_graph`), IndustReal PSR and graph builder. |
| Layer 4 | XR validation/query/review/export/evaluation modules (`assembly_reasoner`, `workflow_queries`, `pruning`, `neo4j_export`, `run_metadata`, `evaluation`, tests, Neo4j import/export/review scripts), IndustReal demo/tests. |
| uncertain | Cross-cutting orchestration/support folders: top-level `XR_Pipeline/`, `XR_Pipeline/src/`, `XR_Pipeline/scripts/`, docs, instructions, bootstrap/config path plumbing. |
