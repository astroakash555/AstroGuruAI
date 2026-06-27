"""Gemini usage and cost tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class UsageRecord:
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    timestamp: datetime


@dataclass
class CostTracker:
    """Track cumulative Gemini usage and estimated cost."""

    input_cost_per_1k: float = 0.0001
    output_cost_per_1k: float = 0.0004
    records: list[UsageRecord] = field(default_factory=list)

    def record_usage(
        self,
        *,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> UsageRecord:
        total = prompt_tokens + completion_tokens
        cost = (
            (prompt_tokens / 1000.0) * self.input_cost_per_1k
            + (completion_tokens / 1000.0) * self.output_cost_per_1k
        )
        entry = UsageRecord(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            estimated_cost_usd=round(cost, 6),
            timestamp=datetime.now(timezone.utc),
        )
        self.records.append(entry)
        return entry

    @property
    def total_estimated_cost_usd(self) -> float:
        return round(sum(item.estimated_cost_usd for item in self.records), 6)

    @property
    def total_tokens(self) -> int:
        return sum(item.total_tokens for item in self.records)
