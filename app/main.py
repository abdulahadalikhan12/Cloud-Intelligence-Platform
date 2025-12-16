from fastapi import FastAPI
from app.routers import weather, predict

app = FastAPI(
    title="Climate Intelligence Platform",
    description="Real-Time Weather Analytics & Pollution Risk Prediction API",
    version="1.0.0"
)

app.include_router(weather.router, prefix="/weather", tags=["Weather"])
# "POST /search/weather" was not the requirement, it was "/forecast/weather". 
# The router defines /forecast, so prefix /weather makes it /weather/forecast.
# But requirement said POST /forecast/weather. I should probably adjust prefix or router.
# Let's clean up routing.
# Req: POST /forecast/weather
# Req: POST /cluster/cities
# Req: POST /predict/air-quality

# I will fix this in main.py by mounting carefully
app.include_router(predict.router, prefix="/predict", tags=["Prediction"]) 
# This covers /predict/air-quality and /predict/pollution

# For others, I can create a 'miscellaneous' router or mount specifically.
# Let's use a specific router for 'forecast' and 'cluster' to match paths exactly.

from fastapi import APIRouter
misc_router = APIRouter()

@misc_router.post("/forecast/weather", tags=["Forecasting"])
def forecast_proxy(city: str):
    # Proxy to weather router logic (reuse function)
    return weather.get_weather_forecast(city)

@misc_router.post("/cluster/cities", tags=["Clustering"])
def cluster_proxy(req: predict.ClusterRequest):
    return predict.cluster_cities(req)

app.include_router(misc_router)

@app.get("/")
def read_root():
    return {"status": "active", "service": "Climate Intelligence Platform Code"}
