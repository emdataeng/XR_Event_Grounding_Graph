"""Helpers for importing IndustReal Neo4j CSVs."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_CSVS = [
    "nodes_runs.csv",
    "nodes_modes.csv",
    "nodes_clips.csv",
    "nodes_events.csv",
    "nodes_components.csv",
    "nodes_goals.csv",
    "nodes_phases.csv",
    "edges_run_mode.csv",
    "edges_mode_clip.csv",
    "edges_clip_event.csv",
    "edges_event_next.csv",
    "edges_event_component.csv",
    "edges_clip_final_component_state.csv",
    "edges_clip_goal.csv",
    "edges_goal_phase.csv",
    "edges_goal_target_component.csv",
    "edges_phase_step.csv",
    "edges_phase_next.csv",
]

CONSTRAINT_CYPHERS = [
    "CREATE CONSTRAINT industreal_run_id IF NOT EXISTS FOR (n:IndustRealRun) REQUIRE n.run_id IS UNIQUE",
    "CREATE CONSTRAINT industreal_mode_id IF NOT EXISTS FOR (n:IndustRealMode) REQUIRE n.mode_id IS UNIQUE",
    "CREATE CONSTRAINT industreal_clip_id IF NOT EXISTS FOR (n:IndustRealClip) REQUIRE n.clip_result_id IS UNIQUE",
    "CREATE CONSTRAINT industreal_event_id IF NOT EXISTS FOR (n:AssemblyEvent) REQUIRE n.event_id IS UNIQUE",
    "CREATE CONSTRAINT industreal_component_id IF NOT EXISTS FOR (n:IndustRealComponent) REQUIRE n.component_id IS UNIQUE",
    "CREATE CONSTRAINT industreal_goal_id IF NOT EXISTS FOR (n:AssemblyGoal) REQUIRE n.goal_id IS UNIQUE",
    "CREATE CONSTRAINT industreal_phase_id IF NOT EXISTS FOR (n:AssemblyPhase) REQUIRE n.phase_id IS UNIQUE",
]

DELETE_RUN_CYPHER = """
MATCH (r:IndustRealRun {run_id: $run_id})
OPTIONAL MATCH (r)-[:HAS_MODE]->(m:IndustRealMode)
OPTIONAL MATCH (m)-[:HAS_CLIP]->(c:IndustRealClip)
OPTIONAL MATCH (c)-[:HAS_GOAL]->(g:AssemblyGoal)
OPTIONAL MATCH (g)-[:HAS_PHASE]->(p:AssemblyPhase)
OPTIONAL MATCH (c)-[:HAS_STEP]->(e:AssemblyEvent)
WITH collect(r) + collect(m) + collect(c) + collect(g) + collect(p) + collect(e) AS nodes
UNWIND nodes AS n
WITH DISTINCT n
WHERE n IS NOT NULL
DETACH DELETE n
"""

DELETE_ORPHAN_COMPONENTS_CYPHER = """
MATCH (component:IndustRealComponent)
WHERE NOT ()-[:ACTS_ON]->(component)
  AND NOT ()-[:ENDS_WITH_COMPONENT_STATE]->(component)
  AND NOT ()-[:TARGETS_COMPONENT]->(component)
DETACH DELETE component
"""


def require_csv_files(csv_dir: Path) -> None:
    missing = [filename for filename in REQUIRED_CSVS if not (csv_dir / filename).exists()]
    if missing:
        missing_list = "\n".join(f"  - {name}" for name in missing)
        raise FileNotFoundError(f"Missing required Neo4j CSV files in {csv_dir}:\n{missing_list}")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_csv_bundle(csv_dir: Path) -> dict[str, list[dict[str, str]]]:
    csv_dir = Path(csv_dir)
    require_csv_files(csv_dir)
    return {filename: read_csv_rows(csv_dir / filename) for filename in REQUIRED_CSVS}


def parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(float(value))


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def parse_bool(value: str | None) -> bool | None:
    if value is None or value == "":
        return None
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_json_list(value: str | None) -> list[str] | None:
    if value is None or value == "":
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        return None
    return [str(item) for item in parsed]


def clean_props(props: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in props.items() if value is not None}
