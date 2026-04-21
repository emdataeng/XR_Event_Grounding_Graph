"""Visualization utilities: RGB-D overlays, depth colormaps, point cloud snapshots."""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List
import numpy as np


def save_rgb_depth_overlay(
    rgb: np.ndarray,
    depth: Optional[np.ndarray],
    out_path: Path,
    title: str = "",
    depth_max: float = 3.0,
):
    """Save a side-by-side RGB / depth image to disk."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2 if depth is not None else 1, figsize=(10, 4))
    if depth is None:
        axes = [axes]

    axes[0].imshow(rgb)
    axes[0].set_title("RGB")
    axes[0].axis("off")

    if depth is not None:
        d_vis = np.where(np.isnan(depth), 0, np.clip(depth, 0, depth_max))
        im = axes[1].imshow(d_vis, cmap="turbo", vmin=0, vmax=depth_max)
        axes[1].set_title("Depth (m)")
        axes[1].axis("off")
        plt.colorbar(im, ax=axes[1], fraction=0.046)

    if title:
        fig.suptitle(title, fontsize=10)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=80, bbox_inches="tight")
    plt.close(fig)


def save_pose_trajectory(pose_list: list, out_path: Path, title: str = "Camera trajectory"):
    """Save a 2D top-down view of camera positions."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = [p[3] for p in pose_list]    # T[:3,3] = translation x
    zs = [p[11] for p in pose_list]   # index 11 = T[2,3] = z

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(xs, zs, "b.-", linewidth=0.8, markersize=4)
    ax.plot(xs[0], zs[0], "go", markersize=8, label="start")
    ax.plot(xs[-1], zs[-1], "rs", markersize=8, label="end")
    ax.set_xlabel("X (m)"); ax.set_ylabel("Z (m)")
    ax.set_title(title); ax.legend(); ax.set_aspect("equal")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=80, bbox_inches="tight")
    plt.close(fig)


def draw_detections_on_rgb(rgb: np.ndarray, detections: list, out_path: Path):
    """Draw detection bounding boxes with class labels and confidence scores.

    Accepts observation dicts from script 05.  Bbox is read from:
      1. V2 fields bbox_x1/y1/x2/y2  (new schema)
      2. Private keys _u_min/_v_min/_u_max/_v_max  (legacy / fallback)
    Falls back to a small placeholder box at (0,0,10,10) if neither is present.

    Label shown is raw label (field: label) with canonical in parentheses when
    different, e.g. "red lego blue lego (red_lego)".
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Colour by semantic_class (the tracking class, stable across frames)
    all_classes = sorted({d.get("semantic_class", "?") for d in detections})
    palette = plt.cm.tab10.colors
    class_color = {cls: palette[i % len(palette)] for i, cls in enumerate(all_classes)}

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(rgb)

    for d in detections:
        # Prefer V2 bbox fields; fall back to legacy private keys
        if d.get("bbox_x1") is not None:
            x1 = float(d["bbox_x1"])
            y1 = float(d["bbox_y1"])
            x2 = float(d["bbox_x2"])
            y2 = float(d["bbox_y2"])
        else:
            x1 = float(d.get("_u_min", 0))
            y1 = float(d.get("_v_min", 0))
            x2 = float(d.get("_u_max", 10))
            y2 = float(d.get("_v_max", 10))

        sem_class = d.get("semantic_class", "?")
        raw_label = d.get("label", sem_class)
        conf = d.get("confidence", 0.0)
        color = class_color.get(sem_class, "white")

        # Show raw label; append canonical in parens when it differs
        if raw_label != sem_class:
            display_label = f"{raw_label} ({sem_class})"
        else:
            display_label = sem_class
        label = display_label

        rect = patches.Rectangle(
            (x1, y1), x2 - x1, y2 - y1,
            linewidth=2, edgecolor=color, facecolor="none",
        )
        ax.add_patch(rect)

        # Label background for readability
        ax.text(
            x1 + 2, y1 + 12,
            f"{label}  {conf:.2f}",
            fontsize=7, color="white",
            bbox=dict(boxstyle="square,pad=0.15", fc=color, ec="none", alpha=0.75),
        )

    ax.axis("off")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=90, bbox_inches="tight")
    plt.close(fig)


def draw_blobs_on_rgb(rgb: np.ndarray, blobs: list, out_path: Path):
    """Draw blob bounding boxes on an RGB image and save."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(rgb)
    colors = plt.cm.tab10.colors
    for i, b in enumerate(blobs):
        c = colors[i % len(colors)]
        rect = patches.Rectangle(
            (b["u_min"], b["v_min"]),
            b["u_max"] - b["u_min"],
            b["v_max"] - b["v_min"],
            linewidth=1.5, edgecolor=c, facecolor="none",
        )
        ax.add_patch(rect)
        ax.text(b["u_min"], b["v_min"] - 2,
                f"d={b['depth_mean']:.2f}m",
                fontsize=7, color=c)
    ax.axis("off")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=80, bbox_inches="tight")
    plt.close(fig)


def save_point_cloud_screenshot(
    points: np.ndarray,
    out_path: Path,
    colors: Optional[np.ndarray] = None,
    title: str = "Point cloud",
):
    """Save a matplotlib 3D scatter of a point cloud (no Open3D needed)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    if len(points) == 0:
        return

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    stride = max(1, len(points) // 5000)  # downsample for speed
    pts = points[::stride]
    c = colors[::stride] / 255.0 if colors is not None else "steelblue"
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=c, s=0.5, alpha=0.5)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title(title)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=80, bbox_inches="tight")
    plt.close(fig)
