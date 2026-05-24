"""
Training script for the Income Prediction Project.
"""

import joblib
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

try:
    from .config import config
    from .data_loader import load_raw_data
    from .utils.preprocessing import preprocess_pipeline
    from .features.feature_engineering import create_features
    from .utils.metrics import ModelEvaluator
    from .utils.model_version import ModelVersionManager
    from .utils.feature_analysis import FeatureImportanceAnalyzer
except ImportError:
    from config import config
    from data_loader import load_raw_data
    from utils.preprocessing import preprocess_pipeline
    from features.feature_engineering import create_features
    from utils.metrics import ModelEvaluator
    from utils.model_version import ModelVersionManager
    from utils.feature_analysis import FeatureImportanceAnalyzer


def preprocess_data(df):
    """Wrapper preprocessing used by training and tests.

    Uses helpers in `src.utils.preprocessing` and applies lightweight feature engineering.
    """
    logger.info(f"Preprocessing {len(df)} samples")
    # deterministic preprocessing
    df_proc = preprocess_pipeline(df)

    # add derived features (kept additive so original columns remain)
    df_proc = create_features(df_proc)
    logger.info(f"Preprocessing complete, output shape: {df_proc.shape}")

    return df_proc


def create_preprocessor():
    """Create a preprocessor for categorical and numerical features."""
    numerical_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, config.NUMERICAL_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                config.CATEGORICAL_FEATURES,
            ),
        ]
    )
    return preprocessor


def train_model():
    """Train the income prediction model."""
    logger.info("Starting model training")

    # Load and preprocess data
    logger.info("Loading raw data")
    df = load_raw_data()
    logger.info(f"Loaded {len(df)} samples with {len(df.columns)} features")

    df = preprocess_data(df)

    # Split features and target
    X = df.drop(config.TARGET, axis=1)
    y = df[config.TARGET]
    logger.info(f"Features shape: {X.shape}, Target distribution: {y.value_counts().to_dict()}")

    # Split into train/test
    logger.info(f"Splitting data with test_size={config.TEST_SIZE}")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )
    logger.info(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Create pipeline
    logger.info("Creating preprocessing pipeline")
    preprocessor = create_preprocessor()

    logger.info(
        f"Building XGBoost model with n_estimators={config.N_ESTIMATORS}, max_depth={config.MAX_DEPTH}"
    )
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                XGBClassifier(
                    n_estimators=config.N_ESTIMATORS,
                    max_depth=config.MAX_DEPTH,
                    random_state=config.RANDOM_STATE,
                    use_label_encoder=False,
                    eval_metric="logloss",
                ),
            ),
        ]
    )

    # Train
    logger.info("Training model...")
    model.fit(X_train, y_train)
    logger.info("Training complete")

    # Save model
    logger.info(f"Saving model to {config.MODELS_DIR}")
    config.MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(model, config.MODELS_DIR / "income_model.pkl")
    joblib.dump(preprocessor, config.MODELS_DIR / "preprocessor.pkl")
    logger.info("Model and preprocessor saved")

    # Evaluate model
    logger.info("Evaluating model on test set")
    evaluator = ModelEvaluator(model, X_test, y_test)
    metrics = evaluator.evaluate()
    evaluator.save_metrics(config.MODELS_DIR / "metrics.json")
    evaluator.print_summary()

    # Track model version
    logger.info("Tracking model version")
    version_manager = ModelVersionManager(config.MODELS_DIR / "versions.json")
    metadata = {
        "n_estimators": config.N_ESTIMATORS,
        "max_depth": config.MAX_DEPTH,
        "test_size": config.TEST_SIZE,
        "random_state": config.RANDOM_STATE,
        "n_features": X.shape[1],
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }
    version_id = version_manager.add_version(metrics, metadata)
    logger.info(f"Model version {version_id} saved")
    version_manager.print_versions(limit=5)

    # Analyze feature importance
    try:
        logger.info("Analyzing feature importance")
        # Get feature names after preprocessing
        preprocessor = model.named_steps["preprocessor"]
        try:
            # Try to get feature names from preprocessor
            feature_names_transformed = preprocessor.get_feature_names_out()
            feature_names_transformed = [str(name) for name in feature_names_transformed]
        except Exception:
            # Fallback to original feature names
            feature_names_transformed = list(X.columns)

        importance_analyzer = FeatureImportanceAnalyzer(model, feature_names_transformed)
        importance_df = importance_analyzer.calculate_tree_importance()

        if not importance_df.empty:
            importance_analyzer.plot_feature_importance(
                output_path=config.MODELS_DIR / "feature_importance.png"
            )
            importance_analyzer.plot_cumulative_importance(
                output_path=config.MODELS_DIR / "cumulative_importance.png"
            )
            importance_analyzer.print_importance_report(top_n=15)
        else:
            logger.warning("Feature importance calculation returned empty results")
    except Exception as e:
        logger.warning(f"Feature importance analysis failed: {e}")

    return model


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    train_model()
