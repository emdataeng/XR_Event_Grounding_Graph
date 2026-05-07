"""Neo4j CSV export helpers for IndustReal assembly graph results."""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .assembly_hierarchy import (
    DEFAULT_FINAL_STATE_INDEX,
    DEFAULT_GOAL_NAME,
    assign_event_phase,
    load_cad_goal,
    load_phase_rules,
    make_goal_id,
    make_phase_id,
    summarize_event_phases,
)


DEFAULT_RUN_ID = "raw_cad_dataset__all_test_clips"
DEFAULT_MODES = ("od_only", "od_plus_psr_error_hints")
DEFAULT_PHASE_RULES = Path(__file__).resolve().parent.parent / "configs" / "assembly_phase_rules.json"

RESTORE_HINT = """Full IndustReal result outputs were not found.

If /tmp was cleaned, restore the preserved result bundle first:

mkdir -p /tmp/industreal_pilot/results/raw_cad_dataset
tar -xzf IndustReal_Pipeline/results/preserved_tmp/raw_cad_dataset__all_test_clips.tar.gz \\
  -C /tmp/industreal_pilot/results/raw_cad_dataset
"""


RUN_FIELDS = [
    "run_id:ID(IndustRealRun)",
    "name",
    "source_results_dir",
    "exported_at",
    "mode_count:int",
    "clip_result_count:int",
    ":LABEL",
]

MODE_FIELDS = [
    "mode_id:ID(IndustRealMode)",
    "run_id",
    "name",
    ":LABEL",
]

CLIP_FIELDS = [
    "clip_result_id:ID(IndustRealClip)",
    "display_name",
    "name",
    "run_id",
    "mode",
    "archive_name",
    "split",
    "clip",
    "n_frames:int",
    "state_frames_scored:int",
    "state_accuracy:float",
    "state_correct:int",
    "gt_steps:int",
    "predicted_steps:int",
    "diagnostic_predicted_steps:int",
    "legal_state_rate:float",
    "error_window_recall:float",
    "event_window_evidence_ratio:float",
    "step_precision:float",
    "step_recall:float",
    "median_step_delay_frames:float",
    "psr_pos:float",
    "psr_f1:float",
    "psr_avg_delay_s:float",
    "psr_tps:int",
    "psr_fps:int",
    "psr_fns:int",
    "b3_diagnostic_step_precision:float",
    "b3_diagnostic_step_recall:float",
    "b3_diagnostic_median_delay_frames:float",
    "b3_diagnostic_psr_pos:float",
    "b3_diagnostic_psr_f1:float",
    "b3_diagnostic_psr_avg_delay_s:float",
    ":LABEL",
]

EVENT_FIELDS = [
    "event_id:ID(AssemblyEvent)",
    "display_name",
    "name",
    "run_id",
    "mode",
    "archive_name",
    "clip",
    "clip_result_id",
    "local_event_id:int",
    "frame:int",
    "time_s:float",
    "event_type",
    "component",
    "action_desc",
    "conf:float",
    ":LABEL",
]

COMPONENT_FIELDS = [
    "component_id:ID(Component)",
    "display_name",
    "name",
    "normalized_name",
    ":LABEL",
]

GOAL_FIELDS = [
    "goal_id:ID(AssemblyGoal)",
    "display_name",
    "name",
    "run_id",
    "mode",
    "archive_name",
    "clip",
    "clip_result_id",
    "goal_name",
    "target_state_index:int",
    "target_state_name",
    "target_state_kind",
    "target_state_asset",
    "target_component_keys",
    "target_components",
    "target_component_count:int",
    ":LABEL",
]

PHASE_FIELDS = [
    "phase_id:ID(AssemblyPhase)",
    "display_name",
    "name",
    "goal_id",
    "clip_result_id",
    "run_id",
    "mode",
    "archive_name",
    "clip",
    "phase_key",
    "phase_name",
    "phase_order:int",
    "configured_order:int",
    "first_frame:int",
    "last_frame:int",
    "step_count:int",
    "has_error:boolean",
    "mean_confidence:float",
    "status",
    ":LABEL",
]

EDGE_RUN_MODE_FIELDS = [
    ":START_ID(IndustRealRun)",
    ":END_ID(IndustRealMode)",
    ":TYPE",
]

EDGE_MODE_CLIP_FIELDS = [
    ":START_ID(IndustRealMode)",
    ":END_ID(IndustRealClip)",
    ":TYPE",
]

EDGE_CLIP_EVENT_FIELDS = [
    ":START_ID(IndustRealClip)",
    ":END_ID(AssemblyEvent)",
    ":TYPE",
]

EDGE_EVENT_NEXT_FIELDS = [
    ":START_ID(AssemblyEvent)",
    ":END_ID(AssemblyEvent)",
    "clip_result_id",
    ":TYPE",
]

EDGE_EVENT_COMPONENT_FIELDS = [
    ":START_ID(AssemblyEvent)",
    ":END_ID(Component)",
    "role",
    ":TYPE",
]

EDGE_CLIP_COMPONENT_STATE_FIELDS = [
    ":START_ID(IndustRealClip)",
    ":END_ID(Component)",
    "state",
    "state_known:boolean",
    ":TYPE",
]

EDGE_CLIP_GOAL_FIELDS = [
    ":START_ID(IndustRealClip)",
    ":END_ID(AssemblyGoal)",
    ":TYPE",
]

EDGE_GOAL_PHASE_FIELDS = [
    ":START_ID(AssemblyGoal)",
    ":END_ID(AssemblyPhase)",
    ":TYPE",
]

EDGE_GOAL_TARGET_COMPONENT_FIELDS = [
    ":START_ID(AssemblyGoal)",
    ":END_ID(Component)",
    "target_state_index:int",
    "target_state_asset",
    "required:boolean",
    ":TYPE",
]

EDGE_PHASE_STEP_FIELDS = [
    ":START_ID(AssemblyPhase)",
    ":END_ID(AssemblyEvent)",
    ":TYPE",
]

EDGE_PHASE_NEXT_FIELDS = [
    ":START_ID(AssemblyPhase)",
    ":END_ID(AssemblyPhase)",
    "clip_result_id",
    ":TYPE",
]

CSV_SCHEMAS = {
    "nodes_runs.csv": RUN_FIELDS,
    "nodes_modes.csv": MODE_FIELDS,
    "nodes_clips.csv": CLIP_FIELDS,
    "nodes_events.csv": EVENT_FIELDS,
    "nodes_components.csv": COMPONENT_FIELDS,
    "nodes_goals.csv": GOAL_FIELDS,
    "nodes_phases.csv": PHASE_FIELDS,
    "edges_run_mode.csv": EDGE_RUN_MODE_FIELDS,
    "edges_mode_clip.csv": EDGE_MODE_CLIP_FIELDS,
    "edges_clip_event.csv": EDGE_CLIP_EVENT_FIELDS,
    "edges_event_next.csv": EDGE_EVENT_NEXT_FIELDS,
    "edges_event_component.csv": EDGE_EVENT_COMPONENT_FIELDS,
    "edges_clip_final_component_state.csv": EDGE_CLIP_COMPONENT_STATE_FIELDS,
    "edges_clip_goal.csv": EDGE_CLIP_GOAL_FIELDS,
    "edges_goal_phase.csv": EDGE_GOAL_PHASE_FIELDS,
    "edges_goal_target_component.csv": EDGE_GOAL_TARGET_COMPONENT_FIELDS,
    "edges_phase_step.csv": EDGE_PHASE_STEP_FIELDS,
    "edges_phase_next.csv": EDGE_PHASE_NEXT_FIELDS,
}


def export_industreal_neo4j_csvs(
    *,
    results_dir: Path,
    output_dir: Path,
    run_id: str = DEFAULT_RUN_ID,
    modes: Iterable[str] = DEFAULT_MODES,
    reports_dir: Path | None = None,
    cad_state_catalog_path: Path | None = None,
    cad_part_catalog_path: Path | None = None,
    phase_rules_path: Path | None = None,
) -> dict[str, int]:
    """Export IndustReal assembly graph results as Neo4j-ready CSV files."""
    results_dir = Path(results_dir)
    output_dir = Path(output_dir)
    if not results_dir.exists():
        raise FileNotFoundError(f"{results_dir}\n\n{RESTORE_HINT}")

    modes_root = results_dir / "modes"
    if not modes_root.exists():
        raise FileNotFoundError(f"{modes_root}\n\n{RESTORE_HINT}")

    selected_modes = [str(mode) for mode in modes]
    summary_lookup = _load_summary_lookup(reports_dir)
    cad_state_catalog_path = _resolve_optional_catalog(
        explicit_path=cad_state_catalog_path,
        reports_dir=reports_dir,
        filename="cad_state_catalog.json",
    )
    cad_part_catalog_path = _resolve_optional_catalog(
        explicit_path=cad_part_catalog_path,
        reports_dir=reports_dir,
        filename="cad_part_catalog.json",
    )
    if cad_state_catalog_path is None:
        raise FileNotFoundError(
            "CAD state catalog is required to create AssemblyGoal nodes. "
            "Pass --cad-state-catalog or run with a reports_dir containing cad/cad_state_catalog.json."
        )
    goal_name, final_state_index = _goal_defaults_from_rules(phase_rules_path or DEFAULT_PHASE_RULES)
    cad_goal = load_cad_goal(
        cad_state_catalog_path,
        cad_part_catalog_path=cad_part_catalog_path,
        final_state_index=final_state_index,
        goal_name=goal_name,
    )
    phase_rules = load_phase_rules(phase_rules_path or DEFAULT_PHASE_RULES)
    exported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    mode_rows: list[dict[str, Any]] = []
    clip_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    component_rows_by_id: dict[str, dict[str, Any]] = {}
    goal_rows: list[dict[str, Any]] = []
    phase_rows: list[dict[str, Any]] = []
    edge_run_mode_rows: list[dict[str, Any]] = []
    edge_mode_clip_rows: list[dict[str, Any]] = []
    edge_clip_event_rows: list[dict[str, Any]] = []
    edge_event_next_rows: list[dict[str, Any]] = []
    edge_event_component_rows: list[dict[str, Any]] = []
    edge_clip_component_state_rows: list[dict[str, Any]] = []
    edge_clip_goal_rows: list[dict[str, Any]] = []
    edge_goal_phase_rows: list[dict[str, Any]] = []
    edge_goal_target_component_rows: list[dict[str, Any]] = []
    edge_phase_step_rows: list[dict[str, Any]] = []
    edge_phase_next_rows: list[dict[str, Any]] = []

    for mode in selected_modes:
        mode_dir = modes_root / mode
        if not mode_dir.exists():
            continue

        mode_id = make_mode_id(run_id, mode)
        mode_rows.append(
            {
                "mode_id:ID(IndustRealMode)": mode_id,
                "run_id": run_id,
                "name": mode,
                ":LABEL": "IndustRealMode",
            }
        )
        edge_run_mode_rows.append(
            {
                ":START_ID(IndustRealRun)": run_id,
                ":END_ID(IndustRealMode)": mode_id,
                ":TYPE": "HAS_MODE",
            }
        )

        for graph_path in sorted(mode_dir.glob("*/*/assembly_graph.json")):
            archive_name = graph_path.parent.parent.name
            clip = graph_path.parent.name
            graph = _load_json(graph_path)
            metrics = _load_metrics(
                graph_path.parent / "metrics.json",
                summary_lookup=summary_lookup,
                mode=mode,
                archive_name=archive_name,
                clip=clip,
            )
            clip_result_id = make_clip_result_id(run_id, mode, archive_name, clip)
            goal_id = make_goal_id(clip_result_id)
            n_frames = int(graph.get("n_frames") or metrics.get("n_frames") or 0)
            split = str(metrics.get("split") or "test")

            clip_rows.append(
                _clip_row(
                    run_id=run_id,
                    mode=mode,
                    archive_name=archive_name,
                    split=split,
                    clip=clip,
                    clip_result_id=clip_result_id,
                    n_frames=n_frames,
                    metrics=metrics,
                )
            )
            edge_mode_clip_rows.append(
                {
                    ":START_ID(IndustRealMode)": mode_id,
                    ":END_ID(IndustRealClip)": clip_result_id,
                    ":TYPE": "HAS_CLIP",
                }
            )
            goal_rows.append(
                _goal_row(
                    cad_goal=cad_goal,
                    run_id=run_id,
                    mode=mode,
                    archive_name=archive_name,
                    clip=clip,
                    clip_result_id=clip_result_id,
                    goal_id=goal_id,
                )
            )
            edge_clip_goal_rows.append(
                {
                    ":START_ID(IndustRealClip)": clip_result_id,
                    ":END_ID(AssemblyGoal)": goal_id,
                    ":TYPE": "HAS_GOAL",
                }
            )
            for component_name in cad_goal.target_components:
                component_id = make_component_id(component_name)
                component_rows_by_id.setdefault(
                    component_id,
                    _component_row(component_id, component_name),
                )
                edge_goal_target_component_rows.append(
                    {
                        ":START_ID(AssemblyGoal)": goal_id,
                        ":END_ID(Component)": component_id,
                        "target_state_index:int": cad_goal.target_state_index,
                        "target_state_asset": cad_goal.target_state_asset,
                        "required:boolean": True,
                        ":TYPE": "TARGETS_COMPONENT",
                    }
                )

            graph_events = sorted(
                graph.get("events", []),
                key=lambda item: (int(item.get("frame", 0)), int(item.get("event_id", 0))),
            )
            phase_id_by_key: dict[str, str] = {}
            previous_phase_id: str | None = None
            for phase_summary in summarize_event_phases(graph_events, phase_rules):
                phase_key = str(phase_summary["phase_key"])
                phase_id = make_phase_id(clip_result_id, phase_key)
                phase_id_by_key[phase_key] = phase_id
                phase_rows.append(
                    _phase_row(
                        run_id=run_id,
                        mode=mode,
                        archive_name=archive_name,
                        clip=clip,
                        clip_result_id=clip_result_id,
                        goal_id=goal_id,
                        phase_id=phase_id,
                        phase_summary=phase_summary,
                    )
                )
                edge_goal_phase_rows.append(
                    {
                        ":START_ID(AssemblyGoal)": goal_id,
                        ":END_ID(AssemblyPhase)": phase_id,
                        ":TYPE": "HAS_PHASE",
                    }
                )
                if previous_phase_id is not None:
                    edge_phase_next_rows.append(
                        {
                            ":START_ID(AssemblyPhase)": previous_phase_id,
                            ":END_ID(AssemblyPhase)": phase_id,
                            "clip_result_id": clip_result_id,
                            ":TYPE": "NEXT_PHASE",
                        }
                    )
                previous_phase_id = phase_id

            previous_event_id: str | None = None
            for event in graph_events:
                local_event_id = int(event.get("event_id", len(event_rows)))
                event_id = make_event_id(run_id, mode, archive_name, clip, local_event_id)
                component_name = str(event.get("component") or "unknown")
                component_id = make_component_id(component_name)
                event_phase = assign_event_phase(event, phase_rules)
                phase_id = phase_id_by_key.get(event_phase.key)
                component_rows_by_id.setdefault(
                    component_id,
                    _component_row(component_id, component_name),
                )
                display_name = str(event.get("action_desc") or f"{event.get('event_type', '')} {component_name}").strip()
                event_rows.append(
                    {
                        "event_id:ID(AssemblyEvent)": event_id,
                        "display_name": display_name,
                        "name": display_name,
                        "run_id": run_id,
                        "mode": mode,
                        "archive_name": archive_name,
                        "clip": clip,
                        "clip_result_id": clip_result_id,
                        "local_event_id:int": local_event_id,
                        "frame:int": int(event.get("frame", 0)),
                        "time_s:float": _csv_value(event.get("time_s")),
                        "event_type": str(event.get("event_type") or ""),
                        "component": component_name,
                        "action_desc": str(event.get("action_desc") or ""),
                        "conf:float": _csv_value(event.get("conf", 1.0)),
                        ":LABEL": "AssemblyEvent;ProcedureStep",
                    }
                )
                edge_clip_event_rows.append(
                    {
                        ":START_ID(IndustRealClip)": clip_result_id,
                        ":END_ID(AssemblyEvent)": event_id,
                        ":TYPE": "HAS_STEP",
                    }
                )
                if phase_id is not None:
                    edge_phase_step_rows.append(
                        {
                            ":START_ID(AssemblyPhase)": phase_id,
                            ":END_ID(AssemblyEvent)": event_id,
                            ":TYPE": "HAS_STEP",
                        }
                    )
                edge_event_component_rows.append(
                    {
                        ":START_ID(AssemblyEvent)": event_id,
                        ":END_ID(Component)": component_id,
                        "role": "component",
                        ":TYPE": "ACTS_ON",
                    }
                )
                if previous_event_id is not None:
                    edge_event_next_rows.append(
                        {
                            ":START_ID(AssemblyEvent)": previous_event_id,
                            ":END_ID(AssemblyEvent)": event_id,
                            "clip_result_id": clip_result_id,
                            ":TYPE": "NEXT",
                        }
                    )
                previous_event_id = event_id

            for component_name, state in sorted((graph.get("component_states") or {}).items()):
                component_name = str(component_name)
                component_id = make_component_id(component_name)
                component_rows_by_id.setdefault(
                    component_id,
                    _component_row(component_id, component_name),
                )
                edge_clip_component_state_rows.append(
                    {
                        ":START_ID(IndustRealClip)": clip_result_id,
                        ":END_ID(Component)": component_id,
                        "state": _component_state_text(state),
                        "state_known:boolean": state is not None,
                        ":TYPE": "ENDS_WITH_COMPONENT_STATE",
                    }
                )

    run_rows = [
        {
            "run_id:ID(IndustRealRun)": run_id,
            "name": run_id,
            "source_results_dir": str(results_dir),
            "exported_at": exported_at,
            "mode_count:int": len(mode_rows),
            "clip_result_count:int": len(clip_rows),
            ":LABEL": "IndustRealRun;PipelineRun",
        }
    ]

    rows_by_file = {
        "nodes_runs.csv": run_rows,
        "nodes_modes.csv": mode_rows,
        "nodes_clips.csv": clip_rows,
        "nodes_events.csv": event_rows,
        "nodes_components.csv": list(sorted(component_rows_by_id.values(), key=lambda row: row["component_id:ID(Component)"])),
        "nodes_goals.csv": goal_rows,
        "nodes_phases.csv": phase_rows,
        "edges_run_mode.csv": edge_run_mode_rows,
        "edges_mode_clip.csv": edge_mode_clip_rows,
        "edges_clip_event.csv": edge_clip_event_rows,
        "edges_event_next.csv": edge_event_next_rows,
        "edges_event_component.csv": edge_event_component_rows,
        "edges_clip_final_component_state.csv": edge_clip_component_state_rows,
        "edges_clip_goal.csv": edge_clip_goal_rows,
        "edges_goal_phase.csv": edge_goal_phase_rows,
        "edges_goal_target_component.csv": edge_goal_target_component_rows,
        "edges_phase_step.csv": edge_phase_step_rows,
        "edges_phase_next.csv": edge_phase_next_rows,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for filename, fields in CSV_SCHEMAS.items():
        rows = rows_by_file[filename]
        _write_csv(output_dir / filename, fields, rows)
        counts[filename] = len(rows)
    return counts


def make_mode_id(run_id: str, mode: str) -> str:
    return f"{run_id}::{mode}"


def make_clip_result_id(run_id: str, mode: str, archive_name: str, clip: str) -> str:
    return f"{run_id}::{mode}::{archive_name}::{clip}"


def make_event_id(run_id: str, mode: str, archive_name: str, clip: str, event_id: int) -> str:
    return f"{make_clip_result_id(run_id, mode, archive_name, clip)}::event_{event_id}"


def make_component_id(component_name: str) -> str:
    return f"industreal_component::{normalize_component_name(component_name)}"


def normalize_component_name(component_name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(component_name).lower()).strip("_")
    return cleaned or "unknown"


def _clip_row(
    *,
    run_id: str,
    mode: str,
    archive_name: str,
    split: str,
    clip: str,
    clip_result_id: str,
    n_frames: int,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "clip_result_id:ID(IndustRealClip)": clip_result_id,
        "display_name": f"{clip} ({mode})",
        "name": f"{clip} ({mode})",
        "run_id": run_id,
        "mode": mode,
        "archive_name": archive_name,
        "split": split,
        "clip": clip,
        "n_frames:int": n_frames,
        ":LABEL": "IndustRealClip;Recording",
    }
    metric_key_map = {
        "state_frames_scored:int": "state_frames_scored",
        "state_accuracy:float": "state_accuracy",
        "state_correct:int": "state_correct",
        "gt_steps:int": "gt_steps",
        "predicted_steps:int": "predicted_steps",
        "diagnostic_predicted_steps:int": "diagnostic_predicted_steps",
        "legal_state_rate:float": "legal_state_rate",
        "error_window_recall:float": "error_window_recall",
        "event_window_evidence_ratio:float": "event_window_evidence_ratio",
        "step_precision:float": "step_precision",
        "step_recall:float": "step_recall",
        "median_step_delay_frames:float": "median_step_delay_frames",
        "psr_pos:float": "psr_pos",
        "psr_f1:float": "psr_f1",
        "psr_avg_delay_s:float": "psr_avg_delay_s",
        "psr_tps:int": "psr_tps",
        "psr_fps:int": "psr_fps",
        "psr_fns:int": "psr_fns",
        "b3_diagnostic_step_precision:float": "b3_diagnostic_step_precision",
        "b3_diagnostic_step_recall:float": "b3_diagnostic_step_recall",
        "b3_diagnostic_median_delay_frames:float": "b3_diagnostic_median_delay_frames",
        "b3_diagnostic_psr_pos:float": "b3_diagnostic_psr_pos",
        "b3_diagnostic_psr_f1:float": "b3_diagnostic_psr_f1",
        "b3_diagnostic_psr_avg_delay_s:float": "b3_diagnostic_psr_avg_delay_s",
    }
    for csv_key, metric_key in metric_key_map.items():
        row[csv_key] = _csv_value(metrics.get(metric_key))
    return row


def _goal_row(
    *,
    cad_goal,
    run_id: str,
    mode: str,
    archive_name: str,
    clip: str,
    clip_result_id: str,
    goal_id: str,
) -> dict[str, Any]:
    return {
        "goal_id:ID(AssemblyGoal)": goal_id,
        "display_name": f"{cad_goal.goal_name} ({clip})",
        "name": f"{cad_goal.goal_name} ({clip})",
        "run_id": run_id,
        "mode": mode,
        "archive_name": archive_name,
        "clip": clip,
        "clip_result_id": clip_result_id,
        "goal_name": cad_goal.goal_name,
        "target_state_index:int": cad_goal.target_state_index,
        "target_state_name": cad_goal.target_state_name,
        "target_state_kind": cad_goal.target_state_kind,
        "target_state_asset": cad_goal.target_state_asset,
        "target_component_keys": cad_goal.target_component_keys,
        "target_components": cad_goal.target_components,
        "target_component_count:int": len(cad_goal.target_components),
        ":LABEL": "AssemblyGoal;CADAssemblyGoal",
    }


def _phase_row(
    *,
    run_id: str,
    mode: str,
    archive_name: str,
    clip: str,
    clip_result_id: str,
    goal_id: str,
    phase_id: str,
    phase_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "phase_id:ID(AssemblyPhase)": phase_id,
        "display_name": phase_summary["phase_name"],
        "name": phase_summary["phase_name"],
        "goal_id": goal_id,
        "clip_result_id": clip_result_id,
        "run_id": run_id,
        "mode": mode,
        "archive_name": archive_name,
        "clip": clip,
        "phase_key": phase_summary["phase_key"],
        "phase_name": phase_summary["phase_name"],
        "phase_order:int": phase_summary["phase_order"],
        "configured_order:int": phase_summary["configured_order"],
        "first_frame:int": phase_summary["first_frame"],
        "last_frame:int": phase_summary["last_frame"],
        "step_count:int": phase_summary["step_count"],
        "has_error:boolean": phase_summary["has_error"],
        "mean_confidence:float": phase_summary["mean_confidence"],
        "status": phase_summary["status"],
        ":LABEL": "AssemblyPhase",
    }


def _component_row(component_id: str, component_name: str) -> dict[str, Any]:
    return {
        "component_id:ID(Component)": component_id,
        "display_name": component_name,
        "name": component_name,
        "normalized_name": normalize_component_name(component_name),
        ":LABEL": "Component;IndustRealComponent",
    }


def _component_state_text(state: Any) -> str:
    if state is True:
        return "installed"
    if state is False:
        return "removed"
    return "unknown"


def _load_summary_lookup(reports_dir: Path | None) -> dict[tuple[str, str, str], dict[str, Any]]:
    if reports_dir is None:
        return {}
    summary_path = Path(reports_dir) / "summary.csv"
    if not summary_path.exists():
        return {}
    with open(summary_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {
        (str(row.get("run_mode")), str(row.get("archive_name")), str(row.get("clip"))): row
        for row in rows
    }


def _resolve_optional_catalog(
    *,
    explicit_path: Path | None,
    reports_dir: Path | None,
    filename: str,
) -> Path | None:
    if explicit_path is not None:
        return Path(explicit_path)
    if reports_dir is None:
        return None
    candidate = Path(reports_dir) / "cad" / filename
    return candidate if candidate.exists() else None


def _goal_defaults_from_rules(phase_rules_path: Path) -> tuple[str, int]:
    if not Path(phase_rules_path).exists():
        return DEFAULT_GOAL_NAME, DEFAULT_FINAL_STATE_INDEX
    data = _load_json(Path(phase_rules_path))
    return (
        str(data.get("goal_name") or DEFAULT_GOAL_NAME),
        int(data.get("final_state_index", DEFAULT_FINAL_STATE_INDEX)),
    )


def _load_metrics(
    metrics_path: Path,
    *,
    summary_lookup: dict[tuple[str, str, str], dict[str, Any]],
    mode: str,
    archive_name: str,
    clip: str,
) -> dict[str, Any]:
    if metrics_path.exists():
        return _load_json(metrics_path)
    return summary_lookup.get((mode, archive_name, clip), {})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fields})


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return json.dumps(list(value), ensure_ascii=True)
    return value
