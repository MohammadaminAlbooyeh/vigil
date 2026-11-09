# Sentinel-X Event Publisher
# Sends events to backend via HTTP

import requests
import json
import time
from typing import Dict, Callable

class EventPublisher:
    """Publishes edge events to the backend API."""

    def __init__(self, backend_url: str, api_key: str):
        self.backend_url = backend_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def publish(self, event: Dict) -> bool:
        """Publish an event to the backend."""
        try:
            response = self.session.post(
                f"{self.backend_url}/api/events",
                json=event,
                timeout=5
            )
            if response.status_code == 201:
                print(f"[PUBLISHED] Event {event.get('track_id')}")
                return True
            else:
                print(f"[PUBLISH FAILED] {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"[PUBLISH ERROR] {e}")
            return False

    def publish_batch(self, events: list) -> bool:
        """Publish multiple events in batch."""
        try:
            response = self.session.post(
                f"{self.backend_url}/api/events/batch",
                json={"events": events},
                timeout=10
            )
            return response.status_code == 201
        except Exception as e:
            print(f"[PUBLISH BATCH ERROR] {e}")
            return False