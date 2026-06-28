"""Resolve birth places to coordinates and IANA timezones."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.core.exceptions import ValidationError
from backend.app.utils.coordinates import validate_birth_coordinates

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlaceSuggestion:
    """Lightweight autocomplete result."""

    place_id: str
    label: str
    description: str


@dataclass(frozen=True)
class ResolvedPlace:
    """Fully resolved birth place with coordinates and timezone."""

    place_id: str
    birth_place: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str
    country: str | None = None
    state: str | None = None


class PlaceResolutionService:
    """Geocode places via OpenStreetMap Nominatim and resolve timezones offline."""

    def __init__(
        self,
        *,
        base_url: str = "https://nominatim.openstreetmap.org",
        user_agent: str = "AstroGuruAI/1.0 (birth-chart-platform)",
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._user_agent = user_agent
        self._timeout = timeout
        self._client = client
        self._timezone_finder = None

    async def autocomplete(self, query: str, *, limit: int = 5) -> list[PlaceSuggestion]:
        """Search for place suggestions matching the query string."""
        normalized = " ".join(query.split())
        if len(normalized) < 2:
            return []

        params = {
            "q": normalized,
            "format": "json",
            "addressdetails": 1,
            "limit": max(1, min(limit, 10)),
        }
        results = await self._get("/search", params=params)
        suggestions: list[PlaceSuggestion] = []
        for item in results:
            place_id = self._compose_place_id(item)
            label = self._short_label(item)
            description = str(item.get("display_name", label))
            suggestions.append(
                PlaceSuggestion(place_id=place_id, label=label, description=description)
            )
        return suggestions

    async def resolve(
        self,
        *,
        place_id: str | None = None,
        query: str | None = None,
    ) -> ResolvedPlace:
        """Resolve a place to coordinates and timezone."""
        if not place_id and not query:
            raise ValidationError("Either place_id or query is required to resolve a birth place.")

        if place_id:
            resolved_items = await self._resolve_by_place_id(place_id)
            if not resolved_items:
                raise ValidationError(f"Could not resolve birth place for place_id '{place_id}'.")
            return self._to_resolved_place(resolved_items[0], fallback_query=query)

        normalized = " ".join((query or "").split())
        if len(normalized) < 2:
            raise ValidationError("Birth place must be at least 2 characters to resolve.")

        search_results = await self._get(
            "/search",
            params={
                "q": normalized,
                "format": "json",
                "addressdetails": 1,
                "limit": 1,
            },
        )
        if not search_results:
            raise ValidationError(f"Could not resolve birth place '{normalized}'.")

        return self._to_resolved_place(search_results[0], fallback_query=normalized)

    def timezone_at(self, latitude: float, longitude: float) -> str | None:
        """Resolve IANA timezone for coordinates (handles DST at conversion time)."""
        finder = self._get_timezone_finder()
        if finder is None:
            return None
        try:
            return finder.timezone_at(lng=longitude, lat=latitude)
        except Exception:
            logger.exception("Timezone lookup failed for lat=%s lon=%s", latitude, longitude)
            return None

    async def _resolve_by_place_id(self, place_id: str) -> list[dict[str, Any]]:
        if place_id.startswith(("N", "W", "R", "n", "w", "r")) and place_id[1:].isdigit():
            osm_ids = place_id if place_id[0].isupper() else f"{place_id[0].upper()}{place_id[1:]}"
            return await self._get("/lookup", params={"osm_ids": osm_ids, "format": "json"})

        if place_id.isdigit():
            details = await self._get("/details", params={"place_id": place_id, "format": "json"})
            if not details:
                return []
            osm_type = str(details.get("osm_type", ""))[0:1].upper()
            osm_id = details.get("osm_id")
            if osm_type and osm_id is not None:
                return await self._get(
                    "/lookup",
                    params={"osm_ids": f"{osm_type}{osm_id}", "format": "json"},
                )
            return [details]

        return await self._get(
            "/search",
            params={"q": place_id, "format": "json", "addressdetails": 1, "limit": 1},
        )

    async def _get(self, path: str, *, params: dict[str, Any]) -> list[dict[str, Any]] | dict[str, Any]:
        headers = {"User-Agent": self._user_agent, "Accept": "application/json"}
        if self._client is not None:
            response = await self._client.get(f"{self._base_url}{path}", params=params, headers=headers)
        else:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._base_url}{path}", params=params, headers=headers)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            return payload
        return payload

    def _to_resolved_place(
        self,
        item: dict[str, Any],
        *,
        fallback_query: str | None,
    ) -> ResolvedPlace:
        latitude = float(item["lat"])
        longitude = float(item["lon"])
        display_name = str(item.get("display_name") or fallback_query or "")
        birth_place = self._short_label(item) or display_name
        validate_birth_coordinates(latitude, longitude, birth_place=birth_place)

        timezone_name = self.timezone_at(latitude, longitude)
        if not timezone_name:
            raise ValidationError(
                f"Could not determine timezone for '{birth_place}'. Try a more specific place name."
            )

        address = item.get("address") or {}
        country = self._address_component(address, ("country",))
        state = self._address_component(
            address,
            ("state", "state_district", "region", "province"),
        )

        return ResolvedPlace(
            place_id=self._compose_place_id(item),
            birth_place=birth_place,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone_name,
            country=country,
            state=state,
        )

    @staticmethod
    def _compose_place_id(item: dict[str, Any]) -> str:
        osm_type = str(item.get("osm_type", "N"))[0:1].upper()
        osm_id = item.get("osm_id")
        if osm_id is not None:
            return f"{osm_type}{osm_id}"
        place_id = item.get("place_id")
        if place_id is not None:
            return str(place_id)
        return str(item.get("display_name", "unknown"))

    @staticmethod
    def _short_label(item: dict[str, Any]) -> str:
        address = item.get("address") or {}
        city = PlaceResolutionService._address_component(
            address,
            ("city", "town", "village", "hamlet", "municipality", "county", "suburb"),
        )
        state = PlaceResolutionService._address_component(
            address,
            ("state", "state_district", "region", "province"),
        )
        country = PlaceResolutionService._address_component(address, ("country",))

        parts = [part for part in (city, state, country) if part]
        if parts:
            return ", ".join(parts)
        display_name = str(item.get("display_name", ""))
        return display_name.split(",")[0].strip() if display_name else ""

    @staticmethod
    def _address_component(address: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = address.get(key)
            if value:
                return str(value)
        return None

    def _get_timezone_finder(self):
        if self._timezone_finder is not None:
            return self._timezone_finder
        try:
            from timezonefinder import TimezoneFinder
        except ImportError:
            logger.warning("timezonefinder is not installed; timezone resolution unavailable.")
            return None
        self._timezone_finder = TimezoneFinder()
        return self._timezone_finder
