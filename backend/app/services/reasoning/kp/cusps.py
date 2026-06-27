"""KP cuspal analysis for the reasoning intelligence layer."""

from __future__ import annotations

from kp_engine.lords import get_sub_lord

from backend.app.services.reasoning.kp.constants import KPObservationCategory, sign_name_from_longitude
from backend.app.services.reasoning.kp.models import KPCuspRecord, KPChartContext, ReasoningObservation, make_observation


def build_cusps(context: KPChartContext) -> tuple[KPCuspRecord, ...]:
    """Build cusp records from supplied house cusp longitudes."""
    if context.cusps:
        return context.cusps

    records: list[KPCuspRecord] = []
    for house in range(1, 13):
        sign_index = (context.lagna_sign_index + house - 1) % 12
        longitude = context.lagna_longitude + ((house - 1) * 30.0)
        _, star_lord, sub_lord = get_sub_lord(longitude)
        records.append(
            KPCuspRecord(
                house=house,
                longitude=longitude % 360.0,
                sign_name=sign_name_from_longitude(longitude),
                star_lord=star_lord,
                sub_lord=sub_lord,
            )
        )
    return tuple(records)


def analyze_cusps(context: KPChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit structured observations for bhava cusp star and sub lords."""
    observations: list[ReasoningObservation] = []

    for cusp in context.cusps:
        observations.append(
            make_observation(
                observation_id=f"kp-cusp-house-{cusp.house:02d}",
                category=KPObservationCategory.CUSP,
                title=f"House {cusp.house} Cuspal Sub Lord",
                explanation=(
                    f"House {cusp.house} cusp at {cusp.longitude:.2f}° ({cusp.sign_name}) "
                    f"has star lord {cusp.star_lord} and sub lord {cusp.sub_lord}."
                ),
                affected_planets=(cusp.star_lord, cusp.sub_lord),
                affected_houses=(cusp.house,),
                severity=0.64,
                confidence=0.92,
                metadata={
                    "longitude": round(cusp.longitude, 4),
                    "sign_name": cusp.sign_name,
                    "star_lord": cusp.star_lord,
                    "sub_lord": cusp.sub_lord,
                },
            )
        )

    grouped: dict[str, list[int]] = {}
    for cusp in context.cusps:
        grouped.setdefault(cusp.sub_lord, []).append(cusp.house)

    for sub_lord, houses in sorted(grouped.items()):
        if len(houses) < 2:
            continue
        observations.append(
            make_observation(
                observation_id=f"kp-cusp-sub-lord-{sub_lord.lower()}",
                category=KPObservationCategory.CUSP,
                title=f"{sub_lord} Cuspal Sub Lord Pattern",
                explanation=(
                    f"Sub lord {sub_lord} repeats on cusps of houses "
                    f"{', '.join(str(house) for house in sorted(houses))}."
                ),
                affected_planets=(sub_lord,),
                affected_houses=tuple(sorted(houses)),
                severity=min(0.6 + (0.07 * len(houses)), 0.88),
                confidence=0.87,
                metadata={"sub_lord": sub_lord, "houses": houses},
            )
        )

    return tuple(observations)
