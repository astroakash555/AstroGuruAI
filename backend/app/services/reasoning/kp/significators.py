"""KP house significator analysis for the reasoning intelligence layer."""

from __future__ import annotations

from kp_engine.lords import get_star_lord

from backend.app.services.reasoning.kp.constants import SIGNIFICATOR_LEVELS, KPObservationCategory, lord_of_sign
from backend.app.services.reasoning.kp.models import (
    KPChartContext,
    KPSignificatorRecord,
    ReasoningObservation,
    make_observation,
)


def build_significators(context: KPChartContext) -> tuple[KPSignificatorRecord, ...]:
    """Compute KP significator levels A-D for all twelve houses."""
    planet_longitudes = {name: planet.longitude for name, planet in context.planets.items()}
    records: list[KPSignificatorRecord] = []

    for house in range(1, 13):
        level_a = _occupants(house, context)
        level_b = _planets_in_star_of_occupants(level_a, planet_longitudes)
        house_lord = lord_of_sign((context.lagna_sign_index + house - 1) % 12)
        level_c = _planets_in_star_of(house_lord, planet_longitudes)
        level_d = (house_lord,) if house_lord in context.planets else ()
        combined = tuple(dict.fromkeys(level_a + level_b + level_c + level_d))
        records.append(
            KPSignificatorRecord(
                house=house,
                level_a=level_a,
                level_b=level_b,
                level_c=level_c,
                level_d=level_d,
                combined=combined,
            )
        )

    return tuple(records)


def analyze_significators(context: KPChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for house significator chains."""
    observations: list[ReasoningObservation] = []

    for record in context.significators:
        observations.append(
            make_observation(
                observation_id=f"kp-significator-house-{record.house:02d}",
                category=KPObservationCategory.SIGNIFICATOR,
                title=f"House {record.house} Significators",
                explanation=(
                    f"House {record.house} significators are "
                    f"A={', '.join(record.level_a) or 'none'}, "
                    f"B={', '.join(record.level_b) or 'none'}, "
                    f"C={', '.join(record.level_c) or 'none'}, "
                    f"D={', '.join(record.level_d) or 'none'}."
                ),
                affected_planets=record.combined,
                affected_houses=(record.house,),
                severity=min(0.45 + (0.05 * len(record.combined)), 0.8),
                confidence=0.9,
                metadata={
                    level: getattr(record, level)
                    for level in SIGNIFICATOR_LEVELS
                },
            )
        )

        if not record.combined:
            observations.append(
                make_observation(
                    observation_id=f"kp-significator-house-{record.house:02d}-empty",
                    category=KPObservationCategory.SIGNIFICATOR,
                    title=f"House {record.house} Weak Significator Chain",
                    explanation=(
                        f"No graha significators were derived for house {record.house}; "
                        "event judgment should rely on cusp sub lords and ruling planets."
                    ),
                    affected_planets=record.level_d,
                    affected_houses=(record.house,),
                    severity=0.62,
                    confidence=0.86,
                    metadata={"combined_count": 0},
                )
            )

    return tuple(observations)


def _occupants(house: int, context: KPChartContext) -> tuple[str, ...]:
    return tuple(
        name
        for name, planet in context.planets.items()
        if planet.house == house
    )


def _planets_in_star_of(reference: str, longitudes: dict[str, float]) -> tuple[str, ...]:
    if reference not in longitudes:
        return tuple()
    target_star = get_star_lord(longitudes[reference])
    return tuple(
        name
        for name, longitude in longitudes.items()
        if get_star_lord(longitude) == target_star
    )


def _planets_in_star_of_occupants(
    occupants: tuple[str, ...],
    longitudes: dict[str, float],
) -> tuple[str, ...]:
    matched: list[str] = []
    for occupant in occupants:
        matched.extend(_planets_in_star_of(occupant, longitudes))
    return tuple(dict.fromkeys(matched))
