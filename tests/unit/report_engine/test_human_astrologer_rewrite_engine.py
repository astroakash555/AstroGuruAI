"""Tests for the human astrologer rewrite delivery engine."""

from __future__ import annotations

import json

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput
from backend.app.services.report_engine.human_astrologer_rewrite_engine import HumanAstrologerRewriteEngine
from backend.app.services.report_engine.human_astrologer_rewrite_models import (
    DELIVERY_MODE,
    HUMAN_ASTROLOGER_SECTION_ORDER,
)
from backend.app.services.report_engine.master_consultation_delivery import build_delivered_client_report
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage


def _run_brain(unified_report: dict, *, problem_text: str | None = None):
    return ConsultationBrain().run(
        ConsultationInput(
            unified_report=unified_report,
            professional_report=None,
            problem_text=problem_text,
            language="hi",
        )
    )


def test_rewrite_produces_ten_hindi_sections(sample_unified_report):
    brain = _run_brain(sample_unified_report, problem_text="Marriage delay")
    payload = HumanAstrologerRewriteEngine().rewrite_to_client_dict(
        brain,
        problem_text="Marriage delay",
        language="hi",
    )
    assert payload["language"] == "hi"
    assert payload["delivery_mode"] == DELIVERY_MODE
    assert len(payload["sections"]) == len(HUMAN_ASTROLOGER_SECTION_ORDER)
    assert payload["sections"][0]["title"] == "अभिवादन"
    assert payload["sections"][-1]["title"] == "अंतिम संदेश"


def test_rewrite_answers_client_question_directly(sample_unified_report):
    brain = _run_brain(sample_unified_report, problem_text="Marriage delay")
    payload = HumanAstrologerRewriteEngine().rewrite_to_client_dict(
        brain,
        problem_text="Marriage delay",
    )
    greeting = payload["sections"][0]["body"]
    assert "Marriage delay" in greeting
    assert "सबसे पहले" in greeting or "आपने" in greeting


def test_rewrite_removes_technical_terms(sample_unified_report):
    brain = _run_brain(sample_unified_report, problem_text="Marriage delay")
    payload = HumanAstrologerRewriteEngine().rewrite_to_client_dict(
        brain,
        problem_text="Marriage delay",
    )
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    forbidden = (
        "supported=",
        "house 7",
        "house 8",
        "cuspal",
        "confidence 0.",
        "category=",
        "fusion",
        "executive summary",
        "timeline:",
        "root cause:",
    )
    for token in forbidden:
        assert token not in serialized, token


def test_rewrite_sections_are_paragraphs_not_bullets(sample_unified_report):
    brain = _run_brain(sample_unified_report, problem_text="Marriage delay")
    payload = HumanAstrologerRewriteEngine().rewrite_to_client_dict(
        brain,
        problem_text="Marriage delay",
    )
    for section in payload["sections"]:
        assert section["body"]
        assert isinstance(section["paragraphs"], list)
        assert all(isinstance(paragraph, str) for paragraph in section["paragraphs"])


def test_delivered_client_report_uses_human_astrologer_rewrite(
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
    assert payload["master_consultation"]["delivery_mode"] == DELIVERY_MODE
    assert len(payload["master_consultation"]["sections"]) == 10
