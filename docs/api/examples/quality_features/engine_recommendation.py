"""
Engine Recommendation Example

This example demonstrates how to use the engine recommendation endpoint
to get AI-powered engine recommendations based on quality requirements (IDEA 47).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def get_engine_recommendation(
    target_tier="standard",
    min_mos_score=None,
    min_similarity=None,
    min_naturalness=None,
):
    """
    Get engine recommendation based on quality requirements.

    Args:
        target_tier: Quality tier - "fast", "standard", "high", "ultra" (default: "standard")
        min_mos_score: Minimum MOS score required (0.0-5.0, optional)
        min_similarity: Minimum similarity required (0.0-1.0, optional)
        min_naturalness: Minimum naturalness required (0.0-1.0, optional)

    Returns:
        EngineRecommendationResponse with recommended engine and reasoning
    """
    url = f"{BASE_URL}/quality/engine-recommendation"

    params = {"target_tier": target_tier}

    if min_mos_score is not None:
        params["min_mos_score"] = min_mos_score
    if min_similarity is not None:
        params["min_similarity"] = min_similarity
    if min_naturalness is not None:
        params["min_naturalness"] = min_naturalness

    print(f"Getting engine recommendation for tier: {target_tier}")
    if min_mos_score:
        print(f"  Minimum MOS Score: {min_mos_score}")
    if min_similarity:
        print(f"  Minimum Similarity: {min_similarity}")
    if min_naturalness:
        print(f"  Minimum Naturalness: {min_naturalness}")

    response = requests.get(url, params=params)
    response.raise_for_status()

    result = response.json()

    print(f"\n✅ Recommendation received!")
    print(f"\n🎯 Recommended Engine: {result['recommended_engine']}")
    print(f"📊 Target Tier: {result['target_tier']}")
    print(f"📋 Reasoning: {result['reasoning']}")

    if "target_metrics" in result and result["target_metrics"]:
        print(f"\n📈 Target Metrics:")
        for metric, value in result["target_metrics"].items():
            print(f"  {metric}: {value}")

    return result


def recommend_for_use_case(use_case):
    """
    Get engine recommendation for a specific use case.

    Args:
        use_case: Use case description - "fast", "quality", "balanced", "maximum"

    Returns:
        Engine recommendation
    """
    recommendations = {
        "fast": {"target_tier": "fast", "min_mos_score": 3.5},
        "quality": {
            "target_tier": "high",
            "min_mos_score": 4.0,
            "min_similarity": 0.85,
        },
        "balanced": {"target_tier": "standard", "min_mos_score": 3.8},
        "maximum": {
            "target_tier": "ultra",
            "min_mos_score": 4.5,
            "min_similarity": 0.90,
            "min_naturalness": 0.90,
        },
    }

    if use_case not in recommendations:
        raise ValueError(
            f"Unknown use case: {use_case}. Use: {list(recommendations.keys())}"
        )

    config = recommendations[use_case]
    return get_engine_recommendation(**config)


# Example usage
if __name__ == "__main__":
    # Example 1: Basic recommendation by tier
    print("Example 1: Basic Recommendation by Tier")
    print("-" * 60)
    result = get_engine_recommendation(target_tier="high")

    # Example 2: Recommendation with specific requirements
    print("\n\nExample 2: Recommendation with Specific Requirements")
    print("-" * 60)
    result = get_engine_recommendation(
        target_tier="standard", min_mos_score=4.0, min_similarity=0.85
    )

    # Example 3: Use case-based recommendation
    print("\n\nExample 3: Use Case-Based Recommendation")
    print("-" * 60)
    result = recommend_for_use_case("quality")

    # Example 4: Maximum quality recommendation
    print("\n\nExample 4: Maximum Quality Recommendation")
    print("-" * 60)
    result = recommend_for_use_case("maximum")
