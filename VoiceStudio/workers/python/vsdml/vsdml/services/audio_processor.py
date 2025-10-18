"""
Audio processing service with robust input normalization and diarization.

This module handles audio input normalization, transcription, and speaker diarization
with proper error handling and path validation.
"""

import os
import logging
from typing import Union, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio processing with robust input normalization and diarization."""
    
    def __init__(self, diarize_model=None):
        """Initialize the audio processor.
        
        Args:
            diarize_model: Optional diarization model instance
        """
        self.diarize_model = diarize_model
    
    def process_audio_batch(
        self,
        args: dict,
        min_speakers: int = 1,
        max_speakers: int = 10,
        **diarizer_kwargs
    ) -> List[dict]:
        """
        Process a batch of audio inputs with normalization and optional diarization.
        
        Args:
            args: Dictionary containing 'audio' key with input(s)
            min_speakers: Minimum number of speakers for diarization
            max_speakers: Maximum number of speakers for diarization
            **diarizer_kwargs: Additional arguments for diarization model
            
        Returns:
            List of processed results preserving input order
        """
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

        # Process each audio input (transcription, etc.)
        # This is where you'd do your usual loading/transcription into results
        results = []
        for i, audio_input in enumerate(inp_list):
            try:
                # Placeholder for actual transcription logic
                # Replace this with your transcription implementation
                result = self._transcribe_audio(audio_input, audio_paths[i])
                results.append(result)
            except Exception as e:
                logger.error(f"Transcription failed for input {i}: {e}")
                # Create empty result to preserve order
                results.append({
                    'index': i,
                    'audio_path': audio_paths[i],
                    'error': str(e),
                    'transcription': None,
                    'diarization': None
                })

        # 2) Diarization section (robust path selection + checks)
        for i, result in enumerate(results):
            audio_for_diar = audio_paths[i] if i < len(audio_paths) else None

            # Validate: must be a string path and exist
            if isinstance(audio_for_diar, str) and os.path.exists(audio_for_diar):
                try:
                    if self.diarize_model:
                        diarize_result = self.diarize_model(
                            audio_for_diar,
                            min_speakers=min_speakers,
                            max_speakers=max_speakers,
                            **diarizer_kwargs
                        )
                        # Merge diarization into result
                        result['diarization'] = diarize_result
                        logger.info(f"Successfully diarized audio: {audio_for_diar}")
                    else:
                        logger.warning("No diarization model available")
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

        return results
    
    def _transcribe_audio(self, audio_input: Any, audio_path: Optional[str]) -> dict:
        """
        Placeholder for transcription logic.
        
        Replace this method with your actual transcription implementation.
        
        Args:
            audio_input: The audio input (path, bytes, or other)
            audio_path: Absolute path if input is a file
            
        Returns:
            Dictionary containing transcription results
        """
        # This is a placeholder - replace with your actual transcription logic
        return {
            'audio_path': audio_path,
            'transcription': f"Transcription for {audio_input}",
            'diarization': None,
            'error': None
        }
    
    def validate_audio_path(self, path: str) -> bool:
        """
        Validate that an audio file path exists and is readable.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        try:
            return isinstance(path, str) and os.path.exists(path) and os.path.isfile(path)
        except Exception:
            return False
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get information about an audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio file information
        """
        try:
            if not self.validate_audio_path(audio_path):
                return {'error': 'Invalid audio path'}
                
            stat = os.stat(audio_path)
            return {
                'path': audio_path,
                'size_bytes': stat.st_size,
                'exists': True,
                'error': None
            }
        except Exception as e:
            return {
                'path': audio_path,
                'size_bytes': 0,
                'exists': False,
                'error': str(e)
            }


# Example usage function
def process_audio_with_diarization(
    audio_inputs: Union[str, List[str], bytes, List[bytes]],
    diarize_model=None,
    min_speakers: int = 1,
    max_speakers: int = 10,
    **kwargs
) -> List[dict]:
    """
    Convenience function to process audio inputs with diarization.
    
    Args:
        audio_inputs: Single audio input or list of inputs
        diarize_model: Optional diarization model
        min_speakers: Minimum speakers for diarization
        max_speakers: Maximum speakers for diarization
        **kwargs: Additional arguments
        
    Returns:
        List of processed results
    """
    processor = AudioProcessor(diarize_model)
    args = {'audio': audio_inputs}
    return processor.process_audio_batch(
        args,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        **kwargs
    )
