# Sentinel-X Camera Manager
# Manages multiple camera feeds on Raspberry Pi

import cv2
import threading
import time
from typing import Dict, List, Callable, Optional

from pipeline import Pipeline

class CameraManager:
    """Manages multiple camera feeds and their AI pipelines."""

    def __init__(self, config: dict):
        self.config = config
        self.cameras: Dict[str, Pipeline] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.running = False

    def add_camera(self, camera_id: str, source: int, config_overrides: dict = None):
        """Add a new camera feed."""
        camera_config = {
            'model_path': self.config.get('ai', {}).get('model_path', 'models/yolov8n.pt'),
            'confidence_threshold': self.config.get('ai', {}).get('confidence_threshold', 0.5),
            'use_hailo': self.config.get('ai', {}).get('use_hailo', True),
            **(config_overrides or {})
        }

        pipeline = Pipeline(camera_config)
        self.cameras[camera_id] = pipeline
        print(f"[CAMERA] Added {camera_id} (source={source})")

    def register_callback(self, camera_id: str, callback: Callable):
        """Register an event callback for a specific camera."""
        if camera_id in self.cameras:
            self.cameras[camera_id].register_callback(callback)

    def _run_camera(self, camera_id: str, source: int):
        """Run a single camera pipeline."""
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"[CAMERA] Cannot open {camera_id} (source={source})")
            return

        pipeline = self.cameras[camera_id]
        print(f"[CAMERA] Starting {camera_id}")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            result = pipeline.process_frame(frame)

            # Display (optional)
            if self.config.get('display', True):
                cv2.imshow(f"Sentinel-X - {camera_id}", result['annotated_frame'])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def start(self):
        """Start all camera pipelines."""
        self.running = True
        for camera_id, pipeline in self.cameras.items():
            source = self.config.get('cameras', {}).get(camera_id, {}).get('source', 0)
            thread = threading.Thread(
                target=self._run_camera,
                args=(camera_id, source),
                daemon=True
            )
            thread.start()
            self.threads[camera_id] = thread
            print(f"[CAMERA] Thread started for {camera_id}")

    def stop(self):
        """Stop all camera pipelines."""
        self.running = False
        for thread in self.threads.values():
            thread.join(timeout=2)
        print("[CAMERA] All cameras stopped")