"""Tests for utils/database module."""

import pytest
import json
from pathlib import Path
from src.utils.database import PredictionLogger


class TestPredictionLogger:
    def test_init_creates_db_path(self, tmp_path):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        assert db_path.exists()

    def test_log_prediction(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(
            sample_features_dict,
            prediction=1,
            prediction_proba=(0.2, 0.8),
            model_version="v_test",
            request_source="test"
        )
        stats = logger.get_statistics()
        assert stats['total_predictions'] == 1

    def test_log_prediction_all_classes(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=0, prediction_proba=(0.9, 0.1))
        logger.log_prediction(sample_features_dict, prediction=1, prediction_proba=(0.3, 0.7))
        stats = logger.get_statistics()
        assert stats['total_predictions'] == 2
        assert stats['predictions_by_class'].get('<=50K', 0) == 1
        assert stats['predictions_by_class'].get('>50K', 0) == 1

    def test_get_predictions_returns_records(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=1, prediction_proba=(0.1, 0.9))
        predictions = logger.get_predictions()
        assert len(predictions) == 1
        assert predictions[0]['prediction'] == 1
        assert predictions[0]['prediction_label'] == '>50K'

    def test_get_predictions_empty(self, tmp_path):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        predictions = logger.get_predictions()
        assert predictions == []

    def test_get_predictions_with_model_version_filter(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=0, prediction_proba=(0.9, 0.1), model_version="v1")
        logger.log_prediction(sample_features_dict, prediction=1, prediction_proba=(0.2, 0.8), model_version="v2")
        v1_preds = logger.get_predictions(model_version="v1")
        assert len(v1_preds) == 1
        assert v1_preds[0]['model_version'] == "v1"

    def test_get_statistics_empty(self, tmp_path):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        stats = logger.get_statistics()
        assert stats['total_predictions'] == 0

    def test_export_predictions_csv(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=1, prediction_proba=(0.1, 0.9))
        export_path = tmp_path / "export.csv"
        logger.export_predictions(export_path)
        assert export_path.exists()
        content = export_path.read_text()
        assert 'prediction_label' in content
        assert '>50K' in content

    def test_get_model_performance(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=0, prediction_proba=(0.9, 0.1))
        logger.log_prediction(sample_features_dict, prediction=1, prediction_proba=(0.2, 0.8))
        perf = logger.get_model_performance()
        assert perf['total_predictions'] == 2
        assert perf['class_0_predictions'] == 1
        assert perf['class_1_predictions'] == 1

    def test_model_performance_with_version(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=0, prediction_proba=(0.9, 0.1), model_version="v1")
        perf = logger.get_model_performance(model_version="v1")
        assert perf['total_predictions'] == 1
        perf = logger.get_model_performance(model_version="nonexistent")
        assert perf['total_predictions'] == 0

    def test_get_statistics_avg_confidence(self, tmp_path, sample_features_dict):
        db_path = tmp_path / "test.db"
        logger = PredictionLogger(db_path)
        logger.log_prediction(sample_features_dict, prediction=0, prediction_proba=(0.8, 0.2))
        logger.log_prediction(sample_features_dict, prediction=1, prediction_proba=(0.3, 0.7))
        stats = logger.get_statistics()
        assert abs(stats['avg_confidence_0'] - 0.55) < 0.01
        assert abs(stats['avg_confidence_1'] - 0.45) < 0.01
