"""Transit event windows and domain activation."""

from __future__ import annotations

from backend.app.services.reasoning.transit.constants import (
    DOMAIN_ACTIVATION_THRESHOLD,
    DOMAIN_TEMPLATES,
    EVENT_WINDOW_SUPPORT_THRESHOLD,
    TransitObservationCategory,
)
from backend.app.services.reasoning.transit.models import (
    ReasoningObservation,
    TransitChartContext,
    TransitEventWindowRecord,
    make_observation,
)


def analyze_domain_activation(context: TransitChartContext) -> tuple[ReasoningObservation, ...]:
    """Score life-domain activation from current transits."""
    observations: list[ReasoningObservation] = []

    for template in DOMAIN_TEMPLATES:
        domain_id = str(template["domain_id"])
        display_name = str(template["display_name"])
        target_houses = tuple(template["target_houses"])  # type: ignore[index]
        primary_planets = tuple(template["primary_planets"])  # type: ignore[index]

        score, matched_planets, matched_houses, evidence = _domain_activation_score(
            context,
            target_houses,
            primary_planets,
        )
        is_active = score >= DOMAIN_ACTIVATION_THRESHOLD

        observations.append(
            make_observation(
                observation_id=f"transit-domain-{domain_id}",
                category=TransitObservationCategory.DOMAIN,
                title=f"{display_name} Domain {'Activated' if is_active else 'Moderate'} by Transit",
                explanation=(
                    f"The {display_name.lower()} domain scores {score:.2f} under current "
                    f"transits. {'; '.join(evidence) if evidence else 'No strong transit linkage detected.'}"
                ),
                affected_planets=matched_planets,
                affected_houses=matched_houses,
                severity=score,
                confidence=0.88 if is_active else 0.80,
                metadata={
                    "domain_id": domain_id,
                    "domain_name": display_name,
                    "activation_score": score,
                    "is_active": is_active,
                    "target_houses": target_houses,
                    "primary_planets": primary_planets,
                    "evidence": evidence,
                },
            )
        )

    return tuple(observations)


def analyze_event_windows(context: TransitChartContext) -> tuple[TransitEventWindowRecord, ...]:
    """Derive structured event windows from transit domain activation."""
    records: list[TransitEventWindowRecord] = []

    for template in DOMAIN_TEMPLATES:
        domain_id = str(template["domain_id"])
        display_name = str(template["display_name"])
        target_houses = tuple(template["target_houses"])  # type: ignore[index]
        primary_planets = tuple(template["primary_planets"])  # type: ignore[index]

        for planet, transit in context.transits.items():
            score, _, _, evidence = _domain_activation_score(
                context,
                target_houses,
                primary_planets,
                focus_planet=planet,
            )
            if score < EVENT_WINDOW_SUPPORT_THRESHOLD:
                continue

            records.append(
                TransitEventWindowRecord(
                    window_id=f"{domain_id}-{planet.lower()}",
                    domain_id=domain_id,
                    domain_name=display_name,
                    planet=planet,
                    activation_score=score,
                    target_houses=target_houses,
                    evidence=evidence,
                )
            )

    return tuple(records)


def event_windows_to_observations(
    records: tuple[TransitEventWindowRecord, ...],
) -> tuple[ReasoningObservation, ...]:
    """Convert event window records into structured reasoning observations."""
    observations: list[ReasoningObservation] = []

    for record in records:
        observations.append(
            make_observation(
                observation_id=f"transit-event-{record.window_id}",
                category=TransitObservationCategory.EVENT_WINDOW,
                title=f"{record.domain_name} Transit Window via {record.planet}",
                explanation=(
                    f"A {record.domain_name.lower()} transit window is active through "
                    f"{record.planet} with activation score {record.activation_score:.2f}."
                ),
                affected_planets=(record.planet,),
                affected_houses=record.target_houses,
                severity=record.activation_score,
                confidence=0.86,
                metadata={
                    "window_id": record.window_id,
                    "domain_id": record.domain_id,
                    "domain_name": record.domain_name,
                    "planet": record.planet,
                    "activation_score": record.activation_score,
                    "evidence": record.evidence,
                },
            )
        )

    return tuple(observations)


def _domain_activation_score(
    context: TransitChartContext,
    target_houses: tuple[int, ...],
    primary_planets: tuple[str, ...],
    *,
    focus_planet: str | None = None,
) -> tuple[float, tuple[str, ...], tuple[int, ...], tuple[str, ...]]:
    score = 0.0
    matched_planets: set[str] = set()
    matched_houses: set[int] = set()
    evidence: list[str] = []

    transits = context.transits.items()
    if focus_planet is not None:
        if focus_planet not in context.transits:
            return 0.0, (), (), ()
        transits = ((focus_planet, context.transits[focus_planet]),)

    for planet, transit in transits:
        weight = 1.0 if focus_planet is None else 1.0
        if planet in primary_planets:
            score += 0.28 * weight
            matched_planets.add(planet)
            evidence.append(f"Transiting {planet} is a primary significator for this domain.")

        if transit.house_from_lagna is not None and transit.house_from_lagna in target_houses:
            score += 0.22 * weight
            matched_houses.add(transit.house_from_lagna)
            matched_planets.add(planet)
            evidence.append(
                f"Transiting {planet} crosses target house {transit.house_from_lagna} from lagna."
            )

        if transit.house_from_moon is not None and transit.house_from_moon in target_houses:
            score += 0.18 * weight
            matched_houses.add(transit.house_from_moon)
            matched_planets.add(planet)
            evidence.append(
                f"Transiting {planet} crosses target house {transit.house_from_moon} from Moon."
            )

    return (
        round(min(score, 1.0), 4),
        tuple(sorted(matched_planets)),
        tuple(sorted(matched_houses)),
        tuple(evidence),
    )
