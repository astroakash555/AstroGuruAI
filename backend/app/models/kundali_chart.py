"""Kundali (natal) chart model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import Ayanamsa, ChartSystem, HouseSystem, ReportStatus
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.dasha_report import DashaReport


class KundaliChart(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Computed natal chart snapshot for a birth profile.

    Stores structured planetary positions, house cusps, and divisional chart
    payloads in JSONB for flexible schema evolution.
    """

    __tablename__ = "kundali_charts"
    __table_args__ = (
        Index("ix_kundali_charts_birth_detail_id", "birth_detail_id"),
        Index("ix_kundali_charts_status", "status"),
        Index("ix_kundali_charts_is_current", "is_current"),
    )

    birth_detail_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_details.id", ondelete="CASCADE"),
        nullable=False,
    )
    chart_system: Mapped[ChartSystem] = mapped_column(
        enum_column(ChartSystem, "chart_system"),
        default=ChartSystem.VEDIC,
        server_default=ChartSystem.VEDIC.value,
        nullable=False,
    )
    ayanamsa: Mapped[Ayanamsa] = mapped_column(
        enum_column(Ayanamsa, "ayanamsa"),
        default=Ayanamsa.LAHIRI,
        server_default=Ayanamsa.LAHIRI.value,
        nullable=False,
    )
    house_system: Mapped[HouseSystem] = mapped_column(
        enum_column(HouseSystem, "house_system"),
        default=HouseSystem.WHOLE_SIGN,
        server_default=HouseSystem.WHOLE_SIGN.value,
        nullable=False,
    )
    chart_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    divisional_charts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    computation_version: Mapped[str] = mapped_column(
        String(32),
        default="1.0.0",
        server_default="1.0.0",
        nullable=False,
    )
    status: Mapped[ReportStatus] = mapped_column(
        enum_column(ReportStatus, "report_status"),
        default=ReportStatus.COMPLETED,
        server_default=ReportStatus.COMPLETED.value,
        nullable=False,
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    birth_detail: Mapped[BirthDetail] = relationship(
        "BirthDetail",
        back_populates="kundali_charts",
    )
    dasha_reports: Mapped[list[DashaReport]] = relationship(
        "DashaReport",
        back_populates="kundali_chart",
    )

    def __repr__(self) -> str:
        return f"<KundaliChart id={self.id} birth_detail_id={self.birth_detail_id}>"
