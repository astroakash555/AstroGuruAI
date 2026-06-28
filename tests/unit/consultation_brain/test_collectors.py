"""Tests for EvidenceCollector."""

from backend.app.services.consultation_brain.clock import FixedClock
from backend.app.services.consultation_brain.collectors import EvidenceCollector, collect_evidence_async
from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationInput
from backend.app.services.consultation_brain.normalizer import EvidenceNormalizer
from backend.app.services.consultation_brain.providers import default_collection_providers


def test_collector_returns_normalized_bundle(sample_consultation_input):
    collector = EvidenceCollector()
    bundle = collector.collect(sample_consultation_input)
    assert bundle.evidence_count > 0
    assert bundle.metadata["provider_count"] == 10
    assert bundle.metadata["collected_at"] == sample_consultation_input.reference_time.isoformat()
    assert len(bundle.yogas) >= 1
    assert len(bundle.professional_report) == 1


def test_collector_is_deterministic(sample_consultation_input):
    fixed_clock = FixedClock(sample_consultation_input.reference_time)
    collector = EvidenceCollector(clock=fixed_clock)
    first = collector.collect(
        ConsultationInput(
            unified_report=sample_consultation_input.unified_report,
            professional_report=sample_consultation_input.professional_report,
        )
    )
    second = collector.collect(
        ConsultationInput(
            unified_report=sample_consultation_input.unified_report,
            professional_report=sample_consultation_input.professional_report,
        )
    )
    assert first == second


def test_collector_accepts_injected_providers(sample_unified_report):
    providers = (default_collection_providers()[0],)
    collector = EvidenceCollector(providers=providers)
    bundle = collector.collect(ConsultationInput(unified_report=sample_unified_report))
    assert all(item.source == EvidenceSource.YOGAS for item in bundle.all_evidence)


def test_collector_exposes_injected_dependencies():
    collector = EvidenceCollector()
    assert collector.providers
    assert isinstance(collector.normalizer, EvidenceNormalizer)
    assert collector.clock


async def test_collector_async_matches_sync(sample_consultation_input):
    collector = EvidenceCollector()
    sync_bundle = collector.collect(sample_consultation_input)
    async_bundle = await collector.collect_async(sample_consultation_input)
    assert async_bundle == sync_bundle


async def test_collect_evidence_async_helper(sample_consultation_input):
    providers = default_collection_providers()
    async_items = await collect_evidence_async(sample_consultation_input, providers)
    assert len(async_items) > 0
