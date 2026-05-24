"""Model monitoring and drift detection."""

import logging
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

# Statistical thresholds for drift detection
DRIFT_THRESHOLD_KOLMOGOROV = 0.05  # p-value for KS test
DRIFT_THRESHOLD_CHI2 = 0.05  # p-value for Chi-square test


class DriftDetector:
    """Detect data drift between reference and current data."""

    def __init__(self, reference_data: pd.DataFrame):
        """Initialize drift detector with reference data.

        Args:
            reference_data: Training data used as reference distribution
        """
        self.reference_data = reference_data
        self.reference_stats = self._calculate_stats(reference_data)
        logger.info(f"Drift detector initialized with {len(reference_data)} reference samples")

    def _calculate_stats(self, data: pd.DataFrame) -> Dict:
        """Calculate statistics for data.

        Args:
            data: Input data

        Returns:
            Dictionary with statistics
        """
        stats_dict = {}

        for col in data.columns:
            if data[col].dtype in ["int64", "float64"]:
                # Numeric feature
                stats_dict[col] = {
                    "type": "numeric",
                    "mean": data[col].mean(),
                    "std": data[col].std(),
                    "min": data[col].min(),
                    "max": data[col].max(),
                    "median": data[col].median(),
                    "q25": data[col].quantile(0.25),
                    "q75": data[col].quantile(0.75),
                }
            else:
                # Categorical feature
                value_counts = data[col].value_counts(normalize=True)
                stats_dict[col] = {
                    "type": "categorical",
                    "distribution": value_counts.to_dict(),
                    "unique_values": len(value_counts),
                }

        return stats_dict

    def detect_numeric_drift(
        self, feature: str, current_data: pd.Series
    ) -> Tuple[bool, float, str]:
        """Detect drift in numeric feature using Kolmogorov-Smirnov test.

        Args:
            feature: Feature name
            current_data: Current feature data

        Returns:
            Tuple of (drift_detected, p_value, description)
        """
        if (
            feature not in self.reference_stats
            or self.reference_stats[feature]["type"] != "numeric"
        ):
            return False, 1.0, f"Feature '{feature}' not in reference or not numeric"

        ref_stats = self.reference_stats[feature]
        ref_mean = ref_stats["mean"]
        ref_std = ref_stats["std"]

        # Normalize current data using reference statistics
        current_normalized = (current_data - ref_mean) / (ref_std + 1e-10)
        reference_normalized = (self.reference_data[feature] - ref_mean) / (ref_std + 1e-10)

        # Kolmogorov-Smirnov test
        statistic, p_value = stats.ks_2samp(reference_normalized, current_normalized)

        drift_detected = p_value < DRIFT_THRESHOLD_KOLMOGOROV
        description = f"KS test: statistic={statistic:.4f}, p_value={p_value:.4f}"

        if drift_detected:
            logger.warning(f"Drift detected in numeric feature '{feature}': {description}")
        else:
            logger.debug(f"No drift in numeric feature '{feature}': {description}")

        return drift_detected, p_value, description

    def detect_categorical_drift(
        self, feature: str, current_data: pd.Series
    ) -> Tuple[bool, float, str]:
        """Detect drift in categorical feature using Chi-square test.

        Args:
            feature: Feature name
            current_data: Current feature data

        Returns:
            Tuple of (drift_detected, p_value, description)
        """
        if (
            feature not in self.reference_stats
            or self.reference_stats[feature]["type"] != "categorical"
        ):
            return False, 1.0, f"Feature '{feature}' not in reference or not categorical"

        ref_stats = self.reference_stats[feature]
        ref_distribution = ref_stats["distribution"]

        # Get current distribution
        current_counts = current_data.value_counts()
        current_dist = (current_counts / len(current_data)).to_dict()

        # Align categories
        all_categories = set(list(ref_distribution.keys()) + list(current_dist.keys()))
        ref_probs = [ref_distribution.get(cat, 0) for cat in all_categories]
        curr_probs = [current_dist.get(cat, 0) for cat in all_categories]

        # Chi-square test
        expected = np.array(ref_probs) * len(current_data)
        observed = np.array(curr_probs) * len(current_data)

        # Avoid zero expected frequencies
        valid_idx = expected > 5
        if valid_idx.sum() < 2:
            return False, 1.0, "Insufficient data for chi-square test"

        expected = expected[valid_idx]
        observed = observed[valid_idx]

        chi2_stat, p_value = stats.chisquare(observed, expected)

        drift_detected = p_value < DRIFT_THRESHOLD_CHI2
        description = f"Chi-square test: statistic={chi2_stat:.4f}, p_value={p_value:.4f}"

        if drift_detected:
            logger.warning(f"Drift detected in categorical feature '{feature}': {description}")
        else:
            logger.debug(f"No drift in categorical feature '{feature}': {description}")

        return drift_detected, p_value, description

    def detect_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect drift in all features.

        Args:
            current_data: Current data to check for drift

        Returns:
            Dictionary with drift detection results for each feature
        """
        logger.info(f"Detecting drift in {len(current_data)} samples")
        drift_results = {"total_features": 0, "drifted_features": 0, "features": {}}

        for feature in self.reference_stats.keys():
            if feature not in current_data.columns:
                logger.warning(f"Feature '{feature}' not in current data")
                continue

            drift_results["total_features"] += 1

            if self.reference_stats[feature]["type"] == "numeric":
                drifted, p_val, desc = self.detect_numeric_drift(feature, current_data[feature])
            else:
                drifted, p_val, desc = self.detect_categorical_drift(feature, current_data[feature])

            if drifted:
                drift_results["drifted_features"] += 1

            drift_results["features"][feature] = {
                "drifted": drifted,
                "p_value": p_val,
                "description": desc,
            }

        drift_results["drift_ratio"] = (
            drift_results["drifted_features"] / drift_results["total_features"]
            if drift_results["total_features"] > 0
            else 0
        )

        return drift_results

    def print_drift_report(self, drift_results: Dict) -> None:
        """Print drift detection report.

        Args:
            drift_results: Dictionary with drift results
        """
        print("\n" + "=" * 80)
        print("DATA DRIFT DETECTION REPORT")
        print("=" * 80)
        print(f"\nTotal Features: {drift_results['total_features']}")
        print(f"Drifted Features: {drift_results['drifted_features']}")
        print(f"Drift Ratio: {drift_results['drift_ratio']:.2%}")

        if drift_results["drift_ratio"] > 0.5:
            print("\n⚠️  WARNING: High drift detected! Model performance may be degrading.")
        elif drift_results["drift_ratio"] > 0.25:
            print("\n⚠️  CAUTION: Moderate drift detected. Monitor model performance.")
        else:
            print("\n✓ No significant drift detected.")

        print("\nFeature-wise Results:")
        for feature, results in drift_results["features"].items():
            status = "DRIFTED" if results["drifted"] else "OK"
            print(f"  {feature:20} {status:8} (p={results['p_value']:.4f})")

        print("=" * 80 + "\n")


class ModelMonitor:
    """Monitor model performance and health."""

    def __init__(self):
        """Initialize model monitor."""
        self.prediction_history = []
        self.performance_history = []

    def log_prediction_batch(self, predictions: np.ndarray, probabilities: np.ndarray) -> None:
        """Log batch of predictions.

        Args:
            predictions: Array of predictions
            probabilities: Array of prediction probabilities
        """
        self.prediction_history.extend(
            [
                {"prediction": int(pred), "confidence": float(max(prob))}
                for pred, prob in zip(predictions, probabilities)
            ]
        )

    def get_confidence_stats(self) -> Dict:
        """Get confidence statistics.

        Returns:
            Dictionary with confidence metrics
        """
        if not self.prediction_history:
            return {}

        confidences = [p["confidence"] for p in self.prediction_history]
        return {
            "mean_confidence": float(np.mean(confidences)),
            "median_confidence": float(np.median(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences)),
            "std_confidence": float(np.std(confidences)),
        }

    def get_prediction_distribution(self) -> Dict:
        """Get prediction distribution.

        Returns:
            Dictionary with class distribution
        """
        if not self.prediction_history:
            return {}

        predictions = [p["prediction"] for p in self.prediction_history]
        total = len(predictions)

        class_0 = sum(1 for p in predictions if p == 0)
        class_1 = total - class_0

        return {
            "class_0_count": class_0,
            "class_1_count": class_1,
            "class_0_percentage": 100 * class_0 / total if total > 0 else 0,
            "class_1_percentage": 100 * class_1 / total if total > 0 else 0,
        }

    def print_monitoring_report(self) -> None:
        """Print model monitoring report."""
        conf_stats = self.get_confidence_stats()
        pred_dist = self.get_prediction_distribution()

        print("\n" + "=" * 80)
        print("MODEL MONITORING REPORT")
        print("=" * 80)

        print(f"\nPrediction Count: {len(self.prediction_history)}")

        if conf_stats:
            print("\nConfidence Statistics:")
            print(f"  Mean: {conf_stats['mean_confidence']:.4f}")
            print(f"  Median: {conf_stats['median_confidence']:.4f}")
            print(f"  Std Dev: {conf_stats['std_confidence']:.4f}")
            print(
                f"  Range: [{conf_stats['min_confidence']:.4f}, {conf_stats['max_confidence']:.4f}]"
            )

        if pred_dist:
            print("\nPrediction Distribution:")
            print(
                f"  <=50K: {pred_dist['class_0_count']:6d} "
                f"({pred_dist['class_0_percentage']:6.2f}%)"
            )
            print(
                f"  >50K:  {pred_dist['class_1_count']:6d} "
                f"({pred_dist['class_1_percentage']:6.2f}%)"
            )

        print("=" * 80 + "\n")
