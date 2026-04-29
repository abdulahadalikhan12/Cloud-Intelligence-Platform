"""Agent orchestration endpoints: full city analysis, comparison, semantic search."""

from fastapi import APIRouter, Body, HTTPException

from app.agents import orchestrator
from app.models.schemas import (
    CityComparison,
    IntelligenceReport,
    SemanticSearchQuery,
    SemanticSearchResponse,
)
from app.services import vector_service

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


@router.post("/analyze/{city}", response_model=IntelligenceReport)
async def analyze_city(city: str):
    """
    Run the full agent pipeline for a city:
    Ingestion → Analysis → Recommendations
    Returns a complete intelligence report.
    """
    try:
        return await orchestrator.run_city_analysis(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")


@router.post("/compare", response_model=CityComparison)
async def compare_cities(cities: list[str] = Body(..., min_length=2, max_length=10)):
    """Compare multiple cities side-by-side using the agent pipeline."""
    try:
        return await orchestrator.compare_cities(cities)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(query: SemanticSearchQuery):
    """
    Semantic search across city intelligence using natural language.
    Example: 'cities with clean air and warm weather'
    """
    results = vector_service.semantic_search(query.query, top_k=query.top_k)
    return SemanticSearchResponse(
        query=query.query,
        results=results,
        total=len(results),
    )
