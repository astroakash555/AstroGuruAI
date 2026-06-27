"""Lal Kitab rule base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from lal_kitab_engine.types import LalKitabFinding
from lal_kitab_engine.context import LalKitabContext


class LalKitabRule(ABC):
    """Pluggable Lal Kitab analysis rule."""

    finding_id: str
    finding_name: str
    category: str

    @abstractmethod
    def analyze(self, context: LalKitabContext) -> LalKitabFinding:
        raise NotImplementedError
