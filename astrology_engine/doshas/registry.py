"""Dosha rule registry for pluggable detection."""

from __future__ import annotations

from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.yogas.context import ChartContext


class DoshaRegistry:
    """Registry of dosha rules supporting runtime extension."""

    def __init__(self) -> None:
        self._rules: dict[str, DoshaRule] = {}

    def register(self, rule: DoshaRule) -> None:
        if rule.dosha_id in self._rules:
            raise ValueError(f"Dosha rule '{rule.dosha_id}' is already registered.")
        self._rules[rule.dosha_id] = rule

    def unregister(self, dosha_id: str) -> None:
        self._rules.pop(dosha_id, None)

    def get(self, dosha_id: str) -> DoshaRule | None:
        return self._rules.get(dosha_id)

    def rules(self) -> tuple[DoshaRule, ...]:
        return tuple(self._rules.values())

    def detect_all(self, context: ChartContext) -> tuple[DoshaDetection, ...]:
        results = [rule.detect(context) for rule in self._rules.values()]
        return tuple(sorted(results, key=lambda item: item.dosha_id))
