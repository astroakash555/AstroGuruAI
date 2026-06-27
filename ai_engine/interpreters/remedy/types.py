"""Remedy generation types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class GeneratedRemedy:
    remedy_type: str
    astrology_system: str
    title: str
    description: str
    planet: str | None
    house: int | None
    priority: int
    confidence_score: float
    expected_effect: str


@dataclass(frozen=True)
class RemedyGenerationInput:
    report_json: dict[str, Any]
    max_remedies: int = 12


@dataclass(frozen=True)
class RemedyGenerationResult:
    generated_at: datetime
    remedies: tuple[GeneratedRemedy, ...]
    summary: str
    metadata: dict[str, object] = field(default_factory=dict)
