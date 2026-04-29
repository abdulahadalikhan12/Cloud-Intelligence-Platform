"""
Recommendation Agent: Generates actionable, human-readable recommendations
from the analysis results. Final stage of the agent pipeline.
"""

from datetime import datetime, timezone
from app.models.schemas import (
    CityDataPacket, AnalysisResult, Recommendation,
    RecommendationReport, RiskLevel,
)


def _calculate_livability_score(data: CityDataPacket, analysis: AnalysisResult) -> float:
    """Calculate a 0-100 livability score based on current conditions."""
    score = 100.0
    aq = data.air_quality
    w = data.weather

    # AQI penalty (biggest factor)
    if aq.aqi > 300:
        score -= 50
    elif aq.aqi > 200:
        score -= 40
    elif aq.aqi > 150:
        score -= 30
    elif aq.aqi > 100:
        score -= 20
    elif aq.aqi > 50:
        score -= 10

    # Temperature comfort penalty
    if w.temperature_c > 40 or w.temperature_c < -15:
        score -= 20
    elif w.temperature_c > 35 or w.temperature_c < -5:
        score -= 10
    elif w.temperature_c > 30 or w.temperature_c < 5:
        score -= 5

    # Rain penalty
    if w.rain_mm > 10:
        score -= 10
    elif w.rain_mm > 2:
        score -= 5

    # Wind penalty
    if w.wind_speed_kmh > 50:
        score -= 10
    elif w.wind_speed_kmh > 30:
        score -= 5

    return max(0, min(100, score))


def _generate_health_advisory(data: CityDataPacket) -> str:
    """Generate a health advisory string."""
    aq = data.air_quality
    w = data.weather

    advisories = []
    if aq.aqi > 200:
        advisories.append("Avoid all outdoor physical activity. Use air purifiers indoors.")
    elif aq.aqi > 150:
        advisories.append("Sensitive groups should avoid prolonged outdoor exposure.")
    elif aq.aqi > 100:
        advisories.append("People with respiratory conditions should limit outdoor activity.")

    if w.temperature_c > 38:
        advisories.append("Stay hydrated. Avoid direct sun exposure between 11 AM and 4 PM.")
    elif w.temperature_c < -10:
        advisories.append("Dress in layers. Risk of frostbite with prolonged exposure.")

    if w.rain_mm > 10:
        advisories.append("Heavy rain expected. Drive carefully and watch for flooding.")

    if not advisories:
        return "No significant health concerns. Enjoy the day!"

    return " ".join(advisories)


def _generate_best_time(data: CityDataPacket) -> str:
    """Suggest best time to visit based on current conditions."""
    w = data.weather
    aq = data.air_quality

    if aq.aqi <= 50 and 15 <= w.temperature_c <= 28 and w.rain_mm < 1:
        return "Right now is an excellent time! Great weather and clean air."
    elif aq.aqi > 150:
        return "Consider visiting during spring or autumn when pollution tends to be lower."
    elif w.temperature_c > 35:
        return "Best visited during cooler months (Oct–Mar) or early morning hours."
    elif w.temperature_c < 0:
        return "Best visited during warmer months (Apr–Sep) for outdoor activities."
    else:
        return "Current conditions are reasonable. Mornings tend to have the best air quality."


def generate_recommendations(data: CityDataPacket, analysis: AnalysisResult) -> RecommendationReport:
    """Generate the full recommendation report."""
    recs = []
    aq = data.air_quality
    w = data.weather

    # ── Health Recommendations ──
    if aq.aqi > 150:
        recs.append(Recommendation(
            category="health", title="Wear a Mask Outdoors",
            description=f"With AQI at {aq.aqi}, an N95 mask is recommended for outdoor activities.",
            priority=RiskLevel.HIGH, icon="😷",
        ))
    if aq.aqi > 100:
        recs.append(Recommendation(
            category="health", title="Run Air Purifiers Indoors",
            description="Keep windows closed and run HEPA air purifiers to maintain indoor air quality.",
            priority=RiskLevel.MODERATE, icon="🌬️",
        ))

    # ── Weather Recommendations ──
    if w.rain_mm > 0.5:
        recs.append(Recommendation(
            category="travel", title="Carry Rain Gear",
            description=f"Rainfall of {w.rain_mm}mm detected. Bring an umbrella or waterproof jacket.",
            priority=RiskLevel.LOW, icon="☔",
        ))
    if w.temperature_c > 35:
        recs.append(Recommendation(
            category="health", title="Heat Protection",
            description="Apply sunscreen, wear light clothing, and stay in shade during peak hours.",
            priority=RiskLevel.HIGH, icon="🌡️",
        ))
    if w.wind_speed_kmh > 40:
        recs.append(Recommendation(
            category="alert", title="Wind Advisory",
            description="Secure loose outdoor items and exercise caution while driving.",
            priority=RiskLevel.MODERATE, icon="💨",
        ))

    # ── Environmental Recommendations ──
    if aq.pm2_5 > 35:
        recs.append(Recommendation(
            category="environment", title="Limit Driving",
            description="Vehicle emissions contribute to PM2.5. Consider public transit or carpooling.",
            priority=RiskLevel.MODERATE, icon="🚗",
        ))
    if aq.aqi <= 50 and w.rain_mm < 1:
        recs.append(Recommendation(
            category="travel", title="Great Day for Outdoor Activities",
            description="Air quality is good and weather is dry. Perfect for walking, cycling, or sightseeing.",
            priority=RiskLevel.LOW, icon="🌟",
        ))

    # ── Travel Recommendations ──
    cluster = analysis.cluster
    recs.append(Recommendation(
        category="travel", title=f"City Profile: {cluster.cluster_name}",
        description=cluster.cluster_description,
        priority=RiskLevel.LOW, icon="🏙️",
    ))

    # Calculate score and comparison
    score = _calculate_livability_score(data, analysis)

    # Generate comparison text based on AQI
    if aq.aqi <= 50:
        comparison = "Better air quality than approximately 75% of major global cities."
    elif aq.aqi <= 100:
        comparison = "Air quality is moderate — comparable to most European and North American cities."
    elif aq.aqi <= 150:
        comparison = "Air quality is below average — worse than approximately 60% of major cities."
    else:
        comparison = "Air quality is poor — among the bottom 20% of major global cities."

    return RecommendationReport(
        city=data.city.name,
        recommendations=recs,
        health_advisory=_generate_health_advisory(data),
        best_time_to_visit=_generate_best_time(data),
        overall_score=round(score, 1),
        comparison_text=comparison,
        generated_at=datetime.now(timezone.utc),
    )
