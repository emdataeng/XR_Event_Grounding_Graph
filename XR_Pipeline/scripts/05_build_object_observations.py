#!/usr/bin/env python3
"""05_build_object_observations.py — Derive object observations from RGB-D frames.

Detection backends (set via configs/pipeline.yaml → observations_source):
  grounding_dino  — open-vocabulary detection with text prompts (requires transformers)
  yolo            — YOLOv8 fixed-class detection (requires ultralytics)
  depth_blobs     — depth segmentation, no semantic labels (no extra dependencies)

Architecture:
  Each backend is a thin DetectionResult producer that returns pixel-space
  bounding boxes only (src/detectors/). Depth back-projection to 3D world
  coordinates happens here, after detection.

Canonicalization, confidence filtering, and class-aware NMS are applied in
src/detection_postprocess.py before observations are written to CSV.
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
from src.geometry import flat_to_matrix, deproject_pixel_to_world
from src.objects import (
    make_observation, OBSERVATION_COLUMNS,
    compute_depth_stats,
)
from src.detectors.base import load_detector, DetectionResult
from src.detection_postprocess import postprocess_detections
from src.vocabulary import Vocabulary
from src.detection_groups import parse_detection_groups, cross_pass_nms
from src.run_metadata import build_run_metadata, save_run_metadata, check_staleness, emit_staleness_warnings
from src.viz import draw_detections_on_rgb

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    max_frames: int = typer.Option(0, help="Limit to first N frames (0 = all)"),
    save_debug: bool = typer.Option(True, help="Save detection overlay images"),
    force: bool = typer.Option(False, help="Continue even if upstream outputs are stale"),
):
    """Build object_observations.csv from RGB-D frames."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    if not paths.frame_manifest.exists():
        console.print("[red]frame_manifest.csv not found. Run 01 first.[/red]")
        raise typer.Exit(1)

    # ── Staleness check ───────────────────────────────────────────────────────
    warnings = check_staleness(
        paths.processed_root, "01_build_frame_manifest", cfg, thr,
    )
    if not emit_staleness_warnings(warnings, console=console, force=force):
        raise typer.Exit(1)

    # ── Load config ───────────────────────────────────────────────────────────
    df_manifest = pd.read_csv(paths.frame_manifest)
    if max_frames > 0:
        df_manifest = df_manifest.head(max_frames)

    obs_source = cfg.get("observations_source", "grounding_dino")
    flip_vertical = cfg.get("camera", {}).get("flip_vertical", True)
    det_cfg = thr.get("detection", {})
    depth_min = float(det_cfg.get("depth_min_m", 0.1))
    depth_max = float(det_cfg.get("depth_max_m", 5.0))
    room_id = cfg.get("default_room_id", "workstation_A")
    pose_cols = [f"T_world_cam_{i:02d}" for i in range(16)]

    # ── Vocabulary + postprocess config ──────────────────────────────────────
    # Vocabulary is built first so its prompt can be passed to the detector.
    vocab = Vocabulary.from_config(cfg)
    conf_min = float(thr.get("confidence", {}).get("min_observation", 0.3))
    min_area_px = float(det_cfg.get("min_bbox_area_px", 0))
    nms_iou_thr = float(det_cfg.get("nms_iou_threshold", 0.5))

    # Resolve detection prompt: use vocabulary prompt when vocab is configured,
    # fall back to detection_prompt in pipeline.yaml.
    _OPEN_VOCAB_BACKENDS = {"grounding_dino", "mm_grounding_dino"}
    if obs_source in _OPEN_VOCAB_BACKENDS and not vocab.is_empty:
        resolved_prompt = vocab.build_prompt()
        console.print(f"[dim]  Prompt from object_vocabulary: {resolved_prompt!r}[/dim]")
    else:
        resolved_prompt = cfg.get("detection_prompt", "object.")

    # Vocabulary rejection only applies to open-vocabulary detectors.
    apply_vocab = obs_source in _OPEN_VOCAB_BACKENDS

    # ── Multi-pass group config ───────────────────────────────────────────────
    # parse_detection_groups returns [] when detection_groups absent → single-pass
    group_passes = parse_detection_groups(cfg, vocab) if apply_vocab else []
    if group_passes:
        console.print(
            f"[cyan]Multi-pass detection: {len(group_passes)} group(s) — "
            + ", ".join(f"{gp.group.name}({len(gp.group.classes)} cls)" for gp in group_passes)
            + "[/cyan]"
        )
    else:
        console.print("[dim]  Single-pass detection (no detection_groups configured)[/dim]")

    # ── Load detector ─────────────────────────────────────────────────────────
    console.print(f"Loading detector backend: [bold]{obs_source}[/bold]")
    try:
        detector = load_detector(obs_source, cfg, thr, prompt=resolved_prompt)
    except (ImportError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    effective_thresholds = _build_effective_threshold_metadata(
        detector=detector,
        group_passes=group_passes,
        min_observation=conf_min,
    )

    # Trigger model loading now (before the progress bar) so load time is visible
    if obs_source in ("grounding_dino", "yolo"):
        try:
            detector._load()
            console.print(f"[green]✓ Detector ready ({detector.model_id})[/green]")
        except ImportError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[green]✓ Detector ready ({detector.model_id})[/green]")

    # ── Process frames ────────────────────────────────────────────────────────
    all_obs = []
    frames_with_depth = df_manifest[df_manifest["depth_encoding"] != "none"]
    console.print(f"Frames with depth: {len(frames_with_depth)} / {len(df_manifest)}")
    console.print(f"Prompt: [italic]{getattr(detector, 'prompt', '—')}[/italic]")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
                  TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("Processing frames...", total=len(df_manifest))

        for _, row in df_manifest.iterrows():
            fidx = int(row["frame_idx"])
            ts_ns = int(row["timestamp_ns"])
            fx, fy = float(row["fx"]), float(row["fy"])
            cx, cy = float(row["cx"]), float(row["cy"])
            w, h = int(row["width"]), int(row["height"])

            # ── Load RGB ──────────────────────────────────────────────────────
            rgb = None
            rp = _resolve(row["rgb_path"])
            if rp.exists():
                try:
                    rgba = load_rgba(rp, width=w, height=h,
                                     stereo_eye=cfg.get("stereo_eye"),
                                     flip_vertical=flip_vertical)
                    rgb = rgba_to_rgb(rgba)
                except Exception:
                    pass

            # ── Load depth ────────────────────────────────────────────────────
            depth = None
            if row["depth_encoding"] not in ("none", "") and pd.notna(row["depth_path"]) and row["depth_path"]:
                dp = _resolve(row["depth_path"])
                depth = load_depth_npy(dp, width=w, height=h, flip_vertical=flip_vertical)

            T_world_cam = flat_to_matrix([row[c] for c in pose_cols])

            # Depth ↔ RGB scale factors (depth may be taller than RGB)
            if depth is not None:
                dh, dw = depth.shape
                rgb_h, rgb_w = (rgb.shape[:2] if rgb is not None else (h, w))
            else:
                dh, dw = (h, w)
                rgb_h, rgb_w = (rgb.shape[:2] if rgb is not None else (h, w))

            scale_x = dw / rgb_w
            scale_y = dh / rgb_h
            d_fx = fx * scale_x
            d_fy = fy * scale_y
            d_cx = cx * scale_x
            d_cy = cy * scale_y

            # Frame context for depth_blobs (intrinsics in depth space)
            frame_context = {
                "fx": d_fx, "fy": d_fy, "cx": d_cx, "cy": d_cy,
                "T_world_cam": T_world_cam,
                "rgb_h": rgb_h, "rgb_w": rgb_w,
                "depth_min_m": depth_min, "depth_max_m": depth_max,
            }

            # ── Detect ────────────────────────────────────────────────────────
            if rgb is None and obs_source != "depth_blobs":
                progress.advance(task)
                continue

            if group_passes:
                # ── Multi-pass: one detector call per group ───────────────────
                # The detector model is loaded once; we swap the prompt (and
                # optionally box/text thresholds) between passes.
                _original_prompt = detector.prompt
                _original_box_thr = getattr(detector, "box_threshold", None)
                _original_text_thr = getattr(detector, "text_threshold", None)
                frame_obs_all = []
                for gp in group_passes:
                    detector.prompt = gp.prompt
                    if gp.box_threshold is not None and hasattr(detector, "box_threshold"):
                        detector.box_threshold = gp.box_threshold
                    if gp.text_threshold is not None and hasattr(detector, "text_threshold"):
                        detector.text_threshold = gp.text_threshold
                    raw_g: list[DetectionResult] = detector.detect(
                        rgb=rgb, depth=depth, frame_context=frame_context,
                    )
                    dets_g = postprocess_detections(
                        raw_g,
                        vocab=gp.vocab,
                        conf_min=conf_min,
                        min_area_px=min_area_px,
                        nms_iou_threshold=nms_iou_thr,
                        apply_vocab=True,
                    )
                    for det in dets_g:
                        obs = _detection_to_observation(
                            det, depth,
                            fidx, ts_ns,
                            fx, fy, cx, cy,
                            d_fx, d_fy, d_cx, d_cy,
                            scale_x, scale_y,
                            T_world_cam, room_id,
                            depth_min, depth_max,
                            detector_group=gp.group.name,
                            detector_pass_id=gp.group.pass_id,
                        )
                        if obs is not None:
                            frame_obs_all.append(obs)
                detector.prompt = _original_prompt
                if _original_box_thr is not None and hasattr(detector, "box_threshold"):
                    detector.box_threshold = _original_box_thr
                if _original_text_thr is not None and hasattr(detector, "text_threshold"):
                    detector.text_threshold = _original_text_thr
                # Cross-pass NMS: remove duplicates from overlapping groups
                frame_obs = cross_pass_nms(frame_obs_all, iou_threshold=nms_iou_thr)

            else:
                # ── Single-pass (backward-compatible) ────────────────────────
                raw_detections: list[DetectionResult] = detector.detect(
                    rgb=rgb, depth=depth, frame_context=frame_context,
                )
                detections = postprocess_detections(
                    raw_detections,
                    vocab=vocab,
                    conf_min=conf_min,
                    min_area_px=min_area_px,
                    nms_iou_threshold=nms_iou_thr,
                    apply_vocab=apply_vocab,
                )
                frame_obs = []
                for det in detections:
                    obs = _detection_to_observation(
                        det, depth,
                        fidx, ts_ns,
                        fx, fy, cx, cy,
                        d_fx, d_fy, d_cx, d_cy,
                        scale_x, scale_y,
                        T_world_cam, room_id,
                        depth_min, depth_max,
                    )
                    if obs is not None:
                        frame_obs.append(obs)

            all_obs.extend(frame_obs)

            # Debug overlay
            if save_debug and rgb is not None and frame_obs:
                out_dbg = paths.debug_box_dir / f"frame_{fidx:06d}_detections.png"
                draw_detections_on_rgb(rgb, frame_obs, out_dbg)

            progress.advance(task)

    # Build group_prompts dict for metadata (populated only in multi-pass mode)
    _group_prompts = {gp.group.name: gp.prompt for gp in group_passes} if group_passes else {}
    _actual_prompt = group_passes[0].prompt if len(group_passes) == 1 else resolved_prompt

    if not all_obs:
        console.print("[yellow]WARN: No observations generated.[/yellow]")
        console.print("  Check detection_prompt and thresholds in pipeline.yaml / thresholds.yaml.")
        pd.DataFrame(columns=OBSERVATION_COLUMNS).to_csv(paths.object_observations, index=False)
        _write_run_metadata(session, cfg, thr, paths, n_observations=0,
                            resolved_prompt=_actual_prompt, group_prompts=_group_prompts,
                            effective_thresholds=effective_thresholds)
        return

    # Strip private keys (prefixed _) used internally during processing
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
    if "canonical_class" in obs_df.columns:
        console.print(f"  Canonical classes: {obs_df['canonical_class'].value_counts().to_dict()}")

    _write_run_metadata(session, cfg, thr, paths, n_observations=len(obs_df),
                        resolved_prompt=_actual_prompt, group_prompts=_group_prompts,
                        effective_thresholds=effective_thresholds)


# ── Depth backprojection ──────────────────────────────────────────────────────

def _detection_to_observation(
    det: DetectionResult,
    depth,
    fidx, ts_ns,
    fx, fy, cx, cy,
    d_fx, d_fy, d_cx, d_cy,
    scale_x, scale_y,
    T_world_cam, room_id,
    depth_min, depth_max,
    detector_group: "str | None" = None,
    detector_pass_id: "str | None" = None,
):
    """Convert a DetectionResult to an observation dict with 3D coordinates.

    For depth_blobs, uses pre-computed 3D from metadata if available.
    For RGB detectors, samples depth from the bbox ROI and back-projects.
    Returns None if no valid depth can be found.
    """
    x1, y1, x2, y2 = det.bbox_xyxy
    # semantic_class is the stable tracking class (canonical when vocab mapped,
    # raw label when permissive / no vocab).
    sem_class = det.metadata.get("canonical_class") or det.raw_label
    canonical = det.metadata.get("canonical_class")

    # ── depth_blobs: use pre-computed 3D ─────────────────────────────────────
    if det.source == "depth_blobs":
        meta = det.metadata
        xyz = meta.get("pre_computed_xyz")
        ext = meta.get("pre_computed_extent")
        if xyz is None:
            return None
        obs = make_observation(
            frame_idx=fidx, timestamp_ns=ts_ns,
            semantic_class=sem_class,
            label=det.raw_label,          # preserve raw detector output
            x=float(xyz[0]), y=float(xyz[1]), z=float(xyz[2]),
            w=float(ext[0]) if ext else 0.0,
            h=float(ext[1]) if ext else 0.0,
            d=float(ext[2]) if ext else 0.0,
            confidence=det.score,
            room_id=room_id,
            source=det.source,
            # V2
            canonical_class=canonical,
            bbox_x1=float(x1), bbox_y1=float(y1),
            bbox_x2=float(x2), bbox_y2=float(y2),
            bbox_area_px=det.bbox_area_px,
            detector_backend=det.source,
            detector_model=det.model_id,
            detector_prompt=det.prompt,
            depth_median=meta.get("blob_depth_mean"),
            depth_min=meta.get("blob_depth_min"),
            depth_max=meta.get("blob_depth_max"),
            depth_valid_px=int(meta.get("blob_area_px", 0)),
            detector_group=detector_group,
            detector_pass_id=detector_pass_id,
        )
        # Private keys for debug overlay (stripped before CSV write)
        obs["_u_min"] = int(x1); obs["_u_max"] = int(x2)
        obs["_v_min"] = int(y1); obs["_v_max"] = int(y2)
        return obs

    # ── RGB detectors: sample depth from bbox ROI ─────────────────────────────
    if depth is None:
        return None

    # Compute depth stats for the bbox (in RGB pixel space)
    depth_stats = compute_depth_stats(
        depth, x1, y1, x2, y2,
        depth_min_m=depth_min, depth_max_m=depth_max,
        scale_x=scale_x, scale_y=scale_y,
    )
    d_val = depth_stats.get("depth_for_proj")
    if d_val is None:
        return None

    # Back-project bbox centre from depth-space coordinates
    u_c = (x1 + x2) / 2.0
    v_c = (y1 + y2) / 2.0
    du_c = u_c * scale_x
    dv_c = v_c * scale_y

    center = deproject_pixel_to_world(
        du_c, dv_c, d_val, d_fx, d_fy, d_cx, d_cy, T_world_cam,
    )

    obs = make_observation(
        frame_idx=fidx, timestamp_ns=ts_ns,
        semantic_class=sem_class,
        label=det.raw_label,              # preserve raw detector output
        x=float(center[0]), y=float(center[1]), z=float(center[2]),
        confidence=det.score,
        room_id=room_id,
        source=det.source,
        # V2
        canonical_class=canonical,
        bbox_x1=float(x1), bbox_y1=float(y1),
        bbox_x2=float(x2), bbox_y2=float(y2),
        bbox_area_px=det.bbox_area_px,
        detector_backend=det.source,
        detector_model=det.model_id,
        detector_prompt=det.prompt,
        depth_median=depth_stats.get("depth_median"),
        depth_min=depth_stats.get("depth_min"),
        depth_max=depth_stats.get("depth_max"),
        depth_valid_px=depth_stats.get("depth_valid_px"),
        detector_group=detector_group,
        detector_pass_id=detector_pass_id,
    )
    # Private keys for debug overlay (stripped before CSV write)
    obs["_u_min"] = int(x1); obs["_u_max"] = int(x2)
    obs["_v_min"] = int(y1); obs["_v_max"] = int(y2)
    return obs


# ── Metadata helper ───────────────────────────────────────────────────────────

def _write_run_metadata(
    session, cfg, thr, paths, n_observations,
    resolved_prompt=None, group_prompts=None, effective_thresholds=None,
):
    from src.config import PROJECT_ROOT as _PR
    meta = build_run_metadata(
        session_id=session,
        stage="05_build_object_observations",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        pipeline_yaml_path=_PR / "configs" / "pipeline.yaml",
        thresholds_yaml_path=_PR / "configs" / "thresholds.yaml",
        extra={
            "observations_source": cfg.get("observations_source", "grounding_dino"),
            # resolved_prompt is the actual prompt sent to the detector
            # (overrides the raw detection_prompt field when vocab is configured)
            "resolved_prompt": resolved_prompt or cfg.get("detection_prompt"),
            "grounding_dino_model": cfg.get("grounding_dino_model"),
            "n_observations": n_observations,
            "multi_pass": bool(cfg.get("detection_groups")),
            "detection_groups": list(cfg.get("detection_groups", {}).keys()),
            # Per-group prompts when multi-pass is active
            "group_prompts": group_prompts or {},
            # Concrete values applied by stage 05. These complement the config
            # hashes above and make runs auditable without re-opening YAML.
            "effective_thresholds": effective_thresholds or {},
        },
    )
    path = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]  Run metadata → {path}[/dim]")


def _build_effective_threshold_metadata(detector, group_passes, min_observation):
    """Return the concrete stage-05 thresholds that will be applied."""
    default_box = getattr(detector, "box_threshold", None)
    default_text = getattr(detector, "text_threshold", None)

    group_thresholds = {}
    for gp in group_passes:
        group_thresholds[gp.group.name] = {
            "pass_id": gp.group.pass_id,
            "prompt": gp.prompt,
            "configured_box_threshold": gp.box_threshold,
            "configured_text_threshold": gp.text_threshold,
            "effective_box_threshold": gp.box_threshold if gp.box_threshold is not None else default_box,
            "effective_text_threshold": gp.text_threshold if gp.text_threshold is not None else default_text,
        }

    return {
        "confidence": {
            "min_observation": float(min_observation),
        },
        "detector_defaults": {
            "box_threshold": default_box,
            "text_threshold": default_text,
        },
        "detection_groups": group_thresholds,
    }


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return PROJECT_ROOT.parent / p


if __name__ == "__main__":
    app()
