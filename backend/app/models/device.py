# Sentinel-X Device Model

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class Device(Base):
    """Device model for ESP32 nodes and edge gateways."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    device_type = Column(String)
    name = Column(String)
    status = Column(String, default="offline")
    location = Column(String, nullable=True)
    capabilities = Column(JSON, default=dict)
    last_seen = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Device(id={self.id}, device_id={self.device_id}, type={self.device_type})>"