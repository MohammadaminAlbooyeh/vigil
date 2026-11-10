# Sentinel-X Alert Service Tests

import pytest
from unittest.mock import patch, AsyncMock
from app.services.alert_service import AlertService


@pytest.fixture
def service():
    return AlertService()


@pytest.mark.asyncio
async def test_send_telegram_not_configured(service, caplog):
    service.telegram_token = None
    service.telegram_chat_id = None
    result = await service.send_telegram("hi", "info")
    assert result is False


@pytest.mark.asyncio
async def test_send_telegram_success(service):
    service.telegram_token = "token"
    service.telegram_chat_id = "chat"
    with patch.object(service, "requests") if False else patch("app.services.alert_service.requests.post") as m:
        m.return_value.status_code = 200
        result = await service.send_telegram("hi", "high")
        assert result is True


@pytest.mark.asyncio
async def test_send_email(service):
    result = await service.send_email("subj", "body")
    assert result is True


@pytest.mark.asyncio
async def test_send_siren(service):
    result = await service.send_siren("actuator-1")
    assert result is True


@pytest.mark.asyncio
async def test_send_alert_unknown_channel(service):
    results = await service.send_alert("test", "msg", channels=["bogus"])
    assert results == {}
