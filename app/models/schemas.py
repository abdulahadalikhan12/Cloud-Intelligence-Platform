"""
Pydantic v2 models for all request/response types across the platform.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class AQICategory(str, Enum):
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


# ──────────────────────────────────────────────
# Geo & City Models
# ──────────────────────────────────────────────

class GeoPoint(BaseModel):
    """Geographic coordinate point."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class CityInfo(BaseModel):
    """City information with geographic data."""
    name: str
    country: str
    lat: float
    lon: float
    population: Optional[int] = None
    timezone: Optional[str] = None
    continent: Optional[str] = None


class CitySearchResult(BaseModel):
    """Result from a city search query."""
    cities: list[CityInfo]
    total: int
    query: str


class NearbyQuery(BaseModel):
    """Query for finding nearby cities."""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=100, ge=1, le=5000)


# ──────────────────────────────────────────────
# Weather Models
# ──────────────────────────────────────────────

class WeatherCurrent(BaseModel):
    """Current weather conditions for a location."""
    city: str
    country: Optional[str] = None
    lat: float
    lon: float
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    wind_direction_deg: Optional[float] = None
    rain_mm: float
    pressure_hpa: Optional[float] = None
    cloud_cover_pct: Optional[float] = None
    condition: str
    feels_like_c: Optional[float] = None
    timestamp: datetime


class ForecastDay(BaseModel):
    """Single day forecast data."""
    date: str
    temp_max_c: float
    temp_min_c: float
    temp_avg_c: float
    precipitation_mm: float
    precipitation_probability_pct: float
    wind_speed_max_kmh: float
    condition: str
    uv_index_max: Optional[float] = None


class WeatherForecast(BaseModel):
    """Multi-day weather forecast."""
    city: str
    lat: float
    lon: float
    forecast_days: list[ForecastDay]
    generated_at: datetime


class HistoricalWeather(BaseModel):
    """Historical weather data point."""
    date: str
    temperature_c: float
    humidity_pct: float
    rain_mm: float
    wind_speed_kmh: float
    pressure_hpa: Optional[float] = None


class WeatherHistory(BaseModel):
    """Historical weather data response."""
    city: str
    lat: float
    lon: float
    period_start: str
    period_end: str
    daily_data: list[HistoricalWeather]


# ──────────────────────────────────────────────
# Air Quality Models
# ──────────────────────────────────────────────

class AirQualityCurrent(BaseModel):
    """Current air quality data."""
    city: str
    lat: float
    lon: float
    aqi: int = Field(..., ge=0, le=500, description="Air Quality Index (EPA standard)")
    category: AQICategory
    pm2_5: float = Field(..., description="PM2.5 (µg/m³)")
    pm10: float = Field(..., description="PM10 (µg/m³)")
    no2: float = Field(..., description="NO₂ (µg/m³)")
    o3: float = Field(..., description="Ozone (µg/m³)")
    dominant_pollutant: str
    timestamp: datetime


class AQForecastDay(BaseModel):
    """Single day AQ forecast."""
    date: str
    aqi_avg: int
    aqi_max: int
    pm2_5_avg: float
    pm10_avg: float
    category: AQICategory


class AirQualityForecast(BaseModel):
    """Air quality forecast response."""
    city: str
    lat: float
    lon: float
    forecast_days: list[AQForecastDay]
    generated_at: datetime


class CityRanking(BaseModel):
    """City ranked by air quality."""
    rank: int
    city: str
    country: str
    aqi: int
    category: AQICategory
    pm2_5: float
    lat: float
    lon: float


class AQRankings(BaseModel):
    """Air quality rankings response."""
    cleanest: list[CityRanking]
    most_polluted: list[CityRanking]
    generated_at: datetime


# ──────────────────────────────────────────────
# Prediction Models
# ──────────────────────────────────────────────

class PredictionRequest(BaseModel):
    """Input features for ML prediction."""
    temperature: float = Field(..., description="Temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    rain: float = Field(..., ge=0, description="Rainfall in mm")
    pressure: float = Field(..., description="Surface pressure in hPa")
    wind_speed: float = Field(..., ge=0, description="Wind speed in km/h")
    month: int = Field(..., ge=1, le=12)
    hour: int = Field(..., ge=0, le=23)


class AQIRiskPrediction(BaseModel):
    """AQI risk classification result."""
    aqi_category: str
    confidence: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    features_used: dict


class PollutionPrediction(BaseModel):
    """PM2.5 regression prediction result."""
    predicted_pm25: float
    risk_level: RiskLevel
    features_used: dict


class ClusterRequest(BaseModel):
    """Input for city clustering."""
    temperature: float
    humidity: float
    rain: float
    pm2_5: float


class ClusterResult(BaseModel):
    """City cluster assignment result."""
    cluster_id: int
    cluster_name: str
    cluster_description: str
    similar_cities: list[str]


class ClusterAnalysis(BaseModel):
    """Full clustering visualization data."""
    clusters: list[dict]
    city_assignments: list[dict]
    silhouette_score: Optional[float] = None


# ──────────────────────────────────────────────
# Agent Models
# ──────────────────────────────────────────────

class CityDataPacket(BaseModel):
    """Normalized data packet from ingestion agent."""
    city: CityInfo
    weather: WeatherCurrent
    air_quality: AirQualityCurrent
    ingested_at: datetime


class AnalysisInsight(BaseModel):
    """Single insight generated by analysis agent."""
    category: str  # "weather", "air_quality", "trend", "anomaly"
    title: str
    description: str
    severity: RiskLevel
    data: Optional[dict] = None


class AnalysisResult(BaseModel):
    """Complete analysis from analysis agent."""
    city: str
    aqi_prediction: AQIRiskPrediction
    pollution_prediction: PollutionPrediction
    cluster: ClusterResult
    insights: list[AnalysisInsight]
    analyzed_at: datetime


class Recommendation(BaseModel):
    """Single actionable recommendation."""
    category: str  # "health", "travel", "environment", "alert"
    title: str
    description: str
    priority: RiskLevel
    icon: str  # emoji for frontend display


class RecommendationReport(BaseModel):
    """Full recommendation report from recommendation agent."""
    city: str
    recommendations: list[Recommendation]
    health_advisory: str
    best_time_to_visit: Optional[str] = None
    overall_score: float = Field(..., ge=0, le=100, description="City livability score")
    comparison_text: str  # "Better air quality than X% of cities"
    generated_at: datetime


class IntelligenceReport(BaseModel):
    """Complete intelligence report — final output of agent pipeline."""
    city: str
    country: Optional[str] = None
    lat: float
    lon: float
    weather: WeatherCurrent
    air_quality: AirQualityCurrent
    analysis: AnalysisResult
    recommendations: RecommendationReport
    generated_at: datetime


class CityComparison(BaseModel):
    """Multi-city comparison response."""
    cities: list[IntelligenceReport]
    summary: str
    best_overall: str
    generated_at: datetime


class SemanticSearchQuery(BaseModel):
    """Semantic search input."""
    query: str = Field(..., min_length=3, max_length=500, description="Natural language query")
    top_k: int = Field(default=5, ge=1, le=20)


class SemanticSearchResult(BaseModel):
    """Single semantic search result."""
    city: str
    country: str
    lat: float
    lon: float
    score: float
    summary: str


class SemanticSearchResponse(BaseModel):
    """Semantic search results."""
    query: str
    results: list[SemanticSearchResult]
    total: int


# ──────────────────────────────────────────────
# System Models
# ──────────────────────────────────────────────

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    uptime_seconds: float


class SystemStatus(BaseModel):
    """Detailed system status."""
    status: str
    version: str
    models_loaded: dict[str, bool]
    faiss_index_size: int
    cities_count: int
    cache_stats: dict
    uptime_seconds: float
