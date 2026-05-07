"""CAD-grounded state reasoning over smoothed per-frame component evidence."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from .psr import convert_states_to_steps, state_string_to_list
from .raw_loader import frame_name_to_idx, load_od_labels, load_step_labels_csv


def _component_keys_for_state(state_name: str, state_catalog: dict[str, Any]) -> list[str]:
    for item in state_catalog["states"]:
        if str(item["state_name"]) == state_name:
            return list(item.get("component_keys", []))
    return []


def _state_name_to_vector(state_name: str) -> list[int] | None:
    if state_name == "background":
        return [0] * 11
    if state_name == "error_state":
        return None
    return state_string_to_list(state_name)


def _score_start_frame_from_rows(rows: list[dict[str, Any]]) -> int | None:
    for row in rows:
        if str(row.get("state_origin", "")) != "seeded_initial_state":
            return int(row["frame_idx"])
    return None


def _is_error_like_step(description: str) -> bool:
    text = description.strip().lower()
    return text.startswith("incorrectly") or text.startswith("remove")


def _oracle_error_step_hints(clip_dir: Path) -> dict[int, list[dict[str, Any]]]:
    hints: dict[int, list[dict[str, Any]]] = {}
    rows = load_step_labels_csv(clip_dir / "PSR_labels_with_errors.csv")
    if not rows:
        return hints
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(int(row["frame_idx"]), []).append(
            {
                "frame": int(row["frame_idx"]),
                "id": int(row["id"]),
                "description": str(row["description"]),
                "conf": 1.0,
            }
        )
    for frame_idx, frame_rows in grouped.items():
        if any(_is_error_like_step(str(row["description"])) for row in frame_rows):
            hints[frame_idx] = frame_rows
    return hints


def oracle_state_sequence_from_labels(
    manifest_rows: list[dict[str, Any]],
    *,
    clip_dir: Path,
    state_catalog: dict[str, Any],
    include_error_step_hints: bool = True,
) -> list[dict[str, Any]]:
    manifest_rows = sorted(manifest_rows, key=lambda item: int(item["frame_idx"]))
    if not manifest_rows:
        return []

    od_labels = load_od_labels(clip_dir / "OD_labels.json")
    error_step_hints = _oracle_error_step_hints(clip_dir) if include_error_step_hints else {}
    anchors = sorted(
        (frame_name_to_idx(frame_name), str(payload["state_name"]))
        for frame_name, payload in od_labels.items()
    )
    anchor_by_frame = {frame_idx: state_name for frame_idx, state_name in anchors}
    slice_start = int(manifest_rows[0]["frame_idx"])
    last_past_anchor: tuple[int, str] | None = None
    for frame_idx, state_name in anchors:
        if frame_idx <= slice_start:
            last_past_anchor = (frame_idx, state_name)
        else:
            break

    first_future_anchor: tuple[int, str] | None = None
    first_future_non_background: tuple[int, str] | None = None
    for frame_idx, state_name in anchors:
        if frame_idx < slice_start:
            continue
        if first_future_anchor is None:
            first_future_anchor = (frame_idx, state_name)
        if state_name != "background":
            first_future_non_background = (frame_idx, state_name)
            break

    seeded_until_frame: int | None = None
    if last_past_anchor is not None and str(last_past_anchor[1]) != "background":
        current_state = str(last_past_anchor[1])
    elif first_future_non_background is not None:
        current_state = str(first_future_non_background[1])
        seeded_until_frame = int(first_future_non_background[0])
    elif last_past_anchor is not None:
        current_state = str(last_past_anchor[1])
    elif first_future_anchor is not None:
        current_state = str(first_future_anchor[1])
        seeded_until_frame = int(first_future_anchor[0])
    else:
        current_state = "background"

    outputs: list[dict[str, Any]] = []
    for row in manifest_rows:
        frame_idx = int(row["frame_idx"])
        frame_name = str(row["frame_name"])
        observed_state = anchor_by_frame.get(frame_idx)
        if observed_state is not None:
            current_state = observed_state
            base_state_origin = "observed_label"
        elif seeded_until_frame is not None and frame_idx < seeded_until_frame:
            base_state_origin = "seeded_initial_state"
        else:
            base_state_origin = "carried_forward_state"

        step_hints = error_step_hints.get(frame_idx, [])
        if step_hints:
            state_name = "error_state"
            state_origin = "inferred_error_state"
            reason_flags = [base_state_origin, "explicit_error_step_label", "inferred_error_state"]
            dominant = _component_keys_for_state(current_state, state_catalog)
            state_conf = 1.0
        else:
            state_name = current_state
            state_origin = base_state_origin
            reason_flags = [state_origin]
            if state_name == "error_state" and state_origin != "observed_label":
                reason_flags.append("inferred_error_state")
            state_conf = (
                1.0
                if state_origin == "observed_label"
                else 0.97
                if state_origin == "carried_forward_state"
                else 0.9
            )
            dominant = _component_keys_for_state(state_name, state_catalog)
        outputs.append(
            {
                "clip": row["clip"],
                "frame_idx": frame_idx,
                "predicted_state": state_name,
                "state_conf": state_conf,
                "top_k_states": json.dumps([[state_name, state_conf]]),
                "dominant_components": json.dumps(dominant),
                "reason_flags": json.dumps(reason_flags),
                "state_origin": state_origin,
                "base_state_origin": base_state_origin,
                "base_state_name": current_state,
                "oracle_step_hints": json.dumps(step_hints),
                "frame_name": frame_name,
                "source_label_frame_idx": frame_idx if observed_state is not None else "",
            }
        )
    return outputs


def direct_transition_steps_from_state_sequence(
    rows: list[dict[str, Any]],
    *,
    proc_info: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda item: int(item["frame_idx"]))
    if not ordered:
        return []
    steps: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str]] = set()
    prev_state_name = str(ordered[0]["predicted_state"])
    for row in ordered:
        step_hints = row.get("oracle_step_hints", "[]")
        if isinstance(step_hints, str):
            try:
                hinted_steps = json.loads(step_hints)
            except json.JSONDecodeError:
                hinted_steps = []
        else:
            hinted_steps = list(step_hints or [])
        for hint in hinted_steps:
            key = (int(hint["frame"]), int(hint["id"]), str(hint["description"]))
            if key in seen:
                continue
            steps.append(
                {
                    "frame": int(hint["frame"]),
                    "id": int(hint["id"]),
                    "description": str(hint["description"]),
                    "conf": float(hint.get("conf", 1.0)),
                }
            )
            seen.add(key)
    for row in ordered[1:]:
        state_name = str(row["predicted_state"])
        if state_name == prev_state_name:
            continue
        prev_vec = _state_name_to_vector(prev_state_name)
        next_vec = _state_name_to_vector(state_name)
        if prev_vec is None or next_vec is None:
            prev_state_name = state_name
            continue
        actions, _ = convert_states_to_steps(
            prev_vec,
            next_vec,
            int(row["frame_idx"]),
            proc_info,
            conf=1.0,
        )
        for action in actions:
            key = (int(action["frame"]), int(action["id"]), str(action["description"]))
            if key in seen:
                continue
            steps.append(action)
            seen.add(key)
        prev_state_name = state_name
    steps.sort(key=lambda item: (int(item["frame"]), int(item["id"])))
    return steps


def filter_steps_to_scored_slice(
    gt_steps: list[dict[str, Any]],
    *,
    state_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int | None]:
    if not state_rows:
        return [], None
    frame_set = {int(row["frame_idx"]) for row in state_rows}
    score_start = _score_start_frame_from_rows(state_rows)
    filtered = []
    for row in gt_steps:
        frame = int(row["frame"])
        if frame not in frame_set:
            continue
        if score_start is not None and frame < score_start:
            continue
        filtered.append(row)
    return filtered, score_start

def component_scores_from_detections(
    detections: list[dict[str, Any]],
    *,
    component_order: list[str],
    floor: float,
) -> tuple[dict[str, float], list[str]]:
    scores = {key: float(floor) for key in component_order}
    flags: list[str] = []
    for det in detections:
        component = str(det.get("canonical_component"))
        if component == "__error__":
            flags.append("explicit_error_detection")
            continue
        if component not in scores:
            continue
        score = float(det.get("smoothed_confidence", det.get("confidence", 0.0)))
        scores[component] = max(scores[component], score)
    return scores, sorted(set(flags))


def _score_background(component_scores: dict[str, float]) -> float:
    max_presence = max(component_scores.values()) if component_scores else 0.0
    return max(0.0, 1.0 - max_presence)


def _score_legal_state(
    component_scores: dict[str, float],
    *,
    state_components: set[str],
    component_order: list[str],
) -> float:
    if not component_order:
        return 0.0
    terms = []
    for key in component_order:
        presence = float(component_scores[key])
        if key in state_components:
            terms.append(presence)
        else:
            terms.append(1.0 - presence)
    raw = sum(terms) / len(terms)
    return max(0.0, min(1.0, raw))


def _observation_scores_for_frame(
    component_scores: dict[str, float],
    *,
    state_catalog: dict[str, Any],
    min_non_error_conf: float,
    flags: list[str],
) -> tuple[dict[str, float], dict[str, float], list[str]]:
    component_order = list(state_catalog["component_order"])
    scores: dict[str, float] = {}
    legal_scores: dict[str, float] = {}
    for state in state_catalog["states"]:
        state_name = str(state["state_name"])
        if state_name == "background":
            scores[state_name] = _score_background(component_scores)
            continue
        if state_name == "error_state":
            continue
        legal_score = _score_legal_state(
            component_scores,
            state_components=set(state["component_keys"]),
            component_order=component_order,
        )
        scores[state_name] = legal_score
        legal_scores[state_name] = legal_score
    best_non_error = max(legal_scores.values()) if legal_scores else 0.0
    has_component_evidence = max(component_scores.values()) > 0.05 if component_scores else False
    explicit_error = "explicit_error_detection" in flags
    if explicit_error:
        flags = flags + ["forced_error_state"]
        scores["error_state"] = max(0.8, 1.0 - best_non_error * 0.25)
    elif has_component_evidence and best_non_error < float(min_non_error_conf):
        flags = flags + ["low_non_error_conf"]
        scores["error_state"] = min(1.0, 0.55 + (float(min_non_error_conf) - best_non_error))
    else:
        scores["error_state"] = 0.0
    return scores, legal_scores, sorted(set(flags))


def _transition_bonus(
    prev_state: str,
    next_state: str,
    *,
    transitions: dict[str, list[str]],
    weights: dict[str, float],
) -> float:
    allowed = set(transitions.get(prev_state, []))
    if next_state not in allowed:
        return -1e9
    if prev_state == next_state:
        return float(weights["stay"])
    if next_state == "error_state":
        return float(weights["error_entry"])
    if prev_state == "error_state":
        return float(weights["error_exit"])
    if prev_state == "background" or next_state == "background":
        return 0.0
    return float(weights["observed"])


def reason_state_sequence(
    frame_records: list[dict[str, Any]],
    *,
    state_catalog: dict[str, Any],
    cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    component_order = list(state_catalog["component_order"])
    state_names = [str(item["state_name"]) for item in state_catalog["states"]]
    transitions = dict(state_catalog["transitions"])
    min_non_error_conf = float(cfg["reasoner"]["min_non_error_conf"])
    floor = float(cfg["reasoner"]["component_presence_floor"])
    weights = dict(cfg["reasoner"]["transition_weights"])

    observations: list[dict[str, Any]] = []
    for frame in sorted(frame_records, key=lambda item: int(item["frame_idx"])):
        component_scores, flags = component_scores_from_detections(
            list(frame.get("detections", [])),
            component_order=component_order,
            floor=floor,
        )
        scores, _, reason_flags = _observation_scores_for_frame(
            component_scores,
            state_catalog=state_catalog,
            min_non_error_conf=min_non_error_conf,
            flags=flags,
        )
        logits = [scores.get(state_name, 0.0) for state_name in state_names]
        exp_values = [math.exp(value) for value in logits]
        denom = sum(exp_values) or 1.0
        norm = {state: exp_values[idx] / denom for idx, state in enumerate(state_names)}
        observations.append(
            {
                "frame": frame,
                "component_scores": component_scores,
                "obs_scores": scores,
                "norm_scores": norm,
                "reason_flags": reason_flags,
                "has_component_evidence": max(component_scores.values()) > 0.05 if component_scores else False,
            }
        )

    dp: list[dict[str, float]] = []
    backptr: list[dict[str, str]] = []
    for index, obs in enumerate(observations):
        current_scores: dict[str, float] = {}
        current_backptr: dict[str, str] = {}
        for state_name in state_names:
            obs_score = float(obs["obs_scores"].get(state_name, 0.0))
            if index == 0:
                current_scores[state_name] = obs_score
                current_backptr[state_name] = ""
                continue
            best_score = -1e18
            best_prev = state_names[0]
            for prev_state in state_names:
                transition = _transition_bonus(
                    prev_state,
                    state_name,
                    transitions=transitions,
                    weights=weights,
                )
                score = dp[index - 1][prev_state] + transition + obs_score
                if score > best_score:
                    best_score = score
                    best_prev = prev_state
            current_scores[state_name] = best_score
            current_backptr[state_name] = best_prev
        dp.append(current_scores)
        backptr.append(current_backptr)

    terminal_state = max(dp[-1], key=dp[-1].get) if dp else "background"
    decoded: list[str] = []
    for index in reversed(range(len(observations))):
        decoded.append(terminal_state)
        terminal_state = backptr[index].get(terminal_state, "")
    decoded.reverse()

    stable_decoded: list[str] = []
    last_non_background = "background"
    for state_name, obs in zip(decoded, observations):
        final_state = state_name
        if (
            not obs["has_component_evidence"]
            and state_name == "background"
            and last_non_background != "background"
        ):
            final_state = last_non_background
            obs["reason_flags"] = sorted(set(obs["reason_flags"] + ["state_carry_forward"]))
        elif state_name != "background":
            last_non_background = state_name
        stable_decoded.append(final_state)

    top_k = int(cfg["reasoner"]["top_k_states"])
    outputs: list[dict[str, Any]] = []
    for obs, predicted_state in zip(observations, stable_decoded):
        sorted_states = sorted(
            obs["norm_scores"].items(),
            key=lambda item: item[1],
            reverse=True,
        )
        dominant = [
            key
            for key, value in sorted(
                obs["component_scores"].items(),
                key=lambda item: item[1],
                reverse=True,
            )
            if value > float(cfg["reasoner"]["component_presence_floor"])
        ][:5]
        frame = obs["frame"]
        outputs.append(
            {
                "clip": frame["clip"],
                "frame_idx": int(frame["frame_idx"]),
                "predicted_state": predicted_state,
                "state_conf": float(obs["norm_scores"].get(predicted_state, 0.0)),
                "top_k_states": json.dumps(sorted_states[:top_k]),
                "dominant_components": json.dumps(dominant),
                "reason_flags": json.dumps(obs["reason_flags"]),
            }
        )
    return outputs


def save_state_sequence(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        out_path.write_text("")
        return
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_state_sequence(path: Path) -> list[dict[str, Any]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def state_sequence_to_asd_frames(
    rows: list[dict[str, Any]],
    *,
    state_catalog: dict[str, Any],
) -> list[list[Any]]:
    state_to_idx = {
        str(item["state_name"]): int(item["state_index"])
        for item in state_catalog["states"]
    }
    if not rows:
        return []
    max_frame = max(int(row["frame_idx"]) for row in rows)
    frames: list[list[Any]] = [[] for _ in range(max_frame + 1)]
    for row in rows:
        frame_idx = int(row["frame_idx"])
        frames[frame_idx] = [
            [
                state_to_idx[str(row["predicted_state"])],
                float(row["state_conf"]),
                [0.0, 0.0, 0.0, 0.0],
            ]
        ]
    return frames
