"""Strongest planetary influence detection."""

from __future__ import annotations

BENEFICS = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})


def detect_strongest_influences(analysis_input) -> tuple[str, ...]:
    """Rank planets by combined influence score."""
    scores: dict[str, float] = {}

    for yoga in analysis_input.yogas.get("present_yogas", []):
        for planet in yoga.get("planets_involved", []):
            scores[planet] = scores.get(planet, 0.0) + yoga.get("strength", 0.0)

    current = analysis_input.dasha.get("current", {})
    for key, weight in (("mahadasha", 0.4), ("antardasha", 0.3), ("pratyantar_dasha", 0.2)):
        period = current.get(key)
        if period and period.get("lord"):
            scores[period["lord"]] = scores.get(period["lord"], 0.0) + weight

    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = analysis_input.transits.get(key, {})
        planet = section.get("planet") or key.capitalize()
        if key == "rahu":
            planet = "Rahu"
        if key == "ketu":
            planet = "Ketu"
        impact_total = sum(item.get("strength", 0.0) for item in section.get("natal_impacts", []))
        scores[planet] = scores.get(planet, 0.0) + impact_total * 0.5

    if analysis_input.kp_analysis:
        for event in analysis_input.kp_analysis.get("events", []):
            if event.get("is_supported"):
                for planet in event.get("significators_matched", []):
                    scores[planet] = scores.get(planet, 0.0) + event.get("support_score", 0.0) * 0.3

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return tuple(planet for planet, score in ranked[:5] if score > 0)
