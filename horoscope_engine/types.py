"""Horoscope engine types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True)
class HoroscopeInput:
    moon_sign_index: int
    lagna_sign_index: int
    current_mahadasha: str | None
    current_antardasha: str | None
    transit_summary: dict[str, str]
    target_date: date


@dataclass(frozen=True)
class HoroscopePeriod:
    period_type: str
    start_date: date
    end_date: date
    theme: str
    focus_areas: tuple[str, ...]
    guidance: tuple[str, ...]
    energy_score: float


@dataclass(frozen=True)
class HoroscopeResult:
    generated_at: datetime
    moon_sign: str
    lagna_sign: str
    daily: HoroscopePeriod
    weekly: HoroscopePeriod
    monthly: HoroscopePeriod
    metadata: dict[str, object] = field(default_factory=dict)
