"""Tests for manifest building and validation logic."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from src.pose_utils import is_valid_pose, poses_are_plausible, meta_to_pose_flat
from src.io_utils import ticks_to_ns


def test_ticks_to_ns_relative():
    base = 639082426426981790
    ts = ticks_to_ns(base, relative_to=base)
    assert ts == 0

    later = base + 10_000_000  # 1 second later in ticks
    ts2 = ticks_to_ns(later, relative_to=base)
    assert ts2 == 1_000_000_000  # 1 second in nanoseconds


def test_valid_pose():
    flat = [1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1]
    assert is_valid_pose(flat)


def test_invalid_pose_wrong_length():
    assert not is_valid_pose([1, 0, 0])


def test_invalid_pose_bad_rotation():
    flat = [2, 0, 0, 0,  # non-orthonormal
            0, 2, 0, 0,
            0, 0, 2, 0,
            0, 0, 0, 1]
    assert not is_valid_pose(flat)


def test_poses_plausible():
    p1 = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    p2 = [1,0,0,0.1, 0,1,0,0.1, 0,0,1,0.1, 0,0,0,1]
    assert poses_are_plausible([p1, p2], max_jump_m=5.0)


def test_meta_to_pose_flat():
    meta = {
        "pose": {
            "position": [1.0, 2.0, 3.0],
            "rotation_xyzw": [0.0, 0.0, 0.0, 1.0],
        }
    }
    flat = meta_to_pose_flat(meta)
    assert len(flat) == 16
    # Translation should be in elements 3, 7, 11
    assert abs(flat[3] - 1.0) < 1e-6
    assert abs(flat[7] - 2.0) < 1e-6
    assert abs(flat[11] - 3.0) < 1e-6
