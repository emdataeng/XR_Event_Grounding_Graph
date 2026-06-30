"""Export Markdown reports for query-driven graph runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_query_reports(rows: list[dict[str, Any]], output_dir: Path) -> None:
    """Write grouped Markdown reports showing query evidence and final answers."""
    output_dir.mkdir(parents=True, exist_ok=True)
    group_field = "scenario" if any(row.get("scenario") for row in rows) else "risk_type"
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get(group_field) or "unclassified"), []).append(row)

    for group_name, group_rows in sorted(grouped.items()):
        path = output_dir / f"{_slug(group_name)}_query_driven_graph.md"
        lines = [
            f"# {group_name} - query_driven_graph",
            "",
            "This report shows the deterministic query plan, Neo4j rows, and final answer for each case.",
            "",
            "## Graph Manifest",
            "",
            *_graph_manifest_lines(_first_graph_manifest(group_rows)),
            "",
            "## Question Set",
            "",
            *_question_set_lines(_first_question_set(group_rows)),
            "",
        ]
        for row in group_rows:
            lines.extend(_case_section(row))
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _case_section(row: dict[str, Any]) -> list[str]:
    return [
        f"## {row.get('case_id')}",
        "",
        f"- Step id: `{row.get('step_id')}`",
        f"- Retrieval template: `{row.get('retrieval_template')}`",
        f"- Query status: `{row.get('query_status')}`",
        "",
        "### Operator Question",
        "",
        str(row.get("question") or ""),
        "",
        "### Cypher",
        "",
        "```cypher",
        str(row.get("cypher") or ""),
        "```",
        "",
        "### Parameters",
        "",
        "```json",
        json.dumps(row.get("query_params") or {}, indent=2, ensure_ascii=False, sort_keys=True),
        "```",
        "",
        "### Query Rows",
        "",
        "```json",
        json.dumps(row.get("query_rows") or [], indent=2, ensure_ascii=False, sort_keys=True),
        "```",
        "",
        "### Answer",
        "",
        str(row.get("response") or ""),
        "",
        "### Evaluation Metadata",
        "",
        "These fields are saved for evaluation only and are not sent as answer requirements.",
        "",
        "```json",
        json.dumps(
            {
                "scenario": row.get("scenario"),
                "risk_type": row.get("risk_type"),
                "status": row.get("status"),
                "expected_answer_elements": row.get("expected_answer_elements"),
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "```",
        "",
    ]


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


def _question_set_lines(question_set: dict[str, Any] | None) -> list[str]:
    """Render the novice-question set used for a run."""
    if not question_set:
        return ["- Question set: `not found in response rows`"]
    return [
        f"- Path: `{question_set.get('path') or 'unknown'}`",
        f"- ID: `{question_set.get('question_set_id') or 'unknown'}`",
        f"- Version: `{question_set.get('question_set_version') or 'unknown'}`",
        f"- Case count: `{question_set.get('case_count') or 'unknown'}`",
        f"- SHA-256: `{_short_hash(question_set.get('sha256'))}`",
    ]


def _graph_manifest_lines(manifest: dict[str, Any] | None) -> list[str]:
    """Render the Neo4j GraphManifest summary for a report."""
    if not manifest:
        return [
            "- Graph manifest: `not found in response rows`",
            "- Action: rebuild and re-import the graph with manifest support, then rerun the experiment.",
        ]

    return [
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
    ]


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


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "report"
