"""Feature engineering helpers for the income prediction dataset.

Keep transformations additive and deterministic so tests remain stable.
"""

import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lightweight derived features without removing originals.

    Adds:
    - `capital_gain_binary`: 1 if `capital-gain` > 0 else 0
    - `capital_loss_binary`: 1 if `capital-loss` > 0 else 0
    - `age_bucket`: small categorical bucket of age
    - `hours_per_week_bucket`: work hours categories
    - `marital_status_simplified`: married vs single
    - `workclass_sector`: simplified workclass categories
    - `native_country_is_us`: 1 if US, 0 otherwise
    """
    df = df.copy()

    # capital gain/loss binary indicators
    if "capital-gain" in df.columns:
        df["capital_gain_binary"] = (df["capital-gain"] > 0).astype(int)
    if "capital-loss" in df.columns:
        df["capital_loss_binary"] = (df["capital-loss"] > 0).astype(int)

    # age buckets (deterministic bins)
    if "age" in df.columns:
        bins = [0, 25, 35, 45, 55, 65, 100]
        labels = ["<=25", "26-35", "36-45", "46-55", "56-65", "66+"]
        df["age_bucket"] = pd.cut(
            df["age"], bins=bins, labels=labels, right=True, include_lowest=True
        )
        df["age_bucket"] = df["age_bucket"].astype(str)

    # hours per week buckets
    if "hours-per-week" in df.columns:
        bins = [0, 20, 40, 50, 60, 100]
        labels = ["part-time", "full-time", "overtime", "long-hours", "extreme"]
        df["hours_per_week_bucket"] = pd.cut(
            df["hours-per-week"], bins=bins, labels=labels, right=True, include_lowest=True
        )
        df["hours_per_week_bucket"] = df["hours_per_week_bucket"].astype(str)

    # marital status simplified
    if "marital-status" in df.columns:
        married_statuses = ["Married-civ-spouse", "Married-spouse-absent", "Married-AF-spouse"]
        df["marital_status_simplified"] = df["marital-status"].isin(married_statuses).astype(int)

    # workclass sector
    if "workclass" in df.columns:

        def categorize_workclass(wc):
            if pd.isna(wc) or wc == " ?":
                return "unknown"
            wc = str(wc).strip()
            if wc in ["Private"]:
                return "private"
            elif wc in ["Self-emp-not-inc", "Self-emp-inc"]:
                return "self-employed"
            elif wc in ["Local-gov", "State-gov", "Federal-gov"]:
                return "government"
            else:
                return "other"

        df["workclass_sector"] = df["workclass"].apply(categorize_workclass)

    # native country is US
    if "native-country" in df.columns:
        df["native_country_is_us"] = (df["native-country"].str.strip() == "United-States").astype(
            int
        )

    return df
