"""
Reference Audio Pre-Processing Example

This example demonstrates how to pre-process reference audio for optimal
voice cloning quality (IDEA 62).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def preprocess_reference_audio(
    profile_id, reference_audio_path=None, auto_enhance=True
):
    """
    Pre-process reference audio for voice cloning optimization.

    Args:
        profile_id: Voice profile ID
        reference_audio_path: Path to reference audio file (optional)
        auto_enhance: Automatically enhance reference audio (default: True)

    Returns:
        ReferenceAudioPreprocessResponse with processed audio and analysis
    """
    url = f"{BASE_URL}/profiles/{profile_id}/preprocess-reference"

    data = {
        "profile_id": profile_id,
        "reference_audio_path": reference_audio_path,
        "auto_enhance": auto_enhance,
        "select_optimal_segments": True,
        "min_segment_duration": 1.0,
        "max_segments": 5,
    }

    print(f"Pre-processing reference audio for profile: {profile_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print(f"\n✅ Pre-processing complete!")
    print(f"Processed audio ID: {result['processed_audio_id']}")
    print(f"Processed audio URL: {result['processed_audio_url']}")

    # Show original analysis
    original = result["original_analysis"]
    print(f"\nOriginal Analysis:")
    print(f"  Quality score: {original['quality_score']:.1f}/10.0")
    print(f"  Has noise: {original['has_noise']}")
    print(f"  Has clipping: {original['has_clipping']}")
    print(f"  Has distortion: {original['has_distortion']}")
    print(f"  Duration: {original['duration']:.2f}s")
    print(f"  Sample rate: {original['sample_rate']} Hz")

    if original["recommendations"]:
        print(f"\nRecommendations:")
        for rec in original["recommendations"]:
            print(f"  - {rec}")

    # Show processed analysis if available
    if result.get("processed_analysis"):
        processed = result["processed_analysis"]
        print(f"\nProcessed Analysis:")
        print(f"  Quality score: {processed['quality_score']:.1f}/10.0")
        print(f"  Quality improvement: {result['quality_improvement']:.2%}")

    # Show improvements applied
    if result.get("improvements_applied"):
        print(f"\nImprovements Applied:")
        for improvement in result["improvements_applied"]:
            print(f"  - {improvement}")

    return result


if __name__ == "__main__":
    # Example usage
    profile_id = "profile-123"

    result = preprocess_reference_audio(profile_id=profile_id, auto_enhance=True)

    # Use processed audio for better cloning
    processed_audio_url = result["processed_audio_url"]
    print(f"\nUse processed audio for cloning: {processed_audio_url}")
