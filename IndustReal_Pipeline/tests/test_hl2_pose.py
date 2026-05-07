from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from src.hl2_pose import (
    is_valid_pose_flat,
    load_pose_csv,
    matrix_to_flat,
    vectors_to_pose_matrix,
)


def test_vectors_to_pose_matrix_produces_valid_pose() -> None:
    pose = vectors_to_pose_matrix(
        forward_xyz=[0.0, 0.0, 1.0],
        position_xyz=[1.5, -2.0, 3.25],
        up_xyz=[0.0, 1.0, 0.0],
    )
    assert np.allclose(pose[:3, 3], [1.5, -2.0, 3.25])
    assert np.allclose(pose[3], [0.0, 0.0, 0.0, 1.0])
    assert np.allclose(pose[:3, :3] @ pose[:3, :3].T, np.eye(3), atol=1e-5)
    assert is_valid_pose_flat(matrix_to_flat(pose))


def test_load_pose_csv_reuses_neighbor_for_zero_vector_rows(tmp_path: Path) -> None:
    pose_path = tmp_path / "pose.csv"
    rows = [
        ["000000.jpg", "0", "0", "1", "1", "2", "3", "0", "1", "0"],
        ["000001.jpg", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["000002.jpg", "0", "1", "0", "4", "5", "6", "0", "0", "1"],
    ]
    with open(pose_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    poses = load_pose_csv(pose_path)

    assert set(poses) == {"000000.jpg", "000001.jpg", "000002.jpg"}
    assert poses["000001.jpg"] == poses["000000.jpg"]
    assert poses["000002.jpg"] != poses["000001.jpg"]
