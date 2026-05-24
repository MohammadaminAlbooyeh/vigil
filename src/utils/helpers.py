"""Small helper utilities for preprocessing and tests."""

from typing import Any
import pandas as pd


def safe_mode(series: pd.Series, fallback: Any = "") -> Any:
    """Return the mode of a series or a deterministic fallback if mode is missing.

    This avoids raising when series is all NaN or empty.
    """
    try:
        modes = series.mode(dropna=True)
        if len(modes) > 0:
            return modes.iloc[0]
    except Exception:
        pass
    return fallback
