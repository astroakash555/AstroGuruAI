"""Provider-agnostic LLM adapter for Kundali chat."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from ai_engine.core.base import InferenceResult, PromptContext
from ai_engine.providers.gemini.client import GeminiClient


@runtime_checkable
class ChatLLMProvider(Protocol):
    """Protocol for chat-capable LLM providers."""

    @property
    def is_available(self) -> bool: ...

    async def generate_answer(self, context: PromptContext) -> InferenceResult: ...


class BaseChatLLMProvider(ABC):
    """Abstract base for chat LLM providers."""

    @property
    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def generate_answer(self, context: PromptContext) -> InferenceResult:
        raise NotImplementedError


class GeminiChatLLMProvider(BaseChatLLMProvider):
    """Gemini-backed chat provider using plain-text responses."""

    def __init__(self, client: GeminiClient | None = None) -> None:
        self._client = client or GeminiClient.from_env()

    @property
    def is_available(self) -> bool:
        return self._client.is_available

    async def generate_answer(self, context: PromptContext) -> InferenceResult:
        return await self._client.generate(context, json_response=False)
