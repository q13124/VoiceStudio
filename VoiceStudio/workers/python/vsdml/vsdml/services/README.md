# Audio Processing Service

This module provides robust audio input normalization and speaker diarization capabilities with comprehensive error handling and path validation.

## Features

- **Robust Input Normalization**: Handles various audio input types (file paths, bytes, PathLike objects)
- **Path Validation**: Validates audio file paths and existence before processing
- **Speaker Diarization**: Integrates with diarization models with proper error handling
- **Input Order Preservation**: Maintains the order of inputs throughout processing
- **Comprehensive Error Handling**: Graceful handling of invalid inputs and processing failures
- **Flexible Configuration**: Supports custom diarization parameters

## Quick Start

### Basic Usage

```python
from services.audio_processor import AudioProcessor, process_audio_with_diarization

# Simple single file processing
results = process_audio_with_diarization(
    audio_inputs="/path/to/audio.wav",
    diarize_model=your_diarization_model,
    min_speakers=2,
    max_speakers=4
)
```

### Multiple Files

```python
# Process multiple audio files
audio_files = ["/path/audio1.wav", "/path/audio2.mp3", "/path/audio3.m4a"]
results = process_audio_with_diarization(
    audio_inputs=audio_files,
    diarize_model=your_diarization_model
)
```

### Using the AudioProcessor Class

```python
processor = AudioProcessor(diarize_model=your_diarization_model)
args = {'audio': audio_files}
results = processor.process_audio_batch(
    args,
    min_speakers=1,
    max_speakers=6
)
```

## Input Types Supported

The audio processor accepts various input types:

- **String paths**: `"/path/to/audio.wav"`
- **PathLike objects**: `pathlib.Path("/path/to/audio.wav")`
- **Bytes**: `b"audio_data_bytes"`
- **Mixed lists**: `["/path/audio.wav", b"bytes", Path("/path/audio2.mp3")]`

## Output Format

Each processed result contains:

```python
{
    'audio_path': '/absolute/path/to/audio.wav',  # Absolute path or None
    'transcription': 'Transcribed text...',        # Transcription result
    'diarization': {                              # Diarization result or None
        'speakers': [
            {'start': 0.0, 'end': 5.0, 'speaker': 'Speaker_0'},
            {'start': 5.0, 'end': 10.0, 'speaker': 'Speaker_1'},
        ],
        'audio_path': '/absolute/path/to/audio.wav',
        'duration': 10.0
    },
    'error': None  # Error message if processing failed
}
```

## Diarization Integration

The processor validates audio paths before attempting diarization:

- ✅ **Valid file paths**: Diarization is attempted
- ❌ **Invalid/missing paths**: Diarization is skipped with warning
- ❌ **Bytes/non-file inputs**: Diarization is skipped (no file path available)

### Diarization Model Requirements

Your diarization model should accept:
- `audio_path`: Path to audio file
- `min_speakers`: Minimum number of speakers
- `max_speakers`: Maximum number of speakers
- Additional keyword arguments

Example diarization model interface:
```python
def diarization_model(audio_path, min_speakers=1, max_speakers=10, **kwargs):
    # Your diarization logic here
    return {
        'speakers': [...],  # List of speaker segments
        'audio_path': audio_path,
        'duration': total_duration
    }
```

## Error Handling

The processor includes comprehensive error handling:

- **Invalid paths**: Logged as warnings, diarization skipped
- **Processing failures**: Captured in result['error']
- **Input normalization errors**: Gracefully handled
- **Diarization failures**: Logged as warnings, processing continues

## Logging

The module uses Python's standard logging. Configure logging level to control verbosity:

```python
import logging
logging.basicConfig(level=logging.INFO)  # or logging.DEBUG for more detail
```

## Examples

See `examples/audio_processing_example.py` for comprehensive usage examples including:

- Single file processing
- Multiple file processing
- Mixed input types
- Error handling scenarios
- Custom diarization parameters

## API Reference

### AudioProcessor Class

#### `__init__(diarize_model=None)`
Initialize the audio processor with an optional diarization model.

#### `process_audio_batch(args, min_speakers=1, max_speakers=10, **diarizer_kwargs)`
Process a batch of audio inputs.

**Parameters:**
- `args`: Dictionary with 'audio' key containing input(s)
- `min_speakers`: Minimum speakers for diarization
- `max_speakers`: Maximum speakers for diarization
- `**diarizer_kwargs`: Additional diarization parameters

**Returns:** List of processed results

#### `validate_audio_path(path)`
Validate that an audio file path exists and is readable.

#### `get_audio_info(audio_path)`
Get information about an audio file.

### Convenience Functions

#### `process_audio_with_diarization(audio_inputs, diarize_model=None, min_speakers=1, max_speakers=10, **kwargs)`
Convenience function for processing audio with diarization.

## Integration Notes

1. **Replace transcription logic**: Update `_transcribe_audio()` method with your actual transcription implementation
2. **Configure diarization model**: Pass your diarization model instance to the processor
3. **Handle results**: Process the returned results list to extract transcriptions and diarization data
4. **Error handling**: Check for errors in the results and handle appropriately

## Dependencies

- Python 3.7+
- `pathlib` (built-in)
- `os` (built-in)
- `logging` (built-in)
- `typing` (built-in)
