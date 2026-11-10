# Sentinel-X

Distributed Edge AI Surveillance Platform — ESP32 camera/sensor/actuator nodes, FastAPI backend, Redis event bus, and a React dashboard.

## Structure

```
backend/        FastAPI API, websocket, Redis consumer, anomaly detection, rules engine
dashboard/      React + Chakra UI dashboard (Vite)
edge/           Edge AI detector, tracker, pipeline + model training
firmware/       ESP32-CAM / ESP32-S3 / ESP32 Actuator Arduino firmware
infrastructure/ Docker, Grafana, Prometheus, Kubernetes manifests
scripts/        Tooling
```

## Getting Started

### 1. Backend

```bash
cp .env.example .env
# edit .env with your credentials
cd backend
pip install -r requirements.txt
python -m app.main   # or: uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`; websocket at `ws://localhost:8000/ws/live`.

### 2. Dashboard

```bash
cd dashboard
npm install
npm run dev          # http://localhost:5173
npm run build        # typecheck + production build
```

### 3. Edge AI (model training)

```bash
pip install -r edge/requirements.txt
python edge/ai/train.py   # trains + saves models/anomaly_model.joblib
```

### 4. Infrastructure

See `infrastructure/` for mosquitto, redis, postgres, minio, Grafana, Prometheus, and k8s manifests.

> Note: `docker-compose` historically referenced a hardcoded plaintext password; use `.env.example` and inject secrets via your orchestrator instead.

## Testing

```bash
cd backend
pip install pytest pytest-asyncio httpx
python -m pytest tests -v
```

## CI

GitHub Actions workflow in `.github/workflows/ci.yml` runs backend tests, dashboard typecheck/lint, and the AI training pipeline on every push/PR to `main`.
