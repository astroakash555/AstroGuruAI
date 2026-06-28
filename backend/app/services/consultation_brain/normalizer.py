"""Evidence normalization for the consultation brain collection layer."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from typing import Any

from backend.app.services.consultation_brain.constants import (
    MAX_EVIDENCE_CONFIDENCE,
    MIN_EVIDENCE_CONFIDENCE,
    EvidenceSource,
)
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationEvidenceBundle


def _clamp_confidence(value: float) -> float:
    return max(MIN_EVIDENCE_CONFIDENCE, min(MAX_EVIDENCE_CONFIDENCE, value))


def _normalize_label(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_timestamp(value: Any) -> str | None:
    if isinstance(value, datetime):
        timestamp = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
        return timestamp.astimezone(UTC).isoformat()
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


class EvidenceNormalizer:
    """Normalizes collected evidence before bundle assembly."""

    _SOURCE_ORDER: tuple[EvidenceSource, ...] = (
        EvidenceSource.YOGAS,
        EvidenceSource.DASHA,
        EvidenceSource.TRANSIT,
        EvidenceSource.KP,
        EvidenceSource.LAL_KITAB,
        EvidenceSource.RULE_STUDIO,
        EvidenceSource.CASE_LEARNING,
        EvidenceSource.FUSION,
        EvidenceSource.GOLDEN_DATASET,
        EvidenceSource.PROFESSIONAL_REPORT,
    )

    def normalize_item(self, item: ConsultationEvidence) -> ConsultationEvidence:
        normalized_metadata = {
            key: _normalize_timestamp(value) if key.endswith("_at") or key == "timestamp" else value
            for key, value in item.metadata.items()
        }
        priority = normalized_metadata.get("priority")
        if isinstance(priority, (int, float)):
            normalized_metadata["priority"] = int(max(0, min(100, priority)))

        normalized_tags = tuple(
            sorted({_normalize_label(tag).lower() for tag in item.tags if _normalize_label(tag)})
        )
        return ConsultationEvidence(
            evidence_id=_normalize_label(item.evidence_id),
            source=item.source,
            category=item.category,
            title=_normalize_label(item.title),
            summary=_normalize_label(item.summary),
            weight=_clamp_confidence(item.weight),
            confidence=_clamp_confidence(item.confidence),
            raw_reference=_normalize_label(item.raw_reference),
            tags=normalized_tags or (item.source.value,),
            metadata=normalized_metadata,
        )

    def normalize(self, evidence: Iterable[ConsultationEvidence]) -> tuple[ConsultationEvidence, ...]:
        normalized = [self.normalize_item(item) for item in evidence]
        deduplicated = self._remove_duplicates(normalized)
        return self._sort_evidence(deduplicated)

    def build_bundle(
        self,
        evidence: Iterable[ConsultationEvidence],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> ConsultationEvidenceBundle:
        normalized = self.normalize(evidence)
        grouped: dict[EvidenceSource, list[ConsultationEvidence]] = {source: [] for source in self._SOURCE_ORDER}
        for item in normalized:
            grouped[item.source].append(item)
        return ConsultationEvidenceBundle(
            yogas=tuple(grouped[EvidenceSource.YOGAS]),
            dasha=tuple(grouped[EvidenceSource.DASHA]),
            transit=tuple(grouped[EvidenceSource.TRANSIT]),
            kp=tuple(grouped[EvidenceSource.KP]),
            lal_kitab=tuple(grouped[EvidenceSource.LAL_KITAB]),
            rule_studio=tuple(grouped[EvidenceSource.RULE_STUDIO]),
            case_learning=tuple(grouped[EvidenceSource.CASE_LEARNING]),
            fusion=tuple(grouped[EvidenceSource.FUSION]),
            golden_dataset=tuple(grouped[EvidenceSource.GOLDEN_DATASET]),
            professional_report=tuple(grouped[EvidenceSource.PROFESSIONAL_REPORT]),
            metadata=dict(metadata or {}),
        )

    def _remove_duplicates(self, evidence: list[ConsultationEvidence]) -> list[ConsultationEvidence]:
        seen: set[str] = set()
        unique: list[ConsultationEvidence] = []
        for item in evidence:
            if item.evidence_id in seen:
                continue
            seen.add(item.evidence_id)
            unique.append(item)
        return unique

    def _sort_evidence(self, evidence: list[ConsultationEvidence]) -> tuple[ConsultationEvidence, ...]:
        source_rank = {source: index for index, source in enumerate(self._SOURCE_ORDER)}
        return tuple(
            sorted(
                evidence,
                key=lambda item: (
                    source_rank.get(item.source, len(source_rank)),
                    -item.weight,
                    -item.confidence,
                    item.title.lower(),
                    item.evidence_id,
                ),
            )
        )
