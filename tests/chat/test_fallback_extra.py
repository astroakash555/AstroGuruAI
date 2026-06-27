"""Additional fallback and provider edge-case tests."""

from __future__ import annotations

from backend.app.services.chat.fallback import _format_dasha, _matching_sections, build_fallback_answer


def test_matching_sections_ignores_invalid_entries():
    assert _matching_sections(["bad", {"section_id": "career", "title": "Career"}], "career path")[
        0
    ]["title"] == "Career"
    assert _matching_sections("invalid", "career") == []


def test_format_dasha_variants():
    assert "Saturn mahadasha with Mercury antardasha" == _format_dasha(
        {"current": {"mahadasha": {"lord": "Saturn"}, "antardasha": {"lord": "Mercury"}}}
    )
    assert "Saturn mahadasha" == _format_dasha({"current": {"mahadasha": {"lord": "Saturn"}}})
    assert "the active dasha period" in _format_dasha({"current": {}})
    assert "dasha details" in _format_dasha(None)


def test_fallback_fusion_dasha_only():
    answer = build_fallback_answer(
        report_context={
            "fusion": {
                "recommendations": [{"title": "Focus Saturn", "explanation": "Be patient."}]
            },
            "dasha": {"current": {"mahadasha": {"lord": "Saturn"}}},
            "consultation_brain": {"sections": []},
        },
        user_message="What next?",
    )
    assert "Focus Saturn" in answer
    assert "Saturn mahadasha" in answer
