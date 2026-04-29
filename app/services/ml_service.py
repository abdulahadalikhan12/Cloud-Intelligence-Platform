"""
ML service: loads pre-trained models and runs inference.
Models are loaded once at startup and kept in memory.
"""

from pathlib import Path

import joblib
import numpy as np

from app.config import get_settings
from app.models.schemas import (
    AQIRiskPrediction,
    ClusterResult,
    PollutionPrediction,
    RiskLevel,
)

settings = get_settings()

# ── Model Registry ───────────────────────────────────────
_models: dict[str, object] = {}
_models_loaded = False


def load_all_models():
    """Load all pre-trained models into memory. Called at startup."""
    global _models, _models_loaded
    models_dir = Path(settings.MODELS_DIR)

    model_files = {
        "risk_classifier": "risk_xgboost.joblib",
        "risk_scaler": "classification_scaler.joblib",
        "risk_encoder": "classification_label_encoder.joblib",
        "pollution_regressor": "pollution_xgboost.joblib",
        "pollution_scaler": "regression_scaler.joblib",
        "kmeans": "kmeans_model.joblib",
        "cluster_scaler": "clustering_scaler.joblib",
        "pca": "pca_model.joblib",
    }

    for key, filename in model_files.items():
        path = models_dir / filename
        if path.exists():
            try:
                _models[key] = joblib.load(path)
            except Exception as e:
                print(f"Warning: Failed to load {filename}: {e}")
        else:
            print(f"Info: Model file not found: {path}")

    _models_loaded = True
    print(f"ML Service: Loaded {len(_models)}/{len(model_files)} models")


def get_models_status() -> dict[str, bool]:
    """Return which models are available."""
    return {
        "risk_classifier": "risk_classifier" in _models,
        "pollution_regressor": "pollution_regressor" in _models,
        "clustering": "kmeans" in _models,
    }


def _pm25_to_risk(pm25: float) -> RiskLevel:
    if pm25 <= 12:
        return RiskLevel.LOW
    if pm25 <= 35.4:
        return RiskLevel.MODERATE
    if pm25 <= 150.4:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _category_to_risk(category: str) -> RiskLevel:
    mapping = {
        "Good": RiskLevel.LOW,
        "Moderate": RiskLevel.MODERATE,
        "Unhealthy for Sensitive Groups": RiskLevel.MODERATE,
        "Unhealthy": RiskLevel.HIGH,
        "Very Unhealthy": RiskLevel.HIGH,
        "Hazardous": RiskLevel.CRITICAL,
    }
    return mapping.get(category, RiskLevel.MODERATE)


# Cluster descriptions (pre-defined based on training data characteristics)
CLUSTER_INFO = {
    0: {
        "name": "Temperate & Clean",
        "description": "Cities with moderate temperatures and good air quality. Typically coastal or well-regulated urban areas.",
        "similar": ["London", "Sydney", "Tokyo", "Berlin", "Vancouver"],
    },
    1: {
        "name": "Hot & Polluted",
        "description": "Cities with high temperatures and elevated pollution levels. Often dense urban/industrial areas in developing regions.",
        "similar": ["Delhi", "Beijing", "Dhaka", "Karachi", "Lahore"],
    },
    2: {
        "name": "Extreme & Variable",
        "description": "Cities with extreme temperature variations and mixed air quality. Often continental or arid climates.",
        "similar": ["Moscow", "Ulaanbaatar", "Almaty", "Denver", "Riyadh"],
    },
}


def predict_aqi_risk(
    temperature: float, humidity: float, rain: float, pressure: float, wind_speed: float, month: int, hour: int
) -> AQIRiskPrediction:
    """Predict AQI risk category using the trained classifier."""
    features = {
        "temperature": temperature,
        "humidity": humidity,
        "rain": rain,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "month": month,
        "hour": hour,
    }

    if "risk_classifier" not in _models:
        # Fallback: rule-based estimation
        return AQIRiskPrediction(
            aqi_category="Moderate",
            confidence=0.5,
            risk_level=RiskLevel.MODERATE,
            features_used=features,
        )

    scaler = _models["risk_scaler"]
    model = _models["risk_classifier"]
    encoder = _models["risk_encoder"]

    X = np.array([[temperature, humidity, rain, pressure, wind_speed, month, hour]])
    X_scaled = scaler.transform(X)
    pred_encoded = model.predict(X_scaled)[0]
    pred_label = encoder.inverse_transform([pred_encoded])[0]
    confidence = float(np.max(model.predict_proba(X_scaled)))

    return AQIRiskPrediction(
        aqi_category=pred_label,
        confidence=round(confidence, 3),
        risk_level=_category_to_risk(pred_label),
        features_used=features,
    )


def predict_pollution(
    temperature: float, humidity: float, rain: float, pressure: float, wind_speed: float, month: int, hour: int
) -> PollutionPrediction:
    """Predict PM2.5 concentration using the trained regressor."""
    features = {
        "temperature": temperature,
        "humidity": humidity,
        "rain": rain,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "month": month,
        "hour": hour,
    }

    if "pollution_regressor" not in _models:
        # Fallback: simple estimation
        estimated = max(5, 30 - wind_speed * 0.5 + humidity * 0.1)
        return PollutionPrediction(
            predicted_pm25=round(estimated, 1),
            risk_level=_pm25_to_risk(estimated),
            features_used=features,
        )

    scaler = _models["pollution_scaler"]
    model = _models["pollution_regressor"]

    X = np.array([[temperature, humidity, rain, pressure, wind_speed, month, hour]])
    X_scaled = scaler.transform(X)
    pred = float(model.predict(X_scaled)[0])

    return PollutionPrediction(
        predicted_pm25=round(max(0, pred), 1),
        risk_level=_pm25_to_risk(pred),
        features_used=features,
    )


def predict_cluster(temperature: float, humidity: float, rain: float, pm2_5: float) -> ClusterResult:
    """Assign a city to an environmental cluster."""
    if "kmeans" not in _models:
        # Fallback: rule-based
        if pm2_5 > 50:
            cluster_id = 1
        elif temperature > 30 or temperature < -5:
            cluster_id = 2
        else:
            cluster_id = 0

        info = CLUSTER_INFO[cluster_id]
        return ClusterResult(
            cluster_id=cluster_id,
            cluster_name=info["name"],
            cluster_description=info["description"],
            similar_cities=info["similar"],
        )

    scaler = _models["cluster_scaler"]
    model = _models["kmeans"]

    X = np.array([[temperature, humidity, rain, pm2_5]])
    X_scaled = scaler.transform(X)
    cluster_id = int(model.predict(X_scaled)[0])

    info = CLUSTER_INFO.get(cluster_id, CLUSTER_INFO[0])
    return ClusterResult(
        cluster_id=cluster_id,
        cluster_name=info["name"],
        cluster_description=info["description"],
        similar_cities=info["similar"],
    )
