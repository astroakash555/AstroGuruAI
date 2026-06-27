"""Dasha (planetary period) report model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import DashaSystem, ReportStatus
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.kundali_chart import KundaliChart


class DashaReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Vimshottari or other dasha system report for a birth profile.

    `report_data` holds the full dasha tree; current period fields enable
    fast lookup without parsing JSON on every read.
    """

    __tablename__ = "dasha_reports"
    __table_args__ = (
        Index("ix_dasha_reports_birth_detail_id", "birth_detail_id"),
        Index("ix_dasha_reports_kundali_chart_id", "kundali_chart_id"),
        Index("ix_dasha_reports_status", "status"),
        Index("ix_dasha_reports_generated_at", "generated_at"),
    )

    birth_detail_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_details.id", ondelete="CASCADE"),
        nullable=False,
    )
    kundali_chart_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kundali_charts.id", ondelete="SET NULL"),
        nullable=True,
    )
    dasha_system: Mapped[DashaSystem] = mapped_column(
        enum_column(DashaSystem, "dasha_system"),
        default=DashaSystem.VIMSHOTTARI,
        server_default=DashaSystem.VIMSHOTTARI.value,
        nullable=False,
    )
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    current_mahadasha: Mapped[str | None] = mapped_column(String(32), nullable=True)
    current_antardasha: Mapped[str | None] = mapped_column(String(32), nullable=True)
    current_pratyantardasha: Mapped[str | None] = mapped_column(String(32), nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
        back_populates="dasha_reports",
    )
    kundali_chart: Mapped[KundaliChart | None] = relationship(
        "KundaliChart",
        back_populates="dasha_reports",
    )

    def __repr__(self) -> str:
        return f"<DashaReport id={self.id} system={self.dasha_system.value}>"
