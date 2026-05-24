"""Model evaluation metrics calculation and reporting."""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
)

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance and save metrics."""

    def __init__(self, model, X_test, y_test, model_name: str = "income_prediction"):
        """Initialize evaluator with model and test data.

        Args:
            model: Trained sklearn pipeline or model
            X_test: Test features
            y_test: Test labels
            model_name: Name for the model (used in saved metrics)
        """
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self.model_name = model_name
        self.metrics = {}
        self.predictions = None
        self.pred_proba = None

    def evaluate(self) -> Dict:
        """Calculate all metrics.

        Returns:
            Dictionary containing all calculated metrics
        """
        logger.info("Starting model evaluation")

        # Get predictions
        self.predictions = self.model.predict(self.X_test)
        self.pred_proba = self.model.predict_proba(self.X_test)[:, 1]

        # Calculate metrics
        self._calculate_classification_metrics()
        self._calculate_confusion_matrix()
        self._calculate_roc_auc()

        logger.info(f"Evaluation complete. Accuracy: {self.metrics['accuracy']:.4f}")
        return self.metrics

    def _calculate_classification_metrics(self) -> None:
        """Calculate accuracy, precision, recall, F1."""
        self.metrics["accuracy"] = float(accuracy_score(self.y_test, self.predictions))
        self.metrics["precision"] = float(precision_score(self.y_test, self.predictions))
        self.metrics["recall"] = float(recall_score(self.y_test, self.predictions))
        self.metrics["f1_score"] = float(f1_score(self.y_test, self.predictions))

        logger.debug(f"Classification metrics: {self.metrics}")

    def _calculate_confusion_matrix(self) -> None:
        """Calculate and store confusion matrix."""
        cm = confusion_matrix(self.y_test, self.predictions)
        self.metrics["confusion_matrix"] = cm.tolist()

        # Calculate related metrics
        tn, fp, fn, tp = cm.ravel()
        self.metrics["true_negatives"] = int(tn)
        self.metrics["false_positives"] = int(fp)
        self.metrics["false_negatives"] = int(fn)
        self.metrics["true_positives"] = int(tp)

        # Specificity and sensitivity
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        self.metrics["specificity"] = float(specificity)
        self.metrics["sensitivity"] = float(sensitivity)

        logger.debug(f"Confusion matrix: {cm}")

    def _calculate_roc_auc(self) -> None:
        """Calculate ROC-AUC score."""
        self.metrics["roc_auc"] = float(roc_auc_score(self.y_test, self.pred_proba))
        logger.debug(f"ROC-AUC: {self.metrics['roc_auc']:.4f}")

    def get_classification_report(self) -> str:
        """Get detailed classification report.

        Returns:
            Formatted classification report string
        """
        return classification_report(self.y_test, self.predictions, target_names=["<=50K", ">50K"])

    def save_metrics(self, output_path: Path = None) -> None:
        """Save metrics to JSON file.

        Args:
            output_path: Path to save metrics JSON. Defaults to models/metrics.json
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent / "models" / "metrics.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.metrics, f, indent=2)

        logger.info(f"Metrics saved to {output_path}")

    def print_summary(self) -> None:
        """Print evaluation summary to console."""
        print("\n" + "=" * 60)
        print("MODEL EVALUATION SUMMARY")
        print("=" * 60)
        print(f"\nAccuracy:  {self.metrics['accuracy']:.4f}")
        print(f"Precision: {self.metrics['precision']:.4f}")
        print(f"Recall:    {self.metrics['recall']:.4f}")
        print(f"F1-Score:  {self.metrics['f1_score']:.4f}")
        print(f"ROC-AUC:   {self.metrics['roc_auc']:.4f}")

        print("\nConfusion Matrix:")
        cm = np.array(self.metrics["confusion_matrix"])
        print(f"  True Negatives:  {self.metrics['true_negatives']}")
        print(f"  False Positives: {self.metrics['false_positives']}")
        print(f"  False Negatives: {self.metrics['false_negatives']}")
        print(f"  True Positives:  {self.metrics['true_positives']}")

        print("\nDetailed Classification Report:")
        print(self.get_classification_report())
        print("=" * 60 + "\n")


class MetricsReporter:
    """Generate metrics reports and comparisons."""

    @staticmethod
    def load_metrics(metrics_path: Path) -> Dict:
        """Load metrics from JSON file.

        Args:
            metrics_path: Path to metrics JSON file

        Returns:
            Dictionary of metrics
        """
        if not metrics_path.exists():
            logger.warning(f"Metrics file not found at {metrics_path}")
            return {}

        with open(metrics_path, "r") as f:
            return json.load(f)

    @staticmethod
    def compare_metrics(current: Dict, previous: Dict) -> Dict:
        """Compare current metrics with previous version.

        Args:
            current: Current metrics dictionary
            previous: Previous metrics dictionary

        Returns:
            Dictionary with metric changes
        """
        changes = {}
        for metric in ["accuracy", "precision", "recall", "f1_score", "roc_auc"]:
            if metric in current and metric in previous:
                change = current[metric] - previous[metric]
                pct_change = (change / previous[metric] * 100) if previous[metric] != 0 else 0
                changes[metric] = {
                    "current": current[metric],
                    "previous": previous[metric],
                    "change": change,
                    "pct_change": pct_change,
                }

        return changes

    @staticmethod
    def print_metrics_comparison(current: Dict, previous: Dict) -> None:
        """Print comparison of current vs previous metrics.

        Args:
            current: Current metrics dictionary
            previous: Previous metrics dictionary
        """
        changes = MetricsReporter.compare_metrics(current, previous)

        print("\n" + "=" * 70)
        print("METRICS COMPARISON (Current vs Previous)")
        print("=" * 70)

        for metric, values in changes.items():
            curr = values["current"]
            prev = values["previous"]
            change = values["change"]
            pct = values["pct_change"]

            indicator = "✓" if change >= 0 else "✗"
            print(
                f"{metric:12} {curr:.4f} (prev: {prev:.4f}) {indicator} {change:+.4f} ({pct:+.2f}%)"
            )

        print("=" * 70 + "\n")
