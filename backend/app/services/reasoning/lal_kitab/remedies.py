"""Lal Kitab remedy generation for the reasoning layer."""

from __future__ import annotations

from backend.app.services.reasoning.lal_kitab.constants import REMEDY_TEMPLATES, LalKitabObservationCategory
from backend.app.services.reasoning.lal_kitab.models import (
    LalKitabChartContext,
    LalKitabRemedy,
    ReasoningObservation,
    make_observation,
)


def generate_remedies(
    context: LalKitabChartContext,
    observations: tuple[ReasoningObservation, ...],
) -> tuple[LalKitabRemedy, ...]:
    """Generate Lal Kitab remedies from active observations and chart patterns."""
    remedies: list[LalKitabRemedy] = []
    seen: set[str] = set()

    for observation in observations:
        remedy_keys = _remedy_keys_for_observation(observation, context)
        for remedy_key in remedy_keys:
            if remedy_key in seen:
                continue
            template = REMEDY_TEMPLATES.get(remedy_key)
            if template is None:
                continue
            seen.add(remedy_key)
            remedies.append(
                _build_remedy(
                    remedy_key=remedy_key,
                    template=template,
                    observation=observation,
                )
            )

    remedies.sort(key=lambda item: (-item.confidence, item.priority))
    return tuple(remedies)


def analyze_remedy_observations(
    remedies: tuple[LalKitabRemedy, ...],
) -> tuple[ReasoningObservation, ...]:
    """Convert generated remedies into fusion-compatible observations."""
    observations: list[ReasoningObservation] = []
    for remedy in remedies:
        observations.append(
            make_observation(
                observation_id=f"lk-remedy-{remedy.remedy_id}",
                category=LalKitabObservationCategory.REMEDY,
                title=remedy.title,
                explanation=remedy.explanation,
                affected_planets=remedy.affected_planets,
                affected_houses=remedy.affected_houses,
                severity=_priority_to_severity(remedy.priority),
                confidence=remedy.confidence,
                metadata={
                    "remedy_id": remedy.remedy_id,
                    "priority": remedy.priority,
                    "expected_duration": remedy.expected_duration,
                    "source_observation_ids": remedy.source_observation_ids,
                },
            )
        )
    return tuple(observations)


def _remedy_keys_for_observation(
    observation: ReasoningObservation,
    context: LalKitabChartContext,
) -> tuple[str, ...]:
    """Map an observation to remedy template keys."""
    keys: list[str] = []

    if observation.category == LalKitabObservationCategory.RIN:
        rin_id = observation.metadata.get("rin_id")
        if observation.metadata.get("is_present") and isinstance(rin_id, str):
            keys.append(rin_id)

    combination_id = observation.metadata.get("combination_id")
    if observation.category == LalKitabObservationCategory.COMBINATION and isinstance(combination_id, str):
        keys.append(combination_id)

    if observation.category == LalKitabObservationCategory.PLANET:
        planet = observation.metadata.get("planet")
        house = observation.affected_houses[0] if observation.affected_houses else None
        if planet == "Mars" and house == 8:
            keys.append("mars_eighth")
        if planet == "Saturn" and house == 7:
            keys.append("saturn_seventh")
        if planet == "Rahu" and house == 12:
            keys.append("rahu_twelfth")

    if observation.category == LalKitabObservationCategory.HOUSE:
        if observation.metadata.get("dusthana") and observation.severity >= 0.70:
            keys.append("general_planet_house")

    return tuple(dict.fromkeys(keys))


def _build_remedy(
    *,
    remedy_key: str,
    template: dict[str, object],
    observation: ReasoningObservation,
) -> LalKitabRemedy:
    """Build a typed remedy record from a template."""
    planets = tuple(template.get("planets") or observation.affected_planets)  # type: ignore[arg-type]
    houses = tuple(template.get("houses") or observation.affected_houses)  # type: ignore[arg-type]
    return LalKitabRemedy(
        remedy_id=remedy_key,
        title=str(template["title"]),
        explanation=str(template["explanation"]),
        priority=str(template["priority"]),
        expected_duration=str(template["expected_duration"]),
        affected_planets=planets,
        affected_houses=houses,
        confidence=round(float(template.get("confidence", observation.confidence)), 4),
        source_observation_ids=(observation.observation_id,),
    )


def _priority_to_severity(priority: str) -> float:
    """Map remedy priority to observation severity."""
    return {
        "high": 0.78,
        "medium": 0.62,
        "low": 0.48,
    }.get(priority, 0.55)
