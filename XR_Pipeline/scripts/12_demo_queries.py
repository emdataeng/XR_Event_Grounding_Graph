#!/usr/bin/env python3
"""12_demo_queries.py — Run demo queries against the EGG graph and operation layer."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import PipelinePaths, load_pipeline_config
from src.egg import load_egg
from src.pruning import answer_query
from src.scene_state_package import load_scene_state_package

app = typer.Typer()
console = Console()

# ── Primitive graph queries (answered against EGG graph) ──────────────────────
GRAPH_QUERIES = [
    "What moved?",
    "What objects appeared?",
    "Which events happened in workstation_A?",
]

# ── Workflow queries (answered against operation_events.csv + SSP) ─────────────
# These are the business-relevant questions for industrial process understanding.
WORKFLOW_QUERIES = [
    "What step is happening now?",
    "What object is being manipulated?",
    "What changed in the scene?",
    "Which operation has the strongest evidence?",
    "What is the current workflow phase?",
]


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Run demo queries against the EGG graph and workflow operation layer."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    paths = PipelinePaths(session, cfg)

    if not paths.egg_graph.exists():
        console.print("[red]egg_graph.json not found. Run 09 first.[/red]")
        raise typer.Exit(1)

    # ── Load EGG graph ────────────────────────────────────────────────────────
    graph = load_egg(paths.egg_graph)
    console.print(
        f"[bold]EGG Graph:[/bold] {len(graph['objects'])} objects, "
        f"{len(graph['events'])} events, {len(graph['rooms'])} rooms"
    )

    # ── Load operation events (optional) ─────────────────────────────────────
    ops_path = paths.objects_dir / "operation_events.csv"
    ops_df: pd.DataFrame | None = None
    if ops_path.exists():
        ops_df = pd.read_csv(ops_path)
        console.print(f"[dim]Operation events: {len(ops_df)} rows[/dim]")
    else:
        console.print(
            "[dim]operation_events.csv not found — "
            "workflow queries will give limited answers.[/dim]"
        )

    # ── Load SSP for workflow phase / state_summary ────────────────────────────
    ssp: dict | None = None
    if paths.scene_state_package.exists():
        ssp = load_scene_state_package(paths.scene_state_package)

    # ── Graph queries ─────────────────────────────────────────────────────────
    results = []
    console.print("\n[bold cyan]── Primitive graph queries ──[/bold cyan]")
    for q in GRAPH_QUERIES:
        subgraph, answer = answer_query(graph, q)
        results.append({
            "query": q,
            "layer": "graph",
            "answer": answer,
            "subgraph_objects": len(subgraph["objects"]),
            "subgraph_events": len(subgraph["events"]),
        })
        console.print(Panel(
            f"[dim]Q:[/dim] {q}\n[bold green]A:[/bold green] {answer}\n"
            f"[dim]Subgraph: {len(subgraph['objects'])} objects, "
            f"{len(subgraph['events'])} events[/dim]",
            title=f"Graph Query {GRAPH_QUERIES.index(q)+1}/{len(GRAPH_QUERIES)}",
        ))

    # ── Workflow queries ───────────────────────────────────────────────────────
    console.print("\n[bold cyan]── Workflow queries ──[/bold cyan]")
    for q in WORKFLOW_QUERIES:
        answer = _answer_workflow_query(q, ops_df, ssp, graph)
        results.append({
            "query": q,
            "layer": "workflow",
            "answer": answer,
        })
        console.print(Panel(
            f"[dim]Q:[/dim] {q}\n[bold green]A:[/bold green] {answer}",
            title=f"Workflow Query {WORKFLOW_QUERIES.index(q)+1}/{len(WORKFLOW_QUERIES)}",
        ))

    # ── Operation events table ────────────────────────────────────────────────
    if ops_df is not None and not ops_df.empty:
        table = Table(title="All Detected Operations")
        table.add_column("ID");      table.add_column("Type");     table.add_column("Agent")
        table.add_column("Object");  table.add_column("Frames");   table.add_column("Conf")
        for _, r in ops_df.iterrows():
            table.add_row(
                str(r["operation_id"]),
                str(r["operation_type"]),
                str(r["agent_track_id"] or "–"),
                str(r["object_track_id"] or "–"),
                f"{r['start_frame_idx']}→{r['end_frame_idx']}",
                f"{r['confidence']:.2f}",
            )
        console.print(table)

    # ── Save results ──────────────────────────────────────────────────────────
    out = paths.queries_dir / "demo_query_results.json"
    out.write_text(json.dumps(results, indent=2))
    console.print(f"[green]✓ Results → {out}[/green]")


# ── Workflow query router ──────────────────────────────────────────────────────

def _answer_workflow_query(
    query: str,
    ops_df: "pd.DataFrame | None",
    ssp: "dict | None",
    graph: dict,
) -> str:
    q = query.lower().strip()

    # ── "What step is happening now?" ─────────────────────────────────────────
    if "step" in q or "happening now" in q:
        if ssp:
            active_ops = ssp.get("state_summary", {}).get("active_operations", [])
            if active_ops:
                items = [
                    f"{op['operation_type']} (agent={op['agent'] or '?'}, "
                    f"obj={op['object'] or '?'}, conf={op['confidence']:.2f})"
                    for op in active_ops
                ]
                return "Active: " + "; ".join(items)
            wf = ssp.get("state_summary", {}).get("workflow_phase")
            if wf:
                return (
                    f"No operations active in the final frames, but the "
                    f"dominant phase was '{wf['label']}' (conf={wf['confidence']:.2f})."
                )
        if ops_df is not None and not ops_df.empty:
            last_op = ops_df.sort_values("end_frame_idx", ascending=False).iloc[0]
            return (
                f"Most recent operation: {last_op['operation_type']} "
                f"(frame {last_op['end_frame_idx']}, conf={last_op['confidence']:.2f})."
            )
        return "No operation events available. Run 10b first."

    # ── "What object is being manipulated?" ───────────────────────────────────
    if "manipulat" in q or "object is being" in q:
        if ops_df is not None and not ops_df.empty:
            # Highest-confidence operation with a workpiece
            best = ops_df.dropna(subset=["object_track_id"]).sort_values(
                "confidence", ascending=False
            ).head(1)
            if not best.empty:
                r = best.iloc[0]
                return (
                    f"Track '{r['object_track_id']}' — involved in "
                    f"{r['operation_type']} "
                    f"(frames {r['start_frame_idx']}–{r['end_frame_idx']}, "
                    f"conf={r['confidence']:.2f})."
                )
        return "No manipulation events detected."

    # ── "What changed in the scene?" ─────────────────────────────────────────
    if "changed" in q:
        changes = []
        # From graph: MOVE events
        move_objs = [
            o["semantic_class"]
            for e in graph["events"] if e["event_type"] == "MOVE"
            for edge in graph["event_edges"] if edge["event_id"] == e["event_id"]
            for o in graph["objects"] if o["track_id"] == edge["track_id"]
        ]
        if move_objs:
            changes.append(
                f"Moved: {', '.join(sorted(set(move_objs)))}"
            )
        # From ops: any operation type that implies change
        if ops_df is not None and not ops_df.empty:
            change_ops = ops_df[
                ops_df["operation_type"].isin(
                    ["PICK_UP", "PUT_DOWN", "CONTACT", "TRANSFER",
                     "PICK_UP_CANDIDATE", "PUT_DOWN_CANDIDATE"]
                )
            ]
            if not change_ops.empty:
                op_summary = change_ops["operation_type"].value_counts()
                changes.append(
                    "Operations: " + ", ".join(
                        f"{cnt}×{ot}" for ot, cnt in op_summary.items()
                    )
                )
        return "; ".join(changes) if changes else "No significant changes detected."

    # ── "Which operation has the strongest evidence?" ─────────────────────────
    if "strongest" in q or "evidence" in q or "best" in q:
        if ops_df is not None and not ops_df.empty:
            best = ops_df.sort_values("confidence", ascending=False).iloc[0]
            n_evidence = len(json.loads(best["evidence_event_ids"])
                             if isinstance(best["evidence_event_ids"], str) else [])
            return (
                f"{best['operation_type']} (id={best['operation_id']}) — "
                f"conf={best['confidence']:.2f}, "
                f"{n_evidence} evidence event(s). "
                f"Notes: {best['notes']}"
            )
        return "No operation events available."

    # ── "What is the current workflow phase?" ─────────────────────────────────
    if "workflow" in q or "phase" in q:
        if ssp:
            wf = ssp.get("state_summary", {}).get("workflow_phase")
            if wf:
                return (
                    f"Phase: '{wf['label']}' "
                    f"(confidence={wf['confidence']:.2f}, {wf['evidence']})."
                )
        if ops_df is not None and not ops_df.empty:
            dominant = ops_df["operation_type"].value_counts().idxmax()
            return (
                f"Dominant operation type: {dominant} "
                f"({ops_df['operation_type'].value_counts()[dominant]} occurrences). "
                "Run 09b after 10b for full workflow phase analysis."
            )
        return "No operation events or SSP available."

    return "Query not specifically matched."


if __name__ == "__main__":
    app()
