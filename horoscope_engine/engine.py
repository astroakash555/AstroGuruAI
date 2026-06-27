"""Horoscope generation engine."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from horoscope_engine.constants import MOON_THEMES, SIGN_NAMES
from horoscope_engine.schemas import HoroscopeJSON
from horoscope_engine.types import HoroscopeInput, HoroscopePeriod, HoroscopeResult


class HoroscopeEngine:
    """Generate daily, weekly, and monthly horoscopes from transit and dasha context."""

    def generate(self, horoscope_input: HoroscopeInput) -> HoroscopeResult:
        moon_sign = SIGN_NAMES[horoscope_input.moon_sign_index]
        lagna_sign = SIGN_NAMES[horoscope_input.lagna_sign_index]
        theme = MOON_THEMES.get(horoscope_input.moon_sign_index, "general_balance")

        daily = self._build_period(
            period_type="daily",
            start=horoscope_input.target_date,
            end=horoscope_input.target_date,
            theme=theme,
            horoscope_input=horoscope_input,
            energy_base=0.62,
        )
        weekly = self._build_period(
            period_type="weekly",
            start=horoscope_input.target_date,
            end=horoscope_input.target_date + timedelta(days=6),
            theme=theme,
            horoscope_input=horoscope_input,
            energy_base=0.68,
        )
        monthly = self._build_period(
            period_type="monthly",
            start=horoscope_input.target_date.replace(day=1),
            end=self._month_end(horoscope_input.target_date),
            theme=theme,
            horoscope_input=horoscope_input,
            energy_base=0.74,
        )

        return HoroscopeResult(
            generated_at=datetime.now(timezone.utc),
            moon_sign=moon_sign,
            lagna_sign=lagna_sign,
            daily=daily,
            weekly=weekly,
            monthly=monthly,
            metadata={"engine": "horoscope_engine_v1", "source": "transit_dasha_rules"},
        )

    def generate_json(self, horoscope_input: HoroscopeInput) -> dict[str, Any]:
        result = self.generate(horoscope_input)
        payload = HoroscopeJSON(
            generated_at=result.generated_at,
            moon_sign=result.moon_sign,
            lagna_sign=result.lagna_sign,
            daily=_period_dict(result.daily),
            weekly=_period_dict(result.weekly),
            monthly=_period_dict(result.monthly),
            metadata=dict(result.metadata),
        )
        return payload.model_dump(mode="json")

    def _build_period(
        self,
        *,
        period_type: str,
        start: date,
        end: date,
        theme: str,
        horoscope_input: HoroscopeInput,
        energy_base: float,
    ) -> HoroscopePeriod:
        focus = [f"Moon theme: {theme}"]
        guidance = []
        if horoscope_input.current_mahadasha:
            focus.append(f"Mahadasha: {horoscope_input.current_mahadasha}")
            guidance.append(
                f"Align actions with {horoscope_input.current_mahadasha} mahadasha priorities."
            )
        if horoscope_input.current_antardasha:
            focus.append(f"Antardasha: {horoscope_input.current_antardasha}")
        for planet, summary in horoscope_input.transit_summary.items():
            guidance.append(f"{planet}: {summary}")

        return HoroscopePeriod(
            period_type=period_type,
            start_date=start,
            end_date=end,
            theme=theme,
            focus_areas=tuple(focus),
            guidance=tuple(guidance[:5]),
            energy_score=round(energy_base, 3),
        )

    @staticmethod
    def _month_end(target: date) -> date:
        if target.month == 12:
            return date(target.year, 12, 31)
        next_month = date(target.year, target.month + 1, 1)
        return next_month - timedelta(days=1)


def _period_dict(period: HoroscopePeriod) -> dict[str, Any]:
    return {
        "period_type": period.period_type,
        "start_date": period.start_date,
        "end_date": period.end_date,
        "theme": period.theme,
        "focus_areas": list(period.focus_areas),
        "guidance": list(period.guidance),
        "energy_score": period.energy_score,
    }
