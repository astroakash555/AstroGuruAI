"""Snapshot tests for client-safe professional report rendering."""

from __future__ import annotations

import json
import re

import pytest

from backend.app.services.report_engine.presentation import FORBIDDEN_PATTERNS, assert_client_safe_text
from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage

FORBIDDEN_SNAPSHOT_PATTERNS = (
    r"\[object Object\]",
    r"supported\s*=",
    r"supported=true",
    r"supported=false",
    r"professional_report_engine",
    r'"observations"\s*:',
    r"'observations'\s*:",
    r"fusion_id",
    r"is_supported",
)


def _assert_no_forbidden_output(payload: dict) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    assert "[object Object]" not in serialized
    for pattern in FORBIDDEN_SNAPSHOT_PATTERNS:
        assert re.search(pattern, serialized, re.IGNORECASE) is None, pattern
    assert_client_safe_text(serialized)


def test_client_report_sections_are_display_safe(
    sample_unified_report,
    sample_remedy_generation,
):
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    _assert_no_forbidden_output(payload)
    assert len(payload["sections"]) == 14
    for section in payload["sections"]:
        assert isinstance(section["title"], str)
        assert isinstance(section["narrative"], str)
        assert isinstance(section["facts"], list)
        assert all(isinstance(line, str) for line in section["facts"])
        assert isinstance(section["confidence_label"], str)


def test_kp_and_lal_kitab_legacy_fields_are_readable(
    sample_unified_report,
    sample_remedy_generation,
):
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            problem_text="Marriage delay",
            language=ReportLanguage.HINDI,
        )
    )
    assert "supported=" not in payload["kp_analysis"].lower()
    assert "is_supported" not in payload["kp_analysis"]
    assert "Mars 8th House Dosh" in payload["lal_kitab_analysis"] or "लाल किताब" in payload["lal_kitab_analysis"]


def test_dasha_analysis_is_human_readable_hindi(
    sample_unified_report,
    sample_remedy_generation,
):
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            language=ReportLanguage.HINDI,
        )
    )
    dasha = payload["dasha_analysis"]
    assert "T00:00:00Z" not in dasha
    assert "महादशा" in dasha
    assert "Saturn" in dasha or "शनि" not in dasha  # lord names stay English in engine output


def test_planet_analysis_is_natural_hindi(
    sample_unified_report,
    sample_remedy_generation,
):
    payload = ProfessionalReportBuilder().build_json(
        ProfessionalReportInput(
            unified_report=sample_unified_report,
            remedy_generation=sample_remedy_generation,
            language=ReportLanguage.HINDI,
        )
    )
    planet = payload["planet_analysis"]
    assert "observations" not in planet
    assert "प्रमुख प्रभाव" in planet or "विशेष टिप्पणी" in planet


def test_forbidden_patterns_constant_covers_snapshot_rules():
    combined = "|".join(FORBIDDEN_PATTERNS)
    assert "supported" in combined
    assert "object Object" in combined
