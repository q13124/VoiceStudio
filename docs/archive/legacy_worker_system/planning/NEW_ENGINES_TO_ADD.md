# New Engines to Add - Tracking Document
## Free & Local Engines for Audio, Video, and Image Generation

**Date Created:** 2025-11-23  
**Status:** 🟡 **NEEDS USER INPUT** - Awaiting engine list  
**Priority:** High - Add to roadmap and implementation plan

---

## 🎯 Purpose

This document tracks the new engines you mentioned that need to be added to VoiceStudio. These engines are:
- ✅ 100% free (no paid APIs)
- ✅ Local (run on user's machine, not web-based)
- ✅ For audio, video, and AI image generation

---

## 📋 Engines to Add

### ✅ User Provided List (2025-11-23)

**Video Engines:**
1. ✅ **Stable Video Diffusion (SVD)** - Already has manifest (`engines/video/svd/`)
2. ⏳ **Deforum** - Keyframed SD animations for video generation
3. ⏳ **First Order Motion Model (FOMM)** - Motion transfer for avatars
4. ⏳ **SadTalker** - Talking head, lip-sync generation
5. ⏳ **DeepFaceLab** - Face replacement/swap (gated with consent/watermark)
6. ⏳ **MoviePy** - Programmable video editing
7. ⏳ **FFmpeg with AI Plugins** - Video transcoding, muxing, filters with AI enhancements
8. ⏳ **prakashdk/video-creator** - Video creation from images and audio

**Audio Engines:**
1. ✅ **Whisper** - Already has manifest (`engines/audio/whisper/`)
2. ⏳ **whisper.cpp** - C++ implementation of Whisper (faster, local STT with SRT/VTT output)

**Alignment/Subtitle Engines:**
1. ⏳ **Aeneas** - Audio-text alignment, subtitle generation

---

## 📝 Current Engine Status

### Already Integrated (Audio):
- ✅ XTTS v2 (Coqui TTS) - Voice cloning
- ✅ Chatterbox TTS - State-of-the-art quality
- ✅ Tortoise TTS - Ultra-realistic HQ mode
- ✅ Piper - Fast, lightweight TTS
- ✅ OpenVoice - Quick cloning
- ✅ Whisper - Speech-to-text

### Already Integrated (Image):
- ✅ SDXL ComfyUI - Stable Diffusion XL
- ✅ Real-ESRGAN - Image/video upscaling

### Already Integrated (Video):
- ✅ Stable Video Diffusion (SVD) - Image-to-video

### Planned (From Documentation):
- ⏳ Higgs Audio - High-fidelity, zero-shot TTS
- ⏳ F5-TTS - Modern expressive neural TTS
- ⏳ MaryTTS - Classic OSS TTS
- ⏳ GPT-SoVITS, MockingBird - Voice conversion
- ⏳ AUTOMATIC1111, SD.Next, InvokeAI - SD pipelines
- ⏳ Deforum - Keyframed SD animations
- ⏳ First Order Motion Model (FOMM) - Motion transfer
- ⏳ SadTalker - Talking head, lip-sync
- ⏳ DeepFaceLab - Face replacement/swap
- ⏳ MoviePy - Programmable video editing
- ⏳ FFmpeg - Video transcoding

---

## 🎯 Integration Plan

### Step 1: Document New Engines
- [ ] List all new engines with descriptions
- [ ] Categorize by type (audio/video/image)
- [ ] Note installation requirements
- [ ] Document local execution method

### Step 2: Create Engine Manifests
- [x] ✅ **COMPLETE** - Created manifests for all 9 engines:
  - ✅ `engines/video/deforum/engine.manifest.json`
  - ✅ `engines/video/fomm/engine.manifest.json`
  - ✅ `engines/video/sadtalker/engine.manifest.json`
  - ✅ `engines/video/deepfacelab/engine.manifest.json`
  - ✅ `engines/video/moviepy/engine.manifest.json`
  - ✅ `engines/video/ffmpeg_ai/engine.manifest.json`
  - ✅ `engines/video/video_creator/engine.manifest.json`
  - ✅ `engines/audio/whisper_cpp/engine.manifest.json`
  - ✅ `engines/audio/aeneas/engine.manifest.json`
- [x] Define engine capabilities
- [x] Set device requirements (GPU/VRAM/RAM)
- [x] Document model storage paths

### Step 3: Implement Engine Classes
- [ ] Create engine class inheriting from `EngineProtocol`
- [ ] Implement required methods
- [ ] Add to `app/core/engines/`
- [ ] Test engine integration

### Step 4: Update Documentation
- [ ] Update `engines/README.md`
- [ ] Update `docs/COMPLETE_PROJECT_SUMMARY.md`
- [ ] Update roadmap
- [ ] Add to user documentation

### Step 5: Add to Roadmap
- [ ] Add to Phase 5 or create new phase
- [ ] Assign to appropriate worker
- [ ] Set priority and timeline

---

## 📁 Files to Update

### Engine Manifests:
- `engines/audio/{engine_id}/engine.manifest.json`
- `engines/video/{engine_id}/engine.manifest.json`
- `engines/image/{engine_id}/engine.manifest.json`

### Engine Implementations:
- `app/core/engines/{engine_id}_engine.py`

### Documentation:
- `engines/README.md`
- `docs/COMPLETE_PROJECT_SUMMARY.md`
- `docs/governance/ROADMAP_TO_COMPLETION.md`
- `docs/VS_Engine_Integration_Addendum.md`

---

## 🚀 Next Steps

1. **User provides engine list** - Fill in the engines above
2. **Research each engine** - Installation, requirements, capabilities
3. **Create manifests** - Engine metadata and configuration
4. **Implement engines** - Create engine classes
5. **Test integration** - Verify engines work
6. **Update roadmap** - Add to development plan
7. **Assign to worker** - Add to appropriate worker's tasks

---

## 📝 Notes

- All engines must be 100% local (no web APIs)
- All engines must be free (no paid services)
- Engines will be automatically discovered via manifests
- No hardcoded limits - system is fully extensible

---

**Status:** ✅ **ALL MANIFESTS CREATED** - 20 engines total (9 previous + 11 image engines)  
**Action Required:** Implement engine classes and add to roadmap

**Latest Update:** 2025-11-23 - Added 11 image generation engines:
- AUTOMATIC1111 WebUI, ComfyUI, SD.Next, InvokeAI, Fooocus, LocalAI
- SDXL, Realistic Vision, OpenJourney
- Stable Diffusion CPU-only, FastSD CPU

**See:** 
- `docs/governance/ENGINE_INTEGRATION_SUMMARY.md` - Complete details
- `docs/governance/IMAGE_ENGINES_ADDED.md` - Image engines details

