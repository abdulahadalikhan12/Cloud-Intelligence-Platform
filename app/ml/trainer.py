"""
ML Model Training Pipeline.
Fetches data from Open-Meteo APIs, trains classification/regression/clustering models,
and saves them as .joblib files for the API to load at startup.

Usage: python -m app.ml.trainer
"""

import os
from datetime import datetime, timedelta, timezone

import httpx
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.ml.preprocessing import clean_data, engineer_features

MODELS_DIR = "app/ml/pretrained"
TRAINING_CITIES = [
    ("London", 51.5074, -0.1278), ("New York", 40.7128, -74.006),
    ("Tokyo", 35.6762, 139.6503), ("Delhi", 28.6139, 77.209),
    ("Beijing", 39.9042, 116.4074), ("Paris", 48.8566, 2.3522),
    ("Berlin", 52.52, 13.405), ("Sydney", -33.8688, 151.2093),
    ("Moscow", 55.7558, 37.6173), ("Dubai", 25.2048, 55.2708),
    ("Singapore", 1.3521, 103.8198), ("Cairo", 30.0444, 31.2357),
    ("Lagos", 6.5244, 3.3792), ("Mumbai", 19.076, 72.8777),
    ("São Paulo", -23.5505, -46.6333), ("Seoul", 37.5665, 126.978),
    ("Los Angeles", 34.0522, -118.2437), ("Bangkok", 13.7563, 100.5018),
    ("Jakarta", -6.2088, 106.8456), ("Mexico City", 19.4326, -99.1332),
    ("Istanbul", 41.0082, 28.9784), ("Buenos Aires", -34.6037, -58.3816),
    ("Karachi", 24.8607, 67.0011), ("Johannesburg", -26.2041, 28.0473),
    ("Lima", -12.0464, -77.0428), ("Dhaka", 23.8103, 90.4125),
    ("Lahore", 31.5204, 74.3587), ("Santiago", -33.4489, -70.6693),
    ("Riyadh", 24.7136, 46.6753), ("Nairobi", -1.2921, 36.8219),
]


def fetch_training_data() -> pd.DataFrame:
    """Fetch 90 days of weather + AQ data for training cities."""
    end_date = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=95)).strftime("%Y-%m-%d")

    all_data = []
    client = httpx.Client(timeout=30.0)

    for city_name, lat, lon in TRAINING_CITIES:
        print(f"  Fetching {city_name}...")
        try:
            # Weather
            w_resp = client.get("https://archive-api.open-meteo.com/v1/archive", params={
                "latitude": lat, "longitude": lon,
                "start_date": start_date, "end_date": end_date,
                "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "surface_pressure", "wind_speed_10m"],
            })
            w_data = w_resp.json().get("hourly", {})

            # Air Quality
            aq_resp = client.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
                "latitude": lat, "longitude": lon,
                "start_date": start_date, "end_date": end_date,
                "hourly": ["pm10", "pm2_5", "nitrogen_dioxide", "ozone"],
            })
            aq_data = aq_resp.json().get("hourly", {})

            # Merge
            n = min(len(w_data.get("time", [])), len(aq_data.get("time", [])))
            for i in range(0, n, 6):  # Sample every 6 hours to reduce data size
                all_data.append({
                    "date": w_data["time"][i],
                    "city": city_name,
                    "temperature": w_data["temperature_2m"][i],
                    "humidity": w_data["relative_humidity_2m"][i],
                    "rain": w_data["rain"][i],
                    "pressure": w_data["surface_pressure"][i],
                    "wind_speed": w_data["wind_speed_10m"][i],
                    "pm10": aq_data["pm10"][i] if i < len(aq_data.get("pm10", [])) else None,
                    "pm2_5": aq_data["pm2_5"][i] if i < len(aq_data.get("pm2_5", [])) else None,
                    "no2": aq_data["nitrogen_dioxide"][i] if i < len(aq_data.get("nitrogen_dioxide", [])) else None,
                    "ozone": aq_data["ozone"][i] if i < len(aq_data.get("ozone", [])) else None,
                })
        except Exception as e:
            print(f"  Warning: Failed for {city_name}: {e}")

    client.close()
    return pd.DataFrame(all_data)


def train_all_models(df: pd.DataFrame):
    """Train classification, regression, and clustering models."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = clean_data(df)
    df = engineer_features(df)

    features = ["temperature", "humidity", "rain", "pressure", "wind_speed", "month", "hour"]
    df_clean = df.dropna(subset=features + ["pm2_5", "aqi_category"])

    # ── Classification: AQI Risk ──
    print("\n📊 Training AQI Risk Classifier...")
    X = df_clean[features].values
    le = LabelEncoder()
    y = le.fit_transform(df_clean["aqi_category"])
    joblib.dump(le, f"{MODELS_DIR}/classification_label_encoder.joblib")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler_cls = StandardScaler()
    X_train_s = scaler_cls.fit_transform(X_train)
    X_test_s = scaler_cls.transform(X_test)
    joblib.dump(scaler_cls, f"{MODELS_DIR}/classification_scaler.joblib")

    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train_s, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test_s))
    print(f"  Accuracy: {acc:.4f}")
    joblib.dump(clf, f"{MODELS_DIR}/risk_xgboost.joblib")

    # ── Regression: PM2.5 ──
    print("\n📊 Training PM2.5 Regressor...")
    y_reg = df_clean["pm2_5"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    scaler_reg = StandardScaler()
    X_train_s = scaler_reg.fit_transform(X_train)
    X_test_s = scaler_reg.transform(X_test)
    joblib.dump(scaler_reg, f"{MODELS_DIR}/regression_scaler.joblib")

    reg = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    reg.fit(X_train_s, y_train)
    rmse = np.sqrt(mean_squared_error(y_test, reg.predict(X_test_s)))
    print(f"  RMSE: {rmse:.4f}")
    joblib.dump(reg, f"{MODELS_DIR}/pollution_xgboost.joblib")

    # ── Clustering: City Segmentation ──
    print("\n📊 Training City Clustering...")
    cluster_features = ["temperature", "humidity", "rain", "pm2_5"]
    city_profiles = df_clean.groupby("city")[cluster_features].mean()

    scaler_clust = StandardScaler()
    X_clust = scaler_clust.fit_transform(city_profiles)
    joblib.dump(scaler_clust, f"{MODELS_DIR}/clustering_scaler.joblib")

    pca = PCA(n_components=2)
    pca.fit_transform(X_clust)
    joblib.dump(pca, f"{MODELS_DIR}/pca_model.joblib")

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X_clust)
    sil = silhouette_score(X_clust, kmeans.labels_) if len(city_profiles) > 3 else 0
    print(f"  Silhouette Score: {sil:.4f}")
    joblib.dump(kmeans, f"{MODELS_DIR}/kmeans_model.joblib")

    print(f"\n✅ All models saved to {MODELS_DIR}/")


def main():
    print("🔄 Cloud Intelligence — ML Training Pipeline")
    print("=" * 50)
    print("Step 1: Fetching training data...")
    df = fetch_training_data()
    print(f"  Fetched {len(df)} data points")

    if len(df) < 100:
        print("❌ Insufficient data for training. Need at least 100 rows.")
        return

    print("\nStep 2: Training models...")
    train_all_models(df)
    print("\n🎉 Training complete!")


if __name__ == "__main__":
    main()
