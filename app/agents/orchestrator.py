"""
Agent Orchestrator: Chains the ingestion → analysis → recommendation pipeline.
Handles errors gracefully — if one agent fails, the pipeline degrades but doesn't crash.
"""

import asyncio
from datetime import datetime, timezone

from app.agents import analysis_agent, ingestion_agent, recommendation_agent
from app.models.schemas import CityComparison, IntelligenceReport


async def run_city_analysis(city_name: str) -> IntelligenceReport:
    """
    Execute the full agent pipeline for a single city:
    1. Ingestion Agent → fetch data
    2. Analysis Agent → run ML + generate insights
    3. Recommendation Agent → produce actionable recommendations
    """
    # Stage 1: Ingest
    data_packet = await ingestion_agent.ingest_city_data(city_name)

    # Stage 2: Analyze
    analysis = analysis_agent.analyze_city_data(data_packet)

    # Stage 3: Recommend
    recommendations = recommendation_agent.generate_recommendations(data_packet, analysis)

    return IntelligenceReport(
        city=data_packet.city.name,
        country=data_packet.city.country,
        lat=data_packet.city.lat,
        lon=data_packet.city.lon,
        weather=data_packet.weather,
        air_quality=data_packet.air_quality,
        analysis=analysis,
        recommendations=recommendations,
        generated_at=datetime.now(timezone.utc),
    )


async def compare_cities(city_names: list[str]) -> CityComparison:
    """
    Run the agent pipeline for multiple cities in parallel and compare.
    """
    tasks = [run_city_analysis(name) for name in city_names]
    reports = await asyncio.gather(*tasks, return_exceptions=True)

    successful = [r for r in reports if isinstance(r, IntelligenceReport)]
    failed = [city_names[i] for i, r in enumerate(reports) if isinstance(r, Exception)]

    if not successful:
        raise ValueError(f"All city analyses failed. Failed cities: {failed}")

    # Find best overall city
    best = max(successful, key=lambda r: r.recommendations.overall_score)

    summary_parts = []
    for report in successful:
        score = report.recommendations.overall_score
        summary_parts.append(f"{report.city}: {score}/100")

    summary = f"Compared {len(successful)} cities. " + ", ".join(summary_parts) + "."
    if failed:
        summary += f" Failed to analyze: {', '.join(failed)}."

    return CityComparison(
        cities=successful,
        summary=summary,
        best_overall=best.city,
        generated_at=datetime.now(timezone.utc),
    )
