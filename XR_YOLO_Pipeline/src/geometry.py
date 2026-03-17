"""3D geometry utilities: intrinsics, projection, bounding boxes, relations."""
from __future__ import annotations
import numpy as np
from typing import Optional, Tuple


def quaternion_to_rotation_matrix(qx: float, qy: float, qz: float, qw: float) -> np.ndarray:
    """Convert quaternion (x,y,z,w) to 3x3 rotation matrix."""
    n = qx*qx + qy*qy + qz*qz + qw*qw
    if n < 1e-10:
        return np.eye(3)
    s = 2.0 / n
    wx = s * qw * qx; wy = s * qw * qy; wz = s * qw * qz
    xx = s * qx * qx; xy = s * qx * qy; xz = s * qx * qz
    yy = s * qy * qy; yz = s * qy * qz; zz = s * qz * qz
    return np.array([
        [1 - (yy + zz),       xy - wz,          xz + wy],
        [      xy + wz,  1 - (xx + zz),          yz - wx],
        [      xz - wy,       yz + wx,      1 - (xx + yy)],
    ])


def pose_to_matrix(position: list, rotation_xyzw: list) -> np.ndarray:
    """Build 4x4 T_world_cam from position [x,y,z] and quaternion [x,y,z,w]."""
    T = np.eye(4)
    T[:3, :3] = quaternion_to_rotation_matrix(*rotation_xyzw)
    T[:3, 3] = position
    return T


def matrix_to_flat(T: np.ndarray) -> list[float]:
    """Flatten 4x4 matrix to list of 16 floats row-major."""
    return T.flatten().tolist()


def flat_to_matrix(flat: list[float]) -> np.ndarray:
    """Reconstruct 4x4 matrix from 16 row-major floats."""
    return np.array(flat, dtype=np.float64).reshape(4, 4)


def deproject_pixel_to_world(
    u: float, v: float, depth_m: float,
    fx: float, fy: float, cx: float, cy: float,
    T_world_cam: np.ndarray,
) -> np.ndarray:
    """Back-project a single pixel (u, v) with depth to world coordinates."""
    x_cam = (u - cx) * depth_m / fx
    y_cam = (v - cy) * depth_m / fy
    z_cam = depth_m
    p_cam = np.array([x_cam, y_cam, z_cam, 1.0])
    p_world = T_world_cam @ p_cam
    return p_world[:3]


def deproject_depth_image(
    depth: np.ndarray,
    fx: float, fy: float, cx: float, cy: float,
    T_world_cam: np.ndarray,
    depth_min: float = 0.1,
    depth_max: float = 5.0,
    stride: int = 1,
) -> np.ndarray:
    """Back-project valid depth pixels to world-frame point cloud.

    Returns (N, 3) array of world-frame 3D points.
    """
    H, W = depth.shape
    rows, cols = np.meshgrid(
        np.arange(0, H, stride), np.arange(0, W, stride), indexing="ij"
    )
    d = depth[rows, cols]
    mask = (d > depth_min) & (d < depth_max)
    r = rows[mask]; c = cols[mask]; dv = d[mask]
    x_cam = (c - cx) * dv / fx
    y_cam = (r - cy) * dv / fy
    z_cam = dv
    ones = np.ones_like(z_cam)
    pts_cam = np.stack([x_cam, y_cam, z_cam, ones], axis=1)  # (N, 4)
    pts_world = (T_world_cam @ pts_cam.T).T  # (N, 4)
    return pts_world[:, :3]


def bbox3d_from_points(pts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute axis-aligned bounding box from Nx3 point cloud.

    Returns (center_xyz, extent_whd).
    """
    if len(pts) == 0:
        return np.zeros(3), np.zeros(3)
    mins = pts.min(axis=0)
    maxs = pts.max(axis=0)
    center = (mins + maxs) / 2
    extent = maxs - mins
    return center, extent


def distance_3d(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(np.array(a) - np.array(b)))


def are_near(a_xyz, b_xyz, threshold_m: float) -> bool:
    return distance_3d(a_xyz, b_xyz) <= threshold_m


def spatial_relation(a_xyz, b_xyz, threshold_m: float = 0.3) -> str:
    """Return coarse spatial relation label between two object centers."""
    d = distance_3d(a_xyz, b_xyz)
    if d <= threshold_m:
        return "NEAR"
    dx = b_xyz[0] - a_xyz[0]
    dy = b_xyz[1] - a_xyz[1]
    dz = b_xyz[2] - a_xyz[2]
    if abs(dy) > abs(dx) and abs(dy) > abs(dz):
        return "ABOVE" if dy < 0 else "BELOW"
    if abs(dx) > abs(dz):
        return "LEFT_OF" if dx > 0 else "RIGHT_OF"
    return "FAR"
