# Venv Families Strategy Analysis

> **TD-015**: Venv Families Strategy  
> **Author**: Engine Engineer (Role 5)  
> **Date**: 2026-02-02  
> **Status**: Analysis Complete - Ready for Implementation

---

## Executive Summary

VoiceStudio has 44 engines with varying dependency requirements. This analysis proposes grouping engines into **8 venv families** based on dependency compatibility, reducing complexity while enabling conflict-free operation.

---

## Current State

### Engine Inventory

| Category | Count | Examples |
|----------|-------|----------|
| Audio TTS | 18 | XTTS, Chatterbox, Piper, Tortoise |
| Audio STT | 4 | Whisper, Whisper.cpp, Vosk |
| Audio Processing | 3 | RVC, SoVITS, Aeneas |
| Image Generation | 11 | SDXL, ComfyUI, Automatic1111 |
| Video | 8 | SadTalker, FOMM, Deforum |

### Current Issues

1. **Dependency Conflicts**: Chatterbox pins `torch==2.6.0`, XTTS needs `torch>=2.2.2`
2. **GPU Compatibility**: RTX 5000 series (SM 120) needs PyTorch 2.11+ nightly
3. **Single Venv**: All 44 engines share `.venv`, causing import conflicts
4. **Model Size**: Combined dependencies exceed 20GB

---

## Proposed Venv Families

### Family 1: `venv_core_tts`
**Engines**: XTTS, Silero, eSpeak-NG, Festival/Flite, MaryTTS, RHVoice  
**Primary Dep**: `coqui-tts==0.27.2`, `torch>=2.2.2`  
**Size**: ~8GB  
**Notes**: Core voice cloning, stable torch version

### Family 2: `venv_advanced_tts`
**Engines**: Chatterbox, F5-TTS, OpenVoice, GPT-SoVITS  
**Primary Dep**: `chatterbox-tts>=1.0`, `torch==2.6.0`  
**Size**: ~10GB  
**Notes**: Latest TTS models, may need nightly torch for SM 120

### Family 3: `venv_fast_tts`
**Engines**: Piper, Bark, Parakeet  
**Primary Dep**: `piper-tts>=1.0`, minimal torch  
**Size**: ~2GB  
**Notes**: Lightweight, CPU-friendly

### Family 4: `venv_stt`
**Engines**: Whisper, Whisper.cpp, Vosk, Aeneas  
**Primary Dep**: `openai-whisper>=20230124`, `faster-whisper`  
**Size**: ~4GB  
**Notes**: Speech-to-text and alignment

### Family 5: `venv_voice_conversion`
**Engines**: RVC, So-VITS-SVC, Mockingbird, Speaker Encoder  
**Primary Dep**: `fairseq`, `pyworld`  
**Size**: ~6GB  
**Notes**: Voice conversion and cloning

### Family 6: `venv_image`
**Engines**: SDXL, SD-CPU, Fooocus, FastSD-CPU, RealESRGAN  
**Primary Dep**: `diffusers>=0.25`, `transformers`  
**Size**: ~12GB  
**Notes**: Image generation, shares diffusers

### Family 7: `venv_comfy`
**Engines**: ComfyUI, SDXL-Comfy, InvokeAI  
**Primary Dep**: ComfyUI workflow engine  
**Size**: ~8GB  
**Notes**: Node-based image workflows

### Family 8: `venv_video`
**Engines**: SadTalker, FOMM, Deforum, SVD, MoviePy, FFmpeg-AI  
**Primary Dep**: `face-alignment`, `imageio-ffmpeg`  
**Size**: ~10GB  
**Notes**: Video synthesis and lip-sync

---

## Implementation Plan

### Phase 1: Core Infrastructure (8 hours)
1. Create `VenvFamilyManager` class
2. Define family configuration schema
3. Implement venv creation/activation logic
4. Add family selection to engine manifest

### Phase 2: Family Configurations (16 hours)
1. Create `requirements-{family}.txt` for each family
2. Test dependency resolution
3. Document known conflicts and resolutions
4. Create setup scripts per family

### Phase 3: Engine Integration (8 hours)
1. Add `venv_family` field to engine manifests
2. Update `EngineLifecycle` to use family venvs
3. Update `ResourceManager` for family awareness
4. Test engine loading from families

### Phase 4: Installer Integration (8 hours)
1. Update installer to bundle family venvs
2. Add family selection UI
3. Implement lazy venv creation (on first use)
4. Add disk space requirements to installer

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Disk space increase | High | Medium | Lazy venv creation, shared packages |
| Installation time | High | Low | Parallel venv creation |
| Maintenance burden | Medium | Medium | Automated dependency updates |
| Cross-family conflicts | Low | High | Strict family isolation |

---

## Disk Space Analysis

| Family | Estimated Size | Notes |
|--------|---------------|-------|
| venv_core_tts | 8 GB | Largest, most used |
| venv_advanced_tts | 10 GB | Latest models |
| venv_fast_tts | 2 GB | Minimal |
| venv_stt | 4 GB | Whisper models |
| venv_voice_conversion | 6 GB | Fairseq heavy |
| venv_image | 12 GB | Diffusers + models |
| venv_comfy | 8 GB | ComfyUI ecosystem |
| venv_video | 10 GB | Face models |
| **Total** | **~60 GB** | vs ~25 GB single venv |

**Recommendation**: Implement lazy venv creation to reduce initial install size.

---

## Existing Assets

- `venv_gpu_sm120`: Already created with PyTorch 2.11+cu128 (SM 120 support)
- `.venv`: Current production venv, becomes `venv_core_tts`

---

## Decision Required

**Options**:
1. **Full Implementation** (40-60 hours): All 8 families
2. **Minimal Implementation** (16-20 hours): 3 critical families only
   - venv_core_tts (XTTS, standard TTS)
   - venv_advanced_tts (Chatterbox, SM 120 support)
   - venv_stt (Whisper)
3. **Defer**: Continue with single venv, document conflicts

**Recommendation**: Option 2 - Start with 3 critical families, expand as needed.

---

## References

- TD-001: Chatterbox torch version (blocked on venv families)
- TD-013: VRAM Resource Scheduler (completed, family-aware)
- ADR-007: Control Plane / Data Plane IPC
- venv_gpu_sm120: Existing GPU-optimized venv
