# Old Project Libraries & Tools Integration Guide
## Complete Inventory of Useful Resources from Old VoiceStudio Projects

**Date:** 2025-01-28  
**Purpose:** Catalog all useful libraries, tools, scripts, and utilities from old projects that can enhance the current VoiceStudio project

---

## 📚 **LIBRARIES TO INTEGRATE**

### **Audio Quality Enhancement Libraries** (HIGH PRIORITY)

From `requirements-audio-quality.txt`:

```python
# Advanced audio analysis
essentia-tensorflow>=1.1.1  # ⭐ NEW - Advanced audio analysis

# Noise reduction & enhancement
voicefixer>=0.1.2  # ⭐ NEW - Voice restoration
deepfilternet>=0.5.0  # ⭐ NEW - Speech enhancement

# Source separation
spleeter>=2.3.0  # ⭐ NEW - Extract voice from music

# Professional effects
pedalboard>=0.7.0  # ⭐ NEW - Audio effects chain

# Audio augmentation
audiomentations>=1.7.0  # ⭐ NEW - Dataset augmentation

# High-quality resampling
resampy>=0.4.2  # ⭐ NEW - Better resampling
pyrubberband>=0.3.0  # ⭐ NEW - Time-stretching

# Quality metrics
pesq>=0.0.4  # ⭐ NEW - Perceptual quality score
pystoi>=0.3.3  # ⭐ NEW - Speech intelligibility
```

**Status:** ⚠️ **CRITICAL MISSING LIBRARIES** - None of these are in `requirements_engines.txt`

**Current Project Has:**
- ✅ `noisereduce==3.0.2` (already have)
- ✅ `pyloudnorm==0.1.1` (already have)
- ✅ `librosa==0.11.0` (already have)
- ✅ `soundfile==0.12.1` (already have)

**Missing:**
- ❌ `essentia-tensorflow` - Advanced audio analysis
- ❌ `voicefixer` - Voice restoration
- ❌ `deepfilternet` - Speech enhancement
- ❌ `spleeter` - Source separation
- ❌ `pedalboard` - Audio effects chain
- ❌ `audiomentations` - Dataset augmentation
- ❌ `resampy` - Better resampling
- ❌ `pyrubberband` - Time-stretching
- ❌ `pesq` - Perceptual quality score
- ❌ `pystoi` - Speech intelligibility

---

### **RVC & Voice Conversion Libraries** (HIGH PRIORITY)

From `services/requirements-voice-cloning.txt`:

```python
# RVC dependencies
numba==0.58.1  # ⚠️ Check version compatibility
llvmlite==0.40.1  # ⚠️ Check version compatibility
fairseq==0.12.2  # ⭐ NEW - Required for RVC
faiss-cpu==1.7.4  # ⭐ NEW - Vector similarity search
pyworld==0.3.2  # ⭐ NEW - Vocoder features
praat-parselmouth>=0.4.3  # ⭐ NEW - Prosody analysis
```

**Status:** ⚠️ **MISSING FROM CURRENT PROJECT**

**Current Project Has:**
- ✅ `numpy==1.26.4` (already have)
- ✅ `scipy>=1.9.0` (already have)
- ✅ `librosa==0.11.0` (already have)

**Missing:**
- ❌ `fairseq==0.12.2` - Required for RVC HuBERT features
- ❌ `faiss-cpu==1.7.4` - Vector similarity search for RVC
- ❌ `pyworld==0.3.2` - Vocoder features
- ❌ `praat-parselmouth>=0.4.3` - Prosody analysis
- ❌ `numba` - Check version (may need specific version)
- ❌ `llvmlite` - Check version (may need specific version)

---

### **Advanced Audio Processing** (MEDIUM PRIORITY)

From `requirements-optional.txt`:

```python
# Voice restoration
voicefixer>=0.1.2
spleeter>=2.3.0
pedalboard>=0.7.0
pedalo>=0.4.0  # ⭐ NEW - Additional effects
deepfilternet>=0.5.0
essentia-tensorflow>=1.1.1
audiomentations>=1.7.0
```

**Status:** ⚠️ **MOSTLY MISSING**

**Current Project Has:**
- ✅ `noisereduce==3.0.2` (already have)

**Missing:**
- ❌ `voicefixer>=0.1.2`
- ❌ `spleeter>=2.3.0`
- ❌ `pedalboard>=0.7.0`
- ❌ `pedalo>=0.4.0`
- ❌ `deepfilternet>=0.5.0`
- ❌ `essentia-tensorflow>=1.1.1`
- ❌ `audiomentations>=1.7.0`

---

### **Deepfake & Video Processing** (OPTIONAL)

From `requirements-deepfake.txt`:

```python
insightface>=0.7.3  # ⭐ NEW - Face recognition
opencv-python>=4.8.0  # ⭐ NEW - Computer vision
opencv-contrib-python>=4.8.0  # ⭐ NEW - Extended OpenCV
onnxruntime>=1.15.0  # ⭐ NEW - ONNX model runtime
```

**Status:** ⚠️ **MISSING - OPTIONAL FOR FUTURE**

**Current Project Has:**
- ✅ `opencv-python>=4.5.0` (already have for image engines)

**Missing:**
- ❌ `insightface>=0.7.3` - Face recognition (for future video features)
- ❌ `opencv-contrib-python>=4.8.0` - Extended OpenCV features
- ❌ `onnxruntime>=1.15.0` - ⚠️ Actually already have this! (line 170 in requirements_engines.txt)

---

### **AI Image/Video Generation** (OPTIONAL)

From `requirements-ai-generators.txt`:

```python
diffusers  # ⭐ NEW - Stable Diffusion models
imageio>=2.31.0  # ⭐ NEW - Image/video I/O
moviepy  # ⭐ NEW - Video processing
```

**Status:** Not in current project. Useful for future image/video features.

---

### **Performance Monitoring** (MEDIUM PRIORITY)

From `services/requirements-optimized-universal.txt`:

```python
py-cpuinfo>=9.0.0  # ⭐ NEW - CPU information
GPUtil>=1.4.0  # ⭐ NEW - GPU monitoring
nvidia-ml-py>=11.0.0  # ⭐ NEW - NVIDIA GPU stats
wandb>=0.15.0  # ⭐ NEW - Experiment tracking
```

**Status:** ⚠️ **MISSING - USEFUL FOR PERFORMANCE MONITORING**

**Current Project Has:**
- ✅ `psutil` - May be included indirectly

**Missing:**
- ❌ `py-cpuinfo>=9.0.0` - CPU information
- ❌ `GPUtil>=1.4.0` - GPU monitoring
- ❌ `nvidia-ml-py>=11.0.0` - NVIDIA GPU stats
- ❌ `wandb>=0.15.0` - Experiment tracking

---

### **Advanced Utilities** (LOW PRIORITY)

From `requirements.txt`:

```python
# Already in current project (verify versions):
- resemblyzer==0.1.4  # ✅ Check if we have this
- webrtcvad==2.0.10  # ✅ Check if we have this
- umap-learn==0.5.9.post2  # ⭐ NEW - Dimensionality reduction
- spacy[ja]==3.8.7  # ⭐ NEW - NLP processing
- tensorboard==2.20.0  # ⭐ NEW - Training visualization
- prometheus-client==0.23.1  # ⭐ NEW - Metrics
- prometheus-fastapi-instrumentator==6.1.0  # ⭐ NEW - FastAPI metrics
```

**Status:** ⚠️ **PARTIALLY MISSING**

**Current Project Has:**
- ✅ `resemblyzer>=0.1.1` (already have - line 40)
- ✅ `transformers==4.57.1` (already have - line 18)
- ✅ `onnxruntime>=1.15.0` (already have - line 170)

**Missing:**
- ❌ `webrtcvad` - Voice activity detection (check if needed)
- ❌ `umap-learn` - Dimensionality reduction
- ❌ `spacy[ja]` - NLP processing
- ❌ `tensorboard` - Training visualization
- ❌ `prometheus-client` - Metrics
- ❌ `prometheus-fastapi-instrumentator` - FastAPI metrics

---

## 🛠️ **TOOLS & SCRIPTS TO INTEGRATE**

### **Audio Quality Tools** (HIGH PRIORITY)

From `C:\OldVoiceStudio\tools\`:

1. **`audio_quality_benchmark.py`** ⭐
   - Purpose: Benchmark audio quality metrics
   - Status: NOT in current project
   - Action: Copy and adapt

2. **`quality_dashboard.py`** ⭐
   - Purpose: Quality metrics dashboard
   - Status: NOT in current project
   - Action: Copy and adapt

3. **`dataset_qa.py`** ⭐
   - Purpose: Dataset quality assurance
   - Status: NOT in current project
   - Action: Copy and adapt

4. **`dataset_report.py`** ⭐
   - Purpose: Generate dataset quality reports
   - Status: NOT in current project
   - Action: Copy and adapt

5. **`benchmark_engines.py`** ⭐
   - Purpose: Benchmark voice cloning engines
   - Status: NOT in current project
   - Action: Copy and adapt

---

### **System Health & Monitoring** (MEDIUM PRIORITY)

1. **`system_health_validator.py`** ⭐
   - Purpose: Validate system health
   - Status: NOT in current project
   - Action: Copy and adapt

2. **`system_monitor.py`** ⭐
   - Purpose: System resource monitoring
   - Status: NOT in current project
   - Action: Copy and adapt

3. **`performance-monitor.py`** ⭐
   - Purpose: Performance monitoring
   - Status: NOT in current project
   - Action: Copy and adapt

4. **`profile_engine_memory.py`** ⭐
   - Purpose: Memory profiling for engines
   - Status: NOT in current project
   - Action: Copy and adapt

---

### **Training & Optimization** (MEDIUM PRIORITY)

1. **`train_ultimate.py`** ⭐
   - Purpose: Ultimate training system
   - Status: NOT in current project
   - Action: Copy and adapt

2. **`train_voice_quality.py`** ⭐
   - Purpose: Voice quality training
   - Status: NOT in current project
   - Action: Copy and adapt

3. **`config-optimizer.py`** ⭐
   - Purpose: Configuration optimization
   - Status: NOT in current project
   - Action: Copy and adapt

---

### **Audio Processing Utilities** (HIGH PRIORITY)

1. **`repair_wavs.py`** ⭐
   - Purpose: Repair corrupted WAV files
   - Status: NOT in current project
   - Action: Copy and adapt

2. **`mark_bad_clips.py`** ⭐
   - Purpose: Mark bad audio clips
   - Status: NOT in current project
   - Action: Copy and adapt

---

### **PowerShell Scripts** (LOW PRIORITY - Reference Only)

Many PowerShell scripts exist in old projects, but since current project uses WinUI 3/C#, these are less critical. However, useful for reference:

- `tools/OVERSEER_Run.ps1` - Overseer automation
- `tools/run_dashboard.ps1` - Dashboard launcher
- `tools/start_engine_gateway.ps1` - Engine gateway
- `tools/start_dev_stack.ps1` - Development stack

**Action:** Review for concepts, adapt to C# if needed.

---

## 📋 **INTEGRATION PRIORITY**

### **CRITICAL (Do First)**
1. ✅ Audio quality libraries (pesq, pystoi, voicefixer, deepfilternet)
2. ✅ RVC dependencies (fairseq, faiss-cpu, pyworld)
3. ✅ Audio quality tools (benchmark, dashboard, QA scripts)

### **HIGH PRIORITY**
4. ✅ Source separation (spleeter)
5. ✅ Professional effects (pedalboard)
6. ✅ Audio augmentation (audiomentations)
7. ✅ System health tools

### **MEDIUM PRIORITY**
8. ⚠️ Performance monitoring libraries
9. ⚠️ Training tools
10. ⚠️ Audio repair utilities

### **LOW PRIORITY (Future)**
11. ⚠️ Deepfake libraries (for future video features)
12. ⚠️ AI image/video generation (for future features)
13. ⚠️ Advanced utilities (umap-learn, spacy, tensorboard)

---

## 🔍 **VERIFICATION CHECKLIST**

Before integrating, verify:

- [ ] Check current `backend/requirements.txt` (if exists)
- [ ] Check current `app/requirements.txt` (if exists)
- [ ] Compare versions for compatibility
- [ ] Test each library installation
- [ ] Verify no conflicts with existing dependencies
- [ ] Update integration log after adding each library

---

## 📝 **NEXT STEPS**

1. ✅ **Create consolidated requirements file** - DONE: `requirements_missing_libraries.txt`
2. ✅ **Create integration plan** - DONE: `docs/governance/MISSING_LIBRARIES_INTEGRATION_PLAN_2025-01-28.md`
3. ⚠️ **Copy and adapt tools** from old projects (see integration plan)
4. ⚠️ **Test each integration** individually (see integration plan)
5. ⚠️ **Update documentation** with new dependencies (after integration)
6. ⚠️ **Add to integration log** (`COMPREHENSIVE_INTEGRATION_LOG_2025-01-28.md`)

---

## 🎯 **SUMMARY**

**Total Missing Libraries:** ~25+ critical libraries  
**Total Missing Tools:** ~15+ useful tools  
**Priority:** Audio quality libraries are CRITICAL and should be integrated immediately.

**Files Created:**
- ✅ `requirements_missing_libraries.txt` - Consolidated requirements file with all missing libraries
- ✅ `docs/governance/MISSING_LIBRARIES_INTEGRATION_PLAN_2025-01-28.md` - Step-by-step integration guide

**Estimated Integration Time:**
- Critical libraries: 2-3 hours
- High priority tools: 4-6 hours
- Medium priority: 8-12 hours
- Total: 10-14 hours (see integration plan for detailed breakdown)

**Quick Start:**
1. Review `MISSING_LIBRARIES_INTEGRATION_PLAN_2025-01-28.md`
2. Start with Phase 1 (Critical Audio Quality Libraries)
3. Install: `pip install -r requirements_missing_libraries.txt`
4. Test each library individually
5. Copy tools from old projects (see integration plan)

---

**Last Updated:** 2025-01-28  
**Status:** ✅ Inventory complete, ready for integration

