"""Lal Kitab Rin (karmic debt) detection for the reasoning layer."""

from __future__ import annotations

from backend.app.services.reasoning.lal_kitab.constants import RIN_DISPLAY_NAMES, LalKitabObservationCategory
from backend.app.services.reasoning.lal_kitab.models import LalKitabChartContext, ReasoningObservation, make_observation


def analyze_rin_debts(context: LalKitabChartContext) -> tuple[ReasoningObservation, ...]:
    """Detect and explain the five primary Lal Kitab Rin debts."""
    detectors = (
        _detect_pitra_rin,
        _detect_matra_rin,
        _detect_stri_rin,
        _detect_guru_rin,
        _detect_dev_rin,
    )
    observations: list[ReasoningObservation] = []
    for detector in detectors:
        observations.append(detector(context))
    return tuple(observations)


def _detect_pitra_rin(context: LalKitabChartContext) -> ReasoningObservation:
    """Detect Pitra Rin from Sun-Saturn dharma axis linkage."""
    sun_house = context.house_of("Sun")
    saturn_house = context.house_of("Saturn")
    is_present = sun_house == 9 and saturn_house in {9, 12}
    return _rin_observation(
        rin_id="pitra_rin",
        is_present=is_present,
        strength=0.82 if is_present else 0.20,
        explanation_present=(
            f"Pitra Rin is indicated because Sun occupies house {sun_house} while Saturn "
            f"occupies house {saturn_house}, linking ancestral karmic debt in Lal Kitab."
        ),
        explanation_absent=(
            f"Pitra Rin is not strongly indicated; Sun is in house {sun_house} and "
            f"Saturn in house {saturn_house}."
        ),
        planets=("Sun", "Saturn"),
        houses=(9, 12),
        context=context,
    )


def _detect_matra_rin(context: LalKitabChartContext) -> ReasoningObservation:
    """Detect Matra Rin from Moon-Rahu maternal axis linkage."""
    moon_house = context.house_of("Moon")
    rahu_house = context.house_of("Rahu")
    is_present = moon_house == 4 and rahu_house in {4, 8}
    return _rin_observation(
        rin_id="matra_rin",
        is_present=is_present,
        strength=0.78 if is_present else 0.18,
        explanation_present=(
            f"Matra Rin is indicated because Moon occupies house {moon_house} with Rahu "
            f"linked through house {rahu_house}."
        ),
        explanation_absent=(
            f"Matra Rin is not strongly indicated; Moon is in house {moon_house} and "
            f"Rahu in house {rahu_house}."
        ),
        planets=("Moon", "Rahu"),
        houses=(4, 8),
        context=context,
    )


def _detect_stri_rin(context: LalKitabChartContext) -> ReasoningObservation:
    """Detect Stri Rin from Venus-Mars relationship axis linkage."""
    venus_house = context.house_of("Venus")
    mars_house = context.house_of("Mars")
    is_present = venus_house == 7 and mars_house in {7, 8}
    return _rin_observation(
        rin_id="stri_rin",
        is_present=is_present,
        strength=0.76 if is_present else 0.16,
        explanation_present=(
            f"Stri Rin is indicated because Venus occupies house {venus_house} while Mars "
            f"occupies house {mars_house}, stressing relationship karmic debt."
        ),
        explanation_absent=(
            f"Stri Rin is not strongly indicated; Venus is in house {venus_house} and "
            f"Mars in house {mars_house}."
        ),
        planets=("Venus", "Mars"),
        houses=(7, 8),
        context=context,
    )


def _detect_guru_rin(context: LalKitabChartContext) -> ReasoningObservation:
    """Detect Guru Rin from afflicted Jupiter placements."""
    jupiter_house = context.house_of("Jupiter")
    saturn_house = context.house_of("Saturn")
    rahu_house = context.house_of("Rahu")
    jupiter_afflicted = jupiter_house in {6, 8, 12}
    linked_malefic = (
        jupiter_house == saturn_house
        or jupiter_house == rahu_house
        or (jupiter_afflicted and saturn_house in {6, 8, 12})
    )
    is_present = jupiter_afflicted and linked_malefic
    return _rin_observation(
        rin_id="guru_rin",
        is_present=is_present,
        strength=0.80 if is_present else 0.17,
        explanation_present=(
            f"Guru Rin is indicated because Jupiter in house {jupiter_house} is afflicted "
            f"and linked with Saturn/Rahu pressure in Lal Kitab judgment."
        ),
        explanation_absent=(
            f"Guru Rin is not strongly indicated; Jupiter in house {jupiter_house} lacks "
            "a strong malefic linkage."
        ),
        planets=("Jupiter", "Saturn", "Rahu"),
        houses=(jupiter_house, saturn_house),
        context=context,
    )


def _detect_dev_rin(context: LalKitabChartContext) -> ReasoningObservation:
    """Detect Dev Rin from Sun-Ketu spiritual axis linkage."""
    sun_house = context.house_of("Sun")
    ketu_house = context.house_of("Ketu")
    is_present = sun_house == 12 and ketu_house in {6, 12}
    return _rin_observation(
        rin_id="dev_rin",
        is_present=is_present,
        strength=0.77 if is_present else 0.15,
        explanation_present=(
            f"Dev Rin is indicated because Sun occupies house {sun_house} with Ketu linked "
            f"through house {ketu_house}, suggesting ritual or divine-karmic debt."
        ),
        explanation_absent=(
            f"Dev Rin is not strongly indicated; Sun is in house {sun_house} and "
            f"Ketu in house {ketu_house}."
        ),
        planets=("Sun", "Ketu"),
        houses=(6, 12),
        context=context,
    )


def _rin_observation(
    *,
    rin_id: str,
    is_present: bool,
    strength: float,
    explanation_present: str,
    explanation_absent: str,
    planets: tuple[str, ...],
    houses: tuple[int, ...],
    context: LalKitabChartContext,
) -> ReasoningObservation:
    """Build a standardized Rin observation."""
    display_name = RIN_DISPLAY_NAMES[rin_id]
    return make_observation(
        observation_id=f"lk-rin-{rin_id}",
        category=LalKitabObservationCategory.RIN,
        title=f"{display_name} {'Present' if is_present else 'Not Active'}",
        explanation=explanation_present if is_present else explanation_absent,
        affected_planets=planets,
        affected_houses=houses,
        severity=strength if is_present else round(strength * 0.5, 4),
        confidence=0.88 if is_present else 0.80,
        metadata={
            "rin_id": rin_id,
            "rin_name": display_name,
            "is_present": is_present,
            "strength": strength,
        },
    )
