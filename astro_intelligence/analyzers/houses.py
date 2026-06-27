"""Affected house detection."""

from __future__ import annotations


def detect_affected_houses(analysis_input) -> tuple[int, ...]:
    """Detect houses affected across analysis sections."""
    houses: set[int] = set()

    if analysis_input.problem_analysis:
        mapping = analysis_input.problem_analysis.get("houses", {})
        for key in ("primary", "secondary", "supporting"):
            houses.update(mapping.get(key, []))

    for dosha in analysis_input.doshas.get("present_doshas", []):
        houses.update(dosha.get("houses_involved", []))

    for yoga in analysis_input.yogas.get("present_yogas", []):
        if yoga.get("strength", 0) >= 0.7:
            continue
        houses.update(yoga.get("houses_involved", []))

    if analysis_input.lal_kitab:
        for finding in analysis_input.lal_kitab.get("dosh_findings", []):
            if finding.get("is_present"):
                houses.update(finding.get("houses_involved", []))

    if analysis_input.kp_analysis:
        for event in analysis_input.kp_analysis.get("events", []):
            if not event.get("is_supported"):
                houses.update(event.get("target_houses", []))

    for key in ("saturn", "jupiter", "rahu", "ketu"):
        section = analysis_input.transits.get(key, {})
        current = section.get("current") or {}
        house = current.get("house_from_lagna")
        if house in {6, 8, 12}:
            houses.add(house)

    return tuple(sorted(houses))
