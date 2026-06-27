"""Transit Engine orchestrator."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from astrology_engine.calculations.ephemeris import EphemerisConfig, EphemerisService
from astrology_engine.core.constants import SIGN_NAMES_EN
from astrology_engine.core.types import VedicChartBundle
from astrology_engine.transits.calculator import TransitCalculator, build_transit_input_from_chart
from astrology_engine.transits.daily import build_daily_transit
from astrology_engine.transits.monthly import build_monthly_transit
from astrology_engine.transits.serializer import to_json_dict, to_json_string
from astrology_engine.transits.types import TransitAnalysisResult, TransitInput
from astrology_engine.transits.yearly import build_yearly_transit


class TransitEngine:
    """
    Gochar (transit) engine for Saturn, Jupiter, Rahu, and Ketu.

    Supports daily, monthly, and yearly analysis windows relative to a natal chart.
    """

    def __init__(self, config: EphemerisConfig | None = None) -> None:
        self._config = config or EphemerisConfig()
        self._ephemeris = EphemerisService(self._config)
        self._calculator = TransitCalculator(self._ephemeris)

    def analyze(
        self,
        transit_input: TransitInput,
        *,
        target_date: date | None = None,
        include_daily: bool = True,
        include_monthly: bool = True,
        include_yearly: bool = True,
    ) -> TransitAnalysisResult:
        """Run transit analysis for configured time horizons."""
        ref = target_date or date.today()
        daily = build_daily_transit(self._calculator, transit_input, ref) if include_daily else None
        monthly = (
            build_monthly_transit(self._calculator, transit_input, ref.year, ref.month)
            if include_monthly
            else None
        )
        yearly = build_yearly_transit(self._calculator, transit_input, ref.year) if include_yearly else None

        def pick(planet: str):
            if daily:
                return next(item for item in daily.analyses if item.planet == planet)
            if monthly:
                return next(item for item in monthly.analyses if item.planet == planet)
            return next(item for item in yearly.analyses if item.planet == planet)

        return TransitAnalysisResult(
            computed_at=datetime.now(timezone.utc),
            natal_lagna_sign=SIGN_NAMES_EN[transit_input.natal_lagna_sign_index],
            natal_moon_sign=SIGN_NAMES_EN[transit_input.natal_moon_sign_index],
            daily=daily,
            monthly=monthly,
            yearly=yearly,
            saturn=pick("Saturn"),
            jupiter=pick("Jupiter"),
            rahu=pick("Rahu"),
            ketu=pick("Ketu"),
            metadata={
                "engine": "transit_engine_v1",
                "reference_date": ref.isoformat(),
                "planets_analyzed": ["Saturn", "Jupiter", "Rahu", "Ketu"],
            },
        )

    def analyze_chart(
        self,
        chart: VedicChartBundle,
        *,
        target_date: date | None = None,
        timezone: str | None = None,
        **kwargs: Any,
    ) -> TransitAnalysisResult:
        """Analyze transits using a computed natal chart bundle."""
        tz = timezone or chart.metadata.datetime_utc.tzinfo
        tz_name = getattr(tz, "key", "UTC") if tz else "UTC"
        transit_input = build_transit_input_from_chart(chart, timezone=str(tz_name))
        return self.analyze(transit_input, target_date=target_date, **kwargs)

    def analyze_json(self, transit_input: TransitInput, **kwargs: Any) -> dict[str, Any]:
        return to_json_dict(self.analyze(transit_input, **kwargs))

    def analyze_chart_json(self, chart: VedicChartBundle, **kwargs: Any) -> dict[str, Any]:
        return to_json_dict(self.analyze_chart(chart, **kwargs))

    def analyze_json_string(self, transit_input: TransitInput, **kwargs: Any) -> str:
        return to_json_string(self.analyze(transit_input, **kwargs))
