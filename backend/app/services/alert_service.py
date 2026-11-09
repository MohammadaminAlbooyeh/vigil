# Sentinel-X Alert Service
# Sends alerts via Telegram, Email, and other channels

import asyncio
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class AlertService:
    """Service for sending alerts through various channels."""

    def __init__(self):
        self.telegram_token = settings.telegram_bot_token
        self.telegram_chat_id = settings.telegram_chat_id

    async def send_telegram(self, message: str, severity: str = "info") -> bool:
        """Send alert via Telegram."""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured")
            return False

        emoji = {"critical": "🚨", "high": "⚠️", "medium": "ℹ️", "low": "📝"}.get(severity, "ℹ️")
        text = f"{emoji} *Sentinel-X Alert*\n\n{message}\n\nSeverity: {severity.upper()}"

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            response = requests.post(url, json={
                "chat_id": self.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False

    async def send_email(self, subject: str, body: str, to: str = None) -> bool:
        """Send alert via email."""
        # Placeholder for email implementation
        logger.info(f"Email alert: {subject}")
        return True

    async def send_siren(self, device_id: str) -> bool:
        """Trigger physical siren via MQTT."""
        # This would publish to MQTT topic
        logger.info(f"Siren triggered for {device_id}")
        return True

    async def send_alert(self, alert_type: str, message: str, severity: str = "info",
                         channels: List[str] = None) -> Dict[str, bool]:
        """Send alert through multiple channels."""
        channels = channels or ["telegram"]
        results = {}

        for channel in channels:
            if channel == "telegram":
                results["telegram"] = await self.send_telegram(message, severity)
            elif channel == "email":
                results["email"] = await self.send_email(alert_type, message)
            elif channel == "siren":
                results["siren"] = await self.send_siren("actuator")
            else:
                logger.warning(f"Unknown channel: {channel}")

        return results