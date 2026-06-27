"""Knowledge entity models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class KnowledgeEntity:
    entity_id: str
    entity_type: str
    name: str
    system: str
    meanings: tuple[str, ...]
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    effects: tuple[str, ...]
    metadata: dict[str, object] = field(default_factory=dict)
