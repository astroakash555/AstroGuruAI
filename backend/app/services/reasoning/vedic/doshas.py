"""Classical Vedic dosha detection."""

from __future__ import annotations

from backend.app.services.reasoning.vedic.constants import (
    DEBILITATION_SIGNS,
    DUSTHANA_HOUSES,
    EXALTATION_SIGNS,
    KAAL_SARP_PLANETS,
    KAAL_SARP_TYPES,
    KEMADRUMA_EXCLUDED_FROM_FLANKS,
    KENDRA_HOUSES,
    MANGAL_DOSHA_HOUSES,
    OWN_SIGNS,
    ObservationCategory,
    VedicChartContext,
    VedicObservation,
    angular_separation,
    house_distance,
    make_observation,
)


def detect_doshas(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    """Run all supported dosha detectors and return present-dosha observations."""
    detectors = (
        _detect_manglik,
        _detect_kaal_sarp,
        _detect_pitra,
        _detect_guru_chandal,
        _detect_kemadruma,
    )
    observations: list[VedicObservation] = []
    for detector in detectors:
        result = detector(context)
        if result is not None:
            observations.append(result)
    return tuple(observations)


def _detect_manglik(context: VedicChartContext) -> VedicObservation | None:
    if not context.has_planet("Mars"):
        return None

    mars_house = context.house_of_planet("Mars")
    moon_house = context.house_of_planet("Moon")
    from_lagna = mars_house in MANGAL_DOSHA_HOUSES
    from_moon = _mars_sensitive_from_reference(context, moon_house)

    if not from_lagna and not from_moon:
        return None

    mitigating = _manglik_mitigations(context)
    severity = 0.8 if from_lagna and from_moon else 0.65
    severity -= min(len(mitigating) * 0.08, 0.35)

    explanation = (
        "Mars occupies marriage-sensitive houses, indicating Manglik Dosha "
        "linked to marital friction or delay."
    )
    if from_lagna:
        explanation += f" Mars is in house {mars_house} from lagna."
    if from_moon:
        explanation += f" Mars is sensitive relative to Moon in house {moon_house}."
    if mitigating:
        explanation += f" Mitigations: {', '.join(mitigating)}."

    return make_observation(
        observation_id="dosha-manglik",
        category=ObservationCategory.DOSHA,
        title="Manglik Dosha",
        explanation=explanation,
        affected_planets=("Mars",),
        affected_houses=(mars_house,),
        severity=severity,
        confidence=0.88 if not mitigating else 0.78,
        metadata={
            "from_lagna": from_lagna,
            "from_moon": from_moon,
            "mitigating_factors": mitigating,
        },
    )


def _mars_sensitive_from_reference(context: VedicChartContext, reference_house: int) -> bool:
    mars_house = context.house_of_planet("Mars")
    for sensitive in MANGAL_DOSHA_HOUSES:
        target = ((reference_house + sensitive - 2) % 12) + 1
        if mars_house == target:
            return True
    return False


def _manglik_mitigations(context: VedicChartContext) -> list[str]:
    factors: list[str] = []
    mars_sign = context.sign_of_planet("Mars")

    if mars_sign in OWN_SIGNS.get("Mars", ()):
        factors.append("Mars in own sign")
    if mars_sign == EXALTATION_SIGNS["Mars"]:
        factors.append("Mars exalted")
    if context.has_planet("Jupiter"):
        if context.has_aspect("Jupiter", "Mars"):
            factors.append("Jupiter aspects Mars")
        if context.planets_in_same_sign("Mars", "Jupiter"):
            factors.append("Mars conjoined with Jupiter")
    return factors


def _detect_kaal_sarp(context: VedicChartContext) -> VedicObservation | None:
    if not context.has_planet("Rahu") or not context.has_planet("Ketu"):
        return None

    rahu = context.get_planet("Rahu")
    ketu = context.get_planet("Ketu")
    enclosed = _planets_enclosed_by_nodes(context, rahu.longitude, ketu.longitude)

    if len(enclosed) != len(KAAL_SARP_PLANETS):
        return None

    rahu_house = rahu.house
    subtype = KAAL_SARP_TYPES.get(rahu_house, "Unknown")

    return make_observation(
        observation_id="dosha-kaal-sarp",
        category=ObservationCategory.DOSHA,
        title="Kaal Sarp Dosha",
        explanation=(
            "All seven classical grahas lie between the Rahu-Ketu axis, forming "
            f"Kaal Sarp Dosha ({subtype} subtype with Rahu in house {rahu_house})."
        ),
        affected_planets=("Rahu", "Ketu", *enclosed),
        affected_houses=(rahu_house, ketu.house),
        severity=0.9,
        confidence=0.92,
        metadata={"subtype": subtype, "enclosed_planets": enclosed},
    )


def _planets_enclosed_by_nodes(
    context: VedicChartContext,
    rahu_longitude: float,
    ketu_longitude: float,
) -> tuple[str, ...]:
    enclosed: list[str] = []
    for planet_name in KAAL_SARP_PLANETS:
        if not context.has_planet(planet_name):
            continue
        planet_lon = context.get_planet(planet_name).longitude % 360.0
        if _is_on_rahu_ketu_arc(planet_lon, rahu_longitude % 360.0, ketu_longitude % 360.0):
            enclosed.append(planet_name)
    return tuple(enclosed)


def _is_on_rahu_ketu_arc(longitude: float, rahu: float, ketu: float) -> bool:
    forward_span = (ketu - rahu + 360.0) % 360.0
    reverse_span = (rahu - ketu + 360.0) % 360.0

    if forward_span <= 180.0:
        arc_start, span = rahu, forward_span
    else:
        arc_start, span = ketu, reverse_span

    offset = (longitude - arc_start + 360.0) % 360.0
    return 0.0 <= offset <= span


def _detect_pitra(context: VedicChartContext) -> VedicObservation | None:
    ninth_lord = context.house_lord(9)
    ninth_lord_house = context.house_of_planet(ninth_lord)

    triggers = {
        "sun_conjunct_rahu": context.has_planet("Rahu") and context.planets_in_same_sign("Sun", "Rahu"),
        "sun_conjunct_ketu": context.has_planet("Ketu") and context.planets_in_same_sign("Sun", "Ketu"),
        "rahu_in_9th_house": context.has_planet("Rahu") and context.house_of_planet("Rahu") == 9,
        "ketu_in_9th_house": context.has_planet("Ketu") and context.house_of_planet("Ketu") == 9,
        "ninth_lord_in_dusthana": ninth_lord_house in DUSTHANA_HOUSES,
        "saturn_in_9th_house": context.house_of_planet("Saturn") == 9,
        "sun_in_dusthana": context.house_of_planet("Sun") in DUSTHANA_HOUSES,
        "ninth_lord_with_nodes": (
            (context.has_planet("Rahu") and context.planets_in_same_sign(ninth_lord, "Rahu"))
            or (context.has_planet("Ketu") and context.planets_in_same_sign(ninth_lord, "Ketu"))
        ),
    }
    active = [label for label, met in triggers.items() if met]

    if not active:
        return None

    return make_observation(
        observation_id="dosha-pitra",
        category=ObservationCategory.DOSHA,
        title="Pitra Dosha",
        explanation=(
            "Ancestral karmic indicators are active through Sun, 9th house, or nodal "
            f"afflictions: {', '.join(label.replace('_', ' ') for label in active)}."
        ),
        affected_planets=("Sun", ninth_lord, "Saturn", "Rahu", "Ketu"),
        affected_houses=(9, context.house_of_planet("Sun"), ninth_lord_house),
        severity=min(0.55 + (0.08 * len(active)), 0.95),
        confidence=0.85,
        metadata={"active_triggers": active},
    )


def _detect_guru_chandal(context: VedicChartContext) -> VedicObservation | None:
    if not context.has_planet("Jupiter"):
        return None

    with_rahu = context.has_planet("Rahu") and context.planets_in_same_sign("Jupiter", "Rahu")
    with_ketu = context.has_planet("Ketu") and context.planets_in_same_sign("Jupiter", "Ketu")

    if not with_rahu and not with_ketu:
        return None

    node = "Rahu" if with_rahu else "Ketu"
    jupiter_house = context.house_of_planet("Jupiter")

    return make_observation(
        observation_id="dosha-guru-chandal",
        category=ObservationCategory.DOSHA,
        title="Guru Chandal Yoga",
        explanation=(
            f"Jupiter conjoins {node}, forming Guru Chandal Yoga which can distort "
            "wisdom, guidance, and ethical judgment until remedied."
        ),
        affected_planets=("Jupiter", node),
        affected_houses=(jupiter_house,),
        severity=0.74,
        confidence=0.9,
        metadata={"node": node},
    )


def _detect_kemadruma(context: VedicChartContext) -> VedicObservation | None:
    if not context.has_planet("Moon"):
        return None

    moon_house = context.house_of_planet("Moon")
    second_from_moon = ((moon_house + 1 - 1) % 12) + 1
    twelfth_from_moon = ((moon_house + 11 - 1) % 12) + 1

    flank_planets = {
        name
        for name in context.planets_in_house(second_from_moon) + context.planets_in_house(twelfth_from_moon)
        if name not in KEMADRUMA_EXCLUDED_FROM_FLANKS
    }
    kendra_from_moon = {
        name
        for name in context.planets
        if name not in KEMADRUMA_EXCLUDED_FROM_FLANKS
        and name != "Moon"
        and context.is_in_kendra_from(name, moon_house)
    }

    if flank_planets or kendra_from_moon:
        return None

    return make_observation(
        observation_id="dosha-kemadruma",
        category=ObservationCategory.DOSHA,
        title="Kemadruma Yoga",
        explanation=(
            "Moon lacks supporting planets in adjacent houses and kendras, forming "
            "Kemadruma Yoga associated with emotional isolation or self-reliance."
        ),
        affected_planets=("Moon",),
        affected_houses=(moon_house, second_from_moon, twelfth_from_moon),
        severity=0.7,
        confidence=0.86,
        metadata={
            "second_from_moon": second_from_moon,
            "twelfth_from_moon": twelfth_from_moon,
        },
    )
