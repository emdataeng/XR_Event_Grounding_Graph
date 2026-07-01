"""Smoke-test an OpenAI-compatible chat endpoint from a YAML config."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "experiments" / "shared" / "configs" / "llm_api_masoud.yaml"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to an LLM API YAML config.")
    parser.add_argument("--prompt", default="Hello, are you working?", help="User message to send.")
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    """Load and minimally validate an LLM API config."""
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    required_fields = (
        "api_base_url",
        "api_key",
        "model_name",
        "temperature",
        "max_tokens",
        "request_timeout_seconds",
        "max_retries",
    )
    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"Missing required config field(s) in {path}: {', '.join(missing)}")
    return config


def main() -> None:
    """Run the smoke test."""
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The OpenAI Python package is not installed. "
            "Use the repository virtual environment and install experiment requirements first."
        ) from exc

    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = REPO_ROOT / config_path
    config = load_config(config_path)

    client = OpenAI(
        base_url=str(config["api_base_url"]),
        api_key=str(config["api_key"]),
        timeout=float(config["request_timeout_seconds"]),
        max_retries=int(config["max_retries"]),
    )

    response = client.chat.completions.create(
        model=str(config["model_name"]),
        messages=[{"role": "user", "content": args.prompt}],
        temperature=float(config["temperature"]),
        max_tokens=int(config["max_tokens"]),
    )

    message = response.choices[0].message
    print((message.content or "").strip())


if __name__ == "__main__":
    main()
