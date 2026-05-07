"""Prepare deterministic raw IndustReal pilot slices under /tmp."""
from __future__ import annotations

import csv
import json
import shutil
import tarfile
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from .raw_cad_config import RawCadPaths
from .raw_loader import ROOT_METADATA_FILES, STREAM_NAMES, discover_clip_streams, frame_name_to_idx


def _is_error_like(description: str) -> bool:
    text = description.strip().lower()
    return text.startswith("incorrectly") or text.startswith("remove")


def _merge_windows(
    windows: list[tuple[int, int, str]],
    *,
    min_frame: int,
    merge_gap: int,
    max_frame: int,
) -> list[dict[str, Any]]:
    if not windows:
        return []
    normalized = []
    for start, end, reason in windows:
        start = max(min_frame, int(start))
        end = min(max_frame, int(end))
        if end < start:
            continue
        normalized.append((start, end, reason))
    normalized.sort(key=lambda item: (item[0], item[1], item[2]))
    merged: list[dict[str, Any]] = []
    cur_start, cur_end, cur_reasons = normalized[0][0], normalized[0][1], [normalized[0][2]]
    for start, end, reason in normalized[1:]:
        if start <= cur_end + merge_gap + 1:
            cur_end = max(cur_end, end)
            if reason not in cur_reasons:
                cur_reasons.append(reason)
            continue
        merged.append({"start": cur_start, "end": cur_end, "reasons": cur_reasons[:]})
        cur_start, cur_end, cur_reasons = start, end, [reason]
    merged.append({"start": cur_start, "end": cur_end, "reasons": cur_reasons[:]})
    return merged


def build_slice_windows(
    step_rows: list[dict[str, Any]],
    *,
    min_frame: int = 0,
    max_frame: int,
    rules: dict[str, Any],
) -> list[dict[str, Any]]:
    windows: list[tuple[int, int, str]] = [
        (min_frame, min(max_frame, min_frame + int(rules["context_head"]) - 1), "context_head"),
        (max(0, max_frame - int(rules["context_tail"]) + 1), max_frame, "context_tail"),
    ]
    for row in step_rows:
        desc = str(row["description"])
        frame_idx = int(row["frame_idx"])
        if desc.startswith("Install "):
            start = frame_idx - int(rules["install_pre"])
            end = frame_idx + int(rules["install_post"])
        else:
            start = frame_idx - int(rules["error_pre"])
            end = frame_idx + int(rules["error_post"])
        windows.append((start, end, desc))
    return _merge_windows(
        windows,
        min_frame=int(min_frame),
        merge_gap=int(rules["merge_gap"]),
        max_frame=max_frame,
    )


def frame_indices_from_windows(windows: list[dict[str, Any]]) -> list[int]:
    frames: list[int] = []
    for window in windows:
        frames.extend(range(int(window["start"]), int(window["end"]) + 1))
    return sorted(set(frames))


def _read_step_rows_from_text(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in csv.reader(text.splitlines()):
        if len(raw) < 3:
            continue
        rows.append(
            {
                "frame_name": raw[0],
                "frame_idx": frame_name_to_idx(raw[0]),
                "id": int(raw[1]),
                "description": raw[2],
            }
        )
    return rows


def _clip_member_map(names: list[str], clip_name: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for name in names:
        if name.endswith("/"):
            continue
        parts = PurePosixPath(name).parts
        if clip_name not in parts:
            continue
        idx = parts.index(clip_name)
        rel = PurePosixPath(*parts[idx + 1 :]).as_posix()
        if rel:
            mapping[rel] = name
    return mapping


def _rgb_frame_indices_from_member_map(member_map: dict[str, str]) -> list[int]:
    indices = []
    for rel in member_map:
        parts = PurePosixPath(rel).parts
        if len(parts) == 2 and parts[0] == "rgb" and parts[1].endswith(".jpg"):
            indices.append(frame_name_to_idx(parts[1]))
    return sorted(indices)


def _archive_has_matching_asd(asd_zip: zipfile.ZipFile, clip_name: str) -> bool:
    names = set(asd_zip.namelist())
    return (
        f"ASD_IndustRealplusSynthetic_test/{clip_name}_results_gt.csv" in names
        and f"ASD_IndustRealplusSynthetic_test/{clip_name}_results_pred.csv" in names
    )


def _qualify_archive_clip(
    archive_path: Path,
    clip_name: str,
    *,
    asd_zip: zipfile.ZipFile,
) -> dict[str, Any] | None:
    with zipfile.ZipFile(archive_path) as zf:
        member_map = _clip_member_map(zf.namelist(), clip_name)
        if "PSR_labels_with_errors.csv" not in member_map:
            return None
        step_rows = _read_step_rows_from_text(zf.read(member_map["PSR_labels_with_errors.csv"]).decode())
        if not step_rows:
            return None
        error_rows = [row for row in step_rows if str(row["description"]).startswith("Incorrectly ")]
        if not error_rows:
            return None
        first_error = min(int(row["frame_idx"]) for row in error_rows)
        later_non_error = any(
            int(row["frame_idx"]) > first_error and not _is_error_like(str(row["description"]))
            for row in step_rows
        )
        if not later_non_error:
            return None
        if not _archive_has_matching_asd(asd_zip, clip_name):
            return None
        rgb_indices = _rgb_frame_indices_from_member_map(member_map)
        if not rgb_indices:
            return None
        return {
            "clip": clip_name,
            "archive_path": archive_path,
            "member_map": member_map,
            "step_rows": step_rows,
            "frame_count": len(rgb_indices),
            "max_frame": max(rgb_indices),
        }


def select_third_clip(cfg: dict[str, Any], paths: RawCadPaths) -> dict[str, Any] | None:
    base_clips = set(cfg["pilot"]["base_clips"])
    asd_zip_path = paths.resolve_archive_path("asd_results_zip")
    if asd_zip_path is None or not asd_zip_path.exists():
        return None
    with zipfile.ZipFile(asd_zip_path) as asd_zip:
        for archive_cfg in cfg["archives"]["source_archives"]:
            archive_path = Path(archive_cfg["local_path"])
            if not archive_path.exists():
                continue
            with zipfile.ZipFile(archive_path) as zf:
                candidate_names = sorted(
                    {
                        part
                        for name in zf.namelist()
                        for part in PurePosixPath(name).parts
                        if "_assy_" in part and part not in base_clips
                    }
                )
            qualified: list[dict[str, Any]] = []
            for clip_name in candidate_names:
                record = _qualify_archive_clip(archive_path, clip_name, asd_zip=asd_zip)
                if record is None:
                    continue
                record["source_archive"] = archive_cfg["name"]
                record["split"] = archive_cfg.get("split", "test")
                qualified.append(record)
            if qualified:
                qualified.sort(key=lambda item: (int(item["frame_count"]), item["clip"]))
                return qualified[0]
    return None


def _copy_selected_from_zip(
    archive_path: Path,
    clip_name: str,
    *,
    member_map: dict[str, str],
    frame_indices: list[int],
    out_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    selected_names = {f"{idx:06d}.jpg" for idx in frame_indices}
    with zipfile.ZipFile(archive_path) as zf:
        for metadata_name in ROOT_METADATA_FILES:
            member = member_map.get(metadata_name)
            if not member:
                continue
            target = out_dir / metadata_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(member))
        for stream in STREAM_NAMES:
            for frame_name in selected_names:
                rel = f"{stream}/{frame_name}"
                member = member_map.get(rel)
                if not member:
                    continue
                target = out_dir / stream / frame_name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(member))


def _extract_base_clips_from_tar(
    tar_path: Path,
    out_root: Path,
    *,
    base_clips: list[str],
) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out_root.parent) as tmpdir:
        tmp_root = Path(tmpdir)
        with tarfile.open(tar_path, "r:gz") as tf:
            tf.extractall(tmp_root)
        extracted_root = tmp_root / "relevant_slice"
        for clip_name in base_clips:
            src = extracted_root / clip_name
            if not src.exists():
                raise FileNotFoundError(f"missing base clip in tarball: {clip_name}")
            shutil.copytree(src, out_root / clip_name, dirs_exist_ok=True)


def _load_step_rows_for_clip(clip_dir: Path) -> list[dict[str, Any]]:
    preferred = clip_dir / "PSR_labels_with_errors.csv"
    fallback = clip_dir / "PSR_labels.csv"
    if preferred.exists():
        return _read_step_rows_from_text(preferred.read_text())
    if fallback.exists():
        return _read_step_rows_from_text(fallback.read_text())
    return []


def _clip_summary(
    clip_dir: Path,
    *,
    source_archive: str,
    split: str,
    rules: dict[str, Any],
) -> dict[str, Any]:
    streams = discover_clip_streams(clip_dir)
    rgb_indices = sorted(streams["rgb"])
    min_frame = min(rgb_indices) if rgb_indices else 0
    max_frame = max(rgb_indices) if rgb_indices else 0
    step_rows = _load_step_rows_for_clip(clip_dir)
    windows = (
        build_slice_windows(step_rows, min_frame=min_frame, max_frame=max_frame, rules=rules)
        if step_rows
        else []
    )
    return {
        "clip": clip_dir.name,
        "source_archive": source_archive,
        "split": split,
        "frame_count": len(rgb_indices),
        "frame_min": min_frame if rgb_indices else None,
        "frame_max": max_frame if rgb_indices else None,
        "windows": windows,
        "selected_frame_count": len(frame_indices_from_windows(windows)) if windows else len(rgb_indices),
        "metadata_present": {
            name: (clip_dir / name).exists()
            for name in ROOT_METADATA_FILES
        },
        "stream_counts": {
            stream: len(frames)
            for stream, frames in streams.items()
        },
    }


def _dir_size_bytes(path: Path) -> int:
    total = 0
    for file_path in path.rglob("*"):
        if file_path.is_file():
            total += file_path.stat().st_size
    return total


def _build_slice_id(cfg: dict[str, Any], clip_names: list[str]) -> str:
    slug = "__".join(sorted(clip_names))
    return f"{cfg['pilot']['name']}__{slug}"


def prepare_pilot_assets(cfg: dict[str, Any], *, paths: RawCadPaths) -> dict[str, Any]:
    paths.ensure_base_dirs()
    rules = cfg["slice_rules"]
    base_tar = paths.resolve_archive_path("base_slice_repo")
    if base_tar is None or not base_tar.exists():
        raise FileNotFoundError(f"missing base slice tarball: {base_tar}")

    third_clip = select_third_clip(cfg, paths)
    selected_clips = list(cfg["pilot"]["base_clips"])
    warnings: list[str] = []
    if third_clip is not None:
        selected_clips.append(str(third_clip["clip"]))
    elif not cfg["pilot"].get("allow_base_slice_fallback", False):
        raise RuntimeError("could not determine the third pilot clip and fallback is disabled")
    else:
        warnings.append("third clip source archive unavailable; using base two-clip slice fallback")

    slice_id = _build_slice_id(cfg, selected_clips)
    slice_dir = paths.slice_workdir(slice_id)
    if slice_dir.exists():
        shutil.rmtree(slice_dir)
    slice_dir.mkdir(parents=True, exist_ok=True)

    _extract_base_clips_from_tar(base_tar, slice_dir, base_clips=list(cfg["pilot"]["base_clips"]))

    clip_records: list[dict[str, Any]] = []
    for clip_name in cfg["pilot"]["base_clips"]:
        clip_records.append(
            _clip_summary(
                slice_dir / clip_name,
                source_archive=base_tar.name,
                split="test",
                rules=rules,
            )
        )

    if third_clip is not None:
        third_dir = slice_dir / str(third_clip["clip"])
        windows = build_slice_windows(
            list(third_clip["step_rows"]),
            min_frame=0,
            max_frame=int(third_clip["max_frame"]),
            rules=rules,
        )
        frame_indices = frame_indices_from_windows(windows)
        _copy_selected_from_zip(
            Path(third_clip["archive_path"]),
            str(third_clip["clip"]),
            member_map=dict(third_clip["member_map"]),
            frame_indices=frame_indices,
            out_dir=third_dir,
        )
        record = _clip_summary(
            third_dir,
            source_archive=str(third_clip["source_archive"]),
            split=str(third_clip["split"]),
            rules=rules,
        )
        record["windows"] = windows
        record["selected_frame_count"] = len(frame_indices)
        clip_records.append(record)

    extracted_mb = _dir_size_bytes(slice_dir) / (1024 * 1024)
    compressed_mb = base_tar.stat().st_size / (1024 * 1024)
    summary = {
        "slice_id": slice_id,
        "slice_dir": str(slice_dir),
        "selected_clips": selected_clips,
        "clip_count": len(selected_clips),
        "warnings": warnings,
        "storage": {
            "compressed_base_slice_mb": round(compressed_mb, 2),
            "extracted_slice_mb": round(extracted_mb, 2),
            "compressed_slice_cap_mb": cfg["storage_limits_mb"]["compressed_slice_cap"],
            "extracted_slice_cap_mb": cfg["storage_limits_mb"]["extracted_slice_cap"],
        },
        "clips": clip_records,
    }
    summary["storage"]["within_cap"] = extracted_mb <= float(cfg["storage_limits_mb"]["extracted_slice_cap"])
    summary_path = paths.slice_summary_path(slice_id)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    paths.latest_slice_path.write_text(
        json.dumps(
            {
                "slice_id": slice_id,
                "slice_dir": str(slice_dir),
                "selected_clips": selected_clips,
                "summary_path": str(summary_path),
            },
            indent=2,
        )
    )
    return summary


def load_latest_slice(paths: RawCadPaths) -> dict[str, Any]:
    if not paths.latest_slice_path.exists():
        raise FileNotFoundError(f"latest slice metadata not found: {paths.latest_slice_path}")
    return json.loads(paths.latest_slice_path.read_text())
