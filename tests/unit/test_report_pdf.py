"""Unit tests for report PDF generation."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.report_service import ReportService
from reports.pdf.generator import PDFGenerationResult


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_repository(mock_session):
    return AsyncMock(spec=ReportRepository)


def _patch_report_engines(service: ReportService):
    service._orchestrator.generate_json.return_value = {
        "version": "unified_report_v2",
        "summary": {"lagna_sign": "Aries", "moon_sign": "Cancer"},
    }
    service._interpretation_engine.interpret_json = AsyncMock(return_value={"summary": "ok"})
    service._remedy_engine.generate_json = AsyncMock(return_value={"remedies": []})
    service._client_writer.write_json.return_value = {
        "problem_summary": "Marriage delay",
        "astrological_root_cause": "Saturn in 7th",
    }
    service._consultation_engine.consult_json.return_value = {"metadata": {"engine": "consultation_v1"}}


@pytest.mark.asyncio
async def test_generate_report_with_pdf_success(tmp_path, mock_session, mock_repository):
    pdf_dir = tmp_path / "reports" / "generated"
    persisted_id = uuid.uuid4()
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    mock_repository.create_report.return_value = Report(
        id=persisted_id,
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={"version": "unified_report_v2"},
        interpretation_json={"summary": "ok"},
        remedy_json={"remedies": []},
        client_report_json={"problem_summary": "Marriage delay"},
        pdf_path=str(pdf_dir / "astroguru_report_test.pdf"),
        generated_at=generated_at,
        updated_at=generated_at,
    )

    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(
            reports_output_path=str(pdf_dir),
            session=mock_session,
            repository=mock_repository,
        )
        _patch_report_engines(service)

        pdf_result = PDFGenerationResult(
            file_path=str(pdf_dir / "astroguru_report_test.pdf"),
            file_name="astroguru_report_test.pdf",
            file_size_bytes=1024,
            generated_at=generated_at,
        )
        service._pdf_generator.generate = MagicMock(return_value=pdf_result)

        result = await service.generate_report(
            date_of_birth=date(1990, 1, 15),
            birth_time=time(5, 0),
            birth_place="New Delhi, India",
            birth_timezone="Asia/Kolkata",
            latitude=28.6139,
            longitude=77.2090,
            problem_text="Marriage delay",
            include_pdf=True,
        )

    assert result["report_id"] == str(persisted_id)
    assert result["pdf"]["generated"] is True
    assert result["pdf"]["filename"] == "astroguru_report_test.pdf"
    assert result["pdf"]["path"] == str(pdf_dir / "astroguru_report_test.pdf")
    assert result["pdf"]["download_url"] == "/api/v1/dashboard/reports/pdf/astroguru_report_test.pdf"

    create_kwargs = mock_repository.create_report.await_args.kwargs
    assert create_kwargs["pdf_path"] == str(pdf_dir / "astroguru_report_test.pdf")
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_report_pdf_failure_still_returns_report(tmp_path, mock_session, mock_repository):
    pdf_dir = tmp_path / "reports" / "generated"
    persisted_id = uuid.uuid4()
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    mock_repository.create_report.return_value = Report(
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

    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ClientReportWriter"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(
            reports_output_path=str(pdf_dir),
            session=mock_session,
            repository=mock_repository,
        )
        _patch_report_engines(service)
        service._pdf_generator.generate = MagicMock(side_effect=RuntimeError("PDF build failed"))

        result = await service.generate_report(
            date_of_birth=date(1990, 1, 15),
            birth_time=time(5, 0),
            birth_place="New Delhi, India",
            birth_timezone="Asia/Kolkata",
            latitude=28.6139,
            longitude=77.2090,
            include_pdf=True,
        )

    assert result["report_id"] == str(persisted_id)
    assert result["pdf"] == {"generated": False}
    create_kwargs = mock_repository.create_report.await_args.kwargs
    assert create_kwargs["pdf_path"] is None


@pytest.mark.asyncio
async def test_pdf_generator_writes_to_generated_directory(tmp_path):
    from reports.pdf import PDFReportGenerator

    output_dir = tmp_path / "reports" / "generated"
    generator = PDFReportGenerator(output_dir=output_dir)
    result = generator.generate(
        client_report_json={
            "problem_summary": "Test problem",
            "astrological_root_cause": "Mars affliction",
        },
        unified_report_json={"summary": {"lagna_sign": "Aries", "moon_sign": "Taurus"}},
    )

    pdf_file = Path(result.file_path)
    assert pdf_file.exists()
    assert pdf_file.parent == output_dir
    assert pdf_file.suffix == ".pdf"
    assert result.file_size_bytes > 0
