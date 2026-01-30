# Missing Items - Worker Assignments
## VoiceStudio Quantum+ - Critical Gaps Assigned

**Date:** 2025-11-23  
**Status:** ✅ Assigned to Workers

---

## 🚨 Critical Missing Items

### Worker 1: Missing Audio Engines (5 engines)

**Priority: HIGH - Must implement first**

1. **GPT-SoVITS** - Voice conversion and fine-tuning
   - Status: Manifest exists, engine class missing
   - Location: `engines/audio/gpt_sovits/engine.manifest.json`
   - Implementation: `app/core/engines/gpt_sovits_engine.py`

2. **MockingBird Clone** - Real-time voice cloning
   - Status: Manifest exists, engine class missing
   - Location: `engines/audio/mockingbird/engine.manifest.json`
   - Implementation: `app/core/engines/mockingbird_engine.py`

3. **whisper.cpp** - C++ implementation, fast local STT
   - Status: Manifest exists, engine class missing
   - Location: `engines/audio/whisper_cpp/engine.manifest.json`
   - Implementation: `app/core/engines/whisper_cpp_engine.py`

4. **Whisper UI** - User interface wrapper for Whisper
   - Status: Manifest exists, engine class missing
   - Location: `engines/audio/whisper_ui/engine.manifest.json`
   - Implementation: `app/core/engines/whisper_ui_engine.py`

5. **Piper (Rhasspy)** - Fast, lightweight TTS
   - Status: Manifest exists, engine class missing
   - Location: `engines/audio/piper/engine.manifest.json`
   - Implementation: `app/core/engines/piper_engine.py`

**Action Required:**
- Create all 5 engine classes
- Follow `EngineProtocol` interface
- Implement ALL methods (NO stubs)
- Test each engine individually
- Update `app/core/engines/__init__.py`

**Timeline:** 2-3 days

---

### Worker 2: Missing UI Panels (3 panels)

**Priority: HIGH - Must create first**

1. **ImageGenView** - Image generation panel
   - Location: `src/VoiceStudio.App/Views/Panels/ImageGenView.xaml`
   - ViewModel: `src/VoiceStudio.App/Views/Panels/ImageGenViewModel.cs`
   - Purpose: Interface for all 13 image generation engines
   - Features:
     - Engine selection dropdown (all 13 image engines)
     - Prompt input (text-to-image)
     - Image input (image-to-image)
     - Parameter controls (CFG scale, steps, seed, width, height, etc.)
     - Preview area with image display
     - Batch generation support
     - Image gallery/history
     - Save/load presets
   - Backend Integration: `/api/image/generate`
   - Design: Use DesignTokens.xaml, follow MVVM pattern

2. **VideoGenView** - Video generation panel
   - Location: `src/VoiceStudio.App/Views/Panels/VideoGenView.xaml`
   - ViewModel: `src/VoiceStudio.App/Views/Panels/VideoGenViewModel.cs`
   - Purpose: Interface for video generation engines (SVD, Deforum, etc.)
   - Features:
     - Engine selection dropdown (8 video engines)
     - Image input (for image-to-video)
     - Text prompt (for text-to-video)
     - Parameter controls (frames, fps, duration, etc.)
     - Preview area with video player
     - Video timeline preview
     - Batch generation support
     - Export options
   - Backend Integration: `/api/video/generate`
   - Design: Use DesignTokens.xaml, follow MVVM pattern

3. **VideoEditView** - Video editing panel
   - Location: `src/VoiceStudio.App/Views/Panels/VideoEditView.xaml`
   - ViewModel: `src/VoiceStudio.App/Views/Panels/VideoEditViewModel.cs`
   - Purpose: Interface for video editing engines (MoviePy, FFmpeg AI)
   - Features:
     - Video timeline editor
     - Clip trimming/splitting
     - Effect application
     - Transition controls
     - Export options
     - Preview player
   - Backend Integration: `/api/video/edit`
   - Design: Use DesignTokens.xaml, follow MVVM pattern

**Action Required:**
- Create all 3 XAML views with code-behind
- Create all 3 ViewModels
- Integrate with backend APIs
- Follow MVVM pattern strictly
- Use DesignTokens.xaml for all styling
- NO stubs or placeholders

**Timeline:** 3-4 days

---

### Worker 3: Missing Audio Effects (10+ effects)

**Priority: HIGH for first 2, MEDIUM/LOW for rest**

**High Priority (Implement First):**

1. **Chorus** - Chorus effect
   - Backend: Add to `backend/api/routes/effects.py`
   - Parameters: Depth (0.0-1.0), Rate (0.1-10.0 Hz), Feedback (0.0-0.95), Mix (0.0-1.0)
   - Implementation: Use LFO modulation with delay
   - UI: Add to `EffectsMixerView.xaml`

2. **Pitch Correction** - Auto-tune for voice
   - Backend: Add to `backend/api/routes/effects.py`
   - Parameters: Key (C, C#, D, etc.), Scale (Major, Minor, etc.), Strength (0.0-1.0), Speed (0.0-1.0)
   - Implementation: Use pitch detection and correction
   - UI: Add to `EffectsMixerView.xaml`

**Medium Priority:**

3. **Convolution Reverb** - Impulse response reverb
   - Parameters: IR file, Mix (0.0-1.0), Pre-delay (0-200ms)
   - Implementation: Convolution with IR files

4. **Formant Shifter** - Voice character modification
   - Parameters: Formant shift (-50% to +50%), Preserve pitch (bool)
   - Implementation: Formant analysis and shifting

**Low Priority (Future):**

5. **Distortion** - Distortion/saturation
6. **Multi-Band Processor** - Multi-band processing
7. **Dynamic EQ** - Frequency-dependent dynamics
8. **Spectral Processor** - Spectral editing
9. **Granular Synthesizer** - Granular synthesis
10. **Vocoder** - Vocoder effect

**Action Required:**
- Add effect types to `backend/api/routes/effects.py`
- Implement `_apply_effect()` handlers for each effect
- Add UI controls to `EffectsMixerView.xaml`
- Create effect models in backend
- Follow existing effect patterns (EQ, Compressor, Reverb, etc.)
- NO stubs or placeholders

**Timeline:** 
- High Priority (2 effects): 1-2 days
- Medium Priority (2 effects): 1-2 days
- Low Priority (6 effects): 3-5 days (future)

---

## 📊 Summary

| Worker | Missing Items | Count | Priority | Timeline |
|--------|---------------|-------|----------|----------|
| **Worker 1** | Audio Engines | 5 | HIGH | 2-3 days |
| **Worker 2** | UI Panels | 3 | HIGH | 3-4 days |
| **Worker 3** | Audio Effects | 10+ | HIGH (2), MED/LOW (8+) | 1-2 days (high), 3-5 days (rest) |

**Total Critical Items:** 18 items
**Total Timeline:** ~6-9 days for high-priority items

---

## ✅ Verification Checklist

### Worker 1:
- [ ] GPT-SoVITS engine class created
- [ ] MockingBird engine class created
- [ ] whisper.cpp engine class created
- [ ] Whisper UI engine class created
- [ ] Piper engine class created
- [ ] All engines implement EngineProtocol
- [ ] All engines tested
- [ ] `__init__.py` updated

### Worker 2:
- [ ] ImageGenView.xaml created
- [ ] ImageGenViewModel.cs created
- [ ] VideoGenView.xaml created
- [ ] VideoGenViewModel.cs created
- [ ] VideoEditView.xaml created
- [ ] VideoEditViewModel.cs created
- [ ] All panels use DesignTokens.xaml
- [ ] All panels follow MVVM pattern
- [ ] Backend integration complete
- [ ] NO stubs or placeholders

### Worker 3:
- [ ] Chorus effect implemented
- [ ] Pitch Correction effect implemented
- [ ] Effects added to backend
- [ ] UI controls added to EffectsMixerView
- [ ] Effects tested
- [ ] NO stubs or placeholders

---

**Status:** ✅ All missing items assigned to workers  
**Next:** Workers begin implementation

