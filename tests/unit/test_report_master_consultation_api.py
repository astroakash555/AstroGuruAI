"""Tests for master consultation exposure in report API payloads."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from backend.app.models.report import Report
from backend.app.services.report_service import ReportService


@pytest.fixture
def sample_master_consultation_payload() -> dict:
    return {
        "language": "hi",
        "sections": [
            {
                "section_id": "greeting",
                "title": "अभिवादन",
                "paragraphs": ["नमस्ते। आपका स्वागत है।"],
                "body": "नमस्ते। आपका स्वागत है।",
            }
        ],
    }


def test_report_to_detail_exposes_master_consultation(sample_master_consultation_payload):
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    report = Report(
        id=uuid.uuid4(),
        client_id=None,
        birth_detail_id=None,
        version="unified_report_v2",
        problem_text="Marriage delay",
        unified_report_json={"summary": {"lagna_sign": "Aries"}},
        interpretation_json={},
        remedy_json={},
        client_report_json={"master_consultation": sample_master_consultation_payload},
        pdf_path=None,
        generated_at=generated_at,
        updated_at=generated_at,
    )

    with patch(
        "backend.app.services.report_service.resolve_master_consultation_payload",
        return_value=sample_master_consultation_payload,
    ):
        payload = ReportService._report_to_detail(report)

    assert payload["master_consultation"] == sample_master_consultation_payload
    assert payload["master_consultation"]["sections"][0]["title"] == "अभिवादन"
