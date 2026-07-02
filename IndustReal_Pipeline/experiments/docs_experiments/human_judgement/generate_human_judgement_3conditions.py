"""Generate blind human-judgement packets for experiment conditions."""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


CONDITION_LABELS = {
    "steps_only": "steps_only",
    "symbolic_domain": "symbolic_domain",
    "graph_grounded": "graph_grounded",
    "query_driven_graph": "query_driven_graph",
}

SCORING_SECTION = """## How to Score

Use the criteria from `Evaluator Instructions.pdf`. Score each answer independently on its own merits, without trying to infer which condition produced it and without comparing it to other answers. Use the full task reference material as the source of truth.

Assign a score from `1` to `5` for each criterion:

| Criterion | What to evaluate |
|---|---|
| Correctness | Whether the answer is technically accurate, consistent with the reference material, and free of false or misleading claims. |
| Completeness | Whether the answer covers all relevant information needed to address the operator's question. |
| Safety | Whether the answer mentions relevant risks, warnings, missing checks, or precautions, and avoids forcing irrelevant safety content when safety is not applicable. |
| Actionability / Usefulness | Whether a novice operator could act on the answer immediately without needing a follow-up question. |
| Explainability | Whether the answer explains the reasoning behind the instruction when that explanation would help the operator. Do not penalize brief factual answers that genuinely need little explanation. |

Score anchors: `1` means poor or unusable for that criterion, `3` means partially adequate with noticeable gaps, and `5` means fully satisfactory. Scores across criteria may differ for the same answer. Add notes for edge cases or uncertain judgements.
"""

JUDGE_SCORE_TABLE = """### Judge Scores

| Criterion | Score | Notes |
|---|---:|---|
| Correctness |  |  |
| Completeness |  |  |
| Safety |  |  |
| Actionability / Usefulness |  |  |
| Explainability |  |  |
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps-only", required=True, help="responses_steps_only*.jsonl")
    parser.add_argument("--symbolic-domain", required=True, help="responses_symbolic_domain*.jsonl")
    parser.add_argument("--graph-grounded", help="responses_graph_grounded*.jsonl")
    parser.add_argument("--query-driven-graph", required=True, help="responses_query_driven_graph*.jsonl")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Directory for generated Markdown and optional DOCX files.",
    )
    parser.add_argument("--clip-name", help="Clip label to show in generated packets.")
    parser.add_argument("--seed", type=int, help="Random seed for global item shuffling.")
    parser.add_argument("--write-docx", action="store_true", help="Also write DOCX files with pandoc.")
    return parser.parse_args()


def local_timestamp_for_filename() -> str:
    """Return a local timestamp with timezone offset for generated artifact names."""
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def local_timestamp_iso() -> str:
    """Return a local ISO timestamp with seconds and timezone offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_filename_part(value: str) -> str:
    """Return a filesystem-safe lowercase label for generated artifact names."""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    safe = re.sub(r"_+", "_", safe).strip("._-")
    return safe.lower() or "unknown_clip"


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL response rows."""
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_number}: {exc}") from exc
    return rows


def compact_step_id(step_id: Any) -> str:
    """Return a readable step label such as step_7."""
    value = str(step_id or "")
    _, separator, suffix = value.rpartition("event_")
    if separator and suffix.isdigit():
        return f"step_{suffix}"
    return value or "unknown"


def infer_clip_name(rows: list[dict[str, Any]]) -> str:
    """Infer clip name from response metadata."""
    for row in rows:
        provenance = row.get("step_provenance")
        if isinstance(provenance, dict) and provenance.get("clip_id"):
            return str(provenance["clip_id"])
        step_id = str(row.get("step_id") or "")
        parts = step_id.split("::")
        if len(parts) >= 2 and parts[-2].startswith("event_"):
            return parts[-1]
        if len(parts) >= 1 and parts[-1] and not parts[-1].startswith("event_"):
            return parts[-1]
    return "unknown"


def response_status(row: dict[str, Any]) -> str:
    """Return a normalized status for answer-key metadata."""
    if "response_status" in row:
        return str(row.get("response_status") or "unknown")
    if "llm_status" in row:
        return str(row.get("llm_status") or "unknown")
    return "unknown"


def normalize_condition_rows(condition: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach condition labels to response rows."""
    normalized = []
    for row in rows:
        item = dict(row)
        item["condition"] = condition
        normalized.append(item)
    return normalized


def build_items(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Load, label, and shuffle response rows."""
    source_paths = {
        "steps_only": args.steps_only,
        "symbolic_domain": args.symbolic_domain,
        "query_driven_graph": args.query_driven_graph,
    }
    if args.graph_grounded:
        source_paths = {
            "steps_only": args.steps_only,
            "symbolic_domain": args.symbolic_domain,
            "graph_grounded": args.graph_grounded,
            "query_driven_graph": args.query_driven_graph,
        }
    grouped_rows = {
        condition: normalize_condition_rows(condition, load_jsonl(path))
        for condition, path in source_paths.items()
    }
    case_counts = {condition: len(rows) for condition, rows in grouped_rows.items()}
    if len(set(case_counts.values())) != 1:
        raise ValueError(f"Expected equal row counts across conditions, got {case_counts}")

    items = [row for rows in grouped_rows.values() for row in rows]
    rng = random.Random(args.seed)
    rng.shuffle(items)
    return items, source_paths


def render_blind_packet(
    items: list[dict[str, Any]],
    *,
    generated_at: str,
    seed: int,
    clip_name: str,
    condition_count: int,
) -> str:
    """Render the blind judgement packet."""
    lines = [
        f"# Human Judgement Packet - {condition_count} Conditions, Blind Items",
        "",
        f"Generated at: `{generated_at}`",
        f"Random seed: `{seed}`",
        f"Clip name: `{clip_name}`",
        "",
        "This packet contains one question-answer pair per item.",
        "The order of all items is randomized globally across questions and hidden conditions.",
        f"Each original question appears {condition_count} times, once for each hidden condition.",
        "Condition names are not shown in this blind packet.",
        "",
        SCORING_SECTION,
        "",
    ]
    for index, row in enumerate(items, start=1):
        lines.extend(
            [
                f"## Item {index:02d}",
                "",
                f"- Clip name: `{clip_name}`",
                f"- Step: `{compact_step_id(row.get('step_id'))}`",
                f"- Question: {row.get('question') or ''}",
                "",
                "### Answer",
                "",
                str(row.get("response") or ""),
                "",
                JUDGE_SCORE_TABLE,
                "",
                "---",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_answer_key(
    items: list[dict[str, Any]],
    source_paths: dict[str, str],
    *,
    generated_at: str,
    seed: int,
    clip_name: str,
    condition_count: int,
) -> str:
    """Render the non-blind answer key."""
    lines = [
        f"# Human Judgement Answer Key - {condition_count} Conditions",
        "",
        f"Generated at: `{generated_at}`",
        f"Random seed: `{seed}`",
        f"Clip name: `{clip_name}`",
        "",
        "Do not share this file with judges before scoring.",
        "",
        SCORING_SECTION,
        "",
        "## Source Files",
        "",
    ]
    for condition, path in source_paths.items():
        lines.append(f"- `{condition}`: `{path}`")
    lines.extend(
        [
            "",
            "## Item Mapping",
            "",
            "| Item | Case ID | Condition | Step | Scenario | Status | Duration seconds |",
            "|---:|---|---|---|---|---|---:|",
        ]
    )
    for index, row in enumerate(items, start=1):
        duration = row.get("duration_seconds")
        duration_label = "" if duration is None else str(duration)
        lines.append(
            "| "
            f"{index:02d} | "
            f"`{row.get('case_id') or ''}` | "
            f"`{row.get('condition') or ''}` | "
            f"`{compact_step_id(row.get('step_id'))}` | "
            f"`{row.get('scenario') or row.get('risk_type') or ''}` | "
            f"`{response_status(row)}` | "
            f"`{duration_label}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_docx(markdown_path: Path) -> Path:
    """Convert Markdown to DOCX using pandoc."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        try:
            import pypandoc
        except ImportError as exc:
            raise FileNotFoundError("pandoc was not found on PATH and pypandoc is not installed") from exc

        pandoc = pypandoc.get_pandoc_path()
    docx_path = markdown_path.with_suffix(".docx")
    subprocess.run([pandoc, str(markdown_path), "-o", str(docx_path)], check=True)
    return docx_path


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    timestamp = local_timestamp_for_filename()
    generated_at = local_timestamp_iso()
    seed = args.seed if args.seed is not None else int(datetime.now().astimezone().strftime("%Y%m%d%H%M%S"))
    args.seed = seed
    items, source_paths = build_items(args)
    condition_count = len(source_paths)
    clip_name = args.clip_name or infer_clip_name(items)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    clip_slug = safe_filename_part(clip_name)
    blind_path = output_dir / f"human_judgement_{condition_count}conditions_{clip_slug}_blind_items_{timestamp}.md"
    answer_key_path = output_dir / f"human_judgement_{condition_count}conditions_{clip_slug}_answer_key_{timestamp}.md"
    blind_path.write_text(
        render_blind_packet(
            items,
            generated_at=generated_at,
            seed=seed,
            clip_name=clip_name,
            condition_count=condition_count,
        ),
        encoding="utf-8",
    )
    answer_key_path.write_text(
        render_answer_key(
            items,
            source_paths,
            generated_at=generated_at,
            seed=seed,
            clip_name=clip_name,
            condition_count=condition_count,
        ),
        encoding="utf-8",
    )
    print(f"Wrote blind packet: {blind_path}")
    print(f"Wrote answer key: {answer_key_path}")

    if args.write_docx:
        try:
            print(f"Wrote blind DOCX: {write_docx(blind_path)}")
            print(f"Wrote answer-key DOCX: {write_docx(answer_key_path)}")
        except FileNotFoundError as exc:
            print(f"Skipped DOCX conversion: {exc}")


if __name__ == "__main__":
    main()
