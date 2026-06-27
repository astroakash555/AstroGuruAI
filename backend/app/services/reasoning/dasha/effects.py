"""Combined dasha effects, dignity, house activation, and domain analysis."""

from __future__ import annotations

from backend.app.services.reasoning.dasha.constants import (
    DOMAIN_ACTIVATION_THRESHOLD,
    DOMAIN_TEMPLATES,
    DIGNITY_CONFIDENCE_MODIFIERS,
    DIGNITY_SEVERITY_MODIFIERS,
    DUSTHANA_HOUSES,
    DashaObservationCategory,
    HOUSE_ACTIVATION_THEMES,
    KENDRA_HOUSES,
    NATURAL_ENEMIES,
    NATURAL_FRIENDS,
    TRIKONA_HOUSES,
)
from backend.app.services.reasoning.dasha.models import DashaChartContext, ReasoningObservation, make_observation


def analyze_combined_effects(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Evaluate synergy or friction between mahadasha and antardasha lords."""
    md = context.active_period("mahadasha")
    ad = context.active_period("antardasha")
    if md is None or ad is None:
        return ()

    md_lord = md.lord
    ad_lord = ad.lord
    if md_lord == ad_lord:
        return (
            make_observation(
                observation_id=f"dasha-combined-{md_lord.lower()}-same-lord",
                category=DashaObservationCategory.COMBINED_EFFECT,
                title=f"Reinforced {md_lord} Dasha Cycle",
                explanation=(
                    f"Mahadasha and antardasha are both ruled by {md_lord}, intensifying "
                    f"that graha's themes without sub-period modulation."
                ),
                affected_planets=(md_lord,),
                affected_houses=_shared_houses(context, md_lord),
                severity=0.78,
                confidence=0.91,
                metadata={
                    "relationship": "same_lord",
                    "mahadasha_lord": md_lord,
                    "antardasha_lord": ad_lord,
                },
            ),
        )

    if ad_lord in NATURAL_FRIENDS.get(md_lord, frozenset()):
        relationship = "friendly"
        title = f"Supportive {md_lord}-{ad_lord} Dasha Blend"
        explanation = (
            f"{ad_lord} antardasha supports {md_lord} mahadasha through natural friendship, "
            f"allowing smoother expression of both lords."
        )
        severity = 0.74
        confidence = 0.89
    elif ad_lord in NATURAL_ENEMIES.get(md_lord, frozenset()):
        relationship = "inimical"
        title = f"Contested {md_lord}-{ad_lord} Dasha Blend"
        explanation = (
            f"{ad_lord} antardasha challenges {md_lord} mahadasha through natural enmity, "
            f"creating mixed or delayed results until the sub-period shifts."
        )
        severity = 0.76
        confidence = 0.87
    else:
        relationship = "neutral"
        title = f"Balanced {md_lord}-{ad_lord} Dasha Blend"
        explanation = (
            f"{ad_lord} antardasha operates neutrally under {md_lord} mahadasha, "
            f"mixing both lords' significations in proportion to chart strength."
        )
        severity = 0.70
        confidence = 0.86

    return (
        make_observation(
            observation_id=f"dasha-combined-{md_lord.lower()}-{ad_lord.lower()}",
            category=DashaObservationCategory.COMBINED_EFFECT,
            title=title,
            explanation=explanation,
            affected_planets=(md_lord, ad_lord),
            affected_houses=_shared_houses(context, md_lord, ad_lord),
            severity=severity,
            confidence=confidence,
            metadata={
                "relationship": relationship,
                "mahadasha_lord": md_lord,
                "antardasha_lord": ad_lord,
            },
        ),
    )


def analyze_dignity_modifiers(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Emit dignity-based modifiers for active dasha lords present in the chart."""
    observations: list[ReasoningObservation] = []
    seen: set[str] = set()

    for level in ("mahadasha", "antardasha", "pratyantar"):
        period = context.active_period(level)
        if period is None:
            continue
        lord = period.lord
        if lord in seen or not context.has_planet(lord):
            continue
        seen.add(lord)

        planet = context.get_planet(lord)
        severity_delta = DIGNITY_SEVERITY_MODIFIERS.get(planet.dignity, 0.0)
        confidence_delta = DIGNITY_CONFIDENCE_MODIFIERS.get(planet.dignity, 0.0)
        base_severity = 0.66 + severity_delta
        base_confidence = 0.86 + confidence_delta

        observations.append(
            make_observation(
                observation_id=f"dasha-dignity-{lord.lower()}-{planet.dignity}",
                category=DashaObservationCategory.DIGNITY,
                title=f"{lord} Dasha Lord in {planet.dignity.title()} Dignity",
                explanation=(
                    f"The active {level.replace('_', ' ')} lord {lord} is {planet.dignity} "
                    f"in {planet.sign_name} (house {planet.house}), modifying dasha results "
                    f"{'positively' if severity_delta >= 0 else 'with strain'}."
                ),
                affected_planets=(lord,),
                affected_houses=(planet.house,),
                severity=base_severity,
                confidence=base_confidence,
                metadata={
                    "level": level,
                    "lord": lord,
                    "dignity": planet.dignity,
                    "sign": planet.sign_name,
                    "house": planet.house,
                    "severity_delta": severity_delta,
                    "confidence_delta": confidence_delta,
                },
            )
        )

    return tuple(observations)


def analyze_house_activation(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Identify houses activated by active dasha lords."""
    observations: list[ReasoningObservation] = []
    activated: set[int] = set()

    for level, weight in (("mahadasha", 0.74), ("antardasha", 0.68), ("pratyantar", 0.62)):
        period = context.active_period(level)
        if period is None:
            continue

        lord = period.lord
        occupied = context.house_of(lord)
        ruled = context.houses_ruled(lord)
        candidate_houses = set(ruled)
        if occupied is not None:
            candidate_houses.add(occupied)

        for house in sorted(candidate_houses):
            if house in activated:
                continue
            activated.add(house)

            house_type = _house_type_label(house)
            theme = HOUSE_ACTIVATION_THEMES.get(house, "life themes of the activated bhava")

            observations.append(
                make_observation(
                    observation_id=f"dasha-house-{house}-{lord.lower()}",
                    category=DashaObservationCategory.HOUSE_ACTIVATION,
                    title=f"House {house} Activated by {lord}",
                    explanation=(
                        f"House {house} ({house_type}) is activated during {lord} {level}, "
                        f"bringing {theme} into focus."
                    ),
                    affected_planets=(lord,),
                    affected_houses=(house,),
                    severity=weight,
                    confidence=0.85,
                    metadata={
                        "level": level,
                        "lord": lord,
                        "house": house,
                        "house_type": house_type,
                        "occupied": occupied == house,
                        "ruled": house in ruled,
                    },
                )
            )

    return tuple(observations)


def analyze_domain_activation(context: DashaChartContext) -> tuple[ReasoningObservation, ...]:
    """Score life-domain activation from active dasha lords against domain templates."""
    observations: list[ReasoningObservation] = []
    active_lords = _active_lords(context)
    if not active_lords:
        return ()

    for template in DOMAIN_TEMPLATES:
        domain_id = str(template["domain_id"])
        display_name = str(template["display_name"])
        target_houses = tuple(template["target_houses"])  # type: ignore[index]
        primary_planets = tuple(template["primary_planets"])  # type: ignore[index]

        score, matched_planets, matched_houses, evidence = _domain_activation_score(
            context,
            active_lords,
            target_houses,
            primary_planets,
        )
        is_active = score >= DOMAIN_ACTIVATION_THRESHOLD

        observations.append(
            make_observation(
                observation_id=f"dasha-domain-{domain_id}",
                category=DashaObservationCategory.DOMAIN,
                title=f"{display_name} Domain {'Activated' if is_active else 'Moderate'} in Dasha",
                explanation=(
                    f"The {display_name.lower()} domain scores {score:.2f} during the active "
                    f"dasha stack. {'; '.join(evidence) if evidence else 'No strong domain linkage detected.'}"
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


def _active_lords(context: DashaChartContext) -> tuple[tuple[str, str, float], ...]:
    """Return active lords with level weights."""
    lords: list[tuple[str, str, float]] = []
    weights = {
        "mahadasha": 0.50,
        "antardasha": 0.35,
        "pratyantar": 0.15,
    }
    for level, weight in weights.items():
        period = context.active_period(level)
        if period is not None:
            lords.append((level, period.lord, weight))
    return tuple(lords)


def _domain_activation_score(
    context: DashaChartContext,
    active_lords: tuple[tuple[str, str, float], ...],
    target_houses: tuple[int, ...],
    primary_planets: tuple[str, ...],
) -> tuple[float, tuple[str, ...], tuple[int, ...], tuple[str, ...]]:
    """Compute domain activation score from dasha lords and chart links."""
    score = 0.0
    matched_planets: set[str] = set()
    matched_houses: set[int] = set()
    evidence: list[str] = []

    for _level, lord, weight in active_lords:
        if lord in primary_planets:
            score += 0.28 * weight / 0.5
            matched_planets.add(lord)
            evidence.append(f"{lord} is a primary significator for this domain.")

        occupied = context.house_of(lord)
        if occupied is not None and occupied in target_houses:
            score += 0.22 * weight / 0.5
            matched_houses.add(occupied)
            matched_planets.add(lord)
            evidence.append(f"{lord} occupies target house {occupied}.")

        for house in context.houses_ruled(lord):
            if house in target_houses:
                score += 0.18 * weight / 0.5
                matched_houses.add(house)
                matched_planets.add(lord)
                evidence.append(f"{lord} rules target house {house}.")

    normalized = min(score, 1.0)
    return (
        round(normalized, 4),
        tuple(sorted(matched_planets)),
        tuple(sorted(matched_houses)),
        tuple(evidence),
    )


def _shared_houses(
    context: DashaChartContext,
    *lords: str,
) -> tuple[int, ...]:
    """Collect houses occupied or ruled by the given lords."""
    houses: set[int] = set()
    for lord in lords:
        occupied = context.house_of(lord)
        if occupied is not None:
            houses.add(occupied)
        houses.update(context.houses_ruled(lord))
    return tuple(sorted(houses))


def _house_type_label(house: int) -> str:
    """Return a descriptive house classification label."""
    if house in KENDRA_HOUSES:
        return "kendra bhava"
    if house in TRIKONA_HOUSES:
        return "trikona bhava"
    if house in DUSTHANA_HOUSES:
        return "dusthana bhava"
    return "upachaya or neutral bhava"
