"""Integration tests for Kundali chat API."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.chat import get_chat_service
from backend.app.main import create_app
from backend.app.services.chat.models import ChatMessage, ChatResponse, ChatTokenUsage
from tests.helpers import override_current_user


@pytest.fixture
def mock_chat_service():
    service = AsyncMock()
    report_id = uuid.uuid4()
    service.chat.return_value = ChatResponse(
        report_id=report_id,
        answer="Marriage timing improves after Venus support strengthens.",
        conversation_history=(
            ChatMessage(role="user", content="When will I marry?"),
            ChatMessage(role="assistant", content="Marriage timing improves after Venus support strengthens."),
        ),
        model="gemini-2.0-flash",
        source="gemini",
        token_usage=ChatTokenUsage(prompt_tokens=100, completion_tokens=40, total_tokens=140),
        generated_at=datetime.now(timezone.utc),
        query_id=uuid.uuid4(),
        metadata={"engine": "kundali_chat_v1"},
    )
    return service


@pytest.fixture
async def chat_client(mock_chat_service, test_user):
    app = create_app()
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service
    override_current_user(app, test_user)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_endpoint_returns_answer(chat_client, mock_chat_service):
    report_id = uuid.uuid4()
    response = await chat_client.post(
        "/api/v1/chat",
        json={
            "report_id": str(report_id),
            "user_message": "When will I marry?",
            "conversation_history": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"]
    assert payload["model"] == "gemini-2.0-flash"
    assert payload["metadata"]["engine"] == "kundali_chat_v1"
    assert len(payload["conversation_history"]) == 2
    mock_chat_service.chat.assert_awaited_once()


@pytest.mark.asyncio
async def test_chat_endpoint_returns_404_for_missing_report(chat_client, mock_chat_service):
    from backend.app.core.exceptions import NotFoundError

    mock_chat_service.chat.side_effect = NotFoundError("missing")
    response = await chat_client.post(
        "/api/v1/chat",
        json={"report_id": str(uuid.uuid4()), "user_message": "Hello"},
    )

    assert response.status_code == 404


def test_get_chat_service_factory():
    from backend.app.api.v1.endpoints.chat import get_chat_service
    from backend.app.core.config import get_settings

    service = get_chat_service(settings=get_settings(), session=AsyncMock())
    assert service.__class__.__name__ == "ChatService"

