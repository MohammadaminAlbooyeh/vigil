"""
Integration tests for the Income Prediction Project.
"""

import pytest
import pandas as pd
import joblib
from pathlib import Path
from unittest.mock import patch
from src.train import train_model, preprocess_data
from src.predict import predict_income, predict_proba_income
from src.data_loader import load_raw_data


class TestEndToEndPipeline:
    """Integration tests for the complete pipeline."""

    def test_train_and_predict_pipeline(self, mock_config, sample_adult_data):
        """Test complete pipeline from training to prediction."""
        # Step 1: Mock data loading
        with patch('src.train.load_raw_data', return_value=sample_adult_data):
            # Step 2: Train model
            model = train_model()
            
            # Verify model was saved
            model_path = mock_config.MODELS_DIR / "income_model.pkl"
            assert model_path.exists()
            
            # Step 3: Make prediction
            features = sample_adult_data.drop('income', axis=1).iloc[0].to_dict()
            prediction = predict_income(features)
            
            # Verify prediction is valid
            assert prediction in [0, 1]

    def test_train_and_predict_proba_pipeline(self, mock_config, sample_adult_data):
        """Test pipeline including probability predictions."""
        with patch('src.train.load_raw_data', return_value=sample_adult_data):
            # Train model
            train_model()
            
            # Make probability prediction
            features = sample_adult_data.drop('income', axis=1).iloc[0].to_dict()
            probabilities = predict_proba_income(features)
            
            # Verify probabilities are valid
            assert len(probabilities) == 2
            assert sum(probabilities) <= 1.01  # Allow small floating point error
            assert all(0 <= p <= 1 for p in probabilities)

    def test_multiple_predictions(self, mock_config, sample_adult_data):
        """Test making multiple predictions with trained model."""
        with patch('src.train.load_raw_data', return_value=sample_adult_data):
            # Train model
            train_model()
            
            # Make multiple predictions
            predictions = []
            for i in range(3):
                features = sample_adult_data.drop('income', axis=1).iloc[i].to_dict()
                prediction = predict_income(features)
                predictions.append(prediction)
            
            # Verify all predictions are valid
            assert len(predictions) == 3
            assert all(p in [0, 1] for p in predictions)

    def test_preprocessing_consistency(self, sample_adult_data):
        """Test that preprocessing produces consistent results."""
        # Preprocess same data twice
        result1 = preprocess_data(sample_adult_data)
        result2 = preprocess_data(sample_adult_data)
        
        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)

    def test_model_persistence(self, mock_config, sample_adult_data):
        """Test that saved model can be loaded and used."""
        with patch('src.train.load_raw_data', return_value=sample_adult_data):
            # Train and save model
            original_model = train_model()
            
            # Load saved model
            model_path = mock_config.MODELS_DIR / "income_model.pkl"
            loaded_model = joblib.load(model_path)
            
            # Make predictions with both models - use same preprocessing as training
            from src.train import preprocess_data
            X_test_raw = sample_adult_data.drop('income', axis=1).head(1)
            X_test = preprocess_data(X_test_raw)
            pred1 = original_model.predict(X_test)
            pred2 = loaded_model.predict(X_test)
            
            # Predictions should be identical
            assert pred1[0] == pred2[0]


class TestDataFlowIntegration:
    """Integration tests for data flow through the pipeline."""

    def test_raw_to_preprocessed_flow(self, mock_config, sample_adult_data):
        """Test data flow from raw to preprocessed."""
        # Save raw data with headers (matching actual format)
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        sample_adult_data.to_csv(file_path, index=False, header=True)
        
        # Load and preprocess
        df = load_raw_data()
        processed = preprocess_data(df)
        
        # Verify transformations
        assert len(processed) == len(sample_adult_data)
        assert processed['income'].isin([0, 1]).all()

    def test_train_test_split_consistency(self, mock_config, sample_adult_data):
        """Test that train-test split is consistent with random state."""
        from sklearn.model_selection import train_test_split
        
        df = preprocess_data(sample_adult_data)
        X = df.drop('income', axis=1)
        y = df['income']
        
        # Split data twice with same random state
        X_train1, X_test1, y_train1, y_test1 = train_test_split(
            X, y, test_size=mock_config.TEST_SIZE, random_state=mock_config.RANDOM_STATE
        )
        X_train2, X_test2, y_train2, y_test2 = train_test_split(
            X, y, test_size=mock_config.TEST_SIZE, random_state=mock_config.RANDOM_STATE
        )
        
        # Results should be identical
        pd.testing.assert_frame_equal(X_train1, X_train2)
        pd.testing.assert_frame_equal(X_test1, X_test2)


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_predict_without_trained_model(self, mock_config, sample_features_dict):
        """Test that prediction fails gracefully without trained model."""
        with pytest.raises(FileNotFoundError):
            predict_income(sample_features_dict)

    def test_train_with_invalid_data(self, mock_config):
        """Test that training handles invalid data appropriately."""
        # Create invalid data (all NaN)
        invalid_data = pd.DataFrame({
            'age': [None, None],
            'income': [None, None]
        })
        
        with patch('src.train.load_raw_data', return_value=invalid_data):
            with pytest.raises(Exception):  # Should raise some exception
                train_model()

    def test_predict_with_missing_features(self, mock_config, sample_adult_data):
        """Test prediction with incomplete feature set."""
        with patch('src.train.load_raw_data', return_value=sample_adult_data):
            train_model()
            
            # Create incomplete features
            incomplete_features = {'age': 30, 'education': 'Bachelors'}
            
            # This should either work (filling defaults) or raise an error
            # Depending on implementation
            try:
                prediction = predict_income(incomplete_features)
                # If it works, verify output
                assert prediction in [0, 1]
            except (KeyError, ValueError):
                # Expected if missing features not handled
                pass
