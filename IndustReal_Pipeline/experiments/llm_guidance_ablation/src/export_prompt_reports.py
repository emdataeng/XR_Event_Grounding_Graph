"""Export report-ready Markdown files showing prompts sent to the LLM."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from context_builders import PromptCondition, build_context, predicate_context_for_step


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
    """Write one Markdown file per risk type documenting LLM requests."""
    if condition not in {PromptCondition.STEPS_ONLY, PromptCondition.SYMBOLIC_DOMAIN}:
        raise NotImplementedError(
            f"{condition.value} prompt reports are not implemented yet. Use steps_only or symbolic_domain."
        )

    if test_cases is None or artifacts is None:
        from run_experiment import load_artifacts, load_test_cases

        test_cases = load_test_cases(config)
        artifacts = load_artifacts(config)

    report_dir = output_dir or (EXPERIMENT_ROOT / "outputs" / "prompt_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    written_paths = []
    for risk_type, grouped_cases in _group_cases_by_risk_type(test_cases).items():
        path = report_dir / f"{_slug(risk_type)}_{condition.value}.md"
        path.write_text(
            render_prompt_report_group(
                config,
                condition,
                risk_type,
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
    risk_type: str,
    test_cases: list[dict[str, Any]],
    artifacts: dict[str, Any],
    run_statistics: dict[str, Any] | None = None,
) -> str:
    """Render one Markdown report containing all prompts for a risk type."""
    step_list_loaded = bool(artifacts.get("step_list"))
    symbolic_domain_included = condition is PromptCondition.SYMBOLIC_DOMAIN
    shared_context = build_context(condition, test_cases[0], artifacts)
    case_sections = [render_prompt_case_section(test_case, condition, artifacts) for test_case in test_cases]
    shared_rules = _render_shared_rules(condition, artifacts)

    return f"""# Prompt Report: {risk_type}

Generated at: {datetime.now(timezone.utc).isoformat()}

- Condition: `{condition.value}`
- Risk type: `{risk_type}`
- Cases in this report: `{len(test_cases)}`

## API Request Settings

- API base URL: `{config.get("api_base_url")}`
- Model name: `{config.get("model_name")}`
- Temperature: `{config.get("temperature")}`
- Max tokens: `{config.get("max_tokens")}`

## Run Timing Statistics

{_render_run_statistics(run_statistics)}

## Prompt-Safe Context Sources

- Step-list artifact configured path: `{config.get("input_paths", {}).get("step_list")}`
- Step-list artifact loaded: `{step_list_loaded}`
- Windowed predicates included: `{'yes' if symbolic_domain_included else 'no'}`
- Step-hop radius: `{artifacts.get("step_hops") if symbolic_domain_included else 'not applicable'}`
- Thesis rules included: `{'yes' if symbolic_domain_included else 'no'}`
- Procedural reasoning graph included: `no`

Both implemented conditions include the same frozen step-list artifact. The `symbolic_domain` condition additionally includes a deterministic predicate window around the current step and the complete `thesis_rules.yaml` file.

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
{artifacts.get("step_list") or "No step-list artifact loaded."}
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
    if condition is PromptCondition.SYMBOLIC_DOMAIN:
        predicate_section = f"""
### Selected Symbolic Predicates

```text
{predicate_context_for_step(str(test_case.get("step_id") or ""), artifacts)}
```
"""
    return f"""
## Case: {test_case.get("case_id")}

- Step id: `{test_case.get("step_id")}`
- Operator question: {test_case.get("question")}
{predicate_section}

### Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `{test_case.get("risk_type")}`
- Expected answer elements:
{_render_expected_elements(test_case.get("expected_answer_elements"))}
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


def _group_cases_by_risk_type(test_cases: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group flattened test cases by risk type while preserving order."""
    grouped_cases: dict[str, list[dict[str, Any]]] = {}
    for test_case in test_cases:
        risk_type = str(test_case.get("risk_type") or "unclassified")
        grouped_cases.setdefault(risk_type, []).append(test_case)
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
