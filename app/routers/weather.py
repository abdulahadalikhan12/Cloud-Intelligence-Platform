"""Weather API endpoints: current, forecast, historical."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import WeatherCurrent, WeatherForecast, WeatherHistory
from app.services import geocoding_service, weather_service

router = APIRouter(prefix="/api/v1/weather", tags=["Weather"])


@router.get("/current/{city}", response_model=WeatherCurrent)
async def get_current_weather(city: str):
    """Get real-time weather for any city worldwide."""
    city_info = await geocoding_service.geocode_city(city)
    if not city_info:
        raise HTTPException(status_code=404, detail=f"City not found: {city}")
    return await weather_service.get_current_weather(
        city=city_info.name,
        lat=city_info.lat,
        lon=city_info.lon,
        country=city_info.country,
    )


@router.get("/forecast/{city}", response_model=WeatherForecast)
async def get_weather_forecast(city: str, days: int = 7):
    """Get multi-day weather forecast (up to 16 days)."""
    city_info = await geocoding_service.geocode_city(city)
    if not city_info:
        raise HTTPException(status_code=404, detail=f"City not found: {city}")
    return await weather_service.get_weather_forecast(
        city=city_info.name,
        lat=city_info.lat,
        lon=city_info.lon,
        days=days,
    )


@router.get("/historical/{city}", response_model=WeatherHistory)
async def get_weather_history(city: str, days: int = 30):
    """Get historical weather data (last N days, up to 90)."""
    city_info = await geocoding_service.geocode_city(city)
    if not city_info:
        raise HTTPException(status_code=404, detail=f"City not found: {city}")
    return await weather_service.get_weather_history(
        city=city_info.name,
        lat=city_info.lat,
        lon=city_info.lon,
        days=min(days, 90),
    )
