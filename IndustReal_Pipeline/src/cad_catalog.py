"""Build the CAD-backed component/state catalog for the raw pilot."""
from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from typing import Any

from . import psr


def load_procedure_info(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def component_definitions_from_cfg(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    components = list(cfg["cad"]["components"])
    components.sort(key=lambda item: int(item["state_bit_index"]))
    return components


def detector_vocabulary(cfg: dict[str, Any]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for item in component_definitions_from_cfg(cfg) + list(cfg["cad"].get("context_components", [])):
        group = str(item["detector_group"])
        groups.setdefault(group, [])
        for phrase in item.get("prompts", []):
            if phrase not in groups[group]:
                groups[group].append(phrase)
    return groups


def _state_to_components(state_name: str, components: list[dict[str, Any]]) -> list[str]:
    if state_name in ("background", "error_state"):
        return []
    active: list[str] = []
    for item in components:
        bit_idx = int(item["state_bit_index"])
        if bit_idx < len(state_name) and state_name[bit_idx] == "1":
            active.append(str(item["key"]))
    return active


def _read_gt_state_sequences(asd_results_zip: Path) -> dict[str, list[str]]:
    clip_sequences: dict[str, list[str]] = {}
    with zipfile.ZipFile(asd_results_zip) as zf:
        for name in sorted(zf.namelist()):
            if not name.endswith("_results_gt.csv"):
                continue
            with zf.open(name) as f:
                reader = csv.DictReader((line.decode() for line in f))
                frame_to_class: dict[int, int] = {}
                clip_name = None
                for row in reader:
                    clip_name = row["clip"]
                    frame = int(row["framenr"])
                    cls = int(row["bb_class"])
                    frame_to_class.setdefault(frame, cls)
                if clip_name is None:
                    continue
                state_sequence = [psr.CATEGORIES[frame_to_class[idx]] for idx in sorted(frame_to_class)]
                clip_sequences[clip_name] = state_sequence
    return clip_sequences


def build_transition_graph(asd_results_zip: Path) -> dict[str, Any]:
    transitions: dict[str, set[str]] = {name: {name} for name in psr.CATEGORIES}
    observed_forward: set[tuple[str, str]] = set()
    clip_sequences = _read_gt_state_sequences(asd_results_zip)
    for sequence in clip_sequences.values():
        prev = None
        for state_name in sequence:
            if prev is None:
                prev = state_name
                continue
            if state_name == prev:
                continue
            transitions.setdefault(prev, {prev}).add(state_name)
            observed_forward.add((prev, state_name))
            prev = state_name
    for src, dst in observed_forward:
        if src not in ("background", "error_state") and dst not in ("background", "error_state"):
            transitions.setdefault(dst, {dst}).add(src)
    for state_name in psr.CATEGORIES:
        transitions.setdefault("background", {"background"}).add(state_name)
        transitions.setdefault(state_name, {state_name}).add("background")
        if state_name != "error_state":
            transitions.setdefault(state_name, {state_name}).add("error_state")
            transitions.setdefault("error_state", {"error_state"}).add(state_name)
    return {
        key: sorted(values)
        for key, values in sorted(transitions.items(), key=lambda item: psr.CATEGORIES.index(item[0]))
    }


def build_cad_part_catalog(cfg: dict[str, Any], *, part_geometries_zip: Path | None) -> dict[str, Any]:
    components = component_definitions_from_cfg(cfg)
    asset_families = dict(cfg["cad"]["asset_families"])
    zip_members: set[str] = set()
    if part_geometries_zip is not None and part_geometries_zip.exists():
        with zipfile.ZipFile(part_geometries_zip) as zf:
            zip_members = set(zf.namelist())
    component_entries = []
    for item in components:
        family_key = str(item["asset_family"])
        family_member = f"part_geometries/{asset_families[family_key]}"
        component_entries.append(
            {
                "key": item["key"],
                "display_name": item["display_name"],
                "state_bit_index": int(item["state_bit_index"]),
                "detector_group": item["detector_group"],
                "prompts": list(item.get("prompts", [])),
                "aliases": list(item.get("aliases", [])),
                "asset_family": family_key,
                "asset_member": family_member if family_member in zip_members else None,
            }
        )
    return {
        "components": component_entries,
        "context_components": list(cfg["cad"].get("context_components", [])),
        "detector_vocabulary": detector_vocabulary(cfg),
        "asset_families": {
            key: {
                "member": f"part_geometries/{value}",
                "present": f"part_geometries/{value}" in zip_members,
            }
            for key, value in asset_families.items()
        },
        "available_state_assets": [
            name for name in sorted(zip_members)
            if name.startswith("part_geometries/state") and name.endswith(".fbx")
        ],
        "overview_pdf": "part_geometries/Overview of states.pdf"
        if "part_geometries/Overview of states.pdf" in zip_members
        else None,
    }


def build_state_catalog(
    cfg: dict[str, Any],
    *,
    procedure_info: list[dict[str, Any]],
    asd_results_zip: Path,
) -> dict[str, Any]:
    components = component_definitions_from_cfg(cfg)
    transitions = build_transition_graph(asd_results_zip)
    states: list[dict[str, Any]] = []
    for state_index, state_name in enumerate(psr.CATEGORIES):
        component_keys = _state_to_components(state_name, components)
        state_entry = {
            "state_index": state_index,
            "state_name": state_name,
            "kind": (
                "background"
                if state_name == "background"
                else "error"
                if state_name == "error_state"
                else "legal"
            ),
            "component_keys": component_keys,
            "component_bits": [
                1 if item["key"] in component_keys else 0
                for item in components
            ],
            "state_asset_member": (
                f"part_geometries/{cfg['cad']['state_asset_pattern'].format(index=state_index)}"
                if 1 <= state_index <= 22
                else None
            ),
        }
        states.append(state_entry)
    step_lookup = {int(step["id"]): step for step in procedure_info}
    return {
        "component_order": [item["key"] for item in components],
        "components": components,
        "states": states,
        "transitions": transitions,
        "procedure_steps": step_lookup,
    }


def save_cad_artifacts(
    out_dir: Path,
    *,
    part_catalog: dict[str, Any],
    state_catalog: dict[str, Any],
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    part_path = out_dir / "cad_part_catalog.json"
    state_path = out_dir / "cad_state_catalog.json"
    part_path.write_text(json.dumps(part_catalog, indent=2))
    state_path.write_text(json.dumps(state_catalog, indent=2))
    return part_path, state_path


def load_cad_artifacts(cad_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    part_catalog = json.loads((cad_dir / "cad_part_catalog.json").read_text())
    state_catalog = json.loads((cad_dir / "cad_state_catalog.json").read_text())
    return part_catalog, state_catalog
