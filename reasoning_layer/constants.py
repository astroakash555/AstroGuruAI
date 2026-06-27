"""Reasoning layer constants."""

from __future__ import annotations

SYSTEMS = ("vedic", "kp", "lal_kitab", "dasha", "transit", "knowledge_brain")

STANCES = ("support", "block", "delay", "neutral")

CAUSE_TYPES = ("actual", "secondary", "hidden")

CONSENSUS_OUTCOMES = (
    "strong_support",
    "moderate_support",
    "mixed_signals",
    "delayed_outcome",
    "blocked_outcome",
    "insufficient_data",
)

DOMAIN_HOUSE_MAP: dict[str, tuple[int, ...]] = {
    "marriage": (2, 7, 8, 11, 12),
    "career": (2, 6, 7, 10, 11),
    "health": (1, 6, 8, 12),
    "finance": (2, 5, 8, 11, 12),
}

MALEFICS = frozenset({"Saturn", "Mars", "Rahu", "Ketu"})
