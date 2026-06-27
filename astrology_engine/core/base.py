"""Base classes for astrology engine components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from astrology_engine.core.types import VedicChartBundle


@dataclass(frozen=True)
class BirthData:
    """Canonical birth data input for chart calculations."""

    datetime_utc: datetime
    latitude: float
    longitude: float
    timezone: str


class AstrologyEngine(ABC):
    """Abstract base for astrology computation engines."""

    @abstractmethod
    def compute_chart(self, birth_data: BirthData) -> VedicChartBundle:
        """Compute an astrological chart from birth data."""
        raise NotImplementedError
