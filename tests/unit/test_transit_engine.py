"""Transit engine unit tests."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from astrology_engine import BirthData, VedicAstrologyEngine

from astrology_engine.core.types import NakshatraInfo, ZodiacSign
from astrology_engine.transits.analyzer import (
    analyze_natal_impacts,
    build_planet_analysis,
    detect_sign_changes,
)
from astrology_engine.transits.serializer import to_json_dict, to_json_string
from astrology_engine.transits.types import (
    DailyTransitResult,
    MonthlyTransitResult,
    TransitAnalysisResult,
    TransitInput,
    TransitPlanetAnalysis,
    TransitPlanetSnapshot,
    YearlyTransitResult,
)


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


def _nakshatra(index: int = 0) -> NakshatraInfo:
    return NakshatraInfo(index=index, name="Ashwini", lord="Ketu", pada=1)


def _snapshot(
    planet: str,
    *,
    sign_index: int,
    house_from_lagna: int,
    house_from_moon: int,
    when: datetime | None = None,
    retrograde: bool = False,
) -> TransitPlanetSnapshot:
    return TransitPlanetSnapshot(
        planet=planet,
        datetime=when or datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc),
        longitude=sign_index * 30.0 + 10.0,
        sign=_sign(sign_index),
        house_from_lagna=house_from_lagna,
        house_from_moon=house_from_moon,
        is_retrograde=retrograde,
        nakshatra=_nakshatra(sign_index % 3),
        speed=-0.5 if retrograde else 0.5,
    )


def _transit_input(
    *,
    lagna: int = 0,
    moon: int = 1,
    natal_planets: dict[str, int] | None = None,
) -> TransitInput:
    planets = natal_planets or {
        "Sun": 4,
        "Moon": moon,
        "Mars": 7,
        "Mercury": 2,
        "Jupiter": 8,
        "Venus": 1,
        "Saturn": 9,
    }
    return TransitInput(
        natal_lagna_sign_index=lagna,
        natal_moon_sign_index=moon,
        natal_planets=planets,
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )


def test_detect_sign_changes_for_saturn():
    snapshots = (
        _snapshot(
            "Saturn",
            sign_index=9,
            house_from_lagna=10,
            house_from_moon=9,
            when=datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
        _snapshot(
            "Saturn",
            sign_index=10,
            house_from_lagna=11,
            house_from_moon=10,
            when=datetime(2024, 3, 29, tzinfo=timezone.utc),
        ),
    )

    events = detect_sign_changes(snapshots)

    assert len(events) == 1
    assert events[0].planet == "Saturn"
    assert events[0].from_sign == "Capricorn"
    assert events[0].to_sign == "Aquarius"


def test_sade_sati_impact_when_saturn_transits_twelfth_from_moon():
    transit_input = _transit_input(moon=1)
    snapshot = _snapshot(
        "Saturn",
        sign_index=0,
        house_from_lagna=1,
        house_from_moon=12,
    )

    impacts = analyze_natal_impacts(snapshot, transit_input)
    impact_types = {item.impact_type for item in impacts}

    assert "sade_sati_phase" in impact_types
    assert "kendra_transit" in impact_types


def test_kendra_and_dusthana_impacts():
    transit_input = _transit_input()
    kendra = _snapshot("Jupiter", sign_index=3, house_from_lagna=4, house_from_moon=3)
    dusthana = _snapshot("Rahu", sign_index=5, house_from_lagna=6, house_from_moon=5)

    kendra_types = {item.impact_type for item in analyze_natal_impacts(kendra, transit_input)}
    dusthana_types = {item.impact_type for item in analyze_natal_impacts(dusthana, transit_input)}

    assert "kendra_transit" in kendra_types
    assert "dusthana_transit" in dusthana_types


def test_build_planet_analysis_includes_theme_and_highlights():
    transit_input = _transit_input()
    snapshots = (
        _snapshot("Jupiter", sign_index=8, house_from_lagna=9, house_from_moon=8),
    )

    analysis = build_planet_analysis("Jupiter", snapshots, transit_input)

    assert analysis.planet == "Jupiter"
    assert analysis.theme == "growth_wisdom_opportunity"
    assert analysis.current is not None
    assert analysis.highlights
    assert "Jupiter in Sagittarius" in analysis.highlights[0]


def test_json_serialization_structure():
    snapshot = _snapshot("Saturn", sign_index=9, house_from_lagna=10, house_from_moon=9)
    analysis = TransitPlanetAnalysis(
        planet="Saturn",
        theme="discipline_karma_obstacles",
        current=snapshot,
        sign_changes=tuple(),
        natal_impacts=tuple(),
        highlights=("Saturn in Capricorn.",),
    )
    daily = DailyTransitResult(
        date=date(2024, 6, 15),
        snapshots=(snapshot,),
        analyses=(analysis,),
    )
    result = TransitAnalysisResult(
        computed_at=datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc),
        natal_lagna_sign="Aries",
        natal_moon_sign="Taurus",
        daily=daily,
        monthly=None,
        yearly=None,
        saturn=analysis,
        jupiter=analysis,
        rahu=analysis,
        ketu=analysis,
        metadata={"engine": "transit_engine_v1"},
    )

    payload = to_json_dict(result)
    text = to_json_string(result)

    assert payload["natal_lagna_sign"] == "Aries"
    assert payload["daily"]["date"] == "2024-06-15"
    assert payload["saturn"]["theme"] == "discipline_karma_obstacles"
    assert "jupiter" in payload
    assert "rahu" in payload
    assert "ketu" in payload
    assert json.loads(text)["metadata"]["engine"] == "transit_engine_v1"


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
def engine():
    pytest.importorskip("swisseph")
    from astrology_engine import VedicAstrologyEngine

    return VedicAstrologyEngine()


def test_transit_engine_daily_monthly_yearly(engine, sample_birth_data):
    bundle = engine.compute_chart(sample_birth_data)
    result = engine.analyze_transits(bundle, target_date=date(2024, 6, 15))

    assert result.daily is not None
    assert result.monthly is not None
    assert result.yearly is not None
    assert result.daily.date == date(2024, 6, 15)
    assert result.monthly.year == 2024 and result.monthly.month == 6
    assert result.yearly.year == 2024


def test_transit_engine_analyzes_slow_movers(engine, sample_birth_data):
    bundle = engine.compute_chart(sample_birth_data)
    result = engine.analyze_transits(bundle, target_date=date(2024, 6, 15))

    for planet in (result.saturn, result.jupiter, result.rahu, result.ketu):
        assert planet.current is not None
        assert planet.theme
        assert planet.highlights


def test_transit_engine_json_output(engine, sample_birth_data):
    from astrology_engine.transits import TransitEngine, to_json_dict

    bundle = engine.compute_chart(sample_birth_data)
    transit_engine = TransitEngine()
    payload = to_json_dict(transit_engine.analyze_chart(bundle, target_date=date(2024, 6, 15)))

    assert payload["daily"] is not None
    assert payload["monthly"] is not None
    assert payload["yearly"] is not None
    for key in ("saturn", "jupiter", "rahu", "ketu"):
        assert payload[key]["current"] is not None
        assert payload[key]["planet"] == key.capitalize() if key != "rahu" else "Rahu"
    assert payload["metadata"]["planets_analyzed"] == ["Saturn", "Jupiter", "Rahu", "Ketu"]
