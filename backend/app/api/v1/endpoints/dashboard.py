"""Dashboard API endpoints."""

from __future__ import annotations

import uuid
from datetime import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user, get_db, get_settings_dep, user_owner_id
from backend.app.core.config import Settings
from backend.app.core.exceptions import ForbiddenError, NotFoundError, forbidden_error, not_found_error
from backend.app.models.user import User
from backend.app.repositories.report_repository import ReportRepository
from backend.app.schemas.dashboard import (
    HoroscopeRequest,
    HoroscopeResponse,
    NamingRequest,
    NamingResponse,
    PDFDownloadResponse,
    ReportDetailResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportListResponse,
)
from backend.app.services.horoscope_service import HoroscopeService
from backend.app.services.naming_service import NamingService
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_report_service(
    settings: Settings = Depends(get_settings_dep),
    session: AsyncSession = Depends(get_db),
) -> ReportService:
    return ReportService(
        reports_output_path=settings.reports_output_path,
        session=session,
        repository=ReportRepository(session),
    )


def get_horoscope_service() -> HoroscopeService:
    return HoroscopeService()


def get_naming_service() -> NamingService:
    return NamingService()


@router.post(
    "/reports/generate",
    response_model=ReportGenerateResponse,
    summary="Generate full client report",
)
async def generate_report(
    payload: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> ReportGenerateResponse:
    if not payload.date_of_birth or not payload.birth_time or not payload.birth_place:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_of_birth, birth_time, and birth_place are required.",
        )
    if payload.latitude is None or payload.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="latitude and longitude are required for report generation.",
        )

    try:
        result = await service.generate_report(
            date_of_birth=payload.date_of_birth,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place,
            birth_timezone=payload.timezone,
            latitude=payload.latitude,
            longitude=payload.longitude,
            problem_text=payload.problem_text,
            target_date=payload.target_date,
            include_pdf=payload.include_pdf,
            client_id=payload.client_id,
            birth_detail_id=payload.birth_detail_id,
            owner_id=current_user.id,
            scoped_owner_id=user_owner_id(current_user),
        )
    except ForbiddenError as exc:
        raise forbidden_error(exc.message) from exc
    except NotFoundError as exc:
        raise not_found_error("Client", str(payload.client_id)) from exc
    return ReportGenerateResponse(**result)


@router.get(
    "/reports",
    response_model=ReportListResponse,
    summary="List persisted reports",
)
async def list_reports(
    client_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> ReportListResponse:
    try:
        result = await service.list_reports(
            scoped_owner_id=user_owner_id(current_user),
            client_id=client_id,
            page=page,
            page_size=page_size,
        )
    except ForbiddenError as exc:
        raise forbidden_error(exc.message) from exc
    except NotFoundError as exc:
        raise not_found_error("Client", str(client_id)) from exc
    return ReportListResponse(**result)


@router.get(
    "/reports/{report_id}",
    response_model=ReportDetailResponse,
    summary="Get persisted report",
)
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> ReportDetailResponse:
    try:
        result = await service.get_report(report_id, scoped_owner_id=user_owner_id(current_user))
    except NotFoundError:
        raise not_found_error("Report", str(report_id)) from None
    return ReportDetailResponse(**result)


@router.delete(
    "/reports/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete persisted report",
)
async def delete_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> None:
    try:
        await service.delete_report(report_id, scoped_owner_id=user_owner_id(current_user))
    except NotFoundError:
        raise not_found_error("Report", str(report_id)) from None


@router.post(
    "/reports/pdf",
    response_model=PDFDownloadResponse,
    summary="Generate PDF from client report JSON",
)
async def generate_pdf(
    client_report: dict,
    unified_report: dict | None = None,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> PDFDownloadResponse:
    result = service.generate_pdf_from_client_report(
        client_report_json=client_report,
        unified_report_json=unified_report,
    )
    return PDFDownloadResponse(**result)


@router.get(
    "/reports/pdf/{file_name}",
    summary="Download generated PDF",
)
async def download_pdf(
    file_name: str,
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings_dep),
):
    file_path = Path(settings.reports_output_path) / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found.")
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_name,
    )


@router.post(
    "/horoscope",
    response_model=HoroscopeResponse,
    summary="Generate daily, weekly, and monthly horoscope",
)
async def generate_horoscope(
    payload: HoroscopeRequest,
    current_user: User = Depends(get_current_user),
    service: HoroscopeService = Depends(get_horoscope_service),
) -> HoroscopeResponse:
    return HoroscopeResponse(**service.generate_horoscope(**payload.model_dump()))


@router.post(
    "/naming/suggestions",
    response_model=NamingResponse,
    summary="Generate naming suggestions",
)
async def naming_suggestions(
    payload: NamingRequest,
    current_user: User = Depends(get_current_user),
    service: NamingService = Depends(get_naming_service),
) -> NamingResponse:
    return NamingResponse(**service.suggest_names(**payload.model_dump()))
