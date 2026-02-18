# VoiceStudio v1.0.0-rc1 Release Notes

**Release Date:** 2026-02-15  
**Release Type:** Release Candidate 1

---

## Overview

VoiceStudio v1.0.0-rc1 is the first release candidate for the initial public release. This version represents a comprehensive voice synthesis, transcription, and audio processing platform for Windows desktop.

## Key Features

### Text-to-Speech (TTS)
- **10+ TTS Engines**: XTTS v2, Bark, Piper, OpenVoice, StyleTTS2, Tacotron2, GPT-SoVITS, Coqui TTS, and more
- **Voice Cloning**: Create custom voices from reference audio samples
- **Multi-language Support**: 15+ languages with native speaker quality
- **Streaming Synthesis**: Real-time audio generation with low latency

### Speech-to-Text (STT)
- **Whisper Integration**: State-of-the-art transcription with faster-whisper
- **Automatic Language Detection**: Supports 99 languages
- **Word-level Timestamps**: Precise timing for subtitle generation
- **GPU Acceleration**: CTranslate2-based acceleration for fast transcription

### Voice Conversion
- **RVC (Retrieval-based Voice Conversion)**: Real-time voice transformation
- **Pitch and Formant Control**: Fine-tune voice characteristics
- **Feature Index Blending**: High-quality speaker transfer

### Audio Library
- **Asset Management**: Organize audio files, voices, and projects
- **Batch Processing**: Process multiple files with consistent settings
- **Export Formats**: WAV, MP3, FLAC, OGG, and more

## What's New in RC1

### Architecture Improvements
- **Contract Version Negotiation**: Frontend-backend API versioning with `X-VS-Contract-Version` header
- **Centralized State Management**: Consolidated `AppStateStore` with undo/redo support
- **Venv Family Isolation**: PyTorch version conflict detection across engine families
- **Command Infrastructure**: `CommandMutexService` for batch job coordination

### User Experience
- **First Run Wizard**: Guided setup for new installations with system checks
- **GPU Fallback Notification**: Informational toast when running in CPU mode
- **Backend Health Monitoring**: Real-time status of backend services and engines

### Quality & Testing
- **Golden Path E2E Test**: End-to-end test covering import → transcribe → clone → synthesize workflow
- **10 Resolved Architecture Gaps**: Button interconnectivity, state management, and infrastructure issues

## System Requirements

### Minimum
- **OS**: Windows 10 (version 1903+) or Windows 11
- **CPU**: 4-core x64 processor
- **RAM**: 8 GB
- **Storage**: 5 GB (application) + model storage

### Recommended
- **OS**: Windows 11
- **CPU**: 8-core x64 processor
- **RAM**: 16 GB
- **GPU**: NVIDIA RTX 2060+ with 6GB+ VRAM (for GPU acceleration)
- **Storage**: 50 GB SSD

## Installation

1. Download `VoiceStudio-Setup-v1.0.0-rc1.exe`
2. Run installer with administrator privileges
3. Complete First Run Wizard to configure system
4. Backend will start automatically on first launch

## Known Limitations

- Some TTS engines require significant VRAM (8GB+ for GPT-SoVITS, StyleTTS2)
- First engine load may take 30-60 seconds for model download
- CPU-only mode is functional but significantly slower for neural TTS

## Resolved Issues

### Gap Closures (Phase D)
- **GAP-I10**: Contract version negotiation implemented
- **GAP-F01**: Duplicate AppStateStore consolidated
- **GAP-E03**: Venv PyTorch conflict detection added
- **GAP-I25**: GPU fallback UX with toast notification

### Button Infrastructure (Phase A)
- **GAP-B01**: Cross-panel CanExecuteChanged propagation
- **GAP-B02**: Profile deletion refresh propagation
- **GAP-B06**: Batch job button coordination
- **GAP-B10**: Command group infrastructure
- **GAP-B14**: Cross-panel command coordination
- **GAP-B21**: Shared ICommand instances via DelegatingCommand

## Upgrade Notes

This is the initial release candidate. There is no upgrade path from development builds.

## API Changes

### New Headers
- `X-VS-Contract-Version`: Required for API requests (version 3)

### New Endpoints
- `GET /api/diagnostics/venv-conflicts`: Check for PyTorch version conflicts

## Contributors

Built with contributions from the VoiceStudio development team.

## License

VoiceStudio is proprietary software. All rights reserved.

---

For issues or feedback, please file a report in the project issue tracker.
