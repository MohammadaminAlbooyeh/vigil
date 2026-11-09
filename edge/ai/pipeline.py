# Sentinel-X Edge AI Pipeline
# Detection → Tracking → Event correlation

import cv2
import time
import json
from typing import List, Dict, Optional

from detector import Detector
from tracker import Tracker

class Pipeline:
    """Main edge AI pipeline: detect → track → emit events."""

    def __init__(self, config: dict):
        self.config = config
        self.detector = Detector(
            model_path=config.get('model_path', 'models/yolov8n.pt'),
            confidence_threshold=config.get('confidence_threshold', 0.5),
            use_hailo=config.get('use_hailo', True)
        )
        self.tracker = Tracker(
            max_age=config.get('max_age', 30),
            min_hits=config.get('min_hits', 3)
        )
        self.event_callbacks = []
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()

    def register_callback(self, callback):
        """Register event callback."""
        self.event_callbacks.append(callback)

    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame through detection and tracking."""
        self.frame_count += 1

        detections = self.detector.detect(frame)
        tracks = self.tracker.update(detections, frame)

        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time

        result = {
            'timestamp': time.time(),
            'fps': self.fps,
            'detections': detections,
            'tracks': tracks,
            'annotated_frame': self.detector.draw(frame.copy(), detections)
        }

        for track in tracks:
            self._emit_event(track)

        return result

    def _emit_event(self, track: Dict):
        """Emit event for a tracked object."""
        event = {
            'type': 'detection',
            'track_id': track['track_id'],
            'class': track['class'],
            'confidence': track['confidence'],
            'bbox': track['bbox'],
            'timestamp': time.time()
        }

        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[PIPELINE] Callback error: {e}")

    def run(self, camera_source=0):
        """Run pipeline on camera feed."""
        cap = cv2.VideoCapture(camera_source)
        if not cap.isOpened():
            print(f"[PIPELINE] Cannot open camera {camera_source}")
            return

        print("[PIPELINE] Starting edge AI pipeline...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result = self.process_frame(frame)
            cv2.imshow("Sentinel-X", result['annotated_frame'])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()