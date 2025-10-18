#!/usr/bin/env python3
"""
Simple test script for audio processing functionality.

This script demonstrates the exact code you were trying to run in PowerShell,
now properly formatted as a Python script.
"""

import os
import logging
from typing import Union, List, Optional, Any
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_audio_processing_code():
    """
    This function contains the exact code you were trying to run in PowerShell,
    now properly formatted as Python code.
    """
    
    # Mock data for demonstration
    # In real usage, these would come from your actual application
    args = {
        "audio": "/path/to/test/audio.wav"  # Replace with actual audio file path
    }
    
    # Mock diarization model (replace with your actual model)
    diarize_model = None  # Replace with your diarization model instance
    min_speakers = 2
    max_speakers = 4
    
    # Mock results list (in real usage, this would come from transcription)
    results = [
        {"transcription": "Sample transcription 1", "audio_path": None},
        {"transcription": "Sample transcription 2", "audio_path": None},
    ]
    
    print("Testing audio processing code...")
    print(f"Input args: {args}")
    
    # 1) Normalize inputs and capture original paths up front
    inp_audio = args.pop("audio")
    if isinstance(inp_audio, (str, bytes, os.PathLike)):
        inp_list = [inp_audio]
    else:
        inp_list = list(inp_audio)

    # keep absolute file paths (None for non-file inputs)
    audio_paths = []
    for a in inp_list:
        if isinstance(a, (str, bytes, os.PathLike)):
            p = os.fspath(a)
            audio_paths.append(os.path.abspath(p))
        else:
            audio_paths.append(None)

    print(f"Normalized input list: {inp_list}")
    print(f"Audio paths: {audio_paths}")

    # 2) Diarization section (robust path selection + checks)
    for i, result in enumerate(results):
        audio_for_diar = audio_paths[i] if i < len(audio_paths) else None

        # Validate: must be a string path and exist
        if isinstance(audio_for_diar, str) and os.path.exists(audio_for_diar):
            try:
                if diarize_model:
                    diarize_result = diarize_model(
                        audio_for_diar,
                        min_speakers=min_speakers,
                        max_speakers=max_speakers,
                        # ... other diarizer kwargs ...
                    )
                    # merge diarization into `result` as before
                    result['diarization'] = diarize_result
                    logger.info(f"Successfully diarized audio: {audio_for_diar}")
                else:
                    logger.warning("No diarization model provided")
                    result['diarization'] = None
            except Exception as e:
                logger.warning(f"Diarization failed for {audio_for_diar}: {e}")
                result['diarization'] = None
                continue
        else:
            logger.warning(
                "Skipping diarization (could not locate audio for session): %r",
                audio_for_diar,
            )
            result['diarization'] = None
            continue

    print(f"Final results: {results}")
    return results


def test_with_real_file():
    """
    Test with an actual audio file if it exists.
    """
    # Try to find a test audio file
    test_files = [
        "test.wav",
        "sample.mp3", 
        "audio.wav",
        "/path/to/your/audio.wav"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nTesting with real file: {test_file}")
            
            args = {"audio": test_file}
            results = [{"transcription": f"Transcription for {test_file}", "audio_path": None}]
            
            # Run the same logic
            inp_audio = args.pop("audio")
            if isinstance(inp_audio, (str, bytes, os.PathLike)):
                inp_list = [inp_audio]
            else:
                inp_list = list(inp_audio)

            audio_paths = []
            for a in inp_list:
                if isinstance(a, (str, bytes, os.PathLike)):
                    p = os.fspath(a)
                    audio_paths.append(os.path.abspath(p))
                else:
                    audio_paths.append(None)

            print(f"Found audio file: {audio_paths[0]}")
            print(f"File exists: {os.path.exists(audio_paths[0])}")
            return
    
    print("\nNo test audio files found. Please add an audio file to test with.")


def main():
    """Run the test."""
    print("Audio Processing Test Script")
    print("=" * 40)
    
    try:
        # Test the basic functionality
        test_audio_processing_code()
        
        # Test with real file if available
        test_with_real_file()
        
        print("\nTest completed successfully!")
        print("\nTo run this script:")
        print("1. Save this as a .py file")
        print("2. Run: python test_audio_processing.py")
        print("3. Or run: python3 test_audio_processing.py")
        
    except Exception as e:
        print(f"Error during test: {e}")
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    main()
