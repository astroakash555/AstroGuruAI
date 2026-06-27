"""Tests for chat service orchestration."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from backend.app.core.exceptions import NotFoundError
from backend.app.services.chat.chat_service import ChatService
from backend.app.services.chat.models import ChatMessage, ChatRequest


@pytest.mark.asyncio
async def test_chat_with_llm_provider(
    report_id,
    mock_session,
    mock_report_repository,
    mock_user_query_repository,
    mock_llm_provider,
):
    service = ChatService(
        session=mock_session,
        report_repository=mock_report_repository,
        user_query_repository=mock_user_query_repository,
        llm_provider=mock_llm_provider,
    )
    result = await service.chat(
        ChatRequest(
            report_id=report_id,
            user_message="When will I get married?",
            conversation_history=(ChatMessage(role="user", content="Hello"),),
        )
    )

    assert result.answer.startswith("Marriage timing")
    assert result.model == "gemini-2.0-flash"
    assert result.source == "gemini"
    assert result.token_usage.total_tokens == 165
    assert len(result.conversation_history) == 3
    mock_user_query_repository.create_query.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_chat_uses_fallback_when_llm_unavailable(
    report_id,
    mock_session,
    mock_report_repository,
    mock_user_query_repository,
):
    provider = AsyncMock()
    provider.is_available = False
    service = ChatService(
        session=mock_session,
        report_repository=mock_report_repository,
        user_query_repository=mock_user_query_repository,
        llm_provider=provider,
    )
    result = await service.chat(
        ChatRequest(report_id=report_id, user_message="Why is marriage delayed?")
    )

    assert result.source == "rule_based_fallback"
    assert "Marriage" in result.answer
    provider.generate_answer.assert_not_called()


@pytest.mark.asyncio
async def test_chat_raises_when_report_missing(report_id, mock_session, mock_report_repository):
    mock_report_repository.get_report.return_value = None
    service = ChatService(session=mock_session, report_repository=mock_report_repository)

    with pytest.raises(NotFoundError):
        await service.chat(ChatRequest(report_id=report_id, user_message="Hello"))


@pytest.mark.asyncio
async def test_chat_skips_query_persistence_without_client_id(
    report_id,
    mock_session,
    sample_report,
    mock_report_repository,
    mock_user_query_repository,
    mock_llm_provider,
):
    sample_report.client_id = None
    service = ChatService(
        session=mock_session,
        report_repository=mock_report_repository,
        user_query_repository=mock_user_query_repository,
        llm_provider=mock_llm_provider,
    )
    result = await service.chat(
        ChatRequest(report_id=report_id, user_message="Tell me about career.")
    )

    assert result.query_id is None
    mock_user_query_repository.create_query.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_chat_handles_missing_token_metadata(
    report_id,
    mock_session,
    mock_report_repository,
    mock_user_query_repository,
):
    provider = AsyncMock()
    provider.is_available = True
    provider.generate_answer.return_value = type(
        "Inference",
        (),
        {
            "content": "Career looks stable.",
            "model": "gemini-2.0-flash",
            "metadata": {"provider": "gemini"},
        },
    )()
    service = ChatService(
        session=mock_session,
        report_repository=mock_report_repository,
        user_query_repository=mock_user_query_repository,
        llm_provider=provider,
    )
    result = await service.chat(ChatRequest(report_id=report_id, user_message="How is my career?"))

    assert result.token_usage.total_tokens is None

