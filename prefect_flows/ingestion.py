import requests
import pandas as pd
from prefect import task, flow
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

# Setup Open-Meteo Client with cache and retry
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

CITIES = {
    "London": {"lat": 51.5074, "lon": -0.1278},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Sydney": {"lat": -33.8688, "lon": 151.2093}
}

@task(retries=3)
def fetch_weather_history(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "surface_pressure", "wind_speed_10m"]
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }
    hourly_data["temperature"] = hourly.Variables(0).ValuesAsNumpy()
    hourly_data["humidity"] = hourly.Variables(1).ValuesAsNumpy()
    hourly_data["rain"] = hourly.Variables(2).ValuesAsNumpy()
    hourly_data["pressure"] = hourly.Variables(3).ValuesAsNumpy()
    hourly_data["wind_speed"] = hourly.Variables(4).ValuesAsNumpy()
    
    df = pd.DataFrame(data=hourly_data)
    return df

@task(retries=3)
def fetch_aq_history(lat, lon, start_date, end_date):
    # OpenAQ API (using v2 or v3)
    # Note: OpenAQ historical data via API can be sparse or require pagination.
    # For this academic project, we will mock the "Historical" aspect of AQ if strictly needed,
    # OR fetch what is available. 
    # However, Open-Meteo ALSO provides Air Quality Archive! Use that for consistency and reliability.
    
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["pm10", "pm2_5", "nitrogen_dioxide", "ozone"]
    }
    # Note: Using Open-Meteo AQ API for easier historical data access than OpenAQ for this specific 'Archive' task
    # We will still use OpenAQ for 'Current' checks if requested, but for training dataset, Open-Meteo AQ is superior.
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }
    hourly_data["pm10"] = hourly.Variables(0).ValuesAsNumpy()
    hourly_data["pm2_5"] = hourly.Variables(1).ValuesAsNumpy()
    hourly_data["no2"] = hourly.Variables(2).ValuesAsNumpy()
    hourly_data["ozone"] = hourly.Variables(3).ValuesAsNumpy()
    
    df = pd.DataFrame(data=hourly_data)
    return df

@task
def merge_data(weather_df, aq_df, city_name):
    # Merge on date
    df = pd.merge(weather_df, aq_df, on="date", how="inner")
    df['city'] = city_name
    return df

@flow(name="Climate Data Ingestion")
def ingestion_flow():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90) # Last 3 months for training
    
    all_data = []
    
    for city_name, coords in CITIES.items():
        print(f"Fetching data for {city_name}...")
        w_df = fetch_weather_history(coords['lat'], coords['lon'], start_date, end_date)
        aq_df = fetch_aq_history(coords['lat'], coords['lon'], start_date, end_date)
        
        merged = merge_data(w_df, aq_df, city_name)
        all_data.append(merged)
    
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Save raw data
    final_df.to_csv("data/raw_climate_data.csv", index=False)
    print(f"Ingested {len(final_df)} rows of data.")
    return final_df

if __name__ == "__main__":
    ingestion_flow()
