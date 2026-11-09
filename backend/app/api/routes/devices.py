# Sentinel-X Devices API

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.device import Device

router = APIRouter()

class DeviceCreate(BaseModel):
    device_id: str
    device_type: str
    name: str
    location: Optional[str] = None
    capabilities: Optional[dict] = None

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    device_type: str
    name: str
    status: str
    location: Optional[str] = None
    last_seen: Optional[str] = None

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate, db = Depends(get_db)):
    """Register a new device."""
    db_device = Device(
        device_id=device.device_id,
        device_type=device.device_type,
        name=device.name,
        location=device.location,
        capabilities=device.capabilities or {}
    )
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device

@router.get("/", response_model=List[DeviceResponse])
async def list_devices(db = Depends(get_db)):
    """List all registered devices."""
    result = await db.execute(db.query(Device))
    return result.scalars().all()

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db = Depends(get_db)):
    """Get a specific device."""
    result = await db.execute(db.query(Device).filter(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: str, db = Depends(get_db)):
    """Delete a device."""
    result = await db.execute(db.query(Device).filter(Device.device_id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await db.delete(device)
    await db.commit()