"""OpenAI-compatible client helpers for local or hosted language models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LMConfig:
    """Configuration required to call an OpenAI-compatible chat API."""

    api_base_url: str
    api_key: str
    model_name: str
    temperature: float
    max_tokens: int


class LMClient:
    """Placeholder wrapper around an OpenAI-compatible chat completion client."""

    def __init__(self, config: LMConfig) -> None:
        self.config = config

    def generate_response(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Generate a model response for a prepared prompt.

        The concrete OpenAI-compatible API call is intentionally left for the
        next implementation pass. Callers should pass only prompt-safe fields;
        evaluation-only metadata must be excluded before this method is called.
        """
        raise NotImplementedError("LLM generation is not implemented yet.")
