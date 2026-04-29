"""Health check and system status endpoints."""

import time

from fastapi import APIRouter

from app.config import get_settings
from app.models.schemas import HealthCheck, SystemStatus
from app.services import geocoding_service, ml_service, vector_service

router = APIRouter()
settings = get_settings()

_start_time = time.time()


@router.get("/health", response_model=HealthCheck, tags=["System"])
def health_check():
    """Basic health check endpoint."""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        uptime_seconds=round(time.time() - _start_time, 1),
    )


@router.get("/api/v1/status", response_model=SystemStatus, tags=["System"])
def system_status():
    """Detailed system status including model availability and cache stats."""
    return SystemStatus(
        status="operational",
        version=settings.APP_VERSION,
        models_loaded=ml_service.get_models_status(),
        faiss_index_size=vector_service.get_index_size(),
        cities_count=len(geocoding_service.get_all_cities()),
        cache_stats={"weather": "in-memory", "aq": "in-memory", "geocoding": "in-memory"},
        uptime_seconds=round(time.time() - _start_time, 1),
    )
