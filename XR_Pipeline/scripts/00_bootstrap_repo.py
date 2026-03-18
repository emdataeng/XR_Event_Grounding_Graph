#!/usr/bin/env python3
"""00_bootstrap_repo.py — Create repo structure, configs, and schema docs."""
import sys
from pathlib import Path

# Allow running from repo root or scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Bootstrap XR_Pipeline repo structure.")
console = Console()


DIRS = [
    "configs",
    "data/raw/session_001/rgb",
    "data/raw/session_001/depth",
    "data/raw/session_001/metadata",
    "data/raw/session_001/spatialobjects",
    "data/interim/session_001",
    "data/processed/session_001/manifests/sample_visualizations",
    "data/processed/session_001/objects",
    "data/processed/session_001/events",
    "data/processed/session_001/graphs/debug_pointclouds",
    "data/processed/session_001/graphs/debug_boxes",
    "data/processed/session_001/queries",
    "data/processed/session_001/neo4j",
    "docs/schemas",
    "docs/decisions",
    "notebooks",
    "scripts",
    "src",
    "tests",
    "neo4j",
]


@app.command()
def main():
    """Bootstrap the XR_Pipeline repository structure."""
    project_root = Path(__file__).resolve().parent.parent
    console.print(Panel(f"[bold green]Bootstrapping XR_Pipeline[/bold green]\n{project_root}"))

    # Create directories
    for d in DIRS:
        (project_root / d).mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] {d}/")

    # Create .gitkeep in data dirs to preserve empty folders
    for d in DIRS:
        p = project_root / d
        gitkeep = p / ".gitkeep"
        if not any(p.iterdir()) and not gitkeep.exists():
            gitkeep.touch()

    # Create schema docs
    _write_if_missing(project_root / "docs/schemas/frame_manifest.md", _FRAME_MANIFEST_SCHEMA)
    _write_if_missing(project_root / "docs/schemas/object_observations.md", _OBS_SCHEMA)
    _write_if_missing(project_root / "docs/schemas/events.md", _EVENTS_SCHEMA)
    _write_if_missing(project_root / "docs/schemas/egg_schema.md", _EGG_SCHEMA)
    _write_if_missing(project_root / "docs/decisions/design_notes.md", _DESIGN_NOTES)

    # Create .env.example if missing
    env_example = project_root / ".env.example"
    if not env_example.exists():
        env_example.write_text(
            "NEO4J_URI=bolt://localhost:7687\nNEO4J_USER=neo4j\nNEO4J_PASSWORD=\n"
        )

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Copy .env.example → .env and fill in credentials")
    console.print("  2. Run: python scripts/01_build_frame_manifest.py --session session_001")
    console.print("  3. Run: python scripts/02_validate_manifest.py --session session_001")
    console.print("[bold green]Bootstrap complete.[/bold green]")


def _write_if_missing(path: Path, content: str):
    if not path.exists():
        path.write_text(content)
        console.print(f"  [cyan]✓[/cyan] {path.relative_to(path.parent.parent.parent)}")


_FRAME_MANIFEST_SCHEMA = """\
# Frame Manifest Schema

Canonical CSV with one row per captured frame.

| Column | Type | Description |
|---|---|---|
| frame_idx | int | Frame index |
| timestamp_ns | int | Timestamp in nanoseconds (relative to first frame) |
| rgb_path | str | Relative path to RGBA file |
| depth_path | str | Relative path to depth .npy file (or empty) |
| depth_encoding | str | npy / f32 / none |
| depth_scale | float | Scale factor (1.0 = already meters) |
| fx, fy, cx, cy | float | Camera intrinsics |
| width, height | int | Image dimensions |
| T_world_cam_00..15 | float | Flattened 4x4 pose matrix row-major |
| room_id | str | Room/workstation label |
| source_stream | str | e.g. quest3_capture |
| notes | str | Optional warnings |
"""

_OBS_SCHEMA = """\
# Object Observations Schema

One row per detected/observed object per frame.

| Column | Description |
|---|---|
| observation_id | Unique ID |
| frame_idx | Frame index |
| timestamp_ns | Timestamp ns |
| semantic_class | Object class |
| x,y,z | World-frame centroid (m) |
| w,h,d | Bounding box extents (m) |
| confidence | Detection confidence 0-1 |
| source | depth_blobs / detection / manual |
"""

_EVENTS_SCHEMA = """\
# Events Schema

event_windows.csv: coarse time windows
events.csv: enriched with summaries
event_object_roles.csv: per-object role in each event
"""

_EGG_SCHEMA = """\
# EGG Graph Schema

egg_graph.json contains:
- graph_metadata
- rooms[]
- objects[] with time_variant_history
- events[]
- event_edges[] (event → object roles)
- room_edges[] (room → object)
- temporal_edges[] (event BEFORE event)
"""

_DESIGN_NOTES = """\
# Design Notes

## Data source
Quest 3 mixed-reality capture: RGBA32 raw bytes + float32 depth (meters) + JSON pose metadata.

## Timestamps
Windows FILETIME ticks → convert to relative nanoseconds (first frame = 0).

## Camera intrinsics
Not embedded in metadata. Using Quest 3 approximate defaults:
  fx=240, fy=240, cx=160, cy=120 for 320x240 resolution.
Override in configs/pipeline.yaml.

## Object detection
Layer A: depth-blob segmentation (no model required).
Layer B: YOLO (optional, set yolo_model in pipeline.yaml).

## EGG graph
Following EGG paper architecture but pragmatic:
no requirement for perfect 3D reconstruction.
"""


if __name__ == "__main__":
    app()
