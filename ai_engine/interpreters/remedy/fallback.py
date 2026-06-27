"""Rule-based remedy generation fallback."""

from __future__ import annotations

from typing import Any

from ai_engine.interpreters.remedy.types import GeneratedRemedy
from remedy_engine import RemedyEngine, RemedyMatchContext


def build_fallback_remedies(report_json: dict[str, Any], *, max_remedies: int) -> tuple[GeneratedRemedy, ...]:
    intelligence = report_json.get("astro_intelligence", {})
    problem = report_json.get("problem_analysis") or {}
    context = RemedyMatchContext(
        root_cause_planets=tuple(intelligence.get("root_cause_planets", [])),
        affected_houses=tuple(intelligence.get("affected_houses", [])),
        categories=(
            (problem.get("category", {}).get("category", "unknown"),)
            if problem
            else ()
        ),
        severity_level=problem.get("severity", {}).get("level", "moderate"),
        max_results=max_remedies,
    )
    matches = RemedyEngine().match(context).matched_remedies
    remedies: list[GeneratedRemedy] = []
    for match in matches:
        remedy = match.remedy
        remedies.append(
            GeneratedRemedy(
                remedy_type=remedy.remedy_type,
                astrology_system=remedy.astrology_system,
                title=remedy.remedy_name,
                description=remedy.description,
                planet=remedy.planet,
                house=remedy.house,
                priority=remedy.priority,
                confidence_score=round(match.match_score, 3),
                expected_effect=remedy.expected_effect,
            )
        )
    _append_gemstone_and_mantra_suggestions(remedies, intelligence)
    remedies.sort(key=lambda item: (item.priority, -item.confidence_score))
    return tuple(remedies[:max_remedies])


def _append_gemstone_and_mantra_suggestions(
    remedies: list[GeneratedRemedy],
    intelligence: dict[str, Any],
) -> None:
    planet_priority = {
        "Saturn": ("gemstone", "Blue Sapphire guidance", "Strengthen Saturn discipline after proper consultation."),
        "Jupiter": ("gemstone", "Yellow Sapphire guidance", "Support Jupiter wisdom after proper consultation."),
        "Mars": ("mantra", "Hanuman Mantra", "Recite Hanuman Chalisa on Tuesdays for Mars balance."),
        "Moon": ("mantra", "Chandra Mantra", "Chant Chandra beeja mantra on Monday evenings."),
        "Rahu": ("donation", "Rahu Donation Protocol", "Offer mustard oil charity on Saturdays."),
        "Venus": ("donation", "Venus Charity", "Offer white sweets on Fridays for relationship harmony."),
    }
    for planet in intelligence.get("root_cause_planets", [])[:3]:
        mapping = planet_priority.get(planet)
        if not mapping:
            continue
        remedy_type, title, effect = mapping
        remedies.append(
            GeneratedRemedy(
                remedy_type=remedy_type,
                astrology_system="vedic",
                title=title,
                description=effect,
                planet=planet,
                house=None,
                priority=2,
                confidence_score=0.65,
                expected_effect=effect,
            )
        )
