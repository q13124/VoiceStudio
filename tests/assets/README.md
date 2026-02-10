# Test Assets

This directory contains test assets used by the VoiceStudio test suite.

## Contents

- `sample.wav` - A 1-second, 440Hz (A4) sine wave at 16kHz sample rate
  - Used for synthesis, processing, and audio I/O tests
  - Mono, 16-bit PCM

## Generating New Test Assets

To regenerate or create new test assets:

```python
import numpy as np
import wave

# Generate a test tone
sample_rate = 16000
duration = 1.0  # seconds
frequency = 440.0  # Hz

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * frequency * t)
audio_int16 = (audio * 32767).astype(np.int16)

with wave.open('sample.wav', 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_int16.tobytes())
```

## Usage in Tests

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_audio_path():
    return Path(__file__).parent / "assets" / "sample.wav"
```

## Notes

- Do NOT commit large audio files (>1MB) to this directory
- For engine-specific test audio, use the engine's test fixtures
