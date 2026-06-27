"""Astrological remedy prescription model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import RemedySourceType, RemedyStatus, RemedyType
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.client import Client


class Remedy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Prescribed astrological remedy linked to a client and optional source report.

    Uses polymorphic-style `source_report_id` + `source_type` to reference
    dasha, transit, Lal Kitab, KP, or AI-generated recommendations.
    """

    __tablename__ = "remedies"
    __table_args__ = (
        Index("ix_remedies_client_id", "client_id"),
        Index("ix_remedies_birth_detail_id", "birth_detail_id"),
        Index("ix_remedies_source", "source_type", "source_report_id"),
        Index("ix_remedies_status", "status"),
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
    source_type: Mapped[RemedySourceType] = mapped_column(
        enum_column(RemedySourceType, "remedy_source_type"),
        nullable=False,
    )
    source_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    remedy_type: Mapped[RemedyType] = mapped_column(
        enum_column(RemedyType, "remedy_type"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    planet: Mapped[str | None] = mapped_column(String(32), nullable=True)
    priority: Mapped[int] = mapped_column(default=1, server_default="1", nullable=False)
    status: Mapped[RemedyStatus] = mapped_column(
        enum_column(RemedyStatus, "remedy_status"),
        default=RemedyStatus.PRESCRIBED,
        server_default=RemedyStatus.PRESCRIBED.value,
        nullable=False,
    )
    prescribed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    client: Mapped[Client] = relationship("Client", back_populates="remedies")
    birth_detail: Mapped[BirthDetail | None] = relationship(
        "BirthDetail",
        back_populates="remedies",
    )

    def __repr__(self) -> str:
        return f"<Remedy id={self.id} type={self.remedy_type.value} title={self.title!r}>"
