"""
Analysis Agent: Runs ML models and generates structured insights
from the ingested city data. Second stage of the agent pipeline.
"""

from datetime import datetime, timezone

from app.models.schemas import (
    AnalysisInsight,
    AnalysisResult,
    CityDataPacket,
    RiskLevel,
)
from app.services import ml_service


def _generate_weather_insights(data: CityDataPacket) -> list[AnalysisInsight]:
    """Generate insights from weather data."""
    insights = []
    w = data.weather

    # Temperature insight
    if w.temperature_c > 40:
        insights.append(AnalysisInsight(
            category="weather", title="Extreme Heat Warning",
            description=f"Temperature is {w.temperature_c}°C — dangerous heat levels. Stay hydrated and avoid outdoor exposure.",
            severity=RiskLevel.CRITICAL,
        ))
    elif w.temperature_c > 35:
        insights.append(AnalysisInsight(
            category="weather", title="High Temperature Alert",
            description=f"Temperature is {w.temperature_c}°C — above comfortable levels. Take precautions for heat-related issues.",
            severity=RiskLevel.HIGH,
        ))
    elif w.temperature_c < -10:
        insights.append(AnalysisInsight(
            category="weather", title="Extreme Cold Warning",
            description=f"Temperature is {w.temperature_c}°C — risk of frostbite and hypothermia.",
            severity=RiskLevel.CRITICAL,
        ))
    elif w.temperature_c < 0:
        insights.append(AnalysisInsight(
            category="weather", title="Freezing Conditions",
            description=f"Temperature is {w.temperature_c}°C — below freezing. Watch for ice and slippery conditions.",
            severity=RiskLevel.MODERATE,
        ))

    # Wind insight
    if w.wind_speed_kmh > 60:
        insights.append(AnalysisInsight(
            category="weather", title="Strong Wind Advisory",
            description=f"Winds at {w.wind_speed_kmh} km/h. Secure loose objects and avoid high-profile vehicles.",
            severity=RiskLevel.HIGH,
        ))

    # Rain insight
    if w.rain_mm > 10:
        insights.append(AnalysisInsight(
            category="weather", title="Heavy Rainfall",
            description=f"Current rainfall: {w.rain_mm}mm. Risk of localized flooding.",
            severity=RiskLevel.MODERATE,
        ))

    return insights


def _generate_aq_insights(data: CityDataPacket) -> list[AnalysisInsight]:
    """Generate insights from air quality data."""
    insights = []
    aq = data.air_quality

    if aq.aqi > 200:
        insights.append(AnalysisInsight(
            category="air_quality", title="Severe Air Pollution",
            description=f"AQI is {aq.aqi} ({aq.category.value}). Everyone should avoid outdoor activities. Dominant pollutant: {aq.dominant_pollutant}.",
            severity=RiskLevel.CRITICAL,
        ))
    elif aq.aqi > 100:
        insights.append(AnalysisInsight(
            category="air_quality", title="Elevated Air Pollution",
            description=f"AQI is {aq.aqi} ({aq.category.value}). Sensitive groups should limit outdoor exposure. Dominant: {aq.dominant_pollutant}.",
            severity=RiskLevel.HIGH,
        ))
    elif aq.aqi > 50:
        insights.append(AnalysisInsight(
            category="air_quality", title="Moderate Air Quality",
            description=f"AQI is {aq.aqi} ({aq.category.value}). Acceptable for most, but unusually sensitive people may experience issues.",
            severity=RiskLevel.MODERATE,
        ))
    else:
        insights.append(AnalysisInsight(
            category="air_quality", title="Good Air Quality",
            description=f"AQI is {aq.aqi} — air quality is satisfactory with minimal health risk.",
            severity=RiskLevel.LOW,
        ))

    return insights


def analyze_city_data(data: CityDataPacket) -> AnalysisResult:
    """
    Run full analysis pipeline on ingested city data.
    - AQI risk classification
    - PM2.5 prediction
    - Cluster assignment
    - Insight generation
    """
    w = data.weather
    aq = data.air_quality
    now = datetime.now(timezone.utc)

    # Run ML predictions
    aqi_pred = ml_service.predict_aqi_risk(
        temperature=w.temperature_c,
        humidity=w.humidity_pct,
        rain=w.rain_mm,
        pressure=w.pressure_hpa or 1013.25,
        wind_speed=w.wind_speed_kmh,
        month=now.month,
        hour=now.hour,
    )

    pollution_pred = ml_service.predict_pollution(
        temperature=w.temperature_c,
        humidity=w.humidity_pct,
        rain=w.rain_mm,
        pressure=w.pressure_hpa or 1013.25,
        wind_speed=w.wind_speed_kmh,
        month=now.month,
        hour=now.hour,
    )

    cluster = ml_service.predict_cluster(
        temperature=w.temperature_c,
        humidity=w.humidity_pct,
        rain=w.rain_mm,
        pm2_5=aq.pm2_5,
    )

    # Generate insights
    insights = []
    insights.extend(_generate_weather_insights(data))
    insights.extend(_generate_aq_insights(data))

    # Prediction vs actual comparison
    if abs(pollution_pred.predicted_pm25 - aq.pm2_5) > 20:
        insights.append(AnalysisInsight(
            category="anomaly", title="PM2.5 Anomaly Detected",
            description=f"Actual PM2.5 ({aq.pm2_5}) differs significantly from model prediction ({pollution_pred.predicted_pm25}). Unusual conditions may be present.",
            severity=RiskLevel.MODERATE,
            data={"actual": aq.pm2_5, "predicted": pollution_pred.predicted_pm25},
        ))

    return AnalysisResult(
        city=data.city.name,
        aqi_prediction=aqi_pred,
        pollution_prediction=pollution_pred,
        cluster=cluster,
        insights=insights,
        analyzed_at=now,
    )
