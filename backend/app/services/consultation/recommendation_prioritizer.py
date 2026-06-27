"""Priority, strength, and risk prioritization for the consultation brain."""

from __future__ import annotations

from backend.app.services.consultation.consultation_models import (
    ConsultationPriorityItem,
    ConsultationRiskItem,
    ConsultationStrengthItem,
)
from backend.app.services.reasoning.fusion.models import FusionResult


def build_priorities(fusion: FusionResult) -> tuple[ConsultationPriorityItem, ...]:
    """Build top five consultation priorities from fusion recommendations and root causes."""
    items: list[ConsultationPriorityItem] = []

    for index, recommendation in enumerate(fusion.recommendations[:5], start=1):
        items.append(
            ConsultationPriorityItem(
                rank=index,
                title=recommendation.title,
                explanation=recommendation.explanation,
                domain=_infer_domain(recommendation.title, recommendation.explanation),
                confidence=recommendation.confidence,
            )
        )

    next_rank = len(items) + 1
    for root in fusion.root_causes:
        if len(items) >= 5:
            break
        if any(item.title == root.title for item in items):
            continue
        items.append(
            ConsultationPriorityItem(
                rank=next_rank,
                title=root.title,
                explanation=root.explanation,
                domain=_infer_domain(root.title, root.explanation),
                confidence=root.confidence,
            )
        )
        next_rank += 1

    if len(items) < 5:
        for observation in fusion.observations:
            if len(items) >= 5:
                break
            if any(item.title == observation.title for item in items):
                continue
            items.append(
                ConsultationPriorityItem(
                    rank=len(items) + 1,
                    title=observation.title,
                    explanation=observation.explanation,
                    domain=_infer_domain(observation.title, observation.explanation),
                    confidence=observation.confidence,
                )
            )

    return tuple(items[:5])


def build_strengths(fusion: FusionResult) -> tuple[ConsultationStrengthItem, ...]:
    """Build top five strengths from high-confidence supportive observations."""
    candidates = [
        item
        for item in fusion.observations
        if item.confidence >= 0.75 and item.severity < 0.72 and not item.has_conflict
    ]
    candidates.sort(key=lambda item: (item.confidence, item.rank_score), reverse=True)

    if not candidates:
        candidates = sorted(
            fusion.observations,
            key=lambda item: (item.confidence, -item.severity),
            reverse=True,
        )

    return tuple(
        ConsultationStrengthItem(
            rank=index,
            title=item.title,
            explanation=item.explanation,
            confidence=item.confidence,
            supporting_engines=tuple(engine.value for engine in item.supporting_engines),
        )
        for index, item in enumerate(candidates[:5], start=1)
    )


def build_risks(fusion: FusionResult) -> tuple[ConsultationRiskItem, ...]:
    """Build top five risks from conflicts and high-severity observations."""
    items: list[ConsultationRiskItem] = []

    for conflict in fusion.conflicts[:5]:
        items.append(
            ConsultationRiskItem(
                rank=len(items) + 1,
                title=conflict.title,
                explanation=conflict.explanation,
                severity=min(conflict.severity_spread + 0.5, 1.0),
                confidence=conflict.confidence,
                has_conflict=True,
            )
        )

    high_severity = [
        item
        for item in fusion.observations
        if item.severity >= 0.72 or item.has_conflict
    ]
    high_severity.sort(key=lambda item: (item.severity, item.confidence), reverse=True)

    for observation in high_severity:
        if len(items) >= 5:
            break
        if any(item.title == observation.title for item in items):
            continue
        items.append(
            ConsultationRiskItem(
                rank=len(items) + 1,
                title=observation.title,
                explanation=observation.explanation,
                severity=observation.severity,
                confidence=observation.confidence,
                has_conflict=observation.has_conflict,
            )
        )

    return tuple(items[:5])


def _infer_domain(title: str, explanation: str) -> str:
    text = f"{title} {explanation}".lower()
    mapping = {
        "marriage": ("marriage", "spouse", "wedding"),
        "relationship": ("relationship", "partner", "venus"),
        "career": ("career", "profession", "10th"),
        "business": ("business", "commerce", "trade"),
        "finance": ("finance", "wealth", "money"),
        "health": ("health", "vitality", "6th"),
        "education": ("education", "study", "learning"),
        "spiritual_growth": ("spiritual", "dharma", "ketu"),
        "foreign_travel": ("foreign", "travel", "abroad"),
        "family": ("family", "home", "4th"),
        "children": ("children", "progeny", "5th"),
    }
    for domain, keywords in mapping.items():
        if any(keyword in text for keyword in keywords):
            return domain
    return "general"
