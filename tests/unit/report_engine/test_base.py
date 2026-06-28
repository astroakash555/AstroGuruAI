"""Tests for shared report engine helpers."""

from backend.app.services.report_engine.base import join_lines, moon_planet, planet_lookup, section


def test_planet_lookup_indexes_by_name(sample_unified_report):
    planets = planet_lookup(sample_unified_report["kundali"])
    assert planets["Moon"]["sign"]["name_en"] == "Aries"


def test_moon_planet_returns_moon(sample_unified_report):
    moon = moon_planet(sample_unified_report["kundali"])
    assert moon is not None
    assert moon["name"] == "Moon"


def test_section_clamps_confidence():
    built = section(
        section_id="test",
        title="Test",
        narrative="Text",
        facts={},
        confidence=1.5,
    )
    assert built.confidence == 1.0


def test_join_lines_skips_empty():
    assert join_lines(["a", "", "b"]) == "a\nb"
