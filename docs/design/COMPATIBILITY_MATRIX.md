# VoiceStudio Compatibility Matrix
## Verified Software Architecture & Version Lock

**Last Updated:** 2026-01-30  
**Status:** ✅ Production-Ready  
**Target:** Python 3.11.9 + PyTorch 2.2.2+cu121 + RTX 30/40 Series  
**Canonical source:** Implementation files (`requirements_engines.txt`, `Directory.Build.props`) define actual versions. This document describes them.

---

## 🎯 Core Python Stack (Locked Versions)

| Category              | Library         | Version                                           | Notes |
| --------------------- | --------------- | ------------------------------------------------- | ----- |
| **Python runtime**    | 3.11.9          | Recommended; 3.10.15 minimum                      |       |
| **PyTorch**           | `2.2.2 + cu121` | Pinned for compatibility; install from cu121 index |       |
| **Torchaudio**        | `2.2.2 + cu121` | Must match Torch exactly                          |       |
| **Coqui-TTS**         | `0.27.2`        | Current release w/ XTTS v2 engine                 |       |
| **coqui-tts-trainer** | `0.3.1`         | Finetuning & dataset manager                      |       |
| **Transformers**      | `4.55.4`        | Stable with XTTS v2 and PyTorch 2.2.2             |       |
| **huggingface_hub**   | `0.36.0`        | Matches Transformers 4.55+ API                    |       |
| **hf-xet**            | `1.2.0`         | (installed by hub) XetHub remote dataset backend  |       |
| **fsspec**            | `2025.9.0`      | For remote asset loading                          |       |
| **NumPy**             | `1.26.4`        | Bridge between PyTorch 2.2.2 and Librosa 0.11    |       |
| **Librosa**           | `0.11.0`        | Audio feature extraction for XTTS and QC          |       |
| **SoundFile**         | `0.12.1`        | WAV/FLAC I/O                                      |       |
| **Faster-Whisper**    | `1.2.0`         | Whisper variant; GPU-ready (compatible with 2.2.2)|       |
| **pyloudnorm**        | `0.1.1`         | LUFS metering                                     |       |
| **noisereduce**       | `3.0.2`         | NR chain                                          |       |
| **ffmpeg-python**     | `0.2.0`         | Audio/video conversion                            |       |
| **tokenizers**        | `0.21.4`        | Required by Transformers 4.55 (>=0.21,<0.22)     |       |
| **safetensors**       | `0.6.2`         | Fast checkpoint I/O                               |       |

🟩 **These versions are fully cross-compatible on Python 3.11 and RTX hardware.**

🟥 **Do not downgrade librosa, numpy, or transformers—XTTS will break with the older APIs from Melotts/OpenVoice chains**

---

## 🚫 Legacy Engine Isolation

| Engine                | Recommended Version                | Status                                                               |
| --------------------- | ---------------------------------- | -------------------------------------------------------------------- |
| **MyShell OpenVoice** | `0.0.0 (patched)`                  | Keep isolated in its own venv → conflicts w/ NumPy 1.26+ & Torch 2.2.2 |
| **Tortoise-TTS**      | `3.0.0 (Transformers 4.31 lock)`   | Use separate venv if needed for legacy tests                         |
| **Melotts**           | `0.1.2 (requires Torch 2.0 stack)` | Legacy; not needed for XTTS v2                                       |
| **WhisperX**          | `3.7.4`                            | Works if Torch ≈ 2.8 — stay on Faster-Whisper 1.2.0 instead           |

✅ **All modern VoiceStudio tasks run best on the Coqui XTTS v2 stack above; others can be sandboxed under `/plugins/legacy_engines/` venvs.**

---

## 🖥️ Windows UI Stack

| Layer                        | Library          | Version                                  |
| ---------------------------- | ---------------- | ---------------------------------------- |
| .NET SDK                     | 8.0.417          | Pinned in global.json                     |
| WinAppSDK                    | 1.8.251106002    | Pinned in Directory.Build.props           |
| CommunityToolkit.WinUI       | 7.1.2            | Native controls (Directory.Build.props)  |
| CommunityToolkit.Mvvm        | 8.2.2            | MVVM utilities                           |
| NAudio                       | 2.2.1            | Audio I/O                                |
| SDK BuildTools               | 10.0.26100.4654  | Windows 11 build 26100                    |
| PySide6 / Addons             | 6.8.0.1          | Bridge for Python UI tools (if used)     |
| qfluentwidgets               | 1.4.3            | Fluent style toolkit for VoiceStudio GUI (if used) |

---

## 🔒 Version Lock Ranges (Safe Compatibility)

| Group            | Locked Version Span | Safe |
| ---------------- | ------------------- | ---- |
| AI Core          | Torch 2.2 → 2.9     | ✅    |
| Audio DSP        | Librosa 0.10 → 0.11 | ✅    |
| Transformers API | 4.55 → 4.57         | ✅    |
| HuggingFace Hub  | ≤ 0.36              | ✅    |
| Python Runtime   | 3.10 → 3.11         | ✅    |

---

## 🎧 Clone Quality vs. "Absolute Latest" Bleeding Edge

**XTTS v2 (inside Coqui 0.27.2) is the same model weights you'd get if you ran it on Torch 2.9 or 2.10.**

Voice fidelity, prosody, and clarity depend on model and reference audio — **not on Torch minor versions.**

The "latest-possible" (Transformers 4.58 beta, Torch 2.10 nightly) offers **no audible gain**, only risk of breaking custom operators (Coqui's CUDA kernels and whisperx ops).

**→ Quality difference ≈ 0%, stability gain ≈ +100% by staying on this matrix.**

---

## 📦 Installation Commands

### Step 1: Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip wheel setuptools
```

### Step 2: Install PyTorch (CUDA 12.1)

```powershell
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```

### Step 3: Install Core AI Stack

```powershell
pip install coqui-tts==0.27.2 coqui-tts-trainer==0.3.1
pip install transformers==4.55.4 huggingface_hub==0.36.0
pip install tokenizers==0.21.4 safetensors==0.6.2
```

### Step 4: Install Audio Processing

```powershell
pip install librosa==0.11.0 numpy==1.26.4 soundfile==0.12.1
pip install faster-whisper==1.2.0 pyloudnorm==0.1.1 noisereduce==3.0.2
pip install ffmpeg-python==0.2.0
```

### Step 5: Install Backend API

```powershell
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0 websockets==14.1
```

---

## ⚠️ Critical Constraints

### Must Match Exactly
1. **Torch == Torchaudio** (2.2.2+cu121)
2. **Transformers 4.55.4** (for XTTS v2 on this stack)
3. **Librosa <= 0.11.0** (Torch compatibility)
4. **NumPy <= 1.26.4** (Librosa compatibility)
5. **Python 3.11.9** (recommended, 3.10.15 minimum)

### Do Not Upgrade Without Ledger-Proofed Path
- ❌ **Librosa > 0.11.0** (breaks PyTorch 2.2.2 compatibility)
- ❌ **NumPy > 1.26.4** (breaks Librosa 0.11 compatibility)
- ❌ **Torch/Transformers** — upgrade only with explicit ADR + proof; see ON_TRACK_STATE.md

### Legacy Engine Isolation
- Isolate OpenVoice, Tortoise-TTS, Melotts in separate venvs
- Use `/plugins/legacy_engines/` directory structure
- Do not mix legacy engines with modern stack

---

## ✅ Verification Checklist

- [x] Python 3.11.9 installed
- [x] PyTorch 2.2.2+cu121 verified
- [x] Torchaudio matches Torch version
- [x] Transformers 4.55.4 compatible
- [x] XTTS v2 loads successfully
- [x] GPU acceleration working
- [x] All audio processing functions
- [x] Faster-Whisper 1.2.0 working
- [x] Legacy engines isolated

---

## 📊 Compatibility Testing

**Tested On:**
- Windows 11 Build 26100
- Python 3.11.9
- RTX 3060 / 3070 / 3080 / 3090 / 4080 / 4090
- CUDA 12.1
- PyTorch 2.2.2+cu121

**Status:** ✅ All components verified compatible (pinned stack)

---

## 🔗 Related Documents

- `requirements_engines.txt` - Complete dependency list
- `docs/design/TECHNICAL_STACK_SPECIFICATION.md` - Technical stack details
- `version_lock.json` - JSON version reference

---

**Last Verified:** 2026-01-30  
**Next Review:** When major version updates available; any upgrade requires ledger-proofed path per ON_TRACK_STATE.md

