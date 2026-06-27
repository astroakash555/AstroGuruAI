"""Typed models for dosha detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DoshaCondition:
    """Single evaluated condition within a dosha rule."""

    name: str
    met: bool
    detail: str


@dataclass(frozen=True)
class DoshaDetection:
    """Result of a single dosha rule evaluation."""

    dosha_id: str
    dosha_name: str
    category: str
    is_present: bool
    severity: float
    severity_level: str
    subtype: str | None
    description: str
    planets_involved: tuple[str, ...]
    houses_involved: tuple[int, ...]
    conditions: tuple[DoshaCondition, ...]
    mitigating_factors: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class DoshaDetectionSummary:
    """Aggregate statistics for a dosha detection run."""

    total_rules: int
    present_count: int
    absent_count: int
    average_severity: float
    highest_severity: float


@dataclass(frozen=True)
class DoshaDetectionResult:
    """Complete dosha detection output."""

    detected_at: datetime
    lagna_sign: str
    moon_sign: str
    doshas: tuple[DoshaDetection, ...]
    present_doshas: tuple[DoshaDetection, ...]
    summary: DoshaDetectionSummary
    metadata: dict[str, object] = field(default_factory=dict)
