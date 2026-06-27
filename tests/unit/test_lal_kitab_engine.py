"""Lal Kitab engine unit tests."""

from __future__ import annotations

import json

from lal_kitab_engine import LalKitabEngine
from lal_kitab_engine.analyzers.planet_house import analyze_planet_by_house
from lal_kitab_engine.context import build_lal_kitab_context
from lal_kitab_engine.registry import LalKitabRegistry
from lal_kitab_engine.rules import DEFAULT_LAL_KITAB_RULES
from lal_kitab_engine.rules.rin import PitraRinRule


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


def _planet(name: str, sign_index: int, house: int):
    from astrology_engine.core.types import NakshatraInfo, PlanetPosition

    return PlanetPosition(
        name=name,
        longitude=sign_index * 30.0 + 10.0,
        latitude=0.0,
        speed=1.0,
        is_retrograde=False,
        sign=_sign(sign_index),
        nakshatra=NakshatraInfo(index=0, name="Ashwini", lord="Ketu", pada=1),
        house=house,
    )


def _chart(**overrides):
    from astrology_engine.core.types import Ascendant, HouseCusp, LagnaKundali, NakshatraInfo

    defaults = {
        "Sun": _planet("Sun", 8, 9),
        "Moon": _planet("Moon", 3, 4),
        "Mars": _planet("Mars", 7, 8),
        "Mercury": _planet("Mercury", 2, 3),
        "Jupiter": _planet("Jupiter", 8, 9),
        "Venus": _planet("Venus", 6, 7),
        "Saturn": _planet("Saturn", 11, 12),
        "Rahu": _planet("Rahu", 3, 4),
        "Ketu": _planet("Ketu", 9, 10),
    }
    defaults.update(overrides)
    asc = Ascendant(
        longitude=5.0,
        sign=_sign(0),
        nakshatra=NakshatraInfo(index=0, name="Ashwini", lord="Ketu", pada=1),
    )
    houses = tuple(
        HouseCusp(number=i, longitude=((i - 1) % 12) * 30.0, sign=_sign((i - 1) % 12))
        for i in range(1, 13)
    )
    return LagnaKundali(ascendant=asc, planets=tuple(defaults.values()), houses=houses)


def test_default_rules_registered():
    engine = LalKitabEngine()
    assert len(engine.registry.rules) == len(DEFAULT_LAL_KITAB_RULES)


def test_pitra_rin_rule_detects_sun_saturn_axis():
    chart = _chart(
        Sun=_planet("Sun", 8, 9),
        Saturn=_planet("Saturn", 11, 12),
    )
    context = build_lal_kitab_context(chart)
    finding = PitraRinRule().analyze(context)

    assert finding.finding_id == "pitra_rin"
    assert finding.is_present is True


def test_planet_by_house_analysis_count():
    chart = _chart()
    context = build_lal_kitab_context(chart)
    analyses = analyze_planet_by_house(context)

    assert len(analyses) == 9
    assert all(item.effect_code for item in analyses)


def test_lal_kitab_json_contract():
    engine = LalKitabEngine()
    payload = engine.analyze_json(_chart())

    assert "planet_by_house" in payload
    assert "rin_findings" in payload
    assert "dosh_findings" in payload
    assert "recommendations" in payload
    assert payload["metadata"]["ai_interpretation"] is False
    assert json.dumps(payload)


def test_registry_extension():
    registry = LalKitabRegistry()
    registry.register(PitraRinRule())
    assert len(registry.rules) == 1
