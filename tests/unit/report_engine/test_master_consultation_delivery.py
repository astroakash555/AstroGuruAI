"""Tests for master consultation delivery overlay."""

from __future__ import annotations

import json
import re

import pytest

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput, MasterConsultationEngine
from backend.app.services.report_engine.master_consultation_delivery import (
    DELIVERY_MODE,
    MasterSourceSpec,
    apply_master_consultation_delivery,
    attach_master_consultation_to_client_report,
    build_delivered_client_report,
    deliverable_narrative,
    resolve_master_consultation_payload,
    scrub_deliverable_text,
    serialize_master_consultation_for_client,
)
from backend.app.services.consultation_brain.master_consultation_models import (
    MASTER_CONSULTATION_SECTION_ORDER,
    MasterConsultationSectionId,
)
from backend.app.services.report_engine.presentation import assert_client_safe_text
from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage

FORBIDDEN_CLIENT_PATTERNS = (
    r"supported\s*=",
    r"category=",
    r"reason=",
    r"Raj Yoga",
    r"House \d+",
    r"Venus Combust",
    r"professional_report_engine",
    r"evidence_id",
)


def _brain_and_master(unified_report: dict, *, problem_text: str | None = None):
    brain_output = ConsultationBrain().run(
        ConsultationInput(
            unified_report=unified_report,
            professional_report=None,
            problem_text=problem_text,
            language="hi",
        )
    )
    master = MasterConsultationEngine().generate(
        brain_output,
        None,
        unified_report,
        language="hi",
        problem_text=problem_text,
    )
    return brain_output, master


def test_apply_master_consultation_delivery_replaces_narratives(
    sample_unified_report,
    sample_remedy_generation,
):
    brain_output, master = _brain_and_master(sample_unified_report, problem_text="Marriage delay")
    report_input = ProfessionalReportInput(
        unified_report=sample_unified_report,
        remedy_generation=sample_remedy_generation,
        problem_text="Marriage delay",
        language=ReportLanguage.HINDI,
        consultation_brain_output=brain_output,
        master_consultation=master,
    )
    builder = ProfessionalReportBuilder()
    raw_result = builder.build(report_input)
    delivered = apply_master_consultation_delivery(raw_result, master, report_input=report_input)

    assert delivered.delivery_metadata["delivery_mode"] == DELIVERY_MODE
    assert delivered.delivery_metadata["technical_facts"]["birth_details"] == raw_result.sections[0].facts
    assert delivered.sections[0].narrative != raw_result.sections[0].narrative
    assert master.sections[0].body_text[:20] in delivered.sections[0].narrative


def test_build_delivered_client_report_is_client_safe(
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
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    for pattern in FORBIDDEN_CLIENT_PATTERNS:
        assert re.search(pattern, serialized, re.IGNORECASE) is None, pattern
    assert_client_safe_text(serialized)
    assert payload["metadata"]["delivery_mode"] == DELIVERY_MODE
    assert payload["master_consultation"]["delivery_mode"] == "human_astrologer_rewrite_v1"
    assert len(payload["sections"]) == 14
    titles = [item["title"] for item in payload["remedies"]]
    assert len(titles) == len(set(titles))


def test_delivered_sections_use_summary_bullets_not_technical_facts(
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
    for section in payload["sections"]:
        assert isinstance(section["facts"], list)
        assert all(isinstance(line, str) for line in section["facts"])
        for line in section["facts"]:
            assert "supported=" not in line.lower()


def test_scrub_deliverable_text_removes_confidence_markers():
    cleaned = scrub_deliverable_text("यह मार्गदर्शन स्पष्ट है (विश्वास 82%)।")
    assert "विश्वास" not in cleaned
    assert cleaned.endswith("।") or cleaned.endswith(".")


def test_deliverable_narrative_deduplicates_repeated_blocks():
    _, master = _brain_and_master({"version": "unified_report_v2", "summary": {}})
    text = deliverable_narrative(
        master,
        (
            MasterSourceSpec(MasterConsultationSectionId.GREETING),
            MasterSourceSpec(MasterConsultationSectionId.GREETING),
        ),
    )
    assert text.count("\n\n") == 0


def test_serialize_master_consultation_for_client_returns_ten_hindi_sections(
    sample_unified_report,
):
    _, master = _brain_and_master(sample_unified_report, problem_text="Marriage delay")
    payload = serialize_master_consultation_for_client(master, language="hi")
    assert payload["language"] == "hi"
    assert len(payload["sections"]) == len(MASTER_CONSULTATION_SECTION_ORDER)
    assert payload["sections"][0]["title"] == "अभिवादन"
    assert payload["sections"][1]["title"] == "आपकी समस्या को समझना"
    assert payload["sections"][-1]["title"] == "अंतिम संदेश"
    serialized = json.dumps(payload, ensure_ascii=False)
    assert "Executive Summary" not in serialized
    assert "supported=" not in serialized.lower()
    assert "planets:" not in serialized.lower()
    assert "confidence 0." not in serialized.lower()
    for section in payload["sections"]:
        assert section["body"]
        assert section["paragraphs"]


def test_build_delivered_client_report_includes_master_consultation(
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
    master = payload["master_consultation"]
    assert master["language"] == "hi"
    assert len(master["sections"]) == 10


def test_resolve_master_consultation_payload_uses_stored_payload(
    sample_unified_report,
    sample_remedy_generation,
):
    delivered = build_delivered_client_report(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    resolved = resolve_master_consultation_payload(
        unified_report=sample_unified_report,
        client_report=delivered,
        problem_text="Marriage delay",
        language="hi",
    )
    assert resolved == delivered["master_consultation"]
