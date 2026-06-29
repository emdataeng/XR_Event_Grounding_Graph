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
        ]
        for row in group_rows:
            lines.extend(_case_section(row))
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _case_section(row: dict[str, Any]) -> list[str]:
    return [
        f"## {row.get('case_id')}",
        "",
        f"- Step id: `{row.get('step_id')}`",
        f"- Intent: `{row.get('intent')}`",
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


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "report"
