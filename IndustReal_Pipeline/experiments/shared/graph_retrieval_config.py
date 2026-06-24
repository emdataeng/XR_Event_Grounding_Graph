"""Load shared graph-retrieval hyperparameters used by experiments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_graph_retrieval_config(path: str | Path) -> dict[str, int]:
    """Load and validate the shared sequence and semantic traversal budgets."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Shared graph retrieval config is missing: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = yaml.safe_load(handle) or {}

    retrieval = data.get("context_retrieval")
    if not isinstance(retrieval, dict):
        raise ValueError(f"Expected context_retrieval mapping in {config_path}")

    missing = [name for name in ("step_hops", "evidence_hops") if name not in retrieval]
    if missing:
        raise ValueError(
            f"Missing graph retrieval hyperparameters in {config_path}: {', '.join(missing)}"
        )

    values = {
        "step_hops": int(retrieval["step_hops"]),
        "evidence_hops": int(retrieval["evidence_hops"]),
    }
    for name, value in values.items():
        if value < 0:
            raise ValueError(f"{name} must be zero or greater in {config_path}")
    return values
