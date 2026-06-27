"""Gemini provider configuration."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class GeminiConfig:
    """Environment-driven Gemini configuration."""

    api_key: str | None
    model: str = "gemini-2.0-flash"
    enabled: bool = False
    max_retries: int = 3
    retry_base_delay_seconds: float = 1.0
    requests_per_minute: int = 30
    max_output_tokens: int = 8192
    temperature: float = 0.4

    @classmethod
    def from_env(cls) -> GeminiConfig:
        api_key = os.getenv("GEMINI_API_KEY") or None
        enabled = os.getenv("GEMINI_ENABLED", "false").lower() in {"1", "true", "yes"}
        return cls(
            api_key=api_key,
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            enabled=enabled and bool(api_key),
            max_retries=int(os.getenv("GEMINI_MAX_RETRIES", "3")),
            retry_base_delay_seconds=float(os.getenv("GEMINI_RETRY_DELAY", "1.0")),
            requests_per_minute=int(os.getenv("GEMINI_RPM_LIMIT", "30")),
            max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192")),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.4")),
        )
