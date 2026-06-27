"""Typed models for yoga detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class YogaCondition:
    """Single evaluated condition within a yoga rule."""

    name: str
    met: bool
    detail: str


@dataclass(frozen=True)
class YogaDetection:
    """Result of a single yoga rule evaluation."""

    yoga_id: str
    yoga_name: str
    category: str
    is_present: bool
    strength: float
    description: str
    planets_involved: tuple[str, ...]
    houses_involved: tuple[int, ...]
    conditions: tuple[YogaCondition, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class YogaDetectionSummary:
    """Aggregate statistics for a detection run."""

    total_rules: int
    present_count: int
    absent_count: int
    average_strength: float


@dataclass(frozen=True)
class YogaDetectionResult:
    """Complete yoga detection output."""

    detected_at: datetime
    lagna_sign: str
    moon_sign: str
    yogas: tuple[YogaDetection, ...]
    present_yogas: tuple[YogaDetection, ...]
    summary: YogaDetectionSummary
    metadata: dict[str, object] = field(default_factory=dict)
