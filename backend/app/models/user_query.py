"""User AI query / consultation model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import QueryStatus, QueryType
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.client import Client


class UserQuery(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    AI-powered user question and response log.

    Optionally scoped to a birth profile for chart-aware contextual answers.
    """

    __tablename__ = "user_queries"
    __table_args__ = (
        Index("ix_user_queries_client_id", "client_id"),
        Index("ix_user_queries_birth_detail_id", "birth_detail_id"),
        Index("ix_user_queries_query_type", "query_type"),
        Index("ix_user_queries_status", "status"),
        Index("ix_user_queries_created_at", "created_at"),
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    birth_detail_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_details.id", ondelete="SET NULL"),
        nullable=True,
    )
    query_type: Mapped[QueryType] = mapped_column(
        enum_column(QueryType, "query_type"),
        default=QueryType.GENERAL,
        server_default=QueryType.GENERAL.value,
        nullable=False,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[QueryStatus] = mapped_column(
        enum_column(QueryStatus, "query_status"),
        default=QueryStatus.RECEIVED,
        server_default=QueryStatus.RECEIVED.value,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    client: Mapped[Client] = relationship("Client", back_populates="user_queries")
    birth_detail: Mapped[BirthDetail | None] = relationship(
        "BirthDetail",
        back_populates="user_queries",
    )

    def __repr__(self) -> str:
        preview = self.query_text[:50] + "..." if len(self.query_text) > 50 else self.query_text
        return f"<UserQuery id={self.id} status={self.status.value} query={preview!r}>"
