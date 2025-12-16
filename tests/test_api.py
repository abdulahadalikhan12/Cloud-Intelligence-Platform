from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active", "service": "Climate Intelligence Platform Code"}

@patch("app.routers.weather.openmeteo.weather_api")
def test_get_current_weather(mock_weather_api):
    # Mocking the OpenMeteo response object hierarchy is complex, 
    # so we might mock the 'get_current_weather' function directly if we want Unit Test
    # Or just test 404 for invalid city
    
    response = client.get("/weather/current?city=InvalidCity")
    assert response.status_code == 404

@patch("app.routers.predict.load_model")
def test_predict_pollution(mock_load_model):
    # Mock the model and scaler
    mock_model = MagicMock()
    mock_model.predict.return_value = [15.5]
    
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[0, 0, 0, 0, 0, 0, 0]]
    
    # load_model maps filename to object. We can use side_effect or just return a mock that works for both
    # Simpler: side_effect based on name
    def side_effect(name):
        if "scaler" in name: return mock_scaler
        if "label_encoder" in name: 
            enc = MagicMock()
            enc.inverse_transform.return_value = ["Good"]
            return enc
        return mock_model
        
    mock_load_model.side_effect = side_effect

    payload = {
        "temperature": 25.0,
        "humidity": 50.0,
        "rain": 0.0,
        "pressure": 1013.0,
        "wind_speed": 10.0,
        "month": 6,
        "hour": 12
    }
    
    response = client.post("/predict/pollution", json=payload)
    assert response.status_code == 200
    assert "predicted_pm25" in response.json()
    assert response.json()["predicted_pm25"] == 15.5
