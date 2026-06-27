"""Yoga detection engine tests."""

from __future__ import annotations

import json

import pytest

from astrology_engine.core.types import Ascendant, HouseCusp, LagnaKundali, NakshatraInfo, PlanetPosition, ZodiacSign
from astrology_engine.yogas import YogaDetectionEngine, YogaRegistry
from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.context import ChartContext, build_chart_context
from astrology_engine.yogas.rules._helpers import build_detection, condition
from astrology_engine.yogas.rules import (
    BudhadityaYogaRule,
    ChandraMangalYogaRule,
    DEFAULT_YOGA_RULES,
    GajKesariYogaRule,
    NeechBhangRajYogaRule,
    RajYogaRule,
    VipreetRajYogaRule,
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
    lords = ("Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter")
    return ZodiacSign(
        index=index,
        name_en=names_en[index],
        name_sa=names_sa[index],
        lord=lords[index],
        degree_in_sign=degree,
    )


def _nakshatra(index: int = 0) -> NakshatraInfo:
    names = ("Ashwini", "Bharani", "Rohini")
    lords = ("Ketu", "Venus", "Moon")
    return NakshatraInfo(index=index, name=names[min(index, 2)], lord=lords[min(index, 2)], pada=1)


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
    asc = Ascendant(
        longitude=lagna_sign * 30.0 + 5.0,
        sign=_sign(lagna_sign),
        nakshatra=_nakshatra(0),
    )
    houses = tuple(
        HouseCusp(number=i, longitude=((lagna_sign + i - 1) % 12) * 30.0, sign=_sign((lagna_sign + i - 1) % 12))
        for i in range(1, 13)
    )
    return LagnaKundali(ascendant=asc, planets=tuple(planets), houses=houses)


@pytest.fixture
def engine() -> YogaDetectionEngine:
    return YogaDetectionEngine()


def test_default_rules_registered(engine: YogaDetectionEngine):
    assert len(engine.registry.rules()) == 6
    yoga_ids = {rule.yoga_id for rule in engine.registry.rules()}
    assert yoga_ids == {
        "gaj_kesari",
        "raj_yoga",
        "vipreet_raj",
        "budhaditya",
        "chandra_mangal",
        "neech_bhang_raj",
    }


def test_gaj_kesari_detection():
    chart = _chart([
        _planet("Moon", 0, 1),
        _planet("Jupiter", 3, 4),
        _planet("Sun", 4, 5),
        _planet("Mars", 7, 8),
        _planet("Mercury", 2, 3),
        _planet("Venus", 1, 2),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ])
    result = GajKesariYogaRule().detect(build_chart_context(chart))
    assert result.is_present is True
    assert result.strength >= 0.75


def test_budhaditya_detection():
    chart = _chart([
        _planet("Sun", 4, 5, 124.0),
        _planet("Mercury", 4, 5, 132.0),
        _planet("Moon", 1, 2),
        _planet("Mars", 7, 8),
        _planet("Jupiter", 8, 9),
        _planet("Venus", 2, 3),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ])
    result = BudhadityaYogaRule().detect(build_chart_context(chart))
    assert result.is_present is True


def test_chandra_mangal_detection():
    chart = _chart([
        _planet("Moon", 3, 4, 94.0),
        _planet("Mars", 3, 4, 98.0),
        _planet("Sun", 4, 5),
        _planet("Mercury", 2, 3),
        _planet("Jupiter", 8, 9),
        _planet("Venus", 1, 2),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ])
    result = ChandraMangalYogaRule().detect(build_chart_context(chart))
    assert result.is_present is True


def test_vipreet_raj_detection():
    # Cancer lagna: 6th lord Jupiter placed in 8th house (Capricorn)
    chart = _chart([
        _planet("Jupiter", 9, 8),
        _planet("Moon", 3, 4),
        _planet("Sun", 4, 5),
        _planet("Mars", 7, 8),
        _planet("Mercury", 2, 3),
        _planet("Venus", 1, 2),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ], lagna_sign=3)
    result = VipreetRajYogaRule().detect(build_chart_context(chart))
    assert result.is_present is True


def test_neech_bhang_raj_detection():
    # Jupiter debilitated in Capricorn (9), dispositor Saturn in kendra (house 10)
    chart = _chart([
        _planet("Jupiter", 9, 4),
        _planet("Saturn", 9, 10),
        _planet("Moon", 1, 2),
        _planet("Sun", 4, 5),
        _planet("Mars", 7, 8),
        _planet("Mercury", 2, 3),
        _planet("Venus", 1, 2),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ], lagna_sign=0)
    result = NeechBhangRajYogaRule().detect(build_chart_context(chart))
    assert result.is_present is True
    assert len(result.evidence) >= 1


def test_raj_yoga_detection():
    # Aries lagna: 5th lord Jupiter and 9th lord Jupiter - need different lords
    # Cancer lagna: 4th lord Venus (Libra), 5th lord Mars (Scorpio) - put Mars and Venus together
    chart = _chart([
        _planet("Venus", 6, 1),
        _planet("Mars", 6, 1, 186.0),
        _planet("Moon", 3, 4),
        _planet("Sun", 4, 5),
        _planet("Mercury", 2, 3),
        _planet("Jupiter", 8, 9),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ], lagna_sign=3)
    result = RajYogaRule().detect(build_chart_context(chart))
    assert result.is_present is True


def test_engine_json_output(engine: YogaDetectionEngine):
    chart = _chart([
        _planet("Moon", 0, 1),
        _planet("Jupiter", 3, 4),
        _planet("Sun", 4, 5, 124.0),
        _planet("Mercury", 4, 5, 132.0),
        _planet("Mars", 0, 1, 8.0),
        _planet("Venus", 1, 2),
        _planet("Saturn", 9, 10),
        _planet("Rahu", 5, 6),
        _planet("Ketu", 11, 12),
    ])
    payload = engine.detect_json(chart)

    assert "yogas" in payload
    assert "present_yogas" in payload
    assert "summary" in payload
    assert payload["summary"]["total_rules"] == 6
    assert len(payload["present_yogas"]) >= 2
    json.dumps(payload)

    present_ids = {item["yoga_id"] for item in payload["present_yogas"]}
    assert "gaj_kesari" in present_ids
    assert "budhaditya" in present_ids


def test_registry_extension():
    class DummyYogaRule(YogaRule):
        yoga_id = "dummy_yoga"
        yoga_name = "Dummy Yoga"
        category = "test"

        def detect(self, context: ChartContext):
            return build_detection(
                yoga_id=self.yoga_id,
                yoga_name=self.yoga_name,
                category_key="gaj_kesari",
                is_present=True,
                strength=0.5,
                description="Test rule",
                planets=(),
                houses=(),
                conditions=[condition("always", True, "test")],
                evidence=["dummy"],
            )

    registry = YogaRegistry()
    for rule in DEFAULT_YOGA_RULES:
        registry.register(rule)
    registry.register(DummyYogaRule())

    chart = _chart([_planet("Moon", 0, 1), _planet("Sun", 1, 2)])
    # Need all planets - use minimal with required ones
    full_chart = _chart([
        _planet("Moon", 0, 1),
        _planet("Sun", 1, 2),
        _planet("Mars", 2, 3),
        _planet("Mercury", 3, 4),
        _planet("Jupiter", 4, 5),
        _planet("Venus", 5, 6),
        _planet("Saturn", 6, 7),
        _planet("Rahu", 7, 8),
        _planet("Ketu", 8, 9),
    ])
    custom_engine = YogaDetectionEngine(registry=registry)
    result = custom_engine.detect(full_chart)
    assert result.summary.total_rules == 7
    assert any(yoga.yoga_id == "dummy_yoga" for yoga in result.yogas)
