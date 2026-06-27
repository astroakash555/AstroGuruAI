"""Conversation history helpers for Kundali chat."""

from __future__ import annotations

from backend.app.services.chat.models import ChatMessage

MAX_HISTORY_MESSAGES = 6
ALLOWED_ROLES = frozenset({"user", "assistant"})


def normalize_history(history: tuple[ChatMessage, ...] | list[ChatMessage]) -> tuple[ChatMessage, ...]:
    """Keep only valid user/assistant turns and cap history length."""
    cleaned: list[ChatMessage] = []
    for message in history:
        role = message.role.strip().lower()
        content = message.content.strip()
        if role not in ALLOWED_ROLES or not content:
            continue
        cleaned.append(ChatMessage(role=role, content=content))
    return tuple(cleaned[-MAX_HISTORY_MESSAGES:])


def append_turn(
    history: tuple[ChatMessage, ...],
    *,
    user_message: str,
    assistant_message: str,
) -> tuple[ChatMessage, ...]:
    """Append the latest user and assistant messages, preserving the cap."""
    updated = history + (
        ChatMessage(role="user", content=user_message.strip()),
        ChatMessage(role="assistant", content=assistant_message.strip()),
    )
    return normalize_history(updated)


def format_history_for_prompt(history: tuple[ChatMessage, ...]) -> str:
    """Render prior turns for inclusion in the LLM user prompt."""
    if not history:
        return "No prior conversation."

    lines: list[str] = []
    for message in history:
        speaker = "User" if message.role == "user" else "Assistant"
        lines.append(f"{speaker}: {message.content}")
    return "\n".join(lines)
