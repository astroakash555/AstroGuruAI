"""Protocol definitions for consultation brain extension points."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationInput


@runtime_checkable
class Clock(Protocol):
    """Injectable time source for deterministic pipeline output."""

    def now_utc(self) -> datetime:
        """Return the current UTC timestamp."""


@runtime_checkable
class EvidenceProvider(Protocol):
    """Collects normalized-ready evidence from one intelligence subsystem."""

    @property
    def source(self) -> EvidenceSource:
        """Subsystem identifier for collected evidence."""

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        """Return evidence items extracted from the consultation input."""


@runtime_checkable
class AsyncEvidenceProvider(Protocol):
    """Async evidence collector for non-blocking pipeline stages."""

    @property
    def source(self) -> EvidenceSource:
        """Subsystem identifier for collected evidence."""

    async def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        """Return evidence items extracted from the consultation input."""
