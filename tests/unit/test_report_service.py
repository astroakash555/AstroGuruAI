"""Unit tests for ReportService persistence."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.report_service import ReportService
from backend.app.core.exceptions import NotFoundError


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_repository(mock_session):
    return AsyncMock(spec=ReportRepository)


@pytest.fixture
def report_service(mock_session, mock_repository):
    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(session=mock_session, repository=mock_repository)
        yield service


@pytest.mark.asyncio
async def test_generate_report_persists_and_returns_database_id(
    report_service,
    mock_session,
    mock_repository,
):
    persisted_id = uuid.uuid4()
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    persisted_report = Report(
        id=persisted_id,
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={"version": "unified_report_v2"},
        interpretation_json={"summary": "ok"},
        remedy_json={"remedies": []},
        client_report_json={"problem_summary": "Marriage delay"},
        pdf_path=None,
        generated_at=generated_at,
        updated_at=generated_at,
    )
    mock_repository.create_report.return_value = persisted_report

    report_service._orchestrator.generate_json.return_value = {
        "version": "unified_report_v2",
        "summary": {},
    }
    report_service._interpretation_engine.interpret_json = AsyncMock(return_value={"summary": "ok"})
    report_service._remedy_engine.generate_json = AsyncMock(return_value={"remedies": []})
    report_service._client_writer.write_json.return_value = {"problem_summary": "Marriage delay"}
    report_service._consultation_engine.consult_json.return_value = {
        "metadata": {"engine": "consultation_v1"},
    }

    result = await report_service.generate_report(
        date_of_birth=date(1990, 1, 15),
        birth_time=time(5, 0),
        birth_place="New Delhi, India",
        birth_timezone="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
        problem_text="Marriage delay",
    )

    assert result["report_id"] == str(persisted_id)
    assert result["version"] == "unified_report_v2"
    mock_repository.create_report.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_report_without_repository_raises():
    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService()

    with pytest.raises(RuntimeError, match="Report persistence is not configured"):
        await service.generate_report(
            date_of_birth=date(1990, 1, 15),
            birth_time=time(5, 0),
            birth_place="New Delhi, India",
            birth_timezone="Asia/Kolkata",
            latitude=28.6139,
            longitude=77.2090,
        )


@pytest.mark.asyncio
async def test_list_reports_returns_pagination(mock_repository):
    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(repository=mock_repository)

    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    report = Report(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={"summary": {"lagna_sign": "Aries", "moon_sign": "Cancer"}},
        interpretation_json={},
        remedy_json={},
        client_report_json={},
        pdf_path=None,
        generated_at=generated_at,
        updated_at=generated_at,
    )
    mock_repository.list_reports.return_value = ([report], 1)

    result = await service.list_reports(page=1, page_size=20)
    assert result["total"] == 1
    assert result["items"][0]["lagna_sign"] == "Aries"
    assert result["items"][0]["has_pdf"] is False


@pytest.mark.asyncio
async def test_get_report_raises_not_found(mock_repository):
    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(repository=mock_repository)

    mock_repository.get_report.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_report(uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_report_commits(mock_session, mock_repository):
    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(session=mock_session, repository=mock_repository)

    report_id = uuid.uuid4()
    mock_repository.delete_report.return_value = True
    await service.delete_report(report_id)
    mock_repository.delete_report.assert_awaited_once_with(report_id)
    mock_session.commit.assert_awaited_once()
