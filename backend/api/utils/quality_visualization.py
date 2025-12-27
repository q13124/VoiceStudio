"""
Advanced Quality Metrics Visualization Utilities (IDEA 60).

Provides advanced analysis and visualization data for quality metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def calculate_quality_heatmap(
    quality_data: List[Dict[str, Any]],
    x_dimension: str = "engine",
    y_dimension: str = "profile",
    metric: str = "mos_score",
) -> Dict[str, Any]:
    """
    Calculate quality heatmap data.

    Args:
        quality_data: List of quality records with metrics
        x_dimension: Dimension for X axis (engine, profile, time_period)
        y_dimension: Dimension for Y axis (engine, profile, time_period)
        metric: Metric to visualize (mos_score, similarity, naturalness)

    Returns:
        Heatmap data dictionary
    """
    # Group data by dimensions
    heatmap_data: Dict[Tuple[str, str], List[float]] = {}
    x_values = set()
    y_values = set()

    for record in quality_data:
        x_val = str(record.get(x_dimension, "unknown"))
        y_val = str(record.get(y_dimension, "unknown"))
        metric_val = record.get("metrics", {}).get(metric)

        if metric_val is not None:
            x_values.add(x_val)
            y_values.add(y_val)
            key = (x_val, y_val)
            if key not in heatmap_data:
                heatmap_data[key] = []
            heatmap_data[key].append(float(metric_val))

    # Calculate averages for each cell
    heatmap_matrix = {}
    for x_val in sorted(x_values):
        for y_val in sorted(y_values):
            key = (x_val, y_val)
            if key in heatmap_data and heatmap_data[key]:
                avg_value = sum(heatmap_data[key]) / len(heatmap_data[key])
                heatmap_matrix[f"{x_val}_{y_val}"] = {
                    "x": x_val,
                    "y": y_val,
                    "value": avg_value,
                    "count": len(heatmap_data[key]),
                }

    return {
        "x_dimension": x_dimension,
        "y_dimension": y_dimension,
        "metric": metric,
        "x_values": sorted(list(x_values)),
        "y_values": sorted(list(y_values)),
        "matrix": heatmap_matrix,
        "min_value": min(
            (cell["value"] for cell in heatmap_matrix.values()), default=0.0
        ),
        "max_value": max(
            (cell["value"] for cell in heatmap_matrix.values()), default=1.0
        ),
    }


def calculate_quality_correlations(
    quality_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculate correlations between quality metrics.

    Args:
        quality_data: List of quality records with metrics

    Returns:
        Correlation matrix dictionary
    """
    metrics_list = ["mos_score", "similarity", "naturalness", "snr_db", "artifact_score"]
    correlation_matrix: Dict[str, Dict[str, float]] = {}

    # Extract metric values
    metric_vectors: Dict[str, List[float]] = {m: [] for m in metrics_list}

    for record in quality_data:
        metrics = record.get("metrics", {})
        for metric_name in metrics_list:
            value = metrics.get(metric_name)
            if value is not None:
                metric_vectors[metric_name].append(float(value))

    # Calculate correlations
    for metric1 in metrics_list:
        correlation_matrix[metric1] = {}
        for metric2 in metrics_list:
            if metric1 == metric2:
                correlation_matrix[metric1][metric2] = 1.0
            else:
                vec1 = metric_vectors[metric1]
                vec2 = metric_vectors[metric2]

                # Align vectors (use minimum length)
                min_len = min(len(vec1), len(vec2))
                if min_len < 2:
                    correlation_matrix[metric1][metric2] = 0.0
                else:
                    vec1_aligned = vec1[:min_len]
                    vec2_aligned = vec2[:min_len]

                    # Calculate Pearson correlation
                    correlation = _calculate_pearson_correlation(
                        vec1_aligned, vec2_aligned
                    )
                    correlation_matrix[metric1][metric2] = correlation

    return {
        "metrics": metrics_list,
        "correlations": correlation_matrix,
    }


def detect_quality_anomalies(
    quality_data: List[Dict[str, Any]],
    metric: str = "mos_score",
    threshold_std: float = 2.0,
) -> List[Dict[str, Any]]:
    """
    Detect quality anomalies and outliers.

    Args:
        quality_data: List of quality records
        metric: Metric to analyze
        threshold_std: Standard deviation threshold for anomaly detection

    Returns:
        List of detected anomalies
    """
    # Extract metric values
    values = []
    records_with_values = []

    for record in quality_data:
        value = record.get("metrics", {}).get(metric)
        if value is not None:
            values.append(float(value))
            records_with_values.append(record)

    if len(values) < 3:
        return []

    # Calculate statistics
    mean = np.mean(values)
    std = np.std(values)

    # Detect anomalies (values beyond threshold_std standard deviations)
    anomalies = []
    for i, (value, record) in enumerate(zip(values, records_with_values)):
        z_score = abs((value - mean) / std) if std > 0 else 0.0
        if z_score > threshold_std:
            anomalies.append(
                {
                    "index": i,
                    "record": record,
                    "metric": metric,
                    "value": value,
                    "mean": mean,
                    "std": std,
                    "z_score": z_score,
                    "deviation": value - mean,
                }
            )

    return sorted(anomalies, key=lambda x: abs(x["deviation"]), reverse=True)


def predict_quality(
    quality_data: List[Dict[str, Any]],
    input_factors: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Predict quality based on input factors (simple linear regression).

    Args:
        quality_data: Historical quality data
        input_factors: Input factors (engine, profile, etc.)

    Returns:
        Predicted quality metrics
    """
    # Simple prediction based on historical averages
    # In a real implementation, this would use machine learning

    # Filter relevant historical data
    relevant_data = []
    for record in quality_data:
        match = True
        for factor, value in input_factors.items():
            if record.get(factor) != value:
                match = False
                break
        if match:
            relevant_data.append(record)

    if not relevant_data:
        # Use all data if no matches
        relevant_data = quality_data

    # Calculate average metrics
    metrics_list = ["mos_score", "similarity", "naturalness", "snr_db"]
    predicted_metrics = {}

    for metric in metrics_list:
        values = [
            r.get("metrics", {}).get(metric)
            for r in relevant_data
            if r.get("metrics", {}).get(metric) is not None
        ]
        if values:
            predicted_metrics[metric] = sum(values) / len(values)
        else:
            predicted_metrics[metric] = None

    return {
        "input_factors": input_factors,
        "predicted_metrics": predicted_metrics,
        "confidence": min(1.0, len(relevant_data) / 10.0),  # Simple confidence
        "sample_count": len(relevant_data),
    }


def generate_quality_insights(
    quality_data: List[Dict[str, Any]],
    time_period_days: int = 30,
) -> List[Dict[str, Any]]:
    """
    Generate quality insights and recommendations.

    Args:
        quality_data: List of quality records
        time_period_days: Time period for analysis

    Returns:
        List of insights
    """
    insights = []

    if not quality_data:
        return insights

    # Calculate overall statistics
    metrics_list = ["mos_score", "similarity", "naturalness"]
    overall_stats = {}

    for metric in metrics_list:
        values = [
            r.get("metrics", {}).get(metric)
            for r in quality_data
            if r.get("metrics", {}).get(metric) is not None
        ]
        if values:
            overall_stats[metric] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

    # Insight 1: Overall quality assessment
    if "mos_score" in overall_stats:
        mos_mean = overall_stats["mos_score"]["mean"]
        if mos_mean >= 4.0:
            insights.append(
                {
                    "type": "positive",
                    "title": "Excellent Quality",
                    "message": f"Average MOS score is {mos_mean:.2f}, indicating excellent quality.",
                    "priority": "low",
                }
            )
        elif mos_mean < 3.0:
            insights.append(
                {
                    "type": "warning",
                    "title": "Quality Below Standard",
                    "message": f"Average MOS score is {mos_mean:.2f}, below professional standard (4.0).",
                    "priority": "high",
                    "action": "review_engine_settings",
                }
            )

    # Insight 2: Consistency check
    if "mos_score" in overall_stats:
        mos_values = [
            r.get("metrics", {}).get("mos_score")
            for r in quality_data
            if r.get("metrics", {}).get("mos_score") is not None
        ]
        if len(mos_values) > 1:
            mos_std = np.std(mos_values)
            if mos_std > 0.5:
                insights.append(
                    {
                        "type": "warning",
                        "title": "Quality Inconsistency",
                        "message": f"High variance in quality (std: {mos_std:.2f}). Quality is inconsistent.",
                        "priority": "medium",
                        "action": "standardize_settings",
                    }
                )

    # Insight 3: Engine comparison
    engine_stats: Dict[str, List[float]] = {}
    for record in quality_data:
        engine = record.get("engine", "unknown")
        mos = record.get("metrics", {}).get("mos_score")
        if mos is not None:
            if engine not in engine_stats:
                engine_stats[engine] = []
            engine_stats[engine].append(float(mos))

    if len(engine_stats) > 1:
        engine_averages = {
            engine: sum(values) / len(values)
            for engine, values in engine_stats.items()
        }
        best_engine = max(engine_averages, key=engine_averages.get)
        worst_engine = min(engine_averages, key=engine_averages.get)

        if engine_averages[best_engine] - engine_averages[worst_engine] > 0.5:
            insights.append(
                {
                    "type": "info",
                    "title": "Engine Performance Difference",
                    "message": f"{best_engine} performs better than {worst_engine} (MOS: {engine_averages[best_engine]:.2f} vs {engine_averages[worst_engine]:.2f}).",
                    "priority": "medium",
                    "action": "consider_engine_selection",
                }
            )

    # Insight 4: Trend analysis
    if len(quality_data) > 5:
        # Split into first half and second half
        mid = len(quality_data) // 2
        first_half = quality_data[:mid]
        second_half = quality_data[mid:]

        first_mos = [
            r.get("metrics", {}).get("mos_score")
            for r in first_half
            if r.get("metrics", {}).get("mos_score") is not None
        ]
        second_mos = [
            r.get("metrics", {}).get("mos_score")
            for r in second_half
            if r.get("metrics", {}).get("mos_score") is not None
        ]

        if first_mos and second_mos:
            first_avg = sum(first_mos) / len(first_mos)
            second_avg = sum(second_mos) / len(second_mos)

            if second_avg > first_avg * 1.05:
                insights.append(
                    {
                        "type": "positive",
                        "title": "Quality Improving",
                        "message": f"Quality has improved over time (MOS: {first_avg:.2f} → {second_avg:.2f}).",
                        "priority": "low",
                    }
                )
            elif second_avg < first_avg * 0.95:
                insights.append(
                    {
                        "type": "warning",
                        "title": "Quality Declining",
                        "message": f"Quality has declined over time (MOS: {first_avg:.2f} → {second_avg:.2f}).",
                        "priority": "high",
                        "action": "investigate_degradation",
                    }
                )

    return insights


def _calculate_pearson_correlation(x: List[float], y: List[float]) -> float:
    """Calculate Pearson correlation coefficient."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))
    sum_y2 = sum(y[i] ** 2 for i in range(n))

    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5

    if denominator == 0:
        return 0.0

    return numerator / denominator

