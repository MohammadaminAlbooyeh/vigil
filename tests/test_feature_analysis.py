"""Tests for utils/feature_analysis module."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from src.utils.feature_analysis import FeatureImportanceAnalyzer, FeatureCorrelationAnalyzer


class TestFeatureImportanceAnalyzer:
    @pytest.fixture
    def model_with_importance(self):
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(random_state=42, n_estimators=10)
        X = pd.DataFrame({
            'feature_a': [1, 2, 3, 4, 5],
            'feature_b': [5, 4, 3, 2, 1],
            'feature_c': [1, 1, 1, 1, 1],
        })
        y = pd.Series([0, 1, 0, 1, 0])
        model.fit(X, y)
        return model

    @pytest.fixture
    def pipeline_with_importance(self):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        model = Pipeline([
            ('classifier', RandomForestClassifier(random_state=42, n_estimators=10))
        ])
        X = pd.DataFrame({
            'feature_a': [1, 2, 3, 4, 5],
            'feature_b': [5, 4, 3, 2, 1],
        })
        y = pd.Series([0, 1, 0, 1, 0])
        model.fit(X, y)
        return model, ['feature_a', 'feature_b']

    def test_calculate_tree_importance(self, model_with_importance):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        result = analyzer.calculate_tree_importance()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'feature' in result.columns
        assert 'importance' in result.columns
        assert result['importance'].sum() > 0

    def test_tree_importance_sorted_descending(self, model_with_importance):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        result = analyzer.calculate_tree_importance()
        assert result['importance'].is_monotonic_decreasing

    def test_calculate_tree_importance_pipeline(self, pipeline_with_importance):
        model, feature_names = pipeline_with_importance
        analyzer = FeatureImportanceAnalyzer(model, feature_names)
        result = analyzer.calculate_tree_importance()
        assert len(result) == 2

    def test_calculate_tree_importance_no_importance_attr(self):
        from sklearn.dummy import DummyClassifier
        model = DummyClassifier(strategy='constant', constant=0)
        X = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        y = pd.Series([0, 0, 0])
        model.fit(X, y)
        analyzer = FeatureImportanceAnalyzer(model, ['a', 'b'])
        result = analyzer.calculate_tree_importance()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_permutation_importance(self):
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(random_state=42, n_estimators=10)
        X = pd.DataFrame({
            'x': [1, 2, 3, 4, 5, 6],
            'y': [5, 4, 3, 2, 1, 0],
        })
        y = np.array([0, 1, 0, 1, 0, 1])
        model.fit(X, y)
        analyzer = FeatureImportanceAnalyzer(model, ['x', 'y'])
        result = analyzer.calculate_permutation_importance(X, y, n_repeats=3)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'std' in result.columns

    def test_get_top_features(self, model_with_importance):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        analyzer.calculate_tree_importance()
        top = analyzer.get_top_features(n=2)
        assert len(top) == 2

    def test_get_top_features_before_calculation(self, model_with_importance):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        result = analyzer.get_top_features(n=2)
        assert result.empty

    def test_plot_feature_importance_saves_file(self, tmp_path, model_with_importance):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        analyzer.calculate_tree_importance()
        output_path = tmp_path / "feature_importance.png"
        analyzer.plot_feature_importance(output_path=output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_plot_cumulative_importance_saves_file(self, tmp_path, model_with_importance):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        analyzer.calculate_tree_importance()
        output_path = tmp_path / "cumulative_importance.png"
        analyzer.plot_cumulative_importance(output_path=output_path)
        assert output_path.exists()

    def test_print_importance_report_runs(self, model_with_importance, capsys):
        feature_names = ['feature_a', 'feature_b', 'feature_c']
        analyzer = FeatureImportanceAnalyzer(model_with_importance, feature_names)
        analyzer.calculate_tree_importance()
        analyzer.print_importance_report(top_n=3)
        captured = capsys.readouterr()
        assert 'FEATURE IMPORTANCE ANALYSIS' in captured.out


class TestFeatureCorrelationAnalyzer:
    @pytest.fixture
    def sample_data(self):
        return pd.DataFrame({
            'age': [25, 35, 45, 55],
            'income': [0, 1, 0, 1],
            'hours-per-week': [40, 50, 40, 60]
        })

    def test_calculate_correlation(self, sample_data):
        corr = FeatureCorrelationAnalyzer.calculate_correlation(sample_data)
        assert isinstance(corr, pd.DataFrame)
        assert corr.shape[0] == 3
        assert corr.shape[1] == 3

    def test_calculate_correlation_returns_correct_shape(self, sample_data):
        corr = FeatureCorrelationAnalyzer.calculate_correlation(sample_data)
        assert list(corr.columns) == ['age', 'income', 'hours-per-week']

    def test_calculate_correlation_identity_diagonal(self, sample_data):
        corr = FeatureCorrelationAnalyzer.calculate_correlation(sample_data)
        assert abs(corr.loc['age', 'age'] - 1.0) < 1e-10

    def test_get_high_correlations(self, sample_data):
        pairs = FeatureCorrelationAnalyzer.get_high_correlations(sample_data, threshold=0.5)
        assert isinstance(pairs, list)
        for pair in pairs:
            assert len(pair) == 3

    def test_get_high_correlations_empty(self, sample_data):
        pairs = FeatureCorrelationAnalyzer.get_high_correlations(sample_data, threshold=0.99)
        assert pairs == []

    def test_plot_correlation_heatmap_saves_file(self, tmp_path, sample_data):
        output_path = tmp_path / "correlation.png"
        FeatureCorrelationAnalyzer.plot_correlation_heatmap(sample_data, output_path=output_path)
        assert output_path.exists()
