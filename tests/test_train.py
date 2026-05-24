"""
Tests for train module.
"""

import pytest
import pandas as pd
import numpy as np
import joblib
from unittest.mock import patch, MagicMock
from sklearn.pipeline import Pipeline
from src.train import preprocess_data, create_preprocessor, train_model


class TestPreprocessData:
    """Test suite for preprocess_data function."""

    def test_preprocess_data_returns_dataframe(self, sample_adult_data):
        """Test that preprocess_data returns a DataFrame."""
        result = preprocess_data(sample_adult_data)
        assert isinstance(result, pd.DataFrame)

    def test_preprocess_data_handles_missing_values(self, sample_adult_data):
        """Test that preprocess_data fills missing values."""
        # Add missing values
        df = sample_adult_data.copy()
        df.loc[0, "age"] = np.nan
        df.loc[1, "workclass"] = np.nan

        result = preprocess_data(df)

        # Check no missing values remain
        assert result["age"].isna().sum() == 0
        assert result["workclass"].isna().sum() == 0

    def test_preprocess_data_encodes_target(self, sample_adult_data):
        """Test that preprocess_data encodes target variable."""
        result = preprocess_data(sample_adult_data)

        # Check that income is encoded as 0 or 1
        assert result["income"].isin([0, 1]).all()
        assert result["income"].dtype in [np.int64, np.int32, int]

    def test_preprocess_data_target_encoding_values(self, sample_adult_data):
        """Test that target encoding maps correctly."""
        result = preprocess_data(sample_adult_data)

        # Check specific mappings
        original_high_income = (sample_adult_data["income"] == ">50K").sum()
        encoded_high_income = (result["income"] == 1).sum()

        assert original_high_income == encoded_high_income

    def test_preprocess_data_does_not_modify_original(self, sample_adult_data):
        """Test that preprocess_data doesn't modify original DataFrame."""
        original = sample_adult_data.copy()
        result = preprocess_data(sample_adult_data)

        # Original should remain unchanged
        pd.testing.assert_frame_equal(sample_adult_data, original)

    def test_preprocess_data_handles_whitespace_in_target(self):
        """Test that preprocess_data handles whitespace in target values."""
        df = pd.DataFrame({"age": [25, 35], "income": [" >50K ", " <=50K "]})

        result = preprocess_data(df)

        assert result["income"].isin([0, 1]).all()

    def test_preprocess_data_fills_categorical_with_mode(self, sample_adult_data):
        """Test that categorical missing values are filled with mode."""
        df = sample_adult_data.copy()
        df.loc[0, "workclass"] = np.nan

        mode_value = df["workclass"].mode()[0]
        result = preprocess_data(df)

        assert result.loc[0, "workclass"] == mode_value

    def test_preprocess_data_fills_numerical_with_median(self, sample_adult_data):
        """Test that numerical missing values are filled with median."""
        df = sample_adult_data.copy()
        df.loc[0, "age"] = np.nan

        median_value = df["age"].median()
        result = preprocess_data(df)

        assert result.loc[0, "age"] == median_value


class TestCreatePreprocessor:
    """Test suite for create_preprocessor function."""

    def test_create_preprocessor_returns_column_transformer(self):
        """Test that create_preprocessor returns a ColumnTransformer."""
        from sklearn.compose import ColumnTransformer

        preprocessor = create_preprocessor()

        assert isinstance(preprocessor, ColumnTransformer)

    def test_create_preprocessor_has_transformers(self):
        """Test that preprocessor has both numerical and categorical transformers."""
        preprocessor = create_preprocessor()

        transformer_names = [name for name, _, _ in preprocessor.transformers]
        assert "num" in transformer_names
        assert "cat" in transformer_names

    def test_create_preprocessor_numerical_transformer(self):
        """Test that numerical transformer is StandardScaler."""
        from sklearn.preprocessing import StandardScaler

        preprocessor = create_preprocessor()

        num_transformer = None
        for name, transformer, _ in preprocessor.transformers:
            if name == "num":
                num_transformer = transformer
                break

        assert isinstance(num_transformer, StandardScaler)

    def test_create_preprocessor_categorical_transformer(self):
        """Test that categorical transformer is OneHotEncoder."""
        from sklearn.preprocessing import OneHotEncoder

        preprocessor = create_preprocessor()

        cat_transformer = None
        for name, transformer, _ in preprocessor.transformers:
            if name == "cat":
                cat_transformer = transformer
                break

        assert isinstance(cat_transformer, OneHotEncoder)


class TestTrainModel:
    """Test suite for train_model function."""

    def test_train_model_saves_model_file(self, mock_config, sample_adult_data):
        """Test that train_model saves the model file."""
        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            train_model()

            model_path = mock_config.MODELS_DIR / "income_model.pkl"
            assert model_path.exists()

    def test_train_model_saves_preprocessor_file(self, mock_config, sample_adult_data):
        """Test that train_model saves the preprocessor file."""
        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            train_model()

            preprocessor_path = mock_config.MODELS_DIR / "preprocessor.pkl"
            assert preprocessor_path.exists()

    def test_train_model_returns_pipeline(self, mock_config, sample_adult_data):
        """Test that train_model returns a Pipeline."""
        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            model = train_model()

            assert isinstance(model, Pipeline)

    def test_train_model_pipeline_has_correct_steps(self, mock_config, sample_adult_data):
        """Test that the pipeline has preprocessor and classifier steps."""
        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            model = train_model()

            step_names = [name for name, _ in model.steps]
            assert "preprocessor" in step_names
            assert "classifier" in step_names

    def test_train_model_uses_random_forest(self, mock_config, sample_adult_data):
        """Test that train_model uses RandomForestClassifier."""
        from sklearn.ensemble import RandomForestClassifier

        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            model = train_model()

            classifier = model.named_steps["classifier"]
            from xgboost import XGBClassifier

            assert isinstance(classifier, XGBClassifier)

    def test_train_model_creates_models_directory(self, mock_config, sample_adult_data):
        """Test that train_model creates MODELS_DIR if it doesn't exist."""
        import shutil

        shutil.rmtree(mock_config.MODELS_DIR)

        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            train_model()

            assert mock_config.MODELS_DIR.exists()

    def test_train_model_can_predict(self, mock_config, sample_adult_data):
        """Test that trained model can make predictions."""
        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            model = train_model()

            # Prepare test data - apply same preprocessing as training
            from src.train import preprocess_data

            X_test_raw = sample_adult_data.drop("income", axis=1).head(1)
            X_test = preprocess_data(X_test_raw)
            predictions = model.predict(X_test)

            assert len(predictions) == 1
            assert predictions[0] in [0, 1]

    def test_train_model_with_config_hyperparameters(self, mock_config, sample_adult_data):
        """Test that train_model uses config hyperparameters."""
        with patch("src.train.load_raw_data", return_value=sample_adult_data):
            model = train_model()

            classifier = model.named_steps["classifier"]
            assert classifier.n_estimators == mock_config.N_ESTIMATORS
            assert classifier.max_depth == mock_config.MAX_DEPTH
            assert classifier.random_state == mock_config.RANDOM_STATE
