"""Event window analysis for the Dasha intelligence layer."""

from __future__ import annotations

from datetime import datetime

from backend.app.services.reasoning.dasha.constants import (
    DOMAIN_TEMPLATES,
    EVENT_WINDOW_SUPPORT_THRESHOLD,
    DashaObservationCategory,
)
from backend.app.services.reasoning.dasha.effects import _domain_activation_score
from backend.app.services.reasoning.dasha.models import (
    DashaChartContext,
    EventWindowRecord,
    ReasoningObservation,
    make_observation,
)


def analyze_event_windows(context: DashaChartContext) -> tuple[EventWindowRecord, ...]:
    """Derive structured event windows from active dasha period boundaries."""
    records: list[EventWindowRecord] = []
    reference = context.reference_datetime

    for level in ("antardasha", "pratyantar", "mahadasha"):
        period = context.active_period(level)
        if period is None or (period.start is None and period.end is None):
            continue

        active_lords = ((level, period.lord, 1.0),)
        for template in DOMAIN_TEMPLATES:
            domain_id = str(template["domain_id"])
            display_name = str(template["display_name"])
            target_houses = tuple(template["target_houses"])  # type: ignore[index]
            primary_planets = tuple(template["primary_planets"])  # type: ignore[index]

            score, _, _, evidence = _domain_activation_score(
                context,
                active_lords,
                target_houses,
                primary_planets,
            )
            is_active = _period_is_active(period.start, period.end, reference)

            records.append(
                EventWindowRecord(
                    window_id=f"{domain_id}-{level}-{period.lord.lower()}",
                    domain_id=domain_id,
                    domain_name=display_name,
                    level=level,
                    lord=period.lord,
                    start=period.start,
                    end=period.end,
                    activation_score=score,
                    target_houses=target_houses,
                    is_active=is_active,
                    evidence=evidence,
                )
            )

    return tuple(records)


def event_windows_to_observations(
    records: tuple[EventWindowRecord, ...],
) -> tuple[ReasoningObservation, ...]:
    """Convert event window records into structured reasoning observations."""
    observations: list[ReasoningObservation] = []

    for record in records:
        if record.activation_score < EVENT_WINDOW_SUPPORT_THRESHOLD:
            continue

        status = "currently active" if record.is_active else "upcoming or recent"
        window_range = _format_window_range(record.start, record.end)

        observations.append(
            make_observation(
                observation_id=f"dasha-event-{record.window_id}",
                category=DashaObservationCategory.EVENT_WINDOW,
                title=f"{record.domain_name} Window via {record.lord.title()} {record.level.title()}",
                explanation=(
                    f"A {record.domain_name.lower()} event window ({status}) runs "
                    f"{window_range} under {record.lord} {record.level} "
                    f"with activation score {record.activation_score:.2f}."
                ),
                affected_planets=(record.lord,),
                affected_houses=record.target_houses,
                severity=record.activation_score,
                confidence=0.87 if record.is_active else 0.82,
                metadata={
                    "window_id": record.window_id,
                    "domain_id": record.domain_id,
                    "domain_name": record.domain_name,
                    "level": record.level,
                    "lord": record.lord,
                    "start": record.start.isoformat() if record.start else None,
                    "end": record.end.isoformat() if record.end else None,
                    "is_active": record.is_active,
                    "activation_score": record.activation_score,
                    "evidence": record.evidence,
                },
            )
        )

    return tuple(observations)


def _period_is_active(
    start: datetime | None,
    end: datetime | None,
    reference: datetime | None,
) -> bool:
    """Return True when the reference moment falls inside a period window."""
    if reference is None:
        return True
    if start is not None and reference < start:
        return False
    if end is not None and reference > end:
        return False
    return True


def _format_window_range(start: datetime | None, end: datetime | None) -> str:
    """Format a human-readable period range."""
    if start is not None and end is not None:
        return f"from {start.date().isoformat()} to {end.date().isoformat()}"
    if start is not None:
        return f"from {start.date().isoformat()}"
    if end is not None:
        return f"until {end.date().isoformat()}"
    return "within the current dasha segment"
