# Artifact and Model Reference

**Domain:** Core Platform (Role 4)
**Created:** 2026-02-10
**Status:** Active

## Overview

This document describes VoiceStudio's artifact and model storage conventions, durability guarantees, and preflight validation.

## Model Storage

### Base Path

Default: `VOICESTUDIO_MODELS_PATH` or `~/.voicestudio/models/`

### Directory Structure

```
models/
├── xtts/
│   ├── xtts_v2/
│   └── speakers/
├── whisper/
│   ├── large-v3/
│   └── medium/
├── rvc/
│   └── trained/
├── piper/
│   └── voices/
└── cache/
    └── huggingface/
```

## Artifact Types

| Type | Extension | Location |
|------|-----------|----------|
| Voice profile | `.json` | `data/profiles/` |
| Trained voice | `.pth`, `.safetensors` | `models/rvc/trained/` |
| Audio output | `.wav`, `.mp3` | `data/output/` |
| Project file | `.vsproj` | `data/projects/` |

## Durability Guarantees

- **Trained models**: Immutable after creation, verified by checksum
- **Voice profiles**: Atomic writes with backup
- **Audio output**: Generated on demand, cached for session

## Preflight Validation

Before job execution, preflight checks validate:

1. Model files exist and pass checksum
2. Required disk space available
3. GPU memory sufficient (if GPU job)
4. Dependencies available

## Model Download

Models are downloaded on first use:
- Source: HuggingFace Hub, custom URLs
- Verification: SHA256 checksum
- Retry: 3 attempts with exponential backoff

## Related Documents

- [Storage Durability Reference](STORAGE_DURABILITY_REFERENCE.md)
- [Preflight Reference](PREFLIGHT_REFERENCE.md)
- [Engine Reference](ENGINE_REFERENCE.md)
