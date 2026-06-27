"""Abstract problem classifier contract for future LLM integration."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ai_engine.analyzers.problem.types import CategoryMatch


class ProblemClassifier(ABC):
    """Abstract classifier — swap rule-based or LLM implementations."""

    @abstractmethod
    def classify(self, normalized_text: str) -> tuple[CategoryMatch, tuple[CategoryMatch, ...]]:
        """Return primary category and alternatives."""
        raise NotImplementedError
