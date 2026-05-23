"""
Tests for config module.
"""

import pytest
from pathlib import Path
from src.config import Config, config


class TestConfig:
    """Test suite for Config class."""

    def test_config_instance_exists(self):
        """Test that global config instance exists."""
        assert config is not None
        assert isinstance(config, Config)

    def test_project_root_is_path(self):
        """Test that PROJECT_ROOT is a Path object."""
        assert isinstance(config.PROJECT_ROOT, Path)

    def test_data_dir_path(self):
        """Test that DATA_DIR is correctly set."""
        assert isinstance(config.DATA_DIR, Path)
        assert config.DATA_DIR == config.PROJECT_ROOT / "models"

    def test_models_dir_path(self):
        """Test that MODELS_DIR is correctly set."""
        assert isinstance(config.MODELS_DIR, Path)
        assert config.MODELS_DIR == config.PROJECT_ROOT / "models"

    def test_notebooks_dir_path(self):
        """Test that NOTEBOOKS_DIR is correctly set."""
        assert isinstance(config.NOTEBOOKS_DIR, Path)
        assert config.NOTEBOOKS_DIR == config.PROJECT_ROOT / "notebooks"

    def test_docs_dir_path(self):
        """Test that DOCS_DIR is correctly set."""
        assert isinstance(config.DOCS_DIR, Path)
        assert config.DOCS_DIR == config.PROJECT_ROOT / "docs"

    def test_data_file_names(self):
        """Test that data file names are set."""
        assert config.RAW_DATA_FILE == "adult.csv"
        assert config.PROCESSED_DATA_FILE == "processed_data.pkl"
        assert config.TRAIN_DATA_FILE == "train_data.pkl"
        assert config.TEST_DATA_FILE == "test_data.pkl"

    def test_hyperparameters(self):
        """Test that hyperparameters are set."""
        assert config.RANDOM_STATE == 42
        assert config.TEST_SIZE == 0.2
        assert config.N_ESTIMATORS == 100
        assert config.MAX_DEPTH == 10

    def test_feature_lists(self):
        """Test that feature lists are defined."""
        assert isinstance(config.CATEGORICAL_FEATURES, list)
        assert isinstance(config.NUMERICAL_FEATURES, list)
        assert len(config.CATEGORICAL_FEATURES) > 0
        assert len(config.NUMERICAL_FEATURES) > 0

    def test_categorical_features_content(self):
        """Test that categorical features contain expected columns."""
        expected_features = ['workclass', 'education', 'marital-status', 'occupation']
        for feature in expected_features:
            assert feature in config.CATEGORICAL_FEATURES

    def test_numerical_features_content(self):
        """Test that numerical features contain expected columns."""
        expected_features = ['age', 'education-num', 'capital-gain', 'capital-loss']
        for feature in expected_features:
            assert feature in config.NUMERICAL_FEATURES

    def test_target_variable(self):
        """Test that target variable is defined."""
        assert config.TARGET == 'income'

    def test_training_settings(self):
        """Test that training settings are defined."""
        assert config.CV_FOLDS == 5
        assert config.SCORING == 'accuracy'

    def test_config_is_singleton(self):
        """Test that config behaves as a singleton."""
        from src.config import config as config2
        assert config is config2
