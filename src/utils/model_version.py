"""Model versioning and metadata management."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

logger = logging.getLogger(__name__)


class ModelVersion:
    """Represents a single model version with metadata."""

    def __init__(self, version_id: str, metrics: Dict, metadata: Optional[Dict] = None):
        """Initialize a model version.

        Args:
            version_id: Unique identifier for this version
            metrics: Dictionary of performance metrics
            metadata: Additional metadata (e.g., hyperparameters, training data info)
        """
        self.version_id = version_id
        self.timestamp = datetime.utcnow().isoformat()
        self.metrics = metrics
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the model version
        """
        return {
            'version_id': self.version_id,
            'timestamp': self.timestamp,
            'metrics': self.metrics,
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict) -> 'ModelVersion':
        """Create from dictionary.

        Args:
            data: Dictionary with version data

        Returns:
            ModelVersion instance
        """
        version = ModelVersion(
            version_id=data['version_id'],
            metrics=data['metrics'],
            metadata=data.get('metadata', {})
        )
        version.timestamp = data.get('timestamp', version.timestamp)
        return version


class ModelVersionManager:
    """Manage model versions and history."""

    def __init__(self, versions_file: Path = None):
        """Initialize version manager.

        Args:
            versions_file: Path to versions history JSON file
        """
        if versions_file is None:
            versions_file = Path(__file__).parent.parent.parent / "models" / "versions.json"

        self.versions_file = versions_file
        self.versions: List[ModelVersion] = []
        self._load_versions()

    def _load_versions(self) -> None:
        """Load versions from file."""
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r') as f:
                    data = json.load(f)
                    self.versions = [ModelVersion.from_dict(v) for v in data.get('versions', [])]
                logger.info(f"Loaded {len(self.versions)} model versions")
            except Exception as e:
                logger.error(f"Failed to load versions: {e}")
                self.versions = []
        else:
            self.versions = []

    def save_versions(self) -> None:
        """Save versions to file."""
        self.versions_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'versions': [v.to_dict() for v in self.versions]
        }

        with open(self.versions_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(self.versions)} model versions to {self.versions_file}")

    def add_version(self, metrics: Dict, metadata: Optional[Dict] = None) -> str:
        """Add a new model version.

        Args:
            metrics: Performance metrics for this version
            metadata: Additional metadata

        Returns:
            Version ID
        """
        version_id = self._generate_version_id(metrics)
        version = ModelVersion(version_id, metrics, metadata)
        self.versions.append(version)

        logger.info(f"Added model version {version_id}")
        self.save_versions()

        return version_id

    def get_latest_version(self) -> Optional[ModelVersion]:
        """Get the latest model version.

        Returns:
            Latest ModelVersion or None
        """
        return self.versions[-1] if self.versions else None

    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get a specific model version by ID.

        Args:
            version_id: Version identifier

        Returns:
            ModelVersion or None
        """
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None

    def get_best_version(self, metric: str = 'accuracy') -> Optional[ModelVersion]:
        """Get the version with best metric.

        Args:
            metric: Metric name to compare (e.g., 'accuracy', 'f1_score')

        Returns:
            ModelVersion with best metric
        """
        if not self.versions:
            return None

        best_version = self.versions[0]
        best_value = best_version.metrics.get(metric, 0)

        for version in self.versions[1:]:
            value = version.metrics.get(metric, 0)
            if value > best_value:
                best_value = value
                best_version = version

        return best_version

    def get_version_history(self, metric: str = 'accuracy', limit: int = 10) -> List[Dict]:
        """Get version history for a specific metric.

        Args:
            metric: Metric name to track
            limit: Maximum number of versions to return

        Returns:
            List of version metrics
        """
        history = []
        for version in self.versions[-limit:]:
            history.append({
                'version_id': version.version_id,
                'timestamp': version.timestamp,
                'metric': metric,
                'value': version.metrics.get(metric, None)
            })
        return history

    def print_versions(self, limit: int = 10) -> None:
        """Print version history.

        Args:
            limit: Maximum number of versions to display
        """
        print("\n" + "="*80)
        print("MODEL VERSION HISTORY")
        print("="*80)

        versions_to_show = self.versions[-limit:]
        for i, version in enumerate(reversed(versions_to_show), 1):
            print(f"\n{i}. Version: {version.version_id}")
            print(f"   Timestamp: {version.timestamp}")
            print(f"   Accuracy: {version.metrics.get('accuracy', 'N/A'):.4f}")
            print(f"   F1-Score: {version.metrics.get('f1_score', 'N/A'):.4f}")
            print(f"   ROC-AUC: {version.metrics.get('roc_auc', 'N/A'):.4f}")

            if version.metadata:
                print(f"   Metadata: {version.metadata}")

        print("\n" + "="*80 + "\n")

    @staticmethod
    def _generate_version_id(metrics: Dict) -> str:
        """Generate version ID from metrics.

        Args:
            metrics: Performance metrics dictionary

        Returns:
            Version ID string (v1, v2, etc. or hash-based)
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        accuracy = metrics.get('accuracy', 0)
        hash_str = hashlib.md5(
            f"{timestamp}_{accuracy}".encode()
        ).hexdigest()[:6]
        return f"v_{timestamp}_{hash_str}"

    def compare_versions(self, version_id1: str, version_id2: str) -> Dict:
        """Compare two model versions.

        Args:
            version_id1: First version ID
            version_id2: Second version ID

        Returns:
            Dictionary with comparison results
        """
        v1 = self.get_version(version_id1)
        v2 = self.get_version(version_id2)

        if not v1 or not v2:
            return {}

        comparison = {}
        for metric in v1.metrics:
            if metric in v2.metrics:
                diff = v2.metrics[metric] - v1.metrics[metric]
                comparison[metric] = {
                    'v1': v1.metrics[metric],
                    'v2': v2.metrics[metric],
                    'difference': diff,
                    'improvement': diff > 0
                }

        return comparison

    def print_version_comparison(self, version_id1: str, version_id2: str) -> None:
        """Print comparison of two versions.

        Args:
            version_id1: First version ID
            version_id2: Second version ID
        """
        comparison = self.compare_versions(version_id1, version_id2)

        print("\n" + "="*80)
        print(f"VERSION COMPARISON: {version_id1} vs {version_id2}")
        print("="*80)

        for metric, values in comparison.items():
            v1_val = values['v1']
            v2_val = values['v2']
            diff = values['difference']
            improved = "↑" if values['improvement'] else "↓"

            print(f"{metric:15} {v1_val:8.4f} → {v2_val:8.4f} ({diff:+.4f}) {improved}")

        print("="*80 + "\n")
