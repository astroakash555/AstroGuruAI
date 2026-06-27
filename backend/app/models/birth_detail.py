"""Birth detail model — canonical input for all chart and report generation."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import RelationshipType
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.client import Client
    from backend.app.models.dasha_report import DashaReport
    from backend.app.models.generated_pdf import GeneratedPDF
    from backend.app.models.kp_report import KPReport
    from backend.app.models.kundali_chart import KundaliChart
    from backend.app.models.lal_kitab_report import LalKitabReport
    from backend.app.models.remedy import Remedy
    from backend.app.models.report import Report
    from backend.app.models.transit_report import TransitReport
    from backend.app.models.user_query import UserQuery


class BirthDetail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Birth data for a person linked to a client.

    Serves as the root entity for kundali charts and all derived report types.
    """

    __tablename__ = "birth_details"
    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "person_name",
            "birth_datetime",
            name="uq_birth_details_client_person_datetime",
        ),
        Index("ix_birth_details_client_id", "client_id"),
        Index("ix_birth_details_birth_datetime", "birth_datetime"),
        Index("ix_birth_details_is_primary", "is_primary"),
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_to_client: Mapped[RelationshipType] = mapped_column(
        enum_column(RelationshipType, "relationship_type"),
        default=RelationshipType.SELF,
        server_default=RelationshipType.SELF.value,
        nullable=False,
    )
    birth_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    birth_place_name: Mapped[str] = mapped_column(String(512), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    client: Mapped[Client] = relationship("Client", back_populates="birth_details")
    kundali_charts: Mapped[list[KundaliChart]] = relationship(
        "KundaliChart",
        back_populates="birth_detail",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    dasha_reports: Mapped[list[DashaReport]] = relationship(
        "DashaReport",
        back_populates="birth_detail",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    transit_reports: Mapped[list[TransitReport]] = relationship(
        "TransitReport",
        back_populates="birth_detail",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    lal_kitab_reports: Mapped[list[LalKitabReport]] = relationship(
        "LalKitabReport",
        back_populates="birth_detail",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    kp_reports: Mapped[list[KPReport]] = relationship(
        "KPReport",
        back_populates="birth_detail",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    remedies: Mapped[list[Remedy]] = relationship(
        "Remedy",
        back_populates="birth_detail",
    )
    generated_pdfs: Mapped[list[GeneratedPDF]] = relationship(
        "GeneratedPDF",
        back_populates="birth_detail",
    )
    user_queries: Mapped[list[UserQuery]] = relationship(
        "UserQuery",
        back_populates="birth_detail",
    )
    reports: Mapped[list[Report]] = relationship(
        "Report",
        back_populates="birth_detail",
    )

    def __repr__(self) -> str:
        return (
            f"<BirthDetail id={self.id} person_name={self.person_name!r} "
            f"birth_datetime={self.birth_datetime}>"
        )
