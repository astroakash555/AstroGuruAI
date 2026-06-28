"""Section builder tests for the professional report engine."""

from __future__ import annotations

import pytest

from backend.app.services.report_engine.birth_details import build_birth_details_section
from backend.app.services.report_engine.dasha_analysis import build_dasha_section
from backend.app.services.report_engine.house_analysis import build_house_wise_section
from backend.app.services.report_engine.moon_analysis import build_ascendant_section, build_moon_section
from backend.app.services.report_engine.planet_analysis import (
    build_planet_wise_section,
    build_planetary_positions_section,
)
from backend.app.services.report_engine.problem_analysis import build_problem_section
from backend.app.services.report_engine.remedy_analysis import build_remedy_section
from backend.app.services.report_engine.summary import (
    build_challenges_section,
    build_final_summary_section,
    build_strengths_section,
)
from backend.app.services.report_engine.transit_analysis import build_transit_section
from backend.app.services.report_engine.types import ReportLanguage
from backend.app.services.report_engine.yoga_analysis import build_yoga_section


@pytest.mark.parametrize(
    ("builder", "section_id", "extra_kwargs"),
    [
        (build_birth_details_section, "birth_details", {"problem_text": "Marriage delay"}),
        (build_planetary_positions_section, "planetary_positions", {}),
        (build_ascendant_section, "ascendant_analysis", {}),
        (build_moon_section, "moon_analysis", {}),
        (build_planet_wise_section, "planet_wise_interpretation", {}),
        (build_house_wise_section, "house_wise_interpretation", {}),
        (build_yoga_section, "yoga_analysis", {}),
        (build_dasha_section, "current_dasha", {}),
        (build_transit_section, "transit_analysis", {}),
        (build_problem_section, "problem_analysis", {"problem_text": "Marriage delay"}),
        (build_remedy_section, "personalized_remedies", {"remedy_generation": {"remedies": []}}),
        (build_strengths_section, "strengths", {}),
        (build_challenges_section, "challenges", {}),
        (build_final_summary_section, "final_summary", {}),
    ],
)
def test_section_builders_return_confident_sections(
    sample_unified_report,
    builder,
    section_id,
    extra_kwargs,
):
    section = builder(sample_unified_report, language=ReportLanguage.HINDI, **extra_kwargs)
    assert section.section_id == section_id
    assert section.title
    assert section.narrative
    assert section.facts
    assert 0.0 <= section.confidence <= 1.0


def test_yoga_section_handles_empty_yogas():
    section = build_yoga_section({"yogas": {"present_yogas": []}}, language=ReportLanguage.ENGLISH)
    assert section.section_id == "yoga_analysis"
    assert "No active yogas" in section.narrative
