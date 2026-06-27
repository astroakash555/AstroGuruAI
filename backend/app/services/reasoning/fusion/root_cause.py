"""Root-cause synthesis from ranked fused observations."""

from __future__ import annotations

from backend.app.services.reasoning.fusion.models import FusedObservation, RootCauseAnalysis

ROOT_CAUSE_MIN_RANK = 0.55
ROOT_CAUSE_MAX_COUNT = 6


def build_root_causes(
    observations: tuple[FusedObservation, ...],
) -> tuple[RootCauseAnalysis, ...]:
    """
    Synthesize root causes from the highest-ranked fused observations.

    Observations are grouped by their primary planetary or house focus so that
    multi-engine agreement surfaces as a single causal hypothesis.
    """
    candidates = [
        observation
        for observation in observations
        if observation.rank_score >= ROOT_CAUSE_MIN_RANK
    ][:ROOT_CAUSE_MAX_COUNT]

    if not candidates:
        candidates = list(observations[: min(3, len(observations))])

    grouped: dict[str, list[FusedObservation]] = {}
    for observation in candidates:
        focus = _primary_focus(observation)
        grouped.setdefault(focus, []).append(observation)

    root_causes: list[RootCauseAnalysis] = []
    for index, group in enumerate(grouped.values(), start=1):
        primary = max(group, key=lambda item: item.rank_score)
        supporting_ids = tuple(dict.fromkeys(item.fusion_id for item in group))
        supporting_engines = tuple(
            dict.fromkeys(
                engine
                for item in group
                for engine in item.supporting_engines
            )
        )
        confidence = _root_cause_confidence(group)

        root_causes.append(
            RootCauseAnalysis(
                title=_root_cause_title(primary),
                explanation=_root_cause_explanation(primary, group),
                supporting_observations=supporting_ids,
                supporting_engines=supporting_engines,
                confidence=confidence,
            )
        )

    root_causes.sort(key=lambda item: item.confidence, reverse=True)
    return tuple(root_causes)


def _primary_focus(observation: FusedObservation) -> str:
    """Return a stable grouping key for root-cause synthesis."""
    if observation.affected_planets:
        return f"planet:{observation.affected_planets[0]}"
    if observation.affected_houses:
        return f"house:{observation.affected_houses[0]}"
    return f"theme:{observation.category}"


def _root_cause_title(observation: FusedObservation) -> str:
    """Build a root-cause title from the leading fused observation."""
    if observation.affected_planets:
        lead_planet = observation.affected_planets[0]
        return f"{lead_planet} Factor: {observation.title}"
    if observation.affected_houses:
        lead_house = observation.affected_houses[0]
        return f"House {lead_house} Factor: {observation.title}"
    return observation.title


def _root_cause_explanation(
    primary: FusedObservation,
    group: tuple[FusedObservation, ...] | list[FusedObservation],
) -> str:
    """Explain why the grouped observations form a root cause."""
    engine_names = ", ".join(
        sorted({engine.value for item in group for engine in item.supporting_engines})
    )
    if len(group) == 1:
        return (
            f"{primary.explanation} Identified as a primary factor by "
            f"{engine_names or primary.supporting_engines[0].value} analysis."
        )
    return (
        f"{primary.explanation} Supported by {len(group)} fused observations across "
        f"{engine_names} intelligence."
    )


def _root_cause_confidence(group: list[FusedObservation]) -> float:
    """Compute confidence for a synthesized root cause."""
    rank_component = max(item.rank_score for item in group)
    confidence_component = sum(item.confidence for item in group) / len(group)
    engine_bonus = min(0.05 * (len({engine for item in group for engine in item.supporting_engines}) - 1), 0.10)
    score = (0.55 * rank_component) + (0.45 * confidence_component) + engine_bonus
    return round(min(max(score, 0.0), 1.0), 4)
