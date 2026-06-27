"""Pure utility tests for astrology engine (no Swiss Ephemeris required)."""

from astrology_engine.utilities.angles import (
    get_degree_in_sign,
    get_sign_index,
    normalize_longitude,
)
from astrology_engine.utilities.vedic import get_navamsha_sign_index, get_nakshatra, get_zodiac_sign, ketu_longitude


def test_normalize_longitude():
    assert normalize_longitude(370.0) == 10.0
    assert normalize_longitude(-10.0) == 350.0


def test_sign_index_and_degree_in_sign():
    assert get_sign_index(45.0) == 1
    assert get_degree_in_sign(45.0) == 15.0


def test_zodiac_sign_metadata():
    sign = get_zodiac_sign(45.0)
    assert sign.name_en == "Taurus"
    assert sign.name_sa == "Vrishabha"
    assert sign.lord == "Venus"


def test_nakshatra_pada():
    nakshatra = get_nakshatra(45.0)
    assert nakshatra.name
    assert 1 <= nakshatra.pada <= 4


def test_navamsha_rules():
    # Aries 10° -> 4th navamsha division -> Cancer (index 3)
    assert get_navamsha_sign_index(10.0) == 3
    # Taurus 10° (40° absolute) -> Capricorn navamsha sequence
    assert get_navamsha_sign_index(40.0) == 0


def test_ketu_opposite_rahu():
    assert ketu_longitude(120.0) == 300.0
