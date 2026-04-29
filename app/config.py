"""
Application configuration using pydantic-settings.
All settings can be overridden via environment variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # App metadata
    APP_NAME: str = "Cloud Intelligence Platform"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = (
        "Agentic Cloud Intelligence Platform with real-time weather, air quality, and ML-powered insights"
    )
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 7860

    # CORS — frontend origins (Vercel + localhost dev)
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://*.lovable.app",
    ]

    # Cache TTL (seconds)
    WEATHER_CACHE_TTL: int = 300  # 5 minutes for current weather
    FORECAST_CACHE_TTL: int = 3600  # 1 hour for forecasts
    GEOCODING_CACHE_TTL: int = 86400  # 24 hours for geocoding
    AQ_CACHE_TTL: int = 600  # 10 minutes for air quality

    # External APIs (all free, no keys required)
    OPEN_METEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_AQ_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
    OPEN_METEO_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com/v1/archive"

    # ML Models
    MODELS_DIR: str = "app/ml/pretrained"

    # Vector DB
    VECTOR_MODEL_NAME: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "app/ml/pretrained/faiss_index"

    # Data
    CITIES_DB_PATH: str = "data/cities.json"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Hugging Face
    HF_SPACE_URL: str = "https://abdulahadalikhan12-cloud-intelligence.hf.space"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
