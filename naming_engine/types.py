"""Naming suggestion types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class NamingInput:
    nakshatra: str
    pada: int
    rashi_sign_index: int
    gender: str = "neutral"
    count: int = 8


@dataclass(frozen=True)
class NameSuggestion:
    name: str
    syllable_seed: str
    nakshatra: str
    pada: int
    rashi: str
    score: float
    reasoning: str


@dataclass(frozen=True)
class NamingResult:
    generated_at: datetime
    suggestions: tuple[NameSuggestion, ...]
    metadata: dict[str, object] = field(default_factory=dict)
