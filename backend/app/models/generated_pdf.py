"""Generated PDF artifact model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import PDFGenerationStatus, PDFReportType, PDFStorageBackend
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail
    from backend.app.models.client import Client


class GeneratedPDF(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Persisted PDF report artifact with storage metadata.

    References the originating report entity via `source_report_id` and
    `report_type` for traceability.
    """

    __tablename__ = "generated_pdfs"
    __table_args__ = (
        Index("ix_generated_pdfs_client_id", "client_id"),
        Index("ix_generated_pdfs_birth_detail_id", "birth_detail_id"),
        Index("ix_generated_pdfs_report_type", "report_type"),
        Index("ix_generated_pdfs_status", "status"),
        Index("ix_generated_pdfs_generated_at", "generated_at"),
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
    report_type: Mapped[PDFReportType] = mapped_column(
        enum_column(PDFReportType, "pdf_report_type"),
        nullable=False,
    )
    source_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str] = mapped_column(
        String(64),
        default="application/pdf",
        server_default="application/pdf",
        nullable=False,
    )
    storage_backend: Mapped[PDFStorageBackend] = mapped_column(
        enum_column(PDFStorageBackend, "pdf_storage_backend"),
        default=PDFStorageBackend.LOCAL,
        server_default=PDFStorageBackend.LOCAL.value,
        nullable=False,
    )
    template_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[PDFGenerationStatus] = mapped_column(
        enum_column(PDFGenerationStatus, "pdf_generation_status"),
        default=PDFGenerationStatus.QUEUED,
        server_default=PDFGenerationStatus.QUEUED.value,
        nullable=False,
    )
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    client: Mapped[Client] = relationship("Client", back_populates="generated_pdfs")
    birth_detail: Mapped[BirthDetail | None] = relationship(
        "BirthDetail",
        back_populates="generated_pdfs",
    )

    def __repr__(self) -> str:
        return f"<GeneratedPDF id={self.id} file_name={self.file_name!r} status={self.status.value}>"
