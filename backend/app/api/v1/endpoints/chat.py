"""Kundali chat API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engine.prompts.loader import PromptLoader
from backend.app.api.deps import get_current_user, get_db, get_settings_dep, get_usage_service, require_usage, user_owner_id
from backend.app.billing.usage import UsageService
from backend.app.core.config import Settings
from backend.app.core.exceptions import NotFoundError, not_found_error
from backend.app.models.enums import UsageMetric
from backend.app.models.user import User
from backend.app.repositories.report_repository import ReportRepository
from backend.app.repositories.user_query_repository import UserQueryRepository
from backend.app.schemas.chat import ChatRequestSchema, ChatResponseSchema, ChatTokenUsageSchema
from backend.app.services.chat import ChatMessage, ChatRequest, ChatService
from backend.app.services.chat.llm_provider import GeminiChatLLMProvider
from backend.app.services.chat.prompt_builder import ChatPromptBuilder

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(
    settings: Settings = Depends(get_settings_dep),
    session: AsyncSession = Depends(get_db),
) -> ChatService:
    return ChatService(
        session=session,
        report_repository=ReportRepository(session),
        user_query_repository=UserQueryRepository(session),
        llm_provider=GeminiChatLLMProvider(),
        prompt_builder=ChatPromptBuilder(PromptLoader(settings.prompts_path)),
    )


@router.post(
    "",
    response_model=ChatResponseSchema,
    summary="Chat about a saved Kundali report",
)
async def chat_about_report(
    payload: ChatRequestSchema,
    current_user: User = Depends(require_usage(UsageMetric.CHAT_MESSAGES)),
    service: ChatService = Depends(get_chat_service),
    usage_service: UsageService = Depends(get_usage_service),
) -> ChatResponseSchema:
    try:
        result = await service.chat(
            ChatRequest(
                report_id=payload.report_id,
                user_message=payload.user_message,
                conversation_history=tuple(
                    ChatMessage(role=message.role, content=message.content)
                    for message in payload.conversation_history
                ),
            ),
            scoped_owner_id=user_owner_id(current_user),
        )
    except NotFoundError as exc:
        raise not_found_error("Report", str(payload.report_id)) from exc

    await usage_service.consume(current_user.id, UsageMetric.CHAT_MESSAGES)

    return ChatResponseSchema(
        report_id=result.report_id,
        answer=result.answer,
        conversation_history=[
            {"role": message.role, "content": message.content}
            for message in result.conversation_history
        ],
        model=result.model,
        source=result.source,
        token_usage=ChatTokenUsageSchema(
            prompt_tokens=result.token_usage.prompt_tokens,
            completion_tokens=result.token_usage.completion_tokens,
            total_tokens=result.token_usage.total_tokens,
        ),
        generated_at=result.generated_at,
        query_id=result.query_id,
        metadata=dict(result.metadata),
    )
