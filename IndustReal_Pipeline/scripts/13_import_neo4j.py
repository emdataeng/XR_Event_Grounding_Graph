#!/usr/bin/env python3
"""Import IndustReal Neo4j CSV files into Neo4j Aura or a local Neo4j DB."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

from src.neo4j_export import DEFAULT_RUN_ID
from src.neo4j_import import (
    CONSTRAINT_CYPHERS,
    DELETE_ORPHAN_COMPONENTS_CYPHER,
    DELETE_RUN_CYPHER,
    clean_props,
    load_csv_bundle,
    parse_bool,
    parse_float,
    parse_int,
    parse_json_list,
)


def _resolve_env_file(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    for candidate in (Path.cwd() / path, ROOT / path, REPO_ROOT / path):
        if candidate.exists():
            return candidate
    return Path.cwd() / path


def _load_env(path: Path) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise SystemExit("python-dotenv is required. Install IndustReal_Pipeline/requirements.txt.") from exc
    load_dotenv(path)


def _batches(rows: list[dict], size: int) -> list[list[dict]]:
    return [rows[idx : idx + size] for idx in range(0, len(rows), size)]


def _run_rows(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for row in rows:
        output.append(
            {
                "run_id": row["run_id:ID(IndustRealRun)"],
                "props": clean_props(
                    {
                        "name": row.get("name"),
                        "display_name": row.get("name"),
                        "source_results_dir": row.get("source_results_dir"),
                        "exported_at": row.get("exported_at"),
                        "mode_count": parse_int(row.get("mode_count:int")),
                        "clip_result_count": parse_int(row.get("clip_result_count:int")),
                    }
                ),
            }
        )
    return output


def _mode_rows(rows: list[dict[str, str]]) -> list[dict]:
    return [
        {
            "mode_id": row["mode_id:ID(IndustRealMode)"],
            "run_id": row.get("run_id"),
            "props": clean_props({"name": row.get("name"), "display_name": row.get("name")}),
        }
        for row in rows
    ]


def _clip_rows(rows: list[dict[str, str]]) -> list[dict]:
    metric_keys = {
        "n_frames": ("n_frames:int", parse_int),
        "state_frames_scored": ("state_frames_scored:int", parse_int),
        "state_accuracy": ("state_accuracy:float", parse_float),
        "state_correct": ("state_correct:int", parse_int),
        "gt_steps": ("gt_steps:int", parse_int),
        "predicted_steps": ("predicted_steps:int", parse_int),
        "diagnostic_predicted_steps": ("diagnostic_predicted_steps:int", parse_int),
        "legal_state_rate": ("legal_state_rate:float", parse_float),
        "error_window_recall": ("error_window_recall:float", parse_float),
        "event_window_evidence_ratio": ("event_window_evidence_ratio:float", parse_float),
        "step_precision": ("step_precision:float", parse_float),
        "step_recall": ("step_recall:float", parse_float),
        "median_step_delay_frames": ("median_step_delay_frames:float", parse_float),
        "psr_pos": ("psr_pos:float", parse_float),
        "psr_f1": ("psr_f1:float", parse_float),
        "psr_avg_delay_s": ("psr_avg_delay_s:float", parse_float),
        "psr_tps": ("psr_tps:int", parse_int),
        "psr_fps": ("psr_fps:int", parse_int),
        "psr_fns": ("psr_fns:int", parse_int),
        "b3_diagnostic_step_precision": ("b3_diagnostic_step_precision:float", parse_float),
        "b3_diagnostic_step_recall": ("b3_diagnostic_step_recall:float", parse_float),
        "b3_diagnostic_median_delay_frames": ("b3_diagnostic_median_delay_frames:float", parse_float),
        "b3_diagnostic_psr_pos": ("b3_diagnostic_psr_pos:float", parse_float),
        "b3_diagnostic_psr_f1": ("b3_diagnostic_psr_f1:float", parse_float),
        "b3_diagnostic_psr_avg_delay_s": ("b3_diagnostic_psr_avg_delay_s:float", parse_float),
    }
    output = []
    for row in rows:
        props = {
            "display_name": row.get("display_name"),
            "name": row.get("name"),
            "run_id": row.get("run_id"),
            "mode": row.get("mode"),
            "archive_name": row.get("archive_name"),
            "split": row.get("split"),
            "clip": row.get("clip"),
        }
        for prop_key, (csv_key, parser) in metric_keys.items():
            props[prop_key] = parser(row.get(csv_key))
        output.append(
            {
                "clip_result_id": row["clip_result_id:ID(IndustRealClip)"],
                "props": clean_props(props),
            }
        )
    return output


def _event_rows(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for row in rows:
        output.append(
            {
                "event_id": row["event_id:ID(AssemblyEvent)"],
                "props": clean_props(
                    {
                        "run_id": row.get("run_id"),
                        "display_name": row.get("display_name"),
                        "name": row.get("name"),
                        "mode": row.get("mode"),
                        "archive_name": row.get("archive_name"),
                        "clip": row.get("clip"),
                        "clip_result_id": row.get("clip_result_id"),
                        "local_event_id": parse_int(row.get("local_event_id:int")),
                        "frame": parse_int(row.get("frame:int")),
                        "time_s": parse_float(row.get("time_s:float")),
                        "event_type": row.get("event_type"),
                        "component": row.get("component"),
                        "action_desc": row.get("action_desc"),
                        "conf": parse_float(row.get("conf:float")),
                    }
                ),
            }
        )
    return output


def _component_rows(rows: list[dict[str, str]]) -> list[dict]:
    return [
        {
            "component_id": row["component_id:ID(Component)"],
            "props": clean_props(
                {
                        "name": row.get("name"),
                        "display_name": row.get("display_name"),
                        "normalized_name": row.get("normalized_name"),
                }
            ),
        }
        for row in rows
    ]


def _goal_rows(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for row in rows:
        output.append(
            {
                "goal_id": row["goal_id:ID(AssemblyGoal)"],
                "props": clean_props(
                    {
                        "run_id": row.get("run_id"),
                        "display_name": row.get("display_name"),
                        "name": row.get("name"),
                        "mode": row.get("mode"),
                        "archive_name": row.get("archive_name"),
                        "clip": row.get("clip"),
                        "clip_result_id": row.get("clip_result_id"),
                        "goal_name": row.get("goal_name"),
                        "target_state_index": parse_int(row.get("target_state_index:int")),
                        "target_state_name": row.get("target_state_name"),
                        "target_state_kind": row.get("target_state_kind"),
                        "target_state_asset": row.get("target_state_asset"),
                        "target_component_keys": parse_json_list(row.get("target_component_keys")),
                        "target_components": parse_json_list(row.get("target_components")),
                        "target_component_count": parse_int(row.get("target_component_count:int")),
                    }
                ),
            }
        )
    return output


def _phase_rows(rows: list[dict[str, str]]) -> list[dict]:
    output = []
    for row in rows:
        output.append(
            {
                "phase_id": row["phase_id:ID(AssemblyPhase)"],
                "props": clean_props(
                    {
                        "goal_id": row.get("goal_id"),
                        "display_name": row.get("display_name"),
                        "name": row.get("name"),
                        "clip_result_id": row.get("clip_result_id"),
                        "run_id": row.get("run_id"),
                        "mode": row.get("mode"),
                        "archive_name": row.get("archive_name"),
                        "clip": row.get("clip"),
                        "phase_key": row.get("phase_key"),
                        "phase_name": row.get("phase_name"),
                        "phase_order": parse_int(row.get("phase_order:int")),
                        "configured_order": parse_int(row.get("configured_order:int")),
                        "first_frame": parse_int(row.get("first_frame:int")),
                        "last_frame": parse_int(row.get("last_frame:int")),
                        "step_count": parse_int(row.get("step_count:int")),
                        "has_error": parse_bool(row.get("has_error:boolean")),
                        "mean_confidence": parse_float(row.get("mean_confidence:float")),
                        "status": row.get("status"),
                    }
                ),
            }
        )
    return output


def _edge_rows(rows: list[dict[str, str]], start_key: str, end_key: str, extra: dict[str, tuple[str, object]] | None = None) -> list[dict]:
    output = []
    for row in rows:
        props = {}
        for prop_key, (csv_key, parser) in (extra or {}).items():
            props[prop_key] = parser(row.get(csv_key)) if callable(parser) else row.get(csv_key)
        output.append(
            {
                "from_id": row[start_key],
                "to_id": row[end_key],
                "props": clean_props(props),
            }
        )
    return output


def _tx_constraints(tx) -> None:
    for cypher in CONSTRAINT_CYPHERS:
        tx.run(cypher)


def _tx_clear_run(tx, run_id: str) -> None:
    tx.run(DELETE_RUN_CYPHER, run_id=run_id)
    tx.run(DELETE_ORPHAN_COMPONENTS_CYPHER)


def _tx_runs(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:IndustRealRun:PipelineRun {run_id: r.run_id}) "
        "SET n += r.props",
        rows=rows,
    )


def _tx_modes(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:IndustRealMode {mode_id: r.mode_id}) "
        "SET n.run_id = r.run_id "
        "SET n += r.props",
        rows=rows,
    )


def _tx_clips(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:IndustRealClip:Recording {clip_result_id: r.clip_result_id}) "
        "SET n += r.props",
        rows=rows,
    )


def _tx_events(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:AssemblyEvent:ProcedureStep {event_id: r.event_id}) "
        "SET n += r.props",
        rows=rows,
    )


def _tx_components(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:Component:IndustRealComponent {component_id: r.component_id}) "
        "SET n += r.props",
        rows=rows,
    )


def _tx_goals(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:AssemblyGoal:CADAssemblyGoal {goal_id: r.goal_id}) "
        "SET n += r.props",
        rows=rows,
    )


def _tx_phases(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MERGE (n:AssemblyPhase {phase_id: r.phase_id}) "
        "SET n += r.props",
        rows=rows,
    )


def _tx_run_mode(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:IndustRealRun {run_id: r.from_id}) "
        "MATCH (b:IndustRealMode {mode_id: r.to_id}) "
        "MERGE (a)-[:HAS_MODE]->(b)",
        rows=rows,
    )


def _tx_mode_clip(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:IndustRealMode {mode_id: r.from_id}) "
        "MATCH (b:IndustRealClip {clip_result_id: r.to_id}) "
        "MERGE (a)-[:HAS_CLIP]->(b)",
        rows=rows,
    )


def _tx_clip_event(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:IndustRealClip {clip_result_id: r.from_id}) "
        "MATCH (b:AssemblyEvent {event_id: r.to_id}) "
        "MERGE (a)-[:HAS_STEP]->(b)",
        rows=rows,
    )


def _tx_event_next(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:AssemblyEvent {event_id: r.from_id}) "
        "MATCH (b:AssemblyEvent {event_id: r.to_id}) "
        "MERGE (a)-[rel:NEXT]->(b) "
        "SET rel += r.props",
        rows=rows,
    )


def _tx_event_component(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:AssemblyEvent {event_id: r.from_id}) "
        "MATCH (b:IndustRealComponent {component_id: r.to_id}) "
        "MERGE (a)-[rel:ACTS_ON]->(b) "
        "SET rel += r.props",
        rows=rows,
    )


def _tx_clip_component_state(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:IndustRealClip {clip_result_id: r.from_id}) "
        "MATCH (b:IndustRealComponent {component_id: r.to_id}) "
        "MERGE (a)-[rel:ENDS_WITH_COMPONENT_STATE]->(b) "
        "SET rel += r.props",
        rows=rows,
    )


def _tx_clip_goal(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:IndustRealClip {clip_result_id: r.from_id}) "
        "MATCH (b:AssemblyGoal {goal_id: r.to_id}) "
        "MERGE (a)-[:HAS_GOAL]->(b)",
        rows=rows,
    )


def _tx_goal_phase(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:AssemblyGoal {goal_id: r.from_id}) "
        "MATCH (b:AssemblyPhase {phase_id: r.to_id}) "
        "MERGE (a)-[:HAS_PHASE]->(b)",
        rows=rows,
    )


def _tx_goal_target_component(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:AssemblyGoal {goal_id: r.from_id}) "
        "MATCH (b:IndustRealComponent {component_id: r.to_id}) "
        "MERGE (a)-[rel:TARGETS_COMPONENT]->(b) "
        "SET rel += r.props",
        rows=rows,
    )


def _tx_phase_step(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:AssemblyPhase {phase_id: r.from_id}) "
        "MATCH (b:AssemblyEvent {event_id: r.to_id}) "
        "MERGE (a)-[:HAS_STEP]->(b)",
        rows=rows,
    )


def _tx_phase_next(tx, rows: list[dict]) -> None:
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:AssemblyPhase {phase_id: r.from_id}) "
        "MATCH (b:AssemblyPhase {phase_id: r.to_id}) "
        "MERGE (a)-[rel:NEXT_PHASE]->(b) "
        "SET rel += r.props",
        rows=rows,
    )


def _write_batches(session, tx_func, rows: list[dict], batch_size: int) -> None:
    for batch in _batches(rows, batch_size):
        session.execute_write(tx_func, batch)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", type=str, default=DEFAULT_RUN_ID)
    parser.add_argument("--csv-dir", type=Path, default=None)
    parser.add_argument("--env-file", type=str, default=".env")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--no-replace-run", action="store_true")
    args = parser.parse_args()

    csv_dir = args.csv_dir or (ROOT / "results" / "neo4j" / args.run_id)
    bundle = load_csv_bundle(csv_dir)
    env_path = _resolve_env_file(args.env_file)
    _load_env(env_path)

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not password:
        raise SystemExit(f"NEO4J_URI and NEO4J_PASSWORD must be set in {env_path}")

    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise SystemExit("neo4j is required. Install IndustReal_Pipeline/requirements.txt.") from exc

    rows = {
        "runs": _run_rows(bundle["nodes_runs.csv"]),
        "modes": _mode_rows(bundle["nodes_modes.csv"]),
        "clips": _clip_rows(bundle["nodes_clips.csv"]),
        "events": _event_rows(bundle["nodes_events.csv"]),
        "components": _component_rows(bundle["nodes_components.csv"]),
        "goals": _goal_rows(bundle["nodes_goals.csv"]),
        "phases": _phase_rows(bundle["nodes_phases.csv"]),
        "run_mode": _edge_rows(bundle["edges_run_mode.csv"], ":START_ID(IndustRealRun)", ":END_ID(IndustRealMode)"),
        "mode_clip": _edge_rows(bundle["edges_mode_clip.csv"], ":START_ID(IndustRealMode)", ":END_ID(IndustRealClip)"),
        "clip_event": _edge_rows(bundle["edges_clip_event.csv"], ":START_ID(IndustRealClip)", ":END_ID(AssemblyEvent)"),
        "event_next": _edge_rows(
            bundle["edges_event_next.csv"],
            ":START_ID(AssemblyEvent)",
            ":END_ID(AssemblyEvent)",
            {"clip_result_id": ("clip_result_id", str)},
        ),
        "event_component": _edge_rows(
            bundle["edges_event_component.csv"],
            ":START_ID(AssemblyEvent)",
            ":END_ID(Component)",
            {"role": ("role", str)},
        ),
        "clip_component_state": _edge_rows(
            bundle["edges_clip_final_component_state.csv"],
            ":START_ID(IndustRealClip)",
            ":END_ID(Component)",
            {
                "state": ("state", str),
                "state_known": ("state_known:boolean", parse_bool),
            },
        ),
        "clip_goal": _edge_rows(bundle["edges_clip_goal.csv"], ":START_ID(IndustRealClip)", ":END_ID(AssemblyGoal)"),
        "goal_phase": _edge_rows(bundle["edges_goal_phase.csv"], ":START_ID(AssemblyGoal)", ":END_ID(AssemblyPhase)"),
        "goal_target_component": _edge_rows(
            bundle["edges_goal_target_component.csv"],
            ":START_ID(AssemblyGoal)",
            ":END_ID(Component)",
            {
                "target_state_index": ("target_state_index:int", parse_int),
                "target_state_asset": ("target_state_asset", str),
                "required": ("required:boolean", parse_bool),
            },
        ),
        "phase_step": _edge_rows(bundle["edges_phase_step.csv"], ":START_ID(AssemblyPhase)", ":END_ID(AssemblyEvent)"),
        "phase_next": _edge_rows(
            bundle["edges_phase_next.csv"],
            ":START_ID(AssemblyPhase)",
            ":END_ID(AssemblyPhase)",
            {"clip_result_id": ("clip_result_id", str)},
        ),
    }

    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    with driver.session() as session:
        session.execute_write(_tx_constraints)
        if not args.no_replace_run:
            session.execute_write(_tx_clear_run, args.run_id)
        _write_batches(session, _tx_runs, rows["runs"], args.batch_size)
        _write_batches(session, _tx_modes, rows["modes"], args.batch_size)
        _write_batches(session, _tx_clips, rows["clips"], args.batch_size)
        _write_batches(session, _tx_components, rows["components"], args.batch_size)
        _write_batches(session, _tx_events, rows["events"], args.batch_size)
        _write_batches(session, _tx_goals, rows["goals"], args.batch_size)
        _write_batches(session, _tx_phases, rows["phases"], args.batch_size)
        _write_batches(session, _tx_run_mode, rows["run_mode"], args.batch_size)
        _write_batches(session, _tx_mode_clip, rows["mode_clip"], args.batch_size)
        _write_batches(session, _tx_clip_goal, rows["clip_goal"], args.batch_size)
        _write_batches(session, _tx_goal_phase, rows["goal_phase"], args.batch_size)
        _write_batches(session, _tx_goal_target_component, rows["goal_target_component"], args.batch_size)
        _write_batches(session, _tx_clip_event, rows["clip_event"], args.batch_size)
        _write_batches(session, _tx_phase_step, rows["phase_step"], args.batch_size)
        _write_batches(session, _tx_event_next, rows["event_next"], args.batch_size)
        _write_batches(session, _tx_phase_next, rows["phase_next"], args.batch_size)
        _write_batches(session, _tx_event_component, rows["event_component"], args.batch_size)
        _write_batches(session, _tx_clip_component_state, rows["clip_component_state"], args.batch_size)
    driver.close()

    print(f"Imported IndustReal run {args.run_id} from {csv_dir}")
    print(
        "Rows: "
        f"{len(rows['runs'])} runs, {len(rows['modes'])} modes, "
        f"{len(rows['clips'])} clips, {len(rows['events'])} events, "
        f"{len(rows['components'])} components, "
        f"{len(rows['goals'])} goals, {len(rows['phases'])} phases"
    )


if __name__ == "__main__":
    main()
