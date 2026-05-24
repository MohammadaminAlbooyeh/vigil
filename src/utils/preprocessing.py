"""Preprocessing utilities for the project.

Provide deterministic, small helpers used by `src.train` and tests.
"""

import pandas as pd

try:
    from .helpers import safe_mode
    from ..config import config
except ImportError:
    from helpers import safe_mode
    from config import config


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values deterministically: mode for objects, median for numerics."""
    df = df.copy()
    for col in df.columns:
        if df[col].dtype in ["object", "string"]:
            # safe_mode returns a deterministic fallback even if column empty
            df[col] = df[col].fillna(safe_mode(df[col]))
        elif pd.api.types.is_numeric_dtype(df[col]):
            median = df[col].median()
            if pd.isna(median):
                median = 0
            df[col] = df[col].fillna(median)
    return df


def encode_target(df: pd.DataFrame, target_col: str = None) -> pd.DataFrame:
    """Encode the `income` target to 0/1.

    Leaves non-target columns unchanged.
    """
    if target_col is None:
        target_col = config.TARGET

    df = df.copy()
    if target_col in df.columns:
        df[target_col] = df[target_col].astype(str).str.strip().map({">50K": 1, "<=50K": 0})
    return df


def preprocess_pipeline(df: pd.DataFrame, save: bool = False) -> pd.DataFrame:
    """Run full preprocessing: fill missing and encode target.

    If `save` is True, save processed DataFrame to `config.DATA_DIR / config.PROCESSED_DATA_FILE`.
    """
    df = fill_missing_values(df)
    df = encode_target(df)

    if save:
        path = config.DATA_DIR / config.PROCESSED_DATA_FILE
        config.DATA_DIR.mkdir(exist_ok=True)
        df.to_pickle(path)

    return df


def verify_schema(df: pd.DataFrame) -> bool:
    """Verify that required features from config are present in df."""
    required = set(config.CATEGORICAL_FEATURES + config.NUMERICAL_FEATURES + [config.TARGET])
    return required.issubset(set(df.columns))
