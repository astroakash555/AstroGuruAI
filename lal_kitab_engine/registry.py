"""Lal Kitab rule registry."""

from __future__ import annotations

from lal_kitab_engine.base import LalKitabRule
from lal_kitab_engine.context import LalKitabContext
from lal_kitab_engine.types import LalKitabFinding


class LalKitabRegistry:
    """Registry of Lal Kitab analysis rules."""

    def __init__(self) -> None:
        self._rules: dict[str, LalKitabRule] = {}

    def register(self, rule: LalKitabRule) -> None:
        self._rules[rule.finding_id] = rule

    def unregister(self, finding_id: str) -> None:
        self._rules.pop(finding_id, None)

    @property
    def rules(self) -> tuple[LalKitabRule, ...]:
        return tuple(self._rules.values())

    def analyze_all(self, context: LalKitabContext) -> tuple[LalKitabFinding, ...]:
        return tuple(rule.analyze(context) for rule in self._rules.values())
