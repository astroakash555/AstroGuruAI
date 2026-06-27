"""Root cause planet detection."""

from __future__ import annotations

from typing import Any

MALEFICS = frozenset({"Saturn", "Mars", "Rahu", "Ketu"})


def detect_root_cause_planets(analysis_input) -> tuple[str, ...]:
    """Detect root cause planets from structured analysis sections."""
    scores: dict[str, float] = {}

    for dosha in analysis_input.doshas.get("present_doshas", []):
        for planet in dosha.get("planets_involved", []):
            scores[planet] = scores.get(planet, 0.0) + dosha.get("severity", 0.5)

    if analysis_input.problem_analysis:
        for planet in analysis_input.problem_analysis.get("planets", {}).get("primary", []):
            scores[planet] = scores.get(planet, 0.0) + 0.35
        for planet in analysis_input.problem_analysis.get("planets", {}).get("shadow", []):
            scores[planet] = scores.get(planet, 0.0) + 0.2

    current = analysis_input.dasha.get("current", {})
    for key in ("mahadasha", "antardasha", "pratyantar_dasha"):
        period = current.get(key)
        if period:
            lord = period.get("lord")
            if lord:
                scores[lord] = scores.get(lord, 0.0) + 0.25

    if analysis_input.lal_kitab:
        for finding in analysis_input.lal_kitab.get("dosh_findings", []):
            if not finding.get("is_present"):
                continue
            for planet in finding.get("planets_involved", []):
                scores[planet] = scores.get(planet, 0.0) + finding.get("strength", 0.4)

    for planet, impact in _transit_natal_impacts(analysis_input.transits).items():
        scores[planet] = scores.get(planet, 0.0) + impact

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return tuple(planet for planet, score in ranked if score >= 0.25)


def rank_root_causes(analysis_input) -> tuple:
    from astro_intelligence.types import RankedCause

    scores: dict[str, list[str]] = {}

    for dosha in analysis_input.doshas.get("present_doshas", []):
        for planet in dosha.get("planets_involved", []):
            scores.setdefault(planet, []).append(
                f"Dosha {dosha.get('dosha_id')} severity {dosha.get('severity', 0)}."
            )

    if analysis_input.problem_analysis:
        for planet in analysis_input.problem_analysis.get("planets", {}).get("primary", []):
            scores.setdefault(planet, []).append("Primary planet in problem mapping.")

    current = analysis_input.dasha.get("current", {})
    for key in ("mahadasha", "antardasha"):
        period = current.get(key)
        if period and period.get("lord"):
            scores.setdefault(period["lord"], []).append(f"Active {key} lord.")

    ranked_values = []
    for planet, reasons in scores.items():
        severity = min(1.0, 0.2 * len(reasons) + (0.3 if planet in MALEFICS else 0.1))
        ranked_values.append(
            RankedCause(planet=planet, severity=round(severity, 3), reasons=tuple(reasons))
        )

    ranked_values.sort(key=lambda item: item.severity, reverse=True)
    return tuple(ranked_values)


def _transit_natal_impacts(transits: dict[str, Any]) -> dict[str, float]:
    impacts: dict[str, float] = {}
    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = transits.get(key, {})
        for impact in section.get("natal_impacts", []):
            planet = section.get("planet", key.capitalize())
            if key == "rahu":
                planet = "Rahu"
            elif key == "ketu":
                planet = "Ketu"
            else:
                planet = section.get("planet", planet)
            impacts[planet] = impacts.get(planet, 0.0) + impact.get("strength", 0.3)
    return impacts
