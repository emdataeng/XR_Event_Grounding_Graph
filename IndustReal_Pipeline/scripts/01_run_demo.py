#!/usr/bin/env python3
"""01_run_demo.py — IndustReal PSR proof-of-concept end-to-end demo.

Processes two real recordings from the IndustReal test set:
  03_assy_0_1  —  clean assembly (participant succeeds, ASD model works)
  03_assy_1_3  —  error case     (participant makes error, ASD model fails entirely)

For each recording:
  1. Load real ASD pred/GT CSVs.
  2. Derive PSR ground-truth labels from GT state transitions.
  3. Run PSR B3 (AccumulatedConfidencePSR with procedure='assy').
  4. Evaluate: POS, F1, avg_delay_s.
  5. Build EGG-style AssemblyGraph for GT and predictions.
  6. Print rich summary.

Usage:
    cd /workspaces/XR_EGG-Claude/IndustReal_Pipeline
    python scripts/01_run_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from repo root or from IndustReal_Pipeline/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_recording
from src.psr import run_psr, evaluate
from src.egg_builder import build_assembly_graph, diff_graphs

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR  = ROOT / "data" / "ASD_results" / "ASD_IndustRealplusSynthetic_test"
PROC_INFO = ROOT / "configs" / "procedure_info.json"

RECORDINGS = [
    ("03_assy_0_1", "Clean assembly — participant succeeds"),
    ("03_assy_1_3", "Error case    — participant makes error, ASD model fails"),
]

# PSR B3 hyper-parameters (IndustReal paper defaults).
PSR_KWARGS = dict(
    implementation      = "expected",
    procedure           = "assy",
    cum_conf_threshold  = 8.0,
    cum_decay           = 0.75,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 70

def _sep(title: str = ""):
    if title:
        print(f"\n{DIVIDER}\n  {title}\n{DIVIDER}")
    else:
        print(DIVIDER)


def _fmt_steps(steps: list, label: str):
    print(f"\n  {label} ({len(steps)} steps):")
    if not steps:
        print("    (none)")
    for s in steps:
        t_s = s["frame"] / 10
        print(f"    [{t_s:6.1f}s] id={s['id']:2d}  {s['description']}")


def _fmt_metrics(metrics: dict):
    print(f"\n  Metrics:")
    print(f"    POS        : {metrics['pos']:.4f}   (1.0 = perfect order)")
    print(f"    F1         : {metrics['f1']:.4f}")
    delay = metrics['avg_delay_s']
    delay_str = f"{delay:.2f} s" if delay is not None else "N/A"
    print(f"    Avg delay  : {delay_str}")
    print(f"    TP / FP / FN : {metrics['system_TPs']} / {metrics['system_FPs']} / {metrics['system_FNs']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    proc_info = json.loads(PROC_INFO.read_text())

    _sep("IndustReal PSR — Proof of Concept")
    print(f"  Procedure info  : {len(proc_info)} action steps")
    print(f"  PSR algorithm   : B3 (AccumulatedConfidence + procedure='assy')")
    print(f"  Recordings      : {len(RECORDINGS)}")

    for clip_name, description in RECORDINGS:
        pred_csv = DATA_DIR / f"{clip_name}_results_pred.csv"
        gt_csv   = DATA_DIR / f"{clip_name}_results_gt.csv"

        _sep(f"{clip_name}  —  {description}")

        # ── Load ─────────────────────────────────────────────────────────────
        rec = load_recording(pred_csv, gt_csv, proc_info)

        print(f"\n  Clip     : {rec['clip']}")
        print(f"  Frames   : {rec['n_frames']}  ({rec['n_frames'] / 10:.1f} s at 10 fps)")
        print(f"  Has pred : {rec['has_pred']}")

        if not rec["has_pred"]:
            print("\n  *** ASD model produced ZERO predictions for this clip. ***")
            print("  This is expected: the participant hit an error-state (class 23)")
            print("  which the model was not trained to handle in a sequential context.")

        # ── GT steps ─────────────────────────────────────────────────────────
        _fmt_steps(rec["psr_gt"], "GT steps (derived from state transitions)")

        # ── PSR prediction ────────────────────────────────────────────────────
        psr_pred = run_psr(rec["asd_pred"], proc_info, **PSR_KWARGS)
        _fmt_steps(psr_pred, "Predicted steps (PSR B3)")

        # ── Evaluation ───────────────────────────────────────────────────────
        metrics = evaluate(rec["psr_gt"], psr_pred, proc_info)
        _fmt_metrics(metrics)

        # ── EGG graphs ────────────────────────────────────────────────────────
        gt_graph   = build_assembly_graph(clip_name, rec["n_frames"], rec["psr_gt"], proc_info)
        pred_graph = build_assembly_graph(clip_name, rec["n_frames"], psr_pred,     proc_info)

        print(f"\n{diff_graphs(gt_graph, pred_graph)}")

    _sep("Done")


if __name__ == "__main__":
    main()
