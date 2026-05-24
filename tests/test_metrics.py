"""Tests for utils/metrics module."""

import pytest
import json
import numpy as np
from pathlib import Path
from src.utils.metrics import ModelEvaluator, MetricsReporter


class TestModelEvaluator:
    def test_evaluate_returns_all_metrics(self, sample_preprocessed_data):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline

        df = sample_preprocessed_data
        X = df.drop('income', axis=1)
        y = df['income']

        X = X.select_dtypes(include=[np.number])
        model = Pipeline([
            ('classifier', RandomForestClassifier(random_state=42, n_estimators=10))
        ])
        model.fit(X, y)

        evaluator = ModelEvaluator(model, X, y)
        metrics = evaluator.evaluate()

        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 'roc_auc' in metrics
        assert 'confusion_matrix' in metrics

    def test_metrics_are_float_values(self, sample_preprocessed_data):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline

        df = sample_preprocessed_data
        X = df.select_dtypes(include=[np.number]).drop('income', axis=1)
        y = df['income']

        model = Pipeline([
            ('classifier', RandomForestClassifier(random_state=42, n_estimators=10))
        ])
        model.fit(X, y)

        evaluator = ModelEvaluator(model, X, y)
        metrics = evaluator.evaluate()

        assert isinstance(metrics['accuracy'], float)
        assert 0 <= metrics['accuracy'] <= 1

    def test_confusion_matrix_elements(self, sample_preprocessed_data):
        from sklearn.ensemble import RandomForestClassifier

        df = sample_preprocessed_data
        X = df.select_dtypes(include=[np.number]).drop('income', axis=1)
        y = df['income']

        model = RandomForestClassifier(random_state=42, n_estimators=10)
        model.fit(X, y)

        evaluator = ModelEvaluator(model, X, y)
        metrics = evaluator.evaluate()

        cm = metrics['confusion_matrix']
        assert len(cm) == 2
        assert len(cm[0]) == 2
        assert 'true_negatives' in metrics
        assert 'false_positives' in metrics
        assert 'false_negatives' in metrics
        assert 'true_positives' in metrics

    def test_save_metrics_creates_file(self, tmp_path, sample_preprocessed_data):
        from sklearn.ensemble import RandomForestClassifier

        df = sample_preprocessed_data
        X = df.select_dtypes(include=[np.number]).drop('income', axis=1)
        y = df['income']

        model = RandomForestClassifier(random_state=42, n_estimators=10)
        model.fit(X, y)

        output_path = tmp_path / "metrics.json"
        evaluator = ModelEvaluator(model, X, y)
        evaluator.evaluate()
        evaluator.save_metrics(output_path)

        assert output_path.exists()
        with open(output_path) as f:
            saved = json.load(f)
        assert 'accuracy' in saved

    def test_classification_report_string(self, sample_preprocessed_data):
        from sklearn.ensemble import RandomForestClassifier

        df = sample_preprocessed_data
        X = df.select_dtypes(include=[np.number]).drop('income', axis=1)
        y = df['income']

        model = RandomForestClassifier(random_state=42, n_estimators=10)
        model.fit(X, y)

        evaluator = ModelEvaluator(model, X, y)
        evaluator.evaluate()
        report = evaluator.get_classification_report()
        assert '<=50K' in report
        assert '>50K' in report

    def test_print_summary_runs(self, sample_preprocessed_data, capsys):
        from sklearn.ensemble import RandomForestClassifier

        df = sample_preprocessed_data
        X = df.select_dtypes(include=[np.number]).drop('income', axis=1)
        y = df['income']

        model = RandomForestClassifier(random_state=42, n_estimators=10)
        model.fit(X, y)

        evaluator = ModelEvaluator(model, X, y)
        evaluator.evaluate()
        evaluator.print_summary()
        captured = capsys.readouterr()
        assert 'MODEL EVALUATION SUMMARY' in captured.out


class TestMetricsReporter:
    def test_load_metrics_nonexistent(self, tmp_path):
        result = MetricsReporter.load_metrics(tmp_path / "nonexistent.json")
        assert result == {}

    def test_load_metrics_valid_file(self, tmp_path):
        metrics_path = tmp_path / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump({'accuracy': 0.85, 'precision': 0.80}, f)
        result = MetricsReporter.load_metrics(metrics_path)
        assert result['accuracy'] == 0.85

    def test_compare_metrics_improvement(self):
        current = {'accuracy': 0.90, 'precision': 0.85, 'recall': 0.80, 'f1_score': 0.82, 'roc_auc': 0.92}
        previous = {'accuracy': 0.85, 'precision': 0.80, 'recall': 0.75, 'f1_score': 0.77, 'roc_auc': 0.88}
        changes = MetricsReporter.compare_metrics(current, previous)
        for metric in ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']:
            assert changes[metric]['change'] > 0

    def test_compare_metrics_regression(self):
        current = {'accuracy': 0.80, 'precision': 0.75, 'recall': 0.70, 'f1_score': 0.72, 'roc_auc': 0.82}
        previous = {'accuracy': 0.85, 'precision': 0.80, 'recall': 0.75, 'f1_score': 0.77, 'roc_auc': 0.88}
        changes = MetricsReporter.compare_metrics(current, previous)
        for metric in ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']:
            assert changes[metric]['change'] < 0

    def test_compare_metrics_empty(self):
        changes = MetricsReporter.compare_metrics({}, {})
        assert changes == {}

    def test_compare_metrics_partial_metrics(self):
        current = {'accuracy': 0.90}
        previous = {'accuracy': 0.85}
        changes = MetricsReporter.compare_metrics(current, previous)
        assert 'accuracy' in changes
        assert abs(changes['accuracy']['change'] - 0.05) < 1e-10
