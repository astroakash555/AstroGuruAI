"""AI Kundali chat service for report-aware conversations."""

from backend.app.services.chat.chat_service import ChatService, ENGINE_VERSION
from backend.app.services.chat.context_builder import build_report_context, context_section_keys
from backend.app.services.chat.history import append_turn, format_history_for_prompt, normalize_history
from backend.app.services.chat.llm_provider import ChatLLMProvider, GeminiChatLLMProvider
from backend.app.services.chat.models import ChatMessage, ChatRequest, ChatResponse, ChatTokenUsage
from backend.app.services.chat.prompt_builder import ChatPromptBuilder

__all__ = [
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatService",
    "ChatTokenUsage",
    "ChatLLMProvider",
    "ChatPromptBuilder",
    "ENGINE_VERSION",
    "GeminiChatLLMProvider",
    "append_turn",
    "build_report_context",
    "context_section_keys",
    "format_history_for_prompt",
    "normalize_history",
]
