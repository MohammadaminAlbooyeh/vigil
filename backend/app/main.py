# Sentinel-X Backend Main
# FastAPI application entry point

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import events, devices, cameras, alerts
from app.api.websocket import websocket_endpoint
from app.workers.redis_consumer import start_redis_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Sentinel-X Backend starting...")
    # Start Redis consumer in background
    import asyncio
    redis_task = asyncio.create_task(start_redis_consumer())
    yield
    logger.info("Sentinel-X Backend shutting down...")
    redis_task.cancel()

app = FastAPI(
    title="Sentinel-X API",
    description="Distributed Edge AI Surveillance Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

# WebSocket
app.add_api_websocket_route("/ws/live", websocket_endpoint)

@app.get("/")
async def root():
    return {"name": "Sentinel-X", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}