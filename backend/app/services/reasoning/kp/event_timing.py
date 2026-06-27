"""KP event timing foundation for the reasoning intelligence layer."""

from __future__ import annotations

from backend.app.services.reasoning.kp.constants import EVENT_SUPPORT_THRESHOLD, EVENT_TEMPLATES, KPObservationCategory
from backend.app.services.reasoning.kp.models import EventTimingRecord, KPChartContext, ReasoningObservation, make_observation


class EventTimingAnalyzer:
    """
    Evaluates structured event templates against KP cusps and significators.

    The public ``analyze`` method returns both machine-readable timing records
    and human-facing observations so future prediction modules can extend event
    logic without changing analyzer interfaces.
    """

    def analyze(self, context: KPChartContext) -> tuple[EventTimingRecord, ...]:
        """Evaluate all configured event templates."""
        return evaluate_event_templates(context)

    def analyze_observations(self, context: KPChartContext) -> tuple[ReasoningObservation, ...]:
        """Convert event timing records into structured reasoning observations."""
        return event_records_to_observations(evaluate_event_templates(context))


def evaluate_event_templates(context: KPChartContext) -> tuple[EventTimingRecord, ...]:
    """Evaluate configured event templates against the chart context."""
    cusp_by_house = {item.house: item for item in context.cusps}
    sig_by_house = {item.house: item for item in context.significators}
    records: list[EventTimingRecord] = []

    for template in EVENT_TEMPLATES:
        target_houses = tuple(template["target_houses"])  # type: ignore[index]
        primary_planets = tuple(template["primary_planets"])  # type: ignore[index]

        matched_significators: set[str] = set()
        matched_sub_lords: set[str] = set()
        evidence: list[str] = []

        for house in target_houses:
            significators = sig_by_house.get(house)
            if significators is None:
                continue
            for planet in primary_planets:
                if planet in significators.combined:
                    matched_significators.add(planet)
                    evidence.append(f"{planet} is significator for house {house}.")
            cusp = cusp_by_house.get(house)
            if cusp is not None and cusp.sub_lord in primary_planets:
                matched_sub_lords.add(cusp.sub_lord)
                evidence.append(f"House {house} cusp sub lord is {cusp.sub_lord}.")

        support_score = _event_support_score(
            matched_significators,
            matched_sub_lords,
            primary_planets,
            target_houses,
        )
        is_supported = support_score >= EVENT_SUPPORT_THRESHOLD

        records.append(
            EventTimingRecord(
                event_id=str(template["event_id"]),
                event_type=str(template["event_type"]),
                target_houses=target_houses,
                is_supported=is_supported,
                support_score=round(support_score, 4),
                significators_matched=tuple(sorted(matched_significators)),
                cusp_sub_lords_matched=tuple(sorted(matched_sub_lords)),
                evidence=tuple(evidence),
            )
        )

    return tuple(records)


def event_records_to_observations(
    records: tuple[EventTimingRecord, ...],
) -> tuple[ReasoningObservation, ...]:
    """Map event timing records to structured observations."""
    observations: list[ReasoningObservation] = []

    for record in records:
        status = "supported" if record.is_supported else "not supported"
        observations.append(
            make_observation(
                observation_id=f"kp-event-{record.event_id}",
                category=KPObservationCategory.EVENT_TIMING,
                title=f"{record.event_type.title()} Event Timing",
                explanation=(
                    f"The {record.event_type} event framework is {status} with "
                    f"support score {record.support_score:.2f} across houses "
                    f"{', '.join(str(house) for house in record.target_houses)}."
                ),
                affected_planets=record.significators_matched + record.cusp_sub_lords_matched,
                affected_houses=record.target_houses,
                severity=record.support_score,
                confidence=0.9 if record.is_supported else 0.82,
                metadata={
                    "event_id": record.event_id,
                    "event_type": record.event_type,
                    "is_supported": record.is_supported,
                    "support_score": record.support_score,
                    "evidence": record.evidence,
                },
            )
        )

    return tuple(observations)


def analyze_event_timing(context: KPChartContext) -> tuple[ReasoningObservation, ...]:
    """Convenience wrapper for event timing observations."""
    return EventTimingAnalyzer().analyze_observations(context)


def _event_support_score(
    matched_significators: set[str],
    matched_sub_lords: set[str],
    primary_planets: tuple[str, ...],
    target_houses: tuple[int, ...],
) -> float:
    score = 0.0
    if matched_significators:
        score += 0.35 * (len(matched_significators) / max(len(primary_planets), 1))
    if matched_sub_lords:
        score += 0.35 * (len(matched_sub_lords) / max(len(target_houses), 1))
    if matched_significators and matched_sub_lords:
        score += 0.15
    return min(score, 1.0)
