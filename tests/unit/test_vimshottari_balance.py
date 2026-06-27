"""Vimshottari dasha balance and duration tests."""

from astrology_engine.core.constants import DEGREES_PER_NAKSHATRA
from astrology_engine.dasha.balance import (
    compute_balance_at_birth,
    get_dasha_lord_for_nakshatra,
    sub_period_duration_years,
)
from astrology_engine.dasha.constants import VIMSHOTTARI_TOTAL_YEARS


def test_balance_at_nakshatra_start():
    balance = compute_balance_at_birth(0.0)
    assert balance.lord == "Ketu"
    assert balance.remaining_fraction == 1.0
    assert balance.duration_years == 7.0


def test_balance_at_nakshatra_midpoint():
    midpoint = DEGREES_PER_NAKSHATRA / 2.0
    balance = compute_balance_at_birth(midpoint)
    assert balance.lord == "Ketu"
    assert abs(balance.remaining_fraction - 0.5) < 0.001
    assert abs(balance.duration_years - 3.5) < 0.01


def test_sub_period_duration_formula():
    assert sub_period_duration_years("Ketu", "Venus") == (7 * 20) / VIMSHOTTARI_TOTAL_YEARS
    assert sub_period_duration_years("Moon", "Saturn") == (10 * 19) / VIMSHOTTARI_TOTAL_YEARS


def test_nakshatra_lord_mapping():
    assert get_dasha_lord_for_nakshatra("Ashwini") == "Ketu"
    assert get_dasha_lord_for_nakshatra("Rohini") == "Moon"
    assert get_dasha_lord_for_nakshatra("Revati") == "Mercury"
