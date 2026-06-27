"""Input builders for report orchestration."""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from astrology_engine.core.base import BirthData
from astrology_engine.core.types import VedicChartBundle
from astrology_engine.dasha.types import DashaBirthInput
from astrology_engine.utilities.datetime_utils import resolve_timezone


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


def build_birth_data_from_report(
    *,
    date_of_birth: date,
    birth_time: time,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> BirthData:
    """Construct birth data from localized birth date and time."""
    localized = datetime.combine(date_of_birth, birth_time.replace(microsecond=0))
    localized = localized.replace(tzinfo=resolve_timezone(timezone_name))
    return BirthData(
        datetime_utc=localized.astimezone(timezone.utc),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_name,
    )
