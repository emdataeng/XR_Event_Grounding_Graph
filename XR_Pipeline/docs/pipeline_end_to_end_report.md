# XR Pipeline End-to-End Report

Built from the root `README.md` execution order, current script code, path definitions, and artifact dependencies.

## Executive Summary

The pipeline is a staged artifact builder. Most stages read CSV/JSON artifacts from `data/processed/<session_id>/`, transform them, and write new artifacts back into the same session folder. The canonical execution order is documented in the root `README.md` under "Running a Session", and `scripts/run_pipeline.py` now follows that order for the base pipeline and assembly reasoning layer.

The core data path is:

```text
raw Quest capture
  -> frame_manifest.csv
  -> object_observations.csv
  -> object_tracks.csv
  -> event_windows.csv
  -> events.csv + event_object_roles.csv
  -> egg_graph.json
  -> scene_state_package.json + state_facts.csv
  -> operation_events.csv + support_state_transitions.csv
  -> workflow_timeline.json/csv
  -> subtask_events.csv + subtask_sequence.json
  -> assembly_state_package.json
  -> assembly_graph.json
  -> reviews / queries / exports
```

The README execution order intentionally separates the base EGG pipeline from the assembly reasoning layer. The assembly layer is run after the base graph exists, in this order: `09b`, `09c`, `10b`, `10c`, `10d`, `09d`, `10e`, `11b`. This lets operation events and workflow/subtask artifacts exist before the assembly state package and assembly graph are generated.

## Important Paths

Defined in `src/config.py` through `PipelinePaths`.

| Path alias | Session path | Meaning |
|---|---|---|
| `processed_root` | `data/processed/<session_id>/` | Root for all generated artifacts for one session |
| `manifests_dir` | `manifests/` | Capture inventory and validation |
| `objects_dir` | `objects/` | Observations, tracks, operations, support state, subtasks |
| `events_dir` | `events/` | Primitive event windows and natural-language event summaries |
| `graphs_dir` | `graphs/` | EGG graph, SSP, facts, timelines, assembly graph, debug image folders |
| `queries_dir` | `queries/` | Query/pruning outputs |
| `neo4j_dir` | `neo4j/` | Neo4j import CSVs and Cypher |
| `logs_dir` | `logs/` | Per-stage run metadata JSON |
| `reviews_dir` | `reviews/operations/` | Operation review bundles |
| `assembly_reviews_dir` | `reviews/assembly/` | Assembly review outputs |

## Execution Order

The root `README.md` gives this canonical manual order for a new session.

Base pipeline:

```text
01 -> 02 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 14
```

Assembly reasoning layer, run after the base pipeline:

```text
09b -> 09c -> 10b -> 10c -> 10d -> 09d -> 10e -> 11b
```

Demo queries are run after the relevant base and/or assembly artifacts exist:

```text
12
```

Optional diagnostic or alternate-input stages:

```text
03 optional visual sanity checks
04 optional legacy spatialobjects ingest
11op optional operation review
13 optional 3D debug visualizations
10f optional thesis Layer 3 constraint/incompatibility reasoning
```

## Orchestrator Behavior

The orchestrator is `scripts/run_pipeline.py`.

| Feature | Behavior |
|---|---|
| Default selected stages | Runs non-optional stages only |
| Optional visuals | `03` and `13`, enabled with `--include-visuals` |
| Optional legacy ingest | `04`, enabled with `--include-legacy` |
| Optional Neo4j import | `14`, enabled with `--include-neo4j-import` |
| Range selection | `--from-stage` and `--to-stage` slice the selected stage list inclusively |
| `--force` | Passes `--force` only to stages that implement staleness checks; deletes nothing |
| `--clean` | Before each selected stage, deletes that stage's owned local outputs |
| `--wipe-session` | Deletes `data/processed/<session_id>/` before running |
| `--dry-run` | Prints commands only |

Current `run_pipeline.py` default stage order:

```text
01, 02, 05, 06, 07, 08, 09, 10, 11,
09b, 09c, 10b, 10c, 10d, 09d, 10e, 10f, 11op, 11b, 12
```

Optional stages are inserted around that order: `03`/`13` with `--include-visuals`, `04` with `--include-legacy`, and `14` with `--include-neo4j-import`. Stage `14` is placed after `11`, matching the README's base pipeline import position.

## Main Stage Table

| Stage | Script | Purpose | Main inputs | Main outputs | Notes |
|---|---|---|---|---|---|
| 00 | `00_bootstrap_repo.py` | Create project directories and baseline files | Repo root | Directories, `.env.example`, placeholder files | Setup helper; not run by `run_pipeline.py` |
| 01 | `01_build_frame_manifest.py` | Scan raw Quest capture and build canonical frame inventory | `raw_data_root` from `pipeline.yaml`; RGB/depth/meta files | `manifests/frame_manifest.csv`; `logs/run_metadata_01_build_frame_manifest.json` | Establishes frame paths, timestamps, camera intrinsics, pose matrix columns |
| 02 | `02_validate_manifest.py` | Validate frame manifest and capture file availability | `manifests/frame_manifest.csv`; raw files referenced by manifest | `manifests/manifest_validation.json` | Does not write run metadata in current code |
| 03 optional | `03_visualize_rgb_depth_pose.py` | Visual sanity checks for RGB/depth/pose | `frame_manifest.csv`; raw RGB/depth files | `manifests/sample_visualizations/frame_*_rgb_depth.png`; `manifests/sample_visualizations/camera_trajectory.png`; `graphs/debug_pointclouds/frame_*_pointcloud.png` | Optional visual-only stage |
| 04 optional | `04_ingest_spatialobjects.py` | Legacy ingest path for `spatialobjects*.csv` | `data/raw/<session>/spatialobjects/spatialobjects*.csv` | `objects/object_observations.csv` | Optional legacy path; may conflict conceptually with stage 05 because both target `object_observations.csv` |
| 05 | `05_build_object_observations.py` | Run detector on frames, map labels, sample depth, backproject to 3D observations | `frame_manifest.csv`; raw RGB/depth; `pipeline.yaml`; `thresholds.yaml`; `object_vocabulary`; `detection_groups` | `objects/object_observations.csv`; `graphs/debug_boxes/frame_*_detections.png`; `logs/run_metadata_05_build_object_observations.json` | Applies Grounding DINO/MM-GDINO thresholds, `confidence.min_observation`, vocabulary mapping, NMS, bbox area filter |
| 06 | `06_link_object_tracks.py` | Link per-frame observations into persistent tracks | `objects/object_observations.csv`; `pipeline.yaml`; `thresholds.yaml` | `objects/object_tracks.csv`; `objects/track_summary.csv`; `objects/track_debug.json`; `logs/run_metadata_06_link_object_tracks.json` | Applies per-frame class dedupe and `tracking.min_track_observations`; ignores classes marked `ignore_for_object_tracks` |
| 07 | `07_build_event_windows.py` | Detect primitive event windows from tracks | `objects/object_tracks.csv`; optional `object_observations.csv`; thresholds event settings | `events/event_windows.csv`; `objects/track_motion_debug.csv`; `logs/run_metadata_07_build_event_windows.json` | Produces MOVE/APPEAR/DISAPPEAR/CO_LOCATE/SEPARATE/INTERACTION-style primitive events |
| 08 | `08_generate_event_summaries.py` | Add natural-language summaries and object roles for primitive events | `events/event_windows.csv`; `objects/object_tracks.csv` | `events/events.csv`; `events/event_object_roles.csv`; `logs/run_metadata_08_generate_event_summaries.json` | Deterministic rule summaries currently; no VLM path active |
| 09 | `09_build_egg_graph.py` | Build Event-Grounded Graph JSON | `objects/object_tracks.csv`; `events/events.csv`; `events/event_object_roles.csv` | `graphs/egg_graph.json`; `logs/run_metadata_09_build_egg_graph.json` | Base graph layer for primitive objects/events/rooms |
| 09b | `09b_build_scene_state_package.py` | Build Scene State Package (SSP) | `object_tracks.csv`; `object_observations.csv`; `event_windows.csv`; `event_object_roles.csv`; optional `events.csv`; optional `objects/operation_events.csv` | `graphs/scene_state_package.json`; `logs/run_metadata_09b_build_scene_state_package.json` | Relation-centric state package; operation events are optional, so SSP content depends on whether 10b already ran |
| 09c | `09c_build_state_facts.py` | Convert tracks/events/operations/support state into formal facts | optional `object_tracks.csv`; `event_windows.csv` or `events.csv`; optional `objects/operation_events.csv`; optional `support_state_transitions.csv`; domain config | `graphs/state_facts.csv`; `graphs/state_facts.json`; `logs/run_metadata_09c_build_state_facts.json` | Facts are used by subtask, assembly, and thesis reasoning layers |
| 09d | `09d_build_assembly_state_package.py` | Consolidate facts/subtasks/timeline into reasoning package | `state_facts.csv`; optional `objects/subtask_events.csv`; optional `graphs/workflow_timeline.json`; optional `graphs/assembly_graph.json`; domain config | `graphs/assembly_state_package.json`; `logs/run_metadata_09d_build_assembly_state_package.json` | README order runs this after 10d, so fresh subtasks and timeline are available. If run before 10e, assembly graph content is naturally absent unless 09d is rerun later |
| 10 | `10_prune_egg_graph.py` | Query-driven graph pruning | `graphs/egg_graph.json`; query string | `queries/pruned_subgraph.json`; `queries/query_answer.json`; `logs/run_metadata_10_prune_egg_graph.json` | Independent query/demo layer over EGG |
| 10b | `10b_build_operation_events.py` | Infer operation-level events and support-state windows | `objects/object_tracks.csv`; `events/event_windows.csv`; domain config; thresholds operation settings | `objects/operation_events.csv`; `objects/support_state_transitions.csv`; `graphs/operation_event_overlays/*.png`; `logs/run_metadata_10b_build_operation_events.json` | Domain config can override enabled operations at runtime. Metadata now hashes raw thresholds, not the mutated effective dict |
| 10c | `10c_build_workflow_timeline.py` | Group operations into workflow phases | `objects/operation_events.csv`; domain config; thresholds workflow settings | `graphs/workflow_timeline.json`; `graphs/workflow_timeline.csv`; `logs/run_metadata_10c_build_workflow_timeline.json` | Staleness-checks `10b` |
| 10d | `10d_build_subtask_events.py` | Infer subtask/step events | `object_tracks.csv`; `graphs/state_facts.csv`; `objects/operation_events.csv`; `objects/support_state_transitions.csv`; domain config | `objects/subtask_events.csv`; `graphs/subtask_sequence.json`; `logs/run_metadata_10d_build_subtask_events.json` | Does not read SSP. Subtask logic is partly domain-driven and partly hardcoded |
| 10e | `10e_build_assembly_graph.py` | Build assembly-aware graph | optional `object_tracks.csv`; `state_facts.csv`; `subtask_events.csv`; optional `egg_graph.json`; optional `workflow_timeline.json`; domain config | `graphs/assembly_graph.json`; `logs/run_metadata_10e_build_assembly_graph.json` | Combines multiple layers into one derived graph |
| 10f | `10f_run_thesis_layer3_constraints.py` | Run thesis Layer 3 constraints/incompatibility reasoning | `graphs/state_facts.csv`; `graphs/scene_state_package.json`; domain YAML; `configs/thesis_rules.yaml` | `constraints.csv`; `incompatibilities.csv`; `logs/run_metadata_10f_run_thesis_layer3_constraints.json` | Optional thesis analysis stage using `src/thesis_constraint_reasoner.py` |
| 11 | `11_export_neo4j_csv.py` | Export EGG graph to Neo4j import CSVs | `graphs/egg_graph.json` | `neo4j/nodes_rooms.csv`; `nodes_objects.csv`; `nodes_events.csv`; `edges_room_object.csv`; `edges_event_object.csv`; `edges_before.csv`; `neo4j/import.cypher` | Exports only the EGG graph layer, not full assembly graph |
| 11op | `11_build_operation_review.py` | Human-readable operation review package | `objects/operation_events.csv`; `object_tracks.csv`; `event_windows.csv`; optional SSP; optional `track_motion_debug.csv`; optional workflow timeline; debug boxes | `reviews/operations/session_review.json`; `.md`; per-operation `.json`; `.md`; copied overlay PNGs; run metadata | Review/reporting layer for operation events |
| 11b | `11b_build_assembly_review.py` | Human-readable assembly review | `graphs/assembly_state_package.json`; optional `graphs/assembly_graph.json` | `reviews/assembly/assembly_review.json`; `assembly_review.md`; run metadata | Uses `src/assembly_reasoner.py` |
| 12 | `12_demo_queries.py` | Run demo graph/workflow/assembly queries | `egg_graph.json`; optional `operation_events.csv`; optional SSP; optional workflow timeline; optional assembly state package/graph | `queries/demo_query_results.json`; `logs/run_metadata_12_demo_queries.json` | Query showcase, not part of artifact dependency core |
| 13 optional | `13_visualize_3d_debug.py` | Generate point-cloud and RGB-depth debug images | `frame_manifest.csv`; raw RGB/depth | `graphs/debug_pointclouds/frame_*_3d.png`; `frame_*_rgbd.png`; `merged_pointcloud.png` | Optional visual-only stage |
| 14 optional | `14_import_neo4j.py` | Import Neo4j CSVs into Neo4j Aura | `neo4j/*.csv`; `.env` credentials | Remote Neo4j database mutation | No local artifact output; `--wipe-all` affects database, not local session folder |

## Dependency View

The dependency graph implied by code is not strictly linear. This is the practical dependency view:

| Artifact | Produced by | Read by |
|---|---|---|
| `manifests/frame_manifest.csv` | 01 | 02, 03, 05, 13 |
| `objects/object_observations.csv` | 05 or legacy 04 | 06, 07, 09b |
| `objects/object_tracks.csv` | 06 | 07, 08, 09, 09b, 09c, 10b, 10d, 10e, 11op |
| `events/event_windows.csv` | 07 | 08, 09b, 09c, 10b, 11op |
| `objects/track_motion_debug.csv` | 07 | 11op |
| `events/events.csv` | 08 | 09, 09b, 09c fallback |
| `events/event_object_roles.csv` | 08 | 09, 09b |
| `graphs/egg_graph.json` | 09 | 10, 10e, 11, 12 |
| `graphs/scene_state_package.json` | 09b | 10f, 11op optional, 12 optional |
| `graphs/state_facts.csv/json` | 09c | 09d, 10d, 10e, 10f |
| `objects/operation_events.csv` | 10b | 09b optional, 09c optional, 10c, 10d, 11op, 12 |
| `objects/support_state_transitions.csv` | 10b | 09c optional, 10d |
| `graphs/workflow_timeline.json/csv` | 10c | 09d optional, 10e optional, 11op optional, 12 |
| `objects/subtask_events.csv` | 10d | 09d optional, 10e |
| `graphs/subtask_sequence.json` | 10d | Mostly human/debug downstream |
| `graphs/assembly_graph.json` | 10e | 09d optional if rerun after 10e, 11b, 12 |
| `graphs/assembly_state_package.json` | 09d | 11b, 12 |
| `constraints.csv`, `incompatibilities.csv` | 10f | Human inspection / thesis analysis |
| `neo4j/*.csv` | 11 | 14 |

## Subtask Layer Details

`10d_build_subtask_events.py` calls `src/subtask_events.infer_subtask_events`.

Inputs:

| Input | Role in subtask inference |
|---|---|
| `operation_events.csv` | Main driver: each operation type maps to a subtask template |
| `state_facts.csv` | Provides supporting/required facts and relation-derived candidates |
| `support_state_transitions.csv` | Generates release/place subtasks from state changes |
| `object_tracks.csv` | Provides track class labels for subtask instance names |
| `domain_lego.yaml` | Provides `subtask_templates`, dependencies, role metadata |

Important behavior:

| Mechanism | How it works |
|---|---|
| `trigger_operations` | Primary domain-config mechanism. An operation type such as `PICK_UP` maps to a template such as `pick_up_part` |
| `trigger_predicates` for operation-triggered templates | Used to collect nearby facts into `required_facts` / `supporting_facts`; usually does not create the subtask by itself |
| Support transition hardcode | `CARRIED -> RESTING` creates `release_part`; `CARRIED -> IN_CONTACT` creates `place_part` |
| Relation fact hardcode | `co_held` facts can create `co_held_parts` candidate subtasks |
| Generic fallback | If no domain templates match, hardcoded operation-to-template maps in `src/subtask_events.py` are used |
| SSP | Not read by 10d |

This is one of the confusing areas: `trigger_predicates` sounds declarative, but in the current code it is partly supporting evidence and partly used only for special relation-fact matching.

## Staleness And Metadata

Most major stages write `logs/run_metadata_<stage>.json` via `src/run_metadata.py`. Metadata stores:

| Field type | Purpose |
|---|---|
| `pipeline_config_hash` | Fingerprint of loaded `pipeline.yaml` content |
| `thresholds_hash` | Fingerprint of loaded `thresholds.yaml` content |
| file hashes when passed | Fingerprint of raw YAML bytes |
| stage extras | Counts and stage-specific provenance |

Stages with staleness checks compare the current config hashes against upstream run metadata before running. If mismatched, they warn and stop unless `--force` is used. `--force` does not clean artifacts.

## Cleanup Semantics

Implemented in `scripts/run_pipeline.py`.

| Flag | Meaning |
|---|---|
| `--force` | Ignore staleness warnings. Deletes nothing |
| `--clean` | Before each selected stage, delete that stage's owned outputs and metadata |
| `--wipe-session` | Delete the whole processed session directory before running |

Stage-specific cleaning is based on the `_stage_owned_outputs` map in `run_pipeline.py`.

## Known Architecture Friction Points

| Issue | Why it matters |
|---|---|
| `09b` optionally reads `operation_events.csv`, but runs before `10b` by default | SSP can contain or omit operation-layer content depending on prior artifacts |
| `10d.trigger_predicates` semantics are misleading | YAML suggests fact-driven triggers, code often uses them as supporting evidence |
| Stage 04 and stage 05 can both write `object_observations.csv` | Legacy ingest and detector-derived observations share the same target |
| Review/query stages mix many optional inputs | Outputs can silently become less rich depending on which optional upstream artifacts exist |
| EGG graph export is not assembly graph export | Stage 11 exports `egg_graph.json`, not `assembly_graph.json` |

## Suggested Mental Model

Think of the pipeline as four layers:

| Layer | Stages | Main artifacts |
|---|---|---|
| Capture/object layer | 01-06 | Manifest, observations, tracks |
| Primitive event/EGG layer | 07-09 | Event windows, event summaries, EGG graph |
| Assembly reasoning layer | 09b, 09c, 10b-10d, 09d, 10e, optional 10f | SSP, state facts, operation events, support transitions, workflow timeline, subtasks, assembly state package, assembly graph, constraints |
| Human/export layer | 10, 11, 11op, 11b, 12, 14 | Query outputs, reviews, Neo4j CSV/import |

The README-backed order to use for a full manual run is:

```text
01 -> 02 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 14
09b -> 09c -> 10b -> 10c -> 10d -> 09d -> 10e -> 11b
12
```

Optional stages can be inserted when needed: `03`/`13` for visuals, `04` for legacy spatialobjects ingest instead of detector-derived observations, `11op` for operation review, and `10f` after `09b`/`09c` when thesis Layer 3 constraint outputs are needed.
