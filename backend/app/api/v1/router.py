"""Version 1 API router aggregation."""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    admin_analytics,
    admin_billing,
    auth,
    billing,
    case_learning,
    chat,
    clients,
    dashboard,
    health,
    places,
    rule_studio,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(billing.router)
api_router.include_router(admin_billing.router)
api_router.include_router(admin_analytics.router)
api_router.include_router(clients.router)
api_router.include_router(places.router)
api_router.include_router(dashboard.router)
api_router.include_router(chat.router)
api_router.include_router(rule_studio.router)
api_router.include_router(case_learning.router)
