"""Persistence layer for user AI queries."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import QueryStatus, QueryType
from backend.app.models.user_query import UserQuery


class UserQueryRepository:
    """Create and update persisted chat/query records."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_query(
        self,
        *,
        client_id: uuid.UUID,
        birth_detail_id: uuid.UUID | None,
        query_type: QueryType,
        query_text: str,
        context_snapshot: dict | None = None,
        metadata: dict | None = None,
    ) -> UserQuery:
        record = UserQuery(
            client_id=client_id,
            birth_detail_id=birth_detail_id,
            query_type=query_type,
            query_text=query_text,
            context_snapshot=context_snapshot,
            status=QueryStatus.PROCESSING,
            metadata_=metadata,
        )
        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)
        return record

    async def mark_answered(
        self,
        query: UserQuery,
        *,
        response_text: str,
        ai_model: str | None,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        total_tokens: int | None,
    ) -> UserQuery:
        query.response_text = response_text
        query.ai_model = ai_model
        query.prompt_tokens = prompt_tokens
        query.completion_tokens = completion_tokens
        query.total_tokens = total_tokens
        query.status = QueryStatus.ANSWERED
        await self._session.flush()
        await self._session.refresh(query)
        return query
