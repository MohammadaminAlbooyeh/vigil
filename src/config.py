"""
Configuration settings for the Income Prediction Project.
"""

import os
from pathlib import Path

class Config:
    """Configuration class for the income prediction project."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "models"  # adult.csv is stored in models directory
    MODELS_DIR = PROJECT_ROOT / "models"
    NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
    DOCS_DIR = PROJECT_ROOT / "docs"

    # Data settings
    RAW_DATA_FILE = "adult.csv"  # Adult Census dataset in models directory
    PROCESSED_DATA_FILE = "processed_data.pkl"
    TRAIN_DATA_FILE = "train_data.pkl"
    TEST_DATA_FILE = "test_data.pkl"

    # Model hyperparameters
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    N_ESTIMATORS = 100  # For Random Forest
    MAX_DEPTH = 10

    # Feature engineering
    CATEGORICAL_FEATURES = [
        'workclass', 'education', 'marital-status', 'occupation',
        'relationship', 'race', 'sex', 'native-country',
        'age_bucket', 'hours_per_week_bucket', 'workclass_sector'
    ]
    NUMERICAL_FEATURES = ['age', 'fnlwgt', 'education-num', 'capital-gain',
                          'capital-loss', 'hours-per-week',
                          'capital_gain_binary', 'capital_loss_binary',
                          'marital_status_simplified', 'native_country_is_us']
    TARGET = 'income'

    # Training settings
    CV_FOLDS = 5
    SCORING = 'accuracy'

# Global config instance
config = Config()