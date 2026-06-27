"""Tests for chat conversation history helpers."""

from __future__ import annotations

from backend.app.services.chat.history import append_turn, format_history_for_prompt, normalize_history
from backend.app.services.chat.models import ChatMessage


def test_normalize_history_caps_and_filters_messages():
    history = normalize_history(
        [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi"),
            ChatMessage(role="system", content="ignored"),
            ChatMessage(role="user", content="  "),
            ChatMessage(role="user", content="Question 1"),
            ChatMessage(role="assistant", content="Answer 1"),
            ChatMessage(role="user", content="Question 2"),
            ChatMessage(role="assistant", content="Answer 2"),
            ChatMessage(role="user", content="Question 3"),
            ChatMessage(role="assistant", content="Answer 3"),
        ]
    )

    assert len(history) == 6
    assert history[-2].content == "Question 3"


def test_append_turn_adds_user_and_assistant_messages():
    history = append_turn((), user_message="When will I marry?", assistant_message="After Venus support.")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"


def test_format_history_for_prompt_empty():
    assert format_history_for_prompt(()) == "No prior conversation."


def test_format_history_for_prompt_renders_roles():
    text = format_history_for_prompt(
        (
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there"),
        )
    )
    assert "User: Hello" in text
    assert "Assistant: Hi there" in text
