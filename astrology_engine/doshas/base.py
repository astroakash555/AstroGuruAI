"""Base dosha rule contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.yogas.context import ChartContext


class DoshaRule(ABC):
    """Abstract dosha detection rule — implement and register to extend the engine."""

    dosha_id: str
    dosha_name: str
    category: str

    @abstractmethod
    def detect(self, context: ChartContext) -> DoshaDetection:
        """Evaluate the dosha against chart context."""
        raise NotImplementedError
