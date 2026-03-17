"""EGG graph construction and serialization."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


def build_egg_graph(
    session_id: str,
    tracks_df: pd.DataFrame,
    events_df: pd.DataFrame,
    event_object_roles_df: pd.DataFrame,
    room_id: str = "workstation_A",
    room_position: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Assemble EGG graph JSON from pipeline DataFrames.

    Returns a dict matching the canonical EGG JSON schema.
    """
    now = datetime.now(timezone.utc).isoformat()

    # ---- Rooms ----
    rooms = [{
        "room_id": room_id,
        "name": room_id,
        "position": room_position or {"x": 0.0, "y": 0.0, "z": 0.0},
    }]

    # ---- Objects (one per track) ----
    objects = []
    for tid, grp in tracks_df.groupby("track_id"):
        grp_s = grp.sort_values("timestamp_ns").reset_index(drop=True)
        sem_class = str(grp_s["semantic_class"].iloc[0])
        history = []
        for _, row in grp_s.iterrows():
            history.append({
                "timestamp_ns": int(row["timestamp_ns"]),
                "frame_idx": int(row["frame_idx"]),
                "x": _f(row["x"]), "y": _f(row["y"]), "z": _f(row["z"]),
                "w": _f(row.get("w")), "h": _f(row.get("h")), "d": _f(row.get("d")),
                "yaw": _f(row.get("yaw")),
            })
        objects.append({
            "track_id": tid,
            "semantic_class": sem_class,
            "label": sem_class,
            "caption": f"{sem_class} object tracked across {len(grp_s)} frames",
            "time_invariant": {},
            "time_variant_history": history,
        })

    # ---- Events ----
    event_list = []
    for _, row in events_df.iterrows():
        event_list.append({
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "summary": str(row.get("summary", "")),
            "start_ts_ns": int(row["start_ts_ns"]),
            "end_ts_ns": int(row["end_ts_ns"]),
            "position": {
                "x": _f(row.get("event_pos_x", 0)),
                "y": _f(row.get("event_pos_y", 0)),
                "z": _f(row.get("event_pos_z", 0)),
            },
        })

    # ---- Event–Object edges ----
    event_edges = []
    for _, row in event_object_roles_df.iterrows():
        event_edges.append({
            "event_id": row["event_id"],
            "track_id": row["track_id"],
            "role": row["role"],
            "role_description": row["role_description"],
        })

    # ---- Room–Object edges ----
    all_track_ids = tracks_df["track_id"].unique().tolist()
    room_edges = [{"room_id": room_id, "track_id": tid} for tid in all_track_ids]

    # ---- Temporal ordering edges (BEFORE) ----
    events_sorted = events_df.sort_values("start_ts_ns").reset_index(drop=True)
    temporal_edges = []
    eids = events_sorted["event_id"].tolist()
    for i in range(len(eids) - 1):
        temporal_edges.append({
            "src_event_id": eids[i],
            "dst_event_id": eids[i + 1],
            "relation": "BEFORE",
        })

    return {
        "graph_metadata": {
            "session_id": session_id,
            "created_at": now,
            "source": "quest3_sparse_rgbd_pose",
            "notes": [],
        },
        "rooms": rooms,
        "objects": objects,
        "events": event_list,
        "event_edges": event_edges,
        "room_edges": room_edges,
        "temporal_edges": temporal_edges,
    }


def _f(val) -> float:
    """Safe float conversion, returns 0.0 for None/NaN."""
    if val is None:
        return 0.0
    try:
        v = float(val)
        return 0.0 if (v != v) else v  # NaN check
    except (TypeError, ValueError):
        return 0.0


def save_egg(graph: Dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(graph, f, indent=2)


def load_egg(path: Path) -> Dict:
    with open(path, "r") as f:
        return json.load(f)
