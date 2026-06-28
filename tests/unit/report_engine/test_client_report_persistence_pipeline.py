"""End-to-end persistence contract tests for client report sections."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.core.exceptions import ValidationError
from backend.app.repositories.report_repository import ReportRepository
from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.serializers import professional_report_to_client_json
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage
from backend.app.services.report_service import ReportService


def test_builder_serializer_database_and_get_payload_preserve_string_facts(
    sample_unified_report,
    sample_remedy_generation,
):
    builder = ProfessionalReportBuilder()
    report_input = ProfessionalReportInput(
        unified_report=sample_unified_report,
        remedy_generation=sample_remedy_generation,
        problem_text="Marriage delay",
        language=ReportLanguage.HINDI,
    )

    builder_result = builder.build(report_input)
    serialized = professional_report_to_client_json(builder_result, report_input=report_input)

    database_payload = copy.deepcopy(serialized)
    get_api_payload = {
        "report_id": str(uuid.uuid4()),
        "client_report": database_payload,
    }
    frontend_payload = get_api_payload["client_report"]

    assert len(serialized["sections"]) == 14
    for section in serialized["sections"]:
        assert isinstance(section["facts"], list), section["section_id"]
        assert all(isinstance(line, str) for line in section["facts"]), section["section_id"]

    for section in get_api_payload["client_report"]["sections"]:
        assert isinstance(section["facts"], list)

    for section in frontend_payload["sections"]:
        assert isinstance(section["facts"], list)
        assert all(isinstance(line, str) for line in section["facts"])


@pytest.mark.asyncio
async def test_repository_rejects_dict_facts_before_insert():
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    repository = ReportRepository(session)

    with pytest.raises(ValidationError, match="must be a list"):
        await repository.create_report(
            owner_id=None,
            client_id=None,
            birth_detail_id=None,
            version="unified_report_v2",
            problem_text="Marriage delay",
            unified_report_json={},
            interpretation_json={},
            remedy_json={},
            client_report_json={
                "sections": [
                    {
                        "section_id": "birth_details",
                        "title": "Birth",
                        "narrative": "Narrative",
                        "facts": {"birth_place": "Delhi"},
                        "confidence": 0.8,
                        "confidence_label": "80%",
                    }
                ]
            },
            pdf_path=None,
            generated_at=datetime.now(timezone.utc),
        )

    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_report_returns_persisted_string_facts_unchanged(
    sample_unified_report,
    sample_remedy_generation,
):
    builder = ProfessionalReportBuilder()
    report_input = ProfessionalReportInput(
        unified_report=sample_unified_report,
        remedy_generation=sample_remedy_generation,
        language=ReportLanguage.HINDI,
    )
    client_report = professional_report_to_client_json(builder.build(report_input), report_input=report_input)

    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    stored_report = MagicMock()
    stored_report.id = uuid.uuid4()
    stored_report.client_id = None
    stored_report.birth_detail_id = None
    stored_report.version = "unified_report_v2"
    stored_report.problem_text = None
    stored_report.unified_report_json = sample_unified_report
    stored_report.interpretation_json = {}
    stored_report.remedy_json = {}
    stored_report.client_report_json = client_report
    stored_report.pdf_path = None
    stored_report.generated_at = generated_at
    stored_report.updated_at = generated_at

    repository = AsyncMock()
    repository.get_report = AsyncMock(return_value=stored_report)

    with patch("backend.app.services.report_service.ReportOrchestrator"), \
         patch("backend.app.services.report_service.AstroInterpretationEngine"), \
         patch("backend.app.services.report_service.RemedyGenerationEngine"), \
         patch("backend.app.services.report_service.ProfessionalReportBuilder"), \
         patch("backend.app.services.report_service.PDFReportGenerator"), \
         patch("backend.app.services.report_service.ConsultationEngine"):
        service = ReportService(repository=repository)

    detail = await service.get_report(stored_report.id)
    for section in detail["client_report"]["sections"]:
        assert isinstance(section["facts"], list)
        assert all(isinstance(line, str) for line in section["facts"])
