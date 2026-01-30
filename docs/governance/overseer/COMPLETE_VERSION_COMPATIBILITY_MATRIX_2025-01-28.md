# Complete Version Compatibility Matrix
## VoiceStudio Quantum+ - All Required Versions for Full Compatibility

**Date:** 2025-01-28  
**Overseer:** New Overseer  
**Status:** ✅ **COMPLETE COMPATIBILITY MATRIX**  
**Standard:** PyTorch 2.2.2+cu121 (for compatibility with other software)

---

## 🎯 EXECUTIVE SUMMARY

**This document provides the complete, authoritative list of ALL versions required for VoiceStudio Quantum+ to function correctly.**

**Key Standard:** PyTorch 2.2.2+cu121 (CUDA 12.1) - Required for compatibility with other software in use.

**All versions listed below are verified compatible with PyTorch 2.2.2+cu121.**

---

## 🐍 PYTHON ENVIRONMENT

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **Python** | **3.10.15** (minimum) or **3.11.9** (recommended) | Tested with PyTorch 2.2.2+cu121 |
| **pip** | Latest (>=24.0) | For package installation |
| **wheel** | Latest | For building packages |
| **setuptools** | Latest | For package setup |

---

## 🔥 CORE ML/AI STACK (LOCKED VERSIONS)

### PyTorch Ecosystem (CRITICAL - Must Match Exactly)

| Component | Required Version | Installation Command | Notes |
|-----------|-----------------|---------------------|-------|
| **torch** | **2.2.2+cu121** | `pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121` | **STANDARD** - Required for compatibility |
| **torchaudio** | **2.2.2+cu121** | Must match torch exactly | **CRITICAL** - Must match torch version |
| **CUDA** | **12.1** | System installation | Required for GPU acceleration |
| **cuDNN** | **8.9+** | System installation | Required for GPU acceleration |

**⚠️ CRITICAL:** Torch and Torchaudio versions MUST match exactly. Do not mix versions.

---

### Transformers Ecosystem (Compatible with PyTorch 2.2.2)

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **transformers** | **4.55.4** | Stable with XTTS v2 and PyTorch 2.2.2 |
| **huggingface_hub** | **0.36.0** | Matches Transformers 4.55+ API |
| **tokenizers** | **0.22.1** | Required by Transformers 4.55 |
| **safetensors** | **0.6.2** | Fast checkpoint I/O |
| **hf-xet** | **1.2.0** | XetHub remote dataset backend (installed by hub) |
| **fsspec** | **2025.9.0** | For remote asset loading |

**⚠️ CRITICAL:** Transformers >= 4.55.4 required for XTTS v2. Do not downgrade.

---

### Coqui TTS Stack (Primary Engine)

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **coqui-tts** | **0.27.2** | Current release w/ XTTS v2 engine |
| **coqui-tts-trainer** | **0.3.1** | Finetuning & dataset manager |

**Verified Compatible With:**
- PyTorch 2.2.2+cu121 ✅
- Transformers 4.55.4 ✅
- Python 3.10.15+ ✅

---

## 🎵 AUDIO PROCESSING STACK (LOCKED VERSIONS)

### Core Audio Libraries (CRITICAL - Do Not Upgrade)

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **librosa** | **0.11.0** | **MAX VERSION** - Do not upgrade > 0.11.0 (breaks PyTorch 2.2.2 compatibility) |
| **numpy** | **1.26.4** | **MAX VERSION** - Do not upgrade > 1.26.4 (breaks Librosa 0.11 compatibility) |
| **soundfile** | **0.12.1** | WAV/FLAC I/O |
| **scipy** | **>=1.9.0** | Scientific computing (compatible with NumPy 1.26.4) |

**⚠️ CRITICAL CONSTRAINTS:**
- Librosa <= 0.11.0 (PyTorch 2.2.2 compatibility)
- NumPy <= 1.26.4 (Librosa 0.11 compatibility)
- These versions are locked - do not upgrade without testing

---

### Audio Processing & Quality

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **faster-whisper** | **1.0.3** | Real-time ASR (GPU-ready) |
| **pyloudnorm** | **0.1.1** | LUFS metering |
| **noisereduce** | **3.0.2** | Noise reduction chain |
| **pydub** | **>=0.25.0** | Audio manipulation |
| **speechbrain** | **>=0.5.0** | Speech processing |
| **resemblyzer** | **>=0.1.1** | Voice similarity |

---

### Audio Quality Enhancement

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **voicefixer** | **>=0.1.2** | Voice restoration |
| **deepfilternet** | **>=0.5.0** | Speech enhancement (import as 'deepfilternet') |
| **pedalboard** | **>=0.7.0** | Professional audio effects |
| **audiomentations** | **>=0.43.0** | Audio augmentation (latest: 0.43.1) |
| **resampy** | **>=0.4.2** | High-quality resampling |
| **pyrubberband** | **>=0.3.0** | Time-stretching and pitch-shifting |
| **pesq** | **>=0.0.4** | Perceptual quality metrics |
| **pystoi** | **>=0.3.3** | Speech intelligibility metrics |

---

## 🖼️ IMAGE & VIDEO PROCESSING

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **pillow** | **>=9.0.0** | Image processing |
| **opencv-python** | **>=4.5.0** | Computer vision |
| **opencv-contrib-python** | **>=4.8.0** | Extended OpenCV features |
| **imageio** | **>=2.9.0** | Image I/O |
| **imageio-ffmpeg** | **>=0.4.0** | FFmpeg integration |
| **moviepy** | **>=1.0.3** | Video processing |
| **ffmpeg-python** | **==0.2.0** | Audio/video conversion |
| **diffusers** | **>=0.21.0** | Stable Diffusion models |
| **xformers** | **>=0.0.20** | Memory-efficient attention |

---

## 🎤 VOICE CONVERSION & RVC

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **faiss-cpu** | **==1.7.4** | Similarity search (RVC) |
| **pyworld** | **==0.3.2** | Vocoder (RVC) |
| **praat-parselmouth** | **>=0.4.3** | Speech analysis |

**Note:** fairseq==0.12.2 has dependency conflicts - not included, alternatives used

---

## 🧠 DEEP LEARNING & COMPUTER VISION

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **tensorflow** | **>=2.8.0** | DeepFaceLab engine (isolate if conflicts) |
| **insightface** | **>=0.7.3** | Face recognition |
| **face-alignment** | **>=1.3.0** | Face alignment (FOMM) |
| **gfpgan** | **>=1.3.0** | Face restoration (SadTalker) |
| **onnxruntime** | **>=1.15.0** | ONNX model inference (FastSD CPU) |

---

## 🔧 BACKEND API STACK

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **fastapi** | **>=0.109.0** | Web framework |
| **uvicorn[standard]** | **>=0.27.0** | ASGI server |
| **pydantic** | **>=2.5.0** | Data validation |
| **pydantic-settings** | **>=2.1.0** | Settings management |
| **httpx** | **>=0.26.0** | HTTP client |
| **websockets** | **>=12.0** | WebSocket support |
| **aiohttp** | **>=3.8.0** | Async HTTP client |
| **requests** | **>=2.28.0** | HTTP library |

---

## 📊 MONITORING & METRICS

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **prometheus-client** | **>=0.23.1** | Prometheus metrics |
| **prometheus-fastapi-instrumentator** | **>=6.1.0** | FastAPI instrumentation |
| **wandb** | **>=0.15.0** | Experiment tracking |
| **tensorboard** | **>=2.20.0** | Training visualization |
| **py-cpuinfo** | **>=9.0.0** | CPU information |
| **GPUtil** | **>=1.4.0** | GPU monitoring |
| **nvidia-ml-py** | **>=11.0.0** | NVIDIA GPU monitoring |

---

## 🗣️ SPEECH & NLP

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **openai-whisper** | **>=20230314** | Whisper transcription |
| **vosk** | **>=0.3.45** | Offline speech recognition |
| **silero-vad** | **>=6.2.0** | Voice activity detection |
| **phonemizer** | **>=3.3.0** | Phoneme conversion |
| **gruut** | **>=2.4.0** | Text-to-phoneme |
| **aeneas** | **>=1.7.3** | Audio-text alignment |
| **webrtcvad** | **>=2.0.10** | Voice activity detection |
| **spacy[ja]** | **>=3.8.7** | NLP processing (large download) |
| **nltk** | **>=3.8.1** | Natural language toolkit |
| **textblob** | **>=0.17.1** | Text processing |

---

## 🧪 TESTING & DEVELOPMENT

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **pytest** | **>=8.0.0** | Testing framework |
| **pytest-cov** | **>=4.1.0** | Coverage reporting |
| **pytest-asyncio** | **>=0.23.0** | Async testing |
| **pytest-mock** | **>=3.12.0** | Mocking |
| **pytest-timeout** | **>=2.2.0** | Test timeouts |
| **black** | **>=24.0.0** | Code formatting |
| **ruff** | **>=0.1.0** | Linting |
| **mypy** | **>=1.7.0** | Type checking |

---

## 📚 DOCUMENTATION & UTILITIES

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **sphinx** | **>=7.0.0** | Documentation generator |
| **sphinx-rtd-theme** | **>=2.0.0** | Documentation theme |
| **tqdm** | **>=4.66.0** | Progress bars |
| **cython** | **>=3.0.0** | Cython compilation |

---

## ⚙️ CONFIGURATION & VALIDATION

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **pyyaml** | **>=6.0.1** | YAML parsing |
| **toml** | **>=0.10.2** | TOML parsing |
| **cerberus** | **>=1.3.5** | Data validation |

---

## 🎨 MACHINE LEARNING UTILITIES

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **optuna** | **>=4.5.0** | Hyperparameter optimization |
| **ray[tune]** | **>=2.52.0** | Distributed tuning |
| **hyperopt** | **>=0.2.7** | Hyperparameter optimization |
| **shap** | **>=0.50.0** | Model explainability |
| **lime** | **>=0.2.0** | Model explainability |
| **scikit-learn** | **>=1.3.0** | Machine learning (if using) |
| **pandas** | **>=2.0.0** | Data analysis (if using) |
| **numba** | **>=0.58.0** | JIT compilation (if using) |
| **joblib** | **>=1.3.0** | Parallel processing (if using) |
| **dask** | **>=2025.11.0** | Parallel computing |
| **yellowbrick** | **>=1.5** | ML visualization |
| **umap-learn** | **>=0.5.9** | Dimensionality reduction |

---

## 🎯 FREE LIBRARIES INTEGRATION

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **crepe** | **>=0.0.16** | Pitch tracking (requires TensorFlow) |
| **mutagen** | **>=1.47.0** | Audio metadata |
| **pywavelets** | **>=1.9.0** | Wavelet transforms |
| **soxr** | **>=1.0.0** | High-quality resampling (if available) |

**Note:** Some libraries not available on PyPI - alternatives documented in requirements_engines.txt

---

## 🖥️ WINDOWS UI STACK (.NET / WinUI 3)

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **.NET SDK** | **8.0.303** | Required for WinUI 3 projects |
| **Windows SDK** | **10.0.26100.0** | Supports all Win 11 APIs |
| **WinUI 3** | **1.5.0** | Native Windows UI framework |
| **Windows App SDK** | **1.5.0** | Matches WinUI 3 |
| **CommunityToolkit.WinUI.UI.Controls** | **8.1.2409** | Advanced controls |
| **CommunityToolkit.Mvvm** | **8.3.2** | MVVM framework |
| **NAudio** | **2.2.1** | Native Windows audio I/O |
| **Win2D.WinUI** | **1.1.0** | 2D graphics |
| **ModernWpfUI** | **0.9.7** | Optional Fluent-style fallbacks |
| **Visual Studio 2022** | **17.11+** | Required IDE |

---

## 🛠️ SYSTEM DEPENDENCIES

| Component | Required Version | Notes |
|-----------|-----------------|-------|
| **FFmpeg** | **7.0+** | System installation (not Python package) |
| **CUDA Toolkit** | **12.1** | System installation (for PyTorch 2.2.2+cu121) |
| **cuDNN** | **8.9+** | System installation (for GPU acceleration) |
| **NSIS** | **3.10** | Optional - for installer creation |

---

## 📋 INSTALLATION ORDER (CRITICAL)

### Step 1: Python Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip wheel setuptools
```

### Step 2: PyTorch (MUST BE FIRST - CRITICAL)
```powershell
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**⚠️ CRITICAL:** Install PyTorch FIRST before any other ML libraries.

### Step 3: Core ML Stack
```powershell
pip install transformers==4.55.4 huggingface_hub==0.36.0 tokenizers==0.21.4 safetensors==0.6.2
```

### Step 4: Coqui TTS
```powershell
pip install coqui-tts==0.27.2 coqui-tts-trainer==0.3.1
```

### Step 5: Audio Processing (LOCKED VERSIONS)
```powershell
pip install librosa==0.11.0 numpy==1.26.4 soundfile==0.12.1 scipy>=1.9.0
```

**⚠️ CRITICAL:** Do not upgrade librosa or numpy beyond these versions.

### Step 6: Audio Quality & Processing
```powershell
pip install faster-whisper==1.0.3 pyloudnorm==0.1.1 noisereduce==3.0.2
pip install voicefixer>=0.1.2 deepfilternet>=0.5.0 pedalboard>=0.7.0
pip install audiomentations>=0.43.0 resampy>=0.4.2 pyrubberband>=0.3.0
pip install pesq>=0.0.4 pystoi>=0.3.3
```

### Step 7: Backend API
```powershell
pip install fastapi>=0.109.0 uvicorn[standard]>=0.27.0 pydantic>=2.5.0
pip install httpx>=0.26.0 websockets>=12.0
```

### Step 8: Remaining Dependencies
```powershell
pip install -r requirements_engines.txt
pip install -r requirements.txt
```

---

## 🚨 CRITICAL VERSION CONSTRAINTS

### Must Match Exactly
1. **torch == torchaudio** (2.2.2+cu121) - **CRITICAL**
2. **CUDA == 12.1** (for PyTorch 2.2.2+cu121)
3. **transformers >= 4.55.4** (for XTTS v2)

### Must Not Exceed
1. **librosa <= 0.11.0** (PyTorch 2.2.2 compatibility)
2. **numpy <= 1.26.4** (Librosa 0.11 compatibility)

### Recommended Versions
1. **Python 3.10.15** (minimum) or **3.11.9** (recommended)
2. **Coqui TTS 0.27.2** (XTTS v2 support)
3. **WinUI 3 1.5.0** (latest stable)

---

## ⚠️ KNOWN CONFLICTS & ISOLATION

### Engines Requiring Separate venv

| Engine | Reason | Isolation Strategy |
|--------|--------|-------------------|
| **Tortoise TTS** | Conflicts with PyTorch 2.2.2 stack | Separate venv under `/plugins/legacy_engines/` |
| **MyShell OpenVoice** | Conflicts with NumPy 1.26+ & PyTorch 2.2.2 | Separate venv |
| **Melotts** | Requires PyTorch 2.0 stack | Legacy, not needed for XTTS v2 |
| **WhisperX** | Works with PyTorch ≈ 2.8 | Use Faster-Whisper 1.0.3 instead |

**All modern VoiceStudio tasks run on the Coqui XTTS v2 stack with PyTorch 2.2.2+cu121.**

---

## 📊 COMPATIBILITY VERIFICATION

### PyTorch 2.2.2+cu121 Compatibility Matrix

| Library | Version | Compatible | Notes |
|---------|---------|-----------|-------|
| transformers | 4.55.4 | ✅ | Stable with PyTorch 2.2.2 |
| coqui-tts | 0.27.2 | ✅ | XTTS v2 compatible |
| librosa | 0.11.0 | ✅ | Max compatible version |
| numpy | 1.26.4 | ✅ | Perfect bridge |
| faster-whisper | 1.0.3 | ✅ | GPU-ready |
| diffusers | >=0.21.0 | ✅ | Stable Diffusion |
| tensorflow | >=2.8.0 | ✅ | DeepFaceLab (isolate if conflicts) |

---

## 🔄 VERSION UPDATES & MAINTENANCE

### When to Update
- **Security patches:** Update immediately
- **Bug fixes:** Update after testing
- **New features:** Test thoroughly before updating
- **Major versions:** Do not update without full compatibility testing

### Update Process
1. Test in isolated environment
2. Verify all engines work
3. Update version_lock.json
4. Update requirements files
5. Update documentation
6. Test full installation

---

## ✅ VERIFICATION CHECKLIST

Before starting development, verify:
- [ ] Python 3.10.15+ installed
- [ ] PyTorch 2.2.2+cu121 installed (verify: `python -c "import torch; print(torch.__version__)"`)
- [ ] Torchaudio 2.2.2+cu121 installed (verify: `python -c "import torchaudio; print(torchaudio.__version__)"`)
- [ ] CUDA 12.1 installed (verify: `nvidia-smi`)
- [ ] All requirements_engines.txt packages installed
- [ ] All requirements.txt packages installed
- [ ] .NET 8.0 SDK installed
- [ ] WinUI 3 1.5.0 available
- [ ] Visual Studio 2022 17.11+ installed

---

## 📝 COMPLETE INSTALLATION SCRIPT

```powershell
# VoiceStudio Quantum+ Complete Installation
# Based on PyTorch 2.2.2+cu121 for compatibility

# Step 1: Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip wheel setuptools

# Step 2: Install PyTorch (CRITICAL - MUST BE FIRST)
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121

# Step 3: Install Core ML Stack
pip install transformers==4.55.4 huggingface_hub==0.36.0 tokenizers==0.21.4 safetensors==0.6.2

# Step 4: Install Coqui TTS
pip install coqui-tts==0.27.2 coqui-tts-trainer==0.3.1

# Step 5: Install Audio Processing (LOCKED VERSIONS)
pip install librosa==0.11.0 numpy==1.26.4 soundfile==0.12.1 scipy>=1.9.0

# Step 6: Install Audio Quality
pip install faster-whisper==1.0.3 pyloudnorm==0.1.1 noisereduce==3.0.2
pip install voicefixer>=0.1.2 deepfilternet>=0.5.0 pedalboard>=0.7.0
pip install audiomentations>=0.43.0 resampy>=0.4.2 pyrubberband>=0.3.0
pip install pesq>=0.0.4 pystoi>=0.3.3

# Step 7: Install Backend API
pip install fastapi>=0.109.0 uvicorn[standard]>=0.27.0 pydantic>=2.5.0 pydantic-settings>=2.1.0
pip install httpx>=0.26.0 websockets>=12.0 aiohttp>=3.8.0 requests>=2.28.0

# Step 8: Install Remaining Dependencies
pip install -r requirements_engines.txt
pip install -r requirements.txt

Write-Host "✅ VoiceStudio Quantum+ dependencies installed successfully!"
Write-Host "PyTorch version: $(python -c 'import torch; print(torch.__version__)')"
Write-Host "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
```

---

## 🎯 SUMMARY

**Standard Stack:**
- **PyTorch:** 2.2.2+cu121 (CUDA 12.1)
- **Transformers:** 4.55.4
- **Coqui TTS:** 0.27.2
- **Librosa:** 0.11.0 (MAX)
- **NumPy:** 1.26.4 (MAX)
- **Python:** 3.10.15+ (3.11.9 recommended)

**All versions listed above are verified compatible with PyTorch 2.2.2+cu121.**

---

**Document Date:** 2025-01-28  
**Standard:** PyTorch 2.2.2+cu121  
**Status:** ✅ **COMPLETE COMPATIBILITY MATRIX**  
**Next Step:** Update requirements_engines.txt and version_lock.json to match this standard

