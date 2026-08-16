from fastapi import APIRouter
from apps.api.app.api.v1.endpoints import (
    health,
    auth,
    analyses,
    results,
    reports,
    payments,
)

api_router = APIRouter()

# Health endpoints
api_router.include_router(health.router)

# Auth & Account endpoints
api_router.include_router(auth.router)

# Payments & Mobile Money endpoints
api_router.include_router(payments.router)

# Analysis lifecycle endpoints
api_router.include_router(analyses.router)

# Detailed Engine results endpoints
api_router.include_router(results.router)

# Report generation and download endpoints
api_router.include_router(reports.router)
