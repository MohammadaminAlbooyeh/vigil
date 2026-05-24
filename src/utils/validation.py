"""Input validation and data quality checks for predictions."""

import pandas as pd
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Valid values for categorical features
VALID_WORKCLASS = {
    'Private', 'Self-emp-not-inc', 'Self-emp-inc', 'Federal-gov',
    'Local-gov', 'State-gov', 'Without-pay', 'Never-worked'
}

VALID_EDUCATION = {
    'Bachelors', 'Some-college', '11th', 'HS-grad', 'Prof-school',
    'Assoc-acdm', 'Assoc-voc', '9th', '7th-8th', '12th', 'Masters',
    '1st-4th', '10th', 'Doctorate', '5th-6th', 'Preschool'
}

VALID_MARITAL_STATUS = {
    'Married-civ-spouse', 'Divorced', 'Never-married', 'Separated',
    'Widowed', 'Married-spouse-absent', 'Married-AF-spouse'
}

VALID_OCCUPATION = {
    'Tech-support', 'Craft-repair', 'Other-service', 'Sales',
    'Exec-managerial', 'Prof-specialty', 'Handlers-cleaners',
    'Machine-op-inspct', 'Adm-clerical', 'Farming-fishing',
    'Transport-moving', 'Priv-house-serv', 'Protective-serv', 'Armed-Forces'
}

VALID_RELATIONSHIP = {
    'Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'
}

VALID_RACE = {
    'White', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other', 'Black'
}

VALID_SEX = {'Female', 'Male'}

VALID_NATIVE_COUNTRY = {
    'United-States', 'Cambodia', 'Thailand', 'Laos', 'Taiwan',
    'Portugal', 'Greece', 'Poland', 'Italy', 'Germany', 'Ireland',
    'France', 'Hungary', 'Scotland', 'England', 'Canada', 'Iran',
    'Japan', 'Mexico', 'India', 'South', 'China', 'Hong', 'Guatemala',
    'Nicaragua', 'El-Salvador', 'Dominican-Republic', 'Haiti', 'Ecuador',
    'Peru', 'Jamaica', 'Cuba', 'Puerto-Rico', 'Philippines', 'Vietnam',
    'Trinadad&Tobago', 'Yugoslavia', 'Hong Kong', 'Columbia', 'Hungary',
    'Honduras', 'Ireland', 'Scotland', 'England', 'Puerto-Rico'
}

# Numeric feature ranges
NUMERIC_RANGES = {
    'age': (18, 100),
    'fnlwgt': (1, 1500000),
    'education-num': (1, 16),
    'capital-gain': (0, 999999),
    'capital-loss': (0, 999999),
    'hours-per-week': (1, 99)
}


def validate_feature_value(feature_name: str, value, valid_values=None) -> Tuple[bool, str]:
    """Validate a single feature value.

    Args:
        feature_name: Name of the feature
        value: Value to validate
        valid_values: Set of valid values (for categorical features)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, f"{feature_name} cannot be None"

    # Categorical validation
    if valid_values is not None:
        if value not in valid_values:
            return False, f"{feature_name} must be one of {valid_values}, got '{value}'"
        return True, ""

    # Numeric validation
    if feature_name in NUMERIC_RANGES:
        min_val, max_val = NUMERIC_RANGES[feature_name]
        if not isinstance(value, (int, float)):
            return False, f"{feature_name} must be numeric, got {type(value).__name__}"
        if value < min_val or value > max_val:
            return False, f"{feature_name} must be between {min_val} and {max_val}, got {value}"
        return True, ""

    return True, ""


def validate_prediction_input(features: Dict) -> Tuple[bool, List[str]]:
    """Validate all prediction input features.

    Args:
        features: Dictionary of features for prediction

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []

    # Validate categorical features
    categorical_validations = {
        'workclass': VALID_WORKCLASS,
        'education': VALID_EDUCATION,
        'marital-status': VALID_MARITAL_STATUS,
        'occupation': VALID_OCCUPATION,
        'relationship': VALID_RELATIONSHIP,
        'race': VALID_RACE,
        'sex': VALID_SEX,
        'native-country': VALID_NATIVE_COUNTRY,
    }

    for feature_name, valid_values in categorical_validations.items():
        if feature_name not in features:
            errors.append(f"Missing required feature: {feature_name}")
            continue

        is_valid, error_msg = validate_feature_value(feature_name, features[feature_name], valid_values)
        if not is_valid:
            errors.append(error_msg)

    # Validate numeric features
    numeric_features = ['age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']
    for feature_name in numeric_features:
        if feature_name not in features:
            errors.append(f"Missing required feature: {feature_name}")
            continue

        is_valid, error_msg = validate_feature_value(feature_name, features[feature_name])
        if not is_valid:
            errors.append(error_msg)

    return len(errors) == 0, errors


def log_validation_errors(errors: List[str], request_data: Dict) -> None:
    """Log validation errors for monitoring.

    Args:
        errors: List of validation error messages
        request_data: The request data that failed validation
    """
    logger.warning(f"Input validation failed with {len(errors)} error(s)")
    for i, error in enumerate(errors, 1):
        logger.warning(f"  {i}. {error}")
    logger.debug(f"Request data: {request_data}")


def check_data_distribution(features: pd.DataFrame, feature_name: str,
                           expected_range: Tuple[float, float]) -> Tuple[bool, str]:
    """Check if a numeric feature is within expected range.

    Args:
        features: DataFrame with features
        feature_name: Name of feature to check
        expected_range: Tuple of (min, max) expected values

    Returns:
        Tuple of (is_normal, warning_message)
    """
    if feature_name not in features.columns:
        return True, ""

    min_val, max_val = expected_range
    feature_values = features[feature_name]

    out_of_range_count = ((feature_values < min_val) | (feature_values > max_val)).sum()
    if out_of_range_count > 0:
        pct = 100 * out_of_range_count / len(features)
        message = f"{feature_name}: {pct:.2f}% of values outside expected range [{min_val}, {max_val}]"
        return False, message

    return True, ""
