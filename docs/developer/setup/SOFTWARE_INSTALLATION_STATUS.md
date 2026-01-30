# VoiceStudio Software Installation Status

**Last Checked:** 2026-01-09  
**System:** Windows 10.0.26200

## ✅ INSTALLED & CORRECT

### Core Development Tools

- **✅ Python 3.11.9** (Required: 3.10.15+)

  - Location: `C:\Users\Tyler\AppData\Local\Programs\Python\Python311\`
  - Status: **MEETS REQUIREMENT**

- **✅ .NET SDK 8.0.416** (Required: 8.0.416 per `global.json`)

  - Location: `C:\Program Files\dotnet\sdk\8.0.416\`
  - Status: **EXACT MATCH**
  - Also installed: 9.0.307, 10.0.101 (not required but not harmful)

- **✅ MSBuild 17.11.48** (Comes with .NET SDK)
  - Status: **CORRECT VERSION**

### Python Core Packages (Installed)

- **✅ fastapi** 0.119.1 (Required: >=0.109.0)
- **✅ uvicorn** 0.38.0 (Required: >=0.27.0)
- **✅ numpy** 1.26.4 (Required: 1.26.4 - **LOCKED VERSION**)
- **✅ librosa** 0.11.0 (Required: 0.11.0 - **LOCKED VERSION**)
- **✅ coqui-tts** 0.27.2 (Required: 0.27.2 - **EXACT MATCH**)
- **✅ coqui-tts-trainer** 0.3.1

---

## ⚠️ INSTALLED BUT WRONG VERSION

### Critical Issue: PyTorch Version Mismatch

- **⚠️ PyTorch 2.8.0+cpu** (Required: **2.2.2+cu121**)
  - Current: `torch==2.8.0+cpu` (CPU-only build)
  - Required: `torch==2.2.2+cu121` (CUDA 12.1 build)
  - **Impact:**
    - ❌ No GPU acceleration (CPU-only)
    - ❌ Version mismatch may cause compatibility issues with locked dependencies
    - ❌ May conflict with `torchaudio==2.2.2+cu121` requirement
  - **Status:** **NEEDS FIX**
  - **Action Required:** Reinstall PyTorch with CUDA support:
    ```powershell
    pip uninstall torch torchaudio torchvision
    pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
    ```

---

## ❌ NOT INSTALLED

### Build Tools

- **❌ Visual Studio 2022** (Required: 17.11+)
  - Checked paths:
    - `C:\Program Files\Microsoft Visual Studio\2022\Community\` - **NOT FOUND**
    - `C:\Program Files\Microsoft Visual Studio\2022\Professional\` - **NOT FOUND**
  - **Impact:**
    - ⚠️ Can still build via `dotnet CLI` (command line)
    - ❌ No Visual Studio IDE for development
    - ❌ Missing Windows SDK tooling integration
    - ❌ Missing WinUI 3 design-time support
  - **Status:** **OPTIONAL** (if using command line builds) or **REQUIRED** (if using IDE)
  - **Download:** https://visualstudio.microsoft.com/downloads/
  - **Required Workloads:**
    - .NET desktop development
    - Windows App SDK (for WinUI 3)

### Audio Processing Tools

- **❌ FFmpeg** (Required: 7.0+)
  - Not found in PATH
  - **Impact:**
    - ❌ Audio format conversion will fail
    - ❌ Audio playback may be limited
    - ❌ Video processing unavailable
  - **Status:** **REQUIRED**
  - **Install Options:**
    1. **Chocolatey:** `choco install ffmpeg -y`
    2. **Manual:** Download from https://ffmpeg.org/download.html
    3. **Set Environment Variable:** `VOICESTUDIO_FFMPEG_PATH` (see VS-0022)

---

## 📋 MISSING PYTHON PACKAGES

Based on `requirements_engines.txt`, many packages may not be installed. Key missing ones (check with `pip list`):

### Critical Engine Dependencies

- **faster-whisper** 1.0.3 (STT engine)
- **torchaudio** 2.2.2+cu121 (must match torch exactly)
- **transformers** 4.55.4 (locked version)
- **huggingface_hub** 0.36.0
- **safetensors** 0.6.2

### Audio Processing (Locked Versions)

- **soundfile** 0.12.1
- **pyloudnorm** 0.1.1
- **noisereduce** 3.0.2
- **pydub** >=0.25.0

### Quality Metrics (Critical)

- **pesq** >=0.0.4
- **pystoi** >=0.3.3

### Voice Conversion

- **faiss-cpu** 1.7.4
- **pyworld** 0.3.2
- **praat-parselmouth** >=0.4.3

**Full List:** See `requirements_engines.txt` and `requirements.txt`

---

## 🔧 VERIFICATION COMMANDS

### Check Python Packages

```powershell
pip list | Select-String "torch|fastapi|numpy|librosa|coqui|whisper"
```

### Check .NET SDK

```powershell
dotnet --version        # Should show: 8.0.416
dotnet --list-sdks      # Lists all installed SDKs
```

### Check MSBuild

```powershell
dotnet msbuild -version  # Should show: 17.11.48
```

### Check FFmpeg

```powershell
where ffmpeg             # Should show path or nothing
ffmpeg -version          # Should show version info
```

### Check Visual Studio (if installed)

```powershell
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\*\Common7\IDE\devenv.exe"
```

---

## 🎯 PRIORITY ACTIONS

### 🔴 CRITICAL (Blocks Functionality)

1. **Reinstall PyTorch with CUDA** (currently CPU-only, wrong version)

   ```powershell
   pip uninstall torch torchaudio torchvision -y
   pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
   ```

2. **Install FFmpeg** (required for audio processing)
   ```powershell
   choco install ffmpeg -y
   # OR download from https://ffmpeg.org/download.html and add to PATH
   ```

### 🟡 HIGH PRIORITY (Required for Full Functionality)

3. **Install Missing Python Packages**

   ```powershell
   pip install -r requirements.txt
   pip install -r requirements_engines.txt
   ```

   ⚠️ **Note:** PyTorch must be installed FIRST (see step 1)

4. **Verify torchaudio matches torch version**
   ```powershell
   pip show torch torchaudio  # Versions must match exactly
   ```

### 🟢 OPTIONAL (Development Experience)

5. **Install Visual Studio 2022** (if using IDE)
   - Download: https://visualstudio.microsoft.com/downloads/
   - Install "Community" edition (free)
   - Select workloads: ".NET desktop development" and "Windows App SDK"

---

## 📊 COMPATIBILITY MATRIX

| Component     | Required Version | Installed Version | Status          |
| ------------- | ---------------- | ----------------- | --------------- |
| Python        | 3.10.15+         | 3.11.9            | ✅ OK           |
| .NET SDK      | 8.0.416          | 8.0.416           | ✅ OK           |
| MSBuild       | 17.11.x          | 17.11.48          | ✅ OK           |
| PyTorch       | 2.2.2+cu121      | 2.8.0+cpu         | ❌ **MISMATCH** |
| torchaudio    | 2.2.2+cu121      | 2.8.0+cpu         | ❌ **MISMATCH** |
| numpy         | 1.26.4           | 1.26.4            | ✅ OK           |
| librosa       | 0.11.0           | 0.11.0            | ✅ OK           |
| coqui-tts     | 0.27.2           | 0.27.2            | ✅ OK           |
| fastapi       | >=0.109.0        | 0.119.1           | ✅ OK           |
| uvicorn       | >=0.27.0         | 0.38.0            | ✅ OK           |
| FFmpeg        | 7.0+             | **NOT FOUND**     | ❌ **MISSING**  |
| Visual Studio | 17.11+           | **NOT FOUND**     | ⚠️ Optional     |

---

## 🔍 SYSTEM REQUIREMENTS CHECK

### Minimum Requirements (Per Documentation)

- **RAM:** 16 GB minimum ✅ (assuming adequate system RAM)
- **Storage:** 20+ GB free space ✅ (1TB M.2 SSD available per docs)
- **GPU:** NVIDIA GPU with 4+ GB VRAM (recommended) ⚠️ **UNKNOWN**
- **OS:** Windows 10 (1903+) or Windows 11 ✅ (Windows 10.0.26200)

### CUDA Support

- **Required:** CUDA 12.1 for PyTorch GPU support
- **Check:** `nvidia-smi` (if NVIDIA GPU present)
- **Status:** ⚠️ **UNKNOWN** - Check if NVIDIA GPU is available

---

## 📝 NOTES

1. **PyTorch Version Lock:** The project uses **locked versions** for compatibility (see `requirements_engines.txt`). PyTorch 2.8.0 is too new and may cause conflicts with locked dependencies like `numpy==1.26.4` and `librosa==0.11.0`.

2. **CUDA vs CPU:** If no NVIDIA GPU is available, CPU-only builds can work but will be significantly slower for ML inference. The CPU build (`torch==2.8.0+cpu`) should still be replaced with the locked version (`torch==2.2.2+cpu`) for compatibility.

3. **Visual Studio:** Not strictly required if building via `dotnet CLI`, but recommended for WinUI 3 development, debugging, and design-time support.

4. **FFmpeg:** Critical for audio/video processing. The project has fallback discovery (see VS-0022), but FFmpeg must be installed somewhere on the system.

5. **Missing Packages:** The `pip list` output only showed a subset of installed packages. Run `pip list` to see the full inventory, then compare against `requirements.txt` and `requirements_engines.txt`.

---

## ✅ NEXT STEPS

1. **Fix PyTorch:** Reinstall with correct version and CUDA support
2. **Install FFmpeg:** Add to PATH or set `VOICESTUDIO_FFMPEG_PATH`
3. **Install Missing Packages:** Run `pip install -r requirements_engines.txt` (after fixing PyTorch)
4. **Verify Installation:** Run build/test commands to confirm all dependencies work

---

**Last Updated:** 2026-01-09  
**Next Review:** After installing missing/corrected software
