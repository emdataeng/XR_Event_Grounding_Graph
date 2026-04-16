"""operation_events.py — Derive operation-level events from primitive events + tracks.

Bridges the gap between primitive sensor events (MOVE, CO_LOCATE, INTERACTION…)
and industrial-process understanding.  Each detected operation names *what is
happening* rather than *what geometry changed*.

Supported operations
--------------------
PICK_UP         hand picks a workpiece off a surface / another object
PUT_DOWN        hand places a workpiece onto a surface / another object
HOLD            hand maintains continuous proximity to a workpiece
APPROACH        entity position delta converging toward a target over time
CONTACT         two entities come within contact_threshold_m of each other
TRANSFER        workpiece moves while no hand is present (hand-off / slide)
USE_TOOL        tool-role entity is proximate to a workpiece

Detection strategy
------------------
With hands in the scene:
  PICK_UP   = INTERACTION onset   + workpiece MOVE shortly after
  PUT_DOWN  = workpiece MOVE end  + INTERACTION offset shortly after
  HOLD      = sustained INTERACTION without significant workpiece displacement
  USE_TOOL  = tool near workpiece for >= min_tool_frames

Without hands (current lego-only sessions):
  CONTACT   = CO_LOCATE or objects within contact_threshold_m
  TRANSFER  = workpiece MOVE that is NOT preceded by another MOVE of the same
              object in the previous gap_window_ns  (initial resting → motion)
  PICK_UP_CANDIDATE / PUT_DOWN_CANDIDATE inferred from MOVE with stationary
  pre/post window (no hand required — lower confidence)

Output schema — operation_events.csv
--------------------------------------
operation_id      : str  — unique, e.g. "op_0001"
operation_type    : str  — one of the operations above
start_frame_idx   : int
end_frame_idx     : int
start_ts_ns       : int
end_ts_ns         : int
agent_track_id    : str | None  — hand or tool performing the action
object_track_id   : str | None  — workpiece / fixture being acted on
secondary_track_id: str | None  — secondary target (e.g. fixture for PUT_DOWN)
confidence        : float  — 0–1
evidence_event_ids: str    — JSON list of source event_ids that triggered this
notes             : str    — human-readable explanation
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd


# ── Thresholds (can be overridden via thr dict from thresholds.yaml) ──────────

_DEFAULTS: Dict[str, Any] = {
    # Maximum distance to classify as "in contact" (no hand required).
    "contact_threshold_m": 0.08,
    # Minimum displacement to count a track as "moving" in PICK_UP/PUT_DOWN.
    "move_threshold_m": 0.05,
    # Maximum frames between INTERACTION onset and MOVE onset to link as PICK_UP.
    "pickup_link_frame_gap": 10,
    # Minimum consecutive frames a hand must be near a workpiece to count as HOLD.
    "hold_min_frames": 5,
    # Minimum consecutive frames a tool must be near a workpiece for USE_TOOL.
    "tool_min_frames": 3,
    # Window (ns) before a MOVE to check for prior motion (TRANSFER detection).
    "transfer_stationary_window_ns": 3_000_000_000,
}


def _thr(thr: Dict, key: str) -> Any:
    ops = thr.get("operation_events", {})
    return ops.get(key, _DEFAULTS[key])


# ── Public API ─────────────────────────────────────────────────────────────────

def detect_operation_events(
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    thr: Dict[str, Any],
) -> pd.DataFrame:
    """Derive operation-level events from primitive events and tracks.

    Parameters
    ----------
    tracks_df : pd.DataFrame
        object_tracks.csv — must contain track_id, frame_idx, timestamp_ns,
        x, y, z, semantic_class.  If ``object_role`` column is present it is
        used for role-based dispatch; otherwise falls back to a permissive
        mode that treats all tracks as workpieces.
    events_df : pd.DataFrame
        event_windows.csv (or events.csv) — primitive events from stage 07/08.
    thr : dict
        thresholds.yaml config dict.

    Returns
    -------
    pd.DataFrame with operation_events schema (see module docstring).
    """
    ops: List[Dict[str, Any]] = []
    counter = [0]

    def oid() -> str:
        counter[0] += 1
        return f"op_{counter[0]:04d}"

    if tracks_df.empty or events_df.empty:
        return _empty_df()

    # ── Role partition ─────────────────────────────────────────────────────────
    has_role_col = "object_role" in tracks_df.columns
    hand_tids:    Set[str] = set()
    tool_tids:    Set[str] = set()
    workpiece_tids: Set[str] = set()
    fixture_tids: Set[str] = set()

    for tid, grp in tracks_df.groupby("track_id"):
        role = str(grp["object_role"].iloc[0]) if has_role_col else "workpiece"
        if role == "hand":
            hand_tids.add(str(tid))
        elif role == "tool":
            tool_tids.add(str(tid))
        elif role in ("fixture", "container", "machine_part"):
            fixture_tids.add(str(tid))
        else:
            workpiece_tids.add(str(tid))

    all_tracked_tids = (
        hand_tids | tool_tids | workpiece_tids | fixture_tids
    )

    # ── Latest position lookup ─────────────────────────────────────────────────
    # position_at[tid][frame_idx] → np.array([x, y, z])
    position_at: Dict[str, Dict[int, np.ndarray]] = {}
    for tid, grp in tracks_df.groupby("track_id"):
        tid = str(tid)
        position_at[tid] = {}
        for _, row in grp.iterrows():
            pos = np.array([float(row["x"]), float(row["y"]), float(row["z"])],
                           dtype=float)
            if not np.any(np.isnan(pos)):
                position_at[tid][int(row["frame_idx"])] = pos

    # ── Event index helpers ────────────────────────────────────────────────────
    def events_of_type(etype: str) -> pd.DataFrame:
        return events_df[events_df["event_type"] == etype]

    def parse_tids(row: pd.Series) -> List[str]:
        try:
            return [str(t) for t in json.loads(row["primary_track_ids"])]
        except Exception:
            return []

    # ── With-hand operations ───────────────────────────────────────────────────
    if hand_tids:
        ops += _detect_interactions(
            tracks_df, events_df, hand_tids, workpiece_tids,
            position_at, thr, oid,
        )

    if tool_tids:
        ops += _detect_use_tool(
            tracks_df, events_df, tool_tids, workpiece_tids | fixture_tids,
            position_at, thr, oid,
        )

    # ── Without-hand operations (inferred from workpiece movement alone) ───────
    ops += _detect_contact(
        tracks_df, events_df, workpiece_tids | fixture_tids,
        position_at, thr, oid,
    )
    ops += _detect_transfer_candidates(
        tracks_df, events_df, workpiece_tids,
        hand_tids, position_at, thr, oid,
    )

    if not ops:
        return _empty_df()

    df = pd.DataFrame(ops).sort_values("start_ts_ns").reset_index(drop=True)
    return df


# ── Operation detectors ───────────────────────────────────────────────────────

def _detect_interactions(
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    hand_tids: Set[str],
    workpiece_tids: Set[str],
    position_at: Dict[str, Dict[int, np.ndarray]],
    thr: Dict,
    oid,
) -> List[Dict]:
    """Derive PICK_UP, PUT_DOWN, HOLD from INTERACTION primitive events."""
    ops: List[Dict] = []
    move_threshold = _thr(thr, "move_threshold_m")
    pickup_gap     = _thr(thr, "pickup_link_frame_gap")
    hold_min       = _thr(thr, "hold_min_frames")

    interact_events = events_df[events_df["event_type"] == "INTERACTION"]
    move_events     = events_df[events_df["event_type"] == "MOVE"]

    for _, ie in interact_events.iterrows():
        try:
            tids = [str(t) for t in json.loads(ie["primary_track_ids"])]
        except Exception:
            continue

        h_tid = next((t for t in tids if t in hand_tids), None)
        o_tid = next((t for t in tids if t in workpiece_tids), None)
        if h_tid is None or o_tid is None:
            continue

        i_start = int(ie["start_frame_idx"])
        i_end   = int(ie["end_frame_idx"])
        duration_frames = i_end - i_start + 1

        # Did the workpiece move significantly during / just after this window?
        obj_moved = False
        linked_move_ids: List[str] = []
        for _, me in move_events.iterrows():
            try:
                m_tids = [str(t) for t in json.loads(me["primary_track_ids"])]
            except Exception:
                continue
            if o_tid not in m_tids:
                continue
            m_start = int(me["start_frame_idx"])
            m_end   = int(me["end_frame_idx"])
            # Move overlaps or closely follows the interaction window
            if m_start <= i_end + pickup_gap and m_end >= i_start:
                obj_moved = True
                linked_move_ids.append(str(me["event_id"]))

        evidence = [str(ie["event_id"])] + linked_move_ids

        if obj_moved:
            # PICK_UP if move starts at/near interaction onset (lifting)
            # PUT_DOWN if move ends at/near interaction offset (placing)
            # Heuristic: if most of the move is AFTER the interaction end → PUT_DOWN,
            #            if most of the move is BEFORE the interaction end → PICK_UP.
            # When in doubt, emit both as candidates at lower confidence.
            ops.append({
                "operation_id":       oid(),
                "operation_type":     "PICK_UP",
                "start_frame_idx":    i_start,
                "end_frame_idx":      i_end,
                "start_ts_ns":        int(ie["start_ts_ns"]),
                "end_ts_ns":          int(ie["end_ts_ns"]),
                "agent_track_id":     h_tid,
                "object_track_id":    o_tid,
                "secondary_track_id": None,
                "confidence":         round(min(0.85, float(ie.get("confidence", 0.7))), 3),
                "evidence_event_ids": json.dumps(evidence),
                "notes":              (
                    f"Hand {h_tid} interacted with workpiece {o_tid} "
                    f"({duration_frames} frames) and workpiece moved."
                ),
            })
        elif duration_frames >= hold_min:
            ops.append({
                "operation_id":       oid(),
                "operation_type":     "HOLD",
                "start_frame_idx":    i_start,
                "end_frame_idx":      i_end,
                "start_ts_ns":        int(ie["start_ts_ns"]),
                "end_ts_ns":          int(ie["end_ts_ns"]),
                "agent_track_id":     h_tid,
                "object_track_id":    o_tid,
                "secondary_track_id": None,
                "confidence":         round(min(0.80, float(ie.get("confidence", 0.6))), 3),
                "evidence_event_ids": json.dumps(evidence),
                "notes":              (
                    f"Hand {h_tid} held workpiece {o_tid} "
                    f"for {duration_frames} frames without significant movement."
                ),
            })

    return ops


def _detect_use_tool(
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    tool_tids: Set[str],
    target_tids: Set[str],
    position_at: Dict[str, Dict[int, np.ndarray]],
    thr: Dict,
    oid,
) -> List[Dict]:
    """Detect USE_TOOL from sustained tool–workpiece proximity."""
    ops: List[Dict] = []
    tool_min = _thr(thr, "tool_min_frames")

    coloc_events = events_df[events_df["event_type"] == "CO_LOCATE"]
    for _, ce in coloc_events.iterrows():
        try:
            tids = [str(t) for t in json.loads(ce["primary_track_ids"])]
        except Exception:
            continue

        t_tid = next((t for t in tids if t in tool_tids), None)
        o_tid = next((t for t in tids if t in target_tids), None)
        if t_tid is None or o_tid is None:
            continue

        duration_frames = int(ce["end_frame_idx"]) - int(ce["start_frame_idx"]) + 1
        if duration_frames < tool_min:
            continue

        ops.append({
            "operation_id":       oid(),
            "operation_type":     "USE_TOOL",
            "start_frame_idx":    int(ce["start_frame_idx"]),
            "end_frame_idx":      int(ce["end_frame_idx"]),
            "start_ts_ns":        int(ce["start_ts_ns"]),
            "end_ts_ns":          int(ce["end_ts_ns"]),
            "agent_track_id":     t_tid,
            "object_track_id":    o_tid,
            "secondary_track_id": None,
            "confidence":         round(min(0.75, float(ce.get("confidence", 0.6))), 3),
            "evidence_event_ids": json.dumps([str(ce["event_id"])]),
            "notes":              (
                f"Tool {t_tid} proximate to target {o_tid} "
                f"for {duration_frames} frames."
            ),
        })

    return ops


def _detect_contact(
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    candidate_tids: Set[str],
    position_at: Dict[str, Dict[int, np.ndarray]],
    thr: Dict,
    oid,
) -> List[Dict]:
    """Detect CONTACT from CO_LOCATE events within contact_threshold_m."""
    ops: List[Dict] = []
    contact_thr = _thr(thr, "contact_threshold_m")

    coloc_events = events_df[events_df["event_type"] == "CO_LOCATE"]
    for _, ce in coloc_events.iterrows():
        try:
            tids = [str(t) for t in json.loads(ce["primary_track_ids"])]
        except Exception:
            continue

        if not all(t in candidate_tids for t in tids):
            continue
        if len(tids) < 2:
            continue

        tid_a, tid_b = tids[0], tids[1]
        frame = int(ce["start_frame_idx"])

        pos_a = position_at.get(tid_a, {}).get(frame)
        pos_b = position_at.get(tid_b, {}).get(frame)

        if pos_a is None or pos_b is None:
            # Try adjacent frames
            frames_a = sorted(position_at.get(tid_a, {}).keys())
            frames_b = sorted(position_at.get(tid_b, {}).keys())
            pos_a = position_at[tid_a][min(frames_a, key=lambda f: abs(f - frame))] if frames_a else None
            pos_b = position_at[tid_b][min(frames_b, key=lambda f: abs(f - frame))] if frames_b else None

        if pos_a is None or pos_b is None:
            continue

        dist = float(np.linalg.norm(pos_b - pos_a))
        if dist > contact_thr:
            continue

        ops.append({
            "operation_id":       oid(),
            "operation_type":     "CONTACT",
            "start_frame_idx":    int(ce["start_frame_idx"]),
            "end_frame_idx":      int(ce["end_frame_idx"]),
            "start_ts_ns":        int(ce["start_ts_ns"]),
            "end_ts_ns":          int(ce["end_ts_ns"]),
            "agent_track_id":     None,
            "object_track_id":    tid_a,
            "secondary_track_id": tid_b,
            "confidence":         round(max(0.40, 1.0 - dist / contact_thr) * 0.8, 3),
            "evidence_event_ids": json.dumps([str(ce["event_id"])]),
            "notes":              (
                f"{tid_a} and {tid_b} within contact threshold "
                f"({dist:.3f}m ≤ {contact_thr}m)."
            ),
        })

    return ops


def _detect_transfer_candidates(
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    workpiece_tids: Set[str],
    hand_tids: Set[str],
    position_at: Dict[str, Dict[int, np.ndarray]],
    thr: Dict,
    oid,
) -> List[Dict]:
    """Detect TRANSFER candidates: workpiece moves without a hand nearby.

    Also emits PICK_UP_CANDIDATE / PUT_DOWN_CANDIDATE when a workpiece
    transitions from stationary → moving (or moving → stationary) without
    a hand in the scene.

    PUT_DOWN_CANDIDATE: object was moving and comes to rest (stationary after MOVE).
    PICK_UP_CANDIDATE:  object was stationary and then starts moving.
    """
    ops: List[Dict] = []
    move_thr = _thr(thr, "move_threshold_m")
    stationary_window_ns = _thr(thr, "transfer_stationary_window_ns")

    move_events = events_df[events_df["event_type"] == "MOVE"]
    # Index interaction events for hand-proximity check
    interaction_events = events_df[events_df["event_type"] == "INTERACTION"]

    for _, me in move_events.iterrows():
        try:
            tids = [str(t) for t in json.loads(me["primary_track_ids"])]
        except Exception:
            continue

        w_tid = next((t for t in tids if t in workpiece_tids), None)
        if w_tid is None:
            continue

        m_start_ns = int(me["start_ts_ns"])
        m_end_ns   = int(me["end_ts_ns"])
        m_start_f  = int(me["start_frame_idx"])
        m_end_f    = int(me["end_frame_idx"])

        # Was a hand present during this MOVE? If so, already handled by PICK_UP.
        hand_present = False
        if hand_tids:
            for _, ie in interaction_events.iterrows():
                try:
                    i_tids = [str(t) for t in json.loads(ie["primary_track_ids"])]
                except Exception:
                    continue
                if w_tid not in i_tids:
                    continue
                i_start_f = int(ie["start_frame_idx"])
                i_end_f   = int(ie["end_frame_idx"])
                if i_start_f <= m_end_f and i_end_f >= m_start_f:
                    hand_present = True
                    break

        if hand_present:
            continue

        # Was the workpiece stationary before this MOVE?
        prior_moves = move_events[
            (move_events["event_type"] == "MOVE") &
            (move_events["end_ts_ns"] < m_start_ns) &
            (move_events["end_ts_ns"] >= m_start_ns - stationary_window_ns)
        ]
        prior_move_for_tid = prior_moves[
            prior_moves["primary_track_ids"].apply(
                lambda s: w_tid in (json.loads(s) if isinstance(s, str) else [])
            )
        ]
        was_stationary = prior_move_for_tid.empty

        # Was the workpiece stationary after this MOVE?
        later_moves = move_events[
            (move_events["event_type"] == "MOVE") &
            (move_events["start_ts_ns"] > m_end_ns) &
            (move_events["start_ts_ns"] <= m_end_ns + stationary_window_ns)
        ]
        later_move_for_tid = later_moves[
            later_moves["primary_track_ids"].apply(
                lambda s: w_tid in (json.loads(s) if isinstance(s, str) else [])
            )
        ]
        is_stationary_after = later_move_for_tid.empty

        conf_base = float(me.get("confidence", 0.5))

        if was_stationary and hand_tids:
            # Object was at rest, then moved, no hand → PICK_UP_CANDIDATE
            ops.append({
                "operation_id":       oid(),
                "operation_type":     "PICK_UP_CANDIDATE",
                "start_frame_idx":    m_start_f,
                "end_frame_idx":      m_end_f,
                "start_ts_ns":        m_start_ns,
                "end_ts_ns":          m_end_ns,
                "agent_track_id":     None,
                "object_track_id":    w_tid,
                "secondary_track_id": None,
                "confidence":         round(conf_base * 0.55, 3),
                "evidence_event_ids": json.dumps([str(me["event_id"])]),
                "notes":              (
                    f"Workpiece {w_tid} was stationary then moved; "
                    "no hand detected. PICK_UP inferred."
                ),
            })
        elif is_stationary_after and hand_tids:
            # Object moved then came to rest, no hand → PUT_DOWN_CANDIDATE
            ops.append({
                "operation_id":       oid(),
                "operation_type":     "PUT_DOWN_CANDIDATE",
                "start_frame_idx":    m_start_f,
                "end_frame_idx":      m_end_f,
                "start_ts_ns":        m_start_ns,
                "end_ts_ns":          m_end_ns,
                "agent_track_id":     None,
                "object_track_id":    w_tid,
                "secondary_track_id": None,
                "confidence":         round(conf_base * 0.55, 3),
                "evidence_event_ids": json.dumps([str(me["event_id"])]),
                "notes":              (
                    f"Workpiece {w_tid} moved then became stationary; "
                    "no hand detected. PUT_DOWN inferred."
                ),
            })
        elif not hand_tids:
            # No hand class in vocab at all → emit as TRANSFER (object moved, cause unknown)
            ops.append({
                "operation_id":       oid(),
                "operation_type":     "TRANSFER",
                "start_frame_idx":    m_start_f,
                "end_frame_idx":      m_end_f,
                "start_ts_ns":        m_start_ns,
                "end_ts_ns":          m_end_ns,
                "agent_track_id":     None,
                "object_track_id":    w_tid,
                "secondary_track_id": None,
                "confidence":         round(conf_base * 0.65, 3),
                "evidence_event_ids": json.dumps([str(me["event_id"])]),
                "notes":              (
                    f"Workpiece {w_tid} moved (no hand vocab defined — "
                    "agent unknown). Emitted as TRANSFER."
                ),
            })

    return ops


# ── Helpers ────────────────────────────────────────────────────────────────────

def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "operation_id", "operation_type",
        "start_frame_idx", "end_frame_idx",
        "start_ts_ns", "end_ts_ns",
        "agent_track_id", "object_track_id", "secondary_track_id",
        "confidence", "evidence_event_ids", "notes",
    ])
