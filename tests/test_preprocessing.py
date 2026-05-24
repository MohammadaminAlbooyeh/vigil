"""Unit tests for preprocessing utilities."""

from src.utils.preprocessing import preprocess_pipeline, verify_schema


def test_preprocess_pipeline_encodes_target(sample_adult_data):
    df = preprocess_pipeline(sample_adult_data)

    # Target should be encoded to 0/1
    assert set(df["income"].unique()).issubset({0, 1})

    # No missing values in required columns
    assert not df[["age", "education", "workclass"]].isna().any().any()


def test_verify_schema(sample_adult_data):
    from src.train import preprocess_data

    df = preprocess_data(sample_adult_data)
    assert verify_schema(df) is True
