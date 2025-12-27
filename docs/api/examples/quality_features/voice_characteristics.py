"""
Voice Characteristic Analysis Example

This example demonstrates how to analyze voice characteristics for
preservation and enhancement (IDEA 64).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def analyze_voice_characteristics(audio_id, reference_audio_id=None, include_prosody=True):
    """
    Analyze voice characteristics (pitch, formants, timbre, prosody).
    
    Args:
        audio_id: Audio ID to analyze
        reference_audio_id: Reference audio for comparison (optional)
        include_prosody: Include prosody analysis (default: True)
    
    Returns:
        VoiceCharacteristicAnalysisResponse with characteristic data
    """
    url = f"{BASE_URL}/voice/analyze-characteristics"
    
    data = {
        "audio_id": audio_id,
        "reference_audio_id": reference_audio_id,
        "include_pitch": True,
        "include_formants": True,
        "include_timbre": True,
        "include_prosody": include_prosody
    }
    
    print(f"Analyzing voice characteristics for audio: {audio_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Analysis complete!")
    
    # Show characteristics
    chars = result['characteristics']
    print(f"\nVoice Characteristics:")
    
    if chars.get('pitch_mean') is not None:
        print(f"  Pitch: mean={chars['pitch_mean']:.1f}Hz, std={chars['pitch_std']:.1f}Hz")
    
    if chars.get('formants'):
        formants = chars['formants']
        print(f"  Formants: F1={formants[0]:.1f}Hz, F2={formants[1]:.1f}Hz, F3={formants[2]:.1f}Hz")
    
    if chars.get('spectral_centroid') is not None:
        print(f"  Spectral centroid: {chars['spectral_centroid']:.1f}Hz")
    
    if chars.get('spectral_rolloff') is not None:
        print(f"  Spectral rolloff: {chars['spectral_rolloff']:.1f}Hz")
    
    # Show comparison with reference if provided
    if result.get('reference_characteristics'):
        print(f"\nReference Comparison:")
        print(f"  Similarity score: {result['similarity_score']:.2%}")
        print(f"  Preservation score: {result['preservation_score']:.2%}")
        
        ref_chars = result['reference_characteristics']
        if ref_chars.get('pitch_mean') is not None and chars.get('pitch_mean') is not None:
            pitch_diff = abs(chars['pitch_mean'] - ref_chars['pitch_mean'])
            print(f"  Pitch difference: {pitch_diff:.1f}Hz")
    
    # Show recommendations
    if result.get('recommendations'):
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  - {rec}")
    
    return result


def compare_voice_characteristics(audio_id, reference_audio_id):
    """
    Compare voice characteristics between two audio files.
    """
    print(f"Comparing audio {audio_id} with reference {reference_audio_id}...")
    result = analyze_voice_characteristics(audio_id, reference_audio_id)
    
    if result['similarity_score'] < 0.7:
        print("\n⚠️  Warning: Low similarity detected. Consider:")
        print("  - Using prosody control to match intonation")
        print("  - Adjusting synthesis parameters")
    
    return result


if __name__ == "__main__":
    # Example usage
    audio_id = "audio-123"
    reference_audio_id = "reference-123"
    
    # Analyze without reference
    result = analyze_voice_characteristics(audio_id)
    
    # Compare with reference
    if reference_audio_id:
        compare_result = compare_voice_characteristics(audio_id, reference_audio_id)

