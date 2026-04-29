"""Air quality API endpoints: current, forecast, rankings."""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import AirQualityCurrent, AirQualityForecast, AQRankings
from app.services import air_quality_service, geocoding_service

router = APIRouter(prefix="/api/v1/air-quality", tags=["Air Quality"])


@router.get("/current/{city}", response_model=AirQualityCurrent)
async def get_current_aq(city: str):
    """Get current air quality index and pollutant levels."""
    city_info = await geocoding_service.geocode_city(city)
    if not city_info:
        raise HTTPException(status_code=404, detail=f"City not found: {city}")
    return await air_quality_service.get_current_air_quality(
        city=city_info.name, lat=city_info.lat, lon=city_info.lon,
    )


@router.get("/forecast/{city}", response_model=AirQualityForecast)
async def get_aq_forecast(city: str, days: int = 5):
    """Get air quality forecast (up to 5 days)."""
    city_info = await geocoding_service.geocode_city(city)
    if not city_info:
        raise HTTPException(status_code=404, detail=f"City not found: {city}")
    return await air_quality_service.get_aq_forecast(
        city=city_info.name, lat=city_info.lat, lon=city_info.lon, days=days,
    )


@router.get("/rankings", response_model=AQRankings)
async def get_aq_rankings(top_n: int = Query(10, ge=1, le=50)):
    """Get cleanest and most polluted city rankings (from seeded DB)."""
    all_cities = geocoding_service.get_all_cities()
    city_dicts = [c.model_dump() for c in all_cities[:40]]  # Limit to avoid rate limits
    return await air_quality_service.get_aq_rankings(city_dicts, top_n=top_n)
