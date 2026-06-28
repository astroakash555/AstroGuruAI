"""Immutable configuration for consultation brain wiring."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.services.consultation_brain.clock import UtcClock
from backend.app.services.consultation_brain.protocols import Clock, EvidenceProvider
from backend.app.services.consultation_brain.collectors import default_evidence_providers


@dataclass(frozen=True)
class ConsultationBrainConfig:
    """Frozen DI container for orchestrator dependencies."""

    evidence_providers: tuple[EvidenceProvider, ...] = field(default_factory=default_evidence_providers)
    clock: Clock = field(default_factory=UtcClock)
