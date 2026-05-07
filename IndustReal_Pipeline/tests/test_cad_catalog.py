from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path

from src.cad_catalog import build_cad_part_catalog, build_state_catalog
from src.raw_cad_config import load_raw_cad_config


def _write_asd_zip(path: Path) -> None:
    rows = [
        ["clip", "framenr", "bb_class", "bb_conf", "bb_x", "bb_y", "bb_w", "bb_h"],
        ["toy_assy_0_1", "0", "0", "1", "0", "0", "1", "1"],
        ["toy_assy_0_1", "1", "1", "1", "0", "0", "1", "1"],
        ["toy_assy_0_1", "2", "5", "1", "0", "0", "1", "1"],
    ]
    with zipfile.ZipFile(path, "w") as zf:
        gt_name = "ASD_IndustRealplusSynthetic_test/toy_assy_0_1_results_gt.csv"
        pred_name = "ASD_IndustRealplusSynthetic_test/toy_assy_0_1_results_pred.csv"
        content = "\n".join(",".join(row) for row in rows)
        zf.writestr(gt_name, content)
        zf.writestr(pred_name, content)


def _write_part_zip(path: Path) -> None:
    cfg = load_raw_cad_config()
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("part_geometries/Overview of states.pdf", b"pdf")
        for name in cfg["cad"]["asset_families"].values():
            zf.writestr(f"part_geometries/{name}", b"3mf")
        for idx in range(1, 23):
            zf.writestr(f"part_geometries/state{idx}.fbx", b"fbx")


def test_build_cad_catalog_contains_all_components_and_states(tmp_path: Path) -> None:
    cfg = load_raw_cad_config()
    asd_zip = tmp_path / "asd.zip"
    part_zip = tmp_path / "parts.zip"
    _write_asd_zip(asd_zip)
    _write_part_zip(part_zip)

    part_catalog = build_cad_part_catalog(cfg, part_geometries_zip=part_zip)
    state_catalog = build_state_catalog(cfg, procedure_info=[{"id": 0}], asd_results_zip=asd_zip)

    assert len(part_catalog["components"]) == 11
    assert len(state_catalog["states"]) == 24
    assert "error_state" in state_catalog["transitions"]
    assert "10000000000" in state_catalog["transitions"]["background"]
