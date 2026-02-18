# Audio Fixtures

This template includes a fixture generation script to create deterministic WAV
samples for regression testing:

- `silence.wav` (1 second, mono, float32)
- `tone_440hz.wav` (1 second, mono, float32)
- `speech_like.wav` (synthetic speech-like envelope, mono, float32)

Run:

```bash
python tests/fixtures/generate_fixtures.py
```
