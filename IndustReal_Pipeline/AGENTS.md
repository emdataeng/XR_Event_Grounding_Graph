# Agent Guidelines

## Python Environment

Use the repository virtual environment when running Python commands.

On Windows PowerShell:

- Prefer `.venv\Scripts\python.exe -m pytest ...` for tests.
- Prefer `.venv\Scripts\python.exe ...` for project scripts.
- Check for `.venv` before falling back to system `python`.
- Do not assume globally installed tools such as `pytest` are available.

