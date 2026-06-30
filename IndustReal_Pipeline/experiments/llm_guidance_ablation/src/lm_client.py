"""OpenAI-compatible client helpers for local or hosted language models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class LMConfig:
    """Configuration required to call an OpenAI-compatible chat API."""

    api_base_url: str
    api_key: str
    model_name: str
    temperature: float
    max_tokens: int
    request_timeout_seconds: float
    max_retries: int


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = EXPERIMENT_ROOT / "configs" / "config.yaml"
_ACTIVE_CONFIG_PATH = DEFAULT_CONFIG_PATH


def set_config_path(config_path: str | Path) -> None:
    """Set the config path used by ``ask_llm``."""
    global _ACTIVE_CONFIG_PATH
    _ACTIVE_CONFIG_PATH = Path(config_path)


def load_lm_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> LMConfig:
    """Load the LLM API settings from the experiment or shared config file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"config.yaml is missing: {path}")

    with path.open("r", encoding="utf-8") as handle:
        config: dict[str, Any] = yaml.safe_load(handle) or {}

    llm_config_path = config.get("llm_config")
    if llm_config_path:
        shared_path = _resolve_configured_path(str(llm_config_path))
        if not shared_path.exists():
            raise FileNotFoundError(f"Shared LLM config is missing: {shared_path}")
        with shared_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}

    try:
        return LMConfig(
            api_base_url=str(config["api_base_url"]),
            api_key=str(config["api_key"]),
            model_name=str(config["model_name"]),
            temperature=float(config["temperature"]),
            max_tokens=int(config["max_tokens"]),
            request_timeout_seconds=float(config["request_timeout_seconds"]),
            max_retries=int(config["max_retries"]),
        )
    except KeyError as exc:
        raise ValueError(f"Missing required LLM config field in {path}: {exc.args[0]}") from exc


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """Send a chat request to an OpenAI-compatible endpoint and return text.

    This function loads API settings from ``config.yaml`` so it works with
    local servers such as LM Studio at ``http://localhost:1234/v1``.
    """
    try:
        from openai import APIConnectionError, APIError, BadRequestError, OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The OpenAI Python package is not installed. "
            "Install experiment dependencies with: "
            "pip install -r experiments/llm_guidance_ablation/requirements.txt"
        ) from exc

    config = load_lm_config(_ACTIVE_CONFIG_PATH)
    client = OpenAI(
        api_key=config.api_key,
        base_url=config.api_base_url,
        timeout=config.request_timeout_seconds,
        max_retries=config.max_retries,
    )

    try:
        completion = _create_chat_completion(client, config, system_prompt, user_prompt)
    except BadRequestError as exc:
        if "Only user and assistant roles are supported" not in str(exc):
            raise RuntimeError(f"The API call failed: {exc}") from exc

        # Some LM Studio prompt templates do not accept a system role. Keep the
        # same instruction content, but send it as a single user message.
        fallback_template = load_fallback_prompt_template(_ACTIVE_CONFIG_PATH)
        completion = _create_chat_completion(
            client,
            config,
            system_prompt="",
            user_prompt=fallback_template.format_map(
                {"system_prompt": system_prompt, "user_prompt": user_prompt}
            ),
        )
    except APIConnectionError as exc:
        raise RuntimeError(
            "Could not connect to the OpenAI-compatible API. "
            "If you are using LM Studio, make sure the local server is running "
            f"and that api_base_url is correct: {config.api_base_url}"
        ) from exc
    except APIError as exc:
        raise RuntimeError(f"The API call failed: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"The API call failed unexpectedly: {exc}") from exc

    message = completion.choices[0].message.content
    return (message or "").strip()


def _create_chat_completion(client: Any, config: LMConfig, system_prompt: str, user_prompt: str) -> Any:
    """Create a chat completion, omitting the system role when it is empty."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    return client.chat.completions.create(
        model=config.model_name,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )


def load_fallback_prompt_template(config_path: str | Path) -> str:
    """Load the LM Studio fallback user-message template."""
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as handle:
        config: dict[str, Any] = yaml.safe_load(handle) or {}

    prompt_path = _resolve_configured_path(config["prompt_paths"]["prompts"])
    with prompt_path.open("r", encoding="utf-8") as handle:
        prompts: dict[str, Any] = yaml.safe_load(handle) or {}

    try:
        return str(prompts["lm_studio_fallback"]["user_template"])
    except KeyError as exc:
        raise ValueError(f"Missing LM Studio fallback prompt template field: {exc.args[0]}") from exc


def _resolve_configured_path(path_value: str) -> Path:
    """Resolve a configured path from common experiment run locations."""
    path = Path(path_value)
    if path.is_absolute():
        return path

    for base in (Path.cwd(), REPO_ROOT, EXPERIMENT_ROOT):
        candidate = base / path
        if candidate.exists():
            return candidate
    return REPO_ROOT / path
