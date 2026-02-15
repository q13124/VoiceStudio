"""
Temporal Consistency Example

This example demonstrates how to enhance temporal consistency
for video deepfakes (IDEA 67).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def enhance_temporal_consistency(video_id, smoothing_strength=0.5, detect_artifacts=True):
    """
    Enhance temporal consistency in video deepfakes.

    Args:
        video_id: Video ID to process
        smoothing_strength: Temporal smoothing strength (0.0-1.0)
        detect_artifacts: Detect temporal artifacts (default: True)

    Returns:
        TemporalConsistencyResponse with processed video and analysis
    """
    url = f"{BASE_URL}/video/temporal-consistency"

    data = {
        "video_id": video_id,
        "smoothing_strength": smoothing_strength,
        "motion_consistency": True,
        "detect_artifacts": detect_artifacts
    }

    print(f"Enhancing temporal consistency for video: {video_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print("\n✅ Temporal consistency enhancement complete!")

    # Show original analysis
    original = result['original_analysis']
    print("\nOriginal Analysis:")
    print(f"  Frame stability: {original['frame_stability']:.2%}")
    print(f"  Motion smoothness: {original['motion_smoothness']:.2%}")
    print(f"  Flicker score: {original['flicker_score']:.2%}")
    print(f"  Jitter score: {original['jitter_score']:.2%}")
    print(f"  Overall consistency: {original['overall_consistency']:.2%}")

    if original.get('artifacts_detected'):
        print(f"  Artifacts detected: {', '.join(original['artifacts_detected'])}")

    # Show processed analysis if available
    if result.get('processed_analysis'):
        processed = result['processed_analysis']
        print("\nProcessed Analysis:")
        print(f"  Frame stability: {processed['frame_stability']:.2%}")
        print(f"  Motion smoothness: {processed['motion_smoothness']:.2%}")
        print(f"  Flicker score: {processed['flicker_score']:.2%}")
        print(f"  Jitter score: {processed['jitter_score']:.2%}")
        print(f"  Overall consistency: {processed['overall_consistency']:.2%}")
        print(f"\nQuality improvement: {result['quality_improvement']:.2%}")

    print(f"\nProcessed video ID: {result['processed_video_id']}")
    print(f"Processed video URL: {result['processed_video_url']}")

    return result


def enhance_temporal_consistency_workflow(video_id):
    """
    Complete workflow with adaptive smoothing strength.
    """
    # Step 1: Analyze with default smoothing
    print("=== Step 1: Analyze Temporal Consistency ===")
    result = enhance_temporal_consistency(video_id, smoothing_strength=0.3, detect_artifacts=True)

    # Step 2: Apply stronger smoothing if artifacts detected
    if result['original_analysis'].get('artifacts_detected'):
        print("\n=== Step 2: Apply Stronger Smoothing ===")
        strong_result = enhance_temporal_consistency(video_id, smoothing_strength=0.7)
        return strong_result

    return result


if __name__ == "__main__":
    # Example usage
    video_id = "video-123"

    result = enhance_temporal_consistency(
        video_id=video_id,
        smoothing_strength=0.5,
        detect_artifacts=True
    )

    print(f"\nDownload processed video: {result['processed_video_url']}")

