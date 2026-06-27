"""Unit tests for house cusp calculation indexing and validation."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from astrology_engine.calculations.houses import calculate_house_cusps
from astrology_engine.core.types import HouseSystemType

JULIAN_DAY = 2451545.0
LATITUDE = 28.6139
LONGITUDE = 77.2090


def _mock_ephemeris(cusps: tuple[float, ...]) -> MagicMock:
    ephemeris = MagicMock()
    ephemeris.calc_houses_ut.return_value = (cusps, ())
    return ephemeris


def test_house_cusps_pyswisseph_twelve_element_tuple():
    """pyswisseph returns 12 cusps: house 1 at index 0, house 12 at index 11."""
    cusps = tuple(index * 30.0 for index in range(12))
    ephemeris = _mock_ephemeris(cusps)

    houses = calculate_house_cusps(
        ephemeris,
        JULIAN_DAY,
        LATITUDE,
        LONGITUDE,
        house_system=HouseSystemType.PLACIDUS,
    )

    assert len(houses) == 12
    assert houses[0].number == 1
    assert houses[0].longitude == 0.0
    assert houses[11].number == 12
    assert houses[11].longitude == 330.0


def test_house_cusps_swe_thirteen_element_tuple():
    """Swiss Ephemeris C API / pysweph: index 0 unused, houses 1-12 at indices 1-12."""
    cusps = (0.0,) + tuple(index * 30.0 for index in range(12))
    ephemeris = _mock_ephemeris(cusps)

    houses = calculate_house_cusps(
        ephemeris,
        JULIAN_DAY,
        LATITUDE,
        LONGITUDE,
        house_system=HouseSystemType.SRIPATHI,
    )

    assert len(houses) == 12
    assert houses[0].longitude == 0.0
    assert houses[11].longitude == 330.0


def test_house_cusps_invalid_tuple_length_raises_value_error():
    ephemeris = _mock_ephemeris((10.0, 20.0, 30.0))

    with pytest.raises(ValueError, match="unexpected cusps tuple length"):
        calculate_house_cusps(ephemeris, JULIAN_DAY, LATITUDE, LONGITUDE)


def test_house_cusps_invalid_latitude_raises_value_error():
    ephemeris = _mock_ephemeris(tuple(range(12)))

    with pytest.raises(ValueError, match="Invalid latitude"):
        calculate_house_cusps(ephemeris, JULIAN_DAY, 95.0, LONGITUDE)

    ephemeris.calc_houses_ut.assert_not_called()


def test_house_cusps_invalid_longitude_raises_value_error():
    ephemeris = _mock_ephemeris(tuple(range(12)))

    with pytest.raises(ValueError, match="Invalid longitude"):
        calculate_house_cusps(ephemeris, JULIAN_DAY, LATITUDE, 200.0)

    ephemeris.calc_houses_ut.assert_not_called()


def test_house_cusps_live_swisseph():
    """Integration check against installed pyswisseph return shape."""
    pytest.importorskip("swisseph")
    from astrology_engine.calculations.ephemeris import EphemerisService

    ephemeris = EphemerisService()
    houses = calculate_house_cusps(
        ephemeris,
        JULIAN_DAY,
        LATITUDE,
        LONGITUDE,
        house_system=HouseSystemType.PLACIDUS,
    )

    assert len(houses) == 12
    for house in houses:
        assert 0.0 <= house.longitude < 360.0
