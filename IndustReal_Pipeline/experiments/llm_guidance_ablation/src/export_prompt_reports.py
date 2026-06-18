"""Export report-ready Markdown files showing prompts sent to the LLM."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from context_builders import PromptCondition, build_context
from run_experiment import load_artifacts, load_config, load_test_cases, resolve_configured_path


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
) -> list[Path]:
    """Write one Markdown file per test case documenting the LLM request."""
    if condition is not PromptCondition.STEPS_ONLY:
        raise NotImplementedError(
            f"{condition.value} prompt reports are not implemented yet. Use --condition steps_only."
        )

    test_cases = load_test_cases(config)
    artifacts = load_artifacts(config)
    report_dir = output_dir or resolve_configured_path("experiments/llm_guidance_ablation/outputs/prompt_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    written_paths = []
    for test_case in test_cases:
        context = build_context(condition, test_case, artifacts)
        path = report_dir / f"{_slug(test_case.get('case_id', 'case'))}_{condition.value}.md"
        path.write_text(
            render_prompt_report(config, condition, test_case, context, artifacts),
            encoding="utf-8",
        )
        written_paths.append(path)
    return written_paths


def render_prompt_report(
    config: dict[str, Any],
    condition: PromptCondition,
    test_case: dict[str, Any],
    context: dict[str, str],
    artifacts: dict[str, Any],
) -> str:
    """Render a single prompt report as Markdown."""
    generated_steps = artifacts.get("generated_steps")
    generated_steps_loaded = bool(generated_steps)
    fallback_template = artifacts["prompt_templates"]["lm_studio_fallback"]["user_template"]
    fallback_user_prompt = fallback_template.format_map(
        {"system_prompt": context["system_prompt"], "user_prompt": context["user_prompt"]}
    )

    return f"""# Prompt Report: {test_case.get("case_id")}

Generated at: {datetime.now(timezone.utc).isoformat()}

## Case

- Condition: `{condition.value}`
- Case id: `{test_case.get("case_id")}`
- Step id: `{test_case.get("step_id")}`
- Operator question: {test_case.get("question")}

## API Request Settings

- API base URL: `{config.get("api_base_url")}`
- Model name: `{config.get("model_name")}`
- Temperature: `{config.get("temperature")}`
- Max tokens: `{config.get("max_tokens")}`

## Prompt-Safe Context Sources

- Generated steps configured path: `{config.get("input_paths", {}).get("generated_steps")}`
- Generated steps loaded: `{generated_steps_loaded}`
- Raw domain config included: `no`
- Thesis rules included: `no`
- Procedural reasoning graph included: `no`

For the current `steps_only` condition, no full list of steps is sent unless it is present in the configured generated-steps artifact and matches the test case `step_id`.

## OpenAI-Compatible Chat Messages

These are the nominal chat messages sent by the experiment runner.

### Message 1

- Role: `system`

```text
{context["system_prompt"]}
```

### Message 2

- Role: `user`

```text
{context["user_prompt"]}
```

## LM Studio Compatibility Fallback

Some LM Studio model templates reject the `system` role. If that happens, the client retries with a single `user` message containing the same instruction and question content:

```text
{fallback_user_prompt}
```

## Evaluation Metadata Not Sent To LLM

These fields are saved in experiment outputs for evaluation only.

- Risk type: `{test_case.get("risk_type")}`
- Expected answer elements:
{_render_expected_elements(test_case.get("expected_answer_elements"))}
"""


def _render_expected_elements(elements: Any) -> str:
    """Render expected answer elements as Markdown bullets."""
    if not elements:
        return "  - None"
    return "\n".join(f"  - {element}" for element in elements)


def _slug(value: Any) -> str:
    """Create a filesystem-friendly filename fragment."""
    text = str(value or "case").lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "case"


def main() -> None:
    """CLI entry point."""
    try:
        args = parse_args()
        output_dir = Path(args.output_dir) if args.output_dir else None
        paths = export_prompt_reports(load_config(args.config), PromptCondition(args.condition), output_dir)
    except Exception as exc:
        print(f"Error: failed to export prompt reports: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
