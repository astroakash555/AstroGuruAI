"""Tests for chat dataclass models."""

from __future__ import annotations

from backend.app.services.chat.models import ChatMessage


def test_chat_message_to_dict():
    payload = ChatMessage(role="user", content="Hello").to_dict()
    assert payload == {"role": "user", "content": "Hello"}
