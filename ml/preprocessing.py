import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic data cleaning: drop duplicates, handle NaNs.
    """
    df = df.drop_duplicates()
    # Interpolate missing values (common in time series) - only on numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear', limit_direction='both')
    return df

def categorize_aqi(pm25_value):
    """
    Categorize PM2.5 into simplified AQI classes.
    """
    if pm25_value <= 12.0:
        return "Good"
    elif pm25_value <= 35.4:
        return "Moderate"
    elif pm25_value <= 55.4:
        return "Unhealthy (Sensitive)"
    elif pm25_value <= 150.4:
        return "Unhealthy"
    else:
        return "Hazardous"

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add feature columns.
    """
    # Create target for Classification
    if 'pm2_5' in df.columns:
        df['aqi_category'] = df['pm2_5'].apply(categorize_aqi)
    
    # Extract temporal features
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['hour'] = df['date'].dt.hour
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
    
    return df
