#!/usr/bin/env python3
"""10b_build_operation_events.py — Derive operation-level events from tracks + primitive events.

Produces operation_events.csv — the industrial-process layer of the pipeline.
Each row names *what is happening* (PICK_UP, PUT_DOWN, HOLD, CONTACT, TRANSFER …)
with evidence links back to the primitive events that triggered it.

Prerequisites
-------------
  object_tracks.csv     — 06_link_object_tracks.py
  event_windows.csv     — 07_build_event_windows.py

Output
------
  objects/operation_events.csv
  graphs/operation_event_overlays/  — representative frames annotated with
                                      detected operations (one PNG per event)

Usage
-----
  python scripts/10b_build_operation_events.py --session session_003
  python scripts/10b_build_operation_events.py --session session_003 --max-overlays 20
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.operation_events import detect_operation_events
from src.run_metadata import (
    build_run_metadata, save_run_metadata,
    check_staleness, emit_staleness_warnings,
)

app = typer.Typer()
console = Console()


@app.command()
def main(
    session:      str  = typer.Option("session_001", help="Session identifier"),
    config:       str  = typer.Option(None,          help="Path to pipeline.yaml override"),
    force:        bool = typer.Option(False, "--force",
                                      help="Continue even if upstream output is stale."),
    max_overlays: int  = typer.Option(30,
                                      help="Max overlay frames to export (0 = skip overlays)."),
):
    """Derive operation-level events and export event overlay frames."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Staleness guard ───────────────────────────────────────────────────────
    warnings = check_staleness(paths.processed_root, "07_build_event_windows", cfg, thr)
    if not emit_staleness_warnings(warnings, console=console, force=force):
        raise typer.Exit(1)

    # ── Load inputs ───────────────────────────────────────────────────────────
    for name, p in [("object_tracks.csv", paths.object_tracks),
                    ("event_windows.csv", paths.event_windows)]:
        if not p.exists():
            console.print(f"[red]{name} not found. Run preceding scripts first.[/red]")
            raise typer.Exit(1)

    tracks_df = pd.read_csv(paths.object_tracks)
    events_df = pd.read_csv(paths.event_windows)
    console.print(
        f"[bold]Detecting operation events[/bold] | "
        f"{tracks_df['track_id'].nunique()} tracks, "
        f"{len(events_df)} primitive events"
    )

    # ── Detect ────────────────────────────────────────────────────────────────
    ops_df = detect_operation_events(tracks_df, events_df, thr)

    # ── Save ──────────────────────────────────────────────────────────────────
    ops_path = paths.objects_dir / "operation_events.csv"
    ops_df.to_csv(ops_path, index=False)
    console.print(f"[green]✓ Wrote {len(ops_df)} operation events → {ops_path}[/green]")

    # ── Summary table ─────────────────────────────────────────────────────────
    if not ops_df.empty:
        type_counts = ops_df["operation_type"].value_counts()
        table = Table(title="Operation Event Distribution")
        table.add_column("Operation Type"); table.add_column("Count"); table.add_column("Avg Confidence")
        for op_type, cnt in type_counts.items():
            avg_conf = ops_df[ops_df["operation_type"] == op_type]["confidence"].mean()
            table.add_row(str(op_type), str(cnt), f"{avg_conf:.2f}")
        console.print(table)

        console.print("\n[bold]Sample operations:[/bold]")
        for _, r in ops_df.head(8).iterrows():
            agent = r["agent_track_id"] or "–"
            obj   = r["object_track_id"] or "–"
            console.print(
                f"  [cyan]{r['operation_type']}[/cyan]  "
                f"agent={agent}  object={obj}  "
                f"frames={r['start_frame_idx']}→{r['end_frame_idx']}  "
                f"conf={r['confidence']:.2f}"
            )
    else:
        console.print("[yellow]No operation events detected.[/yellow]")

    # ── Event overlay frames ──────────────────────────────────────────────────
    if max_overlays > 0 and not ops_df.empty:
        _export_event_overlays(ops_df, tracks_df, paths, max_overlays)

    # ── Run metadata ──────────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="10b_build_operation_events",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={"n_operations": len(ops_df)},
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


# ── Overlay export ─────────────────────────────────────────────────────────────

def _export_event_overlays(
    ops_df: pd.DataFrame,
    tracks_df: pd.DataFrame,
    paths: "PipelinePaths",
    max_overlays: int,
) -> None:
    """Write annotated PNG frames for a representative sample of detected operations.

    For each operation event, finds the middle frame of the event window, loads
    the corresponding debug_box overlay (if it exists), and copies it with a
    header annotation into the operation_event_overlays/ directory.
    """
    try:
        import cv2
    except ImportError:
        console.print("[yellow]cv2 not available — skipping overlays.[/yellow]")
        return

    out_dir = paths.graphs_dir / "operation_event_overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Distribute max_overlays evenly across operation types.
    exported = 0
    # Sort by confidence desc so we show the best evidence first.
    sample = ops_df.sort_values("confidence", ascending=False).head(max_overlays)

    for _, op in sample.iterrows():
        mid_frame = (int(op["start_frame_idx"]) + int(op["end_frame_idx"])) // 2

        # Try to load the existing debug box overlay for this frame.
        src_path = paths.debug_box_dir / f"frame_{mid_frame:06d}_detections.png"
        if not src_path.exists():
            # Fall back to nearest available frame
            available = sorted(paths.debug_box_dir.glob("frame_*_detections.png"))
            if not available:
                continue
            src_path = min(
                available,
                key=lambda p: abs(int(p.stem.split("_")[1]) - mid_frame),
            )

        img = cv2.imread(str(src_path))
        if img is None:
            continue

        # Add a header strip with operation info.
        h, w = img.shape[:2]
        header_h = 40
        header = np.zeros((header_h, w, 3), dtype=np.uint8)

        op_type  = str(op["operation_type"])
        agent    = str(op["agent_track_id"]) if op["agent_track_id"] else "–"
        obj      = str(op["object_track_id"]) if op["object_track_id"] else "–"
        conf     = float(op["confidence"])
        label    = (
            f"{op_type}  agent={agent}  obj={obj}  "
            f"conf={conf:.2f}  frame={mid_frame}"
        )

        # Color-code by confidence: green >0.7, yellow 0.5-0.7, red <0.5
        color = (
            (0, 200, 0) if conf > 0.7 else
            (0, 200, 200) if conf > 0.5 else
            (0, 100, 200)
        )
        cv2.putText(header, label, (8, 28), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, color, 1, cv2.LINE_AA)

        annotated = np.vstack([header, img])
        fname = (
            f"{op['operation_id']}_{op_type}_f{mid_frame:06d}.png"
        )
        out_path = out_dir / fname
        cv2.imwrite(str(out_path), annotated)
        exported += 1

    console.print(f"[green]✓ {exported} operation overlay frames → {out_dir}[/green]")


if __name__ == "__main__":
    app()
