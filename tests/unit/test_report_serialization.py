"""Tests for unified report severity normalization and JSON serialization."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from reports.serializer import to_json_dict
from reports.types import ReportSummary, UnifiedReportResult
from reports.utilities import normalize_highest_dosha_severity


def _minimal_report(summary: ReportSummary) -> UnifiedReportResult:
    return UnifiedReportResult(
        generated_at=datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc),
        subject={"birth_place": "Delhi"},
        kundali={"chart_type": "d1_lagna", "ascendant": {"sign": {"name_en": "Aries"}}, "planets": []},
        navamsha={"chart_type": "d9_navamsha"},
        dasha={"system": "vimshottari", "moon": {"nakshatra": "Ashwini"}, "current": {}, "summary": {}},
        yogas={"summary": {"present_count": 0}},
        doshas={"summary": {"present_count": 0}},
        transits={"metadata": {"engine": "transit_engine_v1"}},
        problem_analysis=None,
        lal_kitab={"summary": {"present_count": 0}},
        kp_analysis={"summary": {"supported_events": 0}},
        astro_intelligence={"severity_score": 0.0, "recommended_remedies": []},
        remedy_recommendations={"matched_remedies": []},
        vedic={"metadata": {"engine": "vedic_intelligence_v1"}, "observations": []},
        kp={"metadata": {"engine": "kp_intelligence_v1"}, "observations": [], "event_timing": []},
        lal_kitab_intelligence={"metadata": {"engine": "lal_kitab_intelligence_v1"}, "observations": [], "remedies": []},
        fusion={
            "analyzed_at": datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc).isoformat(),
            "confidence": 0.5,
            "root_causes": [],
            "conflicts": [],
            "recommendations": [],
            "observations": [],
            "metadata": {"engine": "intelligence_fusion_v1"},
        },
        summary=summary,
        metadata={"orchestrator": "report_orchestrator_v2"},
    )


def _base_summary(**overrides) -> ReportSummary:
    defaults = {
        "lagna_sign": "Aries",
        "moon_sign": "Aries",
        "moon_nakshatra": "Ashwini",
        "present_yogas_count": 0,
        "present_doshas_count": 0,
        "highest_dosha_severity": None,
        "current_mahadasha": None,
        "current_antardasha": None,
        "problem_category": None,
        "problem_severity": None,
    }
    defaults.update(overrides)
    return ReportSummary(**defaults)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.8, "high"),
        ("moderate", "moderate"),
        (None, None),
        ("", None),
        (0.0, "minimal"),
        (0.3, "low"),
        (0.5, "moderate"),
        (0.7, "high"),
        (0.85, "critical"),
        (1.0, "critical"),
    ],
)
def test_normalize_highest_dosha_severity(value, expected):
    assert normalize_highest_dosha_severity(value) == expected


def test_unified_report_json_serializes_float_dosha_severity():
    summary = _base_summary(highest_dosha_severity=0.8)
    payload = to_json_dict(_minimal_report(summary))

    assert payload["summary"]["highest_dosha_severity"] == "high"


def test_unified_report_json_serializes_string_dosha_severity():
    summary = _base_summary(highest_dosha_severity="Moderate")
    payload = to_json_dict(_minimal_report(summary))

    assert payload["summary"]["highest_dosha_severity"] == "moderate"


def test_unified_report_json_serializes_missing_dosha_severity():
    summary = _base_summary(highest_dosha_severity=None)
    payload = to_json_dict(_minimal_report(summary))

    assert payload["summary"]["highest_dosha_severity"] is None


def test_unified_report_json_boundary_severity_values():
    for score, label in [
        (0.0, "minimal"),
        (0.299, "minimal"),
        (0.3, "low"),
        (0.499, "low"),
        (0.5, "moderate"),
        (0.699, "moderate"),
        (0.7, "high"),
        (0.849, "high"),
        (0.85, "critical"),
    ]:
        summary = _base_summary(highest_dosha_severity=score)
        payload = to_json_dict(_minimal_report(summary))
        assert payload["summary"]["highest_dosha_severity"] == label
