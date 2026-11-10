# Sentinel-X Event handler tests (direct invocation, no live DB)

import pytest
from app.api.routes.events import create_event, get_event, EventCreate


class FakeSession:
    def __init__(self, existing=None):
        self.added = None
        self.committed = False
        self.refreshed = None
        self.existing = existing

    def add(self, obj):
        self.added = obj
        obj.id = 1

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed = obj

    async def get(self, model, ident):
        return self.existing


@pytest.mark.asyncio
async def test_create_event_handler():
    db = FakeSession()
    payload = EventCreate(device_id="cam-01", event_type="motion_detected", severity="high")
    result = await create_event(payload, db)
    assert db.committed is True
    assert result.device_id == "cam-01"
    assert result.event_type == "motion_detected"
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_event_found():
    from app.models.event import Event
    ev = Event(id=5, device_id="cam-02", event_type="intrusion", severity="critical")
    db = FakeSession(existing=ev)
    result = await get_event(5, db)
    assert result is ev


@pytest.mark.asyncio
async def test_get_event_not_found():
    db = FakeSession(existing=None)
    from fastapi import HTTPException
    try:
        await get_event(999, db)
        assert False
    except HTTPException as exc:
        assert exc.status_code == 404
