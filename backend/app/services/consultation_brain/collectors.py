"""Evidence collection orchestration for the consultation brain."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Iterable, Sequence

from backend.app.services.consultation_brain.clock import UtcClock
from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationEvidenceBundle, ConsultationInput
from backend.app.services.consultation_brain.normalizer import EvidenceNormalizer
from backend.app.services.consultation_brain.protocols import AsyncEvidenceProvider, Clock, EvidenceProvider
from backend.app.services.consultation_brain.providers import default_collection_providers


class SyncToAsyncEvidenceProvider:
    """Adapts a sync provider for async collection without shared mutable state."""

    __slots__ = ("_provider",)

    def __init__(self, provider: EvidenceProvider) -> None:
        self._provider = provider

    @property
    def source(self) -> EvidenceSource:
        return self._provider.source

    async def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        return self._provider.collect(consultation_input)


def as_async_provider(provider: EvidenceProvider | AsyncEvidenceProvider) -> AsyncEvidenceProvider:
    """Return an async-capable provider, wrapping sync implementations when needed."""
    collect = getattr(provider, "collect", None)
    if collect is not None and inspect.iscoroutinefunction(collect):
        return provider  # type: ignore[return-value]
    return SyncToAsyncEvidenceProvider(provider)


def collect_evidence(
    consultation_input: ConsultationInput,
    providers: Sequence[EvidenceProvider],
) -> tuple[ConsultationEvidence, ...]:
    """Aggregate evidence from sync providers without bundle normalization."""
    collected: list[ConsultationEvidence] = []
    for provider in providers:
        collected.extend(provider.collect(consultation_input))
    return tuple(collected)


async def collect_evidence_async(
    consultation_input: ConsultationInput,
    providers: Sequence[EvidenceProvider | AsyncEvidenceProvider],
) -> tuple[ConsultationEvidence, ...]:
    """Aggregate evidence from async-capable providers without bundle normalization."""
    async_providers = tuple(as_async_provider(provider) for provider in providers)
    chunks = await asyncio.gather(*(provider.collect(consultation_input) for provider in async_providers))
    collected: list[ConsultationEvidence] = []
    for chunk in chunks:
        collected.extend(chunk)
    return tuple(collected)


def provider_sources(providers: Iterable[EvidenceProvider | AsyncEvidenceProvider]) -> tuple[str, ...]:
    """Return source identifiers for diagnostics and metadata."""
    return tuple(provider.source.value for provider in providers)


class EvidenceCollector:
    """Runs providers, merges evidence, normalizes, and returns a bundle."""

    def __init__(
        self,
        *,
        providers: Sequence[EvidenceProvider] | None = None,
        normalizer: EvidenceNormalizer | None = None,
        clock: Clock | None = None,
    ) -> None:
        self._providers: tuple[EvidenceProvider, ...] = tuple(
            providers if providers is not None else default_collection_providers()
        )
        self._normalizer = normalizer or EvidenceNormalizer()
        self._clock = clock or UtcClock()

    @property
    def providers(self) -> tuple[EvidenceProvider, ...]:
        return self._providers

    @property
    def normalizer(self) -> EvidenceNormalizer:
        return self._normalizer

    @property
    def clock(self) -> Clock:
        return self._clock

    def collect(self, consultation_input: ConsultationInput) -> ConsultationEvidenceBundle:
        raw_evidence = collect_evidence(consultation_input, self._providers)
        return self._build_bundle(consultation_input, raw_evidence)

    async def collect_async(self, consultation_input: ConsultationInput) -> ConsultationEvidenceBundle:
        raw_evidence = await collect_evidence_async(consultation_input, self._providers)
        return self._build_bundle(consultation_input, raw_evidence)

    def _build_bundle(
        self,
        consultation_input: ConsultationInput,
        raw_evidence: tuple[ConsultationEvidence, ...],
    ) -> ConsultationEvidenceBundle:
        collected_at = consultation_input.reference_time or self._clock.now_utc()
        metadata = {
            "collected_at": collected_at.isoformat(),
            "provider_count": len(self._providers),
            "provider_sources": provider_sources(self._providers),
            "raw_evidence_count": len(raw_evidence),
            "normalized_evidence_count": len(raw_evidence),
        }
        bundle = self._normalizer.build_bundle(raw_evidence, metadata=metadata)
        return ConsultationEvidenceBundle(
            yogas=bundle.yogas,
            dasha=bundle.dasha,
            transit=bundle.transit,
            kp=bundle.kp,
            lal_kitab=bundle.lal_kitab,
            rule_studio=bundle.rule_studio,
            case_learning=bundle.case_learning,
            fusion=bundle.fusion,
            golden_dataset=bundle.golden_dataset,
            professional_report=bundle.professional_report,
            metadata={
                **bundle.metadata,
                "normalized_evidence_count": bundle.evidence_count,
            },
        )


def default_evidence_providers() -> tuple[EvidenceProvider, ...]:
    """Backward-compatible alias for default collection providers."""
    return default_collection_providers()
