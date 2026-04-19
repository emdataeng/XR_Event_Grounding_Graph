#!/usr/bin/env python3
"""10d_build_subtask_events.py — Build subtask / step event layer.

Reads state facts + operation events and infers assembly subtask candidates
using domain config templates (or generic fallbacks).

Outputs
-------
  objects/subtask_events.csv    — flat subtask table
  graphs/subtask_sequence.json  — ordered sequence with status timeline
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
import pandas as pd
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config, load_thresholds
from src.subtask_events import infer_subtask_events, subtask_sequence_json
from src.domain_config import load_domain_config
from src.run_metadata import build_run_metadata, save_run_metadata

app = typer.Typer()
console = Console()


@app.command()
def main(
    session: str = typer.Option("session_001"),
    config:  str = typer.Option(None),
):
    """Infer assembly subtask candidates from state facts and operations."""
    cfg   = load_pipeline_config(Path(config) if config else None)
    thr   = load_thresholds()
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    # ── Load state facts ──────────────────────────────────────────────────────
    facts_df = pd.DataFrame()
    if paths.state_facts_csv.exists():
        facts_df = pd.read_csv(paths.state_facts_csv)
        console.print(f"[dim]State facts: {len(facts_df)} rows[/dim]")
    else:
        console.print("[yellow]state_facts.csv not found — run 09c first[/yellow]")

    # ── Load operations ───────────────────────────────────────────────────────
    ops_df = pd.DataFrame()
    ops_path = paths.objects_dir / "operation_events.csv"
    if ops_path.exists():
        ops_df = pd.read_csv(ops_path)
        console.print(f"[dim]Operations: {len(ops_df)} rows[/dim]")
    else:
        console.print("[yellow]operation_events.csv not found — subtask inference will be limited[/yellow]")

    # ── Domain config ─────────────────────────────────────────────────────────
    domain = load_domain_config(cfg=cfg)
    if domain:
        console.print(
            f"[cyan]Domain '{domain.domain_name}': "
            f"{len(domain.subtask_templates)} subtask templates, "
            f"{len(domain.dependency_rules)} dependency rules[/cyan]"
        )
    else:
        console.print("[dim]No domain config — using generic subtask templates[/dim]")

    # ── Infer subtasks ────────────────────────────────────────────────────────
    subtasks_df = infer_subtask_events(
        facts_df=facts_df,
        ops_df=ops_df,
        domain_config=domain,
    )
    console.print(f"\n[bold]Subtask events:[/bold] {len(subtasks_df)} total")

    if not subtasks_df.empty:
        for status, cnt in subtasks_df["status"].value_counts().items():
            console.print(f"  {status}: {cnt}")
        for tmpl, cnt in subtasks_df["template_name"].value_counts().head(8).items():
            console.print(f"  template={tmpl}: {cnt}")

    # ── Write outputs ─────────────────────────────────────────────────────────
    subtasks_df.to_csv(paths.subtask_events, index=False)
    console.print(f"[green]✓ subtask_events.csv → {paths.subtask_events}[/green]")

    seq_pkg = subtask_sequence_json(subtasks_df, session_id=session)
    paths.subtask_sequence.write_text(json.dumps(seq_pkg, indent=2))
    console.print(f"[green]✓ subtask_sequence.json → {paths.subtask_sequence}[/green]")

    # ── Run metadata ──────────────────────────────────────────────────────────
    status_counts = subtasks_df["status"].value_counts().to_dict() if not subtasks_df.empty else {}
    meta = build_run_metadata(
        session_id=session,
        stage="10d_build_subtask_events",
        pipeline_cfg=cfg,
        thresholds_cfg=thr,
        extra={
            "total_subtasks":   len(subtasks_df),
            "status_counts":    status_counts,
            "domain_name":      domain.domain_name if domain else None,
            "n_templates_used": len(domain.subtask_templates) if domain else 0,
        },
    )
    saved = save_run_metadata(paths.processed_root, meta)
    console.print(f"[dim]Run metadata → {saved}[/dim]")


if __name__ == "__main__":
    app()
