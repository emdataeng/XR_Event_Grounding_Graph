"""Build metadata for the novice-question set used by an experiment run."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


def build_question_set_manifest(path: str | Path, case_count: int) -> dict[str, Any]:
    """Return stable metadata identifying the question YAML used for a run."""
    question_path = Path(path)
    if not question_path.exists():
        raise FileNotFoundError(f"Question set is missing: {question_path}")

    content = question_path.read_bytes()
    data = yaml.safe_load(content.decode("utf-8")) or {}
    if not isinstance(data, dict):
        data = {}

    return {
        "path": str(question_path),
        "question_set_id": data.get("question_set_id"),
        "question_set_version": data.get("question_set_version"),
        "sha256": hashlib.sha256(content).hexdigest(),
        "case_count": int(case_count),
    }
