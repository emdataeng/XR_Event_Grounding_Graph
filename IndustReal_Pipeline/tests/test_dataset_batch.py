from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

from PIL import Image

from src import psr
from src.dataset_batch import (
    build_clip_inventory,
    default_run_id,
    extract_full_clip_from_zip,
    run_oracle_dataset_batch,
)
from src.raw_cad_config import RawCadPaths


def _jpg_bytes(mode: str, size: tuple[int, int]) -> bytes:
    image = Image.new(mode, size, color=64)
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def _pose_csv_lines(frame_names: list[str]) -> str:
    rows = []
    for frame_name in frame_names:
        rows.append(f"{frame_name},0,0,1,0,0,0,0,1,0")
    return "\n".join(rows) + "\n"


def _gaze_csv_lines(frame_names: list[str]) -> str:
    return "\n".join(f"{frame_name},10,20" for frame_name in frame_names) + "\n"


def _hands_csv_lines(frame_names: list[str]) -> str:
    return "\n".join(f"{frame_name},0,0,0" for frame_name in frame_names) + "\n"


def _od_payload(frame_states: list[tuple[str, str]]) -> dict:
    unique_states = ["background"]
    for _, state in frame_states:
        if state not in unique_states:
            unique_states.append(state)
    categories = [{"id": idx + 1, "name": state} for idx, state in enumerate(unique_states)]
    cat_by_name = {item["name"]: item["id"] for item in categories}
    images = []
    annotations = []
    for idx, (frame_name, state_name) in enumerate(frame_states):
        images.append({"id": idx, "file_name": frame_name, "width": 1280, "height": 720})
        annotations.append(
            {
                "id": idx + 1,
                "image_id": idx,
                "category_id": cat_by_name[state_name],
                "bbox": [100.0, 100.0, 50.0, 50.0],
            }
        )
    return {"images": images, "annotations": annotations, "categories": categories}


def _write_clip_to_zip(
    zf: zipfile.ZipFile,
    *,
    root_prefix: str,
    clip_name: str,
    frame_names: list[str],
    od_payload: dict,
    psr_rows: list[tuple[str, int, str]],
) -> None:
    clip_prefix = f"{root_prefix}/{clip_name}"
    for stream, mode, size in (
        ("rgb", "RGB", (1280, 720)),
        ("depth", "RGB", (320, 288)),
        ("stereo_left", "L", (480, 640)),
        ("stereo_right", "L", (480, 640)),
    ):
        for frame_name in frame_names:
            zf.writestr(f"{clip_prefix}/{stream}/{frame_name}", _jpg_bytes(mode, size))
    zf.writestr(f"{clip_prefix}/pose.csv", _pose_csv_lines(frame_names))
    zf.writestr(f"{clip_prefix}/gaze.csv", _gaze_csv_lines(frame_names))
    zf.writestr(f"{clip_prefix}/hands.csv", _hands_csv_lines(frame_names))
    zf.writestr(f"{clip_prefix}/OD_labels.json", json.dumps(od_payload))
    psr_text = "\n".join(f"{frame},{step_id},{desc}" for frame, step_id, desc in psr_rows) + "\n"
    zf.writestr(f"{clip_prefix}/PSR_labels.csv", psr_text)
    zf.writestr(f"{clip_prefix}/PSR_labels_with_errors.csv", psr_text)


def _write_synthetic_archives(tmp_path: Path) -> tuple[Path, Path]:
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    archive_path = source_dir / "test_p1.zip"
    clean_clip = "03_assy_clean_0"
    error_clip = "03_assy_error_0"
    with zipfile.ZipFile(archive_path, "w") as zf:
        _write_clip_to_zip(
            zf,
            root_prefix="test_p1",
            clip_name=clean_clip,
            frame_names=["000000.jpg", "000001.jpg"],
            od_payload=_od_payload(
                [
                    ("000000.jpg", "10000000000"),
                    ("000001.jpg", "11100000000"),
                ]
            ),
            psr_rows=[
                ("000001.jpg", 3, "Install front chassis"),
                ("000001.jpg", 6, "Install front chassis pin"),
            ],
        )
        _write_clip_to_zip(
            zf,
            root_prefix="test_p1",
            clip_name=error_clip,
            frame_names=["000000.jpg", "000001.jpg"],
            od_payload=_od_payload(
                [
                    ("000000.jpg", "10000000000"),
                ]
            ),
            psr_rows=[
                ("000001.jpg", 4, "Incorrectly installed front chassis"),
                ("000001.jpg", 6, "Install front chassis pin"),
            ],
        )

    asd_zip = tmp_path / "ASD_results.zip"
    clean_state_idx = psr.CATEGORIES.index("11100000000")
    error_state_idx = psr.CATEGORIES.index("10000000000")
    with zipfile.ZipFile(asd_zip, "w") as zf:
        for clip_name, class_idx in ((clean_clip, clean_state_idx), (error_clip, error_state_idx)):
            text = "clip,framenr,bb_class\n" + f"{clip_name},0,{class_idx}\n"
            zf.writestr(f"ASD_IndustRealplusSynthetic_test/{clip_name}_results_gt.csv", text)
            zf.writestr(f"ASD_IndustRealplusSynthetic_test/{clip_name}_results_pred.csv", text)

    part_zip = tmp_path / "part_geometries.zip"
    with zipfile.ZipFile(part_zip, "w") as zf:
        zf.writestr("part_geometries/Overview of states.pdf", b"pdf")
        zf.writestr("part_geometries/state1.fbx", b"fbx")
        zf.writestr("part_geometries/state2.fbx", b"fbx")
        zf.writestr("part_geometries/SPS-000001 - Rubber-band-driven car - Beams Braces.3mf", b"3mf")
        zf.writestr("part_geometries/SPS-000001 - Rubber-band-driven car - Screws Pins.3mf", b"3mf")
        zf.writestr(
            "part_geometries/SPS-000001 - Rubber-band-driven car - Sign Nuts Washers Pulley.3mf",
            b"3mf",
        )
        zf.writestr("part_geometries/SPS-000001 - Rubber-band-driven car - Wheels.3mf", b"3mf")
    return archive_path, asd_zip


def _dataset_cfg(tmp_path: Path) -> dict:
    cfg = json.loads((Path(__file__).resolve().parent.parent / "configs" / "raw_cad_dataset.json").read_text())
    work_root = tmp_path / "working"
    archive_path, asd_zip = _write_synthetic_archives(tmp_path)
    cfg["paths"]["data_root"] = str(tmp_path / "data")
    cfg["paths"]["results_root"] = str(tmp_path / "reports")
    cfg["paths"]["reports_root"] = str(tmp_path / "reports")
    cfg["paths"]["working_root"] = str(work_root)
    cfg["archives"]["asd_results_zip"] = str(asd_zip)
    cfg["archives"]["part_geometries_repo"] = str(tmp_path / "part_geometries.zip")
    cfg["archives"]["part_geometries_working"] = str(work_root / "source" / "part_geometries.zip")
    cfg["archives"]["source_archives"] = [
        {
            "name": "test_p1",
            "split": "test",
            "local_path": str(archive_path),
            "url": "https://example.invalid/test_p1.zip",
        }
    ]
    cfg["batch"]["keep_debug_visuals"] = True
    cfg["batch"]["allow_download_missing"] = False
    cfg["batch"]["resume"] = True
    return cfg


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_archive_inventory_enumerates_clips_from_archive(tmp_path: Path) -> None:
    cfg = _dataset_cfg(tmp_path)
    paths = RawCadPaths(cfg)
    _, inventory = build_clip_inventory(cfg, allow_download=False)
    assert [row["clip"] for row in inventory] == ["03_assy_clean_0", "03_assy_error_0"]
    assert all(row["stream_counts"]["rgb"] == 2 for row in inventory)
    assert all(row["metadata_present"]["OD_labels.json"] for row in inventory)


def test_full_clip_extraction_copies_all_streams_and_metadata(tmp_path: Path) -> None:
    cfg = _dataset_cfg(tmp_path)
    archive_path = Path(cfg["archives"]["source_archives"][0]["local_path"])
    out_dir = tmp_path / "clip"
    extract_full_clip_from_zip(archive_path, "03_assy_clean_0", out_dir=out_dir)
    for required in [
        out_dir / "rgb" / "000000.jpg",
        out_dir / "depth" / "000001.jpg",
        out_dir / "stereo_left" / "000000.jpg",
        out_dir / "stereo_right" / "000001.jpg",
        out_dir / "pose.csv",
        out_dir / "OD_labels.json",
        out_dir / "PSR_labels_with_errors.csv",
    ]:
        assert required.exists()


def test_batch_runner_emits_two_oracle_modes_and_full_gt(tmp_path: Path) -> None:
    cfg = _dataset_cfg(tmp_path)
    paths = RawCadPaths(cfg)
    result = run_oracle_dataset_batch(cfg, paths=paths)
    run_id = default_run_id(cfg)
    assert result["summary_rows"] == 4

    od_only_dir = paths.dataset_clip_mode_dir(run_id, "od_only", "test_p1", "03_assy_error_0")
    plus_dir = paths.dataset_clip_mode_dir(run_id, "od_plus_psr_error_hints", "test_p1", "03_assy_error_0")
    assert od_only_dir.exists()
    assert plus_dir.exists()

    od_only_pred = json.loads((od_only_dir / "psr_pred.json").read_text())
    plus_pred = json.loads((plus_dir / "psr_pred.json").read_text())
    gt_steps = json.loads((plus_dir / "gt_steps.json").read_text())
    assert od_only_pred == []
    assert [step["id"] for step in plus_pred] == [4, 6]
    assert [step["id"] for step in gt_steps] == [4, 6]

    summary_rows = _load_csv_rows(paths.dataset_summary_path(run_id))
    assert len(summary_rows) == 4
    plus_row = next(
        row for row in summary_rows
        if row["run_mode"] == "od_plus_psr_error_hints" and row["clip"] == "03_assy_error_0"
    )
    od_row = next(
        row for row in summary_rows
        if row["run_mode"] == "od_only" and row["clip"] == "03_assy_error_0"
    )
    assert plus_row["step_recall"] == "1.0"
    assert od_row["step_recall"] == "0.0"


def test_batch_runner_resume_skips_completed_items(tmp_path: Path) -> None:
    cfg = _dataset_cfg(tmp_path)
    paths = RawCadPaths(cfg)
    run_id = default_run_id(cfg)
    run_oracle_dataset_batch(cfg, paths=paths)
    metrics_path = paths.dataset_clip_mode_dir(
        run_id,
        "od_plus_psr_error_hints",
        "test_p1",
        "03_assy_error_0",
    ) / "metrics.json"
    before = metrics_path.stat().st_mtime_ns
    run_oracle_dataset_batch(cfg, paths=paths)
    after = metrics_path.stat().st_mtime_ns
    assert before == after


def test_mode_comparison_and_failure_log_reports_are_created(tmp_path: Path) -> None:
    cfg = _dataset_cfg(tmp_path)
    paths = RawCadPaths(cfg)
    run_id = default_run_id(cfg)
    run_oracle_dataset_batch(cfg, paths=paths)

    comparison_rows = _load_csv_rows(paths.dataset_mode_comparison_path(run_id))
    failure_log = json.loads(paths.dataset_failure_log_path(run_id).read_text())
    run_manifest = json.loads(paths.dataset_run_manifest_path(run_id).read_text())
    clip_inventory_rows = _load_csv_rows(paths.dataset_clip_inventory_path(run_id))

    clip_row = next(row for row in comparison_rows if row["scope"] == "clip" and row["clip"] == "03_assy_error_0")
    assert clip_row["delta_step_recall"] == "1.0"
    assert failure_log == []
    assert len(run_manifest["status_by_item"]) == 4
    assert len(clip_inventory_rows) == 2
