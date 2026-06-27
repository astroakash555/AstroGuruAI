"""Tests for chat fallback answers."""

from __future__ import annotations

from backend.app.services.chat.context_builder import build_report_context
from backend.app.services.chat.fallback import build_fallback_answer


def test_fallback_matches_marriage_section(sample_unified_report):
    context = build_report_context(sample_unified_report)
    answer = build_fallback_answer(report_context=context, user_message="Why is my marriage delayed?")

    assert "Marriage" in answer
    assert "Venus pacification" in answer


def test_fallback_uses_fusion_recommendation(sample_unified_report):
    context = build_report_context(sample_unified_report)
    context["consultation_brain"]["sections"] = []
    answer = build_fallback_answer(report_context=context, user_message="What should I do next?")

    assert "Strengthen Venus" in answer


def test_fallback_generic_prompt(sample_unified_report):
    context = build_report_context({"summary": {"lagna_sign": "Aries", "moon_sign": "Leo"}})
    answer = build_fallback_answer(report_context=context, user_message="Hello")

    assert "Lagna Aries" in answer


def test_fallback_uses_executive_summary(sample_unified_report):
    context = build_report_context(sample_unified_report)
    context["consultation_brain"]["sections"] = []
    context["fusion"]["recommendations"] = []
    answer = build_fallback_answer(report_context=context, user_message="Give me an overview")

    assert "Marriage delay is the dominant theme." in answer


def test_fallback_default_message():
    answer = build_fallback_answer(report_context={}, user_message="Hello")
    assert "saved Kundali report" in answer


def test_fallback_section_without_advice(sample_unified_report):
    context = build_report_context(sample_unified_report)
    context["consultation_brain"]["sections"] = [
        {
            "section_id": "marriage",
            "title": "Marriage",
            "current_situation": "Delay continues.",
            "root_cause": "Venus affliction.",
            "actionable_advice": [],
        }
    ]
    answer = build_fallback_answer(report_context=context, user_message="marriage delay")
    assert "Review the active dasha" in answer

