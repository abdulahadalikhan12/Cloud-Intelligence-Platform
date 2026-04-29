"""
Data preprocessing and feature engineering for ML training.
"""

import pandas as pd
import numpy as np


def calculate_aqi_category(pm25: float) -> str:
    """Convert PM2.5 to EPA AQI category string."""
    if pm25 <= 12:
        return "Good"
    elif pm25 <= 35.4:
        return "Moderate"
    elif pm25 <= 55.4:
        return "Unhealthy for Sensitive Groups"
    elif pm25 <= 150.4:
        return "Unhealthy"
    elif pm25 <= 250.4:
        return "Very Unhealthy"
    return "Hazardous"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw climate data: handle missing values and outliers."""
    df = df.copy()

    # Forward fill then median fill for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].ffill()
    for col in numeric_cols:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    # Cap outliers using IQR method
    for col in ["temperature", "humidity", "rain", "wind_speed", "pm2_5", "pm10"]:
        if col in df.columns:
            q1 = df[col].quantile(0.01)
            q99 = df[col].quantile(0.99)
            df[col] = df[col].clip(q1, q99)

    # Ensure non-negative for pollution metrics
    for col in ["pm2_5", "pm10", "no2", "ozone", "rain"]:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based and derived features."""
    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
        df["month"] = df["date"].dt.month
        df["hour"] = df["date"].dt.hour
        df["day_of_week"] = df["date"].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # Season (Northern Hemisphere approximation)
        def get_season(month):
            if month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            elif month in [9, 10, 11]:
                return "autumn"
            return "winter"

        df["season"] = df["month"].apply(get_season)

    # AQI category from PM2.5
    if "pm2_5" in df.columns and "aqi_category" not in df.columns:
        df["aqi_category"] = df["pm2_5"].apply(calculate_aqi_category)

    return df
