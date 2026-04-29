"""
Geocoding service: resolves city names to coordinates.
Uses a local cities.json database + Open-Meteo Geocoding API fallback.
Supports fuzzy search and spatial (nearby) queries.
"""

import json
import math
from difflib import SequenceMatcher
from pathlib import Path

import httpx

from app.config import get_settings
from app.models.schemas import CityInfo

settings = get_settings()

# ── In-memory city database ──────────────────────────────
_cities_db: list[CityInfo] = []
_geocode_cache: dict[str, CityInfo] = {}


def _load_cities_db() -> list[CityInfo]:
    """Load pre-seeded city database from JSON file."""
    global _cities_db
    if _cities_db:
        return _cities_db
    db_path = Path(settings.CITIES_DB_PATH)
    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        _cities_db = [CityInfo(**city) for city in raw]
    return _cities_db


def _similarity(a: str, b: str) -> float:
    """Fuzzy string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two geo points in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def geocode_city(city_name: str) -> CityInfo | None:
    """
    Resolve a city name to CityInfo.
    1. Check in-memory cache
    2. Fuzzy search local database
    3. Fallback to Open-Meteo Geocoding API
    """
    key = city_name.lower().strip()

    # Check cache
    if key in _geocode_cache:
        return _geocode_cache[key]

    # Search local DB (fuzzy)
    cities = _load_cities_db()
    best_match = None
    best_score = 0.0
    for city in cities:
        score = _similarity(key, city.name.lower())
        if score > best_score:
            best_score = score
            best_match = city

    if best_match and best_score >= 0.75:
        _geocode_cache[key] = best_match
        return best_match

    # Fallback: Open-Meteo Geocoding API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                settings.OPEN_METEO_GEOCODING_URL,
                params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            )
            resp.raise_for_status()
            data = resp.json()
            if "results" in data and len(data["results"]) > 0:
                r = data["results"][0]
                city_info = CityInfo(
                    name=r.get("name", city_name),
                    country=r.get("country", "Unknown"),
                    lat=r["latitude"],
                    lon=r["longitude"],
                    population=r.get("population"),
                    timezone=r.get("timezone"),
                    continent=None,
                )
                _geocode_cache[key] = city_info
                return city_info
    except Exception:
        pass

    return None


def search_cities(query: str, limit: int = 20) -> list[CityInfo]:
    """Fuzzy search cities by name. Returns ranked results."""
    cities = _load_cities_db()
    q = query.lower().strip()

    scored = []
    for city in cities:
        # Exact prefix match gets highest priority
        if city.name.lower().startswith(q):
            scored.append((2.0, city))
        else:
            score = _similarity(q, city.name.lower())
            if score > 0.4:
                scored.append((score, city))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [city for _, city in scored[:limit]]


def get_nearby_cities(lat: float, lon: float, radius_km: float = 100, limit: int = 10) -> list[tuple[CityInfo, float]]:
    """Find cities within a radius of given coordinates."""
    cities = _load_cities_db()
    nearby = []
    for city in cities:
        dist = _haversine_km(lat, lon, city.lat, city.lon)
        if dist <= radius_km:
            nearby.append((city, round(dist, 1)))

    nearby.sort(key=lambda x: x[1])
    return nearby[:limit]


def get_all_cities() -> list[CityInfo]:
    """Return all cities in the database."""
    return _load_cities_db()
