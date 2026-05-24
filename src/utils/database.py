"""Database integration for prediction logging and audit trails."""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PredictionLogger:
    """Log predictions to SQLite database for audit trail."""

    def __init__(self, db_path: Path = None):
        """Initialize prediction logger.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "predictions.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    age INTEGER,
                    workclass TEXT,
                    fnlwgt INTEGER,
                    education TEXT,
                    education_num INTEGER,
                    marital_status TEXT,
                    occupation TEXT,
                    relationship TEXT,
                    race TEXT,
                    sex TEXT,
                    capital_gain INTEGER,
                    capital_loss INTEGER,
                    hours_per_week INTEGER,
                    native_country TEXT,
                    prediction INTEGER,
                    prediction_label TEXT,
                    prediction_proba_0 REAL,
                    prediction_proba_1 REAL,
                    model_version TEXT,
                    request_source TEXT
                )
            """)

            # Create index on timestamp
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON predictions(timestamp)
            """)

            # Create statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_predictions INTEGER,
                    avg_prediction_time REAL,
                    error_count INTEGER,
                    model_version TEXT
                )
            """)

            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def log_prediction(
        self,
        features: Dict,
        prediction: int,
        prediction_proba: Tuple[float, float],
        model_version: str = None,
        request_source: str = "api",
    ) -> None:
        """Log a prediction to the database.

        Args:
            features: Input features dictionary
            prediction: Predicted class (0 or 1)
            prediction_proba: Prediction probabilities tuple
            model_version: Model version used
            request_source: Source of request (api, cli, batch)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            prediction_label = ">50K" if prediction == 1 else "<=50K"

            cursor.execute(
                """
                INSERT INTO predictions (
                    timestamp, age, workclass, fnlwgt, education, education_num,
                    marital_status, occupation, relationship, race, sex,
                    capital_gain, capital_loss, hours_per_week, native_country,
                    prediction, prediction_label, prediction_proba_0, prediction_proba_1,
                    model_version, request_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.utcnow().isoformat(),
                    features.get("age"),
                    features.get("workclass"),
                    features.get("fnlwgt"),
                    features.get("education"),
                    features.get("education-num"),
                    features.get("marital-status"),
                    features.get("occupation"),
                    features.get("relationship"),
                    features.get("race"),
                    features.get("sex"),
                    features.get("capital-gain"),
                    features.get("capital-loss"),
                    features.get("hours-per-week"),
                    features.get("native-country"),
                    prediction,
                    prediction_label,
                    prediction_proba[0],
                    prediction_proba[1],
                    model_version,
                    request_source,
                ),
            )

            conn.commit()
            conn.close()
            logger.debug(f"Logged prediction: {prediction_label}")
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")

    def get_predictions(
        self,
        limit: int = 100,
        offset: int = 0,
        model_version: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> List[Dict]:
        """Retrieve predictions from database.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            model_version: Filter by model version
            start_date: Filter by start timestamp (ISO format)
            end_date: Filter by end timestamp (ISO format)

        Returns:
            List of prediction records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM predictions WHERE 1=1"
            params = []

            if model_version:
                query += " AND model_version = ?"
                params.append(model_version)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to retrieve predictions: {e}")
            return []

    def get_statistics(self, model_version: str = None) -> Dict:
        """Get prediction statistics.

        Args:
            model_version: Filter by model version

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total predictions
            query = "SELECT COUNT(*) FROM predictions WHERE 1=1"
            params = []

            if model_version:
                query += " AND model_version = ?"
                params.append(model_version)

            cursor.execute(query, params)
            total = cursor.fetchone()[0]

            # Predictions by class
            query = "SELECT prediction_label, COUNT(*) as count FROM predictions WHERE 1=1"
            params = []

            if model_version:
                query += " AND model_version = ?"
                params.append(model_version)

            query += " GROUP BY prediction_label"
            cursor.execute(query, params)
            class_dist = {row[0]: row[1] for row in cursor.fetchall()}

            # Average probabilities
            query = """
                SELECT
                    AVG(prediction_proba_0) as avg_proba_0,
                    AVG(prediction_proba_1) as avg_proba_1
                FROM predictions WHERE 1=1
            """
            params = []

            if model_version:
                query += " AND model_version = ?"
                params.append(model_version)

            cursor.execute(query, params)
            row = cursor.fetchone()
            avg_proba_0, avg_proba_1 = row if row else (0, 0)

            conn.close()

            return {
                "total_predictions": total,
                "predictions_by_class": class_dist,
                "avg_confidence_0": avg_proba_0,
                "avg_confidence_1": avg_proba_1,
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def export_predictions(
        self,
        output_path: Path,
        model_version: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> None:
        """Export predictions to CSV.

        Args:
            output_path: Path to save CSV file
            model_version: Filter by model version
            start_date: Filter by start timestamp
            end_date: Filter by end timestamp
        """
        try:
            import csv

            predictions = self.get_predictions(
                limit=999999, model_version=model_version, start_date=start_date, end_date=end_date
            )

            if not predictions:
                logger.warning("No predictions to export")
                return

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=predictions[0].keys())
                writer.writeheader()
                writer.writerows(predictions)

            logger.info(f"Exported {len(predictions)} predictions to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export predictions: {e}")

    def get_model_performance(self, model_version: str = None) -> Dict:
        """Get model performance metrics from logged predictions.

        Args:
            model_version: Filter by model version

        Returns:
            Dictionary with performance metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT prediction, COUNT(*) as count FROM predictions WHERE 1=1"
            params = []

            if model_version:
                query += " AND model_version = ?"
                params.append(model_version)

            query += " GROUP BY prediction"
            cursor.execute(query, params)

            pred_counts = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()

            total = sum(pred_counts.values())
            return {
                "class_0_predictions": pred_counts.get(0, 0),
                "class_1_predictions": pred_counts.get(1, 0),
                "total_predictions": total,
                "class_0_percentage": 100 * pred_counts.get(0, 0) / total if total > 0 else 0,
                "class_1_percentage": 100 * pred_counts.get(1, 0) / total if total > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return {}

    def print_statistics(self, model_version: str = None) -> None:
        """Print prediction statistics.

        Args:
            model_version: Filter by model version
        """
        stats = self.get_statistics(model_version)
        perf = self.get_model_performance(model_version)

        print("\n" + "=" * 60)
        print("PREDICTION STATISTICS")
        print("=" * 60)
        print(f"Total Predictions: {stats.get('total_predictions', 0)}")
        print(f"Predictions by Class: {stats.get('predictions_by_class', {})}")
        print(f"Avg Confidence (<=50K): {stats.get('avg_confidence_0', 0):.4f}")
        print(f"Avg Confidence (>50K): {stats.get('avg_confidence_1', 0):.4f}")
        print("\nClass Distribution:")
        print(f"  <=50K: {perf.get('class_0_percentage', 0):.2f}%")
        print(f"  >50K: {perf.get('class_1_percentage', 0):.2f}%")
        print("=" * 60 + "\n")
