# Sentinel-X Event Model

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class Event(Base):
    """Event model for sensor and detection events."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    event_type = Column(String, index=True)
    severity = Column(String, default="info")
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Event(id={self.id}, device={self.device_id}, type={self.event_type})>"