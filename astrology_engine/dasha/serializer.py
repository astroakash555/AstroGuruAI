"""Serialize Vimshottari dasha results to structured JSON."""

from __future__ import annotations

from typing import Any

from astrology_engine.dasha.schemas import VimshottariDashaJSON
from astrology_engine.dasha.types import VimshottariDashaResult


def to_json_dict(result: VimshottariDashaResult) -> dict[str, Any]:
    """Convert a dasha result to a JSON-serializable dictionary."""
    payload = VimshottariDashaJSON(
        system=result.system,
        birth={
            "datetime": result.birth_datetime,
            "birth_place": result.birth_place,
            "timezone": result.timezone,
            "date_of_birth": result.birth_datetime.date().isoformat(),
            "birth_time": result.birth_datetime.time().replace(microsecond=0).isoformat(),
        },
        moon={
            "longitude": result.moon.longitude,
            "nakshatra": result.moon.nakshatra,
            "nakshatra_index": result.moon.nakshatra_index,
            "pada": result.moon.pada,
            "lord": result.moon.lord,
        },
        balance={
            "lord": result.balance.lord,
            "elapsed_fraction": result.balance.elapsed_fraction,
            "remaining_fraction": result.balance.remaining_fraction,
            "duration_years": result.balance.duration_years,
            "duration_days": result.balance.duration_days,
        },
        current={
            "mahadasha": result.current.get("mahadasha"),
            "antardasha": result.current.get("antardasha"),
            "pratyantar_dasha": result.current.get("pratyantar_dasha"),
        },
        mahadashas=list(result.mahadashas),
    )
    return payload.model_dump(mode="json")


def to_json_string(result: VimshottariDashaResult, *, indent: int | None = 2) -> str:
    """Convert a dasha result to a formatted JSON string."""
    import json

    return json.dumps(to_json_dict(result), indent=indent, ensure_ascii=False)
