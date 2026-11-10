# Sentinel-X Edge AI Model Training Pipeline
# Trains an anomaly detection model on synthetic sensor data and persists it.

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import joblib
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_model.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
META_PATH = os.path.join(MODEL_DIR, "metadata.json")

FEATURES = ["temperature", "humidity", "motion"]


def generate_training_data(n_samples: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic normal + anomalous sensor readings."""
    rng = np.random.default_rng(42)

    # Normal cluster
    normal = rng.normal(loc=[22.0, 50.0, 0.1], scale=[2.0, 10.0, 0.3], size=(n_samples, 3))
    normal[:, 2] = np.clip(normal[:, 2], 0, 1)

    # Anomalous cluster
    anomaly = rng.normal(loc=[40.0, 10.0, 0.9], scale=[3.0, 5.0, 0.2], size=(n_samples // 4, 3))
    anomaly[:, 2] = np.clip(anomaly[:, 2], 0, 1)

    X = np.vstack([normal, anomaly]).astype(np.float32)
    y = np.array([0] * len(normal) + [1] * len(anomaly))
    return X, y


def train_model(X: np.ndarray) -> Tuple[object, object]:
    """Train an IsolationForest anomaly detector with a StandardScaler."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if HAS_SKLEARN:
        model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        model.fit(X_scaled)
        return model, scaler

    # Fallback: pure-numpy threshold detector
    class FallbackModel:
        def __init__(self, mean, std):
            self.mean = mean
            self.std = std

        def predict(self, X):
            z = np.abs((X - self.mean) / (self.std + 1e-6))
            return np.where(z.max(axis=1) > 3.0, -1, 1)

    model = FallbackModel(X_scaled.mean(axis=0), X_scaled.std(axis=0))
    return model, scaler


def evaluate(model, scaler, X: np.ndarray, y: np.ndarray) -> Dict:
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    # IsolationForest returns -1 for anomaly, 1 for normal; map to 1/0
    pred_labels = np.where(preds == -1, 1, 0)
    tp = int(((pred_labels == 1) & (y == 1)).sum())
    fp = int(((pred_labels == 1) & (y == 0)).sum())
    fn = int(((pred_labels == 0) & (y == 1)).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "support": int(len(y))}


def save_artifacts(model, scaler, metrics: Dict):
    os.makedirs(MODEL_DIR, exist_ok=True)
    if HAS_SKLEARN:
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
    else:
        import pickle
        with open(MODEL_PATH.replace(".joblib", ".pkl"), "wb") as f:
            pickle.dump({"model": model, "scaler": scaler}, f)

    metadata = {
        "trained_at": datetime.now().astimezone().isoformat(),
        "features": FEATURES,
        "algorithm": "IsolationForest" if HAS_SKLEARN else "FallbackThreshold",
        "metrics": metrics,
        "version": "1.0.0",
    }
    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[TRAIN] Model saved to {MODEL_PATH}")
    print(f"[TRAIN] Metadata saved to {META_PATH}")


def main():
    print("[TRAIN] Generating synthetic training data...")
    X, y = generate_training_data()
    print(f"[TRAIN] Samples: {len(X)} (anomalies: {int((y==1).sum())})")

    print("[TRAIN] Training model...")
    model, scaler = train_model(X)

    print("[TRAIN] Evaluating...")
    metrics = evaluate(model, scaler, X, y)
    print(f"[TRAIN] Metrics: {metrics}")

    save_artifacts(model, scaler, metrics)
    print("[TRAIN] Training complete.")


if __name__ == "__main__":
    main()
