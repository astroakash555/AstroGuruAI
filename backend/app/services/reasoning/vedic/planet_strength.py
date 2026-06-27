"""Planetary dignity, combustion, and strength analysis."""

from __future__ import annotations

from backend.app.services.reasoning.vedic.constants import (
    COMBUSTION_ORBS,
    DEBILITATION_SIGNS,
    DignityState,
    EXALTATION_SIGNS,
    MOOLATRIKONA_SIGNS,
    NATURAL_ENEMIES,
    NATURAL_FRIENDS,
    OWN_SIGNS,
    ObservationCategory,
    VedicChartContext,
    VedicObservation,
    angular_separation,
    lord_of_sign,
    make_observation,
)


def analyze_planet_strengths(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    """Evaluate dignity, combustion, and retrograde status for every graha."""
    observations: list[VedicObservation] = []
    for planet_name, planet in context.planets.items():
        observations.extend(_analyze_single_planet(context, planet_name, planet.name))
    return tuple(observations)


def _analyze_single_planet(
    context: VedicChartContext,
    planet_name: str,
    _display_name: str,
) -> tuple[VedicObservation, ...]:
    planet = context.get_planet(planet_name)
    sign_index = planet.sign_index
    observations: list[VedicObservation] = []

    dignity = classify_dignity(planet_name, sign_index)
    if dignity != DignityState.NEUTRAL_SIGN:
        severity, confidence = _dignity_scores(dignity)
        observations.append(
            make_observation(
                observation_id=f"planet-strength-{planet_name.lower()}-dignity",
                category=ObservationCategory.PLANET_STRENGTH,
                title=f"{planet_name} in {dignity.value.replace('_', ' ').title()}",
                explanation=(
                    f"{planet_name} occupies {planet.sign_name} "
                    f"(house {planet.house}), classified as {dignity.value.replace('_', ' ')}."
                ),
                affected_planets=(planet_name,),
                affected_houses=(planet.house,),
                severity=severity,
                confidence=confidence,
                metadata={"dignity": dignity.value, "sign_index": sign_index},
            )
        )

    if planet.is_retrograde:
        observations.append(
            make_observation(
                observation_id=f"planet-strength-{planet_name.lower()}-retrograde",
                category=ObservationCategory.PLANET_STRENGTH,
                title=f"{planet_name} Retrograde",
                explanation=(
                    f"{planet_name} is retrograde in {planet.sign_name} "
                    f"(house {planet.house}), intensifying karmic review of its significations."
                ),
                affected_planets=(planet_name,),
                affected_houses=(planet.house,),
                severity=0.55,
                confidence=0.95,
                metadata={"is_retrograde": True},
            )
        )

    if planet_name in COMBUSTION_ORBS and context.has_planet("Sun") and planet_name != "Sun":
        combustion = detect_combustion(context, planet_name)
        if combustion is not None:
            observations.append(combustion)

    return tuple(observations)


def classify_dignity(planet_name: str, sign_index: int) -> DignityState:
    """Classify a planet's dignity in its current sign."""
    if planet_name not in EXALTATION_SIGNS:
        return DignityState.NEUTRAL_SIGN

    if sign_index == EXALTATION_SIGNS[planet_name]:
        return DignityState.EXALTATION
    if sign_index == DEBILITATION_SIGNS[planet_name]:
        return DignityState.DEBILITATION
    if sign_index in OWN_SIGNS.get(planet_name, ()):
        return DignityState.OWN_SIGN
    if sign_index == MOOLATRIKONA_SIGNS.get(planet_name, -1):
        return DignityState.MOOLATRIKONA

    sign_lord = lord_of_sign(sign_index)
    friends = NATURAL_FRIENDS.get(planet_name, frozenset())
    enemies = NATURAL_ENEMIES.get(planet_name, frozenset())

    if sign_lord in friends:
        return DignityState.FRIENDLY_SIGN
    if sign_lord in enemies:
        return DignityState.ENEMY_SIGN
    return DignityState.NEUTRAL_SIGN


def detect_combustion(context: VedicChartContext, planet_name: str) -> VedicObservation | None:
    """Return a combustion observation when a graha is within the Sun's orb."""
    sun = context.get_planet("Sun")
    planet = context.get_planet(planet_name)
    orb = COMBUSTION_ORBS[planet_name]
    separation = angular_separation(sun.longitude, planet.longitude)

    if separation > orb:
        return None

    strength_factor = 1.0 - (separation / orb)
    return make_observation(
        observation_id=f"planet-strength-{planet_name.lower()}-combust",
        category=ObservationCategory.PLANET_STRENGTH,
        title=f"{planet_name} Combust",
        explanation=(
            f"{planet_name} is within {separation:.2f}° of the Sun "
            f"(combustion orb {orb:.0f}°), reducing independent expression."
        ),
        affected_planets=(planet_name, "Sun"),
        affected_houses=(planet.house, sun.house),
        severity=round(0.45 + (0.45 * strength_factor), 4),
        confidence=0.9,
        metadata={"separation_degrees": round(separation, 4), "orb_degrees": orb},
    )


def _dignity_scores(dignity: DignityState) -> tuple[float, float]:
    """Map dignity states to severity and confidence scores."""
    mapping: dict[DignityState, tuple[float, float]] = {
        DignityState.EXALTATION: (0.85, 0.95),
        DignityState.MOOLATRIKONA: (0.8, 0.92),
        DignityState.OWN_SIGN: (0.75, 0.9),
        DignityState.FRIENDLY_SIGN: (0.55, 0.82),
        DignityState.NEUTRAL_SIGN: (0.35, 0.7),
        DignityState.ENEMY_SIGN: (0.65, 0.85),
        DignityState.DEBILITATION: (0.8, 0.93),
    }
    return mapping[dignity]
