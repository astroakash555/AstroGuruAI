"""Horoscope service."""

from __future__ import annotations

from datetime import date
from typing import Any

from horoscope_engine import HoroscopeEngine, HoroscopeInput


class HoroscopeService:
    def __init__(self) -> None:
        self._engine = HoroscopeEngine()

    def generate_horoscope(
        self,
        *,
        moon_sign_index: int,
        lagna_sign_index: int,
        current_mahadasha: str | None = None,
        current_antardasha: str | None = None,
        transit_summary: dict[str, str] | None = None,
        target_date: date | None = None,
    ) -> dict[str, Any]:
        payload = self._engine.generate_json(
            HoroscopeInput(
                moon_sign_index=moon_sign_index,
                lagna_sign_index=lagna_sign_index,
                current_mahadasha=current_mahadasha,
                current_antardasha=current_antardasha,
                transit_summary=transit_summary or {},
                target_date=target_date or date.today(),
            )
        )
        return {"horoscope": payload}
