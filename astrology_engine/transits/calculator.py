"""Transit position calculator using Swiss Ephemeris."""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from astrology_engine.calculations.ephemeris import EphemerisService
from astrology_engine.core.constants import SIGN_NAMES_EN
from astrology_engine.transits.constants import TRANSIT_PLANET_IDS, TRANSIT_PLANETS
from astrology_engine.transits.types import TransitInput, TransitPlanetSnapshot
from astrology_engine.utilities.datetime_utils import ensure_utc, resolve_timezone
from astrology_engine.utilities.vedic import get_nakshatra, get_zodiac_sign, ketu_longitude


class TransitCalculator:
    """Compute sidereal transit positions for slow-moving grahas."""

    def __init__(self, ephemeris: EphemerisService) -> None:
        self._ephemeris = ephemeris

    def snapshot_at(
        self,
        when: datetime,
        transit_input: TransitInput,
    ) -> tuple[TransitPlanetSnapshot, ...]:
        """Compute transit snapshots for all configured grahas at a datetime."""
        utc_dt = ensure_utc(when)
        julian_day = self._ephemeris.get_julian_day(utc_dt)
        snapshots: list[TransitPlanetSnapshot] = []

        for planet_name in TRANSIT_PLANETS:
            snapshots.append(
                self._build_snapshot(planet_name, utc_dt, julian_day, transit_input)
            )
        return tuple(snapshots)

    def snapshots_for_dates(
        self,
        dates: list[date],
        transit_input: TransitInput,
        *,
        local_time: time = time(12, 0),
    ) -> tuple[TransitPlanetSnapshot, ...]:
        """Compute noon-time (local) snapshots for multiple dates."""
        tz = resolve_timezone(transit_input.timezone)
        results: list[TransitPlanetSnapshot] = []
        for day in dates:
            local_dt = datetime.combine(day, local_time, tzinfo=tz)
            results.extend(self.snapshot_at(local_dt, transit_input))
        return tuple(results)

    def _build_snapshot(
        self,
        planet_name: str,
        utc_dt: datetime,
        julian_day: float,
        transit_input: TransitInput,
    ) -> TransitPlanetSnapshot:
        if planet_name == "Ketu":
            rahu_id = self._ephemeris.node_planet_id()
            rahu_lon, rahu_lat, _, rahu_speed = self._ephemeris.calc_planet_ut(julian_day, rahu_id)
            longitude = ketu_longitude(rahu_lon)
            latitude = -rahu_lat
            speed = -rahu_speed
        else:
            planet_id = TRANSIT_PLANET_IDS[planet_name]
            longitude, latitude, _, speed = self._ephemeris.calc_planet_ut(julian_day, planet_id)

        sign = get_zodiac_sign(longitude)
        house_lagna = _house_from_reference(sign.index, transit_input.natal_lagna_sign_index)
        house_moon = _house_from_reference(sign.index, transit_input.natal_moon_sign_index)

        return TransitPlanetSnapshot(
            planet=planet_name,
            datetime=utc_dt,
            longitude=longitude,
            sign=sign,
            house_from_lagna=house_lagna,
            house_from_moon=house_moon,
            is_retrograde=speed < 0,
            nakshatra=get_nakshatra(longitude),
            speed=speed,
        )


def build_transit_input_from_chart(
    chart_bundle,
    *,
    timezone: str = "UTC",
    latitude: float | None = None,
    longitude: float | None = None,
) -> TransitInput:
    """Build transit input from a computed Vedic chart bundle or lagna kundali."""
    from astrology_engine.core.types import LagnaKundali, VedicChartBundle

    if isinstance(chart_bundle, VedicChartBundle):
        lagna = chart_bundle.lagna_kundali
        lat = latitude if latitude is not None else chart_bundle.metadata.latitude
        lon = longitude if longitude is not None else chart_bundle.metadata.longitude
    else:
        lagna = chart_bundle
        lat = latitude or 0.0
        lon = longitude or 0.0

    natal_planets = {planet.name: planet.sign.index for planet in lagna.planets}
    moon = next(item for item in lagna.planets if item.name == "Moon")

    return TransitInput(
        natal_lagna_sign_index=lagna.ascendant.sign.index,
        natal_moon_sign_index=moon.sign.index,
        natal_planets=natal_planets,
        latitude=lat,
        longitude=lon,
        timezone=timezone,
    )


def _house_from_reference(planet_sign_index: int, reference_sign_index: int) -> int:
    return ((planet_sign_index - reference_sign_index) % 12) + 1


def sign_name(index: int) -> str:
    return SIGN_NAMES_EN[index]
