"""End-to-end integration tests for the report generation intelligence pipeline."""

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
from reports.intelligence_schemas import FusionReportSchema
from reports.orchestrator import ReportOrchestrator
from reports.schemas import UnifiedReportJSON
from reports.types import ReportInput
from tests.helpers import override_current_user, override_usage_service


GENERATE_URL = "/api/v1/dashboard/reports/generate"


def _sample_birth_data():
    pytest.importorskip("swisseph")
    from astrology_engine import BirthData

    return BirthData(
        datetime_utc=datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )


def _report_input() -> ReportInput:
    return ReportInput(
        birth_data=_sample_birth_data(),
        birth_place="New Delhi, India",
        problem_text="I am facing delay in marriage.",
        target_date=datetime(2024, 6, 15, tzinfo=timezone.utc).date(),
    )


@pytest.fixture
def orchestrator() -> ReportOrchestrator:
    pytest.importorskip("swisseph")
    return ReportOrchestrator()


class TestReportOrchestratorIntelligence:
    def test_unified_report_contains_intelligence_sections(self, orchestrator: ReportOrchestrator) -> None:
        payload = orchestrator.generate_json(_report_input())

        UnifiedReportJSON.model_validate(payload)
        FusionReportSchema.model_validate(payload["fusion"])

        assert payload["vedic"]["metadata"]["engine"] == "vedic_intelligence_v1"
        assert payload["kp"]["metadata"]["engine"] == "kp_intelligence_v1"
        assert payload["lal_kitab_intelligence"]["metadata"]["engine"] == "lal_kitab_intelligence_v1"
        assert payload["fusion"]["metadata"]["engine"] == "intelligence_fusion_v1"

        assert len(payload["vedic"]["observations"]) > 0
        assert len(payload["kp"]["observations"]) > 0
        assert len(payload["lal_kitab_intelligence"]["observations"]) > 0
        assert isinstance(payload["fusion"]["root_causes"], list)
        assert isinstance(payload["fusion"]["conflicts"], list)
        assert isinstance(payload["fusion"]["recommendations"], list)
        assert 0.0 <= payload["fusion"]["confidence"] <= 1.0

        active_engines = payload["fusion"]["metadata"].get("active_engines", [])
        assert "vedic" in active_engines
        assert "kp" in active_engines
        assert "lal_kitab" in active_engines

    def test_intelligence_output_is_deterministic_for_fixed_input(
        self,
        orchestrator: ReportOrchestrator,
    ) -> None:
        first = orchestrator.generate_json(_report_input())
        second = orchestrator.generate_json(_report_input())

        assert first["vedic"]["observations"] == second["vedic"]["observations"]
        assert first["kp"]["observations"] == second["kp"]["observations"]
        assert first["lal_kitab_intelligence"]["observations"] == second["lal_kitab_intelligence"]["observations"]
        assert first["fusion"]["root_causes"] == second["fusion"]["root_causes"]
        assert first["fusion"]["confidence"] == second["fusion"]["confidence"]


@pytest.fixture
async def pipeline_client(tmp_path, test_user):
    pytest.importorskip("swisseph")

    session = AsyncMock()
    session.commit = AsyncMock()
    repository = AsyncMock(spec=ReportRepository)
    report_id = uuid.uuid4()
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)

    async def _create_report(**kwargs):
        return Report(
            id=report_id,
            client_id=kwargs.get("client_id"),
            birth_detail_id=kwargs.get("birth_detail_id"),
            version=kwargs["version"],
            problem_text=kwargs.get("problem_text"),
            unified_report_json=kwargs["unified_report_json"],
            interpretation_json=kwargs["interpretation_json"],
            remedy_json=kwargs["remedy_json"],
            client_report_json=kwargs["client_report_json"],
            pdf_path=kwargs.get("pdf_path"),
            generated_at=kwargs.get("generated_at", generated_at),
            updated_at=generated_at,
        )

    repository.create_report.side_effect = _create_report

    with patch(
        "backend.app.services.report_service.AstroInterpretationEngine"
    ) as interpretation_cls, patch(
        "backend.app.services.report_service.RemedyGenerationEngine"
    ) as remedy_cls, patch(
        "backend.app.services.report_service.ConsultationEngine"
    ) as consultation_cls:
        interpretation = MagicMock()
        interpretation.interpret_json = AsyncMock(
            return_value={"summary": "Deterministic fallback interpretation."}
        )
        interpretation_cls.return_value = interpretation

        remedy = MagicMock()
        remedy.generate_json = AsyncMock(return_value={"remedies": []})
        remedy_cls.return_value = remedy

        consultation = MagicMock()
        consultation.consult_json.return_value = {"metadata": {"engine": "consultation_v1"}}
        consultation_cls.return_value = consultation

        service = ReportService(
            session=session,
            repository=repository,
            reports_output_path=str(tmp_path / "generated"),
        )

        app = create_app()
        app.dependency_overrides[get_report_service] = lambda: service
        override_current_user(app, test_user)
        override_usage_service(app)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, service, repository, session, report_id

        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_report_generation_pipeline_persists_intelligence_payload(pipeline_client, tmp_path) -> None:
    client, _, repository, session, report_id = pipeline_client

    response = await client.post(
        GENERATE_URL,
        json={
            "date_of_birth": "1990-01-15",
            "birth_time": "05:00:00",
            "birth_place": "New Delhi, India",
            "timezone": "Asia/Kolkata",
            "latitude": "28.6139",
            "longitude": "77.2090",
            "problem_text": "Marriage delay",
            "include_pdf": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["report_id"] == str(report_id)

    unified = body["unified_report"]
    assert unified["vedic"]["metadata"]["engine"] == "vedic_intelligence_v1"
    assert unified["kp"]["metadata"]["engine"] == "kp_intelligence_v1"
    assert unified["lal_kitab_intelligence"]["metadata"]["engine"] == "lal_kitab_intelligence_v1"
    assert unified["fusion"]["metadata"]["engine"] == "intelligence_fusion_v1"
    assert unified["fusion"]["confidence"] >= 0.0
    assert body["pdf"] is not None
    assert body["pdf"]["generated"] is True
    assert (tmp_path / "generated" / body["pdf"]["filename"]).exists()

    repository.create_report.assert_awaited_once()
    session.commit.assert_awaited_once()

    persisted_payload = repository.create_report.await_args.kwargs["unified_report_json"]
    assert persisted_payload["fusion"]["root_causes"] == unified["fusion"]["root_causes"]
    assert persisted_payload["vedic"]["observations"]
    assert persisted_payload["lal_kitab_intelligence"]["remedies"] is not None


@pytest.mark.asyncio
async def test_report_service_generate_report_end_to_end(tmp_path) -> None:
    pytest.importorskip("swisseph")

    session = AsyncMock()
    session.commit = AsyncMock()
    repository = AsyncMock(spec=ReportRepository)
    report_id = uuid.uuid4()

    repository.create_report.return_value = Report(
        id=report_id,
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={},
        interpretation_json={},
        remedy_json={},
        client_report_json={},
        pdf_path=str(tmp_path / "generated" / "test.pdf"),
        generated_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch(
        "backend.app.services.report_service.AstroInterpretationEngine"
    ) as interpretation_cls, patch(
        "backend.app.services.report_service.RemedyGenerationEngine"
    ) as remedy_cls, patch(
        "backend.app.services.report_service.ConsultationEngine"
    ) as consultation_cls:
        interpretation = MagicMock()
        interpretation.interpret_json = AsyncMock(return_value={"summary": "Interpretation"})
        interpretation_cls.return_value = interpretation

        remedy = MagicMock()
        remedy.generate_json = AsyncMock(return_value={"remedies": []})
        remedy_cls.return_value = remedy

        consultation = MagicMock()
        consultation.consult_json.return_value = {"metadata": {"engine": "consultation_v1"}}
        consultation_cls.return_value = consultation

        service = ReportService(
            session=session,
            repository=repository,
            reports_output_path=str(tmp_path / "generated"),
        )

        result = await service.generate_report(
            date_of_birth=datetime(1990, 1, 15).date(),
            birth_time=datetime.strptime("05:00:00", "%H:%M:%S").time(),
            birth_place="New Delhi, India",
            birth_timezone="Asia/Kolkata",
            latitude=28.6139,
            longitude=77.2090,
            problem_text="Marriage delay",
            include_pdf=True,
        )

    unified = result["unified_report"]
    assert unified["fusion"]["metadata"]["engine"] == "intelligence_fusion_v1"
    assert unified["vedic"]["observations"]
    assert unified["kp"]["event_timing"] is not None
    assert unified["lal_kitab_intelligence"]["remedies"] is not None
    assert result["pdf"]["generated"] is True
    repository.create_report.assert_awaited_once()
