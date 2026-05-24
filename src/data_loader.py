"""
Data loading utilities for the Income Prediction Project.
"""

import pandas as pd
import requests

try:
    from .config import config
except ImportError:
    from config import config


def download_adult_dataset():
    """Download the Adult dataset from UCI ML Repository if not present."""
    data_dir = config.DATA_DIR
    data_dir.mkdir(exist_ok=True)
    file_path = data_dir / config.RAW_DATA_FILE

    if file_path.exists():
        print(f"Dataset already exists at {file_path}")
        return

    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    print("Downloading Adult dataset...")
    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(response.content)
    print(f"Dataset downloaded to {file_path}")


def load_raw_data():
    """Load the raw Adult dataset into a pandas DataFrame."""
    file_path = config.DATA_DIR / config.RAW_DATA_FILE

    if not file_path.exists():
        download_adult_dataset()

    # Load CSV with headers from adult.csv in models directory
    # The CSV has quoted column names with periods, we need to normalize them
    df = pd.read_csv(file_path, na_values=["?", " ?"])

    # Clean column names: remove quotes and convert periods to hyphens
    df.columns = df.columns.str.strip().str.replace('"', "").str.replace(".", "-")

    # Convert numeric columns to appropriate types
    numeric_cols = [
        "age",
        "fnlwgt",
        "education-num",
        "capital-gain",
        "capital-loss",
        "hours-per-week",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_processed_data():
    """Load processed data if available, otherwise load and process raw data."""
    processed_path = config.DATA_DIR / config.PROCESSED_DATA_FILE

    if processed_path.exists():
        return pd.read_pickle(processed_path)
    else:
        # For now, just return raw data; processing will be in preprocessing
        return load_raw_data()


def verify_raw_data(file_path=None):
    """Verify the raw data file has the expected schema (15 columns).

    Returns True if verification passes, False otherwise.
    """
    if file_path is None:
        file_path = config.DATA_DIR / config.RAW_DATA_FILE

    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {file_path}")

    # Try reading a small sample to verify column count
    try:
        sample = pd.read_csv(file_path, nrows=5)
    except Exception:
        return False

    # Adult dataset should have 15 columns
    return sample.shape[1] == 15
