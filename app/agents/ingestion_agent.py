"""
Ingestion Agent: Fetches and normalizes multi-source environmental data
for a given city. First stage of the agent pipeline.
"""

import asyncio
from datetime import datetime, timezone

from app.models.schemas import CityDataPacket
from app.services import air_quality_service, geocoding_service, weather_service


async def ingest_city_data(city_name: str) -> CityDataPacket:
    """
    Fetch weather + air quality data for a city in parallel.
    Returns a normalized CityDataPacket for downstream agents.
    """
    # Step 1: Resolve city to coordinates
    city_info = await geocoding_service.geocode_city(city_name)
    if not city_info:
        raise ValueError(f"Could not geocode city: {city_name}")

    # Step 2: Fetch weather and AQ data in parallel
    weather_task = weather_service.get_current_weather(
        city=city_info.name, lat=city_info.lat, lon=city_info.lon, country=city_info.country
    )
    aq_task = air_quality_service.get_current_air_quality(city=city_info.name, lat=city_info.lat, lon=city_info.lon)

    weather_data, aq_data = await asyncio.gather(weather_task, aq_task)

    return CityDataPacket(
        city=city_info,
        weather=weather_data,
        air_quality=aq_data,
        ingested_at=datetime.now(timezone.utc),
    )
