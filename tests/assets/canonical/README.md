# Canonical Test Audio

This directory holds the **canonical test audio** used for VoiceStudio voice cloning, transcription, and synthesis tests. This is the single standard reference; all tests that need real speech should use it.

## Rule: Original Must Stay Intact

- **`originals/`** — Contains the source file only. **Never modify or overwrite files in this directory.**
- **`standard/`** — Contains converted formats (WAV). Generated from the original; the original is never altered.

## File Locations

| Purpose | Path | Format |
|---------|------|--------|
| Source (do not modify) | `originals/allan_watts.m4a` | M4A |
| **Standard (primary)** | `standard/allan_watts.wav` | WAV, 22050 Hz, mono, 16-bit PCM |
| **Quick segment** | `standard/allan_watts_15s.wav` | WAV, 15 s, same format |

## Usage

- **Voice cloning tests**: Use `standard/allan_watts.wav`
- **Transcription tests**: Use `standard/allan_watts.wav`
- **Synthesis reference**: Use `standard/allan_watts.wav`

In Python tests, use the `canonical_audio_path` pytest fixture (defined in `tests/conftest.py`).

For programmatic access outside pytest, use:

```python
from tests.fixtures.canonical import get_canonical_wav_path
```

## Creating Additional Formats

If a test needs a different sample rate or format, **convert from the original** (or from the standard WAV), and write the result under `standard/`. Do not overwrite `allan_watts.wav`.

Example (44.1 kHz variant):

```powershell
ffmpeg -y -i "originals/allan_watts.m4a" -acodec pcm_s16le -ar 44100 -ac 1 "standard/allan_watts_44100.wav"
```

Example (16 kHz for some engines):

```powershell
ffmpeg -y -i "standard/allan_watts.wav" -ar 16000 "standard/allan_watts_16000.wav"
```

After adding a format, update `manifest.json` with the new path and metadata.

## Manifest

See `manifest.json` for the single source of truth: paths, sample rates, and usage mapping.

## Notes

- The canonical WAV is long-form (approx. 52 minutes). Use `allan_watts_15s.wav` for quick tests, or the full file when needed.
- Large files are tracked with Git LFS; see CI/CD section below.

## CI/CD Integration

### Git LFS

The canonical audio files are tracked by Git LFS. Ensure LFS is installed:

```bash
git lfs install
git lfs pull
```

### CI Pipeline Restoration

If LFS is unavailable in CI, restore from artifact storage:

```yaml
# GitHub Actions example
- name: Restore canonical audio
  run: |
    if [ ! -f "tests/assets/canonical/standard/allan_watts.wav" ]; then
      curl -L -o canonical.zip "${{ secrets.CANONICAL_AUDIO_URL }}"
      unzip canonical.zip -d tests/assets/
    fi
```

### Skipping Canonical Audio Tests

To skip tests requiring canonical audio (e.g., in lightweight CI):

```bash
pytest -m "not canonical_audio"
```
