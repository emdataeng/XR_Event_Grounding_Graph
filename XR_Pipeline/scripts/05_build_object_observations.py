#!/usr/bin/env python3
"""05_build_object_observations.py — Derive object observations from RGB-D frames.

Detection backends (set via configs/pipeline.yaml → observations_source):
  grounding_dino  — open-vocabulary detection with text prompts (default, requires transformers)
  yolo            — YOLOv8 fixed-class detection (requires ultralytics)
  depth_blobs     — depth segmentation, no semantic labels (no extra dependencies)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import numpy as np
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.io_utils import load_rgba, load_depth_npy, rgba_to_rgb
from src.depth_utils import extract_depth_blobs, blob_to_world_box
from src.geometry import flat_to_matrix, deproject_pixel_to_world
from src.objects import make_observation, classify_blob, OBSERVATION_COLUMNS
from src.viz import draw_blobs_on_rgb, draw_detections_on_rgb

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    max_frames: int = typer.Option(0, help="Limit to first N frames (0 = all)"),
    save_debug: bool = typer.Option(True, help="Save detection overlay images"),
):
    """Build object_observations.csv from RGB-D frames."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    if not paths.frame_manifest.exists():
        console.print("[red]frame_manifest.csv not found. Run 01 first.[/red]")
        raise typer.Exit(1)

    df_manifest = pd.read_csv(paths.frame_manifest)
    if max_frames > 0:
        df_manifest = df_manifest.head(max_frames)

    obs_source = cfg.get("observations_source", "grounding_dino")
    det_cfg = thr.get("detection", {})
    dino_cfg = thr.get("grounding_dino", {})
    depth_min = float(det_cfg.get("depth_min_m", 0.1))
    depth_max = float(det_cfg.get("depth_max_m", 5.0))
    room_id = cfg.get("default_room_id", "workstation_A")
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]

    # ── Load detection model ──────────────────────────────────────────────────
    dino_model = dino_processor = None
    yolo_model = None

    if obs_source == "grounding_dino":
        model_id = cfg.get("grounding_dino_model", "IDEA-Research/grounding-dino-base")
        detection_prompt = cfg.get("detection_prompt", "object.")
        box_threshold = float(dino_cfg.get("box_threshold", 0.30))
        text_threshold = float(dino_cfg.get("text_threshold", 0.25))
        console.print(f"Loading Grounding DINO: [bold]{model_id}[/bold]")
        console.print(f"  Detection prompt: [italic]{detection_prompt}[/italic]")
        console.print(f"  Thresholds: box={box_threshold}, text={text_threshold}")
        try:
            from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
            import torch
            dino_processor = AutoProcessor.from_pretrained(model_id)
            dino_model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dino_model = dino_model.to(device)
            dino_model.eval()
            console.print(f"[green]✓ Grounding DINO ready on {device}[/green]")
        except ImportError:
            console.print("[red]transformers not installed. Run: pip install transformers[/red]")
            raise typer.Exit(1)

    elif obs_source == "yolo":
        yolo_model_name = cfg.get("yolo_model")
        if not yolo_model_name:
            console.print("[red]observations_source=yolo but yolo_model not set in pipeline.yaml.[/red]")
            raise typer.Exit(1)
        try:
            from ultralytics import YOLO
            yolo_model = YOLO(yolo_model_name)
            console.print(f"[green]✓ YOLO model loaded: {yolo_model_name}[/green]")
        except ImportError:
            console.print("[red]ultralytics not installed. Run: pip install ultralytics[/red]")
            raise typer.Exit(1)

    elif obs_source == "depth_blobs":
        min_blob_px = int(det_cfg.get("min_blob_pixels", 200))
        max_blobs = int(det_cfg.get("max_blobs_per_frame", 20))
        console.print("[yellow]Using depth_blobs backend (no semantic labels).[/yellow]")

    else:
        console.print(f"[red]Unknown observations_source: {obs_source}[/red]")
        raise typer.Exit(1)

    # ── Process frames ────────────────────────────────────────────────────────
    all_obs = []
    frames_with_depth = df_manifest[df_manifest["depth_encoding"] != "none"]
    console.print(f"Frames with depth: {len(frames_with_depth)} / {len(df_manifest)}")
    console.print(f"Detection backend: [bold]{obs_source}[/bold]")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
                  TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("Processing frames...", total=len(df_manifest))

        for _, row in df_manifest.iterrows():
            fidx = int(row["frame_idx"])
            ts_ns = int(row["timestamp_ns"])
            fx, fy = float(row["fx"]), float(row["fy"])
            cx, cy = float(row["cx"]), float(row["cy"])
            w, h = int(row["width"]), int(row["height"])

            # Load RGB
            rgb = None
            rp = _resolve(row["rgb_path"])
            if rp.exists():
                try:
                    rgba = load_rgba(rp, width=w, height=h)
                    rgb = rgba_to_rgb(rgba)
                except Exception:
                    pass

            # Load depth
            depth = None
            if row["depth_encoding"] not in ("none", "") and pd.notna(row["depth_path"]) and row["depth_path"]:
                dp = _resolve(row["depth_path"])
                depth = load_depth_npy(dp, width=w, height=h)

            T_world_cam = flat_to_matrix([row[c] for c in pose_cols])

            frame_obs = []

            if obs_source == "grounding_dino":
                if rgb is None:
                    progress.advance(task)
                    continue
                frame_obs = _detect_grounding_dino(
                    rgb, depth, fidx, ts_ns, fx, fy, cx, cy,
                    T_world_cam, dino_model, dino_processor,
                    room_id, depth_min, depth_max,
                    detection_prompt, box_threshold, text_threshold,
                )

            elif obs_source == "yolo":
                if rgb is None:
                    progress.advance(task)
                    continue
                frame_obs = _detect_yolo(
                    rgb, depth, fidx, ts_ns, fx, fy, cx, cy,
                    T_world_cam, yolo_model, room_id, depth_min, depth_max,
                )

            elif obs_source == "depth_blobs" and depth is not None:
                dh, dw = depth.shape
                rgb_h, rgb_w = (rgb.shape[:2] if rgb is not None else (h, w))
                d_fx = fx * dw / rgb_w
                d_fy = fy * dh / rgb_h
                d_cx = cx * dw / rgb_w
                d_cy = cy * dh / rgb_h
                frame_obs = _detect_depth_blobs(
                    rgb, depth, fidx, ts_ns, d_fx, d_fy, d_cx, d_cy,
                    T_world_cam, room_id, depth_min, depth_max,
                    min_blob_px, max_blobs,
                )

            all_obs.extend(frame_obs)

            # Save detection overlay for every frame that has detections
            if save_debug and rgb is not None and frame_obs:
                out_dbg = paths.debug_box_dir / f"frame_{fidx:06d}_detections.png"
                draw_detections_on_rgb(rgb, frame_obs, out_dbg)

            progress.advance(task)

    if not all_obs:
        console.print("[yellow]WARN: No observations generated.[/yellow]")
        console.print("  If using grounding_dino, check that your detection_prompt covers objects in the scene.")
        pd.DataFrame(columns=OBSERVATION_COLUMNS).to_csv(paths.object_observations, index=False)
        return

    clean_obs = [{k: v for k, v in o.items() if not k.startswith("_")} for o in all_obs]
    obs_df = pd.DataFrame(clean_obs)
    for col in OBSERVATION_COLUMNS:
        if col not in obs_df.columns:
            obs_df[col] = None
    obs_df = obs_df[OBSERVATION_COLUMNS]

    obs_df.to_csv(paths.object_observations, index=False)
    console.print(f"[green]✓ Wrote {len(obs_df)} observations → {paths.object_observations}[/green]")
    console.print(f"  Unique frames: {obs_df['frame_idx'].nunique()}")
    console.print(f"  Classes: {obs_df['semantic_class'].value_counts().to_dict()}")


# ── Detection backends ────────────────────────────────────────────────────────

def _detect_grounding_dino(
    rgb, depth, fidx, ts_ns, fx, fy, cx, cy,
    T_world_cam, model, processor, room_id,
    depth_min, depth_max, detection_prompt,
    box_threshold, text_threshold,
):
    """Open-vocabulary detection via Grounding DINO + depth back-projection."""
    import torch
    from PIL import Image

    pil_image = Image.fromarray(rgb)
    rgb_h, rgb_w = rgb.shape[:2]

    inputs = processor(images=pil_image, text=detection_prompt, return_tensors="pt")
    inputs = {k: v.to(next(model.parameters()).device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    results = processor.post_process_grounded_object_detection(
        outputs,
        input_ids=inputs["input_ids"],
        threshold=box_threshold,
        text_threshold=text_threshold,
        target_sizes=[(rgb_h, rgb_w)],
    )

    obs_list = []
    if not results:
        return obs_list

    result = results[0]
    boxes = result["boxes"].tolist()           # absolute pixel coords in RGB space
    labels = result.get("text_labels", result.get("labels", []))  # text label per box
    scores = result["scores"].tolist()

    # Scale factors: RGB → depth coordinate space
    if depth is not None:
        dh, dw = depth.shape
    else:
        dh, dw = rgb_h, rgb_w

    scale_x = dw / rgb_w
    scale_y = dh / rgb_h
    d_fx = fx * scale_x
    d_fy = fy * scale_y
    d_cx = cx * scale_x
    d_cy = cy * scale_y

    for box, label, score in zip(boxes, labels, scores):
        x1, y1, x2, y2 = box
        sem_class = label.strip().rstrip(".").strip()

        # Center in RGB space
        u_c = (x1 + x2) / 2.0
        v_c = (y1 + y2) / 2.0

        if depth is None:
            continue

        # Scale center to depth space for depth sampling
        du_c = u_c * scale_x
        dv_c = v_c * scale_y
        du_i = int(np.clip(du_c, 0, dw - 1))
        dv_i = int(np.clip(dv_c, 0, dh - 1))

        d_val = float(depth[dv_i, du_i])
        if not (depth_min < d_val < depth_max):
            # Fallback: median of scaled bbox region
            dx1 = int(np.clip(x1 * scale_x, 0, dw))
            dy1 = int(np.clip(y1 * scale_y, 0, dh))
            dx2 = int(np.clip(x2 * scale_x, 0, dw))
            dy2 = int(np.clip(y2 * scale_y, 0, dh))
            roi = depth[dy1:dy2, dx1:dx2]
            valid = roi[(roi > depth_min) & (roi < depth_max)]
            if valid.size == 0:
                continue
            d_val = float(np.median(valid))

        # Back-project using depth-space intrinsics and depth-space center
        center = deproject_pixel_to_world(du_c, dv_c, d_val, d_fx, d_fy, d_cx, d_cy, T_world_cam)

        obs = make_observation(
            frame_idx=fidx, timestamp_ns=ts_ns,
            semantic_class=sem_class,
            x=float(center[0]), y=float(center[1]), z=float(center[2]),
            confidence=float(score), room_id=room_id, source="grounding_dino",
        )
        obs["_u_min"] = int(x1); obs["_u_max"] = int(x2)
        obs["_v_min"] = int(y1); obs["_v_max"] = int(y2)
        obs_list.append(obs)

    return obs_list


def _detect_yolo(
    rgb, depth, fidx, ts_ns, fx, fy, cx, cy,
    T_world_cam, yolo_model, room_id, depth_min, depth_max,
):
    """Detect objects with YOLO and back-project using depth."""
    results = yolo_model(rgb, verbose=False)
    obs_list = []

    if depth is not None:
        dh, dw = depth.shape
    else:
        dh, dw = rgb.shape[:2]

    rgb_h, rgb_w = rgb.shape[:2]
    scale_x = dw / rgb_w
    scale_y = dh / rgb_h
    d_fx = fx * scale_x
    d_fy = fy * scale_y
    d_cx = cx * scale_x
    d_cy = cy * scale_y

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            sem_class = yolo_model.names.get(cls_id, f"class_{cls_id}")

            u_c = (x1 + x2) / 2.0
            v_c = (y1 + y2) / 2.0

            if depth is None:
                continue

            du_c = u_c * scale_x
            dv_c = v_c * scale_y
            du_i = int(np.clip(du_c, 0, dw - 1))
            dv_i = int(np.clip(dv_c, 0, dh - 1))

            d_val = float(depth[dv_i, du_i])
            if not (depth_min < d_val < depth_max):
                dx1 = int(np.clip(x1 * scale_x, 0, dw))
                dy1 = int(np.clip(y1 * scale_y, 0, dh))
                dx2 = int(np.clip(x2 * scale_x, 0, dw))
                dy2 = int(np.clip(y2 * scale_y, 0, dh))
                roi = depth[dy1:dy2, dx1:dx2]
                valid = roi[(roi > depth_min) & (roi < depth_max)]
                if valid.size == 0:
                    continue
                d_val = float(np.median(valid))

            center = deproject_pixel_to_world(du_c, dv_c, d_val, d_fx, d_fy, d_cx, d_cy, T_world_cam)

            obs = make_observation(
                frame_idx=fidx, timestamp_ns=ts_ns,
                semantic_class=sem_class,
                x=float(center[0]), y=float(center[1]), z=float(center[2]),
                confidence=conf, room_id=room_id, source="yolo",
            )
            obs["_u_min"] = int(x1); obs["_u_max"] = int(x2)
            obs["_v_min"] = int(y1); obs["_v_max"] = int(y2)
            obs_list.append(obs)

    return obs_list


def _detect_depth_blobs(
    rgb, depth, fidx, ts_ns, fx, fy, cx, cy,
    T_world_cam, room_id, depth_min, depth_max, min_blob_px, max_blobs,
):
    """Extract observations using depth blob segmentation (no semantic labels)."""
    blobs = extract_depth_blobs(
        depth, depth_min=depth_min, depth_max=depth_max,
        min_blob_pixels=min_blob_px, max_blobs=max_blobs,
    )
    obs_list = []
    for i, blob in enumerate(blobs):
        try:
            center, extent = blob_to_world_box(blob, fx, fy, cx, cy, T_world_cam)
        except Exception:
            continue

        sem_class = classify_blob(blob, i)
        conf = min(0.9, 0.3 + blob["area_px"] / 50000)

        obs = make_observation(
            frame_idx=fidx, timestamp_ns=ts_ns,
            semantic_class=sem_class,
            x=float(center[0]), y=float(center[1]), z=float(center[2]),
            w=float(extent[0]), h=float(extent[1]), d=float(extent[2]),
            confidence=conf, room_id=room_id, source="depth_blobs",
        )
        obs["_u_min"] = blob["u_min"]; obs["_u_max"] = blob["u_max"]
        obs["_v_min"] = blob["v_min"]; obs["_v_max"] = blob["v_max"]
        obs_list.append(obs)
    return obs_list


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return PROJECT_ROOT.parent / p


if __name__ == "__main__":
    app()
