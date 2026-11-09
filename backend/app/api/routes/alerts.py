# Sentinel-X Alerts API

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.alert import Alert

router = APIRouter()

class AlertCreate(BaseModel):
    event_id: int
    alert_type: str
    severity: str
    message: str
    channels: List[str] = ["telegram"]

class AlertResponse(BaseModel):
    id: int
    event_id: int
    alert_type: str
    severity: str
    message: str
    status: str
    created_at: datetime

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db = Depends(get_db)):
    """Create a new alert."""
    db_alert = Alert(
        event_id=alert.event_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        status="pending"
    )
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db = Depends(get_db)
):
    """List alerts."""
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db = Depends(get_db)):
    """Acknowledge an alert."""
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "acknowledged"
    await db.commit()
    return {"message": "Alert acknowledged"}

@router.patch("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db = Depends(get_db)):
    """Resolve an alert."""
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "resolved"
    await db.commit()
    return {"message": "Alert resolved"}