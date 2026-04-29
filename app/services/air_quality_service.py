"""
Air Quality service: fetches current AQ, forecasts, and rankings
from Open-Meteo Air Quality API. Includes EPA AQI calculation.
"""

import time
import httpx
from datetime import datetime, timezone
from app.config import get_settings
from app.models.schemas import (
    AirQualityCurrent, AQICategory, AQForecastDay,
    AirQualityForecast, CityRanking, AQRankings,
)

settings = get_settings()

_cache: dict[str, tuple[float, object]] = {}


def _get_cached(key: str, ttl: int):
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < ttl:
            return val
        del _cache[key]
    return None


def _set_cached(key: str, val: object):
    _cache[key] = (time.time(), val)


def calculate_aqi_from_pm25(pm25: float) -> int:
    """Calculate EPA AQI from PM2.5 concentration (µg/m³)."""
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]
    pm25 = max(0, pm25)
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return round(aqi)
    return 500


def aqi_to_category(aqi: int) -> AQICategory:
    """Map AQI value to EPA category."""
    if aqi <= 50:
        return AQICategory.GOOD
    if aqi <= 100:
        return AQICategory.MODERATE
    if aqi <= 150:
        return AQICategory.UNHEALTHY_SENSITIVE
    if aqi <= 200:
        return AQICategory.UNHEALTHY
    if aqi <= 300:
        return AQICategory.VERY_UNHEALTHY
    return AQICategory.HAZARDOUS


def _dominant_pollutant(pm25: float, pm10: float, no2: float, o3: float) -> str:
    """Determine which pollutant is dominant."""
    pollutants = {"PM2.5": pm25 or 0, "PM10": pm10 or 0, "NO₂": no2 or 0, "O₃": o3 or 0}
    return max(pollutants, key=pollutants.get)


async def get_current_air_quality(city: str, lat: float, lon: float) -> AirQualityCurrent:
    """Fetch current air quality data from Open-Meteo."""
    cache_key = f"aq_current_{lat:.2f}_{lon:.2f}"
    cached = _get_cached(cache_key, settings.AQ_CACHE_TTL)
    if cached:
        return cached

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["pm10", "pm2_5", "nitrogen_dioxide", "ozone"],
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(settings.OPEN_METEO_AQ_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data.get("current", {})
    pm25 = current.get("pm2_5") or 0
    pm10 = current.get("pm10") or 0
    no2 = current.get("nitrogen_dioxide") or 0
    o3 = current.get("ozone") or 0

    aqi = calculate_aqi_from_pm25(pm25)

    result = AirQualityCurrent(
        city=city, lat=lat, lon=lon,
        aqi=aqi,
        category=aqi_to_category(aqi),
        pm2_5=round(pm25, 1),
        pm10=round(pm10, 1),
        no2=round(no2, 1),
        o3=round(o3, 1),
        dominant_pollutant=_dominant_pollutant(pm25, pm10, no2, o3),
        timestamp=datetime.now(timezone.utc),
    )
    _set_cached(cache_key, result)
    return result


async def get_aq_forecast(city: str, lat: float, lon: float, days: int = 5) -> AirQualityForecast:
    """Fetch air quality forecast."""
    cache_key = f"aq_forecast_{lat:.2f}_{lon:.2f}_{days}"
    cached = _get_cached(cache_key, settings.FORECAST_CACHE_TTL)
    if cached:
        return cached

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["pm2_5", "pm10"],
        "forecast_days": min(days, 5),
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(settings.OPEN_METEO_AQ_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    pm25_vals = hourly.get("pm2_5", [])
    pm10_vals = hourly.get("pm10", [])

    # Aggregate hourly → daily
    from collections import defaultdict
    daily_agg = defaultdict(lambda: {"pm25": [], "pm10": []})
    for i, t in enumerate(times):
        day = t[:10]
        if i < len(pm25_vals) and pm25_vals[i] is not None:
            daily_agg[day]["pm25"].append(pm25_vals[i])
        if i < len(pm10_vals) and pm10_vals[i] is not None:
            daily_agg[day]["pm10"].append(pm10_vals[i])

    forecast_days = []
    for day in sorted(daily_agg.keys()):
        d = daily_agg[day]
        pm25_avg = sum(d["pm25"]) / len(d["pm25"]) if d["pm25"] else 0
        pm25_max = max(d["pm25"]) if d["pm25"] else 0
        pm10_avg = sum(d["pm10"]) / len(d["pm10"]) if d["pm10"] else 0
        aqi_avg = calculate_aqi_from_pm25(pm25_avg)
        aqi_max = calculate_aqi_from_pm25(pm25_max)

        forecast_days.append(AQForecastDay(
            date=day,
            aqi_avg=aqi_avg,
            aqi_max=aqi_max,
            pm2_5_avg=round(pm25_avg, 1),
            pm10_avg=round(pm10_avg, 1),
            category=aqi_to_category(aqi_avg),
        ))

    result = AirQualityForecast(
        city=city, lat=lat, lon=lon,
        forecast_days=forecast_days,
        generated_at=datetime.now(timezone.utc),
    )
    _set_cached(cache_key, result)
    return result


async def get_aq_rankings(cities: list[dict], top_n: int = 10) -> AQRankings:
    """Fetch current AQ for multiple cities and rank them."""
    cache_key = f"aq_rankings_{len(cities)}_{top_n}"
    cached = _get_cached(cache_key, settings.AQ_CACHE_TTL)
    if cached:
        return cached

    results = []
    for city_data in cities:
        try:
            aq = await get_current_air_quality(
                city_data["name"], city_data["lat"], city_data["lon"]
            )
            results.append((city_data, aq))
        except Exception:
            continue

    # Sort by AQI
    results.sort(key=lambda x: x[1].aqi)

    def _make_ranking(items, start_rank=1):
        rankings = []
        for i, (cd, aq) in enumerate(items):
            rankings.append(CityRanking(
                rank=start_rank + i,
                city=cd["name"],
                country=cd.get("country", "Unknown"),
                aqi=aq.aqi,
                category=aq.category,
                pm2_5=aq.pm2_5,
                lat=cd["lat"],
                lon=cd["lon"],
            ))
        return rankings

    cleanest = _make_ranking(results[:top_n], 1)
    most_polluted = _make_ranking(list(reversed(results[-top_n:])), 1)

    result = AQRankings(
        cleanest=cleanest,
        most_polluted=most_polluted,
        generated_at=datetime.now(timezone.utc),
    )
    _set_cached(cache_key, result)
    return result
