"""Pose utilities for Quest 3 metadata → 4x4 matrices."""
from __future__ import annotations
import numpy as np
from typing import Dict
from .geometry import pose_to_matrix, matrix_to_flat


def meta_to_pose_flat(meta: Dict) -> list[float]:
    """Extract pose from Quest 3 meta dict and return as flat 16-element list."""
    pose = meta.get("pose", {})
    position = pose.get("position", [0.0, 0.0, 0.0])
    rot_xyzw = pose.get("rotation_xyzw", [0.0, 0.0, 0.0, 1.0])
    T = pose_to_matrix(position, rot_xyzw)
    return matrix_to_flat(T)


def is_valid_pose(flat: list[float]) -> bool:
    """Check that a flat 16-element pose is a valid 4x4 matrix."""
    if len(flat) != 16:
        return False
    T = np.array(flat).reshape(4, 4)
    # Bottom row must be [0, 0, 0, 1]
    if not np.allclose(T[3], [0, 0, 0, 1], atol=1e-3):
        return False
    # Rotation block must be approximately orthonormal
    R = T[:3, :3]
    I_approx = R @ R.T
    if not np.allclose(I_approx, np.eye(3), atol=0.05):
        return False
    return True


def poses_are_plausible(pose_list: list[list[float]], max_jump_m: float = 5.0) -> bool:
    """Check that consecutive poses do not jump unrealistically far."""
    for i in range(1, len(pose_list)):
        t1 = np.array(pose_list[i - 1]).reshape(4, 4)[:3, 3]
        t2 = np.array(pose_list[i]).reshape(4, 4)[:3, 3]
        dist = np.linalg.norm(t2 - t1)
        if dist > max_jump_m:
            return False
    return True
