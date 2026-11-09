# Sentinel-X Anomaly Detector
# Detects unusual patterns in sensor data

import numpy as np
from typing import List, Dict, Optional
from collections import deque
import statistics
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detects anomalies in sensor data using statistical methods."""

    def __init__(self, window_size: int = 100, std_threshold: float = 3.0):
        self.window_size = window_size
        self.std_threshold = std_threshold
        self.sensor_buffers: Dict[str, deque] = {}

    def add_reading(self, sensor_type: str, value: float):
        """Add a sensor reading."""
        if sensor_type not in self.sensor_buffers:
            self.sensor_buffers[sensor_type] = deque(maxlen=self.window_size)
        self.sensor_buffers[sensor_type].append(value)

    def detect(self, sensor_type: str, value: float) -> Optional[Dict]:
        """Check if a value is anomalous."""
        if sensor_type not in self.sensor_buffers:
            self.add_reading(sensor_type, value)
            return None

        buffer = list(self.sensor_buffers[sensor_type])
        if len(buffer) < 10:
            self.add_reading(sensor_type, value)
            return None

        mean = statistics.mean(buffer)
        std = statistics.stdev(buffer) if len(buffer) > 1 else 0

        if std == 0:
            self.add_reading(sensor_type, value)
            return None

        z_score = (value - mean) / std

        if abs(z_score) > self.std_threshold:
            anomaly = {
                'sensor_type': sensor_type,
                'value': value,
                'mean': mean,
                'std': std,
                'z_score': z_score,
                'severity': 'high' if abs(z_score) > 5 else 'medium',
                'timestamp': __import__('time').time()
            }
            logger.warning(f"Anomaly detected: {anomaly}")
            self.add_reading(sensor_type, value)
            return anomaly

        self.add_reading(sensor_type, value)
        return None

    def get_statistics(self, sensor_type: str) -> Optional[Dict]:
        """Get statistics for a sensor."""
        if sensor_type not in self.sensor_buffers:
            return None
        buffer = list(self.sensor_buffers[sensor_type])
        if not buffer:
            return None
        return {
            'count': len(buffer),
            'mean': statistics.mean(buffer),
            'min': min(buffer),
            'max': max(buffer),
            'std': statistics.stdev(buffer) if len(buffer) > 1 else 0
        }