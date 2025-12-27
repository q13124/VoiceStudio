# Voice Cloning API Implementation

## Overview

This document describes the voice cloning endpoints and their integration with the VoiceStudio engine system.

## Endpoints

### `/api/voice/synthesize` (POST)

Synthesize audio from text using a voice profile.

**Request:**
```json
{
  "engine": "xtts",  // "chatterbox", "xtts", or "tortoise"
  "profile_id": "profile_123",
  "text": "Hello, this is a test.",
  "language": "en",
  "emotion": "happy"  // optional
}
```

**Response:**
```json
{
  "audio_id": "synth_profile_123_12345",
  "audio_url": "/api/voice/audio/synth_profile_123_12345",
  "duration": 2.5,
  "quality_score": 0.85
}
```

**Features:**
- Supports multiple engines (chatterbox, xtts, tortoise)
- Automatic quality calculation
- Quality enhancement for high-end engines
- Handles both audio array and file outputs

### `/api/voice/analyze` (POST)

Analyze audio quality and voice characteristics.

**Request:**
- Multipart form data with `audio_file` (WAV file)
- Optional `metrics` query parameter (comma-separated: "mos,similarity,naturalness")

**Response:**
```json
{
  "metrics": {
    "mos": 4.2,
    "similarity": 0.87,
    "naturalness": 0.82,
    "snr": 28.5,
    "lufs": -16.2,
    "pitch_stability": 0.91
  },
  "quality_score": 0.85
}
```

**Metrics Available:**
- `mos`: Mean Opinion Score (1-5 scale)
- `similarity`: Voice similarity to reference (0-1)
- `naturalness`: Naturalness score (0-1)
- `snr`: Signal-to-noise ratio (dB)
- `lufs`: Loudness units
- `pitch_stability`: Pitch stability score

### `/api/voice/clone` (POST)

Clone voice from reference audio and optionally synthesize text.

**Request:**
- Multipart form data with `reference_audio` (WAV file)
- Optional `text` parameter
- `engine`: "chatterbox", "xtts", or "tortoise" (default: "xtts")
- `quality_mode`: "fast", "standard", "high", or "ultra" (default: "standard")

**Response:**
```json
{
  "profile_id": "clone_12345",
  "audio_id": "clone_clone_12345",  // null if no text provided
  "audio_url": "/api/voice/audio/clone_12345",  // null if no text provided
  "quality_score": 0.88
}
```

**Quality Modes:**
- `fast`: Quick cloning, lower quality
- `standard`: Balanced quality and speed
- `high`: Best quality, slower processing
- `ultra`: Maximum quality, very slow

## Engine Integration

The voice cloning endpoints are fully integrated with the VoiceStudio engine system:

### Registered Engines

1. **XTTS (xtts)**: High-quality multilingual synthesis
   - Fast inference
   - Multi-language support
   - Good quality/speed balance

2. **Chatterbox (chatterbox)**: Fast, lightweight synthesis
   - Very fast inference
   - Good for real-time applications
   - Lower quality than XTTS/Tortoise

3. **Tortoise (tortoise)**: Ultra-high quality synthesis
   - Best quality output
   - Slower inference
   - Quality enhancement enabled by default

### Engine Router

Engines are automatically registered with the global `EngineRouter` instance:
- Engines are lazy-loaded (created on first use)
- Instances are cached for performance
- Automatic cleanup on shutdown

### Quality Metrics

The API uses the `quality_metrics` module for analysis:
- `calculate_all_metrics()`: Calculate all available metrics
- `calculate_mos_score()`: Mean Opinion Score
- `calculate_similarity()`: Voice similarity
- `calculate_naturalness()`: Naturalness score
- `calculate_snr()`: Signal-to-noise ratio

## Error Handling

All endpoints include comprehensive error handling:
- Engine initialization failures return 503
- Invalid parameters return 400
- Synthesis failures return 500 with detailed error messages
- Fallback to mock responses if engines are unavailable

## Performance Considerations

1. **Engine Caching**: Engines are cached after first use
2. **Quality Calculation**: Can be disabled for faster synthesis
3. **Quality Enhancement**: Only enabled for high-quality engines (tortoise)
4. **Temporary Files**: Automatically cleaned up after processing

## Future Improvements

1. **Profile Storage**: Integrate with profile database for reference audio
2. **Audio Storage**: Store synthesized audio in persistent storage
3. **Batch Processing**: Support batch synthesis requests
4. **Streaming**: Support streaming audio output
5. **Progress Updates**: WebSocket progress updates for long operations

