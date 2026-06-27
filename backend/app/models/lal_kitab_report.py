"""Lal Kitab report model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import ReportStatus
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail


class LalKitabReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Lal Kitab specific chart analysis and remedial indicators.

    Stores house-wise planetary bindings, debts (rin), and remedy mappings
    in structured JSONB payloads.
    """

    __tablename__ = "lal_kitab_reports"
    __table_args__ = (
        Index("ix_lal_kitab_reports_birth_detail_id", "birth_detail_id"),
        Index("ix_lal_kitab_reports_status", "status"),
    )

    birth_detail_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_details.id", ondelete="CASCADE"),
        nullable=False,
    )
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    house_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    planetary_debts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    suggested_remedies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    ai_interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        enum_column(ReportStatus, "report_status"),
        default=ReportStatus.COMPLETED,
        server_default=ReportStatus.COMPLETED.value,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    birth_detail: Mapped[BirthDetail] = relationship(
        "BirthDetail",
        back_populates="lal_kitab_reports",
    )

    def __repr__(self) -> str:
        return f"<LalKitabReport id={self.id} birth_detail_id={self.birth_detail_id}>"
