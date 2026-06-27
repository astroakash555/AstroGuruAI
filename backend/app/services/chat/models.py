"""Typed models for the Kundali chat service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ChatMessage:
    """One turn in a short chat conversation."""

    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class ChatRequest:
    """Internal chat request after API validation."""

    report_id: UUID
    user_message: str
    conversation_history: tuple[ChatMessage, ...] = ()


@dataclass(frozen=True)
class ChatTokenUsage:
    """Token accounting for one chat response."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class ChatResponse:
    """Internal chat response returned by the service layer."""

    report_id: UUID
    answer: str
    conversation_history: tuple[ChatMessage, ...]
    model: str
    source: str
    token_usage: ChatTokenUsage
    generated_at: datetime
    query_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
