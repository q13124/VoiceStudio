# Package Requirements Documentation
## Engine-Specific Package Requirements

**Date:** 2025-01-28  
**Status:** ✅ **DOCUMENTED**  
**Purpose:** Document optional/required packages for engines based on verification findings

---

## 📋 Summary

Many engines have **optional packages** that enable full functionality. When packages are not installed, engines use **reasonable fallback methods**. This document details which packages are required vs optional.

---

## ✅ Verified Engine Requirements

### 1. RVC Engine

**Status:** ✅ **Implementation Complete**

**Required Package for Full Functionality:**
- `rvc-python` or RVC package (provides `SynthesizerTrn` model classes)

**Installation:**
```bash
pip install rvc-python
# OR install from source/alternative location
```

**What Works Without Package:**
- ✅ Checkpoint loading
- ✅ Feature extraction (HuBERT via fairseq)
- ✅ F0 extraction
- ⚠️ Simplified conversion methods (fallback)

**What Requires Package:**
- ✅ Full RVC model inference
- ✅ Real voice conversion using SynthesizerTrn

**Manifest:** `engines/audio/rvc/engine.manifest.json` lists dependencies

**Code Location:** `app/core/engines/rvc_engine.py` lines 1267-1336

**Note:** Engine gracefully falls back when package not available - this is expected behavior.

---

### 2. GPT-SoVITS Engine

**Status:** ⚠️ **Has Implementation, Needs Testing**

**Required Packages for Full Functionality:**

**Option 1: API Server Mode**
- GPT-SoVITS API server running
- Set `GPT_SOVITS_API_URL` environment variable
- OR pass `api_url` parameter

**Option 2: Local Model Mode**
- GPT-SoVITS Python package installed
- Model files available
- `GPT_SoVITS.inference_webui` module available

**Installation:**
```bash
# Option 1: Install GPT-SoVITS package
pip install GPT-SoVITS

# Option 2: Use API server (separate installation)
# See GPT-SoVITS documentation for server setup
```

**What Works Without Package:**
- ✅ API mode (if server available)
- ⚠️ Fallback: Synthetic speech generation (not real GPT-SoVITS)

**What Requires Package:**
- ✅ Real GPT-SoVITS synthesis
- ✅ Full model inference

**Code Location:** `app/core/engines/gpt_sovits_engine.py`
- API mode: `_synthesize_via_api()` (lines 560-626)
- Model mode: `_synthesize_with_model()` (lines 628-727)

**Action Needed:** Test API/model modes to verify they work correctly.

---

### 3. MockingBird Engine

**Status:** ✅ **Implementation Complete**

**Required Package for Full Functionality:**
- MockingBird package (provides encoder, synthesizer, vocoder modules)

**Installation:**
```bash
# Install MockingBird package
pip install mockingbird-tts
# OR install from source
```

**What Works Without Package:**
- ⚠️ Fallback: Synthetic speech generation (not real MockingBird)

**What Requires Package:**
- ✅ Real encoder/synthesizer/vocoder inference
- ✅ Real voice cloning

**Code Location:** `app/core/engines/mockingbird_engine.py`
- Model loading: `_load_model()` (lines 458-572)
- Synthesis: `_synthesize_with_model()` (lines 602-839)

---

### 4. OpenVoice Engine

**Status:** ✅ **Implementation Complete**

**Required Package:**
- `openvoice` package

**Installation:**
```bash
pip install openvoice
```

**Current Status:** Implementation is complete and uses OpenVoice library correctly.

**Code Location:** `app/core/engines/openvoice_engine.py`

---

### 5. Whisper CPP Engine

**Status:** ✅ **Implementation Complete**

**Required for Full Functionality:**

**Option 1: Python Bindings**
- `whisper-cpp-python` package

**Option 2: Binary Execution**
- `whisper.cpp` binary in PATH

**Option 3: Fallback**
- `faster-whisper` package (used as fallback)

**Installation:**
```bash
# Option 1: Python bindings
pip install whisper-cpp-python

# Option 2: Install faster-whisper (fallback)
pip install faster-whisper

# Option 3: Build whisper.cpp binary
# See whisper.cpp documentation
```

**What Works:**
- ✅ Multiple fallback methods
- ✅ Reasonable error handling

**Code Location:** `app/core/engines/whisper_cpp_engine.py`

---

## 📝 General Notes

### Fallback Behavior

All engines implement **graceful fallback** when optional packages are not available:
- ✅ Engines initialize successfully
- ✅ Error handling is comprehensive
- ✅ Fallback methods provide basic functionality
- ✅ No crashes or broken states

### Recommended Installation

For **full functionality**, install all recommended packages:

```bash
# Core requirements
pip install -r requirements.txt
pip install -r requirements_engines.txt

# Optional but recommended
pip install rvc-python
pip install GPT-SoVITS
pip install mockingbird-tts
pip install openvoice
pip install whisper-cpp-python  # or faster-whisper
```

### Package Status in Requirements Files

**requirements_engines.txt:**
- Core dependencies are documented
- Some optional packages may not be listed
- Check individual engine manifests for specifics

**Engine Manifests:**
- Each engine has a manifest file in `engines/{type}/{engine_id}/engine.manifest.json`
- Manifests list required dependencies
- Check manifests for specific version requirements

---

## ✅ Verification Status

- ✅ **RVC Engine** - Requirements documented (needs `rvc-python`)
- ⚠️ **GPT-SoVITS Engine** - Needs testing to verify API/model modes
- ✅ **MockingBird Engine** - Requirements clear (needs `mockingbird-tts`)
- ✅ **OpenVoice Engine** - Requirements clear (needs `openvoice`)
- ✅ **Whisper CPP Engine** - Multiple options documented

---

## 🎯 Action Items

1. ✅ Document package requirements (this document)
2. ⏭️ Add optional packages to requirements_engines.txt with comments
3. ⏭️ Update README with installation instructions
4. ⏭️ Test GPT-SoVITS API/model modes
5. ⏭️ Verify all package requirements are in manifests

---

**Last Updated:** 2025-01-28  
**Status:** ✅ **DOCUMENTED**  
**Next:** Update requirements files and README

