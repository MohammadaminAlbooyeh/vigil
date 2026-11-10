# Sentinel-X Anomaly Detector Tests

import pytest
from app.services.anomaly_detector import AnomalyDetector


@pytest.fixture
def detector():
    return AnomalyDetector(window_size=50, std_threshold=3.0)


def test_normal_reading_returns_none(detector):
    # Fill buffer with stable values, then a normal reading
    for i in range(20):
        detector.add_reading("temp", 20.0 + i * 0.1)
    result = detector.detect("temp", 20.5)
    assert result is None


def test_anomalous_reading_detected(detector):
    import statistics
    for i in range(20):
        detector.add_reading("temp", 20.0 + (i % 3) * 0.5)
    result = detector.detect("temp", 100.0)
    assert result is not None
    assert result["sensor_type"] == "temp"
    assert result["value"] == 100.0
    assert result["severity"] == "high"
    assert "z_score" in result


def test_insufficient_buffer_returns_none(detector):
    result = detector.detect("temp", 50.0)
    assert result is None


def test_zero_std_returns_none(detector):
    for i in range(20):
        detector.add_reading("temp", 20.0)
    result = detector.detect("temp", 20.0)
    assert result is None


def test_get_statistics(detector):
    for v in [10.0, 20.0, 30.0]:
        detector.add_reading("hum", v)
    stats = detector.get_statistics("hum")
    assert stats is not None
    assert stats["count"] == 3
    assert stats["mean"] == 20.0
    assert stats["min"] == 10.0
    assert stats["max"] == 30.0


def test_get_statistics_empty(detector):
    assert detector.get_statistics("missing") is None


def test_severity_medium_threshold(detector):
    import statistics
    for i in range(20):
        detector.add_reading("temp", 20.0 + (i % 3) * 0.5)
    buf = list(detector.sensor_buffers["temp"])
    mean = statistics.mean(buf)
    std = statistics.stdev(buf)
    target = mean + 4 * std  # z_score == 4 -> medium
    result = detector.detect("temp", target)
    assert result is not None
    assert result["severity"] == "medium"
