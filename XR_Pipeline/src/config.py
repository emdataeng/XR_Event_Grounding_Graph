"""Configuration loader — reads YAML configs and exposes paths/thresholds."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Project root = parent of this src/ directory
_SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _SRC_DIR.parent

# Load local, gitignored secrets such as HF_TOKEN and NEO4J_PASSWORD.
load_dotenv(PROJECT_ROOT / ".env")


def _load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def load_pipeline_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    path = config_path or (PROJECT_ROOT / "configs" / "pipeline.yaml")
    return _load_yaml(path)


def load_thresholds(config_path: Optional[Path] = None) -> Dict[str, Any]:
    path = config_path or (PROJECT_ROOT / "configs" / "thresholds.yaml")
    return _load_yaml(path)


def load_neo4j_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    path = config_path or (PROJECT_ROOT / "configs" / "neo4j.yaml")
    cfg = _load_yaml(path)
    # Override with env vars if set
    cfg["uri"] = os.getenv("NEO4J_URI", cfg.get("uri", "bolt://localhost:7687"))
    cfg["user"] = os.getenv("NEO4J_USER", cfg.get("user", "neo4j"))
    cfg["password"] = os.getenv("NEO4J_PASSWORD", cfg.get("password", ""))
    cfg["database"] = os.getenv("NEO4J_DATABASE", cfg.get("database", "neo4j"))
    return cfg


class PipelinePaths:
    """Resolve all important filesystem paths for a given session."""

    def __init__(self, session_id: str = "session_001", cfg: Optional[Dict] = None):
        self.cfg = cfg or load_pipeline_config()
        self.session_id = session_id

        raw_root_str = self.cfg.get("raw_data_root", "../Quest_Capture/quest_capture")
        raw_root = Path(raw_root_str)
        if not raw_root.is_absolute():
            raw_root = (PROJECT_ROOT / raw_root).resolve()
        self.raw_root = raw_root

        processed_root = PROJECT_ROOT / self.cfg.get("processed_root", "data/processed") / session_id
        self.processed_root = processed_root

        self.manifests_dir = processed_root / "manifests"
        self.sample_vis_dir = self.manifests_dir / "sample_visualizations"
        self.objects_dir = processed_root / "objects"
        self.events_dir = processed_root / "events"
        self.graphs_dir = processed_root / "graphs"
        self.queries_dir = processed_root / "queries"
        self.neo4j_dir = processed_root / "neo4j"
        self.debug_pc_dir = self.graphs_dir / "debug_pointclouds"
        self.debug_box_dir = self.graphs_dir / "debug_boxes"
        self.reviews_dir = processed_root / "reviews" / "operations"

        # Key output files
        self.frame_manifest = self.manifests_dir / "frame_manifest.csv"
        self.manifest_validation = self.manifests_dir / "manifest_validation.json"
        self.object_observations = self.objects_dir / "object_observations.csv"
        self.object_tracks = self.objects_dir / "object_tracks.csv"
        self.track_summary = self.objects_dir / "track_summary.csv"
        self.track_debug = self.objects_dir / "track_debug.json"
        self.event_windows = self.events_dir / "event_windows.csv"
        self.track_motion_debug = self.objects_dir / "track_motion_debug.csv"
        self.support_state_transitions = self.objects_dir / "support_state_transitions.csv"
        self.events_csv = self.events_dir / "events.csv"
        self.event_object_roles = self.events_dir / "event_object_roles.csv"
        self.egg_graph = self.graphs_dir / "egg_graph.json"
        self.scene_state_package = self.graphs_dir / "scene_state_package.json"
        self.workflow_timeline = self.graphs_dir / "workflow_timeline.json"
        self.workflow_timeline_csv = self.graphs_dir / "workflow_timeline.csv"
        self.pruned_subgraph = self.queries_dir / "pruned_subgraph.json"
        self.query_answer = self.queries_dir / "query_answer.json"

        # Assembly reasoning layer (Phases 1–7)
        self.state_facts_json       = self.graphs_dir  / "state_facts.json"
        self.state_facts_csv        = self.graphs_dir  / "state_facts.csv"
        self.subtask_events         = self.objects_dir / "subtask_events.csv"
        self.subtask_sequence       = self.graphs_dir  / "subtask_sequence.json"
        self.assembly_graph         = self.graphs_dir  / "assembly_graph.json"
        self.assembly_state_package = self.graphs_dir  / "assembly_state_package.json"
        self.assembly_reasoning     = self.queries_dir / "assembly_reasoning.json"
        self.assembly_reviews_dir   = processed_root   / "reviews" / "assembly"
        self.assembly_review_json   = self.assembly_reviews_dir / "assembly_review.json"
        self.assembly_review_md     = self.assembly_reviews_dir / "assembly_review.md"

    def ensure_dirs(self):
        for d in [
            self.manifests_dir, self.sample_vis_dir, self.objects_dir,
            self.events_dir, self.graphs_dir, self.queries_dir,
            self.neo4j_dir, self.debug_pc_dir, self.debug_box_dir,
            self.reviews_dir, self.assembly_reviews_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def neo4j_csv(self, name: str) -> Path:
        return self.neo4j_dir / name
