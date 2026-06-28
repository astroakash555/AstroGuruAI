"""Shared helpers for golden chart tests without report-layer imports."""

from __future__ import annotations

from datetime import date, datetime, time

from astrology_engine.core.base import BirthData
from astrology_engine.core.types import VedicChartBundle
from astrology_engine.dasha.types import DashaBirthInput
from astrology_engine.utilities.datetime_utils import ensure_utc, resolve_timezone


def build_birth_data(
    *,
    date_of_birth: date,
    birth_time: time,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> BirthData:
    """Construct UTC BirthData from localized birth date and time."""
    localized = datetime.combine(date_of_birth, birth_time.replace(microsecond=0))
    localized = localized.replace(tzinfo=resolve_timezone(timezone_name))
    return BirthData(
        datetime_utc=ensure_utc(localized),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_name,
    )


def build_dasha_input_from_bundle(
    chart: VedicChartBundle,
    *,
    birth_place: str,
    timezone: str,
) -> DashaBirthInput:
    """Build Vimshottari dasha input from a computed chart bundle."""
    localized = chart.metadata.datetime_utc.astimezone(resolve_timezone(timezone))
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
        timezone=timezone,
        moon_nakshatra=moon.nakshatra.name,
        latitude=chart.metadata.latitude,
        longitude=chart.metadata.longitude,
        moon_longitude=moon.longitude,
    )
