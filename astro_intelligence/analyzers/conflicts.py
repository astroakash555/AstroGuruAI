"""Planetary conflict detection."""

from __future__ import annotations

from astro_intelligence.types import PlanetaryConflict

MALEFICS = frozenset({"Saturn", "Mars", "Rahu", "Ketu"})
BENEFICS = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})


def detect_planetary_conflicts(analysis_input) -> tuple[PlanetaryConflict, ...]:
    """Detect structured planetary conflicts from chart and timing sections."""
    conflicts: list[PlanetaryConflict] = []
    planets = {item["name"]: item for item in analysis_input.kundali.get("planets", [])}

    for malefic in MALEFICS:
        if malefic not in planets:
            continue
        malefic_house = planets[malefic].get("house")
        for benefic in BENEFICS:
            if benefic not in planets:
                continue
            benefic_house = planets[benefic].get("house")
            if malefic_house and benefic_house and malefic_house == benefic_house:
                conflicts.append(
                    PlanetaryConflict(
                        planets=(malefic, benefic),
                        conflict_type="malefic_benefic_conjunction",
                        severity=0.72,
                        evidence=(
                            f"{malefic} and {benefic} share house {malefic_house}.",
                        ),
                    )
                )

    for dosha in analysis_input.doshas.get("present_doshas", []):
        involved = dosha.get("planets_involved", [])
        if len(involved) >= 2:
            conflicts.append(
                PlanetaryConflict(
                    planets=tuple(involved[:2]),
                    conflict_type="dosha_pair",
                    severity=min(1.0, dosha.get("severity", 0.5)),
                    evidence=(f"Dosha {dosha.get('dosha_id')} links {', '.join(involved[:2])}.",),
                )
            )

    if analysis_input.lal_kitab:
        for finding in analysis_input.lal_kitab.get("dosh_findings", []):
            if not finding.get("is_present"):
                continue
            involved = finding.get("planets_involved", [])
            if len(involved) >= 2:
                conflicts.append(
                    PlanetaryConflict(
                        planets=tuple(involved[:2]),
                        conflict_type="lal_kitab_dosh_pair",
                        severity=finding.get("strength", 0.5),
                        evidence=(f"Lal Kitab finding {finding.get('finding_id')}.",),
                    )
                )

    return tuple(conflicts)
