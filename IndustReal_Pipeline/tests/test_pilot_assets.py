from __future__ import annotations

import copy
import json
import tarfile
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

from src.pilot_assets import prepare_pilot_assets
from src.raw_cad_config import RawCadPaths, load_raw_cad_config


def _write_clip(root: Path, clip_name: str) -> None:
    clip_dir = root / clip_name
    for idx in (0, 1, 2):
        frame_name = f"{idx:06d}.jpg"
        for stream, size in {
            "rgb": (64, 48),
            "depth": (32, 24),
            "stereo_left": (32, 24),
            "stereo_right": (32, 24),
        }.items():
            path = clip_dir / stream / frame_name
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", size, color=(idx * 20, 10, 10)).save(path)
    (clip_dir / "pose.csv").write_text(
        "000000.jpg,0,0,1,0,0,0,0,1,0\n"
        "000001.jpg,0,0,1,0,0,1,0,1,0\n"
        "000002.jpg,0,0,1,0,0,2,0,1,0\n"
    )
    (clip_dir / "gaze.csv").write_text("000000.jpg,10,10\n")
    (clip_dir / "hands.csv").write_text("000000.jpg,1,0,0\n")
    (clip_dir / "OD_labels.json").write_text(
        json.dumps(
            {
                "categories": [{"id": 1, "name": "background"}],
                "images": [{"id": 0, "file_name": "000000.jpg", "width": 64, "height": 48}],
                "annotations": [{"id": 1, "image_id": 0, "category_id": 1, "bbox": [0, 0, 1, 1]}],
            }
        )
    )
    (clip_dir / "PSR_labels_with_errors.csv").write_text("000001.jpg,3,Install front chassis\n")
    (clip_dir / "PSR_labels.csv").write_text("000001.jpg,3,Install front chassis\n")


def test_prepare_pilot_assets_uses_base_slice_fallback(tmp_path: Path) -> None:
    cfg = copy.deepcopy(load_raw_cad_config())
    working_root = tmp_path / "working"
    results_root = tmp_path / "results"
    cfg["paths"]["working_root"] = str(working_root)
    cfg["paths"]["results_root"] = str(results_root)

    relevant_root = tmp_path / "relevant_slice"
    _write_clip(relevant_root, "03_assy_0_1")
    _write_clip(relevant_root, "03_assy_1_3")
    base_tar = tmp_path / "base.tar.gz"
    with tarfile.open(base_tar, "w:gz") as tf:
        tf.add(relevant_root, arcname="relevant_slice")
    cfg["archives"]["base_slice_repo"] = str(base_tar)

    asd_zip = tmp_path / "asd.zip"
    with zipfile.ZipFile(asd_zip, "w") as zf:
        zf.writestr("ASD_IndustRealplusSynthetic_test/placeholder.txt", "x")
    cfg["archives"]["asd_results_zip"] = str(asd_zip)
    for item in cfg["archives"]["source_archives"]:
        item["local_path"] = str(tmp_path / f"missing_{item['name']}.zip")

    paths = RawCadPaths(cfg)
    summary = prepare_pilot_assets(cfg, paths=paths)
    assert summary["clip_count"] == 2
    assert "fallback" in summary["warnings"][0]
    assert (working_root / "slices" / summary["slice_id"] / "03_assy_0_1").exists()
    assert paths.latest_slice_path.exists()
