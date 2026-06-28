"""Input builders for report orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from astrology_engine.core.base import BirthData
from astrology_engine.core.types import VedicChartBundle
from astrology_engine.dasha.types import DashaBirthInput
from astrology_engine.utilities.datetime_utils import ensure_utc, resolve_timezone

if TYPE_CHECKING:
    from backend.app.models.birth_detail import BirthDetail


@dataclass(frozen=True)
class BirthContext:
    """Normalized birth inputs used across chart, dasha, and transit pipelines."""

    date_of_birth: date
    birth_time: time
    birth_place: str
    timezone_name: str
    latitude: float
    longitude: float
    birth_detail_id: str | None = None


def build_birth_data(
    *,
    datetime_utc: datetime,
    latitude: float,
    longitude: float,
    timezone: str,
) -> BirthData:
    """Construct canonical birth data for chart computation."""
    return BirthData(
        datetime_utc=datetime_utc,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )


def build_dasha_input_from_chart(
    chart: VedicChartBundle,
    *,
    birth_place: str,
    timezone: str | None = None,
) -> DashaBirthInput:
    """Build Vimshottari dasha input from a computed chart bundle."""
    tz_name = timezone or chart.metadata.datetime_utc.tzinfo
    tz_key = getattr(tz_name, "key", "UTC") if tz_name else "UTC"
    localized = chart.metadata.datetime_utc.astimezone(resolve_timezone(tz_key))
    moon = next(planet for planet in chart.lagna_kundali.planets if planet.name == "Moon")

    return DashaBirthInput(
        date_of_birth=localized.date(),
        birth_time=time(
            localized.hour,
            localized.minute,
            localized.second,
            localized.microsecond,
        ),
        birth_place=birth_place,
        timezone=tz_key,
        moon_nakshatra=moon.nakshatra.name,
        latitude=chart.metadata.latitude,
        longitude=chart.metadata.longitude,
        moon_longitude=moon.longitude,
    )


def build_birth_context_from_birth_detail(birth_detail: BirthDetail) -> BirthContext:
    """Extract localized birth fields from a persisted BirthDetail row."""
    localized = birth_detail.birth_datetime.astimezone(ZoneInfo(birth_detail.timezone))
    return BirthContext(
        date_of_birth=localized.date(),
        birth_time=localized.time().replace(microsecond=0),
        birth_place=birth_detail.birth_place_name,
        timezone_name=birth_detail.timezone,
        latitude=float(birth_detail.latitude),
        longitude=float(birth_detail.longitude),
        birth_detail_id=str(birth_detail.id),
    )


def build_birth_context_from_payload(
    *,
    date_of_birth: date,
    birth_time: time,
    birth_place: str,
    timezone_name: str,
    latitude: float | Decimal,
    longitude: float | Decimal,
    birth_detail_id: str | None = None,
) -> BirthContext:
    """Build birth context from explicit API payload values."""
    return BirthContext(
        date_of_birth=date_of_birth,
        birth_time=birth_time.replace(microsecond=0),
        birth_place=birth_place,
        timezone_name=timezone_name,
        latitude=float(latitude),
        longitude=float(longitude),
        birth_detail_id=birth_detail_id,
    )


def build_birth_data_from_context(context: BirthContext) -> BirthData:
    """Convert a BirthContext to canonical UTC BirthData for Swiss Ephemeris."""
    localized = datetime.combine(context.date_of_birth, context.birth_time)
    localized = localized.replace(tzinfo=resolve_timezone(context.timezone_name))
    return BirthData(
        datetime_utc=ensure_utc(localized),
        latitude=context.latitude,
        longitude=context.longitude,
        timezone=context.timezone_name,
    )


def build_birth_data_from_report(
    *,
    date_of_birth: date,
    birth_time: time,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> BirthData:
    """Construct birth data from localized birth date and time."""
    context = build_birth_context_from_payload(
        date_of_birth=date_of_birth,
        birth_time=birth_time,
        birth_place="",
        timezone_name=timezone_name,
        latitude=latitude,
        longitude=longitude,
    )
    return build_birth_data_from_context(context)
