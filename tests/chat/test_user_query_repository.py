"""Tests for user query repository."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.enums import QueryStatus, QueryType
from backend.app.repositories.user_query_repository import UserQueryRepository


@pytest.mark.asyncio
async def test_create_query_persists_processing_record():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    repository = UserQueryRepository(session)
    client_id = uuid.uuid4()
    record = await repository.create_query(
        client_id=client_id,
        birth_detail_id=None,
        query_type=QueryType.KUNDALI,
        query_text="When will I marry?",
        context_snapshot={"report_id": str(uuid.uuid4())},
        metadata={"engine": "kundali_chat_v1"},
    )

    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(record)
    assert record.client_id == client_id
    assert record.status == QueryStatus.PROCESSING


@pytest.mark.asyncio
async def test_mark_answered_updates_response_fields():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    query = MagicMock()

    repository = UserQueryRepository(session)
    updated = await repository.mark_answered(
        query,
        response_text="Answer",
        ai_model="gemini-2.0-flash",
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
    )

    assert updated.response_text == "Answer"
    assert updated.status == QueryStatus.ANSWERED
    session.flush.assert_awaited_once()
