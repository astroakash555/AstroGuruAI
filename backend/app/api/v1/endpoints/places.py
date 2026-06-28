"""Place autocomplete and geocoding endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.deps import get_current_user, get_settings_dep
from backend.app.core.config import Settings
from backend.app.core.exceptions import ValidationError
from backend.app.models.user import User
from backend.app.schemas.places import (
    PlaceAutocompleteResponse,
    PlaceResolveRequest,
    PlaceResolveResponse,
    PlaceSuggestionResponse,
)
from backend.app.services.place_resolution_service import PlaceResolutionService

router = APIRouter(prefix="/places", tags=["places"])


def get_place_resolution_service(
    settings: Settings = Depends(get_settings_dep),
) -> PlaceResolutionService:
    return PlaceResolutionService(user_agent=f"{settings.app_name}/1.0 (birth-chart-platform)")


@router.get(
    "/autocomplete",
    response_model=PlaceAutocompleteResponse,
    summary="Autocomplete birth place search",
)
async def autocomplete_places(
    q: str = Query(..., min_length=2, max_length=255),
    limit: int = Query(default=5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    service: PlaceResolutionService = Depends(get_place_resolution_service),
) -> PlaceAutocompleteResponse:
    del current_user
    try:
        suggestions = await service.autocomplete(q, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Place search is temporarily unavailable.",
        ) from exc

    return PlaceAutocompleteResponse(
        items=[
            PlaceSuggestionResponse(
                place_id=item.place_id,
                label=item.label,
                description=item.description,
            )
            for item in suggestions
        ]
    )


@router.post(
    "/resolve",
    response_model=PlaceResolveResponse,
    summary="Resolve birth place to coordinates and timezone",
)
async def resolve_place(
    payload: PlaceResolveRequest,
    current_user: User = Depends(get_current_user),
    service: PlaceResolutionService = Depends(get_place_resolution_service),
) -> PlaceResolveResponse:
    del current_user
    try:
        resolved = await service.resolve(place_id=payload.place_id, query=payload.query)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.message,
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Place resolution is temporarily unavailable.",
        ) from exc

    return PlaceResolveResponse(
        place_id=resolved.place_id,
        birth_place=resolved.birth_place,
        display_name=resolved.display_name,
        latitude=resolved.latitude,
        longitude=resolved.longitude,
        timezone=resolved.timezone,
        country=resolved.country,
        state=resolved.state,
    )
