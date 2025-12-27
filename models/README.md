# VoiceStudio Models Directory

This directory contains shared model caches and weights for all engines.

## Location

Models are stored in:
```
%PROGRAMDATA%\VoiceStudio\models\
```

This keeps models off the C: drive and allows sharing between installations.

## Structure

```
models/
├── xtts_v2/          # XTTS v2 model files
│   ├── cache/       # HuggingFace cache
│   └── ...
├── piper/            # Piper TTS voices
│   └── voices/
├── openvoice/        # OpenVoice checkpoints
│   └── checkpoints/
├── sdxl/             # SDXL models
│   ├── checkpoints/
│   ├── loras/
│   └── vae/
├── realesrgan/       # Real-ESRGAN models
│   └── models/
└── svd/              # Stable Video Diffusion
    └── checkpoints/
```

## Model Paths

Each engine's manifest specifies its model paths using environment variables:

- `%PROGRAMDATA%\VoiceStudio\models\{engine_id}\` - Base path
- Subdirectories for specific model types (checkpoints, cache, voices, etc.)

## Downloading Models

Models are typically downloaded automatically when engines are first used. You can also:

1. Download models manually to the appropriate subdirectory
2. Use engine-specific download scripts
3. Copy models from another installation

## Disk Space

Models can require significant disk space:

- **XTTS v2:** ~2-4 GB
- **Piper:** ~50-200 MB per voice
- **OpenVoice:** ~500 MB
- **SDXL:** ~7-14 GB (base + checkpoints)
- **Real-ESRGAN:** ~100-500 MB
- **SVD:** ~5-10 GB

**Total estimated:** 20-80 GB depending on which engines you use.

## Sharing Models

Since models are stored in `%PROGRAMDATA%`, they can be shared between:
- Multiple VoiceStudio installations
- Different user accounts (if permissions allow)
- Development and production environments

## Backup

Consider backing up the models directory if you have:
- Custom trained models
- Downloaded checkpoints
- Fine-tuned LoRAs

