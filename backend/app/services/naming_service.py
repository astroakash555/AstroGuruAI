"""Naming suggestion service."""

from __future__ import annotations

from typing import Any

from naming_engine import NamingEngine, NamingInput


class NamingService:
    def __init__(self) -> None:
        self._engine = NamingEngine()

    def suggest_names(
        self,
        *,
        nakshatra: str,
        pada: int,
        rashi_sign_index: int,
        gender: str = "neutral",
        count: int = 8,
    ) -> dict[str, Any]:
        payload = self._engine.suggest_json(
            NamingInput(
                nakshatra=nakshatra,
                pada=pada,
                rashi_sign_index=rashi_sign_index,
                gender=gender,
                count=count,
            )
        )
        return {"naming": payload}
