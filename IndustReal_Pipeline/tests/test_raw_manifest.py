from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from src.raw_manifest import build_raw_manifest, validate_raw_manifest


def _write_image(path: Path, size: tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(32, 64, 96)).save(path)


def _make_clip(clip_dir: Path) -> None:
    for idx in (0, 5):
        frame_name = f"{idx:06d}.jpg"
        _write_image(clip_dir / "rgb" / frame_name, (64, 48))
        _write_image(clip_dir / "depth" / frame_name, (32, 24))
        _write_image(clip_dir / "stereo_left" / frame_name, (32, 24))
        _write_image(clip_dir / "stereo_right" / frame_name, (32, 24))
    (clip_dir / "pose.csv").write_text(
        "\n".join(
            [
                "000000.jpg,0,0,1,0,0,0,0,1,0",
                "000005.jpg,0,0,1,1,2,3,0,1,0",
            ]
        )
    )
    (clip_dir / "gaze.csv").write_text("000000.jpg,10,20\n000005.jpg,30,40\n")
    (clip_dir / "hands.csv").write_text("000000.jpg,1,0,0\n000005.jpg,0,0,0\n")
    od_payload = {
        "categories": [{"id": 1, "name": "background"}],
        "images": [{"id": 0, "file_name": "000000.jpg", "width": 64, "height": 48}],
        "annotations": [{"id": 1, "image_id": 0, "category_id": 1, "bbox": [1, 2, 10, 8]}],
    }
    (clip_dir / "OD_labels.json").write_text(json.dumps(od_payload))
    (clip_dir / "PSR_labels.csv").write_text("000005.jpg,3,Install front chassis\n")


def test_build_raw_manifest_preserves_original_frame_indices(tmp_path: Path) -> None:
    clip_dir = tmp_path / "clip_a"
    _make_clip(clip_dir)

    df = build_raw_manifest(clip_dir, source_archive="base.tar.gz", split="test")
    assert list(df["frame_idx"]) == [0, 5]
    assert list(df["timestamp_ns"]) == [0, 500_000_000]
    assert list(df["gaze_x"]) == [10, 30]
    assert list(df["has_hands"]) == [True, False]

    report = validate_raw_manifest(df, clip_dir)
    assert not report["errors"]
