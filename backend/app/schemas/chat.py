"""Pydantic schemas for Kundali chat API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from backend.app.schemas.common import BaseSchema


class ChatMessageSchema(BaseSchema):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequestSchema(BaseSchema):
    report_id: UUID
    user_message: str = Field(..., min_length=1, max_length=4000)
    conversation_history: list[ChatMessageSchema] = Field(default_factory=list)


class ChatTokenUsageSchema(BaseSchema):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class ChatResponseSchema(BaseSchema):
    report_id: UUID
    answer: str
    conversation_history: list[ChatMessageSchema]
    model: str
    source: str
    token_usage: ChatTokenUsageSchema
    generated_at: datetime
    query_id: UUID | None = None
    metadata: dict = Field(default_factory=dict)
