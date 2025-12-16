# Climate Intelligence Platform 🌍

## Overview
This project is an End-to-End Machine Learning System for processing environmental data (Weather & Air Quality). It features:
- **Data Ingestion**: Automated ETL pipeline using **Prefect** to fetch data from Open-Meteo & OpenAQ.
- **Machine Learning**: 
    - Classification (AQI Risk)
    - Regression (Pollution PM2.5)
    - Clustering (City Segmentation)
- **Backend API**: **FastAPI** service for real-time inference and forecasting.
- **MLOps**: Dockerized deployment, CI/CD methodology, and automated testing.

## Project Structure
```
project-root/
├── app/                # FastAPI application
├── ml/                 # ML Training & Models
├── prefect_flows/      # Data Ingestion workflows
├── tests/              # Unit & Integration tests
├── docker/             # Docker configs
├── .github/workflows/  # CI/CD
└── requirements.txt    # Dependencies
```

## Setup & Running

### 1. Prerequisite
- Docker & Docker Compose
- Python 3.9+

### 2. Run with Docker (Recommended)
```bash
docker-compose up --build
```
The API will be available at: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

### 3. Run Locally
Install dependencies:
```bash
pip install -r requirements.txt
```

**Step A: Ingest Data**
Fetch historical data for training:
```bash
python prefect_flows/ingestion.py
```

**Step B: Train Models**
Train the ML models:
```bash
python ml/training/train_models.py
```

**Step C: Start API**
```bash
uvicorn app.main:app --reload
```

## API Endpoints
- `GET /weather/current?city=London`: Get real-time weather.
- `POST /predict/air-quality`: Predict AQI Risk category.
- `POST /predict/pollution`: Predict PM2.5 concentration.
- `POST /forecast/weather`: Get 3-day weather forecast.
- `POST /cluster/cities`: Assign a city to a climate cluster.

## Testing
Run automated tests:
```bash
pytest tests/
```
