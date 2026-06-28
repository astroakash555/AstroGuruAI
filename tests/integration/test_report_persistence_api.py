"""Integration tests for persisted report generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.api.v1.endpoints.dashboard import get_report_service
from backend.app.main import create_app
from backend.app.models.report import Report
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.report_service import ReportService
from tests.helpers import override_current_user, override_usage_service


@pytest.fixture
def persisted_report_id():
    return uuid.uuid4()


@pytest.fixture
def mock_persistence_stack(persisted_report_id):
    session = AsyncMock()
    session.commit = AsyncMock()
    repository = AsyncMock(spec=ReportRepository)
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    repository.create_report.return_value = Report(
        id=persisted_report_id,
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={"version": "unified_report_v2", "summary": {"lagna_sign": "Taurus"}},
        interpretation_json={"summary": "Interpretation"},
        remedy_json={"remedies": []},
        client_report_json={"problem_summary": "Marriage delay"},
        pdf_path=None,
        generated_at=generated_at,
        updated_at=generated_at,
    )
    return session, repository, persisted_report_id


@pytest.fixture
async def persistence_client(mock_persistence_stack, test_user):
    session, repository, _ = mock_persistence_stack

    with patch("backend.app.services.report_service.ReportOrchestrator") as orchestrator_cls, \
         patch("backend.app.services.report_service.AstroInterpretationEngine") as interpretation_cls, \
         patch("backend.app.services.report_service.RemedyGenerationEngine") as remedy_cls, \
         patch("backend.app.services.report_service.ClientReportWriter") as client_writer_cls, \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine") as consultation_cls:
        orchestrator = MagicMock()
        orchestrator.generate_json.return_value = {
            "version": "unified_report_v2",
            "summary": {"lagna_sign": "Taurus"},
        }
        orchestrator_cls.return_value = orchestrator

        interpretation = MagicMock()
        interpretation.interpret_json = AsyncMock(return_value={"summary": "Interpretation"})
        interpretation_cls.return_value = interpretation

        remedy = MagicMock()
        remedy.generate_json = AsyncMock(return_value={"remedies": []})
        remedy_cls.return_value = remedy

        client_writer = MagicMock()
        client_writer.write_json.return_value = {"problem_summary": "Marriage delay"}
        client_writer_cls.return_value = client_writer

        consultation = MagicMock()
        consultation.consult_json.return_value = {"metadata": {"engine": "consultation_v1"}}
        consultation_cls.return_value = consultation

        service = ReportService(session=session, repository=repository)

        app = create_app()
        app.dependency_overrides[get_report_service] = lambda: service
        override_current_user(app, test_user)
        override_usage_service(app)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, service, repository, session

        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_generate_report_api_returns_persisted_report_id(persistence_client, persisted_report_id):
    client, service, repository, session = persistence_client

    response = await client.post(
        "/api/v1/dashboard/reports/generate",
        json={
            "date_of_birth": "1990-01-15",
            "birth_time": "05:00:00",
            "birth_place": "New Delhi, India",
            "timezone": "Asia/Kolkata",
            "latitude": "28.6139",
            "longitude": "77.2090",
            "problem_text": "Marriage delay",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["report_id"] == str(persisted_report_id)
    assert body["version"] == "unified_report_v2"
    assert body["unified_report"]["summary"]["lagna_sign"] == "Taurus"
    repository.create_report.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_report_api_passes_client_ids_to_repository(persistence_client, test_user):
    client, _, repository, session = persistence_client
    client_id = str(uuid.uuid4())
    birth_detail_id = str(uuid.uuid4())

    from backend.app.models.client import Client
    from backend.app.models.enums import Gender

    lookup_result = MagicMock()
    lookup_result.scalar_one_or_none.return_value = Client(
        id=uuid.UUID(client_id),
        owner_id=test_user.id,
        full_name="Test Client",
        gender=Gender.UNSPECIFIED,
    )
    session.execute.return_value = lookup_result

    response = await client.post(
        "/api/v1/dashboard/reports/generate",
        json={
            "client_id": client_id,
            "birth_detail_id": birth_detail_id,
            "date_of_birth": "1990-01-15",
            "birth_time": "05:00:00",
            "birth_place": "New Delhi, India",
            "timezone": "Asia/Kolkata",
            "latitude": "28.6139",
            "longitude": "77.2090",
        },
    )

    assert response.status_code == 200
    call_kwargs = repository.create_report.await_args.kwargs
    assert call_kwargs["client_id"] == uuid.UUID(client_id)
    assert call_kwargs["birth_detail_id"] == uuid.UUID(birth_detail_id)
