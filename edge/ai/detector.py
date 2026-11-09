# Sentinel-X Edge AI Detector
# YOLOv8 inference on Raspberry Pi 5 with Hailo-8 accelerator

import cv2
import numpy as np
import time
from typing import List, Dict, Tuple, Optional

try:
    from hailo_platform import HailoAsyncInference
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False

class Detector:
    """YOLOv8 object detector with Hailo-8 acceleration."""

    def __init__(self, model_path: str = "models/yolov8n.pt",
                 confidence_threshold: float = 0.5,
                 iou_threshold: float = 0.45,
                 use_hailo: bool = True):
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.use_hailo = use_hailo and HAILO_AVAILABLE

        if self.use_hailo:
            self.hailo = HailoAsyncInference(model_path)
            print("[DETECTOR] Hailo-8 accelerator initialized")
        else:
            self.model = cv2.dnn.readNet(model_path)
            print("[DETECTOR] OpenCV DNN fallback")

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for YOLOv8."""
        blob = cv2.dnn.blobFromImage(
            frame, 1/255.0, (640, 640), swapRB=True, crop=False
        )
        return blob

    def postprocess(self, outputs: np.ndarray, frame_shape: Tuple[int, int]) -> List[Dict]:
        """Convert raw outputs to detection list."""
        detections = []
        return detections

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """Run detection on a frame."""
        if self.use_hailo:
            detections = self.hailo.run(frame)
        else:
            blob = self.preprocess(frame)
            self.model.setInput(blob)
            outputs = self.model.forward()
            detections = self.postprocess(outputs, frame.shape[:2])

        detections = [d for d in detections if d['confidence'] >= self.confidence_threshold]
        return detections

    def draw(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes on frame."""
        for d in detections:
            x1, y1, x2, y2 = d['bbox']
            label = d['class']
            conf = d['confidence']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame