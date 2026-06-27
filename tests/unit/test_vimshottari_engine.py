"""Vimshottari dasha period tree tests."""

from datetime import datetime, timezone

from astrology_engine.dasha.balance import compute_balance_at_birth
from astrology_engine.dasha.calculator import build_mahadashas, find_active_periods
from astrology_engine.dasha.engine import VimshottariDashaEngine
from astrology_engine.dasha.serializer import to_json_dict
from astrology_engine.dasha.types import DashaBirthInput


def test_build_mahadasha_sequence():
    birth = datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc)
    balance = compute_balance_at_birth(0.0)
    mahadashas = build_mahadashas(birth, balance, max_years=120.0)

    assert len(mahadashas) >= 9
    assert mahadashas[0].lord == "Ketu"
    assert mahadashas[0].start == birth
    assert mahadashas[1].lord == "Venus"


def test_mahadasha_contains_antardasha_and_pratyantar():
    birth = datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc)
    balance = compute_balance_at_birth(0.0)
    mahadashas = build_mahadashas(birth, balance, max_years=20.0)
    first = mahadashas[0]

    assert len(first.antardashas) >= 1
    assert first.antardashas[0].lord == first.lord
    assert len(first.antardashas[0].pratyantar_dashas) >= 1
    assert first.antardashas[0].pratyantar_dashas[0].lord == first.antardashas[0].lord


def test_find_active_periods_at_birth():
    birth = datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc)
    balance = compute_balance_at_birth(0.0)
    mahadashas = build_mahadashas(birth, balance, max_years=120.0)
    current = find_active_periods(mahadashas, birth)

    assert current["mahadasha"] is not None
    assert current["mahadasha"].lord == "Ketu"
    assert current["antardasha"] is not None
    assert current["antardasha"].lord == "Ketu"
    assert current["pratyantar_dasha"] is not None
    assert current["pratyantar_dasha"].lord == "Ketu"


def test_engine_json_output_structure():
    engine = VimshottariDashaEngine()
    birth_input = DashaBirthInput(
        date_of_birth=datetime(1990, 1, 15, tzinfo=timezone.utc).date(),
        birth_time=datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc).time(),
        birth_place="New Delhi, India",
        timezone="UTC",
        moon_nakshatra="Ashwini",
        moon_longitude=0.5,
    )
    payload = engine.compute_json(birth_input)

    assert payload["system"] == "vimshottari"
    assert payload["moon"]["nakshatra"] == "Ashwini"
    assert payload["balance"]["lord"] == "Ketu"
    assert "mahadashas" in payload
    assert len(payload["mahadashas"]) >= 1
    assert "antardashas" in payload["mahadashas"][0]
    assert "pratyantar_dashas" in payload["mahadashas"][0]["antardashas"][0]
    assert payload["current"]["mahadasha"]["lord"] == "Ketu"


def test_json_serializer_roundtrip_fields():
    engine = VimshottariDashaEngine()
    birth_input = DashaBirthInput(
        date_of_birth=datetime(1995, 6, 15).date(),
        birth_time=datetime(1995, 6, 15, 10, 30).time(),
        birth_place="Mumbai, India",
        timezone="Asia/Kolkata",
        moon_nakshatra="Rohini",
        moon_longitude=45.0,
    )
    result = engine.compute(birth_input)
    payload = to_json_dict(result)

    assert payload["birth"]["birth_place"] == "Mumbai, India"
    assert payload["moon"]["lord"] == "Moon"
    assert isinstance(payload["mahadashas"], list)
