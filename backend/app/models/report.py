"""Persisted unified astrology report model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.client import Client


class Report(UUIDPrimaryKeyMixin, Base):
    """Full unified report payload persisted for client retrieval and audit."""

    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_client_id", "client_id"),
        Index("ix_reports_birth_detail_id", "birth_detail_id"),
        Index("ix_reports_generated_at", "generated_at"),
        Index("ix_reports_version", "version"),
    )

    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
    )
    birth_detail_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_details.id", ondelete="SET NULL"),
        nullable=True,
    )
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    problem_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    unified_report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    interpretation_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    remedy_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    client_report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    pdf_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    client: Mapped[Client | None] = relationship("Client", back_populates="reports")
    birth_detail: Mapped[BirthDetail | None] = relationship(
        "BirthDetail",
        back_populates="reports",
    )

    def __repr__(self) -> str:
        return f"<Report id={self.id} version={self.version!r}>"
