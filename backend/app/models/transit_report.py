"""Transit (Gochar) report model."""

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


class TransitReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Planetary transit analysis relative to a natal chart.

    Covers a configurable observation window with snapshot data at
    `reference_datetime`.
    """

    __tablename__ = "transit_reports"
    __table_args__ = (
        Index("ix_transit_reports_birth_detail_id", "birth_detail_id"),
        Index("ix_transit_reports_reference_datetime", "reference_datetime"),
        Index("ix_transit_reports_status", "status"),
    )

    birth_detail_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_details.id", ondelete="CASCADE"),
        nullable=False,
    )
    reference_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    significant_transits: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
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
        back_populates="transit_reports",
    )

    def __repr__(self) -> str:
        return (
            f"<TransitReport id={self.id} reference={self.reference_datetime} "
            f"window=[{self.window_start}, {self.window_end}]>"
        )
