"""Unit tests for feature engineering helpers."""

from src.features.feature_engineering import create_features


def test_create_features_adds_columns(sample_adult_data):
    df = create_features(sample_adult_data)

    assert "capital_gain_binary" in df.columns
    assert "age_bucket" in df.columns

    # Check capital_gain_binary correctness for a known row
    # In the fixture, row 1 has capital-gain 15024 -> binary 1
    assert df.loc[1, "capital_gain_binary"] == 1
