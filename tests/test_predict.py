"""
Tests for predict module.
"""

import pytest
import pandas as pd
import joblib
import numpy as np
from unittest.mock import patch, MagicMock
from src.predict import load_model, load_preprocessor, predict_income, predict_proba_income


class TestLoadModel:
    """Test suite for load_model function."""

    def test_load_model_raises_error_if_not_exists(self, mock_config):
        """Test that load_model raises FileNotFoundError if model doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_model()

        assert "Model file not found" in str(exc_info.value)

    def test_load_model_returns_model(self, mock_config, sample_adult_data):
        """Test that load_model returns a model object."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline

        # Create and save a dummy model
        model = Pipeline([("classifier", RandomForestClassifier(random_state=42))])

        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        loaded_model = load_model()

        assert isinstance(loaded_model, Pipeline)

    def test_load_model_loads_correct_file(self, mock_config):
        """Test that load_model loads from the correct path."""
        from sklearn.ensemble import RandomForestClassifier

        model = RandomForestClassifier(random_state=42)
        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        with patch("joblib.load") as mock_load:
            mock_load.return_value = model
            load_model()

            # Check that joblib.load was called with correct path
            called_path = mock_load.call_args[0][0]
            assert called_path == model_path


class TestLoadPreprocessor:
    """Test suite for load_preprocessor function."""

    def test_load_preprocessor_returns_none_if_not_exists(self, mock_config):
        """Test that load_preprocessor returns None if file doesn't exist."""
        result = load_preprocessor()
        assert result is None

    def test_load_preprocessor_returns_preprocessor(self, mock_config):
        """Test that load_preprocessor returns preprocessor if it exists."""
        from sklearn.preprocessing import StandardScaler

        # Create and save a dummy preprocessor
        preprocessor = StandardScaler()
        preprocessor_path = mock_config.MODELS_DIR / "preprocessor.pkl"
        joblib.dump(preprocessor, preprocessor_path)

        loaded = load_preprocessor()

        assert isinstance(loaded, StandardScaler)


class TestPredictIncome:
    """Test suite for predict_income function."""

    def test_predict_income_with_dict_input(self, mock_config, sample_features_dict):
        """Test that predict_income works with dict input."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        # Create a simple model
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    StandardScaler(),
                    [
                        "age",
                        "fnlwgt",
                        "education-num",
                        "capital-gain",
                        "capital-loss",
                        "hours-per-week",
                    ],
                ),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    [
                        "workclass",
                        "education",
                        "marital-status",
                        "occupation",
                        "relationship",
                        "race",
                        "sex",
                        "native-country",
                    ],
                ),
            ]
        )

        model = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier(random_state=42, n_estimators=10)),
            ]
        )

        # Train on dummy data
        from conftest import sample_adult_data

        df = sample_adult_data()
        X = df.drop("income", axis=1)
        y = df["income"].str.strip().map({">50K": 1, "<=50K": 0})
        model.fit(X, y)

        # Save model
        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        # Predict
        prediction = predict_income(sample_features_dict)

        assert prediction in [0, 1]

    def test_predict_income_with_dataframe_input(self, mock_config, sample_features_dict):
        """Test that predict_income works with DataFrame input."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        # Create a simple model
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    StandardScaler(),
                    [
                        "age",
                        "fnlwgt",
                        "education-num",
                        "capital-gain",
                        "capital-loss",
                        "hours-per-week",
                    ],
                ),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    [
                        "workclass",
                        "education",
                        "marital-status",
                        "occupation",
                        "relationship",
                        "race",
                        "sex",
                        "native-country",
                    ],
                ),
            ]
        )

        model = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier(random_state=42, n_estimators=10)),
            ]
        )

        # Train on dummy data
        from conftest import sample_adult_data

        df = sample_adult_data()
        X = df.drop("income", axis=1)
        y = df["income"].str.strip().map({">50K": 1, "<=50K": 0})
        model.fit(X, y)

        # Save model
        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        # Predict with DataFrame
        features_df = pd.DataFrame([sample_features_dict])
        prediction = predict_income(features_df)

        assert prediction in [0, 1]

    def test_predict_income_converts_dict_to_dataframe(self, mock_config, sample_features_dict):
        """Test that predict_income converts dict to DataFrame."""
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1])

        with patch("src.predict.load_model", return_value=mock_model):
            with patch("src.predict.load_preprocessor", return_value=None):
                predict_income(sample_features_dict)

                # Check that predict was called with DataFrame-like object
                call_args = mock_model.predict.call_args[0][0]
                assert isinstance(call_args, pd.DataFrame)


class TestPredictProbaIncome:
    """Test suite for predict_proba_income function."""

    def test_predict_proba_income_returns_probabilities(self, mock_config, sample_features_dict):
        """Test that predict_proba_income returns probability array."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        # Create a simple model
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    StandardScaler(),
                    [
                        "age",
                        "fnlwgt",
                        "education-num",
                        "capital-gain",
                        "capital-loss",
                        "hours-per-week",
                    ],
                ),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    [
                        "workclass",
                        "education",
                        "marital-status",
                        "occupation",
                        "relationship",
                        "race",
                        "sex",
                        "native-country",
                    ],
                ),
            ]
        )

        model = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier(random_state=42, n_estimators=10)),
            ]
        )

        # Train on dummy data
        from conftest import sample_adult_data

        df = sample_adult_data()
        X = df.drop("income", axis=1)
        y = df["income"].str.strip().map({">50K": 1, "<=50K": 0})
        model.fit(X, y)

        # Save model
        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        # Predict probabilities
        probabilities = predict_proba_income(sample_features_dict)

        assert len(probabilities) == 2
        assert np.isclose(np.sum(probabilities), 1.0, atol=0.01)
        assert all(0 <= p <= 1 for p in probabilities)

    def test_predict_proba_income_raises_error_if_no_proba(self, mock_config, sample_features_dict):
        """Test that predict_proba_income raises error if model doesn't support probabilities."""
        from sklearn.svm import LinearSVC

        # Create a model without predict_proba
        model = LinearSVC()
        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        with pytest.raises(AttributeError) as exc_info:
            predict_proba_income(sample_features_dict)

        assert "does not support probability prediction" in str(exc_info.value)

    def test_predict_proba_income_with_dataframe(self, mock_config, sample_features_dict):
        """Test that predict_proba_income works with DataFrame input."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        # Create a simple model
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    StandardScaler(),
                    [
                        "age",
                        "fnlwgt",
                        "education-num",
                        "capital-gain",
                        "capital-loss",
                        "hours-per-week",
                    ],
                ),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore"),
                    [
                        "workclass",
                        "education",
                        "marital-status",
                        "occupation",
                        "relationship",
                        "race",
                        "sex",
                        "native-country",
                    ],
                ),
            ]
        )

        model = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("classifier", RandomForestClassifier(random_state=42, n_estimators=10)),
            ]
        )

        # Train on dummy data
        from conftest import sample_adult_data

        df = sample_adult_data()
        X = df.drop("income", axis=1)
        y = df["income"].str.strip().map({">50K": 1, "<=50K": 0})
        model.fit(X, y)

        # Save model
        model_path = mock_config.MODELS_DIR / "income_model.pkl"
        joblib.dump(model, model_path)

        # Predict with DataFrame
        features_df = pd.DataFrame([sample_features_dict])
        probabilities = predict_proba_income(features_df)

        assert len(probabilities) == 2
        assert np.isclose(np.sum(probabilities), 1.0, atol=0.01)
