"""Tests for chat context builder."""

from __future__ import annotations

from backend.app.services.chat.context_builder import build_report_context, context_section_keys


def test_build_report_context_includes_required_sections(sample_unified_report):
    context = build_report_context(sample_unified_report)

    assert set(context_section_keys()).issubset(set(context.keys()))
    assert context["consultation_brain"]["executive_summary"]
    assert context["fusion"]["recommendations"]
    assert context["dasha"]["current"]["mahadasha"]["lord"] == "Saturn"
    assert context["transits"]["metadata"]["engine"] == "transit_engine_v1"
    assert context["kp"]["event_timing"]


def test_build_report_context_handles_missing_sections():
    context = build_report_context({"version": "unified_report_v2"})

    assert context["consultation_brain"] is None
    assert context["fusion"] is None
    assert context["vedic"] is None


def test_build_report_context_skips_invalid_nested_items():
    context = build_report_context(
        {
            "consultation_brain": {"sections": ["invalid", {"section_id": "marriage", "title": "Marriage"}]},
            "fusion": {"observations": ["invalid", {"title": "Observation"}]},
            "lal_kitab_intelligence": {"observations": [], "remedies": ["bad", {"title": "Remedy"}]},
            "transits": {"significant_transits": "invalid"},
        }
    )

    assert context["consultation_brain"]["sections"][0]["section_id"] == "marriage"
    assert context["fusion"]["observations"][0]["title"] == "Observation"
    assert context["lal_kitab_intelligence"]["remedies"][0]["title"] == "Remedy"
    assert context["transits"]["significant_transits"] is None
    assert build_report_context({"fusion": {"observations": "invalid"}})["fusion"]["observations"] == []

