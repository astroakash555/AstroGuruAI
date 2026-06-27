"""Shared helpers for domain consultation modules."""

from __future__ import annotations

from backend.app.services.consultation.consultation_models import (
    ConsultationSection,
    DomainConsultationConfig,
)
from backend.app.services.reasoning.fusion.models import (
    FusedObservation,
    FusionRecommendation,
    FusionResult,
    RootCauseAnalysis,
)


def score_observation(observation: FusedObservation, config: DomainConsultationConfig) -> float:
    """Score how relevant an observation is to a consultation domain."""
    score = observation.rank_score
    title_lower = observation.title.lower()
    category_lower = observation.category.lower()

    for keyword in config.keywords:
        if keyword in title_lower or keyword in category_lower:
            score += 0.12

    for planet in config.primary_planets:
        if planet in observation.affected_planets:
            score += 0.10

    for house in config.target_houses:
        if house in observation.affected_houses:
            score += 0.08

    return min(score, 1.0)


def filter_observations(
    fusion: FusionResult,
    config: DomainConsultationConfig,
) -> tuple[FusedObservation, ...]:
    """Return observations ranked for a consultation domain."""
    scored = [(score_observation(item, config), item) for item in fusion.observations]
    relevant = [item for value, item in scored if value >= 0.35]
    relevant.sort(key=lambda item: score_observation(item, config), reverse=True)
    return tuple(relevant)


def matching_root_causes(
    fusion: FusionResult,
    observations: tuple[FusedObservation, ...],
    config: DomainConsultationConfig,
) -> tuple[RootCauseAnalysis, ...]:
    """Find root causes aligned with domain observations."""
    obs_ids = {item.fusion_id for item in observations}
    matched: list[RootCauseAnalysis] = []
    for root in fusion.root_causes:
        if obs_ids.intersection(set(root.supporting_observations)):
            matched.append(root)
            continue
        if any(keyword in root.title.lower() for keyword in config.keywords):
            matched.append(root)
    return tuple(matched)


def matching_recommendations(
    fusion: FusionResult,
    root_causes: tuple[RootCauseAnalysis, ...],
    config: DomainConsultationConfig,
) -> tuple[FusionRecommendation, ...]:
    """Find recommendations linked to domain root causes."""
    root_titles = {item.title for item in root_causes}
    matched: list[FusionRecommendation] = []
    for recommendation in fusion.recommendations:
        if root_titles.intersection(set(recommendation.supporting_root_causes)):
            matched.append(recommendation)
            continue
        text = f"{recommendation.title} {recommendation.explanation}".lower()
        if any(keyword in text for keyword in config.keywords):
            matched.append(recommendation)
    return tuple(matched)


def build_consultation_section(
    fusion: FusionResult,
    config: DomainConsultationConfig,
) -> ConsultationSection:
    """Build a full consultation section from fusion evidence."""
    observations = filter_observations(fusion, config)
    root_causes = matching_root_causes(fusion, observations, config)
    recommendations = matching_recommendations(fusion, root_causes, config)

    if observations:
        current_situation = _join_unique(
            f"{item.title}: {item.explanation}" for item in observations[:2]
        )
    else:
        current_situation = (
            f"No dominant {config.title.lower()} signals are active in the current fused chart analysis. "
            "The period appears relatively steady in this domain."
        )

    if root_causes:
        root_cause = root_causes[0].explanation
    elif observations:
        root_cause = observations[0].explanation
    else:
        root_cause = (
            f"No single root cause dominates {config.title.lower()} at present; "
            "background chart factors remain manageable."
        )

    positive_factors = tuple(
        item.title
        for item in observations
        if item.severity < 0.68 and not item.has_conflict
    )[:3]
    if not positive_factors:
        positive_factors = ("Underlying chart support remains available with conscious effort.",)

    challenges = tuple(
        item.title
        for item in observations
        if item.severity >= 0.68 or item.has_conflict
    )[:3]
    conflict_titles = tuple(
        conflict.title
        for conflict in fusion.conflicts
        if any(keyword in conflict.title.lower() for keyword in config.keywords)
    )
    challenges = tuple(dict.fromkeys((*challenges, *conflict_titles)))[:3]
    if not challenges:
        challenges = ("No acute challenge cluster is flagged for this domain right now.",)

    timeline = config.timeline_hint
    for item in observations:
        if "dasha" in item.category or "transit" in item.category:
            timeline = (
                f"{item.title} indicates the current timing emphasis. "
                f"{config.timeline_hint}"
            )
            break

    advice: list[str] = []
    for recommendation in recommendations[:2]:
        advice.append(recommendation.explanation)
    if not advice and fusion.recommendations:
        advice.append(fusion.recommendations[0].explanation)
    if not advice:
        advice.append(
            f"Monitor {config.title.lower()} themes during the active dasha-transit window "
            "and align decisions with stable planetary support."
        )

    confidence = _section_confidence(observations, root_causes, fusion.confidence_score)

    return ConsultationSection(
        section_id=config.section_id,
        title=config.title,
        current_situation=current_situation,
        root_cause=root_cause,
        positive_factors=positive_factors,
        challenges=challenges,
        timeline=timeline,
        actionable_advice=tuple(advice),
        confidence=round(confidence, 4),
        supporting_observation_ids=tuple(item.fusion_id for item in observations[:5]),
    )


def _section_confidence(
    observations: tuple[FusedObservation, ...],
    root_causes: tuple[RootCauseAnalysis, ...],
    fusion_confidence: float,
) -> float:
    if observations and root_causes:
        obs_conf = sum(item.confidence for item in observations[:3]) / min(len(observations), 3)
        root_conf = sum(item.confidence for item in root_causes) / len(root_causes)
        return min((0.45 * fusion_confidence) + (0.35 * obs_conf) + (0.20 * root_conf), 1.0)
    if observations:
        return min(fusion_confidence, sum(item.confidence for item in observations[:3]) / min(len(observations), 3))
    return max(fusion_confidence * 0.6, 0.35)


def _join_unique(parts: tuple[str, ...] | list[str]) -> str:
    seen: set[str] = set()
    lines: list[str] = []
    for part in parts:
        if part in seen:
            continue
        seen.add(part)
        lines.append(part)
    return " ".join(lines)
