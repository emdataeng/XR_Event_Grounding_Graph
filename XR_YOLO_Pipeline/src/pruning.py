"""EGG graph pruning and structured query answering."""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple


def prune_by_time(graph: Dict, start_ns: int, end_ns: int) -> Dict:
    """Keep only events overlapping [start_ns, end_ns]."""
    keep_events = {
        e["event_id"] for e in graph["events"]
        if e["start_ts_ns"] <= end_ns and e["end_ts_ns"] >= start_ns
    }
    return _filter_graph(graph, keep_events)


def prune_by_room(graph: Dict, room_id: str) -> Dict:
    """Keep only rooms, objects, and events in the given room."""
    keep_tracks = {
        e["track_id"] for e in graph["room_edges"]
        if e["room_id"] == room_id
    }
    keep_events = {
        e["event_id"] for e in graph["event_edges"]
        if e["track_id"] in keep_tracks
    }
    return _filter_graph(graph, keep_events, keep_tracks)


def prune_by_semantic_class(graph: Dict, semantic_class: str) -> Dict:
    """Keep objects matching semantic_class and their associated events."""
    keep_tracks = {
        o["track_id"] for o in graph["objects"]
        if semantic_class.lower() in o["semantic_class"].lower()
        or semantic_class.lower() in o["label"].lower()
    }
    keep_events = {
        e["event_id"] for e in graph["event_edges"]
        if e["track_id"] in keep_tracks
    }
    return _filter_graph(graph, keep_events, keep_tracks)


def prune_by_event_type(graph: Dict, event_type: str) -> Dict:
    """Keep only events of a given type and their objects."""
    keep_events = {
        e["event_id"] for e in graph["events"]
        if e["event_type"].upper() == event_type.upper()
    }
    keep_tracks = {
        e["track_id"] for e in graph["event_edges"]
        if e["event_id"] in keep_events
    }
    return _filter_graph(graph, keep_events, keep_tracks)


def get_last_seen(graph: Dict, semantic_class: str) -> Optional[Dict]:
    """Find the last known position of an object matching semantic_class."""
    subgraph = prune_by_semantic_class(graph, semantic_class)
    if not subgraph["objects"]:
        return None
    best = None
    best_ts = -1
    for obj in subgraph["objects"]:
        if obj["time_variant_history"]:
            last = max(obj["time_variant_history"], key=lambda h: h["timestamp_ns"])
            if last["timestamp_ns"] > best_ts:
                best_ts = last["timestamp_ns"]
                best = {"track_id": obj["track_id"], "semantic_class": obj["semantic_class"],
                        "label": obj["label"], **last}
    return best


def answer_query(graph: Dict, query: str) -> Tuple[Dict, str]:
    """Simple rule-based query answering over an EGG graph.

    Supports questions like:
    - "Where was X last seen?"
    - "What moved?"
    - "Which events happened in room Y?"
    - "What is near X?"

    Returns (pruned_subgraph, answer_text).
    """
    q = query.lower().strip()

    # Pattern: "where was X last seen?"
    m = re.search(r"where (?:was|is) (?:the )?(.+?) (?:last )?seen", q)
    if m:
        thing = m.group(1).strip()
        if thing.lower().startswith("the "):
            thing = thing[4:].strip()
        result = get_last_seen(graph, thing)
        subgraph = prune_by_semantic_class(graph, thing)
        if result:
            answer = (
                f"The {thing} (track {result['track_id']}) was last seen at "
                f"({result['x']:.3f}, {result['y']:.3f}, {result['z']:.3f}) "
                f"at timestamp {result['timestamp_ns']} ns."
            )
        else:
            answer = f"No object matching '{thing}' found in the graph."
        return subgraph, answer

    # Pattern: "what moved?" / "what objects moved?"
    if "moved" in q or "move" in q:
        subgraph = prune_by_event_type(graph, "MOVE")
        moved_classes = [
            o["semantic_class"] for o in subgraph["objects"]
        ]
        if moved_classes:
            answer = f"The following object classes were involved in MOVE events: {', '.join(set(moved_classes))}."
        else:
            answer = "No MOVE events found in the graph."
        return subgraph, answer

    # Pattern: "which events happened in room X?" / "happened in workstation_A"
    m = re.search(r"events?.*(?:room|workstation)[_\s]?(\w+)", q)
    if m:
        room_word = m.group(1)
        # Reconstruct workstation_A style room ids
        room = f"workstation_{room_word}" if not room_word.startswith("workstation") else room_word
        # Also try exact match
        all_rooms = {r["room_id"] for r in graph["rooms"]}
        if room not in all_rooms:
            # Try partial match
            matches = [r for r in all_rooms if room_word.lower() in r.lower()]
            room = matches[0] if matches else room
        subgraph = prune_by_room(graph, room)
        n = len(subgraph["events"])
        answer = f"Found {n} events in room/workstation '{room}'."
        return subgraph, answer

    # Pattern: "what appeared?" / "what objects appeared?"
    if "appear" in q:
        subgraph = prune_by_event_type(graph, "APPEAR")
        classes = list({o["semantic_class"] for o in subgraph["objects"]})
        answer = f"Objects that appeared: {', '.join(classes) if classes else 'none'}."
        return subgraph, answer

    # Fallback: return full graph
    answer = (
        f"Query not specifically matched. Returning full graph with "
        f"{len(graph['objects'])} objects and {len(graph['events'])} events."
    )
    return graph, answer


def _filter_graph(
    graph: Dict,
    keep_events: set,
    keep_tracks: Optional[set] = None,
) -> Dict:
    """Return a copy of graph keeping only specified events and tracks."""
    import copy
    g = copy.deepcopy(graph)

    g["events"] = [e for e in g["events"] if e["event_id"] in keep_events]

    if keep_tracks is None:
        keep_tracks = {
            edge["track_id"] for edge in g["event_edges"]
            if edge["event_id"] in keep_events
        }

    g["objects"] = [o for o in g["objects"] if o["track_id"] in keep_tracks]
    g["event_edges"] = [e for e in g["event_edges"]
                        if e["event_id"] in keep_events and e["track_id"] in keep_tracks]
    g["room_edges"] = [e for e in g["room_edges"] if e["track_id"] in keep_tracks]
    g["temporal_edges"] = [e for e in g["temporal_edges"]
                           if e["src_event_id"] in keep_events
                           and e["dst_event_id"] in keep_events]
    return g
