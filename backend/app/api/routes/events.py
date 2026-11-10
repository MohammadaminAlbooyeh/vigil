# Sentinel-X Events API

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.core.database import get_db
from app.models.event import Event

router = APIRouter()

class EventCreate(BaseModel):
    device_id: str
    event_type: str
    severity: str = "info"
    metadata: Optional[dict] = None

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    event_type: str
    severity: str
    timestamp: datetime
    event_metadata: Optional[dict] = None

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db = Depends(get_db)):
    """Create a new event."""
    db_event = Event(
        device_id=event.device_id,
        event_type=event.event_type,
        severity=event.severity,
        event_metadata=event.metadata
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventResponse])
async def list_events(
    skip: int = 0,
    limit: int = 100,
    device_id: Optional[str] = None,
    event_type: Optional[str] = None,
    db = Depends(get_db)
):
    """List events with optional filtering."""
    query = db.query(Event)
    if device_id:
        query = query.filter(Event.device_id == device_id)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    query = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db = Depends(get_db)):
    """Get a specific event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event