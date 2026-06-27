"""Report orchestrator unit tests."""

from __future__ import annotations

import json
from datetime import date, datetime, time, timezone

import pytest

from astrology_engine.core.types import Ascendant, HouseCusp, LagnaKundali, NakshatraInfo, PlanetPosition, ZodiacSign
from reports.builders import build_dasha_input_from_chart
from reports.charts.serializer import kundali_to_json_dict, navamsha_to_json_dict
from reports.serializer import to_json_dict
from reports.types import ReportSummary, UnifiedReportResult


def _sign(index: int, degree: float = 10.0) -> ZodiacSign:
    names_en = (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    )
    names_sa = (
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
    )
    lords = (
        "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
        "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
    )
    return ZodiacSign(
        index=index,
        name_en=names_en[index],
        name_sa=names_sa[index],
        lord=lords[index],
        degree_in_sign=degree,
    )


def _nakshatra(index: int = 0, name: str = "Ashwini") -> NakshatraInfo:
    return NakshatraInfo(index=index, name=name, lord="Ketu", pada=1)


def _planet(name: str, sign_index: int, house: int, longitude: float | None = None) -> PlanetPosition:
    lon = longitude if longitude is not None else sign_index * 30.0 + 10.0
    return PlanetPosition(
        name=name,
        longitude=lon,
        latitude=0.0,
        speed=1.0,
        is_retrograde=False,
        sign=_sign(sign_index),
        nakshatra=_nakshatra(sign_index % 3),
        house=house,
    )


def _sample_metadata():
    from astrology_engine.core.types import ChartMetadata

    return ChartMetadata(
        julian_day=2447892.7083333335,
        ayanamsa="lahiri",
        house_system="whole_sign",
        latitude=28.6139,
        longitude=77.2090,
        datetime_utc=datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc),
    )


def _sample_lagna() -> LagnaKundali:
    asc = Ascendant(longitude=5.0, sign=_sign(0), nakshatra=_nakshatra(0))
    planets = (
        _planet("Sun", 4, 5),
        _planet("Moon", 0, 1, longitude=0.5),
        _planet("Mars", 7, 8),
        _planet("Mercury", 2, 3),
        _planet("Jupiter", 8, 9),
        _planet("Venus", 1, 2),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    )
    houses = tuple(
        HouseCusp(number=i, longitude=((i - 1) % 12) * 30.0, sign=_sign((i - 1) % 12))
        for i in range(1, 13)
    )
    return LagnaKundali(ascendant=asc, planets=planets, houses=houses)


def test_kundali_json_serializer_structure():
    metadata = _sample_metadata()
    payload = kundali_to_json_dict(_sample_lagna(), metadata)

    assert payload["chart_type"] == "d1_lagna"
    assert payload["ascendant"]["sign"]["name_en"] == "Aries"
    assert len(payload["planets"]) == 9
    assert payload["planets"][0]["nakshatra"]["pada"] == 1
    assert payload["metadata"]["ayanamsa"] == "lahiri"


def test_navamsha_json_serializer_structure():
    metadata = _sample_metadata()
    payload = navamsha_to_json_dict(_sample_lagna(), metadata)

    assert payload["chart_type"] == "d9_navamsha"
    assert payload["ascendant"]["sign"]["name_en"] == "Aries"


def test_build_dasha_input_from_synthetic_bundle():
    from astrology_engine.core.types import BhavaChart, NavamshaChart, VedicChartBundle

    lagna = _sample_lagna()
    metadata = _sample_metadata()
    bundle = VedicChartBundle(
        metadata=metadata,
        planetary_positions=lagna.planets,
        lagna_kundali=lagna,
        bhava_chart=BhavaChart(
            ascendant=lagna.ascendant,
            house_cusps=lagna.houses,
            planets=lagna.planets,
            planets_by_house={1: ("Moon",)},
        ),
        navamsha_chart=NavamshaChart(
            ascendant=lagna.ascendant,
            planets=lagna.planets,
            houses=lagna.houses,
        ),
    )

    dasha_input = build_dasha_input_from_chart(
        bundle,
        birth_place="New Delhi, India",
        timezone="UTC",
    )

    assert dasha_input.birth_place == "New Delhi, India"
    assert dasha_input.moon_nakshatra == "Ashwini"
    assert dasha_input.moon_longitude == 0.5


def test_unified_report_json_contract():
    generated_at = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
    result = UnifiedReportResult(
        generated_at=generated_at,
        subject={"birth_place": "Delhi", "timezone": "Asia/Kolkata"},
        kundali={"chart_type": "d1_lagna", "ascendant": {"sign": {"name_en": "Aries"}}, "planets": []},
        navamsha={"chart_type": "d9_navamsha"},
        dasha={"system": "vimshottari", "moon": {"nakshatra": "Ashwini"}, "current": {}, "summary": {}},
        yogas={"summary": {"present_count": 2}},
        doshas={"summary": {"present_count": 1, "highest_severity": "moderate"}},
        transits={"metadata": {"engine": "transit_engine_v1"}},
        problem_analysis={"category": {"category": "marriage"}, "severity": {"level": "high"}},
        lal_kitab={"summary": {"present_count": 1, "rin_count": 1, "dosh_count": 0}},
        kp_analysis={"summary": {"supported_events": 2, "total_events": 5}},
        astro_intelligence={
            "severity_score": 0.6,
            "confidence_score": 0.7,
            "recommended_remedies": [{"remedy_id": "vedic_mars_hanuman_worship"}],
        },
        remedy_recommendations={"matched_remedies": [], "metadata": {"engine": "remedy_engine_v1"}},
        vedic={"metadata": {"engine": "vedic_intelligence_v1"}, "observations": []},
        kp={"metadata": {"engine": "kp_intelligence_v1"}, "observations": [], "event_timing": []},
        lal_kitab_intelligence={"metadata": {"engine": "lal_kitab_intelligence_v1"}, "observations": [], "remedies": []},
        fusion={
            "analyzed_at": generated_at.isoformat(),
            "confidence": 0.72,
            "root_causes": [],
            "conflicts": [],
            "recommendations": [],
            "observations": [],
            "metadata": {"engine": "intelligence_fusion_v1"},
        },
        summary=ReportSummary(
            lagna_sign="Aries",
            moon_sign="Aries",
            moon_nakshatra="Ashwini",
            present_yogas_count=2,
            present_doshas_count=1,
            highest_dosha_severity="moderate",
            current_mahadasha="Ketu",
            current_antardasha="Venus",
            problem_category="marriage",
            problem_severity="high",
            lal_kitab_findings_count=1,
            kp_supported_events=2,
            intelligence_severity_score=0.6,
            recommended_remedies_count=1,
            reasoning_confidence_score=72,
        ),
        metadata={"orchestrator": "report_orchestrator_v2", "ai_interpretation": False},
    )

    payload = to_json_dict(result)

    assert payload["version"] == "unified_report_v2"
    assert payload["kundali"]["chart_type"] == "d1_lagna"
    assert payload["summary"]["present_yogas_count"] == 2
    assert payload["metadata"]["ai_interpretation"] is False
    assert json.loads(json.dumps(payload))["problem_analysis"]["severity"]["level"] == "high"


@pytest.fixture
def sample_birth_data():
    from astrology_engine import BirthData

    return BirthData(
        datetime_utc=datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )


@pytest.fixture
def orchestrator():
    pytest.importorskip("swisseph")
    from reports import ReportOrchestrator

    return ReportOrchestrator()


def test_report_orchestrator_generates_all_sections(orchestrator, sample_birth_data):
    from reports import ReportInput

    payload = orchestrator.generate_json(
        ReportInput(
            birth_data=sample_birth_data,
            birth_place="New Delhi, India",
            problem_text="I am facing delay in marriage.",
            client_id="client-1",
            target_date=date(2024, 6, 15),
        )
    )

    assert payload["version"] == "unified_report_v2"
    assert payload["kundali"]["chart_type"] == "d1_lagna"
    assert payload["navamsha"]["chart_type"] == "d9_navamsha"
    assert payload["dasha"]["system"] == "vimshottari"
    assert "yogas" in payload and "summary" in payload["yogas"]
    assert "doshas" in payload and payload["metadata"]["ai_interpretation"] is False
    assert payload["transits"]["metadata"]["planets_analyzed"] == ["Saturn", "Jupiter", "Rahu", "Ketu"]
    assert payload["lal_kitab"]["summary"]
    assert payload["kp_analysis"]["summary"]
    assert payload["astro_intelligence"]["severity_score"] >= 0
    assert payload["vedic"]["metadata"]["engine"] == "vedic_intelligence_v1"
    assert payload["kp"]["metadata"]["engine"] == "kp_intelligence_v1"
    assert payload["lal_kitab_intelligence"]["metadata"]["engine"] == "lal_kitab_intelligence_v1"
    assert payload["fusion"]["metadata"]["engine"] == "intelligence_fusion_v1"
    assert 0.0 <= payload["fusion"]["confidence"] <= 1.0
    assert isinstance(payload["fusion"]["root_causes"], list)
    assert isinstance(payload["fusion"]["conflicts"], list)
    assert isinstance(payload["fusion"]["recommendations"], list)
    assert payload["summary"]["reasoning_confidence_score"] is not None
    assert payload["remedy_recommendations"]["metadata"]["engine"] == "remedy_engine_v1"
    assert payload["problem_analysis"]["category"]["category"] == "marriage"
    assert payload["summary"]["lagna_sign"]
    assert payload["summary"]["problem_category"] == "marriage"
    assert "lal_kitab" in payload["metadata"]["components"]
    assert "astro_intelligence" in payload["metadata"]["components"]
    assert "vedic" in payload["metadata"]["components"]
    assert "fusion" in payload["metadata"]["components"]
    assert "problem_analysis" in payload["metadata"]["components"]


def test_report_orchestrator_without_problem_text(orchestrator, sample_birth_data):
    from reports import ReportInput

    payload = orchestrator.generate_json(
        ReportInput(
            birth_data=sample_birth_data,
            birth_place="New Delhi, India",
            include_problem_analysis=False,
        )
    )

    assert payload["problem_analysis"] is None
    assert "problem_analysis" not in payload["metadata"]["components"]
