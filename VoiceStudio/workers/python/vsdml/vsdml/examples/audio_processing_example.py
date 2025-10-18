#!/usr/bin/env python3
"""
Example script demonstrating audio processing with diarization.

This script shows how to use the AudioProcessor class to handle audio inputs
with robust path normalization and speaker diarization.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the services
sys.path.append(str(Path(__file__).parent.parent))

from services.audio_processor import AudioProcessor, process_audio_with_diarization

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_single_file():
    """Example: Process a single audio file."""
    print("=== Single File Example ===")
    
    # Example audio file path (replace with your actual file)
    audio_file = "/path/to/your/audio.wav"
    
    # Check if file exists (for demo purposes)
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        print("Please update the audio_file path to point to an actual audio file.")
        return
    
    # Process with diarization
    results = process_audio_with_diarization(
        audio_inputs=audio_file,
        diarize_model=None,  # Replace with your diarization model
        min_speakers=2,
        max_speakers=4
    )
    
    print(f"Processed {len(results)} audio file(s)")
    for i, result in enumerate(results):
        print(f"Result {i}: {result}")


def example_multiple_files():
    """Example: Process multiple audio files."""
    print("\n=== Multiple Files Example ===")
    
    # Example audio files (replace with your actual files)
    audio_files = [
        "/path/to/audio1.wav",
        "/path/to/audio2.mp3", 
        "/path/to/audio3.m4a"
    ]
    
    # Check which files exist
    existing_files = [f for f in audio_files if os.path.exists(f)]
    if not existing_files:
        print("No audio files found. Please update the audio_files list with actual file paths.")
        return
    
    print(f"Found {len(existing_files)} existing audio files")
    
    # Process with diarization
    processor = AudioProcessor(diarize_model=None)  # Replace with your diarization model
    args = {'audio': existing_files}
    
    results = processor.process_audio_batch(
        args,
        min_speakers=1,
        max_speakers=6
    )
    
    print(f"Processed {len(results)} audio file(s)")
    for i, result in enumerate(results):
        print(f"Result {i}:")
        print(f"  Audio path: {result.get('audio_path', 'N/A')}")
        print(f"  Transcription: {result.get('transcription', 'N/A')}")
        print(f"  Diarization: {result.get('diarization', 'N/A')}")
        print(f"  Error: {result.get('error', 'None')}")


def example_mixed_inputs():
    """Example: Process mixed input types (files and bytes)."""
    print("\n=== Mixed Input Types Example ===")
    
    # This example shows the input normalization in action
    mixed_inputs = [
        "/path/to/audio1.wav",  # String path
        Path("/path/to/audio2.mp3"),  # PathLike object
        b"fake_audio_bytes",  # Bytes (for demonstration)
    ]
    
    # Only process actual file paths for this demo
    file_inputs = [inp for inp in mixed_inputs if isinstance(inp, (str, Path)) and os.path.exists(inp)]
    
    if not file_inputs:
        print("No valid file paths found. This example shows the input normalization structure.")
        print("The AudioProcessor can handle:")
        print("- String paths: '/path/to/audio.wav'")
        print("- PathLike objects: pathlib.Path('/path/to/audio.wav')")
        print("- Bytes: b'audio_data_bytes'")
        print("- Mixed lists of the above types")
        return
    
    processor = AudioProcessor()
    args = {'audio': file_inputs}
    
    results = processor.process_audio_batch(args)
    
    print(f"Processed {len(results)} inputs")
    for i, result in enumerate(results):
        print(f"Input {i}: {result}")


def example_with_custom_diarization():
    """Example: Using custom diarization parameters."""
    print("\n=== Custom Diarization Example ===")
    
    # This shows how to pass custom parameters to the diarization model
    audio_file = "/path/to/your/audio.wav"
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        print("Please update the audio_file path to point to an actual audio file.")
        return
    
    # Example with custom diarization parameters
    results = process_audio_with_diarization(
        audio_inputs=audio_file,
        diarize_model=None,  # Replace with your diarization model
        min_speakers=2,
        max_speakers=8,
        # Additional custom parameters would go here
        # clustering_threshold=0.7,
        # embedding_model="speechbrain/spkrec-ecapa-voxceleb",
        # etc.
    )
    
    print(f"Processed with custom parameters: {len(results)} results")


def main():
    """Run all examples."""
    print("Audio Processing Examples")
    print("=" * 50)
    
    # Run examples
    example_single_file()
    example_multiple_files()
    example_mixed_inputs()
    example_with_custom_diarization()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo use this in your own code:")
    print("1. Import: from services.audio_processor import AudioProcessor, process_audio_with_diarization")
    print("2. Provide your diarization model to the processor")
    print("3. Call the appropriate method with your audio inputs")


if __name__ == "__main__":
    main()