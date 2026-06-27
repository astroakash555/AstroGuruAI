"""Google Gemini provider (legacy entrypoint)."""

from ai_engine.providers.gemini.client import GeminiClient, GeminiConfig

__all__ = ["GeminiClient", "GeminiConfig"]


class GeminiProvider(GeminiClient):
    """Backward-compatible alias for GeminiClient."""
