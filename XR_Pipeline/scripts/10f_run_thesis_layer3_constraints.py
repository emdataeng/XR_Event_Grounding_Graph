#!/usr/bin/env python3
"""10f_run_thesis_layer3_constraints.py - Run thesis Layer 3 reasoning.

Evaluates thesis inference and compatibility rules over state_facts.csv and
writes interval-scoped constraints and incompatibilities.

Outputs
-------
  constraints.csv
  incompatibilities.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import typer
from rich.console import Console

from src.config import PipelinePaths, load_pipeline_config
from src.thesis_constraint_reasoner import (
    run_layer3_reasoning,
    write_layer3_outputs,
)

app = typer.Typer()
console = Console()
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_project_path(path_str: str | None, default: Path) -> Path:
    if not path_str:
        return default
    path = Path(path_str)
    if path.exists() or path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _resolve_domain_yaml(cfg: dict) -> Path:
    domain_path = cfg.get("domain_config")
    if not domain_path:
        console.print("[red]pipeline.yaml does not define domain_config[/red]")
        raise typer.Exit(1)

    path = Path(str(domain_path))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        console.print(f"[red]Configured domain YAML not found: {path}[/red]")
        raise typer.Exit(1)
    return path


@app.command()
def main(
    session: str = typer.Option("session_001", help="Session ID"),
    config: str = typer.Option("configs/pipeline.yaml", help="Path to pipeline.yaml"),
    rules: str = typer.Option("configs/thesis_rules.yaml", help="Path to thesis_rules.yaml"),
):
    """Run thesis Layer 3 constraint and incompatibility inference."""
    config_path = _resolve_project_path(config, PROJECT_ROOT / "configs" / "pipeline.yaml")
    rules_path = _resolve_project_path(rules, PROJECT_ROOT / "configs" / "thesis_rules.yaml")

    if not config_path.exists():
        console.print(f"[red]pipeline.yaml not found: {config_path}[/red]")
        raise typer.Exit(1)
    if not rules_path.exists():
        console.print(f"[red]thesis_rules.yaml not found: {rules_path}[/red]")
        raise typer.Exit(1)

    cfg = load_pipeline_config(config_path)
    paths = PipelinePaths(session, cfg)
    paths.ensure_dirs()

    state_facts_path = paths.state_facts_csv
    scene_state_package_path = paths.scene_state_package
    domain_yaml_path = _resolve_domain_yaml(cfg)

    if not state_facts_path.exists():
        console.print(f"[red]state_facts.csv not found at {state_facts_path}. Run 09c first.[/red]")
        raise typer.Exit(1)
    if not scene_state_package_path.exists():
        console.print(
            f"[red]scene_state_package.json not found at {scene_state_package_path}. "
            "Run 09b first.[/red]"
        )
        raise typer.Exit(1)

    console.print(f"[dim]State facts: {state_facts_path}[/dim]")
    console.print(f"[dim]Scene state package: {scene_state_package_path}[/dim]")
    console.print(f"[dim]Domain config: {domain_yaml_path}[/dim]")
    console.print(f"[dim]Thesis rules: {rules_path}[/dim]")

    result = run_layer3_reasoning(
        state_facts=state_facts_path,
        scene_state_package=scene_state_package_path,
        domain_config=domain_yaml_path,
        thesis_rules=rules_path,
    )

    constraints_path = paths.processed_root / "constraints.csv"
    incompatibilities_path = paths.processed_root / "incompatibilities.csv"
    write_layer3_outputs(result, constraints_path, incompatibilities_path)

    fired_rules = set()
    if not result.constraints.empty:
        fired_rules.update(str(v) for v in result.constraints["rule_id"].dropna().unique())
    if not result.incompatibilities.empty:
        fired_rules.update(str(v) for v in result.incompatibilities["rule_id"].dropna().unique())

    console.print(f"\n[bold]Thesis Layer 3 - {session}[/bold]")
    console.print(f"  Constraints inferred:       {len(result.constraints)}")
    console.print(f"  Incompatibilities inferred: {len(result.incompatibilities)}")
    console.print(f"  Unique rules fired:         {len(fired_rules)}")
    if fired_rules:
        console.print(f"  Rules: {sorted(fired_rules)}")

    diag = result.diagnostics or {}
    console.print("\n[bold]Predicate source diagnostics[/bold]")
    console.print(f"  SSP fact instances imported: {diag.get('imported_ssp_predicate_count', 0)}")
    imported = diag.get("imported_ssp_predicates") or []
    if imported:
        console.print(
            "  Predicate types among imported SSP facts actually applied: "
            f"{imported}"
        )
    available = diag.get("available_predicates") or []
    if available:
        console.print(f"  Available predicates:       {available}")
    missing = diag.get("missing_rule_antecedents") or []
    if missing:
        console.print(f"  [red]Missing rule antecedents for {session}:[/red] {missing}")

    ssp_only = diag.get("ssp_only_predicates") or []
    state_only = diag.get("state_only_predicates") or []
    if ssp_only:
        console.print(f"  [yellow]Predicate types absent from state_facts:[/yellow] {ssp_only}")
    if state_only:
        console.print(f"  [yellow]Only in state_facts:[/yellow]   {state_only}")

    conf_diffs = diag.get("confidence_discrepancies") or []
    if conf_diffs:
        console.print(f"  [yellow]Confidence discrepancies:[/yellow] {len(conf_diffs)}")
        for item in conf_diffs[:5]:
            console.print(
                "    "
                f"{item['predicate']}{tuple(item['args'])}: "
                f"state={item['state_conf']} ssp={item['ssp_conf']} "
                f"delta={item['delta']}"
            )
        if len(conf_diffs) > 5:
            console.print(f"    ... {len(conf_diffs) - 5} more")

    console.print(f"[green]constraints.csv -> {constraints_path}[/green]")
    console.print(f"[green]incompatibilities.csv -> {incompatibilities_path}[/green]")


if __name__ == "__main__":
    app()
