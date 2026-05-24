"""
Prediction utilities for the Income Prediction Project.
"""

import pandas as pd
import joblib
import logging
from pathlib import Path

try:
    from .config import config
    from .features.feature_engineering import create_features
    from .utils.database import PredictionLogger
except ImportError:
    from config import config
    from features.feature_engineering import create_features
    from utils.database import PredictionLogger

from sklearn.pipeline import Pipeline

# Global prediction logger instance
_prediction_logger = None


def get_prediction_logger():
    """Get or create prediction logger instance."""
    global _prediction_logger
    if _prediction_logger is None:
        _prediction_logger = PredictionLogger()
    return _prediction_logger

logger = logging.getLogger(__name__)

def load_model():
    """Load the trained model from disk."""
    model_path = config.MODELS_DIR / "income_model.pkl"
    if not model_path.exists():
        logger.error(f"Model file not found at {model_path}")
        raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
    logger.info(f"Loading model from {model_path}")
    return joblib.load(model_path)

def load_preprocessor():
    """Load the preprocessor (if saved separately)."""
    preprocessor_path = config.MODELS_DIR / "preprocessor.pkl"
    if preprocessor_path.exists():
        return joblib.load(preprocessor_path)
    else:
        # Assume preprocessing is done in the model pipeline
        return None

def predict_income(features, log_to_db=True, model_version=None, request_source="api"):
    """
    Predict income category for given features.

    Args:
        features (dict or pd.DataFrame): Input features for prediction.
        log_to_db (bool): Whether to log prediction to database
        model_version (str): Model version used for prediction
        request_source (str): Source of the request (api, cli, batch)

    Returns:
        int: Predicted income category (0 for <=50K, 1 for >50K).
    """
    logger.info("Starting income prediction")
    model = load_model()
    preprocessor = load_preprocessor()

    features_dict = None
    if isinstance(features, dict):
        features_dict = features.copy()
        features = pd.DataFrame([features])
        logger.debug(f"Converted dict to DataFrame with shape {features.shape}")

    # Ensure we apply the same feature engineering used during training
    try:
        features = create_features(features)
        logger.debug("Feature engineering applied")
    except Exception as e:
        logger.warning(f"Feature creation failed: {e}, proceeding without derived features")

    # If the model is a pipeline that already includes a preprocessor step,
    # do not apply the separately-saved preprocessor again (would double-transform).
    if isinstance(model, Pipeline) and 'preprocessor' in getattr(model, 'named_steps', {}):
        features_processed = features
    elif preprocessor is not None:
        features_processed = preprocessor.transform(features)
    else:
        features_processed = features

    prediction = model.predict(features_processed)
    prediction_result = prediction[0]

    # Log to database if requested
    if log_to_db and features_dict:
        try:
            proba = model.predict_proba(features_processed)[0]
            logger.debug("Logging prediction to database")
            db_logger = get_prediction_logger()
            db_logger.log_prediction(
                features_dict,
                prediction_result,
                proba,
                model_version=model_version,
                request_source=request_source
            )
        except Exception as e:
            logger.warning(f"Failed to log prediction to database: {e}")

    logger.info(f"Prediction complete: {prediction_result}")
    return prediction_result

def predict_proba_income(features):
    """
    Predict income probabilities for given features.

    Args:
        features (dict or pd.DataFrame): Input features for prediction.

    Returns:
        np.array: Probabilities for each class.
    """
    model = load_model()
    preprocessor = load_preprocessor()

    if isinstance(features, dict):
        features = pd.DataFrame([features])

    # Apply same feature engineering as during training
    try:
        features = create_features(features)
    except Exception:
        pass

    if isinstance(model, Pipeline) and 'preprocessor' in getattr(model, 'named_steps', {}):
        features_processed = features
    elif preprocessor is not None:
        features_processed = preprocessor.transform(features)
    else:
        features_processed = features

    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(features_processed)
        return probabilities[0]
    else:
        raise AttributeError("Model does not support probability prediction.")