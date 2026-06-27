"""Tests for chat prompt builder."""

from __future__ import annotations

from ai_engine.prompts.loader import PromptLoader

from backend.app.services.chat.context_builder import build_report_context
from backend.app.services.chat.models import ChatMessage
from backend.app.services.chat.prompt_builder import ChatPromptBuilder


def test_build_prompt_includes_report_and_history(sample_unified_report):
    builder = ChatPromptBuilder(PromptLoader("prompts"))
    context = build_report_context(sample_unified_report)
    prompt = builder.build(
        report_context=context,
        user_message="Tell me about marriage timing.",
        conversation_history=(ChatMessage(role="user", content="Hi"),),
    )

    assert "Marriage delay is the dominant theme." in prompt.user_prompt
    assert "Tell me about marriage timing." in prompt.user_prompt
    assert "User: Hi" in prompt.user_prompt
    assert prompt.metadata["task"] == "kundali_chat"
