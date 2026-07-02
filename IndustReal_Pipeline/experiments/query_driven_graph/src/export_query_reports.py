"""Export Markdown reports for query-driven graph runs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SHARED_EXPERIMENTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SHARED_EXPERIMENTS_DIR))

from shared.id_compaction import compact_prompt_text, compact_prompt_value, compact_step_id  # noqa: E402


CONDITION = "query_driven_graph"


def export_query_reports(
    rows: list[dict[str, Any]],
    output_dir: Path,
    run_statistics: dict[str, Any] | None = None,
) -> list[Path]:
    """Write grouped Markdown reports showing query evidence and final answers."""
    output_dir.mkdir(parents=True, exist_ok=True)
    group_field = "scenario" if any(row.get("scenario") for row in rows) else "risk_type"
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get(group_field) or "unclassified"), []).append(row)

    written_paths = []
    for group_name, group_rows in sorted(grouped.items()):
        path = output_dir / f"{_slug(group_name)}_query_driven_graph.md"
        path.write_text(
            render_query_report_group(
                group_name,
                group_field,
                group_rows,
                run_statistics or _derive_run_statistics(rows),
            ),
            encoding="utf-8",
        )
        written_paths.append(path)
    return written_paths


def render_query_report_group(
    group_name: str,
    group_field: str,
    rows: list[dict[str, Any]],
    run_statistics: dict[str, Any] | None = None,
) -> str:
    """Render one Markdown report containing all query-driven prompts for one group."""
    group_label = group_field.replace("_", " ").title()
    shared_prompt = _shared_system_prompt(rows)
    shared_step_context = _shared_step_context(rows)
    shared_step_reference = _first_value(rows, "step_id")
    graph_retrieval = _first_graph_retrieval(rows)
    case_sections = "".join(_case_section(row) for row in rows)

    return f"""# Prompt Report: {group_name}

Generated at: {datetime.now().astimezone().isoformat(timespec="seconds")}

- Condition: `{CONDITION}`
- {group_label}: `{group_name}`
- Cases in this report: `{len(rows)}`

## API Request Settings

{_render_llm_metadata(_first_llm(rows))}

## Run Timing Statistics

{_render_run_statistics(run_statistics)}

## Question Set

{_render_question_set(_first_question_set(rows))}

## Prompt-Safe Context Sources

{_render_context_sources(shared_step_context, graph_retrieval)}

The query-driven graph condition sends a deterministic Cypher query, its parameters, and returned Neo4j evidence for each case. Evaluation-only fields such as risk type, scenario, status, and expected answer elements are documented below but are not included as answer requirements.

{_render_graph_provenance(_first_graph_manifest(rows))}

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### Actual System Message Sent

- Role: `system`

```text
{shared_prompt or "No shared system prompt was stored in response rows."}
```

### Frozen Procedural Step List

This block is inserted into the user message for every case when configured.

```text
{compact_prompt_text(shared_step_context, shared_step_reference) if shared_step_context else "No step-list artifact was stored in response rows."}
```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.

{case_sections}
"""


def _case_section(row: dict[str, Any]) -> str:
    source_step_id = str(row.get("step_id") or "")
    query_rows = compact_prompt_value(row.get("query_rows") or [], source_step_id)
    query_params = compact_prompt_value(row.get("query_params") or {}, source_step_id)
    return f"""
## Case: {row.get('case_id')}

- Step id: `{compact_step_id(source_step_id)}`
- Operator question: {row.get("question")}
- Retrieval template: `{row.get('retrieval_template')}`
- Retrieval template description: `{row.get('retrieval_template_description') or 'not available'}`
- Query status: `{row.get('query_status')}`
- LLM status: `{row.get('llm_status')}`
- Interaction duration: `{_seconds(row.get('duration_seconds'))}`

### Cypher Query Executed

```cypher
{row.get("cypher") or ""}
```

### Query Parameters

```json
{json.dumps(query_params, indent=2, ensure_ascii=False, sort_keys=True)}
```

### Neo4j Query Result Sent To The LLM

```json
{json.dumps(query_rows, indent=2, ensure_ascii=False, sort_keys=True)}
```

{_prompt_section(row.get("prompt"), source_step_id)}

### Answer

{row.get("response") or ""}

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `{row.get("risk_type")}`
- Scenario: `{row.get("scenario")}`
- Status: `{row.get("status")}`
- Expected answer elements:
{_render_expected_elements(row.get("expected_answer_elements"))}
"""


def _prompt_section(prompt: Any, source_step_id: str) -> str:
    """Render the actual case-specific user prompt stored for this case."""
    if not isinstance(prompt, dict):
        return "### Actual User Message Sent\n\n`No LLM prompt was sent for this case.`"

    user_prompt = _case_specific_user_prompt(prompt.get("user_prompt"), source_step_id)
    return f"""### Actual User Message Sent

- Role: `user`

```text
{user_prompt or "No user prompt was stored for this case."}
```"""


def _case_specific_user_prompt(user_prompt: Any, source_step_id: str) -> str:
    """Remove shared step context from a stored user prompt for report readability."""
    text = compact_prompt_text(user_prompt or "", source_step_id)
    marker = "\nShared procedural step list:\n"
    if marker in text:
        text = text.split(marker, 1)[0].rstrip()
    return text


def _first_graph_manifest(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first manifest stored in response rows."""
    for row in rows:
        manifest = row.get("graph_manifest")
        if isinstance(manifest, dict):
            return manifest
    return None


def _first_question_set(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first question-set manifest stored in response rows."""
    for row in rows:
        question_set = row.get("question_set")
        if isinstance(question_set, dict):
            return question_set
    return None


def _first_graph_retrieval(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first graph-retrieval config block stored in response rows."""
    for row in rows:
        graph_retrieval = row.get("graph_retrieval")
        if isinstance(graph_retrieval, dict):
            return graph_retrieval
    return None


def _first_llm(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first LLM metadata block stored in response rows."""
    for row in rows:
        llm = row.get("llm")
        if isinstance(llm, dict):
            return llm
    return None


def _first_value(rows: list[dict[str, Any]], key: str) -> Any:
    """Return the first non-empty value for a response-row key."""
    for row in rows:
        value = row.get(key)
        if value:
            return value
    return None


def _shared_system_prompt(rows: list[dict[str, Any]]) -> str:
    """Return the first stored system prompt, which is shared across successful LLM calls."""
    for row in rows:
        prompt = row.get("prompt")
        if isinstance(prompt, dict) and prompt.get("system_prompt"):
            return str(prompt["system_prompt"])
    return ""


def _shared_step_context(rows: list[dict[str, Any]]) -> str:
    """Extract the shared procedural step-list block from the stored user prompt."""
    for row in rows:
        prompt = row.get("prompt")
        if not isinstance(prompt, dict):
            continue
        user_prompt = str(prompt.get("user_prompt") or "")
        marker = "\nShared procedural step list:\n"
        if marker in user_prompt:
            return user_prompt.split(marker, 1)[1].strip()
    return ""


def _render_question_set(question_set: dict[str, Any] | None) -> str:
    """Render the novice-question set used for a run."""
    if not question_set:
        return "- Question set: `not found in response rows`"
    return "\n".join([
        f"- Path: `{question_set.get('path') or 'unknown'}`",
        f"- ID: `{question_set.get('question_set_id') or 'unknown'}`",
        f"- Version: `{question_set.get('question_set_version') or 'unknown'}`",
        f"- Case count: `{question_set.get('case_count') or 'unknown'}`",
        f"- SHA-256: `{_short_hash(question_set.get('sha256'))}`",
    ])


def _render_llm_metadata(llm: dict[str, Any] | None) -> str:
    """Render report-safe LLM API settings for provenance."""
    if not llm:
        return "- LLM metadata: `not found in response rows`"
    return "\n".join([
        f"- LLM config path: `{llm.get('config_path') or 'unknown'}`",
        f"- API base URL: `{llm.get('api_base_url') or 'unknown'}`",
        f"- Model name: `{llm.get('model_name') or 'unknown'}`",
        f"- Temperature: `{_metadata_value(llm.get('temperature'))}`",
        f"- Max tokens: `{_metadata_value(llm.get('max_tokens'))}`",
        f"- Request timeout seconds: `{_metadata_value(llm.get('request_timeout_seconds'))}`",
        f"- Max retries: `{_metadata_value(llm.get('max_retries'))}`",
    ])


def _render_context_sources(step_context: str, graph_retrieval: dict[str, Any] | None) -> str:
    """Render prompt-safe context-source settings for query-driven graph reports."""
    retrieval = graph_retrieval or {}
    return "\n".join([
        "- Step-list artifact configured path: `not stored in response rows`",
        f"- Step-list artifact loaded: `{bool(step_context)}`",
        "- Windowed predicates included: `no`",
        "- Sequence step-hop radius: `not applicable`",
        "- Semantic evidence-hop radius: `not applicable`",
        "- Thesis rules included: `no`",
        "- Procedural reasoning graph included: `yes`",
        f"- Query template selection mode: `{retrieval.get('template_selection', 'deterministic')}`",
        f"- Neo4j row limit source: `{retrieval.get('row_limit_source', 'experiment config')}`",
    ])


def _render_graph_provenance(manifest: dict[str, Any] | None) -> str:
    """Render the Neo4j GraphManifest summary for a report."""
    if not manifest:
        return (
            "## Graph Provenance\n\n"
            "- Graph manifest: `not found in response rows`\n"
            "- Action: rebuild and re-import the graph with manifest support, then rerun the experiment."
        )

    return "\n".join([
        "## Graph Provenance",
        "",
        f"- Graph name: `{manifest.get('graph_name') or 'unknown'}`",
        f"- PRG id: `{manifest.get('prg_id') or 'unknown'}`",
        f"- Graph schema version: `{manifest.get('graph_schema_version') or 'unknown'}`",
        f"- Graph built at: `{manifest.get('built_at') or 'unknown'}`",
        f"- Graph builder: `{manifest.get('builder') or 'unknown'}`",
        _manifest_source_line(
            "Domain config",
            manifest,
            "domain_config",
            ["domain_model_version", "domain_config_schema_version"],
        ),
        _manifest_source_line(
            "Thesis rules",
            manifest,
            "thesis_rules",
            ["rule_set_version", "thesis_rules_schema_version"],
        ),
        _manifest_source_line(
            "Validation config",
            manifest,
            "validation_config",
            ["validation_rule_set_version", "validation_config_schema_version"],
        ),
    ])


def _manifest_source_line(label: str, manifest: dict[str, Any], prefix: str, version_keys: list[str]) -> str:
    """Format one manifest source line."""
    version = next((manifest.get(key) for key in version_keys if manifest.get(key)), "unknown")
    sha = _short_hash(manifest.get(f"{prefix}_sha256"))
    path = manifest.get(f"{prefix}_path") or "unknown"
    return f"- {label}: version `{version}`, sha256 `{sha}`, path `{path}`"


def _short_hash(value: Any) -> str:
    """Return a readable hash prefix while preserving explicit unknowns."""
    text = str(value or "")
    return text[:12] if text else "unknown"


def _metadata_value(value: Any) -> str:
    """Render a scalar metadata value."""
    return str(value) if value is not None else "unknown"


def _render_expected_elements(elements: Any) -> str:
    """Render expected answer elements as Markdown bullets."""
    if not elements:
        return "  - None"
    return "\n".join(f"  - {element}" for element in elements)


def _seconds(value: Any) -> str:
    """Render seconds for report fields."""
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.2f} s"
    except (TypeError, ValueError):
        return str(value)


def _render_run_statistics(statistics: dict[str, Any] | None) -> str:
    """Render run-wide timing statistics."""
    if not statistics:
        return "Timing statistics are unavailable because this report was exported outside an experiment run."
    return (
        "These statistics cover all successful prompt interactions in this experiment run.\n\n"
        f"- Completed interactions: `{statistics.get('completed_interactions')}`\n"
        f"- Failed interactions: `{statistics.get('failed_interactions', 0)}`\n"
        f"- Minimum prompt time: `{_seconds(statistics.get('min_interaction_seconds'))}`\n"
        f"- Maximum prompt time: `{_seconds(statistics.get('max_interaction_seconds'))}`\n"
        f"- Average prompt time: `{_seconds(statistics.get('avg_interaction_seconds'))}`\n"
        f"- Total experiment time: `{statistics.get('total_duration_hms') or 'n/a'}`"
    )


def _derive_run_statistics(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Derive timing statistics from stored response rows for standalone re-exports."""
    durations = [
        float(row["duration_seconds"])
        for row in rows
        if isinstance(row.get("duration_seconds"), int | float)
    ]
    if not rows:
        return None
    total_seconds = sum(durations) if durations else None
    return {
        "completed_interactions": len(rows),
        "failed_interactions": sum(row.get("llm_status") == "failed" for row in rows),
        "min_interaction_seconds": min(durations) if durations else None,
        "max_interaction_seconds": max(durations) if durations else None,
        "avg_interaction_seconds": (sum(durations) / len(durations)) if durations else None,
        "total_duration_hms": _format_duration_hms(total_seconds) if total_seconds is not None else "n/a",
    }


def _format_duration_hms(seconds: float) -> str:
    """Format elapsed seconds as hours, minutes, and seconds."""
    hours, remainder = divmod(max(0.0, seconds), 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {remaining_seconds:05.2f}s"


def _slug(value: str) -> str:
    text = str(value or "report").lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "report"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load response rows from a JSONL file."""
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object on line {line_number}: {path}")
            rows.append(row)
    return rows


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for standalone report export."""
    parser = argparse.ArgumentParser(description="Export query-driven graph Markdown reports from JSONL rows.")
    parser.add_argument("--responses", required=True, help="Path to responses_query_driven_graph_*.jsonl.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated Markdown reports.")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    paths = export_query_reports(_load_jsonl(Path(args.responses)), Path(args.output_dir))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
