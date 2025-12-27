# VoiceStudio Engine Library Download Guide

## Purpose

This guide ensures all Cursor agents responsible for engine setup automatically download, verify, and install any available **open-source** or **freely licensed** models and runtime files **locally**, without requiring constant internet access.

---

## Primary Rules

- ✅ Prioritize **fully offline** model use.
- ✅ Use local mirrors, pre-downloaded archives, or bundled ZIPs where possible.
- ❌ Do not rely on runtime HTTP fetch unless explicitly marked `auto_update=true`.

---

## Directory Structure

All models and engines must install to this structure:

```
%PROGRAMDATA%\VoiceStudio\models\
├── xtts_v2\              # XTTS v2 model files
│   ├── cache\           # HuggingFace cache
│   └── models\          # Model checkpoints
├── coqui\                # Coqui TTS models
│   └── models\
├── piper\                # Piper TTS voices
│   └── voices\
├── f5_tts\               # F5 TTS models
│   └── models\
├── higgs\                # Higgs TTS models
│   └── models\
├── whisper_cpp\          # Whisper.cpp models
│   └── models\
├── aeneas\               # Aeneas models
│   └── models\
├── comfyui\              # ComfyUI models
│   ├── checkpoints\
│   ├── loras\
│   └── vae\
├── automatic1111\        # Automatic1111 models
│   ├── models\
│   │   ├── Stable-diffusion\
│   │   ├── Lora\
│   │   └── VAE\
├── stable_diffusion_next\ # SD.Next models
│   └── models\
├── realesrgan\           # Real-ESRGAN models
│   └── models\
├── sadtalker\            # SadTalker models
│   └── checkpoints\
├── fomm\                  # First Order Motion Model
│   └── checkpoints\
├── deepfacelab\          # DeepFaceLab models
│   └── models\
├── svd\                   # Stable Video Diffusion
│   └── checkpoints\
└── deforum\              # Deforum models
    └── checkpoints\
```

**Base Path:** `%PROGRAMDATA%\VoiceStudio\models\`  
**Environment Variable:** Uses Windows `%PROGRAMDATA%` environment variable  
**Fallback:** `~/.voicestudio/models/` on non-Windows systems

---

## Index File Format

The `models.index.json` file tracks all available models:

```json
{
  "version": "1.0",
  "updated": "2025-01-27T00:00:00Z",
  "models": [
    {
      "name": "en-us_female",
      "engine": "piper",
      "size_bytes": 52428800,
      "sha256": "a1b2c3d4e5f6...",
      "license": "MIT",
      "download_url": "https://example.com/en-us_female.zip",
      "updated": "2025-01-27T00:00:00Z",
      "auto_update": false
    }
  ]
}
```

### Index File Fields

- **name:** Model identifier (e.g., "en-us_female", "xtts-v2-base")
- **engine:** Engine ID (e.g., "piper", "xtts_v2", "whisper_cpp")
- **size_bytes:** Model file size in bytes
- **sha256:** SHA-256 checksum for verification
- **license:** License type (MIT, Apache-2.0, CC-BY, etc.)
- **download_url:** URL to download model archive
- **updated:** Last update timestamp (ISO 8601)
- **auto_update:** Whether to check for updates automatically (default: false)

### Index File Location

- **Primary:** `engines/models.index.json`
- **Local Override:** `%PROGRAMDATA%\VoiceStudio\models\models.index.json` (user-specific)

---

## Local Download Targets

The following engines should have all known public libraries auto-installed at build time:

### TTS Engines

- **xtts_v2** - Coqui XTTS v2 base models
- **coqui** - Coqui TTS models
- **piper** - Piper TTS voices (all available languages)
- **f5_tts** - F5 TTS models
- **higgs** - Higgs TTS models

### Audio Inference

- **whisper_cpp** - Whisper.cpp models (base, small, medium, large)
- **aeneas** - Aeneas alignment models

### Image Gen

- **comfyui** - ComfyUI base models and workflows
- **automatic1111** - Automatic1111 base models
- **stable_diffusion_next** - SD.Next base models

### Upscaling

- **realesrgan** - Real-ESRGAN upscaling models

### Talking Head / Video

- **sadtalker** - SadTalker checkpoints
- **fomm** - First Order Motion Model checkpoints
- **deepfacelab** - DeepFaceLab models

### Video Gen

- **svd** - Stable Video Diffusion checkpoints
- **deforum** - Deforum models

---

## Cursor Agent Requirements

Cursor agents must:

1. **Check if the file exists and sha256 matches.**
   - Verify model file exists at expected path
   - Calculate SHA-256 checksum of existing file
   - Compare with index file checksum
   - If match: skip download

2. **If not, download and unzip to the correct path.**
   - Download from `download_url` using wget, curl, or Python's requests
   - Verify downloaded file SHA-256 matches index
   - Extract archive to engine-specific directory
   - Verify extracted files

3. **Update models.index.json if successful.**
   - Mark model as downloaded
   - Update local index with download timestamp
   - Record local file path

4. **Use wget, curl, or Python's requests for fetching.**
   - Prefer archives hosted on GitHub, HuggingFace, or direct engine devs
   - Support resume for large downloads
   - Handle network errors gracefully
   - Retry failed downloads (max 3 attempts)

---

## Offline Sync Script

Provide optional script: `python tools/download_all_free_models.py`

This script will:

1. **Traverse all manifests**
   - Scan `engines/` directory for all `engine.manifest.json` files
   - Extract model requirements from manifests
   - Build list of required models

2. **Download all free models**
   - Read `models.index.json` for available models
   - Filter by permissive licenses only
   - Download models for all engines listed in manifests
   - Show progress for each download

3. **Verify checksums**
   - Calculate SHA-256 for each downloaded file
   - Compare with index file checksums
   - Report verification failures
   - Retry failed verifications

4. **Store bundles in models path**
   - Extract archives to `%PROGRAMDATA%\VoiceStudio\models\{engine}\`
   - Preserve directory structure from archives
   - Update local index file

**Usage:**
```bash
# Download all free models
python tools/download_all_free_models.py

# Download for specific engine
python tools/download_all_free_models.py --engine piper

# Verify existing models only
python tools/download_all_free_models.py --verify-only

# Update index from remote
python tools/download_all_free_models.py --update-index
```

---

## Ethics

### License Compliance

- ✅ **Only download models with permissive licenses**
  - MIT, Apache-2.0, BSD, CC-BY, CC0, Public Domain
  - Check license field in index file before downloading

- ✅ **Mark license type in index**
  - All models must have license field populated
  - Display license in UI when available

- ❌ **Do not include restricted commercial datasets**
  - No models with "non-commercial" restrictions
  - No models with "research only" restrictions
  - No proprietary or closed-source models

### License Verification

Before downloading any model:
1. Check `license` field in `models.index.json`
2. Verify license is in approved list
3. Skip models with restricted licenses
4. Log skipped models with reason

---

## Overseer Notes

### Validation Requirements

Before marking engine setup as DONE:

1. **Confirm every engine directory is complete**
   - All required models downloaded
   - All checksums verified
   - All files in correct locations
   - Directory structure matches specification

2. **Validate sha256 and that UI exposes model dropdowns**
   - Verify all downloaded models have correct checksums
   - Ensure UI dropdowns populated with downloaded models
   - Test model selection in UI
   - Verify models load correctly

3. **Include model manager panel for managing/removing these locally**
   - Create Model Manager UI panel
   - Display all downloaded models
   - Show model size, license, last updated
   - Allow model removal
   - Show download progress for new models

### Model Manager UI Requirements

**Panel:** `ModelManagerView.xaml`  
**ViewModel:** `ModelManagerViewModel.cs`  
**Location:** Right panel or Settings panel

**Features:**
- List all downloaded models by engine
- Show model details (size, license, checksum, path)
- Download new models from index
- Remove models (with confirmation)
- Verify model checksums
- Update model index
- Filter by engine, license, status

---

## Final Note

This ensures VoiceStudio remains fully functional in air-gapped or restricted environments without losing functionality or quality.

**Benefits:**
- ✅ Fully offline operation
- ✅ No runtime internet dependency
- ✅ Faster startup (no download delays)
- ✅ Reproducible builds
- ✅ Air-gapped deployment support

---

## Implementation Checklist

- [ ] Create `models.index.json` schema and example
- [ ] Create `tools/download_all_free_models.py` script
- [ ] Implement model download logic in engine setup
- [ ] Add SHA-256 verification to model storage
- [ ] Create Model Manager UI panel
- [ ] Update engine manifests with model requirements
- [ ] Add license verification to download process
- [ ] Document model sources and licenses
- [ ] Test offline operation
- [ ] Validate all engine directories are complete

---

**Last Updated:** 2025-01-27  
**Status:** 📋 Implementation Required

