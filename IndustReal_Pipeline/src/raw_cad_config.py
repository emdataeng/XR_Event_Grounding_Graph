"""Configuration and path helpers for the raw/CAD IndustReal pilot."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "configs" / "raw_cad_pilot.json"


def load_raw_cad_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    path = config_path or DEFAULT_CONFIG
    with open(path, "r") as f:
        return json.load(f)


def resolve_path(value: Optional[str], *, base: Path = ROOT) -> Optional[Path]:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (base / path).resolve()


@dataclass
class RawCadPaths:
    """Resolve working and results paths from the raw/CAD config."""

    cfg: dict[str, Any]
    root: Path = ROOT

    def __post_init__(self) -> None:
        path_cfg = self.cfg["paths"]
        self.data_root = resolve_path(path_cfg["data_root"], base=self.root)
        self.results_root = resolve_path(path_cfg["results_root"], base=self.root)
        self.reports_root = resolve_path(
            path_cfg.get("reports_root", path_cfg["results_root"]),
            base=self.root,
        )
        self.working_root = Path(path_cfg["working_root"])
        self.slice_root = self.working_root / path_cfg.get("slice_subdir", "slices")
        self.source_root = self.working_root / path_cfg.get("source_subdir", "source")
        self.working_results_root = self.working_root / path_cfg.get("working_results_subdir", "results")
        self.batch_extract_root = self.working_root / path_cfg.get("batch_extract_subdir", "dataset_batch")
        self.latest_slice_path = self.results_root / "latest_slice.json"

    def ensure_base_dirs(self) -> None:
        self.results_root.mkdir(parents=True, exist_ok=True)
        self.reports_root.mkdir(parents=True, exist_ok=True)
        self.slice_root.mkdir(parents=True, exist_ok=True)
        self.source_root.mkdir(parents=True, exist_ok=True)
        self.working_results_root.mkdir(parents=True, exist_ok=True)
        self.batch_extract_root.mkdir(parents=True, exist_ok=True)

    def slice_workdir(self, slice_id: str) -> Path:
        return self.slice_root / slice_id

    def slice_results_dir(self, slice_id: str) -> Path:
        return self.results_root / slice_id

    def slice_summary_path(self, slice_id: str) -> Path:
        return self.slice_results_dir(slice_id) / "slice_summary.json"

    def slice_clips_dir(self, slice_id: str) -> Path:
        return self.slice_workdir(slice_id)

    def slice_manifests_dir(self, slice_id: str) -> Path:
        return self.slice_results_dir(slice_id) / "manifests"

    def slice_visuals_dir(self, slice_id: str) -> Path:
        return self.slice_results_dir(slice_id) / "debug_visuals"

    def slice_cad_dir(self, slice_id: str) -> Path:
        return self.slice_results_dir(slice_id) / "cad"

    def clip_result_dir(self, slice_id: str, clip: str) -> Path:
        return self.slice_results_dir(slice_id) / clip

    def resolve_archive_path(self, key: str) -> Optional[Path]:
        return resolve_path(self.cfg["archives"].get(key), base=self.root)

    def dataset_run_reports_dir(self, run_id: str) -> Path:
        return self.reports_root / run_id

    def dataset_run_results_dir(self, run_id: str) -> Path:
        return self.working_results_root / run_id

    def dataset_run_extract_dir(self, run_id: str) -> Path:
        return self.batch_extract_root / run_id

    def dataset_run_shared_dir(self, run_id: str) -> Path:
        return self.dataset_run_results_dir(run_id) / "shared"

    def dataset_run_mode_dir(self, run_id: str, mode: str) -> Path:
        return self.dataset_run_results_dir(run_id) / "modes" / mode

    def dataset_clip_extract_dir(self, run_id: str, archive_name: str, clip: str) -> Path:
        return self.dataset_run_extract_dir(run_id) / archive_name / clip

    def dataset_clip_shared_dir(self, run_id: str, archive_name: str, clip: str) -> Path:
        return self.dataset_run_shared_dir(run_id) / archive_name / clip

    def dataset_clip_mode_dir(self, run_id: str, mode: str, archive_name: str, clip: str) -> Path:
        return self.dataset_run_mode_dir(run_id, mode) / archive_name / clip

    def dataset_run_manifest_path(self, run_id: str) -> Path:
        return self.dataset_run_reports_dir(run_id) / "run_manifest.json"

    def dataset_failure_log_path(self, run_id: str) -> Path:
        return self.dataset_run_reports_dir(run_id) / "failure_log.json"

    def dataset_clip_inventory_path(self, run_id: str) -> Path:
        return self.dataset_run_reports_dir(run_id) / "clip_inventory.csv"

    def dataset_summary_path(self, run_id: str) -> Path:
        return self.dataset_run_reports_dir(run_id) / "summary.csv"

    def dataset_mode_comparison_path(self, run_id: str) -> Path:
        return self.dataset_run_reports_dir(run_id) / "mode_comparison.csv"
