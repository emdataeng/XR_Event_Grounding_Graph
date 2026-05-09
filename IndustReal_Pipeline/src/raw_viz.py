"""Visualization helpers for raw IndustReal pilot clips."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw


def _load_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def _maybe_overlay_gaze(draw: ImageDraw.ImageDraw, gaze_xy: tuple[int, int] | None) -> None:
    if not gaze_xy:
        return
    x, y = gaze_xy
    radius = 10
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="yellow", width=3)


def _maybe_overlay_bbox(draw: ImageDraw.ImageDraw, bbox_xyxy: Iterable[float] | None, label: str | None = None) -> None:
    if not bbox_xyxy:
        return
    x1, y1, x2, y2 = [float(v) for v in bbox_xyxy]
    draw.rectangle((x1, y1, x2, y2), outline="lime", width=3)
    if label:
        draw.text((x1 + 4, y1 + 4), label, fill="lime")


def save_rgb_depth_preview(
    rgb_path: Path,
    depth_path: Path,
    out_path: Path,
    *,
    bbox_xyxy: Optional[Iterable[float]] = None,
    bbox_label: Optional[str] = None,
    gaze_xy: Optional[tuple[int, int]] = None,
    title: Optional[str] = None,
) -> None:
    rgb = _load_image(rgb_path)
    rgb_draw = ImageDraw.Draw(rgb)
    _maybe_overlay_bbox(rgb_draw, bbox_xyxy, bbox_label)
    _maybe_overlay_gaze(rgb_draw, gaze_xy)

    depth = _load_image(depth_path)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(np.asarray(rgb))
    axes[0].axis("off")
    axes[0].set_title("RGB")
    axes[1].imshow(np.asarray(depth))
    axes[1].axis("off")
    axes[1].set_title("Depth JPG")
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_stereo_preview(left_path: Path, right_path: Path, out_path: Path, *, title: Optional[str] = None) -> None:
    left = Image.open(left_path)
    right = Image.open(right_path)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(np.asarray(left), cmap="gray")
    axes[0].axis("off")
    axes[0].set_title("Stereo left")
    axes[1].imshow(np.asarray(right), cmap="gray")
    axes[1].axis("off")
    axes[1].set_title("Stereo right")
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_od_overlay(
    rgb_path: Path,
    out_path: Path,
    *,
    bbox_xyxy: Optional[Iterable[float]] = None,
    state_name: Optional[str] = None,
    gaze_xy: Optional[tuple[int, int]] = None,
) -> None:
    image = _load_image(rgb_path)
    draw = ImageDraw.Draw(image)
    _maybe_overlay_bbox(draw, bbox_xyxy, state_name)
    _maybe_overlay_gaze(draw, gaze_xy)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)


def save_pose_trajectory(translations: np.ndarray | list[tuple[float, float, float]], out_path: Path, *, title: Optional[str] = None) -> None:
    translations = np.asarray(translations, dtype=np.float64)
    if translations.size == 0:
        return
    if translations.ndim != 2 or translations.shape[1] < 3:
        raise ValueError("translations must be shaped like (n, 3)")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(translations[:, 0], translations[:, 2], color="tab:blue", linewidth=2)
    ax.scatter(translations[0, 0], translations[0, 2], color="green", label="start")
    ax.scatter(translations[-1, 0], translations[-1, 2], color="red", label="end")
    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    ax.set_title(title or "Camera trajectory")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
