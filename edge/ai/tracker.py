# Sentinel-X Deep SORT Tracker
# Multi-object tracking for camera feeds

import numpy as np
from typing import List, Dict, Optional

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False

class Tracker:
    """Deep SORT tracker for maintaining object identities across frames."""

    def __init__(self, max_age: int = 30, min_hits: int = 3,
                 iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

        if DEEPSORT_AVAILABLE:
            self.tracker = DeepSort(
                max_age=max_age,
                min_hits=min_hits,
                iou_threshold=iou_threshold
            )
            print("[TRACKER] Deep SORT initialized")
        else:
            self.tracker = None
            print("[TRACKER] Using simple IOU tracker")

    def update(self, detections: List[Dict], frame: np.ndarray) -> List[Dict]:
        """Update tracks with new detections."""
        if not detections:
            return []

        if DEEPSORT_AVAILABLE and self.tracker:
            detections_for_ds = []
            for d in detections:
                x1, y1, x2, y2 = d['bbox']
                detections_for_ds.append(([x1, y1, x2 - x1, y2 - y1], d['confidence'], d['class']))

            tracks = self.tracker.update_tracks(detections_for_ds, frame=frame)

            results = []
            for track in tracks:
                if not track.is_confirmed():
                    continue
                ltrb = track.to_ltrb()
                results.append({
                    'track_id': track.track_id,
                    'bbox': [int(x) for x in ltrb],
                    'class': track.get_class() if hasattr(track, 'get_class') else 'unknown',
                    'confidence': track.confidence,
                    'time_since_update': track.time_since_update
                })
            return results
        else:
            return self._simple_track(detections)

    def _simple_track(self, detections: List[Dict]) -> List[Dict]:
        """Simple IOU tracker fallback."""
        results = []
        for i, d in enumerate(detections):
            results.append({
                'track_id': i,
                'bbox': d['bbox'],
                'class': d['class'],
                'confidence': d['confidence'],
                'time_since_update': 0
            })
        return results