"""Regression tests for client section facts normalization."""

from __future__ import annotations

import pytest

from backend.app.services.report_engine.presentation import normalize_client_facts
from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.serializers import section_to_client_dict
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage, ReportSection


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, []),
        ("", []),
        ("Single fact line", ["Single fact line"]),
        (["line one", "line two"], ["line one", "line two"]),
        ({"a": "first", "b": "second"}, ["first", "second"]),
        (123, ["123"]),
    ],
)
def test_normalize_client_facts_coerces_to_string_array(raw, expected):
    assert normalize_client_facts(raw) == expected


def test_section_to_client_dict_normalizes_non_array_facts():
    section = ReportSection(
        section_id="moon_analysis",
        title="Moon",
        narrative="Moon narrative",
        facts="Moon in Aries",  # type: ignore[arg-type]
        confidence=0.8,
    )
    payload = section_to_client_dict(section, language=ReportLanguage.HINDI)
    assert payload["facts"] == ["Moon in Aries"]


def test_section_to_client_dict_normalizes_null_facts():
    section = ReportSection(
        section_id="strengths",
        title="Strengths",
        narrative="Strong chart",
        facts=None,  # type: ignore[arg-type]
        confidence=0.7,
    )
    payload = section_to_client_dict(section, language=ReportLanguage.HINDI)
    assert payload["facts"] == []


def test_section_to_client_dict_normalizes_list_facts():
    section = ReportSection(
        section_id="transit_analysis",
        title="Transits",
        narrative="Transit narrative",
        facts=["Saturn in 10th house"],  # type: ignore[arg-type]
        confidence=0.75,
    )
    payload = section_to_client_dict(section, language=ReportLanguage.ENGLISH)
    assert payload["facts"] == ["Saturn in 10th house"]


def test_every_report_section_serializes_facts_as_string_array(
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
    assert len(payload["sections"]) == 14
    for section in payload["sections"]:
        facts = section["facts"]
        assert isinstance(facts, list), section["section_id"]
        assert all(isinstance(line, str) for line in facts), section["section_id"]
