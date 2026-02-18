# {{DISPLAY_NAME}} Audio Effect Plugin Template

A specialized VoiceStudio plugin template for audio processing with NumPy.

## Quick Start

### 1. Customize Template Tokens

Replace these tokens in all files:
- `{{PLUGIN_NAME}}` → lowercase_identifier (e.g., `gain_effect`)
- `{{CLASS_NAME}}` → PascalCase (e.g., `GainEffect`)
- `{{DISPLAY_NAME}}` → Human Readable Name
- `{{VERSION}}` → 1.0.0
- `{{AUTHOR}}` → Your Name
- `{{DESCRIPTION}}` → Plugin description

### 2. Project Structure

```
audio-effect/
├── manifest.json        # Plugin metadata with audio permissions
├── plugin.py            # FastAPI backend with audio endpoint
├── processing.py        # Pure audio processing functions
├── models.py            # Pydantic models for audio data
├── requirements.txt     # numpy>=1.20.0
└── tests/
    ├── test_plugin.py      # API integration tests
    └── test_processing.py  # Unit tests for processing
```

### 3. Key Features

- **NumPy audio processing** — Efficient array operations
- **Type-safe models** — Pydantic for validation
- **Separate concerns** — Processing logic isolated from API
- **Audio permissions** — `audio.process`, file read/write

### 4. Processing Functions

Edit `processing.py` to add your audio effects:

```python
import numpy as np

def apply_gain(audio: np.ndarray, gain_db: float) -> np.ndarray:
    """Apply gain in decibels to audio samples."""
    linear_gain = 10 ** (gain_db / 20)
    return np.clip(audio * linear_gain, -1.0, 1.0)

def normalize(audio: np.ndarray) -> np.ndarray:
    """Normalize audio to -1.0 to 1.0 range."""
    max_val = np.abs(audio).max()
    if max_val > 0:
        return audio / max_val
    return audio
```

### 5. API Endpoints

```
POST /api/plugin/{{PLUGIN_NAME}}/process_audio
Body: {
  "samples": [0.1, 0.2, -0.3, ...],
  "sample_rate": 44100,
  "effect": "normalize"
}
Response: {
  "samples": [...],
  "sample_rate": 44100,
  "message": "Processed with effect: normalize"
}
```

### 6. Permissions

This template requests these permissions in `manifest.json`:

| Permission | Purpose |
|------------|---------|
| `filesystem.read.user_selected` | Read audio files user selects |
| `filesystem.write.user_selected` | Write processed audio files |
| `audio.process` | Process audio data |

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
# All tests
pytest tests/ -v

# Processing unit tests
pytest tests/test_processing.py -v

# API integration tests
pytest tests/test_plugin.py -v
```

## Resources

- [Getting Started Guide](../../../docs/plugins/getting-started.md)
- [Backend API Reference](../../../docs/plugins/api-reference-backend.md)
- [Best Practices Guide](../../../docs/plugins/best-practices.md)

## License

MIT
