"""Tests for run_pipeline.py cleanup behavior."""
import importlib.util
import shutil
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_runner():
    module_path = Path(__file__).resolve().parent.parent / "scripts" / "run_pipeline.py"
    spec = importlib.util.spec_from_file_location("run_pipeline", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _paths(tmp_path):
    processed = tmp_path / "session_999"
    return SimpleNamespace(
        processed_root=processed,
        objects_dir=processed / "objects",
        graphs_dir=processed / "graphs",
        logs_dir=processed / "logs",
        debug_box_dir=processed / "graphs" / "debug_boxes",
        debug_pc_dir=processed / "graphs" / "debug_pointclouds",
        sample_vis_dir=processed / "manifests" / "sample_visualizations",
        manifests_dir=processed / "manifests",
        events_dir=processed / "events",
        queries_dir=processed / "queries",
        neo4j_dir=processed / "neo4j",
        reviews_dir=processed / "reviews" / "operations",
        assembly_reviews_dir=processed / "reviews" / "assembly",
        frame_manifest=processed / "manifests" / "frame_manifest.csv",
        manifest_validation=processed / "manifests" / "manifest_validation.json",
        object_observations=processed / "objects" / "object_observations.csv",
        object_tracks=processed / "objects" / "object_tracks.csv",
        track_summary=processed / "objects" / "track_summary.csv",
        track_debug=processed / "objects" / "track_debug.json",
        event_windows=processed / "events" / "event_windows.csv",
        track_motion_debug=processed / "objects" / "track_motion_debug.csv",
        support_state_transitions=processed / "objects" / "support_state_transitions.csv",
        events_csv=processed / "events" / "events.csv",
        event_object_roles=processed / "events" / "event_object_roles.csv",
        egg_graph=processed / "graphs" / "egg_graph.json",
        scene_state_package=processed / "graphs" / "scene_state_package.json",
        workflow_timeline=processed / "graphs" / "workflow_timeline.json",
        workflow_timeline_csv=processed / "graphs" / "workflow_timeline.csv",
        pruned_subgraph=processed / "queries" / "pruned_subgraph.json",
        query_answer=processed / "queries" / "query_answer.json",
        state_facts_json=processed / "graphs" / "state_facts.json",
        state_facts_csv=processed / "graphs" / "state_facts.csv",
        subtask_events=processed / "objects" / "subtask_events.csv",
        subtask_sequence=processed / "graphs" / "subtask_sequence.json",
        assembly_graph=processed / "graphs" / "assembly_graph.json",
        assembly_state_package=processed / "graphs" / "assembly_state_package.json",
        assembly_review_json=processed / "reviews" / "assembly" / "assembly_review.json",
        assembly_review_md=processed / "reviews" / "assembly" / "assembly_review.md",
    )


def _tmp_root():
    root = Path(__file__).resolve().parent.parent / ".tmp" / f"cleanup-test-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    return root


def test_clean_stage_outputs_removes_only_stage_owned_paths():
    runner = _load_runner()
    tmp_root = _tmp_root()
    try:
        paths = _paths(tmp_root)
        stage = runner.Stage("05", "05_build_object_observations.py", "stage 05")

        paths.object_observations.parent.mkdir(parents=True)
        paths.object_observations.write_text("old observations")
        paths.debug_box_dir.mkdir(parents=True)
        (paths.debug_box_dir / "frame_000001_detections.png").write_text("old png")
        paths.logs_dir.mkdir(parents=True)
        (paths.logs_dir / "run_metadata_05_build_object_observations.json").write_text("{}")

        downstream = paths.object_tracks
        downstream.parent.mkdir(parents=True, exist_ok=True)
        downstream.write_text("keep me")

        removed = runner._clean_stage_outputs(stage, paths)

        assert removed == 3
        assert not paths.object_observations.exists()
        assert not paths.debug_box_dir.exists()
        assert not (paths.logs_dir / "run_metadata_05_build_object_observations.json").exists()
        assert downstream.exists()
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_clean_refuses_paths_outside_session():
    runner = _load_runner()
    tmp_root = _tmp_root()
    try:
        paths = _paths(tmp_root)
        outside = tmp_root / "outside.txt"
        outside.write_text("do not touch")

        with pytest.raises(ValueError, match="outside session output"):
            runner._remove_output_path(outside, paths)

        assert outside.exists()
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_wipe_session_outputs_removes_session_root():
    runner = _load_runner()
    tmp_root = _tmp_root()
    try:
        paths = _paths(tmp_root)
        paths.processed_root.mkdir(parents=True)
        (paths.processed_root / "artifact.txt").write_text("old")

        wiped = runner._wipe_session_outputs(paths, "session_999")

        assert wiped is True
        assert not paths.processed_root.exists()
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
