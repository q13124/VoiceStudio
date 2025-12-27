"""
Multi-Pass Synthesis Example

This example demonstrates how to use the multi-pass synthesis endpoint
to generate high-quality voice synthesis with quality refinement (IDEA 61).
"""

import requests
import time

BASE_URL = "http://localhost:8000/api"


def synthesize_multipass(profile_id, text, engine="chatterbox", max_passes=3):
    """
    Perform multi-pass synthesis with quality refinement.
    
    Args:
        profile_id: Voice profile ID
        text: Text to synthesize
        engine: Engine name (default: "chatterbox")
        max_passes: Maximum number of passes (default: 3)
    
    Returns:
        MultiPassSynthesisResponse with best quality audio
    """
    url = f"{BASE_URL}/voice/synthesize/multipass"
    
    data = {
        "engine": engine,
        "profile_id": profile_id,
        "text": text,
        "language": "en",
        "max_passes": max_passes,
        "min_quality_improvement": 0.02,
        "pass_preset": "naturalness_focus",  # Options: naturalness_focus, similarity_focus, artifact_focus
        "adaptive": True
    }
    
    print(f"Starting multi-pass synthesis with {max_passes} passes...")
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Synthesis complete!")
    print(f"Best pass: {result['best_pass']}/{result['passes_completed']}")
    print(f"Quality score: {result['quality_score']:.3f}")
    print(f"Audio ID: {result['audio_id']}")
    print(f"Audio URL: {result['audio_url']}")
    
    # Show improvement tracking
    print("\nImprovement per pass:")
    for i, improvement in enumerate(result['improvement_tracking'], 1):
        if improvement > 0:
            print(f"  Pass {i}: +{improvement:.4f}")
    
    # Show all passes for comparison
    print("\nAll passes:")
    for pass_result in result['passes']:
        print(f"  Pass {pass_result['pass_number']}: "
              f"Quality={pass_result['quality_score']:.3f}, "
              f"MOS={pass_result['quality_metrics'].get('mos_score', 'N/A')}")
    
    return result


def synthesize_multipass_workflow(profile_id, text):
    """
    Complete workflow using multi-pass synthesis with adaptive stopping.
    """
    # Step 1: Multi-pass synthesis with naturalness focus
    print("=== Step 1: Multi-Pass Synthesis (Naturalness Focus) ===")
    result = synthesize_multipass(
        profile_id=profile_id,
        text=text,
        engine="chatterbox",
        max_passes=5,
        pass_preset="naturalness_focus"
    )
    
    audio_id = result['audio_id']
    
    # Step 2: Analyze characteristics
    print("\n=== Step 2: Analyze Voice Characteristics ===")
    from voice_characteristics import analyze_voice_characteristics
    characteristics = analyze_voice_characteristics(audio_id)
    
    # Step 3: Apply post-processing if needed
    if result['quality_score'] < 0.8:
        print("\n=== Step 3: Post-Processing Pipeline ===")
        from post_processing import post_process_audio
        post_process_audio(audio_id)
    
    return result


if __name__ == "__main__":
    # Example usage
    profile_id = "profile-123"
    text = "Hello, this is a test of multi-pass synthesis for improved quality."
    
    result = synthesize_multipass(profile_id, text, max_passes=3)
    
    # Access the best quality audio
    best_audio_url = result['audio_url']
    print(f"\nDownload best quality audio: {best_audio_url}")

