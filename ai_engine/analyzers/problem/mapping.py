"""Astrological house and planet mapping for problem categories."""

from __future__ import annotations

from ai_engine.analyzers.problem.constants import (
    CATEGORY_HOUSES,
    CATEGORY_PLANETS,
    ROOT_CAUSE_TEMPLATES,
    ProblemCategory,
)
from ai_engine.analyzers.problem.types import HouseMapping, PlanetMapping, RootCauseIndicator


def map_houses(category: ProblemCategory) -> HouseMapping:
    """Return related houses for a problem category."""
    houses = CATEGORY_HOUSES[category]
    primary = houses["primary"]
    secondary = houses["secondary"]
    supporting = houses["supporting"]
    all_houses = tuple(dict.fromkeys(primary + secondary + supporting))
    return HouseMapping(
        primary=primary,
        secondary=secondary,
        supporting=supporting,
        all_houses=all_houses,
    )


def map_planets(category: ProblemCategory) -> PlanetMapping:
    """Return related planets for a problem category."""
    planets = CATEGORY_PLANETS[category]
    primary = planets["primary"]
    secondary = planets["secondary"]
    shadow = planets["shadow"]
    all_planets = tuple(dict.fromkeys(primary + secondary + shadow))
    return PlanetMapping(
        primary=primary,
        secondary=secondary,
        shadow=shadow,
        all_planets=all_planets,
    )


def derive_root_cause_indicators(
    category: ProblemCategory,
    normalized_text: str,
    *,
    max_indicators: int = 5,
) -> tuple[RootCauseIndicator, ...]:
    """
    Derive astrological root cause indicators from category and language cues.

    These are analytical context signals only — not remedies.
    """
    templates = ROOT_CAUSE_TEMPLATES[category]
    indicators: list[RootCauseIndicator] = []

    for index, template in enumerate(templates[:max_indicators]):
        relevance = round(max(0.95 - (index * 0.08), 0.55), 3)
        indicators.append(
            RootCauseIndicator(
                indicator=template,
                relevance=relevance,
                source="category_template",
            )
        )

    text_signals = _text_specific_indicators(normalized_text, category)
    for signal in text_signals:
        indicators.append(signal)

    indicators.sort(key=lambda item: item.relevance, reverse=True)
    return tuple(indicators[:max_indicators])


def _text_specific_indicators(
    normalized_text: str,
    category: ProblemCategory,
) -> list[RootCauseIndicator]:
    """Add indicators triggered by explicit language in the problem statement."""
    triggered: list[RootCauseIndicator] = []

    signal_map: list[tuple[tuple[str, ...], str, float]] = [
        (("delay", "delayed", "postpone"), "Delay-related language suggests Saturn influence or obstructed house outcomes.", 0.72),
        (("conflict", "fight", "argument", "dispute"), "Conflict language may indicate Mars affliction or activated 6th house patterns.", 0.74),
        (("loss", "lost", "losing"), "Loss-related language may correlate with afflicted wealth houses (2nd/11th) or Saturn periods.", 0.76),
        (("court", "case", "lawsuit"), "Legal language strongly activates 6th/7th/8th house dispute combinations.", 0.82),
        (("divorce", "separation"), "Separation language highlights 7th house and Venus affliction patterns.", 0.84),
        (("depression", "anxiety", "stress"), "Psychological stress language may relate to Moon affliction or 12th house pressure.", 0.7),
        (("debt", "loan", "bankruptcy"), "Debt language may indicate 6th/8th/12th house financial stress combinations.", 0.78),
    ]

    for keywords, indicator, relevance in signal_map:
        if any(keyword in normalized_text for keyword in keywords):
            triggered.append(
                RootCauseIndicator(
                    indicator=indicator,
                    relevance=relevance,
                    source="text_signal",
                )
            )

    if category == ProblemCategory.UNKNOWN and len(normalized_text.split()) < 6:
        triggered.append(
            RootCauseIndicator(
                indicator="Vague problem description limits precise house targeting; broad chart review is indicated.",
                relevance=0.68,
                source="text_signal",
            )
        )

    return triggered
