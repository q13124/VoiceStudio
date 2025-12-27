"""
Face Enhancement Example

This example demonstrates how to enhance face quality in generated
images and videos (IDEA 66).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def enhance_face_image(image_id, enhancement_preset="portrait", multi_stage=True):
    """
    Enhance face quality in a generated image.

    Args:
        image_id: Image ID to enhance
        enhancement_preset: Enhancement preset (portrait, full_body, close_up)
        multi_stage: Apply multi-stage enhancement (default: True)

    Returns:
        FaceEnhancementResponse with enhanced image and analysis
    """
    url = f"{BASE_URL}/image/enhance-face"

    data = {
        "image_id": image_id,
        "enhancement_preset": enhancement_preset,
        "multi_stage": multi_stage,
        "face_specific": True,
    }

    print(f"Enhancing face in image: {image_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print(f"\n✅ Face enhancement complete!")

    # Show original analysis
    original = result["original_analysis"]
    print(f"\nOriginal Analysis:")
    print(f"  Resolution score: {original['resolution_score']:.1f}/10.0")
    print(f"  Artifact score: {original['artifact_score']:.1f}/10.0")
    print(f"  Alignment score: {original['alignment_score']:.1f}/10.0")
    print(f"  Realism score: {original['realism_score']:.1f}/10.0")
    print(f"  Overall quality: {original['overall_quality']:.1f}/10.0")

    # Show enhanced analysis if available
    if result.get("enhanced_analysis"):
        enhanced = result["enhanced_analysis"]
        print(f"\nEnhanced Analysis:")
        print(f"  Resolution score: {enhanced['resolution_score']:.1f}/10.0")
        print(f"  Artifact score: {enhanced['artifact_score']:.1f}/10.0")
        print(f"  Alignment score: {enhanced['alignment_score']:.1f}/10.0")
        print(f"  Realism score: {enhanced['realism_score']:.1f}/10.0")
        print(f"  Overall quality: {enhanced['overall_quality']:.1f}/10.0")
        print(f"\nQuality improvement: {result['quality_improvement']:.2%}")

    # Show recommendations
    if original.get("recommendations"):
        print(f"\nRecommendations:")
        for rec in original["recommendations"]:
            print(f"  - {rec}")

    if result.get("enhanced_image_id"):
        print(f"\nEnhanced image ID: {result['enhanced_image_id']}")
        print(f"Enhanced image URL: {result['enhanced_image_url']}")

    return result


def enhance_face_video(video_id, enhancement_preset="portrait"):
    """
    Enhance face quality in a generated video.

    Args:
        video_id: Video ID to enhance
        enhancement_preset: Enhancement preset
    """
    url = f"{BASE_URL}/image/enhance-face"

    data = {
        "video_id": video_id,
        "enhancement_preset": enhancement_preset,
        "multi_stage": True,
        "face_specific": True,
    }

    print(f"Enhancing face in video: {video_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()

    result = response.json()

    print(f"\n✅ Video face enhancement complete!")
    if result.get("enhanced_video_id"):
        print(f"Enhanced video URL: {result['enhanced_video_url']}")

    return result


if __name__ == "__main__":
    # Example usage for image
    image_id = "image-123"
    result = enhance_face_image(image_id, enhancement_preset="portrait")

    # Example usage for video
    video_id = "video-123"
    video_result = enhance_face_video(video_id, enhancement_preset="portrait")

    print(f"\nDownload enhanced image: {result['enhanced_image_url']}")
