from fastapi import APIRouter, HTTPException
from app.schemas import WeatherCurrentResponse, ForecastResponse, ForecastPoint
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from datetime import datetime

router = APIRouter()

# Setup Open-Meteo Client
cache_session = requests_cache.CachedSession('.cache', expire_after=300)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_coords(city: str):
    # Mock geocoding for simplicity in this lab
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
    return CITIES.get(city)

@router.get("/current", response_model=WeatherCurrentResponse)
def get_current_weather(city: str):
    coords = get_coords(city)
    if not coords:
        raise HTTPException(status_code=404, detail="City not found in supported list")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords['lat'],
        "longitude": coords['lon'],
        "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "rain"]
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()
    
    return {
        "city_name": city,
        "temperature": current.Variables(0).Value(),
        "humidity": current.Variables(1).Value(),
        "wind_speed": current.Variables(2).Value(),
        "condition": "Rainy" if current.Variables(3).Value() > 0 else "Clear" # Simple logic
    }

@router.post("/forecast", response_model=ForecastResponse)
def get_weather_forecast(city: str): # Could use body if complex, but query param is simpler for GET. Requirements say POST /forecast/weather
    coords = get_coords(city)
    if not coords:
        raise HTTPException(status_code=404, detail="City not found")
        
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords['lat'],
        "longitude": coords['lon'],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", "precipitation_probability_max"],
        "forecast_days": 3
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    daily = response.Daily()
    
    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )
    
    max_temps = daily.Variables(0).ValuesAsNumpy()
    min_temps = daily.Variables(1).ValuesAsNumpy()
    precip_sums = daily.Variables(2).ValuesAsNumpy()
    max_winds = daily.Variables(3).ValuesAsNumpy()
    precip_probs = daily.Variables(4).ValuesAsNumpy()
    
    forecast_points = []
    for i in range(len(dates)):
        avg_temp = (max_temps[i] + min_temps[i]) / 2
        forecast_points.append(
            ForecastPoint(
                date=str(dates[i].date()), 
                temperature=float(avg_temp), 
                wind_speed=float(max_winds[i]),
                rain=float(precip_sums[i]),
                precipitation_probability=float(precip_probs[i]),
                aqi=None
            )
        )
        
    return {"city": city, "forecast": forecast_points}
