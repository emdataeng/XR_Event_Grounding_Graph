"""Tests for src/geometry.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from src.geometry import (
    quaternion_to_rotation_matrix,
    pose_to_matrix,
    matrix_to_flat,
    flat_to_matrix,
    deproject_pixel_to_world,
    distance_3d,
    spatial_relation,
)


def test_identity_quaternion():
    R = quaternion_to_rotation_matrix(0, 0, 0, 1)
    np.testing.assert_allclose(R, np.eye(3), atol=1e-6)


def test_pose_matrix_bottom_row():
    T = pose_to_matrix([1.0, 2.0, 3.0], [0, 0, 0, 1])
    np.testing.assert_allclose(T[3], [0, 0, 0, 1], atol=1e-6)
    np.testing.assert_allclose(T[:3, 3], [1.0, 2.0, 3.0])


def test_flat_roundtrip():
    T = pose_to_matrix([0.5, -0.3, 1.2], [0.1, 0.0, 0.0, 0.9950])
    flat = matrix_to_flat(T)
    assert len(flat) == 16
    T2 = flat_to_matrix(flat)
    np.testing.assert_allclose(T, T2, atol=1e-6)


def test_deproject_center_pixel():
    T = np.eye(4)
    T[:3, 3] = [0, 0, 0]
    # Centre pixel with depth=1.0 should land at (0, 0, 1) in camera=world coords
    p = deproject_pixel_to_world(160.0, 120.0, 1.0, 240.0, 240.0, 160.0, 120.0, T)
    np.testing.assert_allclose(p, [0, 0, 1], atol=1e-4)


def test_distance_3d():
    assert abs(distance_3d([0, 0, 0], [3, 4, 0]) - 5.0) < 1e-6


def test_spatial_relation_near():
    r = spatial_relation([0, 0, 0], [0.1, 0, 0], threshold_m=0.3)
    assert r == "NEAR"


def test_spatial_relation_far():
    r = spatial_relation([0, 0, 0], [5, 0, 0], threshold_m=0.3)
    assert r in ("FAR", "LEFT_OF", "RIGHT_OF")
