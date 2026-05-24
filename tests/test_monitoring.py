"""Tests for utils/monitoring module."""

import pytest
import numpy as np
import pandas as pd
from src.utils.monitoring import DriftDetector, ModelMonitor


class TestDriftDetector:
    @pytest.fixture
    def sample_reference_data(self):
        return pd.DataFrame(
            {
                "age": [25, 35, 45, 55, 30, 40, 50],
                "workclass": [
                    "Private",
                    "Self-emp-inc",
                    "Private",
                    "Federal-gov",
                    "Private",
                    "Local-gov",
                    "Private",
                ],
                "income": [0, 1, 0, 1, 0, 1, 0],
            }
        )

    def test_init_calculates_stats(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        assert "age" in detector.reference_stats
        assert detector.reference_stats["age"]["type"] == "numeric"
        assert "workclass" in detector.reference_stats
        assert detector.reference_stats["workclass"]["type"] == "categorical"

    def test_detect_numeric_drift_no_drift(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current = pd.Series([28, 38, 48, 52, 32, 42, 48])
        drifted, p_val, desc = detector.detect_numeric_drift("age", current)
        assert p_val > 0.05

    def test_detect_numeric_drift_unknown_feature(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current = pd.Series([1, 2, 3])
        drifted, p_val, desc = detector.detect_numeric_drift("missing", current)
        assert drifted is False
        assert p_val == 1.0

    def test_detect_categorical_drift_no_drift(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current = pd.Series(
            ["Private", "Private", "Self-emp-inc", "Federal-gov", "Private", "Local-gov", "Private"]
        )
        drifted, p_val, desc = detector.detect_categorical_drift("workclass", current)
        assert p_val >= 0  # Should not error

    def test_detect_categorical_drift_unknown_feature(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current = pd.Series(["a", "b", "c"])
        drifted, p_val, desc = detector.detect_categorical_drift("missing", current)
        assert drifted is False
        assert p_val == 1.0

    def test_detect_drift_all_features(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current_data = pd.DataFrame(
            {
                "age": [28, 38, 48, 52, 32, 42, 48],
                "workclass": [
                    "Private",
                    "Private",
                    "Self-emp-inc",
                    "Federal-gov",
                    "Private",
                    "Local-gov",
                    "Private",
                ],
            }
        )
        results = detector.detect_drift(current_data)
        assert results["total_features"] == 2
        assert "age" in results["features"]
        assert "workclass" in results["features"]
        assert 0 <= results["drift_ratio"] <= 1

    def test_detect_drift_missing_feature_in_current(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current_data = pd.DataFrame({"age": [28, 38, 48]})
        results = detector.detect_drift(current_data)
        assert results["total_features"] == 1  # only age, workclass is missing

    def test_detect_drift_empty_current_data(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current_data = pd.DataFrame({"age": pd.Series(dtype="int64")})
        results = detector.detect_drift(current_data)
        assert results["total_features"] == 1

    def test_detect_categorical_drift_insufficient_data(self, sample_reference_data):
        detector = DriftDetector(sample_reference_data)
        current = pd.Series(["Private"])
        drifted, p_val, desc = detector.detect_categorical_drift("workclass", current)
        # Should handle gracefully
        assert isinstance(drifted, bool)


class TestModelMonitor:
    @pytest.fixture
    def monitor(self):
        return ModelMonitor()

    def test_empty_initial_state(self, monitor):
        assert monitor.prediction_history == []
        assert monitor.performance_history == []

    def test_log_prediction_batch(self, monitor):
        predictions = np.array([0, 1, 0, 1])
        probabilities = np.array([[0.9, 0.1], [0.2, 0.8], [0.85, 0.15], [0.3, 0.7]])
        monitor.log_prediction_batch(predictions, probabilities)
        assert len(monitor.prediction_history) == 4

    def test_get_confidence_stats(self, monitor):
        predictions = np.array([0, 1])
        probabilities = np.array([[0.9, 0.1], [0.2, 0.8]])
        monitor.log_prediction_batch(predictions, probabilities)
        stats = monitor.get_confidence_stats()
        assert abs(stats["mean_confidence"] - 0.85) < 0.01
        assert abs(stats["max_confidence"] - 0.9) < 0.01

    def test_confidence_stats_empty(self, monitor):
        stats = monitor.get_confidence_stats()
        assert stats == {}

    def test_get_prediction_distribution(self, monitor):
        predictions = np.array([0, 0, 1, 0, 1])
        probabilities = np.array([[0.9, 0.1], [0.85, 0.15], [0.2, 0.8], [0.95, 0.05], [0.3, 0.7]])
        monitor.log_prediction_batch(predictions, probabilities)
        dist = monitor.get_prediction_distribution()
        assert dist["class_0_count"] == 3
        assert dist["class_1_count"] == 2
        assert abs(dist["class_0_percentage"] - 60.0) < 0.01

    def test_prediction_distribution_empty(self, monitor):
        dist = monitor.get_prediction_distribution()
        assert dist == {}

    def test_print_monitoring_report_runs(self, monitor, capsys):
        predictions = np.array([0, 1])
        probabilities = np.array([[0.9, 0.1], [0.2, 0.8]])
        monitor.log_prediction_batch(predictions, probabilities)
        monitor.print_monitoring_report()
        captured = capsys.readouterr()
        assert "MODEL MONITORING REPORT" in captured.out
        assert "Confidence Statistics" in captured.out
