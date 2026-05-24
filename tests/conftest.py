"""
Pytest configuration and shared fixtures.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_adult_data():
    """Create sample Adult dataset for testing."""
    data = {
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
        "fnlwgt": [100000, 200000, 150000, 180000, 120000, 160000, 190000],
        "education": [
            "Bachelors",
            "Masters",
            "HS-grad",
            "Doctorate",
            "Bachelors",
            "Some-college",
            "Assoc-voc",
        ],
        "education-num": [13, 14, 9, 16, 13, 10, 11],
        "marital-status": [
            "Never-married",
            "Married-civ-spouse",
            "Divorced",
            "Married-civ-spouse",
            "Never-married",
            "Married-civ-spouse",
            "Divorced",
        ],
        "occupation": [
            "Tech-support",
            "Exec-managerial",
            "Craft-repair",
            "Prof-specialty",
            "Sales",
            "Adm-clerical",
            "Machine-op-inspct",
        ],
        "relationship": [
            "Not-in-family",
            "Husband",
            "Not-in-family",
            "Husband",
            "Own-child",
            "Wife",
            "Unmarried",
        ],
        "race": ["White", "White", "Black", "Asian-Pac-Islander", "White", "White", "Black"],
        "sex": ["Male", "Male", "Female", "Male", "Female", "Female", "Male"],
        "capital-gain": [0, 15024, 0, 0, 0, 5178, 0],
        "capital-loss": [0, 0, 0, 0, 0, 0, 1902],
        "hours-per-week": [40, 50, 40, 60, 35, 40, 45],
        "native-country": [
            "United-States",
            "United-States",
            "United-States",
            "India",
            "United-States",
            "Canada",
            "United-States",
        ],
        "income": ["<=50K", ">50K", "<=50K", ">50K", "<=50K", ">50K", "<=50K"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_features_dict():
    """Create a sample feature dictionary for prediction."""
    return {
        "age": 35,
        "workclass": "Private",
        "fnlwgt": 200000,
        "education": "Bachelors",
        "education-num": 13,
        "marital-status": "Married-civ-spouse",
        "occupation": "Tech-support",
        "relationship": "Husband",
        "race": "White",
        "sex": "Male",
        "capital-gain": 5000,
        "capital-loss": 0,
        "hours-per-week": 40,
        "native-country": "United-States",
    }


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for data files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_models_dir():
    """Create a temporary directory for model files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config(temp_data_dir, temp_models_dir, monkeypatch):
    """Mock the config object for testing."""
    from src.config import config

    # Store original values
    original_data_dir = config.DATA_DIR
    original_models_dir = config.MODELS_DIR

    # Set temporary directories
    monkeypatch.setattr(config, "DATA_DIR", temp_data_dir)
    monkeypatch.setattr(config, "MODELS_DIR", temp_models_dir)

    yield config

    # Restore original values
    monkeypatch.setattr(config, "DATA_DIR", original_data_dir)
    monkeypatch.setattr(config, "MODELS_DIR", original_models_dir)


@pytest.fixture
def sample_preprocessed_data(sample_adult_data):
    """Create preprocessed sample data."""
    df = sample_adult_data.copy()
    # Convert target to binary
    df["income"] = df["income"].str.strip().map({">50K": 1, "<=50K": 0})
    return df
