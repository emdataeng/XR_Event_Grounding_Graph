"""Build deterministic per-step predicate contexts over a sequence window."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPERIMENTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(EXPERIMENTS_DIR))

from context_builders import canonical_step_id
from shared.graph_retrieval_config import load_graph_retrieval_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step-records", type=Path, required=True)
    parser.add_argument("--predicates", type=Path, required=True)
    parser.add_argument(
        "--graph-retrieval-config",
        type=Path,
        default=EXPERIMENTS_DIR / "shared" / "configs" / "graph_retrieval.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _predicate_prompt_line(record: dict[str, Any]) -> str:
    """Project a predicate to the semantic fields used by rule matching."""
    step_suffix = canonical_step_id(record.get("step_id")).rpartition("::")[2]
    name = str(record.get("name") or "unknown")
    args = json.dumps(record.get("args") or [], ensure_ascii=False, separators=(",", ":"))
    confidence = record.get("conf", record.get("confidence"))
    return f"{step_suffix}: {name}{args} [conf={confidence}]"


def build_predicate_contexts(step_records_path: Path, predicates_path: Path, hops: int) -> dict[str, Any]:
    """Build contexts using index order and preserve original predicate lines."""
    steps = _read_jsonl(step_records_path)
    steps.sort(key=lambda record: record.get("index") if record.get("index") is not None else 10**9)
    ordered_ids = [str(record.get("id") or record.get("step_id") or "") for record in steps]
    ordered_ids = [step_id for step_id in ordered_ids if step_id]

    predicates_by_step: dict[str, list[str]] = {}
    unscoped_predicate_count = 0
    for record in _read_jsonl(predicates_path):
        predicate_step_id = canonical_step_id(record.get("step_id"))
        if not predicate_step_id:
            unscoped_predicate_count += 1
            continue
        predicates_by_step.setdefault(predicate_step_id, []).append(_predicate_prompt_line(record))

    contexts = {}
    for index, center_step_id in enumerate(ordered_ids):
        start = max(0, index - hops)
        end = min(len(ordered_ids), index + hops + 1)
        included_step_ids = ordered_ids[start:end]
        predicate_lines = []
        for included_step_id in included_step_ids:
            predicate_lines.extend(predicates_by_step.get(canonical_step_id(included_step_id), []))
        contexts[canonical_step_id(center_step_id)] = {
            "center_step_id": center_step_id,
            "included_step_ids": included_step_ids,
            "predicate_count": len(predicate_lines),
            "predicate_lines": predicate_lines,
        }

    return {
        "schema_version": "llm_guidance_predicate_contexts.v1",
        "predicate_projection": ["step_id", "name", "args", "conf"],
        "step_hops": hops,
        "step_count": len(ordered_ids),
        "unscoped_predicate_count": unscoped_predicate_count,
        "contexts": contexts,
    }


def main() -> None:
    args = parse_args()
    retrieval = load_graph_retrieval_config(args.graph_retrieval_config)
    artifact = build_predicate_contexts(
        args.step_records,
        args.predicates,
        retrieval["step_hops"],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
