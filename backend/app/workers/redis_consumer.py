# Sentinel-X Redis Consumer
# Consumes events from Redis Streams

import asyncio
import json
import logging
from typing import Dict, Callable
import redis.asyncio as redis

from app.core.config import settings
from app.services.rules_engine import RulesEngine
from app.services.event_correlator import EventCorrelator
from app.services.alert_service import AlertService
from app.services.media_service import MediaService

logger = logging.getLogger(__name__)

class RedisConsumer:
    """Consumes events from Redis Streams."""

    def __init__(self):
        self.redis = None
        self.rules_engine = RulesEngine()
        self.correlator = EventCorrelator()
        self.alert_service = AlertService()
        self.media_service = MediaService()
        self.running = False

    async def connect(self):
        """Connect to Redis."""
        self.redis = redis.from_url(settings.redis_url)
        logger.info("Connected to Redis")

    async def consume(self, stream_name: str = "sentinel:events",
                      group_name: str = "sentinel-consumers",
                      consumer_name: str = "consumer-1"):
        """Consume events from a Redis stream."""
        if not self.redis:
            await self.connect()

        # Create consumer group if it doesn't exist
        try:
            await self.redis.xgroup_create(stream_name, group_name, id="0", mkstream=True)
        except Exception:
            pass  # Group already exists

        self.running = True
        while self.running:
            try:
                # Read events from stream
                result = await self.redis.xreadgroup(
                    group_name, consumer_name,
                    {stream_name: ">"}, count=10, block=1000
                )

                if result:
                    for stream, messages in result:
                        for msg_id, data in messages:
                            await self._process_event(data)
                            # Acknowledge the message
                            await self.redis.xack(stream, group_name, msg_id)

            except Exception as e:
                logger.error(f"Redis consumer error: {e}")
                await asyncio.sleep(1)

    async def _process_event(self, event_data: Dict):
        """Process a single event."""
        try:
            event = json.loads(event_data.get('data', '{}'))
            logger.info(f"Processing event: {event}")

            # Evaluate rules
            matched_rules = self.rules_engine.evaluate(event)
            for rule in matched_rules:
                logger.info(f"Rule matched: {rule.name} -> {rule.action}")

                if rule.action == "alert":
                    await self.alert_service.send_alert(
                        alert_type=rule.name,
                        message=f"Rule triggered: {rule.name}",
                        severity=rule.params.get('severity', 'info'),
                        channels=rule.params.get('channels', ['telegram'])
                    )

            # Add to correlator
            self.correlator.add_event(event)
            incidents = self.correlator.correlate()

            for incident in incidents:
                logger.warning(f"Incident created: {incident['id']}")
                await self.alert_service.send_alert(
                    alert_type=incident['type'],
                    message=incident['description'],
                    severity=incident['severity'],
                    channels=['telegram', 'email']
                )

        except Exception as e:
            logger.error(f"Event processing error: {e}")

    async def stop(self):
        """Stop the consumer."""
        self.running = False
        if self.redis:
            await self.redis.close()

async def start_redis_consumer():
    """Start the Redis consumer as a background task."""
    consumer = RedisConsumer()
    await consumer.consume()