"""Health and readiness endpoints."""

from fastapi import APIRouter, Depends

from backend.app.core.config import Settings
from backend.app.api.deps import get_settings_dep
from backend.app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings_dep)) -> HealthResponse:
    """Return application health status."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
    )
