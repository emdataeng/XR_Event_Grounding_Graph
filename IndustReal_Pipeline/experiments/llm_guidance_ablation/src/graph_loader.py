"""Load experiment artifacts for selected datasets and clips."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetSelection:
    """Identifies the dataset and optional clip used for an experiment run."""

    kind: str
    clip_id: str | None = None


def load_experiment_artifacts(config: dict[str, Any], selection: DatasetSelection) -> dict[str, Any]:
    """Load generated steps, domain files, rules, and graph artifacts.

    This placeholder defines the integration point between the experiment and
    the thesis artifacts produced by scripts 14 through 19.
    """
    raise NotImplementedError("Artifact loading is not implemented yet.")


def resolve_path(path_value: str, base_dir: Path | None = None) -> Path:
    """Resolve a configured path relative to an optional base directory."""
    path = Path(path_value)
    if path.is_absolute() or base_dir is None:
        return path
    return base_dir / path
