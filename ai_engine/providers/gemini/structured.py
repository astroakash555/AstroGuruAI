"""Structured JSON response helpers."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse JSON object from model output, tolerating fenced code blocks."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    payload = json.loads(cleaned)
    if not isinstance(payload, dict):
        raise ValueError("Expected JSON object response.")
    return payload


def validate_required_keys(payload: dict[str, Any], required_keys: tuple[str, ...]) -> None:
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"Missing required JSON keys: {', '.join(missing)}")
