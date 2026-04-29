"""City search, geocoding, and spatial query endpoints."""

from fastapi import APIRouter, Query

from app.models.schemas import CityInfo, CitySearchResult
from app.services import geocoding_service

router = APIRouter(prefix="/api/v1/cities", tags=["Cities"])


@router.get("/search", response_model=CitySearchResult)
async def search_cities(
    q: str = Query(..., min_length=1, description="City name to search"),
    limit: int = Query(20, ge=1, le=50),
):
    """Fuzzy search cities by name."""
    results = geocoding_service.search_cities(q, limit=limit)
    return CitySearchResult(cities=results, total=len(results), query=q)


@router.get("/nearby")
async def get_nearby_cities(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(100, ge=1, le=5000),
    limit: int = Query(10, ge=1, le=50),
):
    """Find cities within a radius of given coordinates."""
    results = geocoding_service.get_nearby_cities(lat, lon, radius_km, limit)
    return {
        "lat": lat, "lon": lon, "radius_km": radius_km,
        "cities": [{"city": c.model_dump(), "distance_km": d} for c, d in results],
        "total": len(results),
    }


@router.get("/all", response_model=list[CityInfo])
async def get_all_cities():
    """Return all cities in the database."""
    return geocoding_service.get_all_cities()
