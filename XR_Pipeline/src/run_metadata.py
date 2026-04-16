"""run_metadata.py — Config hashing, run provenance, and staleness detection.

Each pipeline stage writes a run_metadata.json to the session's processed root
after it completes. Downstream stages call check_staleness() to warn when their
inputs were produced under a different config than the current one.

No automatic rebuilding — we warn loudly and require --force to continue.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Hashing ──────────────────────────────────────────────────────────────────

def _hash_file(path: Path) -> str:
    """SHA256 of a file's contents. Returns 'missing' if file does not exist."""
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _hash_dict(d: Dict) -> str:
    """Stable SHA256 of a JSON-serialisable dict."""
    raw = json.dumps(d, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _git_commit() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=3,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


# ── Metadata record ───────────────────────────────────────────────────────────

def build_run_metadata(
    session_id: str,
    stage: str,
    pipeline_cfg: Dict,
    thresholds_cfg: Dict,
    *,
    pipeline_yaml_path: Optional[Path] = None,
    thresholds_yaml_path: Optional[Path] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a run_metadata dict for a completed pipeline stage.

    Args:
        session_id:           e.g. "session_003"
        stage:                e.g. "05_build_object_observations"
        pipeline_cfg:         loaded pipeline config dict
        thresholds_cfg:       loaded thresholds config dict
        pipeline_yaml_path:   if provided, also hash the file bytes
        thresholds_yaml_path: if provided, also hash the file bytes
        extra:                any additional key/value pairs to store
    """
    meta: Dict[str, Any] = {
        "session_id": session_id,
        "stage": stage,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        # Config content hashes (catches in-memory overrides too)
        "pipeline_config_hash": _hash_dict(pipeline_cfg),
        "thresholds_hash": _hash_dict(thresholds_cfg),
    }

    # File-level hashes let us detect edits that didn't go through load_pipeline_config
    if pipeline_yaml_path:
        meta["pipeline_yaml_file_hash"] = _hash_file(pipeline_yaml_path)
    if thresholds_yaml_path:
        meta["thresholds_yaml_file_hash"] = _hash_file(thresholds_yaml_path)

    if extra:
        meta.update(extra)

    return meta


# ── Persist / load ────────────────────────────────────────────────────────────

def _metadata_path(processed_root: Path, stage: str) -> Path:
    return processed_root / f"run_metadata_{stage}.json"


def save_run_metadata(processed_root: Path, meta: Dict[str, Any]) -> Path:
    """Write run_metadata_<stage>.json under processed_root."""
    path = _metadata_path(processed_root, meta["stage"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, default=str))
    return path


def load_run_metadata(processed_root: Path, stage: str) -> Optional[Dict[str, Any]]:
    """Load a previously saved run_metadata for a stage, or None if not found."""
    path = _metadata_path(processed_root, stage)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


# ── Staleness checks ──────────────────────────────────────────────────────────

class StalenessWarning:
    def __init__(self, stage: str, field: str, previous: str, current: str):
        self.stage = stage
        self.field = field
        self.previous = previous
        self.current = current

    def __str__(self) -> str:
        return (
            f"[STALE] Stage '{self.stage}': {self.field} changed "
            f"({self.previous} → {self.current}). "
            f"Downstream output may not match current config."
        )


def check_staleness(
    processed_root: Path,
    upstream_stage: str,
    pipeline_cfg: Dict,
    thresholds_cfg: Dict,
) -> List[StalenessWarning]:
    """Check if a previous stage run is stale relative to current config.

    Returns a (possibly empty) list of StalenessWarnings. Callers decide
    whether to abort or continue with --force.
    """
    prev = load_run_metadata(processed_root, upstream_stage)
    if prev is None:
        return []  # No metadata yet — not a staleness issue, just a first run

    warnings: List[StalenessWarning] = []
    current_pipeline_hash = _hash_dict(pipeline_cfg)
    current_thresholds_hash = _hash_dict(thresholds_cfg)

    if prev.get("pipeline_config_hash") != current_pipeline_hash:
        warnings.append(StalenessWarning(
            upstream_stage, "pipeline_config_hash",
            prev.get("pipeline_config_hash", "?"), current_pipeline_hash,
        ))

    if prev.get("thresholds_hash") != current_thresholds_hash:
        warnings.append(StalenessWarning(
            upstream_stage, "thresholds_hash",
            prev.get("thresholds_hash", "?"), current_thresholds_hash,
        ))

    return warnings


def emit_staleness_warnings(
    warnings: List[StalenessWarning],
    console=None,
    force: bool = False,
) -> bool:
    """Print staleness warnings and return True if execution should continue.

    If force=True, prints warnings but continues. If force=False and there
    are warnings, prints a hint to rerun with --force and returns False.
    """
    if not warnings:
        return True

    lines = [str(w) for w in warnings]
    header = "Staleness detected — upstream output may not match current config:"
    separator = "─" * 70

    if console is not None:
        console.print(f"\n[yellow]{separator}[/yellow]")
        console.print(f"[yellow bold]{header}[/yellow bold]")
        for line in lines:
            console.print(f"[yellow]  {line}[/yellow]")
        if force:
            console.print("[yellow]  Continuing anyway (--force).[/yellow]")
        else:
            console.print(
                "[yellow]  Re-run the upstream stage or pass --force to continue.[/yellow]"
            )
        console.print(f"[yellow]{separator}[/yellow]\n")
    else:
        print(f"\n{separator}")
        print(header)
        for line in lines:
            print(f"  {line}")
        if force:
            print("  Continuing anyway (--force).")
        else:
            print("  Re-run the upstream stage or pass --force to continue.")
        print(f"{separator}\n")

    return force
