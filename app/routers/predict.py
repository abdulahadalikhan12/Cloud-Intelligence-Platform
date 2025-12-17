from fastapi import APIRouter, HTTPException
from app.schemas import PredictionRequest, AirQualityPrediction, PollutionPrediction, ClusterRequest, ClusterResponse
import joblib
import pandas as pd
import numpy as np
import os

router = APIRouter()

MODELS_DIR = "ml/models"

# Load models (lazy loading or try/except to handle if not yet trained)
def load_model(name):
    path = f"{MODELS_DIR}/{name}"
    if os.path.exists(path):
        return joblib.load(path)
    return None

@router.post("/air-quality", response_model=AirQualityPrediction)
def predict_air_quality(req: PredictionRequest):
    model = load_model("risk_xgboost.pkl")
    encoder = load_model("classification_label_encoder.pkl")
    scaler = load_model("classification_scaler.pkl")
    
    if not model or not encoder or not scaler:
        raise HTTPException(status_code=503, detail="Model not available (training required)")
        
    features = [[req.temperature, req.humidity, req.rain, req.pressure, req.wind_speed, req.month, req.hour]]
    features_scaled = scaler.transform(features)
    
    pred_encoded = model.predict(features_scaled)[0]
    pred_label = encoder.inverse_transform([pred_encoded])[0]
    
    # Mock confidence for now
    confidence = np.max(model.predict_proba(features_scaled))
    
    return {"aqi_category": pred_label, "confidence": float(confidence)}

@router.post("/pollution", response_model=PollutionPrediction)
def predict_pollution(req: PredictionRequest):
    model = load_model("pollution_xgboost.pkl")
    scaler = load_model("regression_scaler.pkl")
    
    if not model or not scaler:
        raise HTTPException(status_code=503, detail="Model not available")
    
    features = [[req.temperature, req.humidity, req.rain, req.pressure, req.wind_speed, req.month, req.hour]]
    features_scaled = scaler.transform(features)
    pred = model.predict(features_scaled)[0]
    
    return {"predicted_pm25": float(pred)}

@router.post("/cities", response_model=ClusterResponse) # POST /cluster/cities
def cluster_cities(req: ClusterRequest):
    model = load_model("kmeans_model.pkl")
    scaler = load_model("clustering_scaler.pkl")
    
    if not model or not scaler:
        raise HTTPException(status_code=503, detail="Model not available")
        
    features = [[req.temperature, req.humidity, req.rain, req.pm2_5]]
    features_scaled = scaler.transform(features)
    cluster = model.predict(features_scaled)[0]
    
    # Naming clusters based on simple logic or mock
    names = {0: "Low Pollution / Moderate Climate", 1: "High Pollution / Industrial", 2: "Extreme Weather"}
    
    return {"cluster_id": int(cluster), "cluster_name": names.get(cluster, "Unknown Group")}

@router.get("/analysis", response_model=list[dict])
def get_clustering_analysis():
    # Helper to return data for plotting (Temp vs PM2.5 with Cluster labels)
    
    # Check if models exist
    model = load_model("kmeans_model.pkl")
    scaler = load_model("clustering_scaler.pkl")
    data_path = "data/raw_climate_data.csv"
    
    if not model or not scaler or not os.path.exists(data_path):
        # Return empty list or mock if training not done, but better to be honest
        return []

    # Reload data to predict clusters for all points
    # NOTE: In prod, we might cache this result or save it as a JSON artifact during training
    try:
        df = pd.read_csv(data_path)
        # Quick preprocessing match
        features = ['temperature', 'humidity', 'rain', 'pm2_5']
        # Ensure columns exist (handling potential missing columns if raw data differs)
        if not all(col in df.columns for col in features):
            return []
            
        df = df[features].dropna()
        
        # We need to aggregate by city like in training? 
        # The training was on city_profiles (groupby city). 
        # If we plot specific points, we should ideally predict on points or use the city profiles.
        # Let's use City Profiles for the Scatter plot as it makes more sense "Segmentation of Cities"
        city_profiles = df.groupby(df['city'] if 'city' in df.columns else df.index).mean(numeric_only=True) # Assuming some city column or index
        # ACTUALLY raw data has 'city' column? Let's check ingestion.
        # ingestion.py saves: city, latitude, longitude, ...
        # So yes, 'city' column exists.
        
        city_profiles = df.groupby('city')[['temperature', 'humidity', 'rain', 'pm2_5']].mean()
        
        X_scaled = scaler.transform(city_profiles)
        clusters = model.predict(X_scaled)
        
        results = []
        for city, cluster, row in zip(city_profiles.index, clusters, city_profiles.itertuples()):
             # names = {0: "Moderate", 1: "Industrial", 2: "Extreme"}
             # Mapping to the logic used in frontend or generic
             results.append({
                 "city": city,
                 "x": float(row.temperature),
                 "y": float(row.pm2_5),
                 "cluster": int(cluster)
             })
        return results

    except Exception as e:
        print(f"Error in analysis endpoint: {e}")
        return []
