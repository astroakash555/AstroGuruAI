"""KP engine unit tests."""

from __future__ import annotations

import json

from kp_engine.lords import get_star_lord, get_sub_lord
from kp_engine.significators.analyzer import analyze_significators
from kp_engine.event.framework import analyze_events
from kp_engine.cusps.calculator import analyze_cusps


def _sign(index: int):
    from astrology_engine.core.types import ZodiacSign

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
        degree_in_sign=10.0,
    )


def _planet(name: str, sign_index: int, house: int, longitude: float | None = None):
    from astrology_engine.core.types import NakshatraInfo, PlanetPosition

    lon = longitude if longitude is not None else sign_index * 30.0 + 10.0
    return PlanetPosition(
        name=name,
        longitude=lon,
        latitude=0.0,
        speed=1.0,
        is_retrograde=False,
        sign=_sign(sign_index),
        nakshatra=NakshatraInfo(index=0, name="Ashwini", lord="Ketu", pada=1),
        house=house,
    )


def _bundle():
    from astrology_engine.core.types import (
        Ascendant,
        BhavaChart,
        ChartMetadata,
        HouseCusp,
        LagnaKundali,
        NakshatraInfo,
        NavamshaChart,
        VedicChartBundle,
    )
    from datetime import datetime, timezone

    asc = Ascendant(
        longitude=5.0,
        sign=_sign(0),
        nakshatra=NakshatraInfo(index=0, name="Ashwini", lord="Ketu", pada=1),
    )
    planets = (
        _planet("Sun", 4, 5),
        _planet("Moon", 1, 2, longitude=40.0),
        _planet("Mars", 7, 8),
        _planet("Mercury", 2, 3),
        _planet("Jupiter", 8, 9),
        _planet("Venus", 1, 2, longitude=45.0),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    )
    houses = tuple(
        HouseCusp(number=i, longitude=((i - 1) % 12) * 30.0 + 5.0, sign=_sign((i - 1) % 12))
        for i in range(1, 13)
    )
    lagna = LagnaKundali(ascendant=asc, planets=planets, houses=houses)
    metadata = ChartMetadata(
        julian_day=2447892.0,
        ayanamsa="lahiri",
        house_system="whole_sign",
        latitude=28.6139,
        longitude=77.2090,
        datetime_utc=datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc),
    )
    return VedicChartBundle(
        metadata=metadata,
        planetary_positions=planets,
        lagna_kundali=lagna,
        bhava_chart=BhavaChart(
            ascendant=asc,
            house_cusps=houses,
            planets=planets,
            planets_by_house={2: ("Moon", "Venus")},
        ),
        navamsha_chart=NavamshaChart(ascendant=asc, planets=planets, houses=houses),
    )


def test_star_and_sub_lord_calculation():
    star = get_star_lord(0.5)
    nakshatra, star_lord, sub_lord = get_sub_lord(0.5)

    assert star == "Ketu"
    assert nakshatra == "Ashwini"
    assert star_lord == "Ketu"
    assert sub_lord in {"Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"}


def test_significator_levels():
    significators = analyze_significators(_bundle())

    assert len(significators) == 12
    house_two = next(item for item in significators if item.house == 2)
    assert "Moon" in house_two.level_a
    assert house_two.combined


def test_event_framework_outputs_structured_events():
    bundle = _bundle()
    cusps = analyze_cusps(bundle)
    significators = analyze_significators(bundle)
    events = analyze_events(cusps, significators)

    assert len(events) >= 5
    assert all(event.event_id for event in events)
    assert all(0.0 <= event.support_score <= 1.0 for event in events)


def test_kp_engine_json_contract():
    from kp_engine import KPEngine

    payload = KPEngine().analyze_json(_bundle())

    assert payload["cusps"]
    assert payload["significators"]
    assert payload["star_lords"]
    assert payload["sub_lords"]
    assert payload["events"]
    assert payload["metadata"]["ai_interpretation"] is False
    assert json.dumps(payload)
