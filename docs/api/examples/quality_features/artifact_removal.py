"""
Artifact Removal Example

This example demonstrates how to detect and remove audio artifacts
from synthesized audio (IDEA 63).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def remove_artifacts(audio_id, artifact_types=None, preview=False):
    """
    Detect and remove audio artifacts from synthesized audio.

    Args:
        audio_id: Audio ID to process
        artifact_types: List of artifact types to check (optional)
        preview: Preview mode without applying (default: False)

    Returns:
        ArtifactRemovalResponse with detection and removal results
    """
    url = f"{BASE_URL}/voice/remove-artifacts"

    data = {
        "audio_id": audio_id,
        "artifact_types": artifact_types or ["clicks", "pops", "distortion", "glitches", "phase_issues"],
        "preview": preview,
        "repair_preset": "comprehensive"  # Options: click_removal, distortion_repair, comprehensive
    }

    print(f"Analyzing audio for artifacts: {audio_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    # Show artifacts detected
    print("\n✅ Analysis complete!")
    print(f"Artifacts detected: {len(result['artifacts_detected'])}")

    if result['artifacts_detected']:
        print("\nDetected Artifacts:")
        for artifact in result['artifacts_detected']:
            print(f"  - {artifact['artifact_type']}: "
                  f"Severity={artifact['severity']:.1f}, "
                  f"Confidence={artifact['confidence']:.2f}")
            if artifact.get('location') is not None:
                print(f"    Location: {artifact['location']:.2f}s")
    else:
        print("  No artifacts detected!")

    # Show artifacts removed (if not preview)
    if not preview and result.get('artifacts_removed'):
        print("\nArtifacts Removed:")
        for artifact_type in result['artifacts_removed']:
            print(f"  - {artifact_type}")

        print(f"\nQuality improvement: {result['quality_improvement']:.2%}")
        print(f"Repaired audio ID: {result['repaired_audio_id']}")
        print(f"Repaired audio URL: {result['repaired_audio_url']}")
    elif preview:
        print("\n⚠️  Preview mode: No repairs applied")

    return result


def remove_artifacts_workflow(audio_id):
    """
    Complete workflow: Preview first, then apply if needed.
    """
    # Step 1: Preview artifacts
    print("=== Step 1: Preview Artifacts ===")
    preview_result = remove_artifacts(audio_id, preview=True)

    # Step 2: Apply removal if artifacts detected
    if preview_result['artifacts_detected']:
        print("\n=== Step 2: Remove Artifacts ===")
        repair_result = remove_artifacts(audio_id, preview=False)

        return repair_result
    else:
        print("\n✅ No artifacts detected - audio is clean!")
        return preview_result


if __name__ == "__main__":
    # Example usage
    audio_id = "audio-123"

    # Preview mode first
    result = remove_artifacts(audio_id, preview=True)

    # If artifacts found, apply removal
    if result['artifacts_detected']:
        repair_result = remove_artifacts(audio_id, preview=False)
        print(f"\nDownload repaired audio: {repair_result['repaired_audio_url']}")

