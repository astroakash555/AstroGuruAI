"""Integration tests for Consultation Brain in the Professional Report Engine."""

from __future__ import annotations

import json
import re

import pytest

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput
from backend.app.services.report_engine.consultation_brain_integration import build_brain_context
from backend.app.services.report_engine.presentation import assert_client_safe_text
from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.master_consultation_delivery import build_delivered_client_report
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage

FORBIDDEN_INTERNAL_PATTERNS = (
    r"category=[\w_]+\|domain=",
    r"evidence_id",
    r"legacy_conflicts",
    r"MappingProxyType",
    r"\[object Object\]",
)


def _run_consultation_brain(unified_report: dict, *, problem_text: str | None = None):
    return ConsultationBrain().run(
        ConsultationInput(
            unified_report=unified_report,
            professional_report=None,
            problem_text=problem_text,
            language="hi",
        )
    )


def test_professional_report_builder_consumes_consultation_brain_output(
    sample_unified_report,
    sample_remedy_generation,
):
    brain_output = _run_consultation_brain(sample_unified_report, problem_text="Marriage delay")
    result = ProfessionalReportBuilder().build(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
            consultation_brain_output=brain_output,
        )
    )
    assert len(result.sections) == 14
    assert result.overall_confidence == brain_output.overall_confidence


def test_client_report_contains_narrative_and_priorities(
    sample_unified_report,
    sample_remedy_generation,
):
    brain_output = _run_consultation_brain(sample_unified_report, problem_text="Marriage delay")
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
            consultation_brain_output=brain_output,
        )
    )
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    assert brain_output.narrative is not None
    greeting = brain_output.narrative.sections[0].paragraphs[0]
    assert greeting[:20] in serialized or "नमस्ते" in serialized
    assert payload["problem_summary"] == "Marriage delay"
    assert payload["planet_analysis"]
    assert payload["dasha_analysis"]
    assert payload["remedies"]


def test_recommendations_and_conflicts_are_visible_in_report(
    sample_unified_report,
    sample_remedy_generation,
):
    brain_output = _run_consultation_brain(sample_unified_report, problem_text="Marriage delay")
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
            consultation_brain_output=brain_output,
        )
    )
    problem_section = next(item for item in payload["sections"] if item["section_id"] == "problem_analysis")
    remedy_section = next(item for item in payload["sections"] if item["section_id"] == "personalized_remedies")
    assert problem_section["narrative"]
    assert remedy_section["narrative"]
    if brain_output.priorities:
        assert any(priority.domain in problem_section["narrative"] for priority in brain_output.priorities) or problem_section["facts"]


def test_no_raw_internal_structures_leak_into_client_report(
    sample_unified_report,
    sample_remedy_generation,
):
    brain_output = _run_consultation_brain(sample_unified_report, problem_text="Marriage delay")
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
            consultation_brain_output=brain_output,
        )
    )
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    for pattern in FORBIDDEN_INTERNAL_PATTERNS:
        assert re.search(pattern, serialized, re.IGNORECASE) is None, pattern
    assert_client_safe_text(serialized)
    for section in payload["sections"]:
        assert isinstance(section["facts"], list)
        assert all(isinstance(line, str) for line in section["facts"])


def test_brain_context_maps_recommendations_without_structured_reasons(
    sample_unified_report,
):
    brain_output = _run_consultation_brain(sample_unified_report, problem_text="Marriage delay")
    context = build_brain_context(brain_output, language=ReportLanguage.HINDI)
    assert context is not None
    remedies = context.legacy_remedies()
    recommendations = context.recommendation_fact_lines()
    assert remedies or recommendations
    for line in recommendations:
        assert "category=" not in line


def test_master_consultation_delivery_replaces_legacy_client_narrative(
    sample_unified_report,
    sample_remedy_generation,
):
    legacy_payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
            consultation_brain_output=_run_consultation_brain(sample_unified_report, problem_text="Marriage delay"),
        )
    )
    delivered_payload = build_delivered_client_report(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    assert delivered_payload["metadata"]["delivery_mode"] == "master_consultation_v1"
    assert delivered_payload["master_consultation"]["delivery_mode"] == "human_astrologer_rewrite_v1"
    assert delivered_payload["sections"][0]["narrative"] != legacy_payload["sections"][0]["narrative"]
    serialized = json.dumps(delivered_payload, ensure_ascii=False, default=str)
    assert "supported=" not in serialized.lower()
    assert "Raj Yoga" not in serialized
