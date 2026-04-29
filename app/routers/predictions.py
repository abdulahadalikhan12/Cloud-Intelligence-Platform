"""ML prediction endpoints."""

from fastapi import APIRouter

from app.models.schemas import (
    AQIRiskPrediction,
    ClusterRequest,
    ClusterResult,
    PollutionPrediction,
    PredictionRequest,
)
from app.services import ml_service

router = APIRouter(prefix="/api/v1/predict", tags=["Predictions"])


@router.post("/aqi-risk", response_model=AQIRiskPrediction)
def predict_aqi_risk(req: PredictionRequest):
    """Classify AQI risk category from environmental features."""
    return ml_service.predict_aqi_risk(
        req.temperature, req.humidity, req.rain,
        req.pressure, req.wind_speed, req.month, req.hour,
    )


@router.post("/pollution", response_model=PollutionPrediction)
def predict_pollution(req: PredictionRequest):
    """Predict PM2.5 concentration from environmental features."""
    return ml_service.predict_pollution(
        req.temperature, req.humidity, req.rain,
        req.pressure, req.wind_speed, req.month, req.hour,
    )


@router.post("/cluster", response_model=ClusterResult)
def predict_cluster(req: ClusterRequest):
    """Assign a city to an environmental cluster based on its metrics."""
    return ml_service.predict_cluster(req.temperature, req.humidity, req.rain, req.pm2_5)
