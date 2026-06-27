"""KP astrology constants."""

from __future__ import annotations

EVENT_TEMPLATES: tuple[dict[str, object], ...] = (
    {
        "event_id": "marriage_event",
        "event_type": "marriage",
        "target_houses": (2, 7, 11),
        "primary_planets": ("Venus", "Jupiter"),
    },
    {
        "event_id": "career_event",
        "event_type": "career",
        "target_houses": (2, 6, 10, 11),
        "primary_planets": ("Sun", "Saturn", "Mercury"),
    },
    {
        "event_id": "health_event",
        "event_type": "health",
        "target_houses": (1, 6, 8, 12),
        "primary_planets": ("Sun", "Moon", "Mars"),
    },
    {
        "event_id": "finance_event",
        "event_type": "finance",
        "target_houses": (2, 6, 11),
        "primary_planets": ("Jupiter", "Venus", "Mercury"),
    },
    {
        "event_id": "legal_event",
        "event_type": "legal",
        "target_houses": (6, 8, 12),
        "primary_planets": ("Saturn", "Mars", "Mercury"),
    },
)

SIGNIFICATOR_LEVELS: tuple[str, ...] = ("level_a", "level_b", "level_c", "level_d")
