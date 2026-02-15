"""
A/B Testing Example

This example demonstrates how to use the A/B testing endpoint
to compare two different synthesis configurations side-by-side (IDEA 46).
"""


import requests

BASE_URL = "http://localhost:8000/api"


def run_ab_test(profile_id, text, engine_a="xtts", engine_b="tortoise",
                emotion_a=None, emotion_b=None, enhance_quality_a=True, enhance_quality_b=True):
    """
    Run an A/B test comparing two synthesis configurations.

    Args:
        profile_id: Voice profile ID to use
        text: Text to synthesize for comparison
        engine_a: Engine for sample A (default: "xtts")
        engine_b: Engine for sample B (default: "tortoise")
        emotion_a: Optional emotion for sample A
        emotion_b: Optional emotion for sample B
        enhance_quality_a: Enable quality enhancement for sample A (default: True)
        enhance_quality_b: Enable quality enhancement for sample B (default: True)

    Returns:
        ABTestResponse with comparison results
    """
    url = f"{BASE_URL}/voice/ab-test"

    data = {
        "profile_id": profile_id,
        "text": text,
        "engine_a": engine_a,
        "engine_b": engine_b,
        "enhance_quality_a": enhance_quality_a,
        "enhance_quality_b": enhance_quality_b
    }

    if emotion_a:
        data["emotion_a"] = emotion_a
    if emotion_b:
        data["emotion_b"] = emotion_b

    print(f"Running A/B test: {engine_a} vs {engine_b}...")
    print(f"Text: {text[:50]}...")

    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print("\n✅ A/B Test complete!")
    print(f"\n📊 Sample A Results ({engine_a}):")
    print(f"  MOS Score: {result['sample_a']['quality_metrics']['mos_score']:.2f}")
    print(f"  Similarity: {result['sample_a']['quality_metrics']['similarity']:.3f}")
    print(f"  Naturalness: {result['sample_a']['quality_metrics']['naturalness']:.3f}")
    print(f"  SNR: {result['sample_a']['quality_metrics']['snr_db']:.1f} dB")
    print(f"  Audio URL: {result['sample_a']['audio_url']}")

    print(f"\n📊 Sample B Results ({engine_b}):")
    print(f"  MOS Score: {result['sample_b']['quality_metrics']['mos_score']:.2f}")
    print(f"  Similarity: {result['sample_b']['quality_metrics']['similarity']:.3f}")
    print(f"  Naturalness: {result['sample_b']['quality_metrics']['naturalness']:.3f}")
    print(f"  SNR: {result['sample_b']['quality_metrics']['snr_db']:.1f} dB")
    print(f"  Audio URL: {result['sample_b']['audio_url']}")

    print("\n🏆 Comparison:")
    if result.get('comparison'):
        comp = result['comparison']
        if 'overall_winner' in comp:
            winner = comp['overall_winner']
            print(f"  Overall Winner: Sample {winner}")

        if 'mos_winner' in comp:
            print(f"  MOS Winner: Sample {comp['mos_winner']}")
        if 'similarity_winner' in comp:
            print(f"  Similarity Winner: Sample {comp['similarity_winner']}")
        if 'naturalness_winner' in comp:
            print(f"  Naturalness Winner: Sample {comp['naturalness_winner']}")

    return result


def compare_engines(profile_id, text, engines=None):
    """
    Compare multiple engines by running A/B tests between pairs.

    Args:
        profile_id: Voice profile ID
        text: Text to synthesize
        engines: List of engines to compare

    Returns:
        Dictionary of comparison results
    """
    if engines is None:
        engines = ["xtts", "chatterbox", "tortoise"]
    results = {}

    # Compare each pair of engines
    for i in range(len(engines)):
        for j in range(i + 1, len(engines)):
            engine_a = engines[i]
            engine_b = engines[j]

            print(f"\n{'='*60}")
            print(f"Comparing {engine_a} vs {engine_b}")
            print(f"{'='*60}")

            result = run_ab_test(profile_id, text, engine_a, engine_b)
            results[f"{engine_a}_vs_{engine_b}"] = result

    return results


# Example usage
if __name__ == "__main__":
    # Example 1: Simple A/B test
    print("Example 1: Simple A/B Test")
    print("-" * 60)
    result = run_ab_test(
        profile_id="profile-123",
        text="Hello, this is a test of voice synthesis quality.",
        engine_a="xtts",
        engine_b="tortoise"
    )

    # Example 2: Compare with different emotions
    print("\n\nExample 2: A/B Test with Emotions")
    print("-" * 60)
    result = run_ab_test(
        profile_id="profile-123",
        text="I'm feeling excited about this new feature!",
        engine_a="chatterbox",
        engine_b="chatterbox",
        emotion_a="happy",
        emotion_b="neutral"
    )

    # Example 3: Compare multiple engines
    print("\n\nExample 3: Compare Multiple Engines")
    print("-" * 60)
    comparisons = compare_engines(
        profile_id="profile-123",
        text="This is a comprehensive engine comparison test.",
        engines=["xtts", "chatterbox", "tortoise"]
    )

