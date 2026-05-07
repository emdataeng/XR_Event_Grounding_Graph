"""Pose helpers for IndustReal HoloLens 2 pose.csv rows."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import numpy as np


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm < 1e-8:
        raise ValueError("zero-length direction vector")
    return vec / norm


def vectors_to_pose_matrix(
    forward_xyz: Iterable[float],
    position_xyz: Iterable[float],
    up_xyz: Iterable[float],
) -> np.ndarray:
    """Convert forward/position/up vectors into a 4x4 camera pose matrix."""
    forward = _normalize(np.asarray(list(forward_xyz), dtype=np.float64))
    up = _normalize(np.asarray(list(up_xyz), dtype=np.float64))
    right = _normalize(np.cross(up, forward))
    up_ortho = _normalize(np.cross(forward, right))

    pose = np.eye(4, dtype=np.float64)
    pose[:3, :3] = np.stack([right, up_ortho, forward], axis=1)
    pose[:3, 3] = np.asarray(list(position_xyz), dtype=np.float64)
    return pose


def matrix_to_flat(pose: np.ndarray) -> list[float]:
    return pose.reshape(-1).astype(float).tolist()


def csv_row_to_pose_flat(row: list[str]) -> list[float]:
    if len(row) != 10:
        raise ValueError(f"expected 10 pose.csv columns, got {len(row)}")
    values = [float(v) for v in row[1:]]
    pose = vectors_to_pose_matrix(values[:3], values[3:6], values[6:9])
    return matrix_to_flat(pose)


def load_pose_csv(path: Path) -> dict[str, list[float]]:
    poses: dict[str, list[float]] = {}
    pending_invalid: list[str] = []
    last_valid_pose: list[float] | None = None
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            frame_name = row[0]
            try:
                pose_flat = csv_row_to_pose_flat(row)
            except ValueError as exc:
                # Some real clips contain short runs of all-zero pose vectors.
                # Reuse the nearest valid pose so a few bad rows do not kill the
                # whole clip-level batch run.
                if "zero-length direction vector" not in str(exc):
                    raise
                if last_valid_pose is None:
                    pending_invalid.append(frame_name)
                    continue
                poses[frame_name] = list(last_valid_pose)
                continue

            if pending_invalid:
                for pending_frame_name in pending_invalid:
                    poses[pending_frame_name] = list(pose_flat)
                pending_invalid.clear()

            poses[frame_name] = pose_flat
            last_valid_pose = pose_flat

    if pending_invalid and last_valid_pose is not None:
        for pending_frame_name in pending_invalid:
            poses[pending_frame_name] = list(last_valid_pose)
    return poses


def is_valid_pose_flat(flat: list[float]) -> bool:
    if len(flat) != 16:
        return False
    pose = np.asarray(flat, dtype=np.float64).reshape(4, 4)
    if not np.allclose(pose[3], [0.0, 0.0, 0.0, 1.0], atol=1e-5):
        return False
    rotation = pose[:3, :3]
    return np.allclose(rotation @ rotation.T, np.eye(3), atol=1e-4)
