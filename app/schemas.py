from pydantic import BaseModel
from typing import List, Optional

class WeatherCurrentResponse(BaseModel):
    city_name: str
    temperature: float
    humidity: float
    wind_speed: float
    condition: str  # e.g. "Cloudy"

class PredictionRequest(BaseModel):
    temperature: float
    humidity: float
    rain: float
    pressure: float
    wind_speed: float
    month: int
    hour: int

class AirQualityPrediction(BaseModel):
    aqi_category: str
    confidence: Optional[float] = None

class PollutionPrediction(BaseModel):
    predicted_pm25: float

class ForecastRequest(BaseModel):
    city: str
    days: int = 3

class ForecastPoint(BaseModel):
    date: str
    temperature: float
    wind_speed: float
    rain: float
    precipitation_probability: float
    aqi: Optional[float] = None # Forecasted AQI if available

class ForecastResponse(BaseModel):
    city: str
    forecast: List[ForecastPoint]

class ClusterRequest(BaseModel):
    temperature: float
    humidity: float
    rain: float
    pm2_5: float

class ClusterResponse(BaseModel):
    cluster_id: int
    cluster_name: str # e.g., "Industrial City", "Clean Coastal"
