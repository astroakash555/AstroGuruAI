"""Classical Vedic yoga detection."""

from __future__ import annotations

from backend.app.services.reasoning.vedic.constants import (
    COMBUSTION_ORBS,
    DEBILITATION_SIGNS,
    DHANA_HOUSES,
    DUSTHANA_HOUSES,
    EXALTATION_SIGNS,
    KENDRA_HOUSES,
    OWN_SIGNS,
    PANCH_MAHAPURUSHA_YOGAS,
    TRIKONA_HOUSES,
    ObservationCategory,
    VedicChartContext,
    VedicObservation,
    angular_separation,
    lord_of_sign,
    make_observation,
)


def detect_yogas(context: VedicChartContext) -> tuple[VedicObservation, ...]:
    """Run all supported yoga detectors and return present-yoga observations."""
    detectors = (
        _detect_gaj_kesari,
        _detect_budhaditya,
        _detect_neecha_bhanga,
        _detect_vipreet_raj,
        _detect_panch_mahapurusha,
        _detect_raj_yoga,
        _detect_dhana_yoga,
    )
    observations: list[VedicObservation] = []
    for detector in detectors:
        result = detector(context)
        if result is not None:
            observations.append(result)
    return tuple(observations)


def _detect_gaj_kesari(context: VedicChartContext) -> VedicObservation | None:
    if not context.has_planet("Moon") or not context.has_planet("Jupiter"):
        return None

    moon_house = context.house_of_planet("Moon")
    jupiter_from_moon = context.is_in_kendra_from("Jupiter", moon_house)
    jupiter_from_lagna = context.is_in_kendra_from("Jupiter", 1)

    if not jupiter_from_moon:
        return None

    confidence = 0.92 if jupiter_from_lagna else 0.82
    return make_observation(
        observation_id="yoga-gaj-kesari",
        category=ObservationCategory.YOGA,
        title="Gaj Kesari Yoga",
        explanation=(
            "Jupiter occupies a kendra from the Moon, forming Gaj Kesari Yoga "
            "which supports wisdom, reputation, and prosperity."
            + (" Jupiter also occupies a kendra from lagna, strengthening the yoga." if jupiter_from_lagna else "")
        ),
        affected_planets=("Moon", "Jupiter"),
        affected_houses=(moon_house, context.house_of_planet("Jupiter")),
        severity=0.78,
        confidence=confidence,
        metadata={"jupiter_kendra_from_lagna": jupiter_from_lagna},
    )


def _detect_budhaditya(context: VedicChartContext) -> VedicObservation | None:
    if not context.has_planet("Sun") or not context.has_planet("Mercury"):
        return None

    if not context.planets_in_same_sign("Sun", "Mercury"):
        return None

    sun = context.get_planet("Sun")
    mercury = context.get_planet("Mercury")
    separation = angular_separation(sun.longitude, mercury.longitude)
    combust = separation <= COMBUSTION_ORBS["Mercury"]

    return make_observation(
        observation_id="yoga-budhaditya",
        category=ObservationCategory.YOGA,
        title="Budhaditya Yoga",
        explanation=(
            "Sun and Mercury share the same sign, forming Budhaditya Yoga for "
            "intelligence and articulate expression."
            + (" Mercury is combust; yoga is present with reduced strength." if combust else "")
        ),
        affected_planets=("Sun", "Mercury"),
        affected_houses=(sun.house, mercury.house),
        severity=0.72 if not combust else 0.58,
        confidence=0.9 if not combust else 0.75,
        metadata={"separation_degrees": round(separation, 4), "mercury_combust": combust},
    )


def _detect_neecha_bhanga(context: VedicChartContext) -> VedicObservation | None:
    cancellations: list[tuple[str, list[str]]] = []

    for planet_name, deb_sign in DEBILITATION_SIGNS.items():
        if not context.has_planet(planet_name):
            continue
        if context.sign_of_planet(planet_name) != deb_sign:
            continue

        reasons = _neecha_bhanga_reasons(context, planet_name)
        if reasons:
            cancellations.append((planet_name, reasons))

    if not cancellations:
        return None

    planets = tuple(planet for planet, _ in cancellations)
    houses = tuple(sorted({context.house_of_planet(planet) for planet in planets}))
    evidence = "; ".join(f"{planet}: {', '.join(reasons)}" for planet, reasons in cancellations)

    return make_observation(
        observation_id="yoga-neecha-bhanga",
        category=ObservationCategory.YOGA,
        title="Neecha Bhanga Raj Yoga",
        explanation=(
            "Debilitation of one or more grahas is cancelled, indicating potential "
            f"elevation after early struggle. Factors: {evidence}."
        ),
        affected_planets=planets,
        affected_houses=houses,
        severity=min(0.7 + (0.08 * len(cancellations)), 0.95),
        confidence=0.88,
        metadata={"cancellations": {planet: reasons for planet, reasons in cancellations}},
    )


def _neecha_bhanga_reasons(context: VedicChartContext, planet_name: str) -> list[str]:
    reasons: list[str] = []
    deb_sign = DEBILITATION_SIGNS[planet_name]
    deb_lord = lord_of_sign(deb_sign)
    exalt_sign = EXALTATION_SIGNS.get(planet_name)
    exalt_lord = lord_of_sign(exalt_sign) if exalt_sign is not None else None

    if context.is_in_kendra_from(planet_name, 1):
        reasons.append("debilitated planet in kendra from lagna")
    if context.is_in_kendra_from(deb_lord, 1):
        reasons.append("dispositor in kendra from lagna")

    moon_house = context.house_of_planet("Moon")
    if context.is_in_kendra_from(planet_name, moon_house):
        reasons.append("debilitated planet in kendra from Moon")
    if context.is_in_kendra_from(deb_lord, moon_house):
        reasons.append("dispositor in kendra from Moon")

    if exalt_lord and context.has_aspect(exalt_lord, planet_name):
        reasons.append(f"aspect from exaltation lord {exalt_lord}")
    if context.planets_in_same_sign(planet_name, deb_lord):
        reasons.append("debilitated planet with dispositor in same sign")
    if context.house_of_planet(deb_lord) in KENDRA_HOUSES:
        reasons.append("dispositor placed in kendra house")

    return reasons


def _detect_vipreet_raj(context: VedicChartContext) -> VedicObservation | None:
    matches: list[tuple[int, str, int, str]] = []

    for house in DUSTHANA_HOUSES:
        lord = context.house_lord(house)
        lord_house = context.house_of_planet(lord)
        if lord_house in DUSTHANA_HOUSES:
            subtype = _vipreet_subtype(house, lord_house)
            matches.append((house, lord, lord_house, subtype))

    if not matches:
        return None

    subtypes = [match[3] for match in matches]
    return make_observation(
        observation_id="yoga-vipreet-raj",
        category=ObservationCategory.YOGA,
        title="Vipreet Raj Yoga",
        explanation=(
            "Dusthana lords occupy dusthana houses, forming Vipreet Raj Yoga "
            f"patterns: {', '.join(subtypes)}."
        ),
        affected_planets=tuple(sorted({match[1] for match in matches})),
        affected_houses=tuple(sorted({match[2] for match in matches})),
        severity=min(0.65 + (0.1 * len(matches)), 0.92),
        confidence=0.86,
        metadata={"subtypes": subtypes},
    )


def _vipreet_subtype(source_house: int, lord_house: int) -> str:
    if source_house == 6 and lord_house == 6:
        return "Harsha Yoga"
    if source_house == 8 and lord_house == 8:
        return "Sarala Yoga"
    if source_house == 12 and lord_house == 12:
        return "Vimala Yoga"
    return f"{source_house}th lord in house {lord_house}"


def _detect_panch_mahapurusha(context: VedicChartContext) -> VedicObservation | None:
    present: list[str] = []

    for yoga_key, spec in PANCH_MAHAPURUSHA_YOGAS.items():
        planet_name = str(spec["planet"])
        if not context.has_planet(planet_name):
            continue

        sign_index = context.sign_of_planet(planet_name)
        in_own_or_exalt = sign_index in OWN_SIGNS.get(planet_name, ()) or sign_index == EXALTATION_SIGNS.get(
            planet_name, -1
        )
        in_kendra = context.house_of_planet(planet_name) in KENDRA_HOUSES

        if in_own_or_exalt and in_kendra:
            present.append(str(spec["name"]))

    if not present:
        return None

    planets = tuple(
        str(PANCH_MAHAPURUSHA_YOGAS[key]["planet"])
        for key in PANCH_MAHAPURUSHA_YOGAS
        if str(PANCH_MAHAPURUSHA_YOGAS[key]["name"]) in present
    )
    houses = tuple(sorted({context.house_of_planet(planet) for planet in planets}))

    return make_observation(
        observation_id="yoga-panch-mahapurusha",
        category=ObservationCategory.YOGA,
        title="Panch Mahapurusha Yoga",
        explanation=(
            "One or more Panch Mahapurusha yogas are present: "
            f"{', '.join(present)}. These indicate exceptional planetary strength."
        ),
        affected_planets=planets,
        affected_houses=houses,
        severity=min(0.75 + (0.05 * len(present)), 0.95),
        confidence=0.9,
        metadata={"present_yogas": present},
    )


def _detect_raj_yoga(context: VedicChartContext) -> VedicObservation | None:
    kendra_lords = {context.house_lord(house) for house in KENDRA_HOUSES}
    trikona_lords = {context.house_lord(house) for house in TRIKONA_HOUSES}
    links: list[str] = []

    for kendra_lord in kendra_lords:
        for trikona_lord in trikona_lords:
            if kendra_lord == trikona_lord:
                continue
            relation = _lord_relation(context, kendra_lord, trikona_lord)
            if relation:
                links.append(f"{kendra_lord}-{trikona_lord} ({relation})")

    if not links:
        return None

    planets = tuple(sorted({part for link in links for part in link.split(" (")[0].split("-")}))
    return make_observation(
        observation_id="yoga-raj",
        category=ObservationCategory.YOGA,
        title="Raj Yoga",
        explanation=(
            "Kendra and trikona lords are connected, forming Raj Yoga for authority "
            f"and recognition. Links: {'; '.join(links[:5])}."
        ),
        affected_planets=planets,
        affected_houses=_houses_for_lords(context, planets),
        severity=min(0.72 + (0.04 * len(links)), 0.94),
        confidence=0.87,
        metadata={"links": links},
    )


def _detect_dhana_yoga(context: VedicChartContext) -> VedicObservation | None:
    second_lord = context.house_lord(2)
    eleventh_lord = context.house_lord(11)
    links: list[str] = []

    relation = _lord_relation(context, second_lord, eleventh_lord)
    if relation:
        links.append(f"2nd-11th lords linked via {relation}")

    if context.house_of_planet(second_lord) == 11:
        links.append("2nd lord in 11th house")
    if context.house_of_planet(eleventh_lord) == 2:
        links.append("11th lord in 2nd house")

    for house in DHANA_HOUSES:
        lord = context.house_lord(house)
        for trikona_house in TRIKONA_HOUSES:
            trikona_lord = context.house_lord(trikona_house)
            relation = _lord_relation(context, lord, trikona_lord)
            if relation:
                links.append(f"dhana lord {lord} linked to trikona lord {trikona_lord} via {relation}")

    if not links:
        return None

    return make_observation(
        observation_id="yoga-dhana",
        category=ObservationCategory.YOGA,
        title="Dhana Yoga",
        explanation=(
            "Wealth-oriented house lords are connected, forming Dhana Yoga for "
            f"financial growth. Indicators: {'; '.join(links[:6])}."
        ),
        affected_planets=(second_lord, eleventh_lord),
        affected_houses=(2, 11, context.house_of_planet(second_lord), context.house_of_planet(eleventh_lord)),
        severity=min(0.68 + (0.05 * len(links)), 0.9),
        confidence=0.84,
        metadata={"links": links},
    )


def _lord_relation(context: VedicChartContext, first: str, second: str) -> str | None:
    if context.planets_in_same_sign(first, second):
        return "conjunction"
    if context.has_aspect(first, second) or context.has_aspect(second, first):
        return "aspect"
    first_sign = context.sign_of_planet(first)
    second_sign = context.sign_of_planet(second)
    if lord_of_sign(first_sign) == second and lord_of_sign(second_sign) == first:
        return "mutual_reception"
    return None


def _houses_for_lords(context: VedicChartContext, planets: tuple[str, ...]) -> tuple[int, ...]:
    return tuple(sorted({context.house_of_planet(planet) for planet in planets}))
