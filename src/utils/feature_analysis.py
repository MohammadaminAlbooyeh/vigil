"""Feature importance analysis and visualization utilities."""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


class FeatureImportanceAnalyzer:
    """Analyze and visualize feature importance."""

    def __init__(self, model, feature_names: List[str]):
        """Initialize feature importance analyzer.

        Args:
            model: Trained sklearn pipeline or model
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.importance_scores = None
        logger.info(f"Feature analyzer initialized with {len(feature_names)} features")

    def calculate_tree_importance(self) -> pd.DataFrame:
        """Calculate feature importance using tree-based model's built-in method.

        Returns:
            DataFrame with features and importance scores
        """
        logger.info("Calculating tree-based feature importance")

        try:
            # Get classifier from pipeline
            if hasattr(self.model, 'named_steps'):
                classifier = self.model.named_steps.get('classifier')
            else:
                classifier = self.model

            # Get feature importances
            if hasattr(classifier, 'feature_importances_'):
                importances = classifier.feature_importances_
            else:
                logger.warning("Model does not have feature_importances_ attribute")
                return pd.DataFrame()

            # Create DataFrame
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)

            self.importance_scores = importance_df
            return importance_df

        except Exception as e:
            logger.error(f"Failed to calculate tree importance: {e}")
            return pd.DataFrame()

    def calculate_permutation_importance(
        self,
        X_test: pd.DataFrame,
        y_test: np.ndarray,
        n_repeats: int = 10
    ) -> pd.DataFrame:
        """Calculate permutation importance.

        Args:
            X_test: Test features
            y_test: Test labels
            n_repeats: Number of repetitions

        Returns:
            DataFrame with features and importance scores
        """
        logger.info(f"Calculating permutation importance ({n_repeats} repeats)")

        try:
            perm_importance = permutation_importance(
                self.model, X_test, y_test,
                n_repeats=n_repeats,
                random_state=42,
                n_jobs=-1
            )

            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': perm_importance.importances_mean,
                'std': perm_importance.importances_std
            }).sort_values('importance', ascending=False)

            return importance_df

        except Exception as e:
            logger.error(f"Failed to calculate permutation importance: {e}")
            return pd.DataFrame()

    def get_top_features(self, n: int = 20) -> pd.DataFrame:
        """Get top N important features.

        Args:
            n: Number of top features to return

        Returns:
            DataFrame with top N features
        """
        if self.importance_scores is None:
            logger.warning("Importance scores not calculated yet")
            return pd.DataFrame()

        return self.importance_scores.head(n)

    def plot_feature_importance(
        self,
        output_path: Path = None,
        top_n: int = 20,
        figsize: Tuple[int, int] = (12, 8)
    ) -> None:
        """Plot feature importance.

        Args:
            output_path: Path to save plot
            top_n: Number of top features to plot
            figsize: Figure size (width, height)
        """
        if self.importance_scores is None:
            logger.warning("No importance scores to plot")
            return

        top_features = self.importance_scores.head(top_n)

        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(
            data=top_features,
            x='importance',
            y='feature',
            palette='viridis',
            ax=ax
        )

        ax.set_xlabel('Importance Score', fontsize=12)
        ax.set_ylabel('Feature', fontsize=12)
        ax.set_title(f'Top {top_n} Feature Importance', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to {output_path}")
        else:
            plt.show()

        plt.close()

    def plot_cumulative_importance(
        self,
        output_path: Path = None,
        figsize: Tuple[int, int] = (10, 6)
    ) -> None:
        """Plot cumulative feature importance.

        Args:
            output_path: Path to save plot
            figsize: Figure size (width, height)
        """
        if self.importance_scores is None:
            logger.warning("No importance scores to plot")
            return

        # Calculate cumulative importance
        cumsum = self.importance_scores['importance'].cumsum()
        cumsum_pct = 100 * cumsum / cumsum.iloc[-1]

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(range(1, len(cumsum_pct) + 1), cumsum_pct.values, 'b-', linewidth=2)
        ax.axhline(y=80, color='r', linestyle='--', label='80% threshold')
        ax.axhline(y=90, color='orange', linestyle='--', label='90% threshold')
        ax.axhline(y=95, color='green', linestyle='--', label='95% threshold')

        ax.set_xlabel('Number of Features', fontsize=12)
        ax.set_ylabel('Cumulative Importance (%)', fontsize=12)
        ax.set_title('Cumulative Feature Importance', fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)
        ax.legend()

        plt.tight_layout()

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Cumulative importance plot saved to {output_path}")
        else:
            plt.show()

        plt.close()

    def print_importance_report(self, top_n: int = 20) -> None:
        """Print feature importance report.

        Args:
            top_n: Number of top features to display
        """
        if self.importance_scores is None:
            logger.warning("No importance scores available")
            return

        top_features = self.importance_scores.head(top_n)
        total_importance = self.importance_scores['importance'].sum()

        print("\n" + "="*70)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("="*70)
        print(f"\nTop {top_n} Most Important Features:\n")

        for idx, (_, row) in enumerate(top_features.iterrows(), 1):
            feature = row['feature']
            importance = row['importance']
            pct = 100 * importance / total_importance

            bar_length = int(pct / 2)
            bar = "█" * bar_length

            print(f"{idx:2d}. {feature:30s} {importance:8.4f} ({pct:6.2f}%) {bar}")

        # Calculate features needed for 80% importance
        cumsum = self.importance_scores['importance'].cumsum()
        cumsum_pct = 100 * cumsum / cumsum.iloc[-1]
        n_80_features = (cumsum_pct <= 80).sum() + 1

        print(f"\n{n_80_features} features account for 80% of importance")
        print(f"Total features: {len(self.importance_scores)}")
        print("="*70 + "\n")


class FeatureCorrelationAnalyzer:
    """Analyze feature correlations."""

    @staticmethod
    def calculate_correlation(data: pd.DataFrame, numeric_only: bool = True) -> pd.DataFrame:
        """Calculate feature correlations.

        Args:
            data: Input data
            numeric_only: Only include numeric features

        Returns:
            Correlation matrix
        """
        if numeric_only:
            numeric_data = data.select_dtypes(include=[np.number])
            return numeric_data.corr()
        else:
            return data.corr()

    @staticmethod
    def plot_correlation_heatmap(
        data: pd.DataFrame,
        output_path: Path = None,
        figsize: Tuple[int, int] = (12, 10)
    ) -> None:
        """Plot correlation heatmap.

        Args:
            data: Input data
            output_path: Path to save plot
            figsize: Figure size (width, height)
        """
        correlation = FeatureCorrelationAnalyzer.calculate_correlation(data)

        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(
            correlation,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )

        ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Correlation heatmap saved to {output_path}")
        else:
            plt.show()

        plt.close()

    @staticmethod
    def get_high_correlations(
        data: pd.DataFrame,
        threshold: float = 0.8
    ) -> List[Tuple[str, str, float]]:
        """Get highly correlated feature pairs.

        Args:
            data: Input data
            threshold: Correlation threshold

        Returns:
            List of (feature1, feature2, correlation) tuples
        """
        correlation = FeatureCorrelationAnalyzer.calculate_correlation(data)

        high_corr_pairs = []
        for i in range(len(correlation.columns)):
            for j in range(i + 1, len(correlation.columns)):
                corr_value = correlation.iloc[i, j]
                if abs(corr_value) >= threshold:
                    high_corr_pairs.append((
                        correlation.columns[i],
                        correlation.columns[j],
                        corr_value
                    ))

        return sorted(high_corr_pairs, key=lambda x: abs(x[2]), reverse=True)
