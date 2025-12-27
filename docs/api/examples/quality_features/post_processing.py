"""
Post-Processing Pipeline Example

This example demonstrates how to use the multi-stage post-processing
enhancement pipeline (IDEA 70).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def post_process_audio(audio_id, enhancement_stages=None, preview=False):
    """
    Apply multi-stage post-processing enhancement to audio.
    
    Args:
        audio_id: Audio ID to process
        enhancement_stages: List of stages (default: ["denoise", "normalize", "enhance", "repair"])
        preview: Preview mode without applying (default: False)
    
    Returns:
        PostProcessingPipelineResponse with processed audio and stage results
    """
    url = f"{BASE_URL}/voice/post-process"
    
    data = {
        "audio_id": audio_id,
        "enhancement_stages": enhancement_stages or ["denoise", "normalize", "enhance", "repair"],
        "optimize_order": True,
        "preview": preview
    }
    
    mode = "Preview" if preview else "Processing"
    print(f"{mode} audio through post-processing pipeline: {audio_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Post-processing {'preview' if preview else 'complete'}!")
    
    # Show stages applied
    print(f"\nStages Applied ({len(result['stages_applied'])}):")
    for stage in result['stages_applied']:
        improvement = stage['improvement']
        improvement_sign = "+" if improvement >= 0 else ""
        print(f"  - {stage['stage_name']}: "
              f"Quality {stage['quality_before']:.3f} → {stage['quality_after']:.3f} "
              f"({improvement_sign}{improvement:.3f})")
    
    print(f"\nTotal quality improvement: {result['total_quality_improvement']:.2%}")
    
    if not preview and result.get('processed_audio_id'):
        print(f"\nProcessed audio ID: {result['processed_audio_id']}")
        print(f"Processed audio URL: {result['processed_audio_url']}")
    
    return result


def post_process_image(image_id, enhancement_stages=None):
    """
    Apply multi-stage post-processing enhancement to image.
    """
    url = f"{BASE_URL}/voice/post-process"
    
    data = {
        "image_id": image_id,
        "enhancement_stages": enhancement_stages or ["upscale", "enhance", "denoise"],
        "optimize_order": True,
        "preview": False
    }
    
    print(f"Processing image through post-processing pipeline: {image_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Image post-processing complete!")
    print(f"Processed image URL: {result['processed_image_url']}")
    
    return result


def post_process_video(video_id, enhancement_stages=None):
    """
    Apply multi-stage post-processing enhancement to video.
    """
    url = f"{BASE_URL}/voice/post-process"
    
    data = {
        "video_id": video_id,
        "enhancement_stages": enhancement_stages or ["upscale", "temporal_smoothing", "enhance"],
        "optimize_order": True,
        "preview": False
    }
    
    print(f"Processing video through post-processing pipeline: {video_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Video post-processing complete!")
    print(f"Processed video URL: {result['processed_video_url']}")
    
    return result


def post_processing_workflow(audio_id):
    """
    Complete workflow: Preview first, then apply.
    """
    # Step 1: Preview stages
    print("=== Step 1: Preview Post-Processing Stages ===")
    preview_result = post_process_audio(audio_id, preview=True)
    
    # Step 2: Apply if improvement is significant
    if preview_result['total_quality_improvement'] > 0.05:
        print(f"\n=== Step 2: Apply Post-Processing (Improvement: {preview_result['total_quality_improvement']:.2%}) ===")
        result = post_process_audio(audio_id, preview=False)
        return result
    else:
        print("\n⚠️  Quality improvement minimal - skipping post-processing")
        return preview_result


if __name__ == "__main__":
    # Example usage for audio
    audio_id = "audio-123"
    result = post_process_audio(audio_id, preview=False)
    
    # Example usage for image
    image_id = "image-123"
    image_result = post_process_image(image_id)
    
    # Example usage for video
    video_id = "video-123"
    video_result = post_process_video(video_id)
    
    print(f"\nDownload processed audio: {result['processed_audio_url']}")

