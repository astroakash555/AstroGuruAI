"""Client (end-user) model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import Gender
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.generated_pdf import GeneratedPDF
    from backend.app.models.remedy import Remedy
    from backend.app.models.report import Report
    from backend.app.models.user import User
    from backend.app.models.user_query import UserQuery


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Platform client who receives astrology consultations and reports.

    A client may have multiple birth profiles (self, family members) and
    accumulate reports, remedies, PDFs, and AI query history over time.
    """

    __tablename__ = "clients"
    __table_args__ = (
        Index("ix_clients_email", "email"),
        Index("ix_clients_phone", "phone"),
        Index("ix_clients_is_active", "is_active"),
        Index("ix_clients_created_at", "created_at"),
        Index("ix_clients_owner_id", "owner_id"),
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    gender: Mapped[Gender] = mapped_column(
        enum_column(Gender, "gender"),
        default=Gender.UNSPECIFIED,
        server_default=Gender.UNSPECIFIED.value,
        nullable=False,
    )
    preferred_language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        server_default="en",
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        default="UTC",
        server_default="UTC",
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    birth_details: Mapped[list[BirthDetail]] = relationship(
        "BirthDetail",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    remedies: Mapped[list[Remedy]] = relationship(
        "Remedy",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    generated_pdfs: Mapped[list[GeneratedPDF]] = relationship(
        "GeneratedPDF",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_queries: Mapped[list[UserQuery]] = relationship(
        "UserQuery",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    reports: Mapped[list[Report]] = relationship(
        "Report",
        back_populates="client",
    )
    owner: Mapped[User | None] = relationship("User", back_populates="clients")

    def __repr__(self) -> str:
        return f"<Client id={self.id} full_name={self.full_name!r}>"
