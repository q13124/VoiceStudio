"""
Quality Comparison Utility
Compare quality metrics across multiple synthesis results
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    from .quality_metrics import calculate_all_metrics

    HAS_QUALITY_METRICS = True
except ImportError:
    HAS_QUALITY_METRICS = False
    logger.warning("Quality metrics not available. Comparison will be limited.")


class QualityComparison:
    """
    Compare quality metrics across multiple audio samples.

    Useful for comparing different engines, settings, or iterations.
    """

    def __init__(self):
        """Initialize quality comparison."""
        self.comparisons: List[Dict[str, Any]] = []

    def add_sample(
        self,
        name: str,
        audio: Any,
        reference_audio: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        sample_rate: int = 22050,
    ) -> Dict[str, Any]:
        """
        Add audio sample for comparison.

        Args:
            name: Sample name/identifier
            audio: Audio array or file path
            reference_audio: Optional reference audio for similarity
            metadata: Optional metadata (engine, settings, etc.)
            sample_rate: Sample rate

        Returns:
            Quality metrics for the sample
        """
        if not HAS_QUALITY_METRICS:
            logger.error("Quality metrics not available")
            return {}

        try:
            # Calculate quality metrics
            metrics = calculate_all_metrics(
                audio=audio,
                reference_audio=reference_audio,
                sample_rate=sample_rate,
            )

            # Store comparison entry
            entry = {
                "name": name,
                "metrics": metrics,
                "metadata": metadata or {},
            }
            self.comparisons.append(entry)

            logger.info(f"Added sample '{name}' for comparison")
            return metrics

        except Exception as e:
            logger.error(f"Failed to add sample '{name}': {e}")
            return {}

    def compare(self) -> Dict[str, Any]:
        """
        Compare all added samples.

        Returns:
            Comparison results with rankings and statistics
        """
        if not self.comparisons:
            return {"error": "No samples to compare"}

        results = {
            "total_samples": len(self.comparisons),
            "rankings": {},
            "statistics": {},
            "best_samples": {},
            "comparison_table": [],
        }

        # Extract metrics for comparison
        metric_names = ["mos_score", "similarity", "naturalness", "snr_db"]

        # Calculate statistics for each metric
        for metric_name in metric_names:
            values = []
            for entry in self.comparisons:
                metric_value = entry["metrics"].get(metric_name)
                if metric_value is not None:
                    values.append(metric_value)

            if values:
                results["statistics"][metric_name] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "range": float(np.max(values) - np.min(values)),
                }

                # Find best sample for this metric
                best_idx = np.argmax(values)
                results["best_samples"][metric_name] = {
                    "name": self.comparisons[best_idx]["name"],
                    "value": float(values[best_idx]),
                }

        # Rank samples by overall quality score
        rankings = []
        for entry in self.comparisons:
            metrics = entry["metrics"]
            # Calculate weighted quality score
            score = (
                metrics.get("mos_score", 0) * 0.3
                + metrics.get("similarity", 0) * 0.3
                + metrics.get("naturalness", 0) * 0.25
                + (metrics.get("snr_db", 0) / 50.0) * 0.15
            )
            rankings.append((entry["name"], score, entry))

        # Sort by score (descending)
        rankings.sort(key=lambda x: x[1], reverse=True)

        results["rankings"] = {
            rank
            + 1: {
                "name": name,
                "score": float(score),
                "metrics": entry["metrics"],
                "metadata": entry["metadata"],
            }
            for rank, (name, score, entry) in enumerate(rankings)
        }

        # Create comparison table
        results["comparison_table"] = self._create_comparison_table()

        return results

    def _create_comparison_table(self) -> List[Dict[str, Any]]:
        """
        Create comparison table for all samples.

        Returns:
            List of comparison entries
        """
        table = []

        for entry in self.comparisons:
            metrics = entry["metrics"]
            table_entry = {
                "name": entry["name"],
                "mos_score": metrics.get("mos_score"),
                "similarity": metrics.get("similarity"),
                "naturalness": metrics.get("naturalness"),
                "snr_db": metrics.get("snr_db"),
                "artifact_score": metrics.get("artifacts", {}).get("artifact_score"),
                "metadata": entry["metadata"],
            }
            table.append(table_entry)

        return table

    def get_best_sample(self, metric: Optional[str] = None) -> Optional[str]:
        """
        Get name of best sample.

        Args:
            metric: Optional specific metric to rank by

        Returns:
            Name of best sample or None
        """
        if not self.comparisons:
            return None

        if metric:
            # Find best for specific metric
            best_value = None
            best_name = None

            for entry in self.comparisons:
                value = entry["metrics"].get(metric)
                if value is not None:
                    if best_value is None or value > best_value:
                        best_value = value
                        best_name = entry["name"]

            return best_name
        else:
            # Find best overall (highest ranking)
            comparison = self.compare()
            if comparison.get("rankings"):
                return comparison["rankings"][1]["name"]
            return None

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of comparison.

        Returns:
            Summary dictionary
        """
        if not self.comparisons:
            return {"error": "No samples to compare"}

        comparison = self.compare()

        summary = {
            "total_samples": len(self.comparisons),
            "best_overall": comparison.get("rankings", {}).get(1, {}).get("name"),
            "best_by_metric": comparison.get("best_samples", {}),
            "statistics": comparison.get("statistics", {}),
        }

        return summary

    def clear(self):
        """Clear all comparisons."""
        self.comparisons.clear()
        logger.info("Comparison cleared")


def compare_audio_samples(
    samples: List[Dict[str, Any]], reference_audio: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Convenience function to compare multiple audio samples.

    Args:
        samples: List of sample dictionaries with 'name' and 'audio' keys
        reference_audio: Optional reference audio for similarity

    Returns:
        Comparison results
    """
    comparison = QualityComparison()

    for sample in samples:
        comparison.add_sample(
            name=sample["name"],
            audio=sample["audio"],
            reference_audio=reference_audio,
            metadata=sample.get("metadata"),
            sample_rate=sample.get("sample_rate", 22050),
        )

    return comparison.compare()
