"""Yoga rule registry for pluggable detection."""

from __future__ import annotations

from astrology_engine.yogas.base import YogaRule
from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.types import YogaDetection


class YogaRegistry:
    """Registry of yoga rules supporting runtime extension."""

    def __init__(self) -> None:
        self._rules: dict[str, YogaRule] = {}

    def register(self, rule: YogaRule) -> None:
        """Register a yoga rule; later registrations with same id are rejected."""
        if rule.yoga_id in self._rules:
            raise ValueError(f"Yoga rule '{rule.yoga_id}' is already registered.")
        self._rules[rule.yoga_id] = rule

    def unregister(self, yoga_id: str) -> None:
        """Remove a yoga rule by id."""
        self._rules.pop(yoga_id, None)

    def get(self, yoga_id: str) -> YogaRule | None:
        return self._rules.get(yoga_id)

    def rules(self) -> tuple[YogaRule, ...]:
        return tuple(self._rules.values())

    def detect_all(self, context: ChartContext) -> tuple[YogaDetection, ...]:
        """Run all registered rules against chart context."""
        results = [rule.detect(context) for rule in self._rules.values()]
        return tuple(sorted(results, key=lambda item: item.yoga_id))
