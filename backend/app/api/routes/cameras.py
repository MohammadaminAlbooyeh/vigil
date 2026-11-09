# Sentinel-X Cameras API

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()

class CameraCreate(BaseModel):
    name: str
    location: str
    ip_address: Optional[str] = None
    port: Optional[int] = 554
    username: Optional[str] = None
    password: Optional[str] = None

class CameraResponse(BaseModel):
    id: int
    name: str
    location: str
    status: str
    ip_address: Optional[str] = None
    is_streaming: bool = False

@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(camera: CameraCreate, db = Depends(get_db)):
    """Register a new camera."""
    return {"id": 1, **camera.dict(), "status": "offline", "is_streaming": False}

@router.get("/", response_model=List[CameraResponse])
async def list_cameras(db = Depends(get_db)):
    """List all cameras."""
    return []

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: int, db = Depends(get_db)):
    """Get a specific camera."""
    raise HTTPException(status_code=404, detail="Camera not found")

@router.post("/{camera_id}/start_stream")
async def start_stream(camera_id: int):
    """Start camera streaming."""
    return {"message": f"Camera {camera_id} stream started"}

@router.post("/{camera_id}/stop_stream")
async def stop_stream(camera_id: int):
    """Stop camera streaming."""
    return {"message": f"Camera {camera_id} stream stopped"}