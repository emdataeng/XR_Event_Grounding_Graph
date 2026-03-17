"""Event window detection and summary generation."""
from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import json
import uuid
import numpy as np
import pandas as pd
from src.geometry import spatial_relation


EVENT_TYPES = [
    "APPEAR", "DISAPPEAR", "MOVE", "PLACE",
    "CO_LOCATE", "SEPARATE", "INTERACTION",
    "ALIGN_CANDIDATE", "ATTACH_CANDIDATE",
    "STATE_CHANGE_CANDIDATE", "ASSEMBLY_CHANGE_CANDIDATE",
    "USE_TOOL_CANDIDATE", "INSPECT",
]


def detect_event_windows(
    tracks_df: pd.DataFrame,
    min_move_distance_m: float = 0.05,
    near_threshold_m: float = 0.3,
    disappear_frames: int = 3,
    event_merge_gap_ns: int = 2_000_000_000,
    room_id: str = "workstation_A",
) -> pd.DataFrame:
    """Detect coarse event windows from object track data.

    Logic:
    - APPEAR: first observation of a track
    - DISAPPEAR: last observation of a track (if followed by silence)
    - MOVE: track position changes more than threshold between consecutive obs
    - CO_LOCATE: two tracks come within near_threshold of each other
    - SEPARATE: two tracks that were near move apart

    Returns event_windows DataFrame.
    """
    events = []
    event_counter = [0]

    def eid() -> str:
        event_counter[0] += 1
        return f"evt_{event_counter[0]:04d}"

    # ---- Per-track events (APPEAR, DISAPPEAR, MOVE) ----
    for tid, grp in tracks_df.groupby("track_id"):
        grp_s = grp.sort_values("timestamp_ns").reset_index(drop=True)

        # APPEAR
        first = grp_s.iloc[0]
        events.append({
            "event_id": eid(),
            "event_type": "APPEAR",
            "start_frame_idx": int(first["frame_idx"]),
            "end_frame_idx": int(first["frame_idx"]),
            "start_ts_ns": int(first["timestamp_ns"]),
            "end_ts_ns": int(first["timestamp_ns"]),
            "primary_track_ids": json.dumps([tid]),
            "room_id": room_id,
            "trigger_reason": "first observation of track",
            "confidence": 0.9,
        })

        # DISAPPEAR
        last = grp_s.iloc[-1]
        if len(grp_s) > 1:
            events.append({
                "event_id": eid(),
                "event_type": "DISAPPEAR",
                "start_frame_idx": int(last["frame_idx"]),
                "end_frame_idx": int(last["frame_idx"]),
                "start_ts_ns": int(last["timestamp_ns"]),
                "end_ts_ns": int(last["timestamp_ns"]),
                "primary_track_ids": json.dumps([tid]),
                "room_id": room_id,
                "trigger_reason": "last observation of track",
                "confidence": 0.7,
            })

        # MOVE events between consecutive observations
        for i in range(1, len(grp_s)):
            prev = grp_s.iloc[i - 1]
            curr = grp_s.iloc[i]
            p0 = np.array([prev["x"], prev["y"], prev["z"]], dtype=float)
            p1 = np.array([curr["x"], curr["y"], curr["z"]], dtype=float)
            if np.any(np.isnan(p0)) or np.any(np.isnan(p1)):
                continue
            dist = np.linalg.norm(p1 - p0)
            if dist >= min_move_distance_m:
                events.append({
                    "event_id": eid(),
                    "event_type": "MOVE",
                    "start_frame_idx": int(prev["frame_idx"]),
                    "end_frame_idx": int(curr["frame_idx"]),
                    "start_ts_ns": int(prev["timestamp_ns"]),
                    "end_ts_ns": int(curr["timestamp_ns"]),
                    "primary_track_ids": json.dumps([tid]),
                    "room_id": room_id,
                    "trigger_reason": f"displacement {dist:.3f}m > {min_move_distance_m}m",
                    "confidence": min(1.0, 0.5 + dist),
                })

    # ---- Pairwise events (CO_LOCATE, SEPARATE) ----
    track_ids = tracks_df["track_id"].unique().tolist()
    for i, tid_a in enumerate(track_ids):
        for tid_b in track_ids[i + 1:]:
            grp_a = tracks_df[tracks_df["track_id"] == tid_a].sort_values("timestamp_ns")
            grp_b = tracks_df[tracks_df["track_id"] == tid_b].sort_values("timestamp_ns")

            # Find common frame indices
            frames_a = set(grp_a["frame_idx"].tolist())
            frames_b = set(grp_b["frame_idx"].tolist())
            common = sorted(frames_a & frames_b)
            if len(common) < 2:
                continue

            was_near = False
            for frame in common:
                row_a = grp_a[grp_a["frame_idx"] == frame].iloc[0]
                row_b = grp_b[grp_b["frame_idx"] == frame].iloc[0]
                p_a = np.array([row_a["x"], row_a["y"], row_a["z"]], dtype=float)
                p_b = np.array([row_b["x"], row_b["y"], row_b["z"]], dtype=float)
                if np.any(np.isnan(p_a)) or np.any(np.isnan(p_b)):
                    continue
                now_near = np.linalg.norm(p_b - p_a) <= near_threshold_m

                if was_near is False and now_near:
                    ts_a = int(row_a["timestamp_ns"])
                    events.append({
                        "event_id": eid(),
                        "event_type": "CO_LOCATE",
                        "start_frame_idx": frame, "end_frame_idx": frame,
                        "start_ts_ns": ts_a, "end_ts_ns": ts_a,
                        "primary_track_ids": json.dumps([tid_a, tid_b]),
                        "room_id": room_id,
                        "trigger_reason": f"objects came within {near_threshold_m}m",
                        "confidence": 0.7,
                    })
                elif was_near is True and not now_near:
                    ts_a = int(row_a["timestamp_ns"])
                    events.append({
                        "event_id": eid(),
                        "event_type": "SEPARATE",
                        "start_frame_idx": frame, "end_frame_idx": frame,
                        "start_ts_ns": ts_a, "end_ts_ns": ts_a,
                        "primary_track_ids": json.dumps([tid_a, tid_b]),
                        "room_id": room_id,
                        "trigger_reason": f"objects moved apart beyond {near_threshold_m}m",
                        "confidence": 0.7,
                    })
                was_near = now_near

    # ---- INTERACTION events (hands near non-hands object) ----
    hands_tids = set(
        tracks_df.loc[tracks_df["semantic_class"] == "hands", "track_id"].tolist()
    )
    for htid in hands_tids:
        h_grp = tracks_df[tracks_df["track_id"] == htid].sort_values("timestamp_ns")
        h_frames = set(h_grp["frame_idx"].tolist())

        for oid in tracks_df["track_id"].unique():
            if oid == htid:
                continue
            o_class = str(tracks_df.loc[tracks_df["track_id"] == oid, "semantic_class"].iloc[0])
            if o_class == "hands":
                continue

            o_grp = tracks_df[tracks_df["track_id"] == oid].sort_values("timestamp_ns")
            common = sorted(h_frames & set(o_grp["frame_idx"].tolist()))
            if len(common) < 2:
                continue

            was_interacting = False
            interact_start_frame = None
            interact_start_ts = None

            for frame in common:
                row_h = h_grp[h_grp["frame_idx"] == frame].iloc[0]
                row_o = o_grp[o_grp["frame_idx"] == frame].iloc[0]
                p_h = np.array([row_h["x"], row_h["y"], row_h["z"]], dtype=float)
                p_o = np.array([row_o["x"], row_o["y"], row_o["z"]], dtype=float)
                if np.any(np.isnan(p_h)) or np.any(np.isnan(p_o)):
                    continue
                now_near = np.linalg.norm(p_o - p_h) <= near_threshold_m

                if not was_interacting and now_near:
                    interact_start_frame = frame
                    interact_start_ts = int(row_h["timestamp_ns"])
                    was_interacting = True
                elif was_interacting and not now_near:
                    events.append({
                        "event_id": eid(),
                        "event_type": "INTERACTION",
                        "start_frame_idx": interact_start_frame,
                        "end_frame_idx": frame,
                        "start_ts_ns": interact_start_ts,
                        "end_ts_ns": int(row_h["timestamp_ns"]),
                        "primary_track_ids": json.dumps([htid, oid]),
                        "room_id": room_id,
                        "trigger_reason": f"hands near {o_class} for {frame - interact_start_frame} frames",
                        "confidence": 0.8,
                    })
                    was_interacting = False
                    interact_start_frame = None
                    interact_start_ts = None

            # Close any open interaction window at end of track overlap
            if was_interacting and interact_start_frame is not None:
                last_frame = common[-1]
                last_row = h_grp[h_grp["frame_idx"] == last_frame].iloc[0]
                events.append({
                    "event_id": eid(),
                    "event_type": "INTERACTION",
                    "start_frame_idx": interact_start_frame,
                    "end_frame_idx": last_frame,
                    "start_ts_ns": interact_start_ts,
                    "end_ts_ns": int(last_row["timestamp_ns"]),
                    "primary_track_ids": json.dumps([htid, oid]),
                    "room_id": room_id,
                    "trigger_reason": f"hands near {o_class} for {last_frame - interact_start_frame} frames (until track end)",
                    "confidence": 0.8,
                })

    if not events:
        return pd.DataFrame(columns=[
            "event_id", "event_type", "start_frame_idx", "end_frame_idx",
            "start_ts_ns", "end_ts_ns", "primary_track_ids",
            "room_id", "trigger_reason", "confidence",
        ])

    df = pd.DataFrame(events).sort_values("start_ts_ns").reset_index(drop=True)
    return df


# ---------- Templates for rule-based summaries ----------

_TEMPLATES: Dict[str, str] = {
    "APPEAR": "{class_a} appeared at ({x:.2f}, {y:.2f}, {z:.2f}).",
    "DISAPPEAR": "{class_a} disappeared from ({x:.2f}, {y:.2f}, {z:.2f}).",
    "MOVE": "{class_a} moved from ({x0:.2f},{y0:.2f},{z0:.2f}) to ({x1:.2f},{y1:.2f},{z1:.2f}) (dist {dist:.2f}m). {spatial_ctx}",
    "CO_LOCATE": "{class_a} and {class_b} came within {near_dist:.2f}m of each other ({relation}).",
    "SEPARATE": "{class_a} and {class_b} moved apart (now {near_dist:.2f}m, previously proximate).",
    "INTERACTION": "User's hands interacted with {class_b} at ({x:.2f},{y:.2f},{z:.2f}): {class_b} was {relation} during contact.",
    "PLACE": "{class_a} was placed near ({x:.2f},{y:.2f},{z:.2f}).",
    "ALIGN_CANDIDATE": "{class_a} aligned with {class_b}.",
    "ATTACH_CANDIDATE": "{class_a} may have attached to {class_b}.",
    "STATE_CHANGE_CANDIDATE": "{class_a} may have changed state.",
    "ASSEMBLY_CHANGE_CANDIDATE": "Assembly state changed near {class_a}.",
    "USE_TOOL_CANDIDATE": "{class_a} was used as a tool near {class_b}.",
    "INSPECT": "{class_a} was inspected.",
}

_ROLES: Dict[str, List[str]] = {
    "APPEAR": ["appearing_object"],
    "DISAPPEAR": ["disappearing_object"],
    "MOVE": ["moving_object"],
    "CO_LOCATE": ["co_located_object", "co_located_object"],
    "SEPARATE": ["separating_object", "separating_object"],
    "INTERACTION": ["interacting_hand", "target_object"],
    "PLACE": ["placed_object"],
    "ALIGN_CANDIDATE": ["aligned_object", "reference_object"],
    "ATTACH_CANDIDATE": ["attaching_object", "target_object"],
    "STATE_CHANGE_CANDIDATE": ["changed_object"],
    "ASSEMBLY_CHANGE_CANDIDATE": ["assembly_object"],
    "USE_TOOL_CANDIDATE": ["tool_object", "target_object"],
    "INSPECT": ["inspected_object"],
}


def generate_event_summary(
    event_row: pd.Series,
    tracks_df: pd.DataFrame,
) -> Tuple[str, list]:
    """Return (summary_text, list_of_role_dicts) for a single event."""
    etype = event_row["event_type"]
    track_ids = json.loads(event_row["primary_track_ids"])
    template = _TEMPLATES.get(etype, "{class_a} was involved in {etype} event.")
    roles = _ROLES.get(etype, ["primary_object"] * len(track_ids))

    # Look up track info
    info = []
    for tid in track_ids:
        t_rows = tracks_df[tracks_df["track_id"] == tid]
        if t_rows.empty:
            info.append({"tid": tid, "class": "unknown", "x": 0, "y": 0, "z": 0,
                         "x0": 0, "y0": 0, "z0": 0, "x1": 0, "y1": 0, "z1": 0})
            continue
        first = t_rows.sort_values("timestamp_ns").iloc[0]
        last = t_rows.sort_values("timestamp_ns").iloc[-1]
        info.append({
            "tid": tid,
            "class": str(first["semantic_class"]),
            "x": float(last["x"]) if not pd.isna(last["x"]) else 0.0,
            "y": float(last["y"]) if not pd.isna(last["y"]) else 0.0,
            "z": float(last["z"]) if not pd.isna(last["z"]) else 0.0,
            "x0": float(first["x"]) if not pd.isna(first["x"]) else 0.0,
            "y0": float(first["y"]) if not pd.isna(first["y"]) else 0.0,
            "z0": float(first["z"]) if not pd.isna(first["z"]) else 0.0,
            "x1": float(last["x"]) if not pd.isna(last["x"]) else 0.0,
            "y1": float(last["y"]) if not pd.isna(last["y"]) else 0.0,
            "z1": float(last["z"]) if not pd.isna(last["z"]) else 0.0,
        })

    # Geometry-aware variables for enriched templates
    spatial_ctx = ""
    relation = "NEAR"
    near_dist = 0.0

    if etype == "MOVE" and info:
        dest = np.array([info[0]["x1"], info[0]["y1"], info[0]["z1"]], dtype=float)
        end_frame = event_row.get("end_frame_idx", None)
        if end_frame is not None:
            others = tracks_df[
                (tracks_df["track_id"] != track_ids[0]) &
                (tracks_df["frame_idx"] == end_frame)
            ]
            nearby = []
            for _, orow in others.iterrows():
                op = np.array([float(orow["x"]), float(orow["y"]), float(orow["z"])], dtype=float)
                if np.any(np.isnan(op)):
                    continue
                rel = spatial_relation(dest, op, threshold_m=0.5)
                if rel != "FAR":
                    nearby.append(f"{orow['semantic_class']} is {rel}")
            if nearby:
                spatial_ctx = "Now " + "; ".join(nearby[:2]) + "."

    elif etype in ("CO_LOCATE", "SEPARATE", "INTERACTION") and len(info) >= 2:
        p_a = np.array([info[0]["x"], info[0]["y"], info[0]["z"]], dtype=float)
        p_b = np.array([info[1]["x"], info[1]["y"], info[1]["z"]], dtype=float)
        if not (np.any(np.isnan(p_a)) or np.any(np.isnan(p_b))):
            near_dist = float(np.linalg.norm(p_b - p_a))
            relation = spatial_relation(p_a, p_b, threshold_m=0.5)

    fmt = {
        "etype": etype,
        "class_a": info[0]["class"] if info else "object",
        "class_b": info[1]["class"] if len(info) > 1 else "object",
        "x": info[0]["x"] if info else 0.0,
        "y": info[0]["y"] if info else 0.0,
        "z": info[0]["z"] if info else 0.0,
        "x0": info[0]["x0"] if info else 0.0,
        "y0": info[0]["y0"] if info else 0.0,
        "z0": info[0]["z0"] if info else 0.0,
        "x1": info[0]["x1"] if info else 0.0,
        "y1": info[0]["y1"] if info else 0.0,
        "z1": info[0]["z1"] if info else 0.0,
        "dist": float(np.linalg.norm([
            info[0]["x1"] - info[0]["x0"],
            info[0]["y1"] - info[0]["y0"],
            info[0]["z1"] - info[0]["z0"],
        ])) if info else 0.0,
        "spatial_ctx": spatial_ctx,
        "relation": relation,
        "near_dist": near_dist,
    }

    try:
        summary = template.format(**fmt)
    except (KeyError, IndexError):
        summary = f"{etype} event involving {', '.join(t['class'] for t in info)}."

    role_rows = []
    for i, (tid_info, role_label) in enumerate(zip(info, roles[:len(info)])):
        role_rows.append({
            "event_id": event_row["event_id"],
            "track_id": tid_info["tid"],
            "role": role_label,
            "role_description": f"{tid_info['class']} acted as {role_label.replace('_', ' ')} in {etype} event.",
        })

    return summary, role_rows
