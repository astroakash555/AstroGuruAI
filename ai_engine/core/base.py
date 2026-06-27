"""Base classes for AI engine components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptContext:
    """Context passed to AI providers for inference."""

    system_prompt: str
    user_prompt: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class InferenceResult:
    """Standardized AI inference response."""

    content: str
    model: str
    metadata: dict[str, Any]


class AIEngine(ABC):
    """Abstract base for AI inference engines."""

    @abstractmethod
    async def generate(self, context: PromptContext) -> InferenceResult:
        """Generate a response from the given prompt context."""
        raise NotImplementedError
