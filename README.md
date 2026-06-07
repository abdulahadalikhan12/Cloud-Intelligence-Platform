---
title: Cloud Intelligence Platform
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: true
license: mit
---

**Live site:** https://cloud-intelligence-platform.abdulahadalikhan12.workers.dev/

# 🌍 Cloud Intelligence Platform v2

**Agentic Cloud Intelligence Platform** with real-time weather, air quality monitoring, ML-powered predictions, and semantic search — built with FastAPI, FAISS, and a 3-agent pipeline.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│               Frontend (Lovable/Vercel)       │
│  Map View │ Dashboard │ AI Insights Panel     │
└────────────────────┬─────────────────────────┘
                     │ REST API
┌────────────────────┴─────────────────────────┐
│            FastAPI Backend (HF Spaces)        │
│                                               │
│  ┌─────────────┐ ┌──────────┐ ┌───────────┐  │
│  │  Ingestion   │→│ Analysis │→│ Recommend │  │
│  │   Agent      │ │  Agent   │ │   Agent   │  │
│  └──────┬──────┘ └────┬─────┘ └─────┬─────┘  │
│         │              │             │         │
│  ┌──────┴──────────────┴─────────────┴─────┐  │
│  │           Services Layer                 │  │
│  │  Weather │ AQ │ Geocoding │ ML │ Vector  │  │
│  └──────────────────────────────────────────┘  │
│                                               │
│  ┌──────────────────────────────────────────┐  │
│  │          Data Layer                       │  │
│  │  FAISS Index │ ML Models │ Cities DB      │  │
│  └──────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/weather/current/{city}` | Real-time weather |
| GET | `/api/v1/weather/forecast/{city}` | 7-day forecast |
| GET | `/api/v1/air-quality/current/{city}` | Current AQI & pollutants |
| GET | `/api/v1/air-quality/rankings` | Cleanest/most polluted cities |
| GET | `/api/v1/cities/search?q=...` | Fuzzy city search |
| POST | `/api/v1/predict/aqi-risk` | AQI risk classification |
| POST | `/api/v1/predict/pollution` | PM2.5 prediction |
| POST | `/api/v1/agents/analyze/{city}` | Full agent pipeline |
| POST | `/api/v1/agents/compare` | Multi-city comparison |
| POST | `/api/v1/agents/search` | Semantic search |

📖 Full Swagger docs at `/docs`

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload --port 7860

# Run tests
pip install -r requirements-dev.txt
pytest tests/ -v
```

## 🐳 Docker

```bash
docker build -t cloud-intelligence .
docker run -p 7860:7860 cloud-intelligence
```

## 🤖 ML Training (Optional)

Pre-trained models are included. To retrain with fresh data:

```bash
python -m app.ml.trainer
```

## 📦 Deployment

This project deploys to **Hugging Face Spaces** (Docker SDK) via GitHub Actions.

1. Create a Space: `abdulahadalikhan12/cloud-intelligence` with Docker SDK
2. Add `HF_TOKEN` to GitHub repo secrets
3. Push to `main` → auto-deploys

## 👤 Author

Abdul Ahad Ali Khan — [GitHub](https://github.com/abdulahadalikhan12)
