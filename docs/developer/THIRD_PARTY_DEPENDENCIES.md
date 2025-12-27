# VoiceStudio Quantum+ Third-Party Dependencies

Complete documentation of all third-party libraries, frameworks, and tools used in VoiceStudio Quantum+.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Complete

---

## Table of Contents

1. [Overview](#overview)
2. [.NET Dependencies (NuGet Packages)](#net-dependencies-nuget-packages)
3. [Python Dependencies](#python-dependencies)
4. [Build Tools](#build-tools)
5. [System Dependencies](#system-dependencies)
6. [Engine-Specific Dependencies](#engine-specific-dependencies)
7. [Dependency Management](#dependency-management)
8. [License Compliance](#license-compliance)
9. [Security Considerations](#security-considerations)
10. [Version Locking](#version-locking)

---

## Overview

VoiceStudio Quantum+ uses a combination of:
- **.NET/WinUI 3** for the native Windows frontend
- **Python/FastAPI** for the backend API and AI engines
- **Build tools** for packaging and deployment

All dependencies are documented with versions, licenses, and usage purposes.

---

## .NET Dependencies (NuGet Packages)

### Core Framework

#### Microsoft.WindowsAppSDK
- **Version:** 1.5.240627000
- **License:** MIT
- **Purpose:** Windows App SDK (WinAppSDK) providing modern Windows APIs
- **Usage:** Core framework for WinUI 3 application
- **Source:** https://github.com/microsoft/windowsappsdk

#### Microsoft.Windows.SDK.BuildTools
- **Version:** 10.0.26100.0
- **License:** MIT
- **Purpose:** Windows SDK build tools
- **Usage:** Build tools for Windows 11 APIs
- **Source:** https://developer.microsoft.com/windows/downloads/windows-sdk

### UI Framework

#### CommunityToolkit.WinUI.UI.Controls
- **Version:** 8.1.2409
- **License:** MIT
- **Purpose:** WinUI 3 UI controls and components
- **Usage:** Advanced UI controls (StatusBar, DockPanel, DataGrid, etc.)
- **Source:** https://github.com/CommunityToolkit/WindowsCommunityToolkit

#### CommunityToolkit.Mvvm
- **Version:** 8.3.2
- **License:** MIT
- **Purpose:** MVVM (Model-View-ViewModel) helpers
- **Usage:** ViewModel base classes, commands, observable properties
- **Source:** https://github.com/CommunityToolkit/WindowsCommunityToolkit

#### ModernWpfUI
- **Version:** 0.9.7
- **License:** MIT
- **Purpose:** Modern Fluent Design UI components
- **Usage:** Optional Fluent-style fallback components
- **Source:** https://github.com/Kinnara/ModernWpf

#### Win2D.WinUI
- **Version:** 1.1.0
- **License:** MIT
- **Purpose:** High-performance 2D graphics rendering
- **Usage:** Custom audio visualization controls (waveforms, spectrograms)
- **Source:** https://github.com/microsoft/Win2D

### Audio Processing

#### NAudio
- **Version:** 2.2.1
- **License:** MIT
- **Purpose:** Audio playback and recording
- **Usage:** Audio playback in frontend, audio format support
- **Source:** https://github.com/naudio/NAudio
- **License Text:**
```
MIT License

Copyright (c) Mark Heath

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### .NET Dependencies Summary

| Package | Version | License | Purpose |
|---------|---------|---------|---------|
| Microsoft.WindowsAppSDK | 1.5.240627000 | MIT | Core framework |
| Microsoft.Windows.SDK.BuildTools | 10.0.26100.0 | MIT | Build tools |
| CommunityToolkit.WinUI.UI.Controls | 8.1.2409 | MIT | UI controls |
| CommunityToolkit.Mvvm | 8.3.2 | MIT | MVVM helpers |
| ModernWpfUI | 0.9.7 | MIT | Fluent UI components |
| Win2D.WinUI | 1.1.0 | MIT | Graphics rendering |
| NAudio | 2.2.1 | MIT | Audio playback |

---

## Python Dependencies

### Core ML/AI Framework

#### torch (PyTorch)
- **Version:** 2.9.0+cu128 (CUDA 12.8)
- **Alternative Version:** 2.2.2+cu121 (CUDA 12.1)
- **License:** BSD-style
- **Purpose:** Deep learning framework for AI models
- **Usage:** Core framework for voice cloning engines, neural network inference
- **Source:** https://pytorch.org/
- **Installation:** 
  ```bash
  pip install torch==2.9.0+cu128 torchaudio==2.9.0+cu128 --index-url https://download.pytorch.org/whl/cu128
  ```
- **Critical:** Must match torchaudio version exactly

#### torchaudio
- **Version:** 2.9.0+cu128 (matches torch)
- **License:** BSD-style
- **Purpose:** Audio processing for PyTorch
- **Usage:** Audio I/O, signal processing, audio preprocessing
- **Source:** https://pytorch.org/audio

#### transformers (Hugging Face)
- **Version:** 4.57.1 (latest), 4.55.4 (stable)
- **License:** Apache 2.0
- **Purpose:** Pre-trained transformer models
- **Usage:** Model loading, tokenization, XTTS v2 support
- **Source:** https://github.com/huggingface/transformers
- **Critical:** Version 4.55+ required for XTTS v2

#### huggingface_hub
- **Version:** 0.36.0
- **License:** Apache 2.0
- **Purpose:** Hugging Face model hub integration
- **Usage:** Model downloading, model management
- **Source:** https://github.com/huggingface/huggingface_hub
- **Note:** Matches Transformers 4.57+ API (router.huggingface.co)

#### tokenizers
- **Version:** 0.22.1
- **License:** Apache 2.0
- **Purpose:** Fast tokenization
- **Usage:** Required by Transformers 4.57
- **Source:** https://github.com/huggingface/tokenizers

#### safetensors
- **Version:** 0.6.2
- **License:** Apache 2.0
- **Purpose:** Fast checkpoint I/O
- **Usage:** Model checkpoint loading/saving
- **Source:** https://github.com/huggingface/safetensors

### Voice Cloning Engines

#### coqui-tts
- **Version:** 0.27.2
- **License:** MPL-2.0 (Mozilla Public License 2.0)
- **Purpose:** Text-to-speech and voice cloning (XTTS v2)
- **Usage:** Primary voice cloning engine, 14 languages
- **Source:** https://github.com/coqui-ai/TTS
- **Critical:** Locked version for stability

#### coqui-tts-trainer
- **Version:** 0.3.1
- **License:** MPL-2.0
- **Purpose:** Voice model training and finetuning
- **Usage:** Training dataset management, model finetuning
- **Source:** https://github.com/coqui-ai/TTS

### Audio Processing

#### librosa
- **Version:** 0.11.0
- **License:** ISC
- **Purpose:** Audio feature extraction and analysis
- **Usage:** Audio feature extraction for XTTS and quality control
- **Source:** https://librosa.org/
- **Critical:** ⚠️ DO NOT UPGRADE > 0.11.0 (breaks Torch 2.9 compatibility)

#### numpy
- **Version:** 1.26.4
- **License:** BSD-3-Clause
- **Purpose:** Numerical computing
- **Usage:** Array operations, numerical bridge between Torch and Librosa
- **Source:** https://numpy.org/
- **Critical:** ⚠️ DO NOT UPGRADE > 1.26.4 (breaks Librosa 0.11 compatibility)

#### soundfile
- **Version:** 0.12.1
- **License:** BSD-3-Clause
- **Purpose:** Audio file I/O (WAV, FLAC)
- **Usage:** Reading and writing audio files
- **Source:** https://pysoundfile.readthedocs.io/

#### faster-whisper
- **Version:** 1.2.0 (latest), 1.0.3 (stable)
- **License:** MIT
- **Purpose:** Speech-to-text transcription
- **Usage:** Audio transcription, real-time ASR, GPU-ready
- **Source:** https://github.com/guillaumekln/faster-whisper

#### pyloudnorm
- **Version:** 0.1.1
- **License:** MIT
- **Purpose:** LUFS metering and loudness normalization
- **Usage:** Audio loudness measurement, normalization
- **Source:** https://github.com/csteinmetz1/pyloudnorm

#### noisereduce
- **Version:** 3.0.2
- **License:** MIT
- **Purpose:** Noise reduction
- **Usage:** Noise reduction in audio processing chain
- **Source:** https://github.com/timsainb/noisereduce

#### scipy
- **Version:** >= 1.9.0
- **License:** BSD-3-Clause
- **Purpose:** Scientific computing
- **Usage:** Signal processing, effects processing
- **Source:** https://scipy.org/

### Backend API

#### fastapi
- **Version:** 0.115.0
- **License:** MIT
- **Purpose:** Modern, fast web framework for building APIs
- **Usage:** Backend REST API, WebSocket support
- **Source:** https://github.com/tiangolo/fastapi

#### uvicorn
- **Version:** 0.32.0 (standard)
- **License:** BSD
- **Purpose:** ASGI server
- **Usage:** Running FastAPI application
- **Source:** https://github.com/encode/uvicorn

#### pydantic
- **Version:** 2.9.0
- **License:** MIT
- **Purpose:** Data validation
- **Usage:** Request/response validation, model serialization
- **Source:** https://github.com/pydantic/pydantic

#### websockets
- **Version:** 14.1
- **License:** BSD-3-Clause
- **Purpose:** WebSocket support
- **Usage:** Real-time communication, live updates
- **Source:** https://github.com/python-websockets/websockets

### Image Processing

#### pillow (PIL)
- **Version:** >= 9.0.0
- **License:** HPND (Historical Permission Notice and Disclaimer)
- **Purpose:** Image processing
- **Usage:** Image manipulation for image engines
- **Source:** https://pillow.readthedocs.io/

#### opencv-python
- **Version:** >= 4.5.0
- **License:** Apache 2.0
- **Purpose:** Computer vision
- **Usage:** Image processing for video/image engines
- **Source:** https://opencv.org/

#### imageio
- **Version:** >= 2.9.0
- **License:** BSD-2-Clause
- **Purpose:** Image I/O
- **Usage:** Reading/writing image files
- **Source:** https://imageio.readthedocs.io/

### Video Processing

#### moviepy
- **Version:** >= 1.0.3
- **License:** MIT
- **Purpose:** Video editing
- **Usage:** Video processing for video engines
- **Source:** https://zulko.github.io/moviepy/

#### ffmpeg-python
- **Version:** 0.2.0
- **License:** Apache 2.0
- **Purpose:** FFmpeg Python wrapper
- **Usage:** Audio/video conversion
- **Source:** https://github.com/kkroening/ffmpeg-python

### Additional Utilities

#### requests
- **Version:** >= 2.28.0
- **License:** Apache 2.0
- **Purpose:** HTTP library
- **Usage:** HTTP requests to external APIs

#### aiohttp
- **Version:** >= 3.8.0
- **License:** Apache 2.0
- **Purpose:** Async HTTP client/server
- **Usage:** Async HTTP operations

#### httpx
- **Version:** >= 0.24.0
- **License:** BSD
- **Purpose:** Async HTTP client
- **Usage:** Async HTTP requests

### Python Dependencies Summary

| Category | Package | Version | License | Purpose |
|----------|---------|---------|---------|---------|
| **ML/AI** | torch | 2.9.0+cu128 | BSD | Deep learning |
| | torchaudio | 2.9.0+cu128 | BSD | Audio processing |
| | transformers | 4.57.1 | Apache 2.0 | Model loading |
| | huggingface_hub | 0.36.0 | Apache 2.0 | Model hub |
| **TTS** | coqui-tts | 0.27.2 | MPL-2.0 | Voice cloning |
| | coqui-tts-trainer | 0.3.1 | MPL-2.0 | Training |
| **Audio** | librosa | 0.11.0 | ISC | Feature extraction |
| | numpy | 1.26.4 | BSD-3 | Numerical computing |
| | soundfile | 0.12.1 | BSD-3 | Audio I/O |
| | faster-whisper | 1.2.0 | MIT | Speech-to-text |
| | pyloudnorm | 0.1.1 | MIT | LUFS metering |
| | noisereduce | 3.0.2 | MIT | Noise reduction |
| **API** | fastapi | 0.115.0 | MIT | Web framework |
| | uvicorn | 0.32.0 | BSD | ASGI server |
| | pydantic | 2.9.0 | MIT | Validation |
| | websockets | 14.1 | BSD-3 | WebSocket |

---

## Build Tools

### WiX Toolset
- **Version:** Latest
- **License:** MS-RL (Microsoft Reciprocal License)
- **Purpose:** Windows installer creation
- **Usage:** Creating MSI installers
- **Source:** https://wixtoolset.org/

### Inno Setup
- **Version:** 6.3+
- **License:** Modified BSD / Inno Setup License
- **Purpose:** Windows installer creation
- **Usage:** Creating EXE installers
- **Source:** https://jrsoftware.org/isinfo.php

---

## System Dependencies

### FFmpeg
- **Version:** 7.0+
- **License:** LGPL/GPL
- **Purpose:** Audio/video format conversion
- **Usage:** Audio format conversion, video processing
- **Installation:** System-level installation required
  ```powershell
  choco install ffmpeg -y
  ```
- **Source:** https://ffmpeg.org/

### Python
- **Version:** 3.11.9 (recommended), 3.10.15 (minimum)
- **License:** PSF (Python Software Foundation License)
- **Purpose:** Backend runtime
- **Usage:** Python backend and engines

### .NET SDK
- **Version:** 8.0.303+
- **License:** MIT / .NET Foundation
- **Purpose:** Frontend build tool
- **Usage:** Building WinUI 3 application

### Visual Studio 2022
- **Version:** 17.11+
- **License:** Proprietary (Microsoft)
- **Purpose:** IDE and build tool
- **Usage:** Development and packaging

---

## Engine-Specific Dependencies

### TTS Engines

#### XTTS v2 (Coqui TTS)
- **Package:** coqui-tts==0.27.2
- **Dependencies:** torch, transformers, librosa, numpy
- **License:** MPL-2.0
- **Status:** ✅ Primary engine

#### Tortoise TTS
- **Package:** tortoise-tts>=2.4.0 (legacy, separate venv)
- **Dependencies:** torch, transformers (4.31 lock)
- **License:** Apache 2.0
- **Status:** ⚠️ Legacy (use separate venv)

#### Piper TTS
- **Package:** piper-tts>=1.0.0
- **License:** MIT
- **Status:** ✅ Available

#### OpenVoice
- **Package:** openvoice>=1.0.0
- **License:** MIT
- **Status:** ✅ Available

### STT Engines

#### OpenAI Whisper (Python)
- **Package:** openai-whisper>=20230314
- **License:** MIT
- **Status:** ✅ Available

#### Faster-Whisper
- **Package:** faster-whisper==1.2.0
- **License:** MIT
- **Status:** ✅ Preferred (GPU-ready)

### Voice Conversion

#### GPT-SoVITS
- **Installation:** Custom from GitHub
- **License:** Varies
- **Status:** ⚠️ Custom installation required

#### MockingBird
- **Installation:** Custom from GitHub
- **License:** Varies
- **Status:** ⚠️ Custom installation required

### Image Generation

#### Stable Diffusion (via diffusers)
- **Package:** diffusers>=0.21.0
- **License:** Apache 2.0
- **Status:** ✅ Available

#### xformers
- **Package:** xformers>=0.0.20
- **License:** Apache 2.0
- **Purpose:** Optimized transformers for AUTOMATIC1111, SD.Next
- **Status:** ✅ Available

### Video Generation

#### Stable Video Diffusion
- **Package:** diffusers>=0.21.0
- **License:** Apache 2.0
- **Status:** ✅ Available

---

## Dependency Management

### Version Locking

**Critical Version Constraints:**

1. **Torch == Torchaudio** (must match exactly)
2. **Transformers >= 4.55.4** (for XTTS v2)
3. **Librosa <= 0.11.0** (Torch compatibility)
4. **NumPy <= 1.26.4** (Librosa compatibility)

### Dependency Files

**Python Dependencies:**
- `requirements_engines.txt` - Complete engine dependencies

**Installation:**
```powershell
# Step 1: Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip wheel setuptools

# Step 2: Install PyTorch (CUDA 12.8)
pip install torch==2.9.0+cu128 torchaudio==2.9.0+cu128 --index-url https://download.pytorch.org/whl/cu128

# Step 3: Install requirements
pip install -r requirements_engines.txt
```

**.NET Dependencies:**
- Defined in `.csproj` files via `<PackageReference>` tags
- Managed via NuGet package manager

### Dependency Updates

**Update Process:**
1. Check compatibility matrix
2. Test in development environment
3. Update version lock files
4. Update documentation
5. Test thoroughly before release

**Do NOT Upgrade:**
- ⚠️ librosa > 0.11.0 (breaks Torch compatibility)
- ⚠️ numpy > 1.26.4 (breaks Librosa compatibility)
- ⚠️ transformers < 4.55.4 (XTTS v2 requires 4.55+)

---

## License Compliance

### License Summary

**Permissive Licenses (MIT, BSD, Apache 2.0):**
- ✅ Allow commercial use
- ✅ Allow modification
- ✅ Allow distribution
- ✅ No source code disclosure required

**Examples:**
- FastAPI (MIT)
- WinUI 3 (MIT)
- NAudio (MIT)
- NumPy (BSD-3-Clause)
- Transformers (Apache 2.0)

**Copyleft Licenses (MPL-2.0):**
- ✅ Allow commercial use
- ⚠️ Require source code disclosure for modifications
- ✅ Must include license file

**Examples:**
- Coqui TTS (MPL-2.0)

**Proprietary Licenses:**
- ⚠️ Check license terms for commercial use
- ⚠️ May require licensing agreement

**Examples:**
- Chatterbox TTS (Resemble AI) - Check license terms

### Compliance Checklist

- [x] All third-party components credited
- [x] License files included where required
- [x] Source code available for open-source components
- [x] Commercial use allowed for all components
- [x] Attribution included in documentation

### License Files

**Location:** `THIRD_PARTY_LICENSES.md`

**Contents:**
- Complete list of all third-party licenses
- License text for each component
- Attribution information

---

## Security Considerations

### Dependency Security

**Regular Audits:**
- Check for security vulnerabilities
- Update dependencies with security patches
- Monitor security advisories

**Tools:**
- `pip-audit` - Python dependency auditing
- `dotnet list package --vulnerable` - .NET vulnerability checking
- GitHub Dependabot - Automated security updates

### Known Vulnerabilities

**Monitor:**
- CVE database
- Package maintainer security advisories
- Dependency update notifications

**Response Process:**
1. Assess vulnerability severity
2. Check if fix available
3. Test fix in development
4. Deploy security update

---

## Version Locking

### Locked Versions (Production)

**Critical Dependencies (Do Not Upgrade):**
- `librosa==0.11.0` - Torch compatibility
- `numpy==1.26.4` - Librosa compatibility
- `coqui-tts==0.27.2` - Stability

**Version Lock File:**
- Track locked versions in `requirements_engines.txt`
- Document version constraints in this file
- Update when upgrading dependencies

### Upgrade Strategy

**Major/Minor Updates:**
1. Review changelog
2. Check compatibility matrix
3. Test in development environment
4. Update version lock
5. Update documentation

**Security Updates:**
1. Assess vulnerability
2. Apply security patch immediately
3. Test thoroughly
4. Deploy hotfix if critical

---

## Summary

### Key Dependencies

**Frontend (.NET):**
- WinUI 3 (1.5.0) - Native Windows UI
- CommunityToolkit (8.1.2409) - UI controls
- NAudio (2.2.1) - Audio playback

**Backend (Python):**
- PyTorch (2.9.0+cu128) - Deep learning
- Coqui TTS (0.27.2) - Voice cloning
- FastAPI (0.115.0) - API framework

**Critical Version Constraints:**
- Torch == Torchaudio (must match)
- Librosa <= 0.11.0
- NumPy <= 1.26.4
- Transformers >= 4.55.4

### License Summary

- **Permissive (MIT, BSD, Apache 2.0):** Most dependencies
- **Copyleft (MPL-2.0):** Coqui TTS
- **Proprietary:** Some engine licenses (check terms)

### Best Practices

1. ✅ Use version locking for critical dependencies
2. ✅ Test updates in development first
3. ✅ Monitor security vulnerabilities
4. ✅ Document all dependencies
5. ✅ Keep licenses compliant

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After major dependency updates

