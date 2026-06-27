"""Tests for chat LLM provider adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_engine.core.base import InferenceResult, PromptContext
from ai_engine.providers.gemini.client import GeminiClient
from ai_engine.providers.gemini.config import GeminiConfig
from backend.app.services.chat.llm_provider import GeminiChatLLMProvider


@pytest.mark.asyncio
async def test_gemini_chat_provider_uses_text_mode():
    client = MagicMock(spec=GeminiClient)
    client.is_available = True
    client.generate = AsyncMock(
        return_value=InferenceResult(content="Answer", model="gemini-2.0-flash", metadata={"provider": "gemini"})
    )
    provider = GeminiChatLLMProvider(client=client)

    result = await provider.generate_answer(
        PromptContext(system_prompt="System", user_prompt="User", metadata={"task": "kundali_chat"})
    )

    assert result.content == "Answer"
    client.generate.assert_awaited_once()
    assert client.generate.await_args.kwargs["json_response"] is False


def test_gemini_chat_provider_availability():
    provider = GeminiChatLLMProvider(client=GeminiClient(config=GeminiConfig(api_key=None, enabled=False)))
    assert provider.is_available is False


def test_base_chat_provider_contract():
    from backend.app.services.chat.llm_provider import BaseChatLLMProvider

    class DummyProvider(BaseChatLLMProvider):
        @property
        def is_available(self) -> bool:
            return True

        async def generate_answer(self, context):
            return InferenceResult(content="ok", model="dummy", metadata={})

    provider = DummyProvider()
    assert provider.is_available is True
