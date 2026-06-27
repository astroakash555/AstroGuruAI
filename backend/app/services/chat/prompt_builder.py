"""Prompt construction for Kundali chat."""

from __future__ import annotations

import json
from typing import Any

from ai_engine.core.base import PromptContext
from ai_engine.prompts.loader import PromptLoader

from backend.app.services.chat.history import format_history_for_prompt
from backend.app.services.chat.models import ChatMessage


class ChatPromptBuilder:
    """Build provider-agnostic prompts from report context and chat history."""

    def __init__(self, prompt_loader: PromptLoader | None = None) -> None:
        self._prompts = prompt_loader or PromptLoader()

    def build(
        self,
        *,
        report_context: dict[str, Any],
        user_message: str,
        conversation_history: tuple[ChatMessage, ...],
    ) -> PromptContext:
        system_prompt = self._prompts.load("kundali_chat", "system.txt")
        user_template = self._prompts.load("kundali_chat", "user.txt")
        user_prompt = self._prompts.render(
            user_template,
            report_context=json.dumps(report_context, ensure_ascii=False, indent=2),
            conversation_history=format_history_for_prompt(conversation_history),
            user_message=user_message.strip(),
        )
        return PromptContext(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"task": "kundali_chat"},
        )
