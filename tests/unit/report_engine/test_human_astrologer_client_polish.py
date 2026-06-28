"""Tests for full client report human delivery polish."""

from __future__ import annotations

import json

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput
from backend.app.services.report_engine.human_astrologer_client_polish import (
    polish_client_report_for_human_delivery,
)
from backend.app.services.report_engine.master_consultation_delivery import build_delivered_client_report
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage


def test_polish_removes_confidence_and_technical_legacy_fields(
    sample_unified_report,
    sample_remedy_generation,
):
    payload = build_delivered_client_report(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    brain = ConsultationBrain().run(
        ConsultationInput(
            unified_report=sample_unified_report,
            problem_text="Marriage delay",
            language="hi",
        )
    )
    polish_client_report_for_human_delivery(payload, brain, problem_text="Marriage delay")

    serialized = json.dumps(payload, ensure_ascii=False).lower()
    assert "confidence" not in serialized
    assert "supported=" not in serialized
    assert "house 7" not in serialized
    assert "kp analysis" not in serialized
    assert "cuspal" not in serialized
    for section in payload["sections"]:
        assert "confidence" not in section
        assert "confidence_label" not in section


def test_polish_maps_legacy_fields_to_human_consultation_sections(
    sample_unified_report,
    sample_remedy_generation,
):
    payload = build_delivered_client_report(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    brain = ConsultationBrain().run(
        ConsultationInput(
            unified_report=sample_unified_report,
            problem_text="Marriage delay",
            language="hi",
        )
    )
    polish_client_report_for_human_delivery(payload, brain, problem_text="Marriage delay")

    assert payload["problem_summary"] == "Marriage delay"
    assert payload["astrological_root_cause"]
    assert payload["dasha_analysis"]
    assert "KP" not in payload["kp_analysis"]
    assert "Lal Kitab" not in payload["lal_kitab_analysis"]
    assert payload["language"] == "hi"
