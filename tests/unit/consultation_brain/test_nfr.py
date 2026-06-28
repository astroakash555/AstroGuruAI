"""Non-functional requirement tests for consultation brain."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from types import MappingProxyType

import pytest

from backend.app.services.consultation_brain.brain import ConsultationBrain
from backend.app.services.consultation_brain.clock import FixedClock, UtcClock
from backend.app.services.consultation_brain.config import ConsultationBrainConfig
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource, SOURCE_WEIGHTS
from backend.app.services.consultation_brain.models import ConsultationBrainOutput, ConsultationEvidence, ConsultationInput
from backend.app.services.consultation_brain.protocols import AsyncEvidenceProvider, Clock, EvidenceProvider
from backend.app.services.consultation_brain.collectors import (
    as_async_provider,
    collect_evidence,
    collect_evidence_async,
    default_evidence_providers,
)
from backend.app.services.consultation_brain.providers import YogaEvidenceProvider


class NativeAsyncProvider:
    source = EvidenceSource.FUSION

    async def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        return ()


def test_source_weights_are_read_only():
    with pytest.raises(TypeError):
        SOURCE_WEIGHTS[next(iter(SOURCE_WEIGHTS))] = 0.1  # type: ignore[index]


def test_evidence_metadata_is_immutable():
    evidence = ConsultationEvidence(
        evidence_id="evidence-yogas-1",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        title="Title",
        summary="Summary",
        weight=0.5,
        confidence=0.0,
        metadata={"key": "value"},
    )
    assert isinstance(evidence.metadata, MappingProxyType)
    with pytest.raises(TypeError):
        evidence.metadata["key"] = "changed"  # type: ignore[index]


def test_default_providers_return_fresh_instances():
    first = default_evidence_providers()
    second = default_evidence_providers()
    assert first is not second
    assert first[0] is not second[0]


def test_brain_run_is_deterministic_with_fixed_clock_and_reference_time(sample_unified_report):
    fixed = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    consultation_input = ConsultationInput(
        unified_report=sample_unified_report,
        problem_text="Career",
        reference_time=fixed,
    )
    brain = ConsultationBrain(clock=FixedClock(datetime(2099, 1, 1, tzinfo=UTC)))
    first = brain.run(consultation_input)
    second = brain.run(consultation_input)
    assert first == second
    assert first.generated_at == fixed


def test_brain_uses_injected_clock_when_reference_time_missing(sample_unified_report):
    fixed = datetime(2026, 3, 15, 8, 30, tzinfo=UTC)
    consultation_input = ConsultationInput(unified_report=sample_unified_report)
    output = ConsultationBrain(clock=FixedClock(fixed)).run(consultation_input)
    assert output.generated_at == fixed


def test_brain_config_is_frozen_and_injectable():
    providers = default_evidence_providers()
    clock = FixedClock(datetime(2026, 6, 1, tzinfo=UTC))
    config = ConsultationBrainConfig(evidence_providers=providers, clock=clock)
    brain = ConsultationBrain(config=config)
    assert brain.evidence_providers == providers
    assert isinstance(brain.clock, FixedClock)


async def test_run_async_matches_sync_output(sample_consultation_input):
    brain = ConsultationBrain()
    sync_output = brain.run(sample_consultation_input)
    async_output = await brain.run_async(sample_consultation_input)
    assert async_output == sync_output


async def test_collect_evidence_async_matches_sync(sample_consultation_input):
    providers = default_evidence_providers()
    sync_items = collect_evidence(sample_consultation_input, providers)
    async_items = await collect_evidence_async(sample_consultation_input, providers)
    assert async_items == sync_items


async def test_run_json_async_returns_serializable_dict(sample_consultation_input):
    payload = await ConsultationBrain().run_json_async(sample_consultation_input)
    assert payload["metadata"]["engine_version"]
    assert isinstance(payload["stage_trace"], list)


async def test_provider_collect_async_delegates_to_sync(sample_unified_report):
    provider = YogaEvidenceProvider()
    consultation_input = ConsultationInput(unified_report=sample_unified_report)
    sync_result = provider.collect(consultation_input)
    async_result = await provider.collect_async(consultation_input)
    assert async_result == sync_result


def test_native_async_provider_is_not_double_wrapped():
    provider = NativeAsyncProvider()
    adapted = as_async_provider(provider)
    assert adapted is provider


def test_sync_provider_adapted_for_async_protocol():
    provider = default_evidence_providers()[0]
    adapted = as_async_provider(provider)
    assert isinstance(adapted, AsyncEvidenceProvider)


def test_brain_parallel_runs_are_thread_safe(sample_consultation_input):
    brain = ConsultationBrain()

    def run_pipeline() -> ConsultationBrainOutput:
        return brain.run(sample_consultation_input)

    with ThreadPoolExecutor(max_workers=4) as executor:
        outputs = list(executor.map(lambda _: run_pipeline(), range(8)))

    assert all(output == outputs[0] for output in outputs)


def test_clock_protocol_compliance():
    assert isinstance(UtcClock(), Clock)
    assert isinstance(FixedClock(datetime(2026, 1, 1, tzinfo=UTC)), Clock)


def test_evidence_provider_protocol_compliance():
    for provider in default_evidence_providers():
        assert isinstance(provider, EvidenceProvider)
