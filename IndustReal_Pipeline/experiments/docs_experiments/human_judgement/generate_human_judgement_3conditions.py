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
    parser.add_argument("--answer-key-only", action="store_true", help="Write only the non-blind answer key.")
    parser.add_argument("--blind-only", action="store_true", help="Write only the blind packet.")
    parser.add_argument("--timestamp", help="Timestamp suffix to use in generated filenames.")
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
    _, separator, suffix = value.rpartition("step_")
    if separator and suffix.isdigit():
        return f"step_{suffix}"
    return value or "unknown"


def step_index_from_step_id(step_id: Any) -> str:
    """Return the numeric step index from a step ID, if present."""
    value = str(step_id or "")
    _, separator, suffix = value.rpartition("event_")
    if separator and suffix.isdigit():
        return suffix
    _, separator, suffix = value.rpartition("step_")
    if separator and suffix.isdigit():
        return suffix
    return ""


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


def infer_question_set_metadata(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Infer question-set metadata from response rows."""
    metadata: dict[str, str] = {}
    for row in rows:
        question_set = row.get("question_set")
        if not isinstance(question_set, dict):
            continue
        for source_key, output_key in (
            ("path", "path"),
            ("question_set_id", "id"),
            ("question_set_version", "version"),
            ("case_count", "case_count"),
            ("sha256", "sha256"),
        ):
            value = question_set.get(source_key)
            if value is not None and output_key not in metadata:
                metadata[output_key] = str(value)
    return metadata


def format_seconds(total_seconds: float) -> str:
    """Return a human-readable minutes/seconds label."""
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f"{minutes} min {seconds:.1f} s"


def mmss_to_seconds(value: str) -> float:
    """Convert an mm:ss.s label to seconds."""
    minutes, seconds = value.split(":", maxsplit=1)
    return int(minutes) * 60 + float(seconds)


def format_step_time_window(
    start_frame: str | None,
    end_frame: str | None,
    start_mmss: str | None = None,
    end_mmss: str | None = None,
) -> str:
    """Return a human-readable step time window."""
    if start_mmss:
        start_label = format_seconds(mmss_to_seconds(start_mmss))
    elif start_frame and start_frame not in {"None", "null", ""}:
        start_label = format_seconds(float(start_frame) / 10.0)
    else:
        start_label = "unknown start"

    if end_mmss and end_mmss not in {"None", "null", ""}:
        end_label = format_seconds(mmss_to_seconds(end_mmss))
    elif end_frame and end_frame not in {"None", "null", ""}:
        end_label = format_seconds(float(end_frame) / 10.0)
    else:
        end_label = "unknown end"

    return f"{start_label} - {end_label}"


def parse_step_time_windows(step_text: str) -> dict[str, str]:
    """Parse step time windows from a shared step-list text block."""
    windows: dict[str, str] = {}
    current_step: str | None = None
    start_frame: str | None = None
    end_frame: str | None = None

    def flush_step() -> None:
        if current_step is not None and start_frame is not None:
            windows[current_step] = format_step_time_window(start_frame, end_frame)

    for line in step_text.splitlines():
        seconds_step_match = re.match(
            r"Step (?P<index>\d+) \[(?P<start>\d+(?:\.\d+)?)-(?P<end>\d+(?:\.\d+)?)s\]:",
            line,
        )
        if seconds_step_match:
            current_step = None
            index = seconds_step_match.group("index")
            start_label = format_seconds(float(seconds_step_match.group("start")))
            end_label = format_seconds(float(seconds_step_match.group("end")))
            windows[index] = f"{start_label} - {end_label}"
            continue

        step_match = re.match(r"- Step (?P<index>\d+):", line)
        if step_match:
            flush_step()
            current_step = step_match.group("index")
            start_frame = None
            end_frame = None
            continue

        frame_match = re.search(r"time_window: start_frame=(?P<start>[^,\n]+), end_frame=(?P<end>[^\n]+)", line)
        if frame_match:
            start_frame = frame_match.group("start").strip()
            end_frame = frame_match.group("end").strip()
            continue

        mmss_match = re.search(r"time_window_mmss: start=(?P<start>[^,\n]+), end=(?P<end>[^\n]+)", line)
        if mmss_match and current_step is not None:
            windows[current_step] = format_step_time_window(
                start_frame,
                end_frame,
                start_mmss=mmss_match.group("start").strip(),
                end_mmss=mmss_match.group("end").strip(),
            )

    flush_step()
    return windows


def infer_step_list_path(rows: list[dict[str, Any]]) -> Path | None:
    """Infer the shared step-list artifact path from response provenance."""
    for row in rows:
        provenance = row.get("step_provenance")
        if not isinstance(provenance, dict):
            continue
        evidence_mode = provenance.get("evidence_mode")
        archive = provenance.get("archive")
        clip_id = provenance.get("clip_id")
        if not (evidence_mode and archive and clip_id):
            continue
        path = Path("experiments") / "shared" / "data" / f"steps_{evidence_mode}_{archive}_{clip_id}.txt"
        if path.exists():
            return path
    return None


def infer_step_time_windows(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Infer per-step time windows as human-readable minutes/seconds labels."""
    step_list_path = infer_step_list_path(rows)
    if step_list_path:
        return parse_step_time_windows(step_list_path.read_text(encoding="utf-8"))

    windows: dict[str, str] = {}
    for row in rows:
        prompt = row.get("prompt")
        if isinstance(prompt, dict):
            prompt_text = "\n".join(str(value) for value in prompt.values())
        elif isinstance(prompt, str):
            prompt_text = prompt
        else:
            continue
        windows.update(parse_step_time_windows(prompt_text))
    return windows


def step_time_window_label(row: dict[str, Any], step_time_windows: dict[str, str]) -> str:
    """Return the time-window label for a response row's target step."""
    step_index = step_index_from_step_id(row.get("step_id"))
    if not step_index:
        provenance = row.get("step_provenance")
        if isinstance(provenance, dict) and provenance.get("step_index") is not None:
            step_index = str(provenance["step_index"])
    if not step_index:
        return "N/A"
    labels_to_try = [step_index]
    if step_index.isdigit():
        labels_to_try.append(str(int(step_index)))
        labels_to_try.append(f"{int(step_index):02d}")
    for label in labels_to_try:
        if label in step_time_windows:
            return step_time_windows[label]
    return "N/A"


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
    question_set_metadata: dict[str, str],
    step_time_windows: dict[str, str],
    condition_count: int,
) -> str:
    """Render the blind judgement packet."""
    lines = [
        f"# Human Judgement Packet - {condition_count} Conditions, Blind Items",
        "",
        f"Generated at: `{generated_at}`",
        f"Random seed: `{seed}`",
        f"Clip name: `{clip_name}`",
        f"Question set path: `{question_set_metadata.get('path') or 'unknown'}`",
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
        expected_answer_lines = render_expected_answer_elements(row.get("expected_answer_elements"))
        lines.extend(
            [
                f"## Item {index:02d}",
                "",
                f"- Clip name: `{clip_name}`",
                f"- Step: `{compact_step_id(row.get('step_id'))}`",
                f"- Step time window: `{step_time_window_label(row, step_time_windows)}`",
                f"- Question: {row.get('question') or ''}",
                *expected_answer_lines,
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


def render_expected_answer_elements(elements: Any) -> list[str]:
    """Render evaluation target elements beside the blind question."""
    if not isinstance(elements, list) or not elements:
        return ["- Expected answer elements: none recorded"]
    lines = ["- Expected answer elements:"]
    for element in elements:
        lines.append(f"  - {element}")
    return lines


def render_answer_key(
    items: list[dict[str, Any]],
    source_paths: dict[str, str],
    *,
    generated_at: str,
    seed: int,
    clip_name: str,
    question_set_metadata: dict[str, str],
    step_time_windows: dict[str, str],
    condition_count: int,
) -> str:
    """Render the non-blind answer key."""
    lines = [
        f"# Human Judgement Answer Key - {condition_count} Conditions",
        "",
        f"Generated at: `{generated_at}`",
        f"Random seed: `{seed}`",
        f"Clip name: `{clip_name}`",
        f"Question set path: `{question_set_metadata.get('path') or 'unknown'}`",
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
            "## Question Set",
            "",
            f"- Path: `{question_set_metadata.get('path') or 'unknown'}`",
            f"- ID: `{question_set_metadata.get('id') or 'unknown'}`",
            f"- Version: `{question_set_metadata.get('version') or 'unknown'}`",
            f"- Case count: `{question_set_metadata.get('case_count') or 'unknown'}`",
            f"- SHA-256: `{question_set_metadata.get('sha256') or 'unknown'}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Item Mapping",
            "",
            "| Item | Case ID | Condition | Step | Step time window | Scenario | Status | Duration seconds |",
            "|---:|---|---|---|---|---|---|---:|",
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
            f"`{step_time_window_label(row, step_time_windows)}` | "
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
    if args.answer_key_only and args.blind_only:
        raise ValueError("Use only one of --answer-key-only or --blind-only.")
    timestamp = args.timestamp or local_timestamp_for_filename()
    generated_at = local_timestamp_iso()
    seed = args.seed if args.seed is not None else int(datetime.now().astimezone().strftime("%Y%m%d%H%M%S"))
    args.seed = seed
    items, source_paths = build_items(args)
    condition_count = len(source_paths)
    clip_name = args.clip_name or infer_clip_name(items)
    question_set_metadata = infer_question_set_metadata(items)
    step_time_windows = infer_step_time_windows(items)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    clip_slug = safe_filename_part(clip_name)
    blind_path = output_dir / f"human_judgement_{condition_count}conditions_{clip_slug}_blind_items_{timestamp}.md"
    answer_key_path = output_dir / f"human_judgement_{condition_count}conditions_{clip_slug}_answer_key_{timestamp}.md"
    if not args.answer_key_only:
        blind_path.write_text(
            render_blind_packet(
                items,
                generated_at=generated_at,
                seed=seed,
                clip_name=clip_name,
                question_set_metadata=question_set_metadata,
                step_time_windows=step_time_windows,
                condition_count=condition_count,
            ),
            encoding="utf-8",
        )
    if not args.blind_only:
        answer_key_path.write_text(
            render_answer_key(
                items,
                source_paths,
                generated_at=generated_at,
                seed=seed,
                clip_name=clip_name,
                question_set_metadata=question_set_metadata,
                step_time_windows=step_time_windows,
                condition_count=condition_count,
            ),
            encoding="utf-8",
        )
    if not args.answer_key_only:
        print(f"Wrote blind packet: {blind_path}")
    if not args.blind_only:
        print(f"Wrote answer key: {answer_key_path}")

    if args.write_docx:
        try:
            if not args.answer_key_only:
                print(f"Wrote blind DOCX: {write_docx(blind_path)}")
            if not args.blind_only:
                print(f"Wrote answer-key DOCX: {write_docx(answer_key_path)}")
        except FileNotFoundError as exc:
            print(f"Skipped DOCX conversion: {exc}")


if __name__ == "__main__":
    main()
