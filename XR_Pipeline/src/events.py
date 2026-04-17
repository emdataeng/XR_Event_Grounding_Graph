"""Event window detection and summary generation."""
from __future__ import annotations
from typing import Any, List, Dict, Optional, Tuple
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
    position_smooth_window: int = 1,
    hand_classes: Optional[List[str]] = None,
    min_move_distance_by_role: Optional[Dict[str, float]] = None,
    min_2d_disp_px: float = 0.0,
) -> pd.DataFrame:
    """Detect coarse event windows from object track data.

    Parameters
    ----------
    tracks_df : pd.DataFrame
        object_tracks.csv — must contain at least track_id, frame_idx,
        timestamp_ns, x, y, z, semantic_class.  If an ``object_role``
        column is present it is used to identify hand-role tracks for
        INTERACTION detection; otherwise the legacy fallback (checking
        semantic_class == "hands") is used.
    hand_classes : list of str, optional
        Explicit list of canonical class names that carry the "hand" role.
        When provided, overrides any ``object_role`` column and the legacy
        fallback.  Pass ``vocab.classes_with_role("hand")`` from the caller.

    Logic:
    - APPEAR: first observation of a track
    - DISAPPEAR: last observation of a track (if followed by silence)
    - MOVE: track position changes more than threshold between consecutive obs
    - CO_LOCATE: two tracks come within near_threshold of each other
    - SEPARATE: two tracks that were near move apart
    - INTERACTION: hand-role track near a non-hand track

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

        # Smooth raw world positions to suppress depth/bbox noise before MOVE detection.
        # Uses a centred rolling mean; min_periods=1 keeps end observations.
        if position_smooth_window > 1:
            for col in ("x", "y", "z"):
                grp_s[col] = (
                    grp_s[col]
                    .rolling(window=position_smooth_window, center=True, min_periods=1)
                    .mean()
                )

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

        # Per-role MOVE threshold (falls back to global if role absent or unlisted)
        _role = None
        if "object_role" in grp_s.columns:
            _role = str(grp_s["object_role"].iloc[0])
        _move_thr = (
            min_move_distance_by_role.get(_role, min_move_distance_m)
            if min_move_distance_by_role and _role
            else min_move_distance_m
        )

        # Pre-check whether tracks_df has 2D bbox columns for fallback (B3)
        _has_2d_cols = min_2d_disp_px > 0 and all(
            c in grp_s.columns for c in ("bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2")
        )

        # MOVE events between consecutive observations
        for i in range(1, len(grp_s)):
            prev = grp_s.iloc[i - 1]
            curr = grp_s.iloc[i]
            p0 = np.array([prev["x"], prev["y"], prev["z"]], dtype=float)
            p1 = np.array([curr["x"], curr["y"], curr["z"]], dtype=float)
            if np.any(np.isnan(p0)) or np.any(np.isnan(p1)):
                continue
            dist = np.linalg.norm(p1 - p0)
            if dist >= _move_thr:
                events.append({
                    "event_id": eid(),
                    "event_type": "MOVE",
                    "start_frame_idx": int(prev["frame_idx"]),
                    "end_frame_idx": int(curr["frame_idx"]),
                    "start_ts_ns": int(prev["timestamp_ns"]),
                    "end_ts_ns": int(curr["timestamp_ns"]),
                    "primary_track_ids": json.dumps([tid]),
                    "room_id": room_id,
                    "trigger_reason": f"displacement {dist:.3f}m > {_move_thr}m (role={_role or 'unknown'})",
                    "confidence": min(1.0, 0.5 + dist),
                })
            elif _has_2d_cols:
                # B3: 3D below threshold — check 2D bbox center displacement as fallback.
                # Fires a supplementary MOVE at lower confidence when 2D signal is strong.
                try:
                    cx0 = (float(prev["bbox_x1"]) + float(prev["bbox_x2"])) / 2
                    cy0 = (float(prev["bbox_y1"]) + float(prev["bbox_y2"])) / 2
                    cx1 = (float(curr["bbox_x1"]) + float(curr["bbox_x2"])) / 2
                    cy1 = (float(curr["bbox_y1"]) + float(curr["bbox_y2"])) / 2
                    disp_2d = float(np.sqrt((cx1 - cx0) ** 2 + (cy1 - cy0) ** 2))
                except (TypeError, ValueError):
                    disp_2d = 0.0
                if disp_2d >= min_2d_disp_px:
                    events.append({
                        "event_id": eid(),
                        "event_type": "MOVE",
                        "start_frame_idx": int(prev["frame_idx"]),
                        "end_frame_idx": int(curr["frame_idx"]),
                        "start_ts_ns": int(prev["timestamp_ns"]),
                        "end_ts_ns": int(curr["timestamp_ns"]),
                        "primary_track_ids": json.dumps([tid]),
                        "room_id": room_id,
                        "trigger_reason": (
                            f"2D bbox displacement {disp_2d:.1f}px ≥ {min_2d_disp_px}px "
                            f"(3D {dist:.3f}m < threshold {_move_thr}m; role={_role or 'unknown'})"
                        ),
                        "confidence": min(0.55, 0.3 + disp_2d / 100.0),
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

    # ---- INTERACTION events (hand-role track near a non-hand object) ----
    # Resolution order:
    #   1. explicit hand_classes argument (vocab.classes_with_role("hand"))
    #   2. object_role column in tracks_df  (populated by script 06 when vocab has roles)
    #   3. legacy fallback: semantic_class == "hands"
    if hand_classes is not None:
        hand_class_set = set(hand_classes)
        hands_tids = set(
            tracks_df.loc[tracks_df["semantic_class"].isin(hand_class_set), "track_id"].tolist()
        )
    elif "object_role" in tracks_df.columns:
        hands_tids = set(
            tracks_df.loc[tracks_df["object_role"] == "hand", "track_id"].tolist()
        )
    else:
        # Legacy fallback — keeps pre-taxonomy sessions working
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
                        "trigger_reason": f"hand-role object near {o_class} for {frame - interact_start_frame} frames",
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
                    "trigger_reason": f"hand-role object near {o_class} for {last_frame - interact_start_frame} frames (until track end)",
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


# ── Motion diagnostics ────────────────────────────────────────────────────────

def compute_track_motion_debug(
    tracks_df: pd.DataFrame,
    min_move_distance_m: float = 0.05,
    min_move_distance_by_role: Optional[Dict[str, float]] = None,
    position_smooth_window: int = 1,
    obs_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Compute per-frame displacement statistics for each track.

    Returns a DataFrame useful for debugging why MOVE events did or did not
    fire.  Each row covers one observation (frame) of one track and includes:
      - raw and smoothed 3D positions
      - frame-to-frame displacement (smoothed)
      - the threshold that would apply given the track's role
      - whether that step would trigger a MOVE event
      - 2D bbox center and displacement (when obs_df with bbox columns is provided)

    Parameters
    ----------
    tracks_df :                 object_tracks.csv as a DataFrame.
    min_move_distance_m :       Global fallback threshold (same as detect_event_windows).
    min_move_distance_by_role : Per-role overrides (same dict as detect_event_windows).
    position_smooth_window :    Smoothing window (same as detect_event_windows).
    obs_df :                    object_observations.csv (optional).  When provided and
                                tracks_df has an ``observation_id`` column, bbox_x1/y1/x2/y2
                                are joined in and 2D motion columns are populated.
    """
    _EMPTY_COLS = [
        "track_id", "semantic_class", "object_role", "frame_idx", "timestamp_ns",
        "x_raw", "y_raw", "z_raw", "x_smooth", "y_smooth", "z_smooth",
        "displacement_m", "move_threshold_m", "would_fire_move", "below_threshold_by_m",
        # B3: 2D bbox motion columns (None when obs_df not available)
        "bbox_cx", "bbox_cy", "bbox_area_px", "bbox_disp_2d_px", "bbox_area_change_pct",
    ]
    if tracks_df is None or tracks_df.empty:
        return pd.DataFrame(columns=_EMPTY_COLS)

    # B3: Build (track_id, frame_idx) → (cx, cy, area_px) lookup from observations.
    # Requires tracks_df to have observation_id and obs_df to have bbox_x1/y1/x2/y2.
    _bbox_map: Dict[Tuple[str, int], Tuple] = {}
    _bbox_cols = {"bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2"}
    if (
        obs_df is not None
        and not obs_df.empty
        and _bbox_cols.issubset(obs_df.columns)
        and "observation_id" in tracks_df.columns
        and "observation_id" in obs_df.columns
    ):
        _obs_bbox = obs_df[["observation_id", "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2"]]
        _link = tracks_df[["track_id", "frame_idx", "observation_id"]].drop_duplicates()
        _merged = _link.merge(_obs_bbox, on="observation_id", how="left")
        for _, _r in _merged.iterrows():
            x1, y1 = _r.get("bbox_x1"), _r.get("bbox_y1")
            x2, y2 = _r.get("bbox_x2"), _r.get("bbox_y2")
            try:
                cx = float(x1 + x2) / 2 if x1 is not None and x2 is not None else None
                cy = float(y1 + y2) / 2 if y1 is not None and y2 is not None else None
                area = float((x2 - x1) * (y2 - y1)) if x1 is not None else None
                if cx is not None and np.isnan(cx): cx = None
                if cy is not None and np.isnan(cy): cy = None
                if area is not None and np.isnan(area): area = None
            except (TypeError, ValueError):
                cx = cy = area = None
            _bbox_map[(str(_r["track_id"]), int(_r["frame_idx"]))] = (cx, cy, area)

    rows = []
    for tid, grp in tracks_df.groupby("track_id"):
        grp_s = grp.sort_values("timestamp_ns").reset_index(drop=True)
        sem_class = str(grp_s["semantic_class"].iloc[0]) if "semantic_class" in grp_s.columns else "unknown"
        role = str(grp_s["object_role"].iloc[0]) if "object_role" in grp_s.columns else None

        # Raw positions
        xs_raw = grp_s["x"].values.astype(float)
        ys_raw = grp_s["y"].values.astype(float)
        zs_raw = grp_s["z"].values.astype(float)

        # Smoothed positions
        if position_smooth_window > 1:
            xs_sm = grp_s["x"].rolling(window=position_smooth_window, center=True, min_periods=1).mean().values.astype(float)
            ys_sm = grp_s["y"].rolling(window=position_smooth_window, center=True, min_periods=1).mean().values.astype(float)
            zs_sm = grp_s["z"].rolling(window=position_smooth_window, center=True, min_periods=1).mean().values.astype(float)
        else:
            xs_sm, ys_sm, zs_sm = xs_raw.copy(), ys_raw.copy(), zs_raw.copy()

        move_thr = (
            min_move_distance_by_role.get(role, min_move_distance_m)
            if min_move_distance_by_role and role
            else min_move_distance_m
        )

        for i in range(len(grp_s)):
            disp = None
            below_by = None
            if i > 0:
                p0 = np.array([xs_sm[i - 1], ys_sm[i - 1], zs_sm[i - 1]])
                p1 = np.array([xs_sm[i], ys_sm[i], zs_sm[i]])
                if not (np.any(np.isnan(p0)) or np.any(np.isnan(p1))):
                    disp = float(np.linalg.norm(p1 - p0))
                    below_by = move_thr - disp  # positive = still below threshold

            row = grp_s.iloc[i]
            frame = int(row["frame_idx"])
            tid_str = str(tid)

            # B3: 2D bbox metrics from lookup
            cx, cy, area = _bbox_map.get((tid_str, frame), (None, None, None))
            disp_2d = None
            area_chg = None
            if i > 0:
                cx_prev, cy_prev, area_prev = _bbox_map.get((tid_str, int(grp_s.iloc[i - 1]["frame_idx"])), (None, None, None))
                if cx is not None and cx_prev is not None and cy is not None and cy_prev is not None:
                    disp_2d = round(float(np.sqrt((cx - cx_prev) ** 2 + (cy - cy_prev) ** 2)), 2)
                if area is not None and area_prev is not None and area_prev > 0:
                    area_chg = round(float((area - area_prev) / area_prev * 100), 2)

            rows.append({
                "track_id":         tid_str,
                "semantic_class":   sem_class,
                "object_role":      role or "unknown",
                "frame_idx":        frame,
                "timestamp_ns":     int(row["timestamp_ns"]),
                "x_raw":            float(xs_raw[i]) if not np.isnan(xs_raw[i]) else None,
                "y_raw":            float(ys_raw[i]) if not np.isnan(ys_raw[i]) else None,
                "z_raw":            float(zs_raw[i]) if not np.isnan(zs_raw[i]) else None,
                "x_smooth":         float(xs_sm[i])  if not np.isnan(xs_sm[i])  else None,
                "y_smooth":         float(ys_sm[i])  if not np.isnan(ys_sm[i])  else None,
                "z_smooth":         float(zs_sm[i])  if not np.isnan(zs_sm[i])  else None,
                "displacement_m":   round(disp, 4) if disp is not None else None,
                "move_threshold_m": move_thr,
                "would_fire_move":  disp is not None and disp >= move_thr,
                "below_threshold_by_m": round(below_by, 4) if below_by is not None and below_by > 0 else None,
                # B3: 2D columns
                "bbox_cx":               round(cx,      2) if cx      is not None else None,
                "bbox_cy":               round(cy,      2) if cy      is not None else None,
                "bbox_area_px":          round(area,    1) if area    is not None else None,
                "bbox_disp_2d_px":       disp_2d,
                "bbox_area_change_pct":  area_chg,
            })

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=_EMPTY_COLS)


# ---------- Templates for rule-based summaries ----------

_TEMPLATES: Dict[str, str] = {
    "APPEAR": "{class_a} appeared at ({x:.2f}, {y:.2f}, {z:.2f}).",
    "DISAPPEAR": "{class_a} disappeared from ({x:.2f}, {y:.2f}, {z:.2f}).",
    "MOVE": "{class_a} moved from ({x0:.2f},{y0:.2f},{z0:.2f}) to ({x1:.2f},{y1:.2f},{z1:.2f}) (dist {dist:.2f}m). {spatial_ctx}",
    "CO_LOCATE": "{class_a} and {class_b} came within {near_dist:.2f}m of each other ({relation}).",
    "SEPARATE": "{class_a} and {class_b} moved apart (now {near_dist:.2f}m, previously proximate).",
    "INTERACTION": "Hand-role object interacted with {class_b} at ({x:.2f},{y:.2f},{z:.2f}): {class_b} was {relation} during contact.",
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
