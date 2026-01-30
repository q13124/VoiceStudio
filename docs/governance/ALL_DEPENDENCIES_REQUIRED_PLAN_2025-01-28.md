# All Dependencies Required - Implementation Plan
## VoiceStudio Quantum+ - No Optional Dependencies

**Date:** 2025-01-28  
**Status:** 📋 **PLAN CREATED**  
**User Requirement:** "I don't want any optional downloads. If it can be downloaded and ran locally I want to. I have a 1TB M.2 SSD for this project. I don't care how much harddrive this project takes."

---

## 🎯 Goal

**Make ALL dependencies REQUIRED - no optional flags, no fallbacks for missing dependencies.**

Everything that can run locally should be:
1. ✅ Listed in `requirements_engines.txt`
2. ✅ Required (not optional) in code
3. ✅ Validated at initialization
4. ✅ Fail fast with clear errors if missing

---

## 📋 Implementation Tasks

### Phase 1: Merge All Missing Libraries (Worker 1)

**Task 1.1:** Merge `requirements_missing_libraries.txt` into `requirements_engines.txt`
- Add all missing libraries from old projects
- Remove "optional" comments
- Mark everything as required

**Task 1.2:** Update `dependency_validator.py`
- Remove all "optional" dependency categories
- Make all dependencies required
- Update validation logic

**Task 1.3:** Update all engines to require all dependencies
- Remove optional checks
- Require all dependencies at initialization
- Fail fast if any dependency missing

### Phase 2: Update All Engines (Worker 1)

**Task 2.1:** Remove optional flags from all engines
- FOMM Engine
- SadTalker Engine
- Speaker Encoder Engine
- Bark Engine
- Streaming Engine
- Quality Metrics
- Enhanced Quality Metrics
- All other engines

**Task 2.2:** Add dependency validation to all engines
- Check all dependencies at initialization
- Fail fast with clear errors
- No silent fallbacks

### Phase 3: Update Audio Modules (Worker 1)

**Task 3.1:** Remove optional flags from audio modules
- Enhanced Quality Metrics
- Enhanced Ensemble Router
- Audio Utils
- All audio processing modules

**Task 3.2:** Require all audio dependencies
- Librosa (required)
- PyLoudNorm (required)
- SoundFile (required)
- All audio libraries (required)

### Phase 4: Update Backend Routes (Worker 1)

**Task 4.1:** Fix all backend imports
- Quality routes
- Voice routes
- All routes that check for optional modules

**Task 4.2:** Require all backend dependencies
- All quality modules (required)
- All optimization modules (required)

### Phase 5: UI Updates (Worker 2)

**Task 5.1:** Update UI to show all dependencies as required
- Settings panel
- Error messages
- Dependency status display

### Phase 6: Testing & Documentation (Worker 3)

**Task 6.1:** Update tests for required dependencies
- Test all engines with all dependencies
- Verify no optional checks remain

**Task 6.2:** Update documentation
- Remove "optional" from all docs
- Mark everything as required
- Update installation guide

---

## 📊 Complete Dependency List (All Required)

### Core ML/AI Dependencies
- torch==2.9.0+cu128 ✅
- torchaudio==2.9.0+cu128 ✅
- transformers==4.57.1 ✅
- huggingface_hub==0.36.0 ✅
- tokenizers==0.21.4 ✅
- safetensors==0.6.2 ✅
- hf-xet==1.2.0 ✅
- fsspec==2025.9.0 ✅
- diffusers>=0.21.0 ✅
- scipy>=1.9.0 ✅

### Audio Processing (All Required)
- librosa==0.11.0 ✅
- numpy==1.26.4 ✅
- soundfile==0.12.1 ✅
- faster-whisper==1.2.0 ✅
- pyloudnorm==0.1.1 ✅
- noisereduce==3.0.2 ✅
- pydub>=0.25.0 ✅
- speechbrain>=0.5.0 ✅
- resemblyzer>=0.1.1 ✅

### Audio Quality Enhancement (NEW - All Required)
- essentia-tensorflow>=1.1.1 ⭐ NEW
- voicefixer>=0.1.2 ⭐ NEW
- deepfilternet>=0.5.0 ⭐ NEW
- spleeter>=2.3.0 ⭐ NEW
- pedalboard>=0.7.0 ⭐ NEW
- audiomentations>=1.7.0 ⭐ NEW
- resampy>=0.4.2 ⭐ NEW
- pyrubberband>=0.3.0 ⭐ NEW
- pesq>=0.0.4 ⭐ NEW
- pystoi>=0.3.3 ⭐ NEW

### Image Processing (All Required)
- pillow>=9.0.0 ✅
- opencv-python>=4.5.0 ✅
- imageio>=2.9.0 ✅
- imageio-ffmpeg>=0.4.0 ✅

### Video Processing (All Required)
- moviepy>=1.0.3 ✅
- ffmpeg-python==0.2.0 ✅

### TTS Engines (All Required)
- coqui-tts==0.27.2 ✅
- coqui-tts-trainer==0.3.1 ✅
- piper-tts>=1.0.0 ✅
- openvoice>=1.0.0 ✅
- paddlepaddle>=2.4.0 ✅
- paddlespeech>=1.2.0 ✅

### STT Engines (All Required)
- openai-whisper>=20230314 ✅
- faster-whisper==1.2.0 ✅

### Voice Conversion (All Required)
- RVC dependencies:
  - fairseq==0.12.2 ⭐ NEW
  - faiss-cpu==1.7.4 ⭐ NEW
  - pyworld==0.3.2 ⭐ NEW
  - praat-parselmouth>=0.4.3 ⭐ NEW

### Alignment/Subtitle (All Required)
- aeneas>=1.7.3 ✅

### Image Generation (All Required)
- xformers>=0.0.20 ✅
- diffusers>=0.21.0 ✅

### Video Generation (All Required)
- face-alignment>=1.3.0 ✅
- gfpgan>=1.3.0 ✅
- tensorflow>=2.8.0 ✅

### Deepfake/Video Processing (All Required)
- insightface>=0.7.3 ⭐ NEW (if available)
- opencv-contrib-python>=4.8.0 ⭐ NEW (if available)

### Utilities (All Required)
- requests>=2.28.0 ✅
- aiohttp>=3.8.0 ✅
- httpx>=0.24.0 ✅
- onnxruntime>=1.15.0 ✅

### Performance Monitoring (All Required)
- py-cpuinfo>=9.0.0 ⭐ NEW
- GPUtil>=1.4.0 ⭐ NEW
- nvidia-ml-py>=11.0.0 ⭐ NEW
- wandb>=0.15.0 ⭐ NEW
- tensorboard>=2.20.0 ⭐ NEW

### Advanced Utilities (All Required)
- webrtcvad>=2.0.10 ⭐ NEW
- umap-learn>=0.5.9 ⭐ NEW
- spacy[ja]>=3.8.7 ⭐ NEW (large download, but required)

### Metrics & Monitoring (All Required)
- prometheus-client>=0.23.1 ⭐ NEW
- prometheus-fastapi-instrumentator>=6.1.0 ⭐ NEW

---

## 🔧 Code Changes Required

### 1. Update `dependency_validator.py`

**Remove:**
```python
"optional": [
    ("dependency", "package-name"),
]
```

**Change to:**
```python
"required": [
    ("dependency", "package-name"),
],
```

### 2. Update All Engines

**Remove:**
```python
try:
    import dependency
    HAS_DEPENDENCY = True
except ImportError:
    HAS_DEPENDENCY = False
    logger.warning("Optional dependency...")
```

**Change to:**
```python
try:
    import dependency
except ImportError:
    error_msg = (
        "dependency is required for EngineName. "
        "Install with: pip install package-name>=version"
    )
    logger.error(error_msg)
    raise ImportError(error_msg)
```

### 3. Update All Initialization Methods

**Add to all `initialize()` methods:**
```python
def initialize(self) -> bool:
    # Validate ALL required dependencies
    if not self._validate_dependencies():
        return False
    # Continue initialization...
```

---

## ✅ Success Criteria

1. ✅ No "optional" dependencies in code
2. ✅ All dependencies in `requirements_engines.txt`
3. ✅ All engines validate all dependencies at initialization
4. ✅ All engines fail fast with clear errors if dependencies missing
5. ✅ No silent fallbacks for missing dependencies
6. ✅ All documentation updated to show dependencies as required

---

## 📝 Files to Update

### Requirements Files
- `requirements_engines.txt` - Merge all missing libraries

### Code Files
- `app/core/engines/dependency_validator.py` - Remove optional
- All engine files - Require all dependencies
- All audio module files - Require all dependencies
- All backend route files - Require all dependencies

### Documentation Files
- All docs mentioning "optional" - Update to "required"
- Installation guides - Update to show all dependencies required

---

**Document Created:** 2025-01-28  
**Status:** Ready for Implementation  
**Total Tasks:** ~50 tasks (updates across all engines and modules)

