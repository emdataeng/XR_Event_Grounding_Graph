"""Object track linking: connect observations across sparse frames."""
from __future__ import annotations
from typing import List, Dict, Optional
import numpy as np
import pandas as pd


def compute_linkage_score(
    obs_a: dict, obs_b: dict,
    max_spatial_jump: float = 0.8,
    size_ratio_threshold: float = 3.0,
    class_must_match: bool = True,
) -> float:
    """Compute a 0–1 linkage score between two observations.

    Returns 0 if they should not be linked.
    """
    if class_must_match and obs_a["semantic_class"] != obs_b["semantic_class"]:
        return 0.0

    pos_a = np.array([obs_a["x"], obs_a["y"], obs_a["z"]], dtype=float)
    pos_b = np.array([obs_b["x"], obs_b["y"], obs_b["z"]], dtype=float)

    # Handle NaN positions
    if np.any(np.isnan(pos_a)) or np.any(np.isnan(pos_b)):
        return 0.0

    dist = np.linalg.norm(pos_b - pos_a)
    if dist > max_spatial_jump:
        return 0.0

    # Size similarity
    size_a = max(obs_a.get("w", 0) or 0, obs_a.get("h", 0) or 0, 0.01)
    size_b = max(obs_b.get("w", 0) or 0, obs_b.get("h", 0) or 0, 0.01)
    ratio = max(size_a, size_b) / max(min(size_a, size_b), 0.01)
    if ratio > size_ratio_threshold:
        return 0.0

    # Score: inverse distance
    spatial_score = 1.0 - (dist / max_spatial_jump)
    size_score = 1.0 - min((ratio - 1.0) / (size_ratio_threshold - 1.0), 1.0)
    return float(0.7 * spatial_score + 0.3 * size_score)


def link_observations_to_tracks(
    obs_df: pd.DataFrame,
    max_spatial_jump: float = 0.8,
    max_time_gap_ns: int = 5_000_000_000,
    size_ratio_threshold: float = 3.0,
    class_must_match: bool = True,
) -> pd.DataFrame:
    """Greedy nearest-neighbor track linking for sparse frames.

    Processes observations frame by frame, linking each to the best
    existing track or creating a new one.

    Returns DataFrame with TRACK_COLUMNS.
    """
    obs_sorted = obs_df.sort_values("timestamp_ns").reset_index(drop=True)

    # active_tracks: track_id -> last observation dict
    active_tracks: Dict[str, dict] = {}
    track_counter = [0]
    rows = []

    def new_track_id() -> str:
        track_counter[0] += 1
        return f"trk_{track_counter[0]:04d}"

    for _, obs in obs_sorted.iterrows():
        obs_dict = obs.to_dict()
        ts = obs_dict["timestamp_ns"]

        best_track_id = None
        best_score = 0.0

        for tid, prev_obs in list(active_tracks.items()):
            # Expire stale tracks
            if ts - prev_obs["timestamp_ns"] > max_time_gap_ns:
                continue
            score = compute_linkage_score(
                prev_obs, obs_dict,
                max_spatial_jump=max_spatial_jump,
                size_ratio_threshold=size_ratio_threshold,
                class_must_match=class_must_match,
            )
            if score > best_score:
                best_score = score
                best_track_id = tid

        if best_track_id is None or best_score == 0.0:
            best_track_id = new_track_id()

        active_tracks[best_track_id] = obs_dict

        rows.append({
            "track_id": best_track_id,
            "observation_id": obs_dict["observation_id"],
            "frame_idx": obs_dict["frame_idx"],
            "timestamp_ns": ts,
            "semantic_class": obs_dict["semantic_class"],
            "x": obs_dict["x"], "y": obs_dict["y"], "z": obs_dict["z"],
            "w": obs_dict.get("w"), "h": obs_dict.get("h"), "d": obs_dict.get("d"),
            "yaw": obs_dict.get("yaw"),
            "is_first_in_track": False,  # set below
            "is_last_in_track": False,   # set below
            "linkage_score": best_score,
        })

    if not rows:
        return pd.DataFrame(columns=[
            "track_id", "observation_id", "frame_idx", "timestamp_ns",
            "semantic_class", "x", "y", "z", "w", "h", "d", "yaw",
            "is_first_in_track", "is_last_in_track", "linkage_score",
        ])

    df = pd.DataFrame(rows)

    # Mark first and last per track
    for tid, group in df.groupby("track_id"):
        idxs = group.index.tolist()
        df.loc[idxs[0], "is_first_in_track"] = True
        df.loc[idxs[-1], "is_last_in_track"] = True

    return df


def build_track_summary(tracks_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize each track: duration, observation count, mean position."""
    records = []
    for tid, grp in tracks_df.groupby("track_id"):
        grp_sorted = grp.sort_values("timestamp_ns")
        records.append({
            "track_id": tid,
            "semantic_class": grp_sorted["semantic_class"].iloc[0],
            "n_observations": len(grp_sorted),
            "first_frame": int(grp_sorted["frame_idx"].min()),
            "last_frame": int(grp_sorted["frame_idx"].max()),
            "first_ts_ns": int(grp_sorted["timestamp_ns"].min()),
            "last_ts_ns": int(grp_sorted["timestamp_ns"].max()),
            "duration_ns": int(grp_sorted["timestamp_ns"].max() - grp_sorted["timestamp_ns"].min()),
            "mean_x": float(grp_sorted["x"].mean()),
            "mean_y": float(grp_sorted["y"].mean()),
            "mean_z": float(grp_sorted["z"].mean()),
        })
    return pd.DataFrame(records)
