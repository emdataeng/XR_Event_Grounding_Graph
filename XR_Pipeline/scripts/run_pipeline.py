#!/usr/bin/env python3
"""Run the XR pipeline end to end for one session.

This is a thin orchestrator around the existing stage scripts. It keeps each
stage independently runnable while giving day-to-day use a single command.
"""
from __future__ import annotations

import subprocess
import sys
import argparse
import shutil
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PipelinePaths, load_pipeline_config


def _default_python() -> Path:
    """Prefer the project virtualenv when the runner is launched outside it."""
    candidates = [
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe",
        PROJECT_ROOT / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


def _subprocess_env() -> Dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


@dataclass(frozen=True)
class Stage:
    key: str
    script: str
    description: str
    accepts_force: bool = False
    optional_group: Optional[str] = None


STAGES: List[Stage] = [
    Stage("01", "01_build_frame_manifest.py", "Build frame manifest"),
    Stage("02", "02_validate_manifest.py", "Validate manifest"),
    Stage("03", "03_visualize_rgb_depth_pose.py", "Visual sanity checks", optional_group="visuals"),
    Stage("04", "04_ingest_spatialobjects.py", "Legacy spatialobjects ingest", optional_group="legacy"),
    Stage("05", "05_build_object_observations.py", "Detect and backproject object observations", accepts_force=True),
    Stage("06", "06_link_object_tracks.py", "Link observations into tracks"),
    Stage("07", "07_build_event_windows.py", "Build event windows", accepts_force=True),
    Stage("08", "08_generate_event_summaries.py", "Generate event summaries", accepts_force=True),
    Stage("09", "09_build_egg_graph.py", "Build EGG graph", accepts_force=True),
    Stage("09b", "09b_build_scene_state_package.py", "Build scene state package", accepts_force=True),
    Stage("09c", "09c_build_state_facts.py", "Build state facts"),
    Stage("09d", "09d_build_assembly_state_package.py", "Build assembly state package"),
    Stage("10", "10_prune_egg_graph.py", "Prune graph for a query", accepts_force=True),
    Stage("10b", "10b_build_operation_events.py", "Build operation events", accepts_force=True),
    Stage("10c", "10c_build_workflow_timeline.py", "Build workflow timeline", accepts_force=True),
    Stage("10d", "10d_build_subtask_events.py", "Build subtask events"),
    Stage("10e", "10e_build_assembly_graph.py", "Build assembly graph"),
    Stage("10f", "10f_run_thesis_layer3_constraints.py", "Run thesis Layer 3 constraints"),
    Stage("11", "11_export_neo4j_csv.py", "Export Neo4j CSV files"),
    Stage("11op", "11_build_operation_review.py", "Build operation review", accepts_force=True),
    Stage("11b", "11b_build_assembly_review.py", "Build assembly review"),
    Stage("12", "12_demo_queries.py", "Run demo graph queries"),
    Stage("13", "13_visualize_3d_debug.py", "3D debug visualizations", optional_group="visuals"),
    Stage("14", "14_import_neo4j.py", "Import into Neo4j", optional_group="neo4j"),
]


def _selected_stages(
    *,
    from_stage: Optional[str],
    to_stage: Optional[str],
    include_visuals: bool,
    include_legacy: bool,
    include_neo4j_import: bool,
) -> List[Stage]:
    selected = []
    enabled_groups = set()
    if include_visuals:
        enabled_groups.add("visuals")
    if include_legacy:
        enabled_groups.add("legacy")
    if include_neo4j_import:
        enabled_groups.add("neo4j")

    for stage in STAGES:
        if stage.optional_group and stage.optional_group not in enabled_groups:
            continue
        selected.append(stage)

    keys = [s.key for s in selected]
    if from_stage:
        if from_stage not in keys:
            raise ValueError(f"Unknown or excluded --from-stage: {from_stage}")
        selected = selected[keys.index(from_stage):]

    keys = [s.key for s in selected]
    if to_stage:
        if to_stage not in keys:
            raise ValueError(f"Unknown or excluded --to-stage: {to_stage}")
        selected = selected[: keys.index(to_stage) + 1]

    return selected


def _command_for_stage(
    stage: Stage,
    *,
    python_exe: Path,
    session: str,
    config: Optional[str],
    force: bool,
    max_frames: int,
    query: str,
    rules: str,
    wipe_all: bool,
) -> List[str]:
    cmd = [str(python_exe), str(PROJECT_ROOT / "scripts" / stage.script), "--session", session]

    if config:
        cmd.extend(["--config", config])

    if force and stage.accepts_force:
        cmd.append("--force")

    if stage.key == "05" and max_frames > 0:
        cmd.extend(["--max-frames", str(max_frames)])

    if stage.key == "10":
        cmd.extend(["--query", query])

    if stage.key == "10f":
        cmd.extend(["--rules", rules])

    if stage.key == "14" and wipe_all:
        cmd.append("--wipe-all")

    return cmd


def _metadata_path(paths: PipelinePaths, stage: Stage) -> Path:
    return paths.logs_dir / f"run_metadata_{Path(stage.script).stem}.json"


def _stage_owned_outputs(stage: Stage, paths: PipelinePaths) -> List[Path]:
    """Return files/directories owned by a stage and safe to clean before rerun."""
    op_events = paths.objects_dir / "operation_events.csv"
    operation_overlays = paths.graphs_dir / "operation_event_overlays"
    demo_results = paths.queries_dir / "demo_query_results.json"
    constraints = paths.processed_root / "constraints.csv"
    incompatibilities = paths.processed_root / "incompatibilities.csv"

    by_key: Dict[str, List[Path]] = {
        "01": [paths.frame_manifest],
        "02": [paths.manifest_validation],
        "03": [
            paths.sample_vis_dir,
            *paths.debug_pc_dir.glob("frame_*_pointcloud.png"),
        ],
        "04": [paths.object_observations],
        "05": [paths.object_observations, paths.debug_box_dir],
        "06": [paths.object_tracks, paths.track_summary, paths.track_debug],
        "07": [paths.event_windows, paths.track_motion_debug],
        "08": [paths.events_csv, paths.event_object_roles],
        "09": [paths.egg_graph],
        "09b": [paths.scene_state_package],
        "09c": [paths.state_facts_csv, paths.state_facts_json],
        "09d": [paths.assembly_state_package],
        "10": [paths.pruned_subgraph, paths.query_answer],
        "10b": [op_events, paths.support_state_transitions, operation_overlays],
        "10c": [paths.workflow_timeline, paths.workflow_timeline_csv],
        "10d": [paths.subtask_events, paths.subtask_sequence],
        "10e": [paths.assembly_graph],
        "10f": [constraints, incompatibilities],
        "11": [paths.neo4j_dir],
        "11op": [paths.reviews_dir],
        "11b": [paths.assembly_review_json, paths.assembly_review_md],
        "12": [demo_results],
        "13": [
            *paths.debug_pc_dir.glob("frame_*_3d.png"),
            *paths.debug_pc_dir.glob("frame_*_rgbd.png"),
            paths.debug_pc_dir / "merged_pointcloud.png",
        ],
        # Stage 14 mutates Neo4j, not local session artifacts.
        "14": [],
    }
    return [*by_key.get(stage.key, []), _metadata_path(paths, stage)]


def _assert_safe_output_path(path: Path, paths: PipelinePaths) -> None:
    root = paths.processed_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Refusing to clean path outside session output: {resolved}") from exc


def _remove_output_path(path: Path, paths: PipelinePaths) -> bool:
    _assert_safe_output_path(path, paths)
    if not path.exists():
        return False
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return True


def _clean_stage_outputs(stage: Stage, paths: PipelinePaths) -> int:
    removed = 0
    seen = set()
    for path in _stage_owned_outputs(stage, paths):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if _remove_output_path(path, paths):
            removed += 1
    return removed


def _wipe_session_outputs(paths: PipelinePaths, session: str) -> bool:
    root = paths.processed_root.resolve()
    if root == PROJECT_ROOT.resolve() or root.parent == root:
        raise ValueError(f"Refusing unsafe session wipe path: {root}")
    if root.name != session:
        raise ValueError(f"Refusing to wipe {root}; final path component is not session {session!r}")
    if not root.exists():
        return False
    shutil.rmtree(root)
    return True


def _print_stage_table(stages: List[Stage]) -> None:
    print("Pipeline stages:")
    for stage in stages:
        print(f"  {stage.key:>4}  {stage.script:<38} {stage.description}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the XR pipeline stage scripts in order.")
    parser.add_argument("--session", default="session_001", help="Session ID to process")
    parser.add_argument("--config", default=None, help="Path to pipeline.yaml override")
    parser.add_argument("--from-stage", default=None, help="Start at this stage key, e.g. 05")
    parser.add_argument("--to-stage", default=None, help="Stop after this stage key, e.g. 09b")
    parser.add_argument("--force", action="store_true", help="Pass --force to stages with staleness checks")
    parser.add_argument("--max-frames", type=int, default=0, help="Limit stage 05 to first N frames; 0 means all")
    parser.add_argument("--query", default="What moved?", help="Query used by stage 10")
    parser.add_argument("--rules", default="configs/thesis_rules.yaml", help="Rules YAML for stage 10f")
    parser.add_argument("--include-visuals", action="store_true", help="Also run stages 03 and 13")
    parser.add_argument("--include-legacy", action="store_true", help="Also run legacy stage 04")
    parser.add_argument("--include-neo4j-import", action="store_true", help="Also run stage 14 Neo4j import")
    parser.add_argument("--wipe-all", action="store_true", help="Pass --wipe-all to Neo4j import")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Before each selected stage, delete that stage's owned local outputs.",
    )
    parser.add_argument(
        "--wipe-session",
        action="store_true",
        help="Delete data/processed/<session> before running selected stages.",
    )
    parser.add_argument("--continue-on-error", action="store_true", help="Continue after a failed stage")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them")
    parser.add_argument("--list-stages", action="store_true", help="Show selected stages and exit")
    parser.add_argument(
        "--python",
        default=None,
        help="Python executable for stage scripts; defaults to .venv when present",
    )
    return parser.parse_args()


def main() -> int:
    """Run the pipeline stage scripts in order."""
    args = _parse_args()
    try:
        stages = _selected_stages(
            from_stage=args.from_stage,
            to_stage=args.to_stage,
            include_visuals=args.include_visuals,
            include_legacy=args.include_legacy,
            include_neo4j_import=args.include_neo4j_import,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.list_stages:
        _print_stage_table(stages)
        return 0

    python_exe = Path(args.python).resolve() if args.python else _default_python()
    cfg = load_pipeline_config(Path(args.config) if args.config else None)
    paths = PipelinePaths(args.session, cfg)

    print(f"Running XR pipeline for {args.session}")
    print(f"Python: {python_exe}")
    if args.dry_run:
        print("Dry run: commands will not be executed.")

    if args.wipe_session:
        print(f"Session output wipe: {paths.processed_root}")
        if not args.dry_run:
            wiped = _wipe_session_outputs(paths, args.session)
            print("Deleted session output folder." if wiped else "Session output folder did not exist.")

    failures = []
    for index, stage in enumerate(stages, start=1):
        cmd = _command_for_stage(
            stage,
            python_exe=python_exe,
            session=args.session,
            config=args.config,
            force=args.force,
            max_frames=args.max_frames,
            query=args.query,
            rules=args.rules,
            wipe_all=args.wipe_all,
        )
        print(f"\n=== {index}/{len(stages)} {stage.key} {stage.script} ===")
        print(stage.description)
        print(" ".join(cmd))

        if args.dry_run:
            continue

        if args.clean:
            removed = _clean_stage_outputs(stage, paths)
            print(f"Cleaned {removed} stage-owned output path(s).")

        result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=_subprocess_env())
        if result.returncode != 0:
            failures.append((stage, result.returncode))
            print(f"Stage {stage.key} failed with exit code {result.returncode}.")
            if not args.continue_on_error:
                return result.returncode

    if failures:
        print(f"Pipeline finished with {len(failures)} failed stage(s).")
        for stage, code in failures:
            print(f"  {stage.key} {stage.script}: exit code {code}")
        return 1

    print("Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
