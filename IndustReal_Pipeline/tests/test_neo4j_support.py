from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from src.neo4j_export import (
    DEFAULT_RUN_ID,
    export_industreal_neo4j_csvs,
    make_clip_result_id,
    make_component_id,
    make_event_id,
)
from src.neo4j_import import DELETE_ORPHAN_COMPONENTS_CYPHER, DELETE_RUN_CYPHER, load_csv_bundle


def _write_result(
    results_dir: Path,
    *,
    mode: str,
    archive: str,
    clip: str,
    events: list[dict],
    component_states: dict,
) -> None:
    out_dir = results_dir / "modes" / mode / archive / clip
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "assembly_graph.json").write_text(
        json.dumps(
            {
                "clip": clip,
                "n_frames": 20,
                "events": events,
                "component_states": component_states,
            }
        )
    )
    (out_dir / "metrics.json").write_text(
        json.dumps(
            {
                "run_mode": mode,
                "archive_name": archive,
                "split": "test",
                "clip": clip,
                "n_frames": 20,
                "state_frames_scored": 2,
                "state_accuracy": 1.0,
                "state_correct": 2,
                "gt_steps": 2,
                "predicted_steps": len(events),
                "diagnostic_predicted_steps": 1,
                "legal_state_rate": 1.0,
                "error_window_recall": 1.0 if any(e["event_type"] == "ERROR" for e in events) else None,
                "event_window_evidence_ratio": 1.0,
                "step_precision": 0.5,
                "step_recall": 1.0,
                "median_step_delay_frames": 0,
                "psr_pos": 0.5,
                "psr_f1": 0.67,
                "psr_avg_delay_s": 0.0,
                "psr_tps": 1,
                "psr_fps": 1,
                "psr_fns": 0,
            }
        )
    )


def _write_cad_catalogs(root: Path) -> tuple[Path, Path]:
    cad_dir = root / "cad"
    cad_dir.mkdir(parents=True, exist_ok=True)
    state_catalog = cad_dir / "cad_state_catalog.json"
    part_catalog = cad_dir / "cad_part_catalog.json"
    state_catalog.write_text(
        json.dumps(
            {
                "states": [
                    {
                        "state_index": 22,
                        "state_name": "11101111111",
                        "kind": "legal",
                        "component_keys": ["base", "front_chassis", "front_chassis_pin"],
                        "component_bits": [1, 1, 1],
                        "state_asset_member": "part_geometries/state22.fbx",
                    }
                ]
            }
        )
    )
    part_catalog.write_text(
        json.dumps(
            {
                "components": [
                    {"key": "base", "display_name": "base"},
                    {"key": "front_chassis", "display_name": "front chassis"},
                    {"key": "front_chassis_pin", "display_name": "front chassis pin"},
                ]
            }
        )
    )
    return state_catalog, part_catalog


def _read(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_export_industreal_neo4j_csvs_counts_and_ids(tmp_path: Path) -> None:
    results_dir = tmp_path / "results" / DEFAULT_RUN_ID
    reports_dir = tmp_path / "reports" / DEFAULT_RUN_ID
    _write_cad_catalogs(reports_dir)
    _write_result(
        results_dir,
        mode="od_only",
        archive="test_p1",
        clip="03_assy_0_1",
        events=[
            {
                "event_id": 0,
                "frame": 5,
                "time_s": 0.5,
                "event_type": "INSTALL",
                "component": "front chassis",
                "action_desc": "Install front chassis",
                "conf": 1.0,
            },
            {
                "event_id": 1,
                "frame": 8,
                "time_s": 0.8,
                "event_type": "INSTALL",
                "component": "front chassis pin",
                "action_desc": "Install front chassis pin",
                "conf": 1.0,
            },
        ],
        component_states={"base": True, "front chassis": True},
    )
    _write_result(
        results_dir,
        mode="od_plus_psr_error_hints",
        archive="test_p1",
        clip="03_assy_0_1",
        events=[
            {
                "event_id": 0,
                "frame": 5,
                "time_s": 0.5,
                "event_type": "ERROR",
                "component": "front chassis",
                "action_desc": "Incorrectly installed front chassis",
                "conf": 1.0,
            },
            {
                "event_id": 1,
                "frame": 8,
                "time_s": 0.8,
                "event_type": "INSTALL",
                "component": "front chassis pin",
                "action_desc": "Install front chassis pin",
                "conf": 1.0,
            },
        ],
        component_states={"base": True, "front chassis": None},
    )

    output_dir = tmp_path / "neo4j"
    counts = export_industreal_neo4j_csvs(results_dir=results_dir, output_dir=output_dir, reports_dir=reports_dir)

    assert counts["nodes_runs.csv"] == 1
    assert counts["nodes_modes.csv"] == 2
    assert counts["nodes_clips.csv"] == 2
    assert counts["nodes_events.csv"] == 4
    assert counts["nodes_components.csv"] == 3
    assert counts["nodes_goals.csv"] == 2
    assert counts["nodes_phases.csv"] == 4
    assert counts["edges_event_next.csv"] == 2
    assert counts["edges_clip_final_component_state.csv"] == 4
    assert counts["edges_clip_goal.csv"] == 2
    assert counts["edges_goal_phase.csv"] == 4
    assert counts["edges_goal_target_component.csv"] == 6
    assert counts["edges_phase_step.csv"] == 4
    assert counts["edges_phase_next.csv"] == 2

    clip_id = make_clip_result_id(DEFAULT_RUN_ID, "od_only", "test_p1", "03_assy_0_1")
    event_id = make_event_id(DEFAULT_RUN_ID, "od_only", "test_p1", "03_assy_0_1", 0)
    assert _read(output_dir / "nodes_runs.csv")[0][":LABEL"] == "IndustRealRun;PipelineRun"
    assert _read(output_dir / "nodes_clips.csv")[0]["clip_result_id:ID(IndustRealClip)"] == clip_id
    assert _read(output_dir / "nodes_clips.csv")[0]["display_name"] == "03_assy_0_1 (od_only)"
    assert _read(output_dir / "nodes_clips.csv")[0]["name"] == "03_assy_0_1 (od_only)"
    assert _read(output_dir / "nodes_events.csv")[0]["event_id:ID(AssemblyEvent)"] == event_id
    assert _read(output_dir / "nodes_events.csv")[0]["display_name"] == "Install front chassis"
    assert _read(output_dir / "nodes_events.csv")[0]["name"] == "Install front chassis"
    assert _read(output_dir / "nodes_components.csv")[0]["component_id:ID(Component)"].startswith("industreal_component::")
    goals = _read(output_dir / "nodes_goals.csv")
    assert goals[0]["goal_name"] == "Reach final CAD assembly state"
    assert goals[0]["display_name"] == "Reach final CAD assembly state (03_assy_0_1)"
    assert goals[0]["name"] == "Reach final CAD assembly state (03_assy_0_1)"
    assert goals[0]["target_state_index:int"] == "22"
    assert goals[0]["target_state_asset"] == "part_geometries/state22.fbx"
    assert "front chassis" in goals[0]["target_components"]
    goal_target_components = _read(output_dir / "edges_goal_target_component.csv")
    assert len(goal_target_components) == 6
    assert goal_target_components[0][":TYPE"] == "TARGETS_COMPONENT"
    assert goal_target_components[0]["target_state_index:int"] == "22"
    assert goal_target_components[0]["target_state_asset"] == "part_geometries/state22.fbx"
    assert goal_target_components[0]["required:boolean"] == "true"
    assert goal_target_components[0][":START_ID(AssemblyGoal)"] == f"{clip_id}::goal"
    assert {row[":END_ID(Component)"] for row in goal_target_components} >= {
        make_component_id("base"),
        make_component_id("front chassis"),
        make_component_id("front chassis pin"),
    }
    phases = _read(output_dir / "nodes_phases.csv")
    assert {row["phase_name"] for row in phases} >= {"Chassis assembly", "Connector installation", "Correction handling"}
    assert {row["display_name"] for row in phases} >= {"Chassis assembly", "Connector installation", "Correction handling"}
    assert {row["name"] for row in phases} >= {"Chassis assembly", "Connector installation", "Correction handling"}
    correction = [row for row in phases if row["phase_name"] == "Correction handling"][0]
    assert correction["has_error:boolean"] == "true"
    assert make_component_id("front chassis pin") == "industreal_component::front_chassis_pin"


def test_import_helpers_load_bundle_and_do_not_target_xr_labels(tmp_path: Path) -> None:
    results_dir = tmp_path / "results" / DEFAULT_RUN_ID
    reports_dir = tmp_path / "reports" / DEFAULT_RUN_ID
    _write_cad_catalogs(reports_dir)
    _write_result(
        results_dir,
        mode="od_only",
        archive="test_p1",
        clip="03_assy_0_1",
        events=[],
        component_states={"base": True},
    )
    output_dir = tmp_path / "neo4j"
    export_industreal_neo4j_csvs(results_dir=results_dir, output_dir=output_dir, reports_dir=reports_dir, modes=["od_only"])

    bundle = load_csv_bundle(output_dir)
    assert set(bundle) >= {
        "nodes_runs.csv",
        "nodes_clips.csv",
        "nodes_goals.csv",
        "nodes_phases.csv",
        "edges_mode_clip.csv",
        "edges_goal_target_component.csv",
    }
    assert bundle["nodes_components.csv"][0]["component_id:ID(Component)"] == "industreal_component::base"
    assert bundle["nodes_goals.csv"][0]["target_state_asset"] == "part_geometries/state22.fbx"
    assert bundle["edges_goal_target_component.csv"][0][":TYPE"] == "TARGETS_COMPONENT"

    assert "IndustRealRun" in DELETE_RUN_CYPHER
    assert "AssemblyGoal" in DELETE_RUN_CYPHER
    assert "AssemblyPhase" in DELETE_RUN_CYPHER
    assert ":Room" not in DELETE_RUN_CYPHER
    assert ":Object" not in DELETE_RUN_CYPHER
    assert ":Event" not in DELETE_RUN_CYPHER
    assert "TARGETS_COMPONENT" in DELETE_ORPHAN_COMPONENTS_CYPHER


def test_neo4j_cli_help_and_export_smoke(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parent.parent
    export_script = root / "scripts" / "12_export_neo4j_csv.py"
    import_script = root / "scripts" / "13_import_neo4j.py"

    for script in (export_script, import_script):
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        assert "usage:" in result.stdout

    results_dir = tmp_path / "results" / DEFAULT_RUN_ID
    reports_dir = tmp_path / "reports" / DEFAULT_RUN_ID
    _write_cad_catalogs(reports_dir)
    _write_result(
        results_dir,
        mode="od_only",
        archive="test_p1",
        clip="03_assy_0_1",
        events=[],
        component_states={"base": True},
    )
    output_dir = tmp_path / "neo4j"
    result = subprocess.run(
        [
            sys.executable,
            str(export_script),
            "--results-dir",
            str(results_dir),
            "--output-dir",
            str(output_dir),
            "--reports-dir",
            str(reports_dir),
            "--modes",
            "od_only",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "nodes_runs.csv" in result.stdout
    assert "nodes_goals.csv" in result.stdout
    assert "edges_goal_target_component.csv" in result.stdout
    assert (output_dir / "nodes_runs.csv").exists()
    assert (output_dir / "nodes_goals.csv").exists()
    assert (output_dir / "edges_goal_target_component.csv").exists()
