"""Astrology engine unit tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

pytest.importorskip("swisseph")

from astrology_engine import BirthData, VedicAstrologyEngine
from astrology_engine.core.constants import PLANET_ORDER
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.utilities.vedic import get_navamsha_sign_index, get_whole_sign_house, ketu_longitude


@pytest.fixture
def sample_birth_data() -> BirthData:
    return BirthData(
        datetime_utc=datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )


@pytest.fixture
def engine() -> VedicAstrologyEngine:
    return VedicAstrologyEngine()


def test_engine_compute_bundle_structure(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)

    assert bundle.metadata.julian_day > 0
    assert bundle.metadata.ayanamsa == "lahiri"
    assert len(bundle.planetary_positions) == 9
    assert len(bundle.lagna_kundali.houses) == 12
    assert len(bundle.bhava_chart.house_cusps) == 12
    assert len(bundle.navamsha_chart.planets) == 9
    assert len(bundle.navamsha_chart.houses) == 12


def test_planetary_positions_include_all_grahas(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)
    names = {planet.name for planet in bundle.planetary_positions}
    assert names == set(PLANET_ORDER)


def test_ketu_is_opposite_rahu(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)
    planets = {planet.name: planet for planet in bundle.planetary_positions}
    rahu = planets["Rahu"].longitude
    ketu = planets["Ketu"].longitude
    assert abs(normalize_longitude(ketu - rahu) - 180.0) < 0.0001
    assert abs(ketu_longitude(rahu) - ketu) < 0.0001


def test_lagna_kundali_assigns_houses(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)
    lagna_sign = bundle.lagna_kundali.ascendant.sign.index

    for planet in bundle.lagna_kundali.planets:
        assert planet.house is not None
        assert 1 <= planet.house <= 12
        expected = get_whole_sign_house(planet.sign.index, lagna_sign)
        assert planet.house == expected


def test_bhava_chart_groups_planets_by_house(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)
    grouped = bundle.bhava_chart.planets_by_house
    assert len(grouped) == 12
    assigned = sum(len(names) for names in grouped.values())
    assert assigned == len(bundle.bhava_chart.planets)


def test_navamsha_sign_calculation():
    assert get_navamsha_sign_index(10.0) == 3
    assert get_navamsha_sign_index(40.0) == 0


def test_ascendant_has_valid_sign(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)
    asc = bundle.lagna_kundali.ascendant
    assert 0 <= asc.sign.index <= 11
    assert 0.0 <= asc.sign.degree_in_sign < 30.0
    assert 1 <= asc.nakshatra.pada <= 4


def test_planets_have_nakshatra(engine: VedicAstrologyEngine, sample_birth_data: BirthData):
    bundle = engine.compute_chart(sample_birth_data)
    for planet in bundle.planetary_positions:
        assert planet.nakshatra.name
        assert 1 <= planet.nakshatra.pada <= 4
        assert 0.0 <= planet.sign.degree_in_sign < 30.0
