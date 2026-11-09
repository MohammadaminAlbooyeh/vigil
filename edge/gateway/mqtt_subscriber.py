# Sentinel-X MQTT Subscriber
# Receives events from ESP32 sensor nodes

import paho.mqtt.client as mqtt
import json
import time
from typing import Callable, Dict

class MQTTSubscriber:
    """MQTT client for subscribing to ESP32 sensor events."""

    def __init__(self, broker: str, port: int, username: str, password: str,
                 topic: str = "sentinel/events/+"):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self.handlers: Dict[str, Callable] = {}
        self.connected = False

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.connected = True
            print(f"[MQTT] Connected to {self.broker}")
            client.subscribe(self.topic)
            print(f"[MQTT] Subscribed to {self.topic}")
        else:
            print(f"[MQTT] Connection failed: {reason_code}")

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            topic = message.topic

            for pattern, handler in self.handlers.items():
                if pattern in topic or pattern == topic:
                    handler(topic, payload)

            if '+' in self.topic:
                device_type = topic.split('/')[-1]
                print(f"[MQTT] Event from {device_type}: {payload}")
        except Exception as e:
            print(f"[MQTT] Message error: {e}")

    def register_handler(self, pattern: str, handler: Callable):
        """Register a handler for a topic pattern."""
        self.handlers[pattern] = handler

    def connect(self):
        """Connect to MQTT broker."""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")

    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False