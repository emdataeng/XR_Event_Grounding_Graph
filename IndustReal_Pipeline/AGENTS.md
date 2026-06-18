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
