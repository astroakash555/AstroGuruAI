"""Kundali-aware conversational chat service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError
from backend.app.models.enums import QueryType
from backend.app.repositories.report_repository import ReportRepository
from backend.app.repositories.user_query_repository import UserQueryRepository
from backend.app.services.chat.context_builder import build_report_context
from backend.app.services.chat.fallback import build_fallback_answer
from backend.app.services.chat.history import append_turn, normalize_history
from backend.app.services.chat.llm_provider import ChatLLMProvider, GeminiChatLLMProvider
from backend.app.services.chat.models import ChatRequest, ChatResponse, ChatTokenUsage
from backend.app.services.chat.prompt_builder import ChatPromptBuilder

ENGINE_VERSION = "kundali_chat_v1"


class ChatService:
    """Answer natural-language questions against a persisted unified report."""

    def __init__(
        self,
        *,
        session: AsyncSession,
        report_repository: ReportRepository,
        user_query_repository: UserQueryRepository | None = None,
        llm_provider: ChatLLMProvider | None = None,
        prompt_builder: ChatPromptBuilder | None = None,
    ) -> None:
        self._session = session
        self._reports = report_repository
        self._queries = user_query_repository or UserQueryRepository(session)
        self._llm = llm_provider or GeminiChatLLMProvider()
        self._prompts = prompt_builder or ChatPromptBuilder()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Load a report, answer the user message, and return updated history."""
        report = await self._reports.get_report(request.report_id)
        if report is None:
            raise NotFoundError(f"Report {request.report_id} was not found.")

        history = normalize_history(request.conversation_history)
        report_context = build_report_context(report.unified_report_json)
        prompt = self._prompts.build(
            report_context=report_context,
            user_message=request.user_message,
            conversation_history=history,
        )

        query_record = None
        if report.client_id is not None:
            query_record = await self._queries.create_query(
                client_id=report.client_id,
                birth_detail_id=report.birth_detail_id,
                query_type=QueryType.KUNDALI,
                query_text=request.user_message,
                context_snapshot={
                    "report_id": str(report.id),
                    "conversation_history": [message.to_dict() for message in history],
                    "report_context_keys": list(report_context.keys()),
                },
                metadata={"engine": ENGINE_VERSION},
            )

        if self._llm.is_available:
            inference = await self._llm.generate_answer(prompt)
            answer = inference.content.strip()
            model = inference.model
            source = str(inference.metadata.get("provider", "llm"))
            token_usage = ChatTokenUsage(
                prompt_tokens=_optional_int(inference.metadata.get("prompt_tokens")),
                completion_tokens=_optional_int(inference.metadata.get("completion_tokens")),
                total_tokens=_optional_int(inference.metadata.get("total_tokens")),
            )
        else:
            answer = build_fallback_answer(
                report_context=report_context,
                user_message=request.user_message,
            )
            model = "rule_based_fallback"
            source = "rule_based_fallback"
            token_usage = ChatTokenUsage()

        updated_history = append_turn(
            history,
            user_message=request.user_message,
            assistant_message=answer,
        )

        if query_record is not None:
            await self._queries.mark_answered(
                query_record,
                response_text=answer,
                ai_model=model,
                prompt_tokens=token_usage.prompt_tokens,
                completion_tokens=token_usage.completion_tokens,
                total_tokens=token_usage.total_tokens,
            )
            await self._session.commit()

        return ChatResponse(
            report_id=report.id,
            answer=answer,
            conversation_history=updated_history,
            model=model,
            source=source,
            token_usage=token_usage,
            generated_at=datetime.now(timezone.utc),
            query_id=query_record.id if query_record is not None else None,
            metadata={
                "engine": ENGINE_VERSION,
                "report_version": report.version,
                "context_sections": list(report_context.keys()),
            },
        )


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)
