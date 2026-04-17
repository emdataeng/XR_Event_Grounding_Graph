#!/usr/bin/env python3
"""10c_build_workflow_timeline.py — Build session-level workflow timeline.

Consumes operation_events.csv (stage 10b) and groups operations into
temporally coherent workflow phases.  Outputs:
  workflow_timeline.json   — full timeline with phases, transitions, summary
  workflow_timeline.csv    — flat phase table for downstream queries

Staleness check: warns if 10b output is older than current config hash.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.workflow_timeline import build_workflow_timeline, timeline_to_df
from src.domain_config import load_domain_config
from src.run_metadata import (
    build_run_metadata, save_run_metadata, check_staleness, emit_staleness_warnings,
)

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config: str = typer.Option(None),
    force: bool = typer.Option(False, "--force", help="Continue even if upstream outputs are stale"),
):
    """Build workflow timeline from operation events."""
    cfg = load_pipeline_config(Path(config) if config else None)
    thr = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Staleness check ───────────────────────────────────────────────────────
    warnings = check_staleness(paths.processed_root, "10b_build_operation_events", cfg, thr)
    if not emit_staleness_warnings(warnings, console=console, force=force):
        raise typer.Exit(1)

    # ── Load operation events ─────────────────────────────────────────────────
    op_events_path = paths.objects_dir / "operation_events.csv"
    if not op_events_path.exists():
        console.print(f"[red]operation_events.csv not found at {op_events_path}. Run 10b first.[/red]")
        raise typer.Exit(1)

    ops_df = pd.read_csv(op_events_path)
    console.print(f"Loaded {len(ops_df)} operation events from {op_events_path}")

    # ── Domain config (D2) ────────────────────────────────────────────────────
    domain = load_domain_config(cfg=cfg)
    if domain:
        console.print(f"[cyan]Domain '{domain.domain_name}' v{domain.domain_version} loaded[/cyan]")
    else:
        console.print("[dim]No domain config — using generic phase labels[/dim]")

    # ── Build timeline ────────────────────────────────────────────────────────
    timeline = build_workflow_timeline(ops_df, thr=thr, session_id=session, domain_config=domain)

    phases = timeline.get("phases", [])
    summary = timeline.get("summary", {})

    console.print(f"\n[bold]Workflow Timeline — {session}[/bold]")
    console.print(f"  Phases: {summary.get('total_phases', 0)}")
    console.print(f"  Dominant phase: [cyan]{summary.get('dominant_phase', 'idle')}[/cyan]")
    console.print(f"  Phase sequence: {summary.get('phase_sequence', [])}")
    console.print(f"  Unresolved candidates: {summary.get('unresolved_candidates', 0)}")

    # ── Write outputs ─────────────────────────────────────────────────────────
    timeline_json = paths.graphs_dir / "workflow_timeline.json"
    timeline_csv  = paths.graphs_dir / "workflow_timeline.csv"

    with open(timeline_json, "w") as f:
        json.dump(timeline, f, indent=2, default=str)
    console.print(f"[green]✓ workflow_timeline.json → {timeline_json}[/green]")

    df = timeline_to_df(timeline)
    df.to_csv(timeline_csv, index=False)
    console.print(f"[green]✓ workflow_timeline.csv  → {timeline_csv}[/green]")

    # Print phase details
    for phase in phases:
        console.print(
            f"  [{phase['phase_id']}] {phase['label']} "
            f"frames {phase['start_frame_idx']}–{phase['end_frame_idx']} "
            f"conf={phase['confidence']:.2f}  ops={len(phase['supporting_operations'])}"
        )

    # ── Run metadata ──────────────────────────────────────────────────────────
    meta = build_run_metadata(
        session_id=session,
        stage="10c_build_workflow_timeline",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        pipeline_yaml_path=PROJECT_ROOT / "configs" / "pipeline.yaml",
        thresholds_yaml_path=PROJECT_ROOT / "configs" / "thresholds.yaml",
        extra={
            "n_operations": len(ops_df),
            "n_phases": summary.get("total_phases", 0),
            "dominant_phase": summary.get("dominant_phase", "idle"),
            "phase_sequence": summary.get("phase_sequence", []),
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]  Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
