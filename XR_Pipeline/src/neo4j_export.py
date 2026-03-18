"""Neo4j CSV export from EGG graph."""
from __future__ import annotations
from pathlib import Path
from typing import Dict
import pandas as pd


def export_neo4j_csvs(graph: Dict, output_dir: Path):
    """Write all Neo4j import CSVs from an EGG graph dict."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # nodes_rooms.csv
    rooms = []
    for r in graph["rooms"]:
        rooms.append({
            "room_id:ID(Room)": r["room_id"],
            "name": r["name"],
            "x:float": r["position"]["x"],
            "y:float": r["position"]["y"],
            "z:float": r["position"]["z"],
            ":LABEL": "Room",
        })
    pd.DataFrame(rooms).to_csv(output_dir / "nodes_rooms.csv", index=False)

    # nodes_objects.csv
    objects = []
    for o in graph["objects"]:
        objects.append({
            "track_id:ID(Object)": o["track_id"],
            "semantic_class": o["semantic_class"],
            "label": o["label"],
            "caption": o.get("caption", ""),
            ":LABEL": "Object",
        })
    pd.DataFrame(objects).to_csv(output_dir / "nodes_objects.csv", index=False)

    # nodes_events.csv
    events = []
    for e in graph["events"]:
        pos = e.get("position", {})
        events.append({
            "event_id:ID(Event)": e["event_id"],
            "event_type": e["event_type"],
            "summary": e.get("summary", ""),
            "start_ts_ns:long": e["start_ts_ns"],
            "end_ts_ns:long": e["end_ts_ns"],
            "pos_x:float": pos.get("x", 0.0),
            "pos_y:float": pos.get("y", 0.0),
            "pos_z:float": pos.get("z", 0.0),
            ":LABEL": "Event",
        })
    pd.DataFrame(events).to_csv(output_dir / "nodes_events.csv", index=False)

    # edges_room_object.csv
    room_obj = []
    for e in graph["room_edges"]:
        room_obj.append({
            ":START_ID(Room)": e["room_id"],
            ":END_ID(Object)": e["track_id"],
            ":TYPE": "CONTAINS",
        })
    pd.DataFrame(room_obj).to_csv(output_dir / "edges_room_object.csv", index=False)

    # edges_event_object.csv
    evt_obj = []
    for e in graph["event_edges"]:
        evt_obj.append({
            ":START_ID(Event)": e["event_id"],
            ":END_ID(Object)": e["track_id"],
            "role": e.get("role", ""),
            "role_description": e.get("role_description", ""),
            ":TYPE": "INVOLVES",
        })
    pd.DataFrame(evt_obj).to_csv(output_dir / "edges_event_object.csv", index=False)

    # edges_before.csv
    before = []
    for e in graph["temporal_edges"]:
        before.append({
            ":START_ID(Event)": e["src_event_id"],
            ":END_ID(Event)": e["dst_event_id"],
            ":TYPE": "BEFORE",
        })
    pd.DataFrame(before).to_csv(output_dir / "edges_before.csv", index=False)

    return {
        "nodes_rooms": len(rooms),
        "nodes_objects": len(objects),
        "nodes_events": len(events),
        "edges_room_object": len(room_obj),
        "edges_event_object": len(evt_obj),
        "edges_before": len(before),
    }
