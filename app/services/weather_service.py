"""
Weather service: fetches current weather, forecasts, and historical data
from Open-Meteo APIs. Includes in-memory caching with TTL.
"""

import time
from datetime import datetime, timedelta, timezone

import httpx

from app.config import get_settings
from app.models.schemas import (
    ForecastDay,
    HistoricalWeather,
    WeatherCurrent,
    WeatherForecast,
    WeatherHistory,
)

settings = get_settings()

# ── Simple TTL Cache ─────────────────────────────────────
_cache: dict[str, tuple[float, object]] = {}


def _get_cached(key: str, ttl: int) -> object | None:
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < ttl:
            return val
        del _cache[key]
    return None


def _set_cached(key: str, val: object):
    _cache[key] = (time.time(), val)


def _weather_condition(rain: float, cloud_cover: float | None, wind: float) -> str:
    """Derive a human-readable condition string."""
    if rain > 5:
        return "Heavy Rain"
    if rain > 0.5:
        return "Rainy"
    if rain > 0:
        return "Light Rain"
    if cloud_cover is not None and cloud_cover > 80:
        return "Overcast"
    if cloud_cover is not None and cloud_cover > 50:
        return "Partly Cloudy"
    if wind > 40:
        return "Windy"
    return "Clear"


def _forecast_condition(precip: float, precip_prob: float, wind: float) -> str:
    if precip > 10:
        return "Heavy Rain"
    if precip_prob > 70:
        return "Likely Rain"
    if precip > 1:
        return "Rainy"
    if precip_prob > 40:
        return "Possible Rain"
    if wind > 40:
        return "Windy"
    return "Clear"


async def get_current_weather(city: str, lat: float, lon: float, country: str | None = None) -> WeatherCurrent:
    """Fetch current weather from Open-Meteo."""
    cache_key = f"weather_current_{lat:.2f}_{lon:.2f}"
    cached = _get_cached(cache_key, settings.WEATHER_CACHE_TTL)
    if cached:
        return cached

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "rain",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover",
            "apparent_temperature",
        ],
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(settings.OPEN_METEO_WEATHER_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data["current"]
    rain = current.get("rain", 0) or 0
    cloud = current.get("cloud_cover")
    wind = current.get("wind_speed_10m", 0) or 0

    result = WeatherCurrent(
        city=city,
        country=country,
        lat=lat,
        lon=lon,
        temperature_c=round(current["temperature_2m"], 1),
        humidity_pct=round(current["relative_humidity_2m"], 1),
        wind_speed_kmh=round(wind, 1),
        wind_direction_deg=current.get("wind_direction_10m"),
        rain_mm=round(rain, 2),
        pressure_hpa=current.get("surface_pressure"),
        cloud_cover_pct=cloud,
        condition=_weather_condition(rain, cloud, wind),
        feels_like_c=current.get("apparent_temperature"),
        timestamp=datetime.now(timezone.utc),
    )

    _set_cached(cache_key, result)
    return result


async def get_weather_forecast(city: str, lat: float, lon: float, days: int = 7) -> WeatherForecast:
    """Fetch multi-day forecast from Open-Meteo."""
    cache_key = f"weather_forecast_{lat:.2f}_{lon:.2f}_{days}"
    cached = _get_cached(cache_key, settings.FORECAST_CACHE_TTL)
    if cached:
        return cached

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "uv_index_max",
        ],
        "forecast_days": min(days, 16),
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(settings.OPEN_METEO_WEATHER_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data["daily"]
    forecast_days = []
    for i in range(len(daily["time"])):
        t_max = daily["temperature_2m_max"][i] or 0
        t_min = daily["temperature_2m_min"][i] or 0
        precip = daily["precipitation_sum"][i] or 0
        precip_prob = daily["precipitation_probability_max"][i] or 0
        wind_max = daily["wind_speed_10m_max"][i] or 0

        forecast_days.append(
            ForecastDay(
                date=daily["time"][i],
                temp_max_c=round(t_max, 1),
                temp_min_c=round(t_min, 1),
                temp_avg_c=round((t_max + t_min) / 2, 1),
                precipitation_mm=round(precip, 1),
                precipitation_probability_pct=round(precip_prob, 0),
                wind_speed_max_kmh=round(wind_max, 1),
                condition=_forecast_condition(precip, precip_prob, wind_max),
                uv_index_max=daily.get("uv_index_max", [None])[i] if i < len(daily.get("uv_index_max", [])) else None,
            )
        )

    result = WeatherForecast(
        city=city,
        lat=lat,
        lon=lon,
        forecast_days=forecast_days,
        generated_at=datetime.now(timezone.utc),
    )
    _set_cached(cache_key, result)
    return result


async def get_weather_history(city: str, lat: float, lon: float, days: int = 30) -> WeatherHistory:
    """Fetch historical weather data from Open-Meteo Archive API."""
    cache_key = f"weather_history_{lat:.2f}_{lon:.2f}_{days}"
    cached = _get_cached(cache_key, settings.FORECAST_CACHE_TTL)
    if cached:
        return cached

    end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "rain_sum",
            "wind_speed_10m_max",
            "surface_pressure_mean",
        ],
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(settings.OPEN_METEO_ARCHIVE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data["daily"]
    daily_data = []
    for i in range(len(daily["time"])):
        daily_data.append(
            HistoricalWeather(
                date=daily["time"][i],
                temperature_c=round(daily["temperature_2m_mean"][i] or 0, 1),
                humidity_pct=round(daily["relative_humidity_2m_mean"][i] or 0, 1),
                rain_mm=round(daily["rain_sum"][i] or 0, 1),
                wind_speed_kmh=round(daily["wind_speed_10m_max"][i] or 0, 1),
                pressure_hpa=daily.get("surface_pressure_mean", [None])[i]
                if i < len(daily.get("surface_pressure_mean", []))
                else None,
            )
        )

    result = WeatherHistory(
        city=city,
        lat=lat,
        lon=lon,
        period_start=start_date,
        period_end=end_date,
        daily_data=daily_data,
    )
    _set_cached(cache_key, result)
    return result
