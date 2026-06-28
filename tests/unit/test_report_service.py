"""Unit tests for ReportService persistence."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.report_service import ReportService
from backend.app.core.exceptions import NotFoundError, ValidationError


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
         patch("backend.app.services.report_service.ProfessionalReportBuilder"), \
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

    valid_client_report = {
        "sections": [
            {
                "section_id": "birth_details",
                "title": "Birth",
                "narrative": "Narrative",
                "facts": ["Birth place: New Delhi, India"],
                "confidence": 0.8,
                "confidence_label": "80%",
            }
        ],
        "problem_summary": "Marriage delay",
    }

    report_service._orchestrator.generate_json.return_value = {
        "version": "unified_report_v2",
        "summary": {},
    }
    report_service._interpretation_engine.interpret_json = AsyncMock(return_value={"summary": "ok"})
    report_service._remedy_engine.generate_json = AsyncMock(return_value={"remedies": []})
    report_service._report_builder.build.return_value = MagicMock()
    report_service._consultation_brain.run = MagicMock(return_value=MagicMock())
    report_service._consultation_engine.consult_json.return_value = {
        "metadata": {"engine": "consultation_v1"},
    }

    with patch(
        "backend.app.services.report_service.MasterConsultationEngine"
    ) as master_engine_cls, patch(
        "backend.app.services.report_service.apply_master_consultation_delivery",
        side_effect=lambda result, master, report_input=None: result,
    ), patch(
        "backend.app.services.report_service.professional_report_to_client_json",
        return_value=valid_client_report,
    ):
        master_engine_cls.return_value.generate.return_value = MagicMock()
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
    persisted_payload = mock_repository.create_report.await_args.kwargs["client_report_json"]
    assert isinstance(persisted_payload["sections"][0]["facts"], list)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_report_blocks_persistence_when_section_facts_are_objects(
    report_service,
    mock_session,
    mock_repository,
):
    report_service._orchestrator.generate_json.return_value = {
        "version": "unified_report_v2",
        "summary": {},
    }
    report_service._interpretation_engine.interpret_json = AsyncMock(return_value={"summary": "ok"})
    report_service._remedy_engine.generate_json = AsyncMock(return_value={"remedies": []})
    report_service._report_builder.build.return_value = MagicMock()
    report_service._consultation_brain.run = MagicMock(return_value=MagicMock())
    report_service._consultation_engine.consult_json.return_value = {
        "metadata": {"engine": "consultation_v1"},
    }

    invalid_client_report = {
        "sections": [
            {
                "section_id": "birth_details",
                "title": "Birth",
                "narrative": "Narrative",
                "facts": {"birth_place": "Delhi"},
                "confidence": 0.8,
                "confidence_label": "80%",
            }
        ],
        "problem_summary": "Marriage delay",
    }

    with patch(
        "backend.app.services.report_service.MasterConsultationEngine"
    ) as master_engine_cls, patch(
        "backend.app.services.report_service.apply_master_consultation_delivery",
        side_effect=lambda result, master, report_input=None: result,
    ), patch(
        "backend.app.services.report_service.professional_report_to_client_json",
        return_value=invalid_client_report,
    ):
        master_engine_cls.return_value.generate.return_value = MagicMock()
        with pytest.raises(ValidationError, match="must be a list"):
            await report_service.generate_report(
                date_of_birth=date(1990, 1, 15),
                birth_time=time(5, 0),
                birth_place="New Delhi, India",
                birth_timezone="Asia/Kolkata",
                latitude=28.6139,
                longitude=77.2090,
                problem_text="Marriage delay",
            )

    mock_repository.create_report.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_report_without_repository_raises():
    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ProfessionalReportBuilder"), \
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
         patch("backend.app.services.report_service.ProfessionalReportBuilder"), \
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
         patch("backend.app.services.report_service.ProfessionalReportBuilder"), \
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
         patch("backend.app.services.report_service.ProfessionalReportBuilder"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(session=mock_session, repository=mock_repository)

    report_id = uuid.uuid4()
    mock_repository.delete_report.return_value = True
    await service.delete_report(report_id)
    mock_repository.delete_report.assert_awaited_once_with(report_id, owner_id=None)
    mock_session.commit.assert_awaited_once()
