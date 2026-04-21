#!/usr/bin/env python3
"""sweep_grounding_dino.py — Prompt and threshold sweep for Grounding DINO.

Runs the current Grounding DINO model over a small number of frames with
different prompt/threshold combinations and reports detection counts per class.
Use this to tune prompts and thresholds before committing to a full run.

Usage examples:
    # Quick sweep with defaults (first 10 frames, built-in prompt variants)
    python scripts/sweep_grounding_dino.py --session session_003 --max-frames 10

    # Custom prompt list and box threshold range
    python scripts/sweep_grounding_dino.py \\
        --session session_003 \\
        --max-frames 10 \\
        --prompts "red lego. blue lego." \\
        --prompts "a red lego brick. a blue lego brick." \\
        --box-thresholds 0.20 0.25 0.30

    # Save results to a CSV
    python scripts/sweep_grounding_dino.py \\
        --session session_003 --max-frames 15 --out sweep_results.csv
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.io_utils import load_rgba, load_depth_npy, rgba_to_rgb

app = typer.Typer(add_completion=False)
console = Console()

# Default prompt variants to try if none supplied
DEFAULT_PROMPTS = [
    "red lego. blue lego.",
    "a red lego brick. a blue lego brick.",
    "red block. blue block.",
    "red lego brick. blue lego brick. red brick. blue brick.",
]


@app.command()
def main(
    session: str = typer.Option("session_003", help="Session ID"),
    config: Optional[str] = typer.Option(None, help="Path to pipeline.yaml"),
    max_frames: int = typer.Option(10, help="Number of frames to sweep over (0 = all)"),
    prompts: Optional[List[str]] = typer.Option(None, help="Prompts to try (repeatable). Defaults to built-in variants."),
    box_thresholds: Optional[List[float]] = typer.Option(None, help="Box thresholds to try (repeatable). Default: 0.20 0.25 0.30 0.35."),
    text_threshold: float = typer.Option(0.25, help="Fixed text threshold for all runs"),
    model_id: Optional[str] = typer.Option(None, help="Override grounding_dino_model from config"),
    out: Optional[str] = typer.Option(None, help="Write results CSV to this path"),
):
    """Sweep Grounding DINO prompts and thresholds over a small frame sample."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)

    if not paths.frame_manifest.exists():
        console.print("[red]frame_manifest.csv not found. Run 01 first.[/red]")
        raise typer.Exit(1)

    df_manifest = pd.read_csv(paths.frame_manifest)
    if max_frames > 0:
        df_manifest = df_manifest.head(max_frames)

    flip_vertical = cfg.get("camera", {}).get("flip_vertical", True)
    _model_id = model_id or cfg.get("grounding_dino_model", "IDEA-Research/grounding-dino-base")
    _prompts = prompts if prompts else DEFAULT_PROMPTS
    _box_thresholds = box_thresholds if box_thresholds else [0.20, 0.25, 0.30, 0.35]

    console.print(f"\n[bold]Sweep configuration[/bold]")
    console.print(f"  Model: {_model_id}")
    console.print(f"  Frames: {len(df_manifest)}")
    console.print(f"  Prompts: {len(_prompts)}")
    console.print(f"  Box thresholds: {_box_thresholds}")
    console.print(f"  Text threshold: {text_threshold} (fixed)")
    console.print(f"  Total runs: {len(_prompts) * len(_box_thresholds)}\n")

    # Load model once
    console.print(f"Loading Grounding DINO: [bold]{_model_id}[/bold]")
    try:
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
        import torch
        processor = AutoProcessor.from_pretrained(_model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(_model_id)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        model.eval()
        console.print(f"[green]✓ Loaded on {device}[/green]\n")
    except ImportError:
        console.print("[red]transformers not installed.[/red]")
        raise typer.Exit(1)

    # Pre-load all RGB frames
    console.print("Pre-loading frames...")
    frames = []
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    for _, row in df_manifest.iterrows():
        rp = Path(row["rgb_path"])
        if not rp.is_absolute():
            rp = (PROJECT_ROOT.parent / rp).resolve()
        if not rp.exists():
            continue
        try:
            rgba = load_rgba(rp, width=int(row["width"]), height=int(row["height"]),
                             stereo_eye=cfg.get("stereo_eye"), flip_vertical=flip_vertical)
            rgb = rgba_to_rgb(rgba)
            frames.append({
                "frame_idx": int(row["frame_idx"]),
                "rgb": rgb,
            })
        except Exception as e:
            console.print(f"[yellow]Skipped frame {row['frame_idx']}: {e}[/yellow]")

    if not frames:
        console.print("[red]No frames loaded. Check raw_data_root in pipeline.yaml.[/red]")
        raise typer.Exit(1)

    console.print(f"Loaded {len(frames)} frames.\n")

    # ── Run sweep ─────────────────────────────────────────────────────────────
    results = []

    import torch
    from PIL import Image

    total_runs = len(_prompts) * len(_box_thresholds)
    run_num = 0

    for prompt in _prompts:
        for box_thr in _box_thresholds:
            run_num += 1
            console.print(f"[dim]Run {run_num}/{total_runs}  prompt='{prompt}'  box_thr={box_thr}[/dim]")

            all_labels: list[str] = []
            t0 = time.perf_counter()

            for frame in frames:
                rgb = frame["rgb"]
                pil_image = Image.fromarray(rgb)
                rgb_h, rgb_w = rgb.shape[:2]

                inputs = processor(images=pil_image, text=prompt, return_tensors="pt")
                inputs = {k: v.to(next(model.parameters()).device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = model(**inputs)

                res = processor.post_process_grounded_object_detection(
                    outputs,
                    input_ids=inputs["input_ids"],
                    threshold=box_thr,
                    text_threshold=text_threshold,
                    target_sizes=[(rgb_h, rgb_w)],
                )
                if res:
                    labels = res[0].get("text_labels", res[0].get("labels", []))
                    scores = res[0]["scores"].tolist()
                    for lbl, score in zip(labels, scores):
                        all_labels.append(lbl.strip().rstrip(".").strip())

            elapsed = time.perf_counter() - t0
            label_counts = pd.Series(all_labels).value_counts().to_dict() if all_labels else {}
            total_det = len(all_labels)
            det_per_frame = total_det / max(len(frames), 1)

            row = {
                "prompt": prompt,
                "box_threshold": box_thr,
                "text_threshold": text_threshold,
                "n_frames": len(frames),
                "total_detections": total_det,
                "det_per_frame": round(det_per_frame, 2),
                "elapsed_s": round(elapsed, 1),
                "label_counts": json.dumps(label_counts),
            }
            results.append(row)

    # ── Print results table ───────────────────────────────────────────────────
    df_results = pd.DataFrame(results)

    table = Table(title="Grounding DINO Sweep Results", show_lines=True)
    table.add_column("Prompt", max_width=50, overflow="fold")
    table.add_column("box_thr", justify="right")
    table.add_column("total_det", justify="right")
    table.add_column("det/frame", justify="right")
    table.add_column("elapsed_s", justify="right")
    table.add_column("label_counts", max_width=60, overflow="fold")

    for _, r in df_results.iterrows():
        table.add_row(
            r["prompt"],
            str(r["box_threshold"]),
            str(r["total_detections"]),
            str(r["det_per_frame"]),
            f"{r['elapsed_s']}s",
            r["label_counts"],
        )

    console.print(table)

    if out:
        out_path = Path(out)
        df_results.to_csv(out_path, index=False)
        console.print(f"\n[green]✓ Results saved → {out_path}[/green]")

    # Highlight best candidate: highest det/frame without too many composites
    console.print("\n[bold]Recommendation:[/bold]")
    best = df_results.loc[df_results["det_per_frame"].idxmax()]
    console.print(
        f"  Highest detections/frame: prompt='{best['prompt']}'  "
        f"box_thr={best['box_threshold']}  ({best['det_per_frame']} det/frame)"
    )
    console.print("  Review label_counts column to check for composite labels (e.g. 'red lego blue lego').")
    console.print("  Ideal: each expected object appears as its own label in every frame.\n")


if __name__ == "__main__":
    app()
