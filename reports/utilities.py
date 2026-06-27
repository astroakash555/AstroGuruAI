"""Shared helpers for report orchestration and serialization."""

from __future__ import annotations

from typing import Any

from astrology_engine.doshas.rules._helpers import severity_level


def normalize_highest_dosha_severity(value: Any) -> str | None:
    """
    Normalize dosha severity for unified report summary JSON.

    Dosha detection stores numeric severity (0.0-1.0); the unified report
    contract exposes a string label. Existing string labels are preserved.
    """
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped.lower() if stripped else None
    if isinstance(value, (int, float)):
        return severity_level(float(value))
    return None
