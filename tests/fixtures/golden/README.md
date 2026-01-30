# Golden Audio Test Fixtures

This directory contains reference audio outputs for regression testing.

## Structure

```
golden/
├── xtts/                  # XTTS engine golden outputs
│   ├── hello_world.wav    # Reference audio
│   ├── hello_world.json   # Metadata and quality metrics
│   └── ...
├── chatterbox/            # Chatterbox engine golden outputs
├── piper/                 # Piper engine golden outputs
├── config.json            # Golden test configuration
└── README.md              # This file
```

## Adding New Golden Files

1. Generate reference audio using the engine
2. Calculate quality metrics (MOS, similarity, LUFS)
3. Save both audio and metadata JSON:

```json
{
  "text": "Hello world",
  "engine": "xtts",
  "voice_profile": "default",
  "created_at": "2026-01-29T00:00:00Z",
  "metrics": {
    "mos": 4.5,
    "similarity": 0.85,
    "lufs": -16.0,
    "snr_db": 45.0
  }
}
```

## Updating Golden Files

To update golden files after intentional changes:

```bash
pytest tests/regression/test_audio_golden.py --update-golden
```

## Tolerance Configuration

Tolerances are defined in `config.json`:

- MOS: ±0.3
- Similarity: ±0.1
- LUFS: ±2.0 dB
- SNR: ±3.0 dB

Adjust these based on engine stability and expected variance.
