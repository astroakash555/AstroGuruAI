"""Ranking rules for consultation priority intelligence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence
from backend.app.services.consultation_brain.priority_models import ALL_PRIORITY_DOMAINS, PriorityDomain
from backend.app.services.consultation_brain.weights import weighted_evidence_score

SUPPRESSION_THRESHOLD = 0.15
SECONDARY_PRIORITY_COUNT = 3

DOMAIN_ALIASES: Mapping[str, PriorityDomain] = {
    "career": PriorityDomain.CAREER,
    "finance": PriorityDomain.FINANCE,
    "marriage": PriorityDomain.MARRIAGE,
    "relationship": PriorityDomain.RELATIONSHIP,
    "health": PriorityDomain.HEALTH,
    "education": PriorityDomain.EDUCATION,
    "children": PriorityDomain.CHILDREN,
    "property": PriorityDomain.PROPERTY,
    "business": PriorityDomain.BUSINESS,
    "spirituality": PriorityDomain.SPIRITUALITY,
    "spiritual": PriorityDomain.SPIRITUALITY,
    "foreign_travel": PriorityDomain.FOREIGN_TRAVEL,
    "travel": PriorityDomain.FOREIGN_TRAVEL,
    "legal": PriorityDomain.LEGAL,
    "mental_wellbeing": PriorityDomain.MENTAL_WELLBEING,
    "mental health": PriorityDomain.MENTAL_WELLBEING,
    "family": PriorityDomain.FAMILY,
}

TAG_DOMAIN_MAP: Mapping[str, PriorityDomain] = {
    "career": PriorityDomain.CAREER,
    "finance": PriorityDomain.FINANCE,
    "marriage": PriorityDomain.MARRIAGE,
    "relationship": PriorityDomain.RELATIONSHIP,
    "health": PriorityDomain.HEALTH,
    "education": PriorityDomain.EDUCATION,
    "children": PriorityDomain.CHILDREN,
    "property": PriorityDomain.PROPERTY,
    "business": PriorityDomain.BUSINESS,
    "spirituality": PriorityDomain.SPIRITUALITY,
    "foreign_travel": PriorityDomain.FOREIGN_TRAVEL,
    "legal": PriorityDomain.LEGAL,
    "mental_wellbeing": PriorityDomain.MENTAL_WELLBEING,
    "family": PriorityDomain.FAMILY,
}

CATEGORY_DOMAIN_MAP: Mapping[EvidenceCategory, tuple[PriorityDomain, ...]] = {
    EvidenceCategory.CAREER: (PriorityDomain.CAREER, PriorityDomain.BUSINESS),
    EvidenceCategory.RELATIONSHIP: (PriorityDomain.RELATIONSHIP, PriorityDomain.MARRIAGE),
    EvidenceCategory.HEALTH: (PriorityDomain.HEALTH, PriorityDomain.MENTAL_WELLBEING),
    EvidenceCategory.FINANCE: (PriorityDomain.FINANCE, PriorityDomain.PROPERTY),
    EvidenceCategory.SPIRITUAL: (PriorityDomain.SPIRITUALITY,),
    EvidenceCategory.TIMING: (PriorityDomain.FOREIGN_TRAVEL, PriorityDomain.CAREER),
    EvidenceCategory.REMEDY: (PriorityDomain.HEALTH, PriorityDomain.FAMILY),
    EvidenceCategory.GENERAL: (PriorityDomain.FAMILY,),
}


def normalize_domain_label(value: str) -> PriorityDomain | None:
    """Map a free-text domain label to a priority domain."""
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in DOMAIN_ALIASES:
        return DOMAIN_ALIASES[normalized]
    compact = normalized.replace("_", " ")
    return DOMAIN_ALIASES.get(compact)


def map_evidence_to_domains(evidence: ConsultationEvidence) -> tuple[PriorityDomain, ...]:
    """Assign evidence to one or more priority domains using structural signals only."""
    domains: set[PriorityDomain] = set()
    metadata_domain = evidence.metadata.get("domain")
    if isinstance(metadata_domain, str):
        mapped = normalize_domain_label(metadata_domain)
        if mapped is not None:
            domains.add(mapped)

    for tag in evidence.tags:
        mapped = TAG_DOMAIN_MAP.get(tag.lower())
        if mapped is not None:
            domains.add(mapped)

    for domain in CATEGORY_DOMAIN_MAP.get(evidence.category, ()):
        domains.add(domain)

    return tuple(sorted(domains, key=lambda item: item.value))


def filter_active_evidence(evidence: Sequence[ConsultationEvidence]) -> tuple[ConsultationEvidence, ...]:
    """Exclude conflict losers from priority scoring."""
    return tuple(item for item in evidence if not item.metadata.get("conflict_loser"))


def compute_urgency(items: Sequence[ConsultationEvidence]) -> float:
    """Higher when timing sources dominate the supporting evidence."""
    if not items:
        return 0.0
    timing_count = sum(
        1
        for item in items
        if item.source in {EvidenceSource.DASHA, EvidenceSource.TRANSIT} or item.category == EvidenceCategory.TIMING
    )
    timing_ratio = timing_count / len(items)
    average_confidence = sum(item.confidence for item in items) / len(items)
    return round(min(1.0, timing_ratio * 0.55 + average_confidence * 0.45), 4)


def compute_importance(
    items: Sequence[ConsultationEvidence],
    *,
    weights: Mapping[EvidenceSource, float],
) -> float:
    """Weighted source importance derived from architectural weights."""
    if not items:
        return 0.0
    scores = [weighted_evidence_score(item, weights=weights) for item in items]
    return round(sum(scores) / len(scores), 4)


def compute_domain_confidence(items: Sequence[ConsultationEvidence]) -> float:
    if not items:
        return 0.0
    return round(sum(item.confidence for item in items) / len(items), 4)


def supporting_sources(items: Sequence[ConsultationEvidence]) -> tuple[EvidenceSource, ...]:
    return tuple(sorted({item.source for item in items}, key=lambda source: source.value))


def compute_priority_score(
    *,
    urgency: float,
    importance: float,
    evidence_count: int,
    confidence: float,
    supporting_source_count: int,
) -> float:
    """Combine ranking signals into one deterministic domain score."""
    evidence_factor = min(evidence_count / 5.0, 1.0)
    source_factor = min(supporting_source_count / 4.0, 1.0)
    score = (
        importance * 0.35
        + confidence * 0.25
        + urgency * 0.20
        + evidence_factor * 0.10
        + source_factor * 0.10
    )
    return round(min(1.0, max(0.0, score)), 4)


def is_suppressed(*, priority_score: float, evidence_count: int) -> bool:
    """Return True when a domain should be moved to suppressed topics."""
    if evidence_count <= 0:
        return True
    return priority_score < SUPPRESSION_THRESHOLD


def sort_domain_priorities(
    scored_domains: Sequence[tuple[PriorityDomain, dict[str, float | int | tuple[EvidenceSource, ...] | tuple[str, ...]]]],
) -> list[tuple[PriorityDomain, dict[str, float | int | tuple[EvidenceSource, ...] | tuple[str, ...]]]]:
    """Sort domains deterministically by score and label."""
    return sorted(
        scored_domains,
        key=lambda item: (
            -float(item[1]["priority_score"]),
            -float(item[1]["confidence"]),
            item[0].value,
        ),
    )


def empty_domain_set() -> dict[PriorityDomain, list[ConsultationEvidence]]:
    return {domain: [] for domain in ALL_PRIORITY_DOMAINS}
