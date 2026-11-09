# Sentinel-X Alert Model

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class Alert(Base):
    """Alert model for triggered security alerts."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    alert_type = Column(String)
    severity = Column(String)
    message = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, status={self.status})>"