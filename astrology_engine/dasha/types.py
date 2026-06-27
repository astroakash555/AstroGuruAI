"""Typed models for Vimshottari dasha calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time


@dataclass(frozen=True)
class DashaBirthInput:
    """Input required to compute Vimshottari dasha."""

    date_of_birth: date
    birth_time: time
    birth_place: str
    timezone: str
    moon_nakshatra: str
    latitude: float | None = None
    longitude: float | None = None
    moon_longitude: float | None = None


@dataclass(frozen=True)
class DashaBalance:
    """Remaining balance of the birth mahadasha."""

    lord: str
    elapsed_fraction: float
    remaining_fraction: float
    duration_years: float
    duration_days: float


@dataclass(frozen=True)
class PratyantarDashaPeriod:
    """Pratyantar (sukshma) dasha period."""

    lord: str
    start: datetime
    end: datetime
    duration_years: float
    duration_days: float
    level: str = "pratyantar"


@dataclass(frozen=True)
class AntardashaPeriod:
    """Antardasha (bhukti) period with nested pratyantar dashas."""

    lord: str
    start: datetime
    end: datetime
    duration_years: float
    duration_days: float
    pratyantar_dashas: tuple[PratyantarDashaPeriod, ...]
    level: str = "antardasha"


@dataclass(frozen=True)
class MahadashaPeriod:
    """Mahadasha period with nested antardashas."""

    lord: str
    start: datetime
    end: datetime
    duration_years: float
    duration_days: float
    antardashas: tuple[AntardashaPeriod, ...]
    level: str = "mahadasha"


@dataclass(frozen=True)
class MoonNakshatraContext:
    """Moon placement context used for dasha seeding."""

    longitude: float
    nakshatra: str
    nakshatra_index: int
    pada: int
    lord: str


@dataclass(frozen=True)
class ActiveDashaPeriod:
    """Currently active dasha at a reference datetime."""

    lord: str
    start: datetime
    end: datetime
    duration_years: float
    duration_days: float


@dataclass(frozen=True)
class VimshottariDashaResult:
    """Complete Vimshottari dasha computation result."""

    system: str
    birth_datetime: datetime
    birth_place: str
    timezone: str
    moon: MoonNakshatraContext
    balance: DashaBalance
    current: dict[str, ActiveDashaPeriod | None]
    mahadashas: tuple[MahadashaPeriod, ...]
