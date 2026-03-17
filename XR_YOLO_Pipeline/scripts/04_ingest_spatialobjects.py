#!/usr/bin/env python3
"""04_ingest_spatialobjects.py — Ingest spatialobjects CSV (if available) into object_observations.csv.

NOTE: The current workspace no longer uses spatialobjects.csv.
This script is a passthrough/normalizer that outputs an empty CSV if no file is found,
allowing the pipeline to continue to script 05 which derives observations from RGB-D.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config
from src.objects import OBSERVATION_COLUMNS

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
):
    """Ingest spatialobjects CSV if present; otherwise signal that script 05 should be used."""
    cfg = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # Look for spatialobjects files
    so_dir = PROJECT_ROOT / "data/raw" / session / "spatialobjects"
    candidates = list(so_dir.glob("spatialobjects*.csv"))

    if not candidates:
        console.print("[yellow]No spatialobjects CSV found.[/yellow]")
        console.print("→ Script 05 (build_object_observations) will derive observations from RGB-D.")
        console.print("→ Skipping ingest, no output written.")
        return

    # Use spatialobjects_clean if available, else spatialobjects
    so_path = next((p for p in candidates if "clean" in p.name), candidates[0])
    console.print(f"[bold]Ingesting:[/bold] {so_path}")

    raw = pd.read_csv(so_path)
    console.print(f"  Raw rows: {len(raw)}, columns: {list(raw.columns)}")

    # Normalize to object_observations schema
    rows = []
    import uuid

    # Try to map common SpatialObjects column names
    col_map = {
        "id": "raw_object_id",
        "class": "semantic_class",
        "label": "label",
        "x": "x", "y": "y", "z": "z",
        "w": "w", "h": "h", "d": "d",
        "yaw": "yaw",
        "confidence": "confidence",
        "frame_idx": "frame_idx",
        "timestamp": "timestamp_ns",
    }

    for _, r in raw.iterrows():
        obs = {c: None for c in OBSERVATION_COLUMNS}
        obs["observation_id"] = f"obs_{uuid.uuid4().hex[:8]}"
        obs["source"] = "spatialobjects_csv"
        obs["room_id"] = cfg.get("default_room_id", "workstation_A")

        for src, dst in col_map.items():
            if src in r.index and dst in OBSERVATION_COLUMNS:
                obs[dst] = r[src]

        if obs["semantic_class"] is None:
            obs["semantic_class"] = "unknown"
        if obs["label"] is None:
            obs["label"] = obs["semantic_class"]
        if obs["confidence"] is None:
            obs["confidence"] = 0.5

        rows.append(obs)

    df = pd.DataFrame(rows)[OBSERVATION_COLUMNS]
    out = paths.object_observations
    df.to_csv(out, index=False)
    console.print(f"[green]✓ Wrote {len(df)} observations → {out}[/green]")


if __name__ == "__main__":
    app()
