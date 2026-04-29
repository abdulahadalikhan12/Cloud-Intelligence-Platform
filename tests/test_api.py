"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "platform" in data
    assert data["version"] == "2.0.0"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_system_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "models_loaded" in data
    assert "cities_count" in data


def test_cities_all():
    response = client.get("/api/v1/cities/all")
    assert response.status_code == 200
    cities = response.json()
    assert len(cities) > 50


def test_cities_search():
    response = client.get("/api/v1/cities/search?q=London")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert data["cities"][0]["name"] == "London"


def test_cities_search_fuzzy():
    response = client.get("/api/v1/cities/search?q=Londn")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0


def test_predict_cluster():
    response = client.post("/api/v1/predict/cluster", json={
        "temperature": 20, "humidity": 60, "rain": 1.0, "pm2_5": 15,
    })
    assert response.status_code == 200
    data = response.json()
    assert "cluster_id" in data
    assert "cluster_name" in data


def test_predict_aqi_risk():
    response = client.post("/api/v1/predict/aqi-risk", json={
        "temperature": 25, "humidity": 55, "rain": 0,
        "pressure": 1013, "wind_speed": 10, "month": 6, "hour": 14,
    })
    assert response.status_code == 200
    assert "aqi_category" in response.json()


def test_predict_pollution():
    response = client.post("/api/v1/predict/pollution", json={
        "temperature": 30, "humidity": 70, "rain": 0,
        "pressure": 1010, "wind_speed": 5, "month": 7, "hour": 12,
    })
    assert response.status_code == 200
    assert "predicted_pm25" in response.json()
