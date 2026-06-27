"""Supportive planet detection."""

from __future__ import annotations

BENEFICS = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})
KENDRA_HOUSES = frozenset({1, 4, 7, 10})


def detect_supportive_planets(analysis_input) -> tuple[str, ...]:
    """Detect planets providing structural support."""
    supportive: dict[str, float] = {}
    planets = {item["name"]: item for item in analysis_input.kundali.get("planets", [])}

    for yoga in analysis_input.yogas.get("present_yogas", []):
        if yoga.get("strength", 0) < 0.55:
            continue
        for planet in yoga.get("planets_involved", []):
            supportive[planet] = supportive.get(planet, 0.0) + yoga.get("strength", 0.0)

    for planet_name, data in planets.items():
        house = data.get("house")
        if planet_name in BENEFICS and house in KENDRA_HOUSES:
            supportive[planet_name] = supportive.get(planet_name, 0.0) + 0.35

    if analysis_input.kp_analysis:
        for event in analysis_input.kp_analysis.get("events", []):
            if event.get("is_supported"):
                for planet in event.get("significators_matched", []):
                    if planet in BENEFICS:
                        supportive[planet] = supportive.get(planet, 0.0) + 0.2

    ranked = sorted(supportive.items(), key=lambda item: item[1], reverse=True)
    return tuple(planet for planet, score in ranked if score >= 0.2)
