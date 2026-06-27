"""Base yoga rule contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from astrology_engine.yogas.context import ChartContext
from astrology_engine.yogas.types import YogaDetection


class YogaRule(ABC):
    """Abstract yoga detection rule — implement and register to extend the engine."""

    yoga_id: str
    yoga_name: str
    category: str

    @abstractmethod
    def detect(self, context: ChartContext) -> YogaDetection:
        """Evaluate the yoga against chart context."""
        raise NotImplementedError
