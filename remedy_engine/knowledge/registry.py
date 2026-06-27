"""Remedy knowledge registry."""

from __future__ import annotations

from remedy_engine.knowledge.kp import KP_REMEDIES
from remedy_engine.knowledge.lal_kitab import LAL_KITAB_REMEDIES
from remedy_engine.knowledge.vedic import VEDIC_REMEDIES
from remedy_engine.models.remedy import RemedyRecord


class RemedyKnowledgeRegistry:
    """Central registry of machine-readable remedy records."""

    def __init__(self, remedies: tuple[RemedyRecord, ...] | None = None) -> None:
        self._remedies: dict[str, RemedyRecord] = {}
        for remedy in remedies or DEFAULT_REMEDIES:
            self.register(remedy)

    @property
    def remedies(self) -> tuple[RemedyRecord, ...]:
        return tuple(self._remedies.values())

    def register(self, remedy: RemedyRecord) -> None:
        self._remedies[remedy.remedy_id] = remedy

    def get(self, remedy_id: str) -> RemedyRecord | None:
        return self._remedies.get(remedy_id)

    def by_system(self, astrology_system: str) -> tuple[RemedyRecord, ...]:
        return tuple(
            remedy
            for remedy in self._remedies.values()
            if remedy.astrology_system == astrology_system
        )

    def by_planet(self, planet: str) -> tuple[RemedyRecord, ...]:
        return tuple(
            remedy
            for remedy in self._remedies.values()
            if remedy.planet == planet
        )

    def by_category(self, category: str) -> tuple[RemedyRecord, ...]:
        return tuple(
            remedy
            for remedy in self._remedies.values()
            if remedy.category == category
        )


DEFAULT_REMEDIES: tuple[RemedyRecord, ...] = VEDIC_REMEDIES + LAL_KITAB_REMEDIES + KP_REMEDIES
