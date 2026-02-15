"""
Prosody Control Example

This example demonstrates how to control prosody and intonation
for natural speech synthesis (IDEA 65).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def control_prosody(audio_id, intonation_pattern="rising", prosody_template=None):
    """
    Apply prosody control to audio for natural speech synthesis.

    Args:
        audio_id: Audio ID to process
        intonation_pattern: Intonation pattern (rising, falling, flat)
        prosody_template: Prosody template name (optional)

    Returns:
        ProsodyControlResponse with processed audio
    """
    url = f"{BASE_URL}/voice/prosody-control"

    data = {
        "audio_id": audio_id,
        "intonation_pattern": intonation_pattern,  # Options: rising, falling, flat
        "prosody_template": prosody_template,
        "stress_markers": [
            {"word": "hello", "stress": "primary"},
            {"word": "world", "stress": "secondary"}
        ]
    }

    print(f"Applying prosody control to audio: {audio_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print("\n✅ Prosody control applied!")
    print(f"Processed audio ID: {result['processed_audio_id']}")
    print(f"Processed audio URL: {result['processed_audio_url']}")
    print(f"Quality improvement: {result['quality_improvement']:.2%}")

    # Show what was applied
    print("\nProsody Applied:")
    for key, value in result['prosody_applied'].items():
        print(f"  - {key}: {value}")

    return result


def control_prosody_with_contour(audio_id, pitch_contour):
    """
    Apply prosody control with custom pitch contour.

    Args:
        audio_id: Audio ID to process
        pitch_contour: List of pitch values over time
    """
    url = f"{BASE_URL}/voice/prosody-control"

    data = {
        "audio_id": audio_id,
        "pitch_contour": pitch_contour,
        "rhythm_adjustments": {
            "tempo": 1.0,
            "beat_strength": 0.8
        }
    }

    print(f"Applying custom prosody contour to audio: {audio_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print("\n✅ Custom prosody applied!")
    return result


def prosody_control_workflow(audio_id):
    """
    Complete workflow: Apply prosody control for question intonation.
    """
    # Apply rising intonation for questions
    print("=== Applying Prosody Control (Question Intonation) ===")
    result = control_prosody(
        audio_id=audio_id,
        intonation_pattern="rising"
    )

    return result


if __name__ == "__main__":
    # Example usage
    audio_id = "audio-123"

    # Apply rising intonation
    result = control_prosody(audio_id, intonation_pattern="rising")

    # Apply custom pitch contour
    pitch_contour = [200, 220, 240, 250, 240, 220, 200]  # Hz values
    custom_result = control_prosody_with_contour(audio_id, pitch_contour)

    print(f"\nDownload processed audio: {result['processed_audio_url']}")

