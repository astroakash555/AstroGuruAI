"""Vimshottari Dasha Engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from astrology_engine.calculations.ephemeris import EphemerisConfig, EphemerisService
from astrology_engine.calculations.planets import get_planet_by_name
from astrology_engine.core.constants import NAKSHATRA_NAMES
from astrology_engine.dasha.balance import (
    compute_balance_at_birth,
    get_dasha_lord_for_nakshatra,
)
from astrology_engine.dasha.calculator import build_mahadashas, find_active_periods
from astrology_engine.dasha.constants import DEFAULT_MAX_YEARS
from astrology_engine.dasha.serializer import to_json_dict, to_json_string
from astrology_engine.dasha.types import (
    DashaBirthInput,
    MoonNakshatraContext,
    VimshottariDashaResult,
)
from astrology_engine.utilities.datetime_utils import ensure_utc, resolve_timezone
from astrology_engine.utilities.vedic import get_nakshatra


class VimshottariDashaEngine:
    """
    Production-grade Vimshottari dasha computation engine.

    Computes mahadasha, antardasha, and pratyantar dasha timelines from birth
    data and moon nakshatra, with optional Swiss Ephemeris moon refinement.
    """

    def __init__(self, ephemeris_config: EphemerisConfig | None = None) -> None:
        self._ephemeris_config = ephemeris_config or EphemerisConfig()
        self._ephemeris: EphemerisService | None = None

    def _get_ephemeris(self) -> EphemerisService:
        if self._ephemeris is None:
            self._ephemeris = EphemerisService(self._ephemeris_config)
        return self._ephemeris

    def compute(
        self,
        birth_input: DashaBirthInput,
        *,
        reference_datetime: datetime | None = None,
        max_years: float = DEFAULT_MAX_YEARS,
    ) -> VimshottariDashaResult:
        """Compute full Vimshottari dasha tree."""
        birth_datetime = self._resolve_birth_datetime(birth_input)
        moon_context = self._resolve_moon_context(birth_input, birth_datetime)
        balance = compute_balance_at_birth(moon_context.longitude)
        mahadashas = build_mahadashas(birth_datetime, balance, max_years=max_years)

        reference = ensure_utc(reference_datetime) if reference_datetime else birth_datetime
        current = find_active_periods(mahadashas, reference)

        return VimshottariDashaResult(
            system="vimshottari",
            birth_datetime=birth_datetime,
            birth_place=birth_input.birth_place,
            timezone=birth_input.timezone,
            moon=moon_context,
            balance=balance,
            current=current,
            mahadashas=mahadashas,
        )

    def compute_json(
        self,
        birth_input: DashaBirthInput,
        *,
        reference_datetime: datetime | None = None,
        max_years: float = DEFAULT_MAX_YEARS,
    ) -> dict[str, Any]:
        """Compute dasha and return structured JSON dictionary."""
        result = self.compute(
            birth_input,
            reference_datetime=reference_datetime,
            max_years=max_years,
        )
        return to_json_dict(result)

    def compute_json_string(
        self,
        birth_input: DashaBirthInput,
        *,
        reference_datetime: datetime | None = None,
        max_years: float = DEFAULT_MAX_YEARS,
        indent: int | None = 2,
    ) -> str:
        """Compute dasha and return formatted JSON string."""
        result = self.compute(
            birth_input,
            reference_datetime=reference_datetime,
            max_years=max_years,
        )
        return to_json_string(result, indent=indent)

    def _resolve_birth_datetime(self, birth_input: DashaBirthInput) -> datetime:
        tz = resolve_timezone(birth_input.timezone)
        localized = datetime.combine(
            birth_input.date_of_birth,
            birth_input.birth_time.replace(microsecond=0),
            tzinfo=tz,
        )
        return ensure_utc(localized)

    def _resolve_moon_context(
        self,
        birth_input: DashaBirthInput,
        birth_datetime: datetime,
    ) -> MoonNakshatraContext:
        moon_longitude = birth_input.moon_longitude

        if moon_longitude is None and birth_input.latitude is not None and birth_input.longitude is not None:
            moon_longitude = self._moon_longitude_from_ephemeris(birth_datetime)

        if moon_longitude is None:
            moon_longitude = self._approximate_longitude_from_nakshatra(birth_input.moon_nakshatra)

        nakshatra = get_nakshatra(moon_longitude)
        expected_lord = get_dasha_lord_for_nakshatra(birth_input.moon_nakshatra)

        if nakshatra.name.lower() != birth_input.moon_nakshatra.strip().lower():
            raise ValueError(
                f"Moon nakshatra mismatch: computed '{nakshatra.name}' "
                f"but input was '{birth_input.moon_nakshatra}'."
            )
        if nakshatra.lord != expected_lord:
            raise ValueError(
                f"Dasha lord mismatch for nakshatra '{birth_input.moon_nakshatra}'."
            )

        return MoonNakshatraContext(
            longitude=moon_longitude,
            nakshatra=nakshatra.name,
            nakshatra_index=nakshatra.index,
            pada=nakshatra.pada,
            lord=nakshatra.lord,
        )

    def _moon_longitude_from_ephemeris(self, birth_datetime: datetime) -> float:
        ephemeris = self._get_ephemeris()
        julian_day = ephemeris.get_julian_day(birth_datetime)
        from astrology_engine.calculations.planets import calculate_planetary_positions

        planets = calculate_planetary_positions(ephemeris, julian_day)
        moon = get_planet_by_name(planets, "Moon")
        return moon.longitude

    @staticmethod
    def _approximate_longitude_from_nakshatra(nakshatra_name: str) -> float:
        """Use nakshatra midpoint when precise moon longitude is unavailable."""
        normalized = nakshatra_name.strip().lower()
        for index, name in enumerate(NAKSHATRA_NAMES):
            if name.lower() == normalized:
                from astrology_engine.core.constants import DEGREES_PER_NAKSHATRA

                return index * DEGREES_PER_NAKSHATRA + (DEGREES_PER_NAKSHATRA / 2.0)
        raise ValueError(f"Unknown nakshatra: {nakshatra_name}")
