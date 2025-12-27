"""
Example: Custom Engine Recommendation Algorithm

This example demonstrates how to create a custom engine recommendation
algorithm with user preferences and advanced scoring.
"""

from typing import Any, Dict, List, Optional

# Engine characteristics database
ENGINE_CHARACTERISTICS = {
    "xtts": {
        "tier": "standard",
        "mos_range": (3.5, 4.2),
        "similarity_range": (0.80, 0.90),
        "naturalness_range": (0.75, 0.85),
        "speed": "fast",
        "multilingual": True,
        "languages": 14,
    },
    "chatterbox": {
        "tier": "high",
        "mos_range": (4.0, 4.5),
        "similarity_range": (0.85, 0.95),
        "naturalness_range": (0.80, 0.90),
        "speed": "medium",
        "multilingual": True,
        "languages": 23,
    },
    "tortoise": {
        "tier": "ultra",
        "mos_range": (4.2, 4.8),
        "similarity_range": (0.90, 0.98),
        "naturalness_range": (0.85, 0.95),
        "speed": "slow",
        "multilingual": False,
        "languages": 1,
    },
}

# Tier definitions
TIER_DEFINITIONS = {
    "fast": {
        "target_mos": 3.5,
        "target_similarity": 0.80,
        "target_naturalness": 0.75,
        "speed_priority": 1.0,
    },
    "standard": {
        "target_mos": 3.8,
        "target_similarity": 0.85,
        "target_naturalness": 0.80,
        "speed_priority": 0.7,
    },
    "high": {
        "target_mos": 4.2,
        "target_similarity": 0.90,
        "target_naturalness": 0.85,
        "speed_priority": 0.4,
    },
    "ultra": {
        "target_mos": 4.5,
        "target_similarity": 0.95,
        "target_naturalness": 0.90,
        "speed_priority": 0.1,
    },
}


def calculate_tier_match_score(engine_tier: str, target_tier: str) -> float:
    """Calculate how well engine tier matches target tier."""
    tier_order = ["fast", "standard", "high", "ultra"]

    engine_index = tier_order.index(engine_tier)
    target_index = tier_order.index(target_tier)

    # Exact match = 1.0, adjacent = 0.7, far = 0.3
    distance = abs(engine_index - target_index)
    if distance == 0:
        return 1.0
    elif distance == 1:
        return 0.7
    else:
        return 0.3


def calculate_metric_match(engine_range: tuple, target_value: float) -> float:
    """Calculate how well engine range matches target value."""
    min_val, max_val = engine_range

    if min_val <= target_value <= max_val:
        # Target is within range - perfect match
        return 1.0
    elif target_value < min_val:
        # Target is below range
        distance = min_val - target_value
        range_size = max_val - min_val
        return max(0.0, 1.0 - (distance / range_size))
    else:
        # Target is above range
        distance = target_value - max_val
        range_size = max_val - min_val
        return max(0.0, 1.0 - (distance / range_size))


def calculate_speed_score(engine_speed: str, speed_priority: float) -> float:
    """Calculate speed score based on priority."""
    speed_scores = {"fast": 1.0, "medium": 0.6, "slow": 0.2}

    base_score = speed_scores.get(engine_speed, 0.5)
    return base_score * speed_priority


def recommend_engine_custom(
    target_tier: str = "standard",
    min_mos_score: Optional[float] = None,
    min_similarity: Optional[float] = None,
    min_naturalness: Optional[float] = None,
    user_preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Custom engine recommendation with advanced scoring.

    Args:
        target_tier: Quality tier (fast, standard, high, ultra)
        min_mos_score: Minimum MOS requirement
        min_similarity: Minimum similarity requirement
        min_naturalness: Minimum naturalness requirement
        user_preferences: User preferences (preferred_engine, speed_priority, etc.)

    Returns:
        Recommendation with engine, score, and reasoning
    """
    # Get tier definition
    tier_def = TIER_DEFINITIONS.get(target_tier, TIER_DEFINITIONS["standard"])

    # Build target metrics
    target_metrics = {
        "mos_score": min_mos_score or tier_def["target_mos"],
        "similarity": min_similarity or tier_def["target_similarity"],
        "naturalness": min_naturalness or tier_def["target_naturalness"],
    }

    # Score each engine
    engine_scores = {}

    for engine_name, characteristics in ENGINE_CHARACTERISTICS.items():
        score = 0.0

        # Tier match (0-40 points)
        tier_match = calculate_tier_match_score(characteristics["tier"], target_tier)
        score += tier_match * 40

        # MOS match (0-25 points)
        mos_match = calculate_metric_match(
            characteristics["mos_range"], target_metrics["mos_score"]
        )
        score += mos_match * 25

        # Similarity match (0-20 points)
        similarity_match = calculate_metric_match(
            characteristics["similarity_range"], target_metrics["similarity"]
        )
        score += similarity_match * 20

        # Naturalness match (0-10 points)
        naturalness_match = calculate_metric_match(
            characteristics["naturalness_range"], target_metrics["naturalness"]
        )
        score += naturalness_match * 10

        # Speed bonus (0-5 points)
        speed_score = calculate_speed_score(
            characteristics["speed"], tier_def["speed_priority"]
        )
        score += speed_score * 5

        # User preference bonus
        if user_preferences:
            if user_preferences.get("preferred_engine") == engine_name:
                score += 10  # Bonus for preferred engine

            if user_preferences.get("multilingual") and characteristics.get(
                "multilingual"
            ):
                score += 5  # Bonus for multilingual support

        engine_scores[engine_name] = score

    # Select best engine
    recommended_engine = max(engine_scores, key=engine_scores.get)
    max_score = engine_scores[recommended_engine]

    # Generate reasoning
    reasoning_parts = []
    reasoning_parts.append(f"Engine '{recommended_engine}' scored {max_score:.1f}/100")

    char = ENGINE_CHARACTERISTICS[recommended_engine]
    if char["tier"] == target_tier:
        reasoning_parts.append(
            f"Tier match: {char['tier']} matches target {target_tier}"
        )

    if char["mos_range"][0] <= target_metrics["mos_score"] <= char["mos_range"][1]:
        reasoning_parts.append("MOS score within engine's capability range")

    reasoning = ". ".join(reasoning_parts) + "."

    return {
        "recommended_engine": recommended_engine,
        "target_tier": target_tier,
        "target_metrics": target_metrics,
        "score": max_score,
        "all_scores": engine_scores,
        "reasoning": reasoning,
    }


# Example usage
if __name__ == "__main__":
    # Example 1: Standard recommendation
    print("Example 1: Standard Recommendation")
    print("-" * 60)
    result = recommend_engine_custom(target_tier="high")
    print(f"Recommended: {result['recommended_engine']}")
    print(f"Score: {result['score']:.1f}/100")
    print(f"Reasoning: {result['reasoning']}")
    print(f"All Scores: {result['all_scores']}")

    # Example 2: With specific requirements
    print("\nExample 2: With Specific Requirements")
    print("-" * 60)
    result = recommend_engine_custom(
        target_tier="ultra", min_mos_score=4.5, min_similarity=0.90
    )
    print(f"Recommended: {result['recommended_engine']}")
    print(f"Score: {result['score']:.1f}/100")

    # Example 3: With user preferences
    print("\nExample 3: With User Preferences")
    print("-" * 60)
    result = recommend_engine_custom(
        target_tier="standard",
        user_preferences={"preferred_engine": "chatterbox", "multilingual": True},
    )
    print(f"Recommended: {result['recommended_engine']}")
    print(f"Score: {result['score']:.1f}/100")
