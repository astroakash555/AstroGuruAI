"""Dashboard API schemas for reports, horoscope, and naming."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from pydantic import Field

from backend.app.schemas.common import BaseSchema
from backend.app.schemas.validators import validate_birth_date, validate_birth_place, validate_birth_time_value


class ReportGenerateRequest(BaseSchema):
    client_id: uuid.UUID | None = None
    birth_detail_id: uuid.UUID | None = None
    date_of_birth: date | None = None
    birth_time: time | None = None
    birth_place: str | None = Field(default=None, min_length=2, max_length=512)
    timezone: str = Field(default="Asia/Kolkata", min_length=1, max_length=64)
    latitude: Decimal | None = Field(default=None, ge=Decimal("-90"), le=Decimal("90"))
    longitude: Decimal | None = Field(default=None, ge=Decimal("-180"), le=Decimal("180"))
    problem_text: str | None = Field(default=None, max_length=5000)
    target_date: date | None = None
    include_pdf: bool = False


class ReportPdfResponse(BaseSchema):
    """PDF artifact metadata returned with report generation."""

    generated: bool
    filename: str | None = None
    path: str | None = None
    download_url: str | None = None


class ReportGenerateResponse(BaseSchema):
    report_id: str
    version: str
    unified_report: dict[str, Any]
    interpretation: dict[str, Any]
    remedy_generation: dict[str, Any]
    client_report: dict[str, Any]
    pdf: ReportPdfResponse | None = None
    generated_at: datetime


class ReportSummaryResponse(BaseSchema):
    """Lightweight report entry for history listings."""

    report_id: str
    client_id: uuid.UUID | None = None
    birth_detail_id: uuid.UUID | None = None
    version: str
    problem_text: str | None = None
    lagna_sign: str | None = None
    moon_sign: str | None = None
    generated_at: datetime
    has_pdf: bool = False


class ReportDetailResponse(BaseSchema):
    """Full persisted report payload."""

    report_id: str
    client_id: uuid.UUID | None = None
    birth_detail_id: uuid.UUID | None = None
    version: str
    problem_text: str | None = None
    unified_report: dict[str, Any]
    interpretation: dict[str, Any]
    remedy_generation: dict[str, Any]
    client_report: dict[str, Any]
    pdf: ReportPdfResponse | None = None
    generated_at: datetime
    updated_at: datetime


class ReportListResponse(BaseSchema):
    """Paginated report history response."""

    items: list[ReportSummaryResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PDFDownloadResponse(BaseSchema):
    pdf_id: str
    file_name: str
    file_path: str
    file_size_bytes: int
    download_url: str


class HoroscopeRequest(BaseSchema):
    moon_sign_index: int = Field(..., ge=0, le=11)
    lagna_sign_index: int = Field(..., ge=0, le=11)
    current_mahadasha: str | None = None
    current_antardasha: str | None = None
    transit_summary: dict[str, str] = Field(default_factory=dict)
    target_date: date | None = None


class HoroscopeResponse(BaseSchema):
    horoscope: dict[str, Any]


class NamingRequest(BaseSchema):
    nakshatra: str = Field(..., min_length=2, max_length=64)
    pada: int = Field(..., ge=1, le=4)
    rashi_sign_index: int = Field(..., ge=0, le=11)
    gender: str = Field(default="neutral", pattern="^(male|female|neutral)$")
    count: int = Field(default=8, ge=1, le=20)


class NamingResponse(BaseSchema):
    naming: dict[str, Any]
