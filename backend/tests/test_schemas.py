# Sentinel-X API Schema & Handler Tests

from datetime import datetime
from pydantic import ValidationError
from app.api.routes.events import EventCreate, EventResponse
from app.models.event import Event


def test_event_create_valid():
    e = EventCreate(device_id="cam-01", event_type="motion_detected", severity="high", metadata={"x": 1})
    assert e.device_id == "cam-01"
    assert e.severity == "high"


def test_event_create_defaults():
    e = EventCreate(device_id="cam-01", event_type="motion_detected")
    assert e.severity == "info"
    assert e.metadata is None


def test_event_create_missing_required():
    try:
        EventCreate(event_type="motion_detected")
        assert False, "should have raised"
    except ValidationError:
        pass


def test_event_response_from_model():
    ev = Event(id=1, device_id="cam-01", event_type="motion_detected", severity="info")
    ev.timestamp = datetime.utcnow()
    resp = EventResponse.model_validate(ev)
    assert resp.id == 1
    assert resp.device_id == "cam-01"
    assert resp.event_metadata is None
