"""Knowledge rule models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RuleConditions:
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()
    signs: tuple[str, ...] = ()
    nakshatras: tuple[str, ...] = ()
    aspects: tuple[str, ...] = ()
    dasha_lords: tuple[str, ...] = ()
    transits: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AstrologyRule:
    rule_id: str
    system: str
    domain: str
    category: str
    title: str
    description: str
    conditions: RuleConditions
    effects: tuple[str, ...]
    strength_weight: float
    confidence: float
    tags: tuple[str, ...] = field(default_factory=tuple)
    severity: str = "moderate"
