"""Dosha detection engine tests."""

from __future__ import annotations

import json

import pytest

from astrology_engine.core.types import Ascendant, HouseCusp, LagnaKundali, NakshatraInfo, PlanetPosition, ZodiacSign
from astrology_engine.doshas import DoshaDetectionEngine, DoshaRegistry
from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.rules import (
    DEFAULT_DOSHA_RULES,
    GrahanDoshaRule,
    KaalSarpDoshaRule,
    MangalDoshaRule,
    PitraDoshaRule,
    ShrapitDoshaRule,
)
from astrology_engine.doshas.rules._helpers import build_detection, condition
from astrology_engine.yogas.context import build_chart_context


def _sign(index: int, degree: float = 10.0) -> ZodiacSign:
    names_en = (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    )
    names_sa = (
        "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
        "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
    )
    lords = ("Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter")
    return ZodiacSign(index=index, name_en=names_en[index], name_sa=names_sa[index], lord=lords[index], degree_in_sign=degree)


def _nakshatra(index: int = 0) -> NakshatraInfo:
    return NakshatraInfo(index=index, name="Ashwini", lord="Ketu", pada=1)


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


def _chart(planets: list[PlanetPosition], lagna_sign: int = 0) -> LagnaKundali:
    asc = Ascendant(longitude=lagna_sign * 30.0 + 5.0, sign=_sign(lagna_sign), nakshatra=_nakshatra(0))
    houses = tuple(
        HouseCusp(number=i, longitude=((lagna_sign + i - 1) % 12) * 30.0, sign=_sign((lagna_sign + i - 1) % 12))
        for i in range(1, 13)
    )
    return LagnaKundali(ascendant=asc, planets=tuple(planets), houses=houses)


def _all_planets(**overrides: PlanetPosition) -> list[PlanetPosition]:
    defaults = {
        "Sun": _planet("Sun", 4, 5),
        "Moon": _planet("Moon", 1, 2),
        "Mars": _planet("Mars", 7, 8),
        "Mercury": _planet("Mercury", 2, 3),
        "Jupiter": _planet("Jupiter", 8, 9),
        "Venus": _planet("Venus", 1, 2),
        "Saturn": _planet("Saturn", 9, 10),
        "Rahu": _planet("Rahu", 5, 6),
        "Ketu": _planet("Ketu", 11, 12),
    }
    defaults.update(overrides)
    return list(defaults.values())


@pytest.fixture
def engine() -> DoshaDetectionEngine:
    return DoshaDetectionEngine()


def test_default_dosha_rules_registered(engine: DoshaDetectionEngine):
    ids = {rule.dosha_id for rule in engine.registry.rules()}
    assert ids == {
        "mangal_dosha",
        "kaal_sarp_dosha",
        "pitra_dosha",
        "grahan_dosha",
        "shrapit_dosha",
    }


def test_mangal_dosha_detection():
    chart = _chart(_all_planets(mars=_planet("Mars", 6, 7)))
    result = MangalDoshaRule().detect(build_chart_context(chart))
    assert result.is_present is True
    assert result.severity > 0


def test_kaal_sarp_dosha_detection():
    # Rahu at 120°, Ketu at 300° — planets between 120 and 300
    chart = _chart(_all_planets(
        rahu=_planet("Rahu", 4, 5, 125.0),
        ketu=_planet("Ketu", 10, 11, 305.0),
        sun=_planet("Sun", 4, 5, 130.0),
        moon=_planet("Moon", 5, 6, 160.0),
        mars=_planet("Mars", 6, 7, 190.0),
        mercury=_planet("Mercury", 7, 8, 220.0),
        jupiter=_planet("Jupiter", 8, 9, 250.0),
        venus=_planet("Venus", 9, 10, 280.0),
        saturn=_planet("Saturn", 5, 6, 170.0),
    ))
    result = KaalSarpDoshaRule().detect(build_chart_context(chart))
    assert result.is_present is True
    assert result.subtype is not None


def test_pitra_dosha_detection():
    chart = _chart(_all_planets(
        sun=_planet("Sun", 5, 6, 150.0),
        rahu=_planet("Rahu", 5, 6, 155.0),
    ), lagna_sign=3)
    result = PitraDoshaRule().detect(build_chart_context(chart))
    assert result.is_present is True


def test_grahan_dosha_detection():
    chart = _chart(_all_planets(
        moon=_planet("Moon", 7, 8, 210.0),
        rahu=_planet("Rahu", 7, 8, 215.0),
    ))
    result = GrahanDoshaRule().detect(build_chart_context(chart))
    assert result.is_present is True
    assert result.subtype == "lunar_grahan"


def test_shrapit_dosha_detection():
    chart = _chart(_all_planets(
        saturn=_planet("Saturn", 9, 10, 275.0),
        rahu=_planet("Rahu", 9, 10, 280.0),
    ))
    result = ShrapitDoshaRule().detect(build_chart_context(chart))
    assert result.is_present is True
    assert result.severity >= 0.75


def test_engine_json_output(engine: DoshaDetectionEngine):
    chart = _chart(_all_planets(
        mars=_planet("Mars", 6, 7),
        sun=_planet("Sun", 5, 6, 150.0),
        rahu=_planet("Rahu", 5, 6, 155.0),
        saturn=_planet("Saturn", 9, 10, 275.0),
    ), lagna_sign=0)
    payload = engine.detect_json(chart)

    assert payload["summary"]["total_rules"] == 5
    assert "present_doshas" in payload
    assert payload["metadata"]["remedies_generated"] is False
    assert "remedy" not in json.dumps(payload).lower()
    assert len(payload["present_doshas"]) >= 2


def test_registry_extension():
    class DummyDoshaRule(DoshaRule):
        dosha_id = "dummy_dosha"
        dosha_name = "Dummy Dosha"
        category = "test"

        def detect(self, context):
            return build_detection(
                dosha_id=self.dosha_id,
                dosha_name=self.dosha_name,
                category_key="mangal_dosha",
                is_present=True,
                severity=0.4,
                description="Test dosha",
                planets=(),
                houses=(),
                conditions=[condition("test", True, "test")],
                evidence=["dummy"],
            )

    registry = DoshaRegistry()
    for rule in DEFAULT_DOSHA_RULES:
        registry.register(rule)
    registry.register(DummyDoshaRule())

    chart = _chart(_all_planets())
    custom = DoshaDetectionEngine(registry=registry)
    result = custom.detect(chart)
    assert result.summary.total_rules == 6
