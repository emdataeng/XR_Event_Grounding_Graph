#!/usr/bin/env python3
"""14_import_neo4j.py — Push EGG graph CSVs directly into Neo4j Aura.

Reads credentials from .env (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD).
Clears existing data for the session's room before importing,
so re-running is always safe and idempotent.

Usage:
    python scripts/14_import_neo4j.py --session session_002
    python scripts/14_import_neo4j.py --session session_001 --wipe-all
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
import os
import typer
from dotenv import load_dotenv
from neo4j import GraphDatabase
from rich.console import Console
from rich.progress import track

from src.config import PipelinePaths, load_pipeline_config

app = typer.Typer()
console = Console()


# ---------------------------------------------------------------------------
# CSV loaders — return plain list[dict] with friendly key names
# ---------------------------------------------------------------------------

def _read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_rooms(path: Path) -> list[dict]:
    return [
        {"room_id": r["room_id:ID(Room)"], "name": r["name"],
         "x": float(r["x:float"]), "y": float(r["y:float"]), "z": float(r["z:float"])}
        for r in _read(path)
    ]


def load_objects(path: Path) -> list[dict]:
    return [
        {"track_id": r["track_id:ID(Object)"], "semantic_class": r["semantic_class"],
         "label": r["label"], "caption": r["caption"]}
        for r in _read(path)
    ]


def load_events(path: Path) -> list[dict]:
    return [
        {"event_id": r["event_id:ID(Event)"], "event_type": r["event_type"],
         "summary": r["summary"],
         "start_ts_ns": int(r["start_ts_ns:long"]), "end_ts_ns": int(r["end_ts_ns:long"]),
         "pos_x": float(r["pos_x:float"]), "pos_y": float(r["pos_y:float"]), "pos_z": float(r["pos_z:float"])}
        for r in _read(path)
    ]


def load_room_object_edges(path: Path) -> list[dict]:
    return [
        {"room_id": r[":START_ID(Room)"], "track_id": r[":END_ID(Object)"]}
        for r in _read(path)
    ]


def load_event_object_edges(path: Path) -> list[dict]:
    return [
        {"event_id": r[":START_ID(Event)"], "track_id": r[":END_ID(Object)"],
         "role": r["role"], "role_description": r["role_description"]}
        for r in _read(path)
    ]


def load_before_edges(path: Path) -> list[dict]:
    return [
        {"from_id": r[":START_ID(Event)"], "to_id": r[":END_ID(Event)"]}
        for r in _read(path)
    ]


# ---------------------------------------------------------------------------
# Batch helper
# ---------------------------------------------------------------------------

def _batches(lst: list, size: int = 500):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


# ---------------------------------------------------------------------------
# Write transactions
# ---------------------------------------------------------------------------

def tx_clear_room(tx, room_id: str):
    tx.run(
        """
        OPTIONAL MATCH (r:Room {room_id: $rid})
        OPTIONAL MATCH (r)-[:CONTAINS]->(o:Object)
        OPTIONAL MATCH (e:Event)-[:INVOLVES]->(o)
        DETACH DELETE r, o, e
        """,
        rid=room_id,
    )


def tx_rooms(tx, rows):
    tx.run(
        "UNWIND $rows AS r MERGE (n:Room {room_id: r.room_id}) "
        "SET n.name=r.name, n.x=r.x, n.y=r.y, n.z=r.z",
        rows=rows,
    )


def tx_objects(tx, rows):
    tx.run(
        "UNWIND $rows AS r MERGE (n:Object {track_id: r.track_id}) "
        "SET n.semantic_class=r.semantic_class, n.label=r.label, n.caption=r.caption",
        rows=rows,
    )


def tx_events(tx, rows):
    tx.run(
        "UNWIND $rows AS r MERGE (n:Event {event_id: r.event_id}) "
        "SET n.event_type=r.event_type, n.summary=r.summary, "
        "    n.start_ts_ns=r.start_ts_ns, n.end_ts_ns=r.end_ts_ns, "
        "    n.pos_x=r.pos_x, n.pos_y=r.pos_y, n.pos_z=r.pos_z",
        rows=rows,
    )


def tx_room_object_edges(tx, rows):
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (room:Room {room_id: r.room_id}) "
        "MATCH (obj:Object {track_id: r.track_id}) "
        "MERGE (room)-[:CONTAINS]->(obj)",
        rows=rows,
    )


def tx_event_object_edges(tx, rows):
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (evt:Event {event_id: r.event_id}) "
        "MATCH (obj:Object {track_id: r.track_id}) "
        "MERGE (evt)-[rel:INVOLVES]->(obj) "
        "SET rel.role=r.role, rel.role_description=r.role_description",
        rows=rows,
    )


def tx_before_edges(tx, rows):
    tx.run(
        "UNWIND $rows AS r "
        "MATCH (a:Event {event_id: r.from_id}) "
        "MATCH (b:Event {event_id: r.to_id}) "
        "MERGE (a)-[:BEFORE]->(b)",
        rows=rows,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

@app.command()
def main(
    session: str = typer.Option("session_001", help="Session ID to import"),
    config: str = typer.Option(None, help="Path to pipeline.yaml"),
    wipe_all: bool = typer.Option(False, "--wipe-all", help="Delete ALL nodes before importing"),
    env_file: str = typer.Option(".env", help="Path to .env credentials file"),
):
    """Import a session's EGG graph CSVs directly into Neo4j Aura."""

    # --- Credentials ---
    env_path = Path(env_file)
    if not env_path.is_absolute():
        env_path = (Path(__file__).resolve().parent.parent / env_path)
    load_dotenv(env_path)

    uri      = os.getenv("NEO4J_URI")
    user     = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not password:
        console.print("[red]ERROR: NEO4J_URI and NEO4J_PASSWORD must be set in .env[/red]")
        console.print(f"  Expected: {env_path}")
        console.print("  Copy .env.example → .env and fill in your Aura credentials.")
        raise typer.Exit(1)

    # --- Paths ---
    cfg   = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)
    d     = paths.neo4j_dir

    files = {
        "rooms":    d / "nodes_rooms.csv",
        "objects":  d / "nodes_objects.csv",
        "events":   d / "nodes_events.csv",
        "ro_edges": d / "edges_room_object.csv",
        "eo_edges": d / "edges_event_object.csv",
        "be_edges": d / "edges_before.csv",
    }
    for name, path in files.items():
        if not path.exists():
            console.print(f"[red]Missing: {path}[/red]  — run 11_export_neo4j_csv.py first.")
            raise typer.Exit(1)

    # --- Load ---
    rooms    = load_rooms(files["rooms"])
    objects  = load_objects(files["objects"])
    events   = load_events(files["events"])
    ro_edges = load_room_object_edges(files["ro_edges"])
    eo_edges = load_event_object_edges(files["eo_edges"])
    be_edges = load_before_edges(files["be_edges"])
    room_id  = rooms[0]["room_id"] if rooms else session

    # --- Connect ---
    console.print(f"\n[bold]Connecting to Neo4j:[/bold] {uri}")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    console.print("[green]Connected.[/green]\n")

    with driver.session() as s:

        if wipe_all:
            console.print("[yellow]Wiping ALL nodes...[/yellow]")
            s.run("MATCH (n) DETACH DELETE n")
        else:
            console.print(f"[yellow]Clearing session data for room:[/yellow] {room_id}")
            s.execute_write(tx_clear_room, room_id)

        console.print(f"Importing rooms   : {len(rooms)}")
        s.execute_write(tx_rooms, rooms)

        console.print(f"Importing objects : {len(objects)}")
        for b in track(list(_batches(objects)), description="  objects "):
            s.execute_write(tx_objects, b)

        console.print(f"Importing events  : {len(events)}")
        for b in track(list(_batches(events)), description="  events  "):
            s.execute_write(tx_events, b)

        console.print(f"Importing CONTAINS: {len(ro_edges)}")
        s.execute_write(tx_room_object_edges, ro_edges)

        console.print(f"Importing INVOLVES: {len(eo_edges)}")
        for b in track(list(_batches(eo_edges)), description="  INVOLVES"):
            s.execute_write(tx_event_object_edges, b)

        console.print(f"Importing BEFORE  : {len(be_edges)}")
        for b in track(list(_batches(be_edges)), description="  BEFORE  "):
            s.execute_write(tx_before_edges, b)

    driver.close()

    total_edges = len(ro_edges) + len(eo_edges) + len(be_edges)
    console.print(f"\n[bold green]Done — session {session} imported into Neo4j[/bold green]")
    console.print(f"  Nodes : {len(rooms)} rooms + {len(objects)} objects + {len(events)} events")
    console.print(f"  Edges : {total_edges} ({len(ro_edges)} CONTAINS + {len(eo_edges)} INVOLVES + {len(be_edges)} BEFORE)")


if __name__ == "__main__":
    app()
