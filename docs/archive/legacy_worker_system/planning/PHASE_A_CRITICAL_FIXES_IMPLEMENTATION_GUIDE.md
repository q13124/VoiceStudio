# Phase A: Critical Fixes - Implementation Guide

## Detailed Guide for Fixing All Placeholders

**Date:** 2025-01-28  
**Status:** READY FOR EXECUTION  
**Purpose:** Step-by-step guide for fixing all critical placeholders  
**Priority:** CRITICAL - Must be completed first

---

## 🎯 Overview

Phase A focuses on fixing all placeholders, stubs, and incomplete implementations identified in the comprehensive audit. This is the foundation for all subsequent phases.

**Estimated Time:** 10-15 days with 2 workers  
**Success Criteria:** Zero placeholders, stubs, bookmarks, or tags in codebase

---

## 📋 A1: Engine Fixes (Priority Order)

### A1.1: Whisper CPP Engine (EASIEST - Start Here)

**File:** `app/core/engines/whisper_cpp_engine.py`  
**Issue:** Returns placeholder text instead of actual transcription  
**Effort:** 1 day  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Line ~318-322: Returns `"[Transcription placeholder - {duration:.2f}s of audio]"` instead of real transcription

#### Implementation Steps:

1. Check if `whisper.cpp` Python bindings are available (`whisper-cpp-python` or similar)
2. If Python bindings available:
   - Import the whisper.cpp Python module
   - Load model using whisper.cpp API
   - Perform actual transcription
   - Return real transcription text
3. If Python bindings not available:
   - Check if whisper.cpp binary is in PATH
   - Use subprocess to call whisper.cpp binary
   - Parse output to get transcription
   - Return real transcription text
4. Add error handling for when whisper.cpp is not available

#### Dependencies to Install:

```bash
pip install whisper-cpp-python  # If Python bindings available
# OR ensure whisper.cpp binary is in PATH
```

#### Test:

- Test with sample audio file
- Verify transcription is accurate
- Test error handling when whisper.cpp not available

---

### A1.2: GPT-SoVITS Engine (HIGH PRIORITY)

**File:** `app/core/engines/gpt_sovits_engine.py`  
**Issue:** Generates silence (`np.zeros()`) instead of real synthesis  
**Effort:** 1 day  
**Status:** ⚠️ CRITICAL - Generates silence

#### What Needs to be Fixed:

- Line ~255: Placeholder model loading logic
- Line ~264: Sets fake model dict instead of real model
- Line ~295: Returns `np.zeros()` - generates silence

#### Implementation Steps:

1. **Check if old project has complete implementation:**
   - Check `C:\OldVoiceStudio\app\engines\gpt_sovits_engine.py`
   - If exists, port the complete implementation
2. **If porting from old project:**
   - Copy API-based implementation
   - Update imports to match current project structure
   - Test with GPT-SoVITS server
3. **If implementing from scratch:**
   - Check if GPT-SoVITS API server is running (default port 9880)
   - Implement API calls to GPT-SoVITS server endpoints:
     - `/tts` endpoint for synthesis
     - Health check endpoint
   - Load actual GPT and SoVITS models if local mode
   - Perform actual text-to-speech synthesis
   - Return real audio (not silence)

#### Dependencies to Install:

```bash
# If using API mode (recommended):
# Ensure GPT-SoVITS server is running on port 9880
# No additional Python packages needed (uses requests)

# If using local mode:
pip install gpt-sovits  # If package exists
```

#### Reference Implementation:

- `C:\OldVoiceStudio\app\engines\gpt_sovits_engine.py` (if exists)

#### Test:

- Test with sample text
- Verify audio is generated (not silence)
- Test with different languages
- Test error handling when server unavailable

---

### A1.3: MockingBird Engine (HIGH PRIORITY)

**File:** `app/core/engines/mockingbird_engine.py`  
**Issue:** Generates silence (`np.zeros()`) instead of real synthesis  
**Effort:** 1 day  
**Status:** ⚠️ CRITICAL - Generates silence

#### What Needs to be Fixed:

- Line ~228: Placeholder model loading logic
- Line ~235: Sets fake model dict instead of real model
- Line ~266: Returns `np.zeros()` - generates silence

#### Implementation Steps:

1. **Research MockingBird implementation:**
   - MockingBird typically uses encoder, synthesizer, and vocoder models
   - Check MockingBird repository for correct usage
2. **Implement model loading:**
   - Load encoder model (speaker encoder)
   - Load synthesizer model (text-to-mel)
   - Load vocoder model (mel-to-audio)
3. **Implement synthesis:**
   - Extract speaker embedding from reference audio
   - Generate mel spectrogram from text
   - Apply voice conversion using encoder
   - Convert mel to audio using vocoder
   - Return real audio (not silence)

#### Dependencies to Install:

```bash
# Check MockingBird repository for dependencies
# Typically requires:
pip install torch torchaudio
# MockingBird-specific packages
```

#### Reference:

- MockingBird GitHub repository
- MockingBird documentation

#### Test:

- Test with sample text and reference audio
- Verify audio is generated (not silence)
- Test voice cloning quality

---

### A1.4: RVC Engine (COMPLEX - Do After Others)

**File:** `app/core/engines/rvc_engine.py`  
**Issue:** Uses simplified transformations instead of real RVC model inference  
**Effort:** 3-4 days  
**Status:** ⚠️ INCOMPLETE - Has structure but needs real implementation

#### What Needs to be Fixed:

- Line ~1010: Comment says "simplified RVC conversion - full implementation would load actual architecture"
- `_apply_rvc_model()`: Falls back to feature transformations instead of real RVC inference
- Needs actual RVC model architecture loading and inference

#### Implementation Steps:

1. **Check old project for RVC implementation:**
   - Check `C:\OldVoiceStudio\Retrieval-based-Voice-Conversion-WebUI\tools\rvc_for_realtime.py`
   - If exists, study the implementation
2. **Implement real RVC model loading:**
   - RVC models typically use encoder-decoder architecture
   - Load actual model architecture from checkpoint
   - Support different RVC model versions/formats
3. **Implement real RVC inference:**
   - Apply encoder to extract features
   - Apply decoder with target speaker embeddings
   - Use retrieval-based voice conversion if index available
   - Apply pitch shifting in feature space
   - Convert back to audio using vocoder
4. **Integrate with existing code:**
   - Replace simplified transformation in `_apply_rvc_model()`
   - Ensure compatibility with existing API
   - Maintain fallback for when model not available

#### Dependencies to Install:

```bash
pip install fairseq  # For HuBERT (already checked in code)
pip install faiss-cpu  # For vector similarity search
pip install pyworld  # For vocoder features
# RVC-specific packages (check RVC repository)
```

#### Reference Implementation:

- `C:\OldVoiceStudio\Retrieval-based-Voice-Conversion-WebUI\tools\rvc_for_realtime.py` (if exists)
- RVC repository documentation

#### Test:

- Test with sample RVC model
- Verify voice conversion works
- Test with different speakers
- Test pitch shifting
- Test real-time conversion

---

### A1.5: OpenVoice Engine (Accent Control)

**File:** `app/core/engines/openvoice_engine.py`  
**Issue:** Accent control is limited  
**Effort:** 1 day  
**Status:** ⚠️ PARTIAL

#### What Needs to be Fixed:

- Line ~863: Comment "accent control is limited to prosody adjustments"
- Needs full accent control implementation

#### Implementation Steps:

1. Research OpenVoice accent control capabilities
2. Implement full accent control if available in OpenVoice API
3. If not available, document limitation and ensure graceful degradation

#### Test:

- Test accent control functionality
- Verify prosody adjustments work

---

### A1.6-A1.11: Remaining Engine Fixes

**Lyrebird Engine** (Local model placeholder):

- Implement local voice cloning model loading
- Implement actual voice cloning logic for local mode

**Voice.ai Engine** (Local model placeholder):

- Implement local voice conversion model loading
- Implement actual voice conversion logic for local mode

**SadTalker Engine** (Placeholder features):

- Load actual SadTalker model
- Implement real face animation features

**FOMM Engine** (Source image placeholder):

- Implement actual face animation
- Load FOMM model properly

**DeepFaceLab Engine** (Placeholder structures):

- Load actual DeepFaceLab model
- Implement real face swapping

**Manifest Loader** (3 TODOs):

- Implement Python version check
- Implement dependencies check
- Implement GPU/VRAM checks

---

## 📋 A2: Backend Route Fixes

### A2.1: Workflows Route (CRITICAL)

**File:** `backend/api/routes/workflows.py`  
**Issue:** 4 TODOs, returns placeholder audio IDs  
**Effort:** 1-2 days  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Line ~364: `# TODO: Call actual synthesis API`
- Line ~374: Returns `f"placeholder_audio_{uuid.uuid4().hex[:8]}"`
- Line ~400: `# TODO: Call actual effect API`
- Line ~434: `# TODO: Call actual export API`
- Line ~461: `# TODO: Implement conditional logic`

#### Implementation Steps:

1. **Synthesis API Call:**

   - Call `/api/voice/synthesize` endpoint internally
   - Get real audio ID from response
   - Return real audio ID

2. **Effect API Call:**

   - Call `/api/effects/apply` endpoint internally
   - Get real audio ID from response
   - Return real audio ID

3. **Export API Call:**

   - Call `/api/audio/export` endpoint internally
   - Get real export file path
   - Return real export information

4. **Conditional Logic:**
   - Implement workflow conditional evaluation
   - Support if/else logic
   - Support comparison operators

#### Test:

- Test workflow execution
- Verify real audio IDs are returned
- Test conditional logic

---

### A2.2: Dataset Route (CRITICAL)

**File:** `backend/api/routes/dataset.py`  
**Issue:** Returns placeholder data with fake scores  
**Effort:** 1 day  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Line ~46: Returns placeholder results
- Line ~52: Logs "returning placeholder data"
- Line ~57-62: Generates fake scores (SNR, LUFS, quality)

#### Implementation Steps:

1. **Real Audio Analysis:**

   - Use librosa/soundfile to analyze audio files
   - Calculate real SNR using audio processing
   - Calculate real LUFS using loudness meter
   - Calculate real quality scores using quality metrics module

2. **Replace Placeholder Data:**
   - Load actual audio files
   - Perform real analysis
   - Return real scores

#### Dependencies:

- Already have librosa (used elsewhere)
- May need to add LUFS calculation library if not present

#### Test:

- Test with sample audio files
- Verify real scores are calculated
- Compare with expected values

---

### A2.3: Emotion Route (CRITICAL)

**File:** `backend/api/routes/emotion.py`  
**Issue:** Returns placeholder data  
**Effort:** 1 day  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Line ~138: Comment "return placeholder data"
- Line ~141: Logs "returning placeholder data"
- Line ~144-159: Returns hardcoded placeholder values

#### Implementation Steps:

1. **Implement Emotion Recognition:**

   - Use emotion recognition model (e.g., wav2vec2 for speech emotion)
   - Or use audio feature extraction + ML classifier
   - Calculate valence and arousal from audio features

2. **Replace Placeholder Data:**
   - Load actual audio
   - Perform real emotion analysis
   - Return real emotion scores

#### Dependencies:

```bash
# May need emotion recognition library
pip install transformers  # For wav2vec2
# Or use custom emotion recognition model
```

#### Test:

- Test with audio samples of different emotions
- Verify emotion classification is accurate

---

### A2.4-A2.10: Remaining Backend Route Fixes

**Image Search Route:**

- Integrate with image search APIs (Unsplash, Pexels, Pixabay)
- Implement local image library search

**Macros Route:**

- Implement actual macro execution engine
- Implement real macro processing logic

**Spatial Audio Route:**

- Implement HRTF filtering
- Implement binaural audio processing

**Lexicon Route:**

- Implement phoneme generation
- Implement pronunciation dictionary lookup

**Voice Cloning Wizard Route:**

- Implement actual audio file loading
- Implement real validation logic

**Deepfake Creator Route:**

- Implement actual deepfake processing
- Implement async job processing

**Effects Route:**

- Implement actual audio processing
- Implement real effect chain application

---

## 📋 A3: ViewModel Fixes

### A3.1: UpscalingViewModel (File Upload)

**File:** `src/VoiceStudio.App/ViewModels/UpscalingViewModel.cs`  
**Issue:** File upload not implemented  
**Effort:** 0.5 days  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Line ~213-225: File upload placeholder comments
- Line ~225: Shows message "file upload not yet implemented"

#### Implementation Steps:

1. Implement multipart/form-data file upload
2. Use HttpClient to upload file to backend
3. Send upload request with file content
4. Handle upload progress
5. Handle upload errors

#### Test:

- Test file upload with sample image
- Verify file is uploaded successfully
- Test error handling

---

### A3.2: DeepfakeCreatorViewModel (File Upload)

**File:** `src/VoiceStudio.App/ViewModels/DeepfakeCreatorViewModel.cs`  
**Issue:** File upload not implemented  
**Effort:** 0.5 days  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Line ~216-229: File upload placeholder comments
- Line ~229: Shows message "file upload not yet implemented"

#### Implementation Steps:

- Same as A3.1 (multipart/form-data upload)

#### Test:

- Test with source and target images/videos
- Verify files are uploaded successfully

---

### A3.3-A3.10: Remaining ViewModel Fixes

**VideoGenViewModel:**

- Implement quality metrics calculation from backend

**TrainingDatasetEditorViewModel:**

- Implement real dataset loading from training API

**RealTimeVoiceConverterViewModel:**

- Implement list endpoint for sessions

**TextHighlightingViewModel:**

- Implement audio library loading

**PronunciationLexiconViewModel:**

- Implement special synthesis endpoint that uses lexicon

**AssistantViewModel:**

- Implement projects API loading

**MixAssistantViewModel:**

- Implement projects API loading

**EmbeddingExplorerViewModel:**

- Implement audio files and voice profiles loading

---

## 📋 A4: UI Placeholder Fixes

### A4.1: AnalyzerPanel.xaml (Chart Placeholders)

**File:** `src/VoiceStudio.App/Views/Panels/AnalyzerPanel.xaml`  
**Issue:** 5 chart placeholders  
**Effort:** 1-2 days  
**Status:** ⚠️ INCOMPLETE

#### What Needs to be Fixed:

- Waveform Chart Placeholder
- Spectral Chart Placeholder
- Radar Chart Placeholder
- Loudness Chart Placeholder
- Phase Chart Placeholder

#### Implementation Steps:

1. Use WinUI 3 chart controls (e.g., WinUI Community Toolkit charts)
2. Or implement custom chart controls
3. Bind charts to audio analysis data from ViewModel
4. Implement real-time updates if needed

#### Test:

- Test with sample audio
- Verify charts display correctly
- Test real-time updates

---

### A4.2-A4.5: Remaining UI Fixes

**MacroPanel.xaml:**

- Implement actual node graph
- Replace placeholder nodes with real node system

**EffectsMixerPanel.xaml:**

- Replace fader placeholder with real fader control

**TimelinePanel.xaml:**

- Replace waveform placeholder with real waveform visualization

**ProfilesPanel.xaml:**

- Replace profile card placeholder with dynamic profile cards bound to data

---

## 📋 Execution Order Recommendation

### Week 1 (Days 1-5):

1. **Day 1:** Whisper CPP Engine (A1.1) - EASIEST
2. **Day 2:** GPT-SoVITS Engine (A1.2) - Port from old project
3. **Day 3:** MockingBird Engine (A1.3) - Research and implement
4. **Day 4-5:** Workflows Route (A2.1) + Dataset Route (A2.2)

### Week 2 (Days 6-10):

5. **Day 6:** Emotion Route (A2.3) + Image Search Route
6. **Day 7:** Remaining backend routes (Macros, Spatial Audio, Lexicon, etc.)
7. **Day 8:** ViewModel file uploads (A3.1, A3.2)
8. **Day 9:** Remaining ViewModels (A3.3-A3.10)
9. **Day 10:** UI placeholder fixes (A4.1-A4.5)

### Week 3 (Days 11-15):

10. **Days 11-14:** RVC Engine (A1.4) - COMPLEX
11. **Day 15:** Remaining engine fixes + final verification

---

## ✅ Verification Checklist

After each fix:

- [ ] No placeholders, stubs, bookmarks, or tags remain
- [ ] Code compiles/runs without errors
- [ ] Functionality works as expected
- [ ] Error handling is implemented
- [ ] Tests pass (if applicable)
- [ ] Dependencies are installed and documented

After Phase A completion:

- [ ] Comprehensive scan for all forbidden terms
- [ ] All 11 engines fixed and tested
- [ ] All 30 backend routes fixed and tested
- [ ] All 10 ViewModels fixed and tested
- [ ] All 5 UI files fixed and tested
- [ ] Zero placeholders found in codebase

---

**Last Updated:** 2025-01-28  
**Status:** READY FOR EXECUTION  
**Next Step:** Begin with A1.1 - Whisper CPP Engine (easiest fix)
