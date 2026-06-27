"""KP event analysis framework."""

from __future__ import annotations

from kp_engine.constants import EVENT_TEMPLATES
from kp_engine.types import CuspalPoint, EventAnalysis, SignificatorSet


def analyze_events(
    cusps: tuple[CuspalPoint, ...],
    significators: tuple[SignificatorSet, ...],
) -> tuple[EventAnalysis, ...]:
    """Evaluate structured event templates against cusps and significators."""
    cusp_by_house = {item.house: item for item in cusps}
    sig_by_house = {item.house: item for item in significators}
    events: list[EventAnalysis] = []

    for template in EVENT_TEMPLATES:
        target_houses = tuple(template["target_houses"])  # type: ignore[index]
        primary_planets = tuple(template["primary_planets"])  # type: ignore[index]

        matched_significators: set[str] = set()
        matched_sub_lords: set[str] = set()
        evidence: list[str] = []

        for house in target_houses:
            sig = sig_by_house[house]
            for planet in primary_planets:
                if planet in sig.combined:
                    matched_significators.add(planet)
                    evidence.append(f"{planet} is significator for house {house}.")
            cusp = cusp_by_house[house]
            if cusp.sub_lord in primary_planets:
                matched_sub_lords.add(cusp.sub_lord)
                evidence.append(f"House {house} cusp sub lord is {cusp.sub_lord}.")

        support_score = _event_support_score(
            matched_significators,
            matched_sub_lords,
            primary_planets,
            target_houses,
        )
        is_supported = support_score >= 0.45

        events.append(
            EventAnalysis(
                event_id=str(template["event_id"]),
                event_type=str(template["event_type"]),
                target_houses=target_houses,
                is_supported=is_supported,
                support_score=round(support_score, 3),
                significators_matched=tuple(sorted(matched_significators)),
                cusp_sub_lords_matched=tuple(sorted(matched_sub_lords)),
                evidence=tuple(evidence),
            )
        )

    return tuple(events)


def _event_support_score(
    matched_significators: set[str],
    matched_sub_lords: set[str],
    primary_planets: tuple[str, ...],
    target_houses: tuple[int, ...],
) -> float:
    score = 0.0
    if matched_significators:
        score += 0.35 * (len(matched_significators) / max(len(primary_planets), 1))
    if matched_sub_lords:
        score += 0.35 * (len(matched_sub_lords) / max(len(target_houses), 1))
    if matched_significators and matched_sub_lords:
        score += 0.15
    return min(score, 1.0)
