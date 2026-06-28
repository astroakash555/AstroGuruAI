"""Version 1 API router aggregation."""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import admin_billing, auth, billing, case_learning, chat, clients, dashboard, health, rule_studio

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(billing.router)
api_router.include_router(admin_billing.router)
api_router.include_router(clients.router)
api_router.include_router(dashboard.router)
api_router.include_router(chat.router)
api_router.include_router(rule_studio.router)
api_router.include_router(case_learning.router)
