"""Natal impact analysis for transiting grahas."""

from __future__ import annotations

from astrology_engine.transits.constants import (
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    PLANET_ASPECTS,
    SADE_SATI_HOUSES_FROM_MOON,
    TRANSIT_THEMES,
)
from astrology_engine.transits.types import NatalImpact, SignChangeEvent, TransitInput, TransitPlanetSnapshot


def analyze_natal_impacts(
    snapshot: TransitPlanetSnapshot,
    transit_input: TransitInput,
) -> tuple[NatalImpact, ...]:
    """Derive natal impact indicators for a transit snapshot."""
    impacts: list[NatalImpact] = []

    if snapshot.house_from_lagna in KENDRA_HOUSES:
        impacts.append(
            NatalImpact(
                impact_type="kendra_transit",
                description=f"{snapshot.planet} transiting kendra house {snapshot.house_from_lagna} from lagna.",
                strength=0.7,
                house_from_lagna=snapshot.house_from_lagna,
            )
        )
    if snapshot.house_from_lagna in DUSTHANA_HOUSES:
        impacts.append(
            NatalImpact(
                impact_type="dusthana_transit",
                description=f"{snapshot.planet} transiting dusthana house {snapshot.house_from_lagna} from lagna.",
                strength=0.75,
                house_from_lagna=snapshot.house_from_lagna,
            )
        )
    if snapshot.planet == "Saturn" and snapshot.house_from_moon in SADE_SATI_HOUSES_FROM_MOON:
        impacts.append(
            NatalImpact(
                impact_type="sade_sati_phase",
                description=(
                    f"Saturn in house {snapshot.house_from_moon} from Moon — "
                    "Sade Sati phase indicator."
                ),
                strength=0.85,
                house_from_moon=snapshot.house_from_moon,
            )
        )

    for natal_planet, natal_sign in transit_input.natal_planets.items():
        if natal_planet in {"Rahu", "Ketu"}:
            continue
        if _has_transit_aspect(snapshot, natal_sign, transit_input.natal_lagna_sign_index):
            impacts.append(
                NatalImpact(
                    impact_type="aspect_to_natal",
                    description=f"{snapshot.planet} aspects natal {natal_planet} by house drishti.",
                    strength=0.65,
                    target=natal_planet,
                )
            )
        if snapshot.sign.index == natal_sign:
            impacts.append(
                NatalImpact(
                    impact_type="conjunction_with_natal",
                    description=f"{snapshot.planet} transiting over natal {natal_planet} sign.",
                    strength=0.8,
                    target=natal_planet,
                )
            )

    impacts.sort(key=lambda item: item.strength, reverse=True)
    return tuple(impacts)


def detect_sign_changes(
    snapshots: tuple[TransitPlanetSnapshot, ...],
) -> tuple[SignChangeEvent, ...]:
    """Detect sign ingress events from ordered snapshots (per planet)."""
    by_planet: dict[str, list[TransitPlanetSnapshot]] = {}
    for snap in snapshots:
        by_planet.setdefault(snap.planet, []).append(snap)

    events: list[SignChangeEvent] = []
    for planet, planet_snaps in by_planet.items():
        ordered = sorted(planet_snaps, key=lambda item: item.datetime)
        for previous, current in zip(ordered, ordered[1:]):
            if previous.sign.index == current.sign.index:
                continue
            events.append(
                SignChangeEvent(
                    planet=planet,
                    datetime=current.datetime,
                    from_sign=previous.sign.name_en,
                    to_sign=current.sign.name_en,
                    from_house_lagna=previous.house_from_lagna,
                    to_house_lagna=current.house_from_lagna,
                )
            )
    return tuple(sorted(events, key=lambda item: item.datetime))


def build_highlights(
    planet: str,
    snapshots: tuple[TransitPlanetSnapshot, ...],
    sign_changes: tuple[SignChangeEvent, ...],
    natal_impacts: tuple[NatalImpact, ...],
) -> tuple[str, ...]:
    """Build human-readable highlight strings for a planet."""
    if not snapshots:
        return tuple()

    current = snapshots[-1]
    highlights = [
        (
            f"{planet} in {current.sign.name_en} (house {current.house_from_lagna} from lagna, "
            f"house {current.house_from_moon} from Moon)."
        )
    ]
    if current.is_retrograde:
        highlights.append(f"{planet} is retrograde.")
    for event in sign_changes:
        if event.planet == planet:
            highlights.append(
                f"{planet} enters {event.to_sign} on {event.datetime.date().isoformat()}."
            )
    highlights.extend(impact.description for impact in natal_impacts[:3])
    return tuple(highlights)


def analyze_planet_transit(
    planet: str,
    snapshots: tuple[TransitPlanetSnapshot, ...],
    transit_input: TransitInput,
) -> tuple[tuple[SignChangeEvent, ...], tuple[NatalImpact, ...], tuple[str, ...]]:
    """Analyze snapshots for one planet."""
    planet_snaps = tuple(item for item in snapshots if item.planet == planet)
    sign_changes = tuple(event for event in detect_sign_changes(planet_snaps) if event.planet == planet)
    current = planet_snaps[-1] if planet_snaps else None
    natal_impacts = analyze_natal_impacts(current, transit_input) if current else tuple()
    highlights = build_highlights(planet, planet_snaps, sign_changes, natal_impacts)
    return sign_changes, natal_impacts, highlights


def build_planet_analysis(
    planet: str,
    snapshots: tuple[TransitPlanetSnapshot, ...],
    transit_input: TransitInput,
) -> "TransitPlanetAnalysis":
    from astrology_engine.transits.types import TransitPlanetAnalysis

    planet_snaps = tuple(item for item in snapshots if item.planet == planet)
    sign_changes, natal_impacts, highlights = analyze_planet_transit(
        planet,
        planet_snaps,
        transit_input,
    )
    return TransitPlanetAnalysis(
        planet=planet,
        theme=TRANSIT_THEMES[planet],
        current=planet_snaps[-1] if planet_snaps else None,
        sign_changes=sign_changes,
        natal_impacts=natal_impacts,
        highlights=highlights,
    )


def _has_transit_aspect(
    snapshot: TransitPlanetSnapshot,
    natal_sign_index: int,
    lagna_sign_index: int,
) -> bool:
    transit_house = snapshot.house_from_lagna
    natal_house = ((natal_sign_index - lagna_sign_index) % 12) + 1
    distance = _house_distance(transit_house, natal_house)
    aspects = PLANET_ASPECTS.get(snapshot.planet, frozenset({7}))
    return distance in aspects


def _house_distance(from_house: int, to_house: int) -> int:
    return ((to_house - from_house + 12) % 12) + 1
