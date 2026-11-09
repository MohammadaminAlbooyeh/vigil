# Sentinel-X Event Correlator
# Combines multiple events into meaningful incidents

import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class EventCorrelator:
    """Correlates related events into incidents."""

    def __init__(self, time_window_seconds: int = 300):
        self.time_window = time_window_seconds
        self.event_buffer: List[Dict] = []
        self.incidents: List[Dict] = []

    def add_event(self, event: Dict):
        """Add an event to the buffer."""
        self.event_buffer.append(event)
        self._cleanup_old_events()

    def _cleanup_old_events(self):
        """Remove events older than the time window."""
        current_time = time.time()
        self.event_buffer = [
            e for e in self.event_buffer
            if current_time - e.get('timestamp', current_time) < self.time_window
        ]

    def correlate(self) -> List[Dict]:
        """Find correlated events and create incidents."""
        incidents = []

        # Group events by device_id and location
        groups = defaultdict(list)
        for event in self.event_buffer:
            key = (event.get('device_id'), event.get('location', 'unknown'))
            groups[key].append(event)

        for key, events in groups.items():
            device_id, location = key

            # Check for motion + detection correlation
            motion_events = [e for e in events if e.get('event_type') == 'motion']
            detection_events = [e for e in events if e.get('event_type') == 'detection']

            if motion_events and detection_events:
                incident = {
                    'id': f"inc_{int(time.time())}",
                    'type': 'motion_with_detection',
                    'device_id': device_id,
                    'location': location,
                    'timestamp': time.time(),
                    'events': motion_events + detection_events,
                    'severity': 'high',
                    'description': f"Motion detected followed by object detection at {location}"
                }
                incidents.append(incident)
                self.incidents.append(incident)

            # Check for rapid motion events (potential break-in)
            if len(motion_events) >= 3:
                time_span = motion_events[-1].get('timestamp', 0) - motion_events[0].get('timestamp', 0)
                if time_span < 60:  # 3+ motions in 60 seconds
                    incident = {
                        'id': f"inc_{int(time.time())}_rapid",
                        'type': 'rapid_motion',
                        'device_id': device_id,
                        'location': location,
                        'timestamp': time.time(),
                        'events': motion_events,
                        'severity': 'critical',
                        'description': f"Rapid motion detected ({len(motion_events)} events in {time_span}s)"
                    }
                    incidents.append(incident)
                    self.incidents.append(incident)

        return incidents

    def get_active_incidents(self) -> List[Dict]:
        """Get all active (unresolved) incidents."""
        return [i for i in self.incidents if i.get('status', 'active') == 'active']

    def resolve_incident(self, incident_id: str):
        """Mark an incident as resolved."""
        for incident in self.incidents:
            if incident['id'] == incident_id:
                incident['status'] = 'resolved'
                incident['resolved_at'] = time.time()
                break