"""Raw RGB detector backends for the CAD-grounded pilot."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

from .raw_loader import load_od_labels, load_step_labels_csv


@dataclass
class DetectorContext:
    part_catalog: dict[str, Any]
    state_catalog: dict[str, Any]
    config: dict[str, Any]

    def component_lookup(self) -> dict[str, dict[str, Any]]:
        return {
            str(item["key"]): item
            for item in self.part_catalog["components"]
        }


def _state_component_lookup(state_catalog: dict[str, Any]) -> dict[str, list[str]]:
    return {
        str(item["state_name"]): list(item.get("component_keys", []))
        for item in state_catalog["states"]
    }


def _label_lexicon(part_catalog: dict[str, Any]) -> dict[str, str]:
    lexicon: dict[str, str] = {}
    for component in part_catalog["components"]:
        key = str(component["key"])
        lexicon[key.replace("_", " ")] = key
        lexicon[str(component["display_name"]).lower()] = key
        for phrase in component.get("prompts", []):
            lexicon[str(phrase).lower()] = key
        for alias in component.get("aliases", []):
            lexicon[str(alias).lower()] = key
    for context_item in part_catalog.get("context_components", []):
        key = str(context_item["key"])
        lexicon[str(context_item["display_name"]).lower()] = key
        for phrase in context_item.get("prompts", []):
            lexicon[str(phrase).lower()] = key
        for alias in context_item.get("aliases", []):
            lexicon[str(alias).lower()] = key
    return lexicon


def canonicalize_label(raw_label: str, part_catalog: dict[str, Any]) -> str | None:
    label = raw_label.strip().lower()
    lexicon = _label_lexicon(part_catalog)
    if label in lexicon:
        return lexicon[label]
    for phrase, key in lexicon.items():
        if label in phrase or phrase in label:
            return key
    return None


def _manifest_frame_record(row: pd.Series) -> dict[str, Any]:
    return {
        "clip": row["clip"],
        "frame_idx": int(row["frame_idx"]),
        "frame_name": row["frame_name"],
        "timestamp_ns": int(row["timestamp_ns"]),
    }


def _is_error_like_step(description: str) -> bool:
    text = description.strip().lower()
    return text.startswith("incorrectly") or text.startswith("remove")


def oracle_od_records(
    manifest_df: pd.DataFrame,
    *,
    clip_dir: Path,
    context: DetectorContext,
    include_error_step_hints: bool = True,
) -> list[dict[str, Any]]:
    od_labels = load_od_labels(clip_dir / "OD_labels.json")
    step_rows = load_step_labels_csv(clip_dir / "PSR_labels_with_errors.csv")
    error_step_hints: dict[int, list[dict[str, Any]]] = {}
    if include_error_step_hints:
        grouped_step_rows: dict[int, list[dict[str, Any]]] = {}
        for row in step_rows:
            frame_idx = int(row["frame_idx"])
            grouped_step_rows.setdefault(frame_idx, []).append(
                {
                    "frame": frame_idx,
                    "id": int(row["id"]),
                    "description": str(row["description"]),
                    "conf": 1.0,
                }
            )
        for frame_idx, rows_for_frame in grouped_step_rows.items():
            if any(_is_error_like_step(str(item["description"])) for item in rows_for_frame):
                error_step_hints[frame_idx] = rows_for_frame
    component_lookup = context.component_lookup()
    state_to_components = _state_component_lookup(context.state_catalog)
    oracle_mode = str(context.config["detector"].get("oracle_mode", "state_labels"))
    records = []
    for _, row in manifest_df.iterrows():
        base = _manifest_frame_record(row)
        label = od_labels.get(str(row["frame_name"]))
        frame_error_steps = error_step_hints.get(int(row["frame_idx"]), [])
        detections = []
        base["oracle_mode"] = oracle_mode
        if label is not None:
            state_name = str(label["state_name"])
            base["source_state_name"] = state_name
            base["source_bbox_xyxy"] = list(label["bbox_xyxy"])
            if oracle_mode == "components_legacy":
                if state_name not in ("background", "error_state"):
                    for component_key in state_to_components.get(state_name, []):
                        component = component_lookup[component_key]
                        detections.append(
                            {
                                "raw_label": state_name,
                                "canonical_component": component_key,
                                "bbox_xyxy": list(label["bbox_xyxy"]),
                                "confidence": 1.0,
                                "detector_group": component["detector_group"],
                                "backend": "oracle_od",
                            }
                        )
                elif state_name == "error_state":
                    detections.append(
                        {
                            "raw_label": state_name,
                            "canonical_component": "__error__",
                            "bbox_xyxy": list(label["bbox_xyxy"]),
                            "confidence": 1.0,
                            "detector_group": "error",
                            "backend": "oracle_od",
                        }
                    )
        if frame_error_steps:
            base["source_error_steps"] = frame_error_steps
        records.append({**base, "backend": "oracle_od", "detections": detections})
    return records


def _load_open_vocab_backend(model_ids: list[str]):
    try:
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "transformers is required for the open_vocab_rgb backend"
        ) from exc

    last_error = None
    for model_id in model_ids:
        try:
            processor = AutoProcessor.from_pretrained(model_id)
            model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
            return model_id, processor, model
        except Exception as exc:  # pragma: no cover - network/model availability
            last_error = exc
            continue
    raise RuntimeError(f"could not load any open-vocabulary detector model: {last_error}")


def open_vocab_records(
    manifest_df: pd.DataFrame,
    *,
    context: DetectorContext,
) -> list[dict[str, Any]]:
    model_id, processor, model = _load_open_vocab_backend(
        list(context.config["detector"]["model_ids"])
    )
    component_lookup = context.component_lookup()
    group_vocab = dict(context.part_catalog["detector_vocabulary"])
    records = []
    for _, row in manifest_df.iterrows():
        rgb_path = Path(str(row["rgb_path"]))
        base = _manifest_frame_record(row)
        detections = []
        with Image.open(rgb_path) as image:
            width, height = image.size
            for detector_group, phrases in group_vocab.items():
                prompt = ". ".join(phrases)
                inputs = processor(images=image, text=prompt, return_tensors="pt")
                outputs = model(**inputs)
                results = processor.post_process_grounded_object_detection(
                    outputs,
                    inputs.input_ids,
                    box_threshold=float(context.config["detector"]["box_threshold"]),
                    text_threshold=float(context.config["detector"]["text_threshold"]),
                    target_sizes=[(height, width)],
                )[0]
                boxes = results.get("boxes", [])
                scores = results.get("scores", [])
                labels = results.get("labels", [])
                for box, score, label in zip(boxes, scores, labels):
                    label_text = str(label)
                    canonical = canonicalize_label(label_text, context.part_catalog)
                    if canonical is None:
                        continue
                    detections.append(
                        {
                            "raw_label": label_text,
                            "canonical_component": canonical,
                            "bbox_xyxy": [float(v) for v in box.tolist()],
                            "confidence": float(score),
                            "detector_group": detector_group,
                            "backend": model_id,
                        }
                    )
        records.append({**base, "backend": "open_vocab_rgb", "detections": detections})
    return records


def run_detector_for_clip(
    manifest_df: pd.DataFrame,
    *,
    clip_dir: Path,
    part_catalog: dict[str, Any],
    state_catalog: dict[str, Any],
    cfg: dict[str, Any],
    backend: str | None = None,
    include_error_step_hints: bool = True,
) -> list[dict[str, Any]]:
    detector_backend = backend or str(cfg["detector"]["default_backend"])
    context = DetectorContext(part_catalog=part_catalog, state_catalog=state_catalog, config=cfg)
    if detector_backend == "oracle_od":
        return oracle_od_records(
            manifest_df,
            clip_dir=clip_dir,
            context=context,
            include_error_step_hints=include_error_step_hints,
        )
    if detector_backend == "open_vocab_rgb":
        return open_vocab_records(manifest_df, context=context)
    raise ValueError(f"unknown detector backend: {detector_backend}")
