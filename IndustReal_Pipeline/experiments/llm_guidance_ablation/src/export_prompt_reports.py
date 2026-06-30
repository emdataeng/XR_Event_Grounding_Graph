"""Export report-ready Markdown files showing prompts sent to the LLM."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from context_builders import PromptCondition, build_context, graph_evidence_for_step, predicate_context_for_step
from graph_loader import extract_step_subgraph

SHARED_EXPERIMENTS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SHARED_EXPERIMENTS_DIR))

from shared.id_compaction import compact_prompt_text, compact_step_id  # noqa: E402


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for prompt report export."""
    parser = argparse.ArgumentParser(description="Export Markdown prompt reports for test cases.")
    parser.add_argument("--config", default=str(EXPERIMENT_ROOT / "configs" / "config.yaml"))
    parser.add_argument("--condition", choices=[condition.value for condition in PromptCondition], default="steps_only")
    parser.add_argument("--output-dir", help="Directory for generated Markdown reports.")
    return parser.parse_args()


def export_prompt_reports(
    config: dict[str, Any],
    condition: PromptCondition,
    output_dir: Path | None = None,
    test_cases: list[dict[str, Any]] | None = None,
    artifacts: dict[str, Any] | None = None,
    run_statistics: dict[str, Any] | None = None,
) -> list[Path]:
    """Write one Markdown file per scenario or risk type documenting LLM requests."""
    if test_cases is None or artifacts is None:
        from run_experiment import load_artifacts, load_test_cases

        test_cases = load_test_cases(config)
        artifacts = load_artifacts(config, condition=condition)

    report_dir = output_dir or (EXPERIMENT_ROOT / "outputs" / "prompt_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    written_paths = []
    group_field = _report_group_field(test_cases)
    for group_name, grouped_cases in _group_cases(test_cases, group_field).items():
        path = report_dir / f"{_slug(group_name)}_{condition.value}.md"
        path.write_text(
            render_prompt_report_group(
                config,
                condition,
                group_name,
                group_field,
                grouped_cases,
                artifacts,
                run_statistics=run_statistics,
            ),
            encoding="utf-8",
        )
        written_paths.append(path)
    return written_paths


def render_prompt_report_group(
    config: dict[str, Any],
    condition: PromptCondition,
    group_name: str,
    group_field: str,
    test_cases: list[dict[str, Any]],
    artifacts: dict[str, Any],
    run_statistics: dict[str, Any] | None = None,
) -> str:
    """Render one Markdown report containing all prompts for one report group."""
    step_list_loaded = bool(artifacts.get("step_list"))
    symbolic_domain_included = condition is PromptCondition.SYMBOLIC_DOMAIN
    graph_grounded_included = condition is PromptCondition.GRAPH_GROUNDED
    shared_context = build_context(condition, test_cases[0], artifacts)
    report_step_list = compact_prompt_text(
        artifacts.get("step_list") or "",
        test_cases[0].get("step_id"),
    )
    case_sections = [render_prompt_case_section(test_case, condition, artifacts) for test_case in test_cases]
    shared_rules = _render_shared_rules(condition, artifacts)

    group_label = group_field.replace("_", " ").title()

    return f"""# Prompt Report: {group_name}

Generated at: {datetime.now().astimezone().isoformat(timespec="seconds")}

- Condition: `{condition.value}`
- {group_label}: `{group_name}`
- Cases in this report: `{len(test_cases)}`

## API Request Settings

- API base URL: `{config.get("api_base_url")}`
- Model name: `{config.get("model_name")}`
- Temperature: `{config.get("temperature")}`
- Max tokens: `{config.get("max_tokens")}`

## Run Timing Statistics

{_render_run_statistics(run_statistics)}

## Question Set

{_render_question_set(artifacts.get("question_set"))}

## Prompt-Safe Context Sources

- Step-list artifact configured path: `{config.get("input_paths", {}).get("step_list")}`
- Step-list artifact loaded: `{step_list_loaded}`
- Windowed predicates included: `{'yes' if symbolic_domain_included else 'no'}`
- Sequence step-hop radius: `{artifacts.get("step_hops") if symbolic_domain_included or graph_grounded_included else 'not applicable'}`
- Semantic evidence-hop radius: `{artifacts.get("evidence_hops") if graph_grounded_included else 'not applicable'}`
- Thesis rules included: `{'yes' if symbolic_domain_included else 'no'}`
- Procedural reasoning graph included: `{'yes' if graph_grounded_included else 'no'}`

All conditions include the same frozen step-list artifact. The `symbolic_domain` condition adds a deterministic predicate window and `thesis_rules.yaml`; `graph_grounded` adds a deterministic local graph neighborhood.

{_render_graph_provenance(condition, artifacts)}

## Shared Prompt Content

The following content is identical for every case in this report and is shown only once.

### System Message

- Role: `system`

```text
{shared_context["system_prompt"]}
```

### Frozen Procedural Step List

This block is inserted into the user message for every case.

```text
{report_step_list or "No step-list artifact loaded."}
```

{shared_rules}

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message instead of separate `system` and `user` messages.

The fallback message has two sections:

- `Instructions`: contains the same system prompt shown in Message 1.
- `User question`: contains the same shared and case-specific content documented in this report.

No additional evaluation metadata is added in the fallback path.

## Case-Specific Prompt Content

Each section below shows only the fields that vary by case. The experiment runner combines these fields with the shared content above using the configured user prompt template.

{''.join(case_sections)}
"""


def render_prompt_case_section(
    test_case: dict[str, Any],
    condition: PromptCondition,
    artifacts: dict[str, Any],
) -> str:
    """Render only prompt content that varies for one test case."""
    predicate_section = ""
    source_step_id = str(test_case.get("step_id") or "")
    if condition is PromptCondition.SYMBOLIC_DOMAIN:
        predicate_section = f"""
### Selected Symbolic Predicates

```text
{compact_prompt_text(predicate_context_for_step(source_step_id, artifacts), source_step_id)}
```
"""
    elif condition is PromptCondition.GRAPH_GROUNDED:
        subgraph = extract_step_subgraph(
            artifacts["procedural_reasoning_graph"],
            source_step_id,
            int(artifacts["step_hops"]),
            int(artifacts["evidence_hops"]),
        )
        evidence_text = compact_prompt_text(
            graph_evidence_for_step(source_step_id, artifacts),
            source_step_id,
        )
        predicate_section = _render_graph_evidence_report(subgraph, evidence_text, artifacts)
    return f"""
## Case: {test_case.get("case_id")}

- Step id: `{compact_step_id(source_step_id)}`
- Operator question: {test_case.get("question")}
{predicate_section}

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `{test_case.get("risk_type")}`
- Scenario: `{test_case.get("scenario")}`
- Status: `{test_case.get("status")}`
- Expected answer elements:
{_render_expected_elements(test_case.get("expected_answer_elements"))}
"""


def _render_graph_evidence_report(
    subgraph: dict[str, Any],
    evidence_text: str,
    artifacts: dict[str, Any],
) -> str:
    """Present graph retrieval statistics and the exact LLM evidence block."""
    node_counts = Counter(str(node.get("type") or "Unknown") for node in subgraph.get("nodes", []))
    edge_counts = Counter(str(edge.get("type") or "UNKNOWN") for edge in subgraph.get("edges", []))
    node_rows = "\n".join(f"| {name} | {count} |" for name, count in sorted(node_counts.items()))
    edge_rows = "\n".join(f"| {name} | {count} |" for name, count in sorted(edge_counts.items()))
    return f"""
### Procedural Reasoning Subgraph

The sequence traversal follows only `NEXT` edges. Semantic traversal starts
from the current step, follows the fixed semantic edge allowlist, and treats
neighboring steps, entities, rules, and sources as terminal nodes.

- Sequence step hops: `{artifacts.get('step_hops')}`
- Semantic evidence hops: `{artifacts.get('evidence_hops')}`
- Selected nodes: `{len(subgraph.get('nodes', []))}`
- Selected edges: `{len(subgraph.get('edges', []))}`

#### Nodes By Type

| Node type | Count |
|---|---:|
{node_rows or '| None | 0 |'}

#### Relationships By Type

| Relationship | Count |
|---|---:|
{edge_rows or '| None | 0 |'}

#### Exact Graph Evidence Sent To The LLM

```text
{evidence_text}
```
"""


def _render_shared_rules(condition: PromptCondition, artifacts: dict[str, Any]) -> str:
    """Render rules once because they do not vary between symbolic cases."""
    if condition is not PromptCondition.SYMBOLIC_DOMAIN:
        return ""
    return f"""### Thesis Rules

This block is inserted into the user message for every case.

```yaml
{artifacts.get("thesis_rules") or "No thesis-rules artifact loaded."}
```"""


def _render_expected_elements(elements: Any) -> str:
    """Render expected answer elements as Markdown bullets."""
    if not elements:
        return "  - None"
    return "\n".join(f"  - {element}" for element in elements)


def _render_run_statistics(statistics: dict[str, Any] | None) -> str:
    """Render run-wide timing statistics or a standalone-export notice."""
    if not statistics:
        return "Timing statistics are unavailable because this report was exported outside an experiment run."
    return (
        "These statistics cover all successful prompt interactions in this experiment run.\n\n"
        f"- Completed interactions: `{statistics.get('completed_interactions')}`\n"
        f"- Minimum prompt time: `{statistics.get('min_interaction_seconds'):.2f} s`\n"
        f"- Maximum prompt time: `{statistics.get('max_interaction_seconds'):.2f} s`\n"
        f"- Average prompt time: `{statistics.get('avg_interaction_seconds'):.2f} s`\n"
        f"- Total experiment time: `{statistics.get('total_duration_hms')}`"
    )


def _render_graph_provenance(condition: PromptCondition, artifacts: dict[str, Any]) -> str:
    """Render graph build provenance so reports identify the exact graph source."""
    if condition is not PromptCondition.GRAPH_GROUNDED:
        return "## Graph Provenance\n\n- Graph provenance: `not applicable to this condition`"

    graph = artifacts.get("procedural_reasoning_graph")
    graph_path = artifacts.get("procedural_reasoning_graph_path") or "unknown"
    if not isinstance(graph, dict):
        return (
            "## Graph Provenance\n\n"
            f"- Graph path: `{graph_path}`\n"
            "- Graph provenance: `unavailable; graph artifact was not loaded as a mapping`"
        )

    provenance = graph.get("provenance")
    if not isinstance(provenance, dict):
        return (
            "## Graph Provenance\n\n"
            f"- Graph path: `{graph_path}`\n"
            f"- Graph name: `{graph.get('graph_name') or 'unknown'}`\n"
            "- Graph provenance: `unavailable; rebuild the graph with the current graph builder to create provenance metadata`"
        )

    source_files = provenance.get("source_files") if isinstance(provenance.get("source_files"), dict) else {}
    lines = [
        "## Graph Provenance",
        "",
        f"- Graph path: `{graph_path}`",
        f"- Graph name: `{graph.get('graph_name') or 'unknown'}`",
        f"- Graph schema version: `{graph.get('schema_version') or provenance.get('graph_schema_version') or 'unknown'}`",
        f"- Graph built at: `{provenance.get('built_at') or 'unknown'}`",
        f"- Graph builder: `{provenance.get('builder') or 'unknown'}`",
        _source_file_line("Domain config", source_files.get("domain_config"), "domain_model_version"),
        _source_file_line("Thesis rules", source_files.get("thesis_rules"), "rule_set_version"),
        _source_file_line("Validation config", source_files.get("validation_config"), "rule_set_version"),
    ]
    return "\n".join(lines)


def _source_file_line(label: str, value: Any, version_key: str) -> str:
    """Format one provenance source file line."""
    if not isinstance(value, dict):
        return f"- {label}: `provenance unavailable`"
    version = value.get(version_key) or value.get("version") or "unknown"
    sha = _short_hash(value.get("sha256"))
    path = value.get("path") or "unknown"
    return f"- {label}: version `{version}`, sha256 `{sha}`, path `{path}`"


def _short_hash(value: Any) -> str:
    """Return a readable hash prefix while preserving explicit unknowns."""
    text = str(value or "")
    return text[:12] if text else "unknown"


def _render_question_set(question_set: Any) -> str:
    """Render the novice-question set manifest used for a run."""
    if not isinstance(question_set, dict):
        return "- Question set: `not available`"
    return "\n".join([
        f"- Path: `{question_set.get('path') or 'unknown'}`",
        f"- ID: `{question_set.get('question_set_id') or 'unknown'}`",
        f"- Version: `{question_set.get('question_set_version') or 'unknown'}`",
        f"- Case count: `{question_set.get('case_count') or 'unknown'}`",
        f"- SHA-256: `{_short_hash(question_set.get('sha256'))}`",
    ])


def _report_group_field(test_cases: list[dict[str, Any]]) -> str:
    """Choose the report grouping metadata field."""
    if any(test_case.get("scenario") for test_case in test_cases):
        return "scenario"
    return "risk_type"


def _group_cases(test_cases: list[dict[str, Any]], group_field: str) -> dict[str, list[dict[str, Any]]]:
    """Group flattened test cases by a metadata field while preserving order."""
    grouped_cases: dict[str, list[dict[str, Any]]] = {}
    for test_case in test_cases:
        group_name = str(test_case.get(group_field) or "unclassified")
        grouped_cases.setdefault(group_name, []).append(test_case)
    return grouped_cases


def _slug(value: Any) -> str:
    """Create a filesystem-friendly filename fragment."""
    text = str(value or "case").lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "case"


def main() -> None:
    """CLI entry point."""
    try:
        args = parse_args()
        from run_experiment import load_config

        output_dir = Path(args.output_dir) if args.output_dir else None
        paths = export_prompt_reports(load_config(args.config), PromptCondition(args.condition), output_dir)
    except Exception as exc:
        print(f"Error: failed to export prompt reports: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
