#!/usr/bin/env python3
"""evaluation/bakeoff.py — Compare detector configurations on annotated frames.

For each model/config combination listed via --models, loads the corresponding
object_observations.csv (run with that config), evaluates against ground-truth
annotations, and produces a comparison CSV + printed table.

Usage:
    # Compare two existing observation CSVs against annotations
    python evaluation/bakeoff.py \\
        --session session_003 \\
        --annotations evaluation/annotations/session_003.json \\
        --models grounding_dino mm_grounding_dino

    # The script looks for CSVs at:
    #   data/processed/<session>/objects/object_observations_<model>.csv
    # OR the default:
    #   data/processed/<session>/objects/object_observations.csv  (for "current")

Labelling your frames:
    Create evaluation/annotations/<session_id>.json. Format:
    {
      "session_id": "session_003",
      "frames": [
        {
          "frame_idx": 14,
          "objects": [
            {"class": "red_lego", "bbox": [x1, y1, x2, y2]},
            {"class": "blue_lego", "bbox": [x1, y1, x2, y2]}
          ]
        }
      ]
    }
    Coordinates are in RGB image pixel space (640x240 for session_003).
    At least 20-30 annotated frames are recommended for meaningful results.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from evaluation.metrics import (
    load_annotations,
    load_detections_from_csv,
    match_detections_to_annotations,
    metrics_to_dataframe,
    print_metrics_table,
)

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_003", help="Session ID"),
    annotations: str = typer.Option(
        None,
        help="Path to annotation JSON. Defaults to evaluation/annotations/<session>.json",
    ),
    models: Optional[List[str]] = typer.Option(
        None,
        help="Model/config suffixes to compare. Each maps to object_observations_<suffix>.csv. "
             "Use 'current' for the default object_observations.csv.",
    ),
    iou_threshold: float = typer.Option(0.5, help="IoU threshold for TP matching"),
    out: Optional[str] = typer.Option(None, help="Write comparison CSV to this path"),
):
    """Evaluate and compare detector configurations against annotations."""
    # Resolve annotation file
    eval_dir = Path(__file__).resolve().parent
    if annotations:
        ann_path = Path(annotations)
    else:
        ann_path = eval_dir / "annotations" / f"{session}.json"

    if not ann_path.exists():
        console.print(f"[red]Annotation file not found: {ann_path}[/red]")
        console.print(
            "  Create it with at least 20 labelled frames.\n"
            "  See the docstring at the top of this file for the format."
        )
        raise typer.Exit(1)

    ann_boxes = load_annotations(ann_path)
    console.print(f"[bold]Loaded {len(ann_boxes)} annotated boxes from {ann_path.name}[/bold]")
    console.print(f"  Annotated frames: {len(set(b.frame_idx for b in ann_boxes))}")
    console.print(f"  Classes: {list(set(b.cls for b in ann_boxes))}\n")

    # Resolve model list
    _models = models if models else ["current"]

    # Resolve base processed dir
    project_root = Path(__file__).resolve().parent.parent
    objects_dir = project_root / "data" / "processed" / session / "objects"

    all_results = []

    for model_key in _models:
        if model_key == "current":
            csv_path = objects_dir / "object_observations.csv"
        else:
            csv_path = objects_dir / f"object_observations_{model_key}.csv"

        if not csv_path.exists():
            console.print(f"[yellow]SKIP {model_key}: {csv_path} not found[/yellow]")
            continue

        console.print(f"Evaluating: [bold]{model_key}[/bold]  ({csv_path.name})")
        det_boxes = load_detections_from_csv(csv_path)

        annotated_frames = set(b.frame_idx for b in ann_boxes)
        det_in_annotated = [d for d in det_boxes if d.frame_idx in annotated_frames]

        console.print(
            f"  Detections in annotated frames: {len(det_in_annotated)} "
            f"(of {len(det_boxes)} total)"
        )

        per_class = match_detections_to_annotations(
            det_in_annotated, ann_boxes, iou_threshold=iou_threshold,
        )

        # Load run_metadata if available
        meta_path = objects_dir.parent / f"run_metadata_05_build_object_observations.json"
        meta = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
            except Exception:
                pass

        df_m = metrics_to_dataframe(per_class)
        df_m.insert(0, "model_key", model_key)
        df_m["iou_threshold"] = iou_threshold
        df_m["pipeline_config_hash"] = meta.get("pipeline_config_hash", "?")
        df_m["detection_prompt"] = meta.get("detection_prompt", "?")
        df_m["grounding_dino_model"] = meta.get("grounding_dino_model", "?")
        all_results.append(df_m)

        print_metrics_table(per_class, title=f"  {model_key}")
        console.print()

    if not all_results:
        console.print("[yellow]No results to compare.[/yellow]")
        return

    df_all = pd.concat(all_results, ignore_index=True)

    # Summary: F1 per model
    console.print("[bold]F1 Summary[/bold]")
    summary_table = Table(show_lines=True)
    summary_table.add_column("model_key")
    summary_table.add_column("class")
    summary_table.add_column("precision", justify="right")
    summary_table.add_column("recall", justify="right")
    summary_table.add_column("f1", justify="right")
    summary_table.add_column("mean_iou", justify="right")

    for _, row in df_all.sort_values(["model_key", "class"]).iterrows():
        summary_table.add_row(
            row["model_key"], row["class"],
            f"{row['precision']:.3f}", f"{row['recall']:.3f}",
            f"{row['f1']:.3f}", f"{row['mean_iou']:.3f}",
        )
    console.print(summary_table)

    if out:
        out_path = Path(out)
        df_all.to_csv(out_path, index=False)
        console.print(f"\n[green]✓ Comparison CSV → {out_path}[/green]")


if __name__ == "__main__":
    app()
