# Agent Guidelines

## Python Environment

Use the repository virtual environment when running Python commands.

On Windows PowerShell:

- Prefer `.venv\Scripts\python.exe -m pytest ...` for tests.
- Prefer `.venv\Scripts\python.exe ...` for project scripts.
- Check for `.venv` before falling back to system `python`.
- Do not assume globally installed tools such as `pytest` are available.

## Prompt Configuration

For any code that sends prompts to an LLM, keep prompt text in a dedicated
`prompts.yaml` file rather than hard-coding it in Python. Code should load and
render prompt templates from config so prompts are easy to inspect, edit, reuse,
and report.

## Experiment Hyperparameters

Keep tunable experiment and retrieval hyperparameters in YAML configuration,
not as numeric or behavioral defaults embedded in Python or query templates.
When multiple experiments use the same setting, define it once under
`experiments/shared/configs/` and make each experiment reference that shared
file. Code should fail clearly when required hyperparameters are missing rather
than silently falling back to hard-coded values.

## Timestamped Logs

For timestamped experiment outputs, write structured log timestamps in local
time with an explicit UTC offset, matching the timezone used in output
filenames. Do not mix local-time filenames with UTC log entries.
