"""Tests for utils/validation module."""

from src.utils.validation import (
    validate_feature_value,
    validate_prediction_input,
    check_data_distribution,
    VALID_SEX,
)


class TestValidateFeatureValue:
    def test_valid_categorical_value(self):
        is_valid, msg = validate_feature_value("sex", "Male", VALID_SEX)
        assert is_valid is True
        assert msg == ""

    def test_invalid_categorical_value(self):
        is_valid, msg = validate_feature_value("sex", "Alien", VALID_SEX)
        assert is_valid is False
        assert "Alien" in msg

    def test_none_value(self):
        is_valid, msg = validate_feature_value("age", None)
        assert is_valid is False
        assert "cannot be None" in msg

    def test_valid_numeric_in_range(self):
        is_valid, msg = validate_feature_value("age", 35)
        assert is_valid is True
        assert msg == ""

    def test_numeric_below_min(self):
        is_valid, msg = validate_feature_value("age", 5)
        assert is_valid is False
        assert "between" in msg

    def test_numeric_above_max(self):
        is_valid, msg = validate_feature_value("age", 200)
        assert is_valid is False
        assert "between" in msg

    def test_numeric_non_numeric_value(self):
        is_valid, msg = validate_feature_value("age", "old")
        assert is_valid is False
        assert "must be numeric" in msg

    def test_numeric_non_numeric_type_float(self):
        is_valid, msg = validate_feature_value("age", 35.5)
        assert is_valid is True

    def test_unknown_feature_no_ranges(self):
        is_valid, msg = validate_feature_value("unknown_field", "value")
        assert is_valid is True
        assert msg == ""

    def test_boundary_value_min(self):
        is_valid, msg = validate_feature_value("hours-per-week", 1)
        assert is_valid is True

    def test_boundary_value_max(self):
        is_valid, msg = validate_feature_value("hours-per-week", 99)
        assert is_valid is True


class TestValidatePredictionInput:
    def test_valid_input(self, sample_features_dict):
        is_valid, errors = validate_prediction_input(sample_features_dict)
        assert is_valid is True
        assert errors == []

    def test_invalid_categorical_value(self):
        features = {
            "age": 35,
            "workclass": "Invalid",
            "fnlwgt": 200000,
            "education": "Bachelors",
            "education-num": 13,
            "marital-status": "Married-civ-spouse",
            "occupation": "Tech-support",
            "relationship": "Husband",
            "race": "White",
            "sex": "Male",
            "capital-gain": 0,
            "capital-loss": 0,
            "hours-per-week": 40,
            "native-country": "United-States",
        }
        is_valid, errors = validate_prediction_input(features)
        assert is_valid is False
        assert any("workclass" in e for e in errors)

    def test_missing_feature(self):
        features = {"age": 35}
        is_valid, errors = validate_prediction_input(features)
        assert is_valid is False
        assert any("Missing" in e for e in errors)

    def test_invalid_numeric_value(self):
        features = {
            "age": 200,
            "workclass": "Private",
            "fnlwgt": 200000,
            "education": "Bachelors",
            "education-num": 13,
            "marital-status": "Married-civ-spouse",
            "occupation": "Tech-support",
            "relationship": "Husband",
            "race": "White",
            "sex": "Male",
            "capital-gain": 0,
            "capital-loss": 0,
            "hours-per-week": 40,
            "native-country": "United-States",
        }
        is_valid, errors = validate_prediction_input(features)
        assert is_valid is False
        assert any("age" in e for e in errors)


class TestCheckDataDistribution:
    def test_all_in_range(self):
        import pandas as pd

        df = pd.DataFrame({"age": [25, 35, 45]})
        is_normal, msg = check_data_distribution(df, "age", (18, 100))
        assert is_normal is True
        assert msg == ""

    def test_some_out_of_range(self):
        import pandas as pd

        df = pd.DataFrame({"age": [25, 150, 45]})
        is_normal, msg = check_data_distribution(df, "age", (18, 100))
        assert is_normal is False
        assert "outside expected range" in msg

    def test_missing_feature_returns_ok(self):
        import pandas as pd

        df = pd.DataFrame({"age": [25, 35]})
        is_normal, msg = check_data_distribution(df, "missing", (0, 100))
        assert is_normal is True
        assert msg == ""
