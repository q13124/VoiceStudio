"""
Example: Custom A/B Testing Comparison Algorithm

This example demonstrates how to create a custom comparison algorithm
for A/B testing with weighted scoring.
"""

from typing import Any, Dict


def normalize_metric(metric_name: str, value: float) -> float:
    """
    Normalize metric value to 0-1 range.

    Args:
        metric_name: Name of the metric
        value: Metric value

    Returns:
        Normalized value (0.0-1.0)
    """
    normalization_ranges = {
        "mos_score": (1.0, 5.0),  # MOS: 1.0-5.0
        "similarity": (0.0, 1.0),  # Similarity: 0.0-1.0
        "naturalness": (0.0, 1.0),  # Naturalness: 0.0-1.0
        "snr_db": (0.0, 60.0),  # SNR: 0-60 dB
    }

    if metric_name not in normalization_ranges:
        return 0.0

    min_val, max_val = normalization_ranges[metric_name]
    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))  # Clamp to 0-1


def custom_ab_comparison(
    sample_a: Dict[str, Any], sample_b: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Custom A/B comparison with weighted scoring.

    Args:
        sample_a: Sample A data with quality_metrics
        sample_b: Sample B data with quality_metrics

    Returns:
        Comparison results with winner and scores
    """
    # Define metric weights
    weights = {
        "mos_score": 0.4,  # 40% weight
        "similarity": 0.3,  # 30% weight
        "naturalness": 0.2,  # 20% weight
        "snr_db": 0.1,  # 10% weight
    }

    scores = {}

    # Calculate weighted scores for both samples
    for sample_name, sample_data in [("A", sample_a), ("B", sample_b)]:
        score = 0.0
        metrics = sample_data.get("quality_metrics", {})

        for metric, weight in weights.items():
            if metric in metrics:
                normalized_value = normalize_metric(metric, metrics[metric])
                score += normalized_value * weight

        scores[sample_name] = score

    # Determine winner
    if scores["A"] > scores["B"]:
        winner = "A"
    elif scores["B"] > scores["A"]:
        winner = "B"
    else:
        winner = "Tie"

    # Calculate difference
    difference = abs(scores["A"] - scores["B"])

    return {
        "overall_winner": winner,
        "scores": scores,
        "difference": difference,
        "sample_a_score": scores["A"],
        "sample_b_score": scores["B"],
        "confidence": (
            "high" if difference > 0.1 else "medium" if difference > 0.05 else "low"
        ),
    }


# Example usage
if __name__ == "__main__":
    # Sample A data
    sample_a = {
        "quality_metrics": {
            "mos_score": 4.2,
            "similarity": 0.88,
            "naturalness": 0.85,
            "snr_db": 45.0,
        }
    }

    # Sample B data
    sample_b = {
        "quality_metrics": {
            "mos_score": 4.0,
            "similarity": 0.90,
            "naturalness": 0.82,
            "snr_db": 42.0,
        }
    }

    # Perform comparison
    result = custom_ab_comparison(sample_a, sample_b)

    print("Custom A/B Comparison Results:")
    print(f"  Winner: Sample {result['overall_winner']}")
    print(f"  Sample A Score: {result['sample_a_score']:.3f}")
    print(f"  Sample B Score: {result['sample_b_score']:.3f}")
    print(f"  Difference: {result['difference']:.3f}")
    print(f"  Confidence: {result['confidence']}")
