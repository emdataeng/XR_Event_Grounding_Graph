#!/usr/bin/env python3
"""Export IndustReal assembly graphs to Neo4j-ready CSV files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.neo4j_export import DEFAULT_MODES, DEFAULT_RUN_ID, export_industreal_neo4j_csvs
from src.raw_cad_config import RawCadPaths, load_raw_cad_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "raw_cad_dataset.json")
    parser.add_argument("--run-id", type=str, default=DEFAULT_RUN_ID)
    parser.add_argument("--modes", nargs="*", default=list(DEFAULT_MODES))
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--reports-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--cad-state-catalog", type=Path, default=None)
    parser.add_argument("--cad-part-catalog", type=Path, default=None)
    parser.add_argument("--phase-rules", type=Path, default=ROOT / "configs" / "assembly_phase_rules.json")
    args = parser.parse_args()

    cfg = load_raw_cad_config(args.config)
    paths = RawCadPaths(cfg)
    results_dir = args.results_dir or paths.dataset_run_results_dir(args.run_id)
    reports_dir = args.reports_dir or paths.dataset_run_reports_dir(args.run_id)
    output_dir = args.output_dir or (ROOT / "results" / "neo4j" / args.run_id)

    counts = export_industreal_neo4j_csvs(
        results_dir=results_dir,
        output_dir=output_dir,
        run_id=args.run_id,
        modes=args.modes,
        reports_dir=reports_dir,
        cad_state_catalog_path=args.cad_state_catalog,
        cad_part_catalog_path=args.cad_part_catalog,
        phase_rules_path=args.phase_rules,
    )
    print(json.dumps({"output_dir": str(output_dir), "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
