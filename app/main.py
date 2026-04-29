"""
Cloud Intelligence Platform v2 — Main FastAPI Application
Agentic cloud intelligence with real-time weather, air quality, and ML-powered insights.
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import agents, air_quality, cities, health, predictions, weather
from app.services import ml_service, vector_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Load ML models
    ml_service.load_all_models()

    # Build vector index from cities database
    cities_path = Path(settings.CITIES_DB_PATH)
    if cities_path.exists():
        with open(cities_path, "r", encoding="utf-8") as f:
            cities_data = json.load(f)
        try:
            vector_service.build_index(cities_data)
        except Exception as e:
            print(f"Warning: Vector index build failed: {e}")

    print("✅ Platform ready")
    yield
    # ── Shutdown ──
    print("👋 Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Abdul Ahad Ali Khan", "url": "https://github.com/abdulahadalikhan12"},
    license_info={"name": "MIT"},
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive for dev; restrict in production via settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
app.include_router(health.router)
app.include_router(cities.router)
app.include_router(weather.router)
app.include_router(air_quality.router)
app.include_router(predictions.router)
app.include_router(agents.router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint — platform info."""
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "/health",
        "endpoints": {
            "weather": "/api/v1/weather/current/{city}",
            "air_quality": "/api/v1/air-quality/current/{city}",
            "analyze": "/api/v1/agents/analyze/{city}",
            "compare": "/api/v1/agents/compare",
            "search": "/api/v1/agents/search",
            "cities": "/api/v1/cities/all",
            "predict": "/api/v1/predict/aqi-risk",
        },
    }
