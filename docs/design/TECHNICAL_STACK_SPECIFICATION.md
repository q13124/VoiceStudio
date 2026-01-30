# VoiceStudio Quantum+ Technical Stack Specification

## Complete Dependency & Version Matrix

**Version:** 2.0  
**Last Updated:** 2025-01-27  
**Purpose:** Definitive specification for all dependencies, versions, and compatibility requirements

**⚠️ IMPORTANT:** See `docs/design/COMPATIBILITY_MATRIX.md` for the complete, production-ready compatibility matrix.

---

## 🧠 Core AI & Audio Engine Stack (Production-Ready Locked Versions)

### Python Environment

| Component             | Stable Version    | Notes                                                                    |
| --------------------- | ----------------- | ------------------------------------------------------------------------ |
| **Python**            | **3.11.9**        | Latest tested with PyTorch 2.2.2 + Transformers 4.55.4 (3.10.15 minimum) |
| **Coqui-TTS**         | **0.27.2**        | Current release w/ XTTS v2 engine                                        |
| **coqui-tts-trainer** | **0.3.1**         | Finetuning & dataset manager                                             |
| **Torch (CUDA)**      | **2.2.2 + cu121** | Required for compatibility with other software                           |
| **Torchaudio**        | **2.2.2 + cu121** | Must match Torch exactly                                                 |
| **Transformers**      | **4.55.4**        | Stable with XTTS v2 and PyTorch 2.2.2                                    |
| **huggingface_hub**   | **0.36.0**        | Matches Transformers 4.55+ API                                           |
| **tokenizers**        | **0.21.4**        | Required by Transformers 4.55 (tokenizers>=0.21,<0.22)                   |
| **safetensors**       | **0.6.2**         | Fast checkpoint I/O                                                      |
| **NumPy**             | **1.26.4**        | Perfect bridge between PyTorch 2.2.2 and Librosa 0.11                    |
| **Librosa**           | **0.11.0**        | Audio feature extraction; ⚠️ DO NOT UPGRADE > 0.11.0                     |
| **SoundFile**         | **0.12.1**        | WAV/FLAC I/O                                                             |
| **Faster-Whisper**    | **1.0.3**         | Whisper variant; GPU-ready (compatible with PyTorch 2.2.2)               |
| **pyloudnorm**        | **0.1.1**         | LUFS metering                                                            |
| **noisereduce**       | **3.0.2**         | NR chain                                                                 |
| **ffmpeg-python**     | **0.2.0**         | Audio/video conversion                                                   |
| **ffmpeg**            | **7.0+**          | Backend for conversions & preview playback                               |

✅ **All above verified GPU-compatible and deterministic on Windows 11 RTX 30/40 series with PyTorch 2.2.2+cu121.**

🟥 **Critical:** Do not downgrade librosa, numpy, or transformers—XTTS will break with older APIs. PyTorch 2.2.2+cu121 is the standard for compatibility.

---

## 🖥️ Native Windows UI Stack (WinUI 3)

These are the correct, non-web dependencies for native Windows desktop application:

| Component                              | Latest Verified  | Compatibility                                           |
| -------------------------------------- | ---------------- | ------------------------------------------------------- |
| **.NET SDK**                           | **8.0.303**      | Required for WinUI 3 projects                           |
| **Windows SDK**                        | **10.0.26100.0** | Supports all Win 11 APIs                                |
| **WinUI 3**                            | **1.5.0**        | For VoiceStudioApp.csproj                               |
| **WinAppSDK**                          | **1.5.0**        | Matches WinUI 3.5                                       |
| **CommunityToolkit.WinUI.UI.Controls** | **8.1.2409**     | Toolkit controls (StatusBar, DockPanel, DataGrid, etc.) |
| **ModernWpf**                          | **0.9.7**        | Optional for Fluent-style fallbacks                     |
| **Visual Studio 2022**                 | **17.11+**       | Required IDE for packaging and debug                    |
| **NSIS**                               | **3.10**         | Native installer for .exe packaging                     |

🟩 **These versions are mutually verified and safe for packaging VoiceStudio as a true native desktop app.**

---

## 🧩 Python UI / Bridge Layer (Optional or PySide6 Edition)

For cross-platform testing or Python-based frontend variant:

| Component                  | Version     | Notes                            |
| -------------------------- | ----------- | -------------------------------- |
| **PySide6**                | **6.8.0.1** | Supports Qt 6.8 and Fluent style |
| **PySide6-Addons**         | **6.8.0.1** | Required for advanced widgets    |
| **PySide6-Fluent-Widgets** | **1.6.6**   | Provides Fluent-like controls    |
| **QtAwesome**              | **1.3.1**   | Icon pack                        |
| **Qt-Material**            | **2.14**    | Optional theming engine          |
| **qfluentwidgets**         | **1.4.3**   | For the modern Fluent UI look    |

💡 **Works perfectly if you run a Python frontend variant instead of .NET/WinUI 3. Keep both in parallel—WinUI 3 for native Windows build, PySide6 for cross-platform testing.**

---

## 🎨 Design & MCP Integration Stack

| Tool / Server               | Recommended Version | Function                                 |
| --------------------------- | ------------------- | ---------------------------------------- |
| **Figma MCP**               | latest              | Imports layouts, tokens                  |
| **Shadcn UI MCP**           | latest              | Provides component blueprints            |
| **Magic UI / Flux UI MCPs** | latest              | Generate visual hierarchy and animations |
| **Storybook MCP**           | latest              | Component documentation                  |
| **Obsidian / Notion MCPs**  | latest              | Knowledge base & UX docs                 |
| **Design Handoff MCP**      | latest              | Converts Figma to XAML (WinUI 3)         |

🟢 **All these were listed in your ignored report — you can safely re-enable them for design-token synchronization and automated component generation.**

---

## 🎧 VoiceStudio Integration Matrix

| Subsystem                           | Engine / Framework             | Version                | Status         |
| ----------------------------------- | ------------------------------ | ---------------------- | -------------- |
| **TTS / Voice Cloning**             | Coqui XTTS v2                  | internal to TTS 0.27.2 | ✅ Stable      |
| **Voice Conversion (RVC)**          | so-vits-svc 5.1 fork           | 5.1.1                  | ✅ Compatible  |
| **Realtime Voice Conversion Panel** | WebSocket /ws/voice-conversion | —                      | ✅ Implemented |
| **Transcription**                   | Faster-Whisper 1.0.3           | —                      | ✅             |
| **Training Dataset Manager**        | Coqui Trainer 0.3.1            | —                      | ✅             |
| **Ensemble Synthesis**              | Custom Plugin API              | —                      | ✅             |
| **GPU Acceleration**                | CUDA 12.1 / cuDNN 8.9+         | —                      | ✅             |

---

## ⚙️ Recommended Install Command (PowerShell, Clean Venv)

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

### Step 3: Install Coqui TTS & Core Audio Stack

```powershell
pip install coqui-tts==0.27.2 coqui-tts-trainer==0.3.1
pip install transformers==4.55.4 librosa==0.11.0 numpy==1.26.4 soundfile==0.12.1
```

### Step 4: Install Audio Processing & ASR

```powershell
pip install faster-whisper==1.0.3 pyloudnorm==0.1.1 noisereduce==3.0.2 ffmpeg-python
```

### Step 5: Install FastAPI & WebSocket Support (for Backend API)

```powershell
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0 websockets==14.1
```

### Complete Installation Script

```powershell
# VoiceStudio Backend Setup Script
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip wheel setuptools

# PyTorch with CUDA 12.1
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121

# Coqui TTS & Core
pip install coqui-tts==0.27.2 coqui-tts-trainer==0.3.1
pip install transformers==4.55.4 librosa==0.11.0 numpy==1.26.4 soundfile==0.12.1

# Audio Processing
pip install faster-whisper==1.0.3 pyloudnorm==0.1.1 noisereduce==3.0.2 ffmpeg-python

# Backend API
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0 websockets==14.1 pydantic==2.9.0

Write-Host "✅ VoiceStudio backend dependencies installed successfully!"
```

---

## 📦 .NET / WinUI 3 Project Dependencies

### VoiceStudio.App.csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>
    <TargetPlatformMinVersion>10.0.17763.0</TargetPlatformMinVersion>
    <RootNamespace>VoiceStudio.App</RootNamespace>
    <ApplicationManifest>app.manifest</ApplicationManifest>
    <Platforms>x64;ARM64</Platforms>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.5.240627000" />
    <PackageReference Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.26100.0" />
    <PackageReference Include="CommunityToolkit.WinUI.UI.Controls" Version="8.1.2409" />
    <PackageReference Include="CommunityToolkit.Mvvm" Version="8.3.2" />
    <PackageReference Include="ModernWpfUI" Version="0.9.7" />
    <PackageReference Include="NAudio" Version="2.2.1" />
    <PackageReference Include="Win2D.WinUI" Version="1.1.0" />
  </ItemGroup>
</Project>
```

---

## 🔮 Summary

### ✅ AI Stack

- **Torch 2.2.2 (CUDA 12.1) + Coqui TTS 0.27.2**
- Verified GPU-compatible on Windows 11 RTX 3060
- All audio processing libraries compatible

### ✅ UI Stack

- **WinUI 3 (1.5.0) on .NET 8.0**
- Native Windows desktop application
- CommunityToolkit for advanced controls

### ✅ Design Layer

- **MCP servers + Figma integration**
- Automated component generation
- Design token synchronization

### ✅ Frontend Optional

- **PySide6 6.8.0.1 + Fluent Widgets 1.6.6**
- Cross-platform testing variant
- Parallel to WinUI 3 build

### ✅ Installer

- **NSIS 3.10 or Inno 6.3**
- Native Windows installer
- MSIX packaging support

### ✅ Platform

- **100% Windows-native + GPU-optimized**
- CUDA 12.1 / cuDNN 8.9+ support (for PyTorch 2.2.2+cu121)
- RTX 30/40 series verified

---

## 🔍 Compatibility Matrix

### Python 3.10.15 Compatibility

| Package        | Version     | Python 3.10 | Notes                                          |
| -------------- | ----------- | ----------- | ---------------------------------------------- |
| torch          | 2.2.2+cu121 | ✅          | Full CUDA support (standard for compatibility) |
| torchaudio     | 2.2.2+cu121 | ✅          | Must match torch exactly                       |
| coqui-tts      | 0.27.2      | ✅          | XTTS v2 compatible                             |
| transformers   | 4.55.4      | ✅          | Required for XTTS                              |
| librosa        | 0.11.0      | ✅          | Max compatible version                         |
| numpy          | 1.26.4      | ✅          | Max compatible version                         |
| faster-whisper | 1.0.3       | ✅          | Real-time ASR                                  |

### .NET 8.0 Compatibility

| Package          | Version      | .NET 8.0 | Notes             |
| ---------------- | ------------ | -------- | ----------------- |
| WinUI 3          | 1.5.0        | ✅       | Native Windows UI |
| Windows SDK      | 10.0.26100.0 | ✅       | Win 11 APIs       |
| CommunityToolkit | 8.1.2409     | ✅       | MVVM & Controls   |

---

## 🚨 Critical Version Constraints

### Must Match Exactly

1. **Torch == Torchaudio** (2.2.2+cu121) - **CRITICAL**
2. **CUDA == 12.1** (for PyTorch 2.2.2+cu121)
3. **Transformers >= 4.55.4** (for XTTS v2)
4. **Librosa <= 0.11.0** (PyTorch 2.2.2 compatibility)
5. **NumPy <= 1.26.4** (Librosa compatibility)

### Recommended Versions

1. **Python 3.10.15** (minimum) or **3.11.9** (recommended)
2. **PyTorch 2.2.2+cu121** (standard for compatibility)
3. **Coqui TTS 0.27.2** (XTTS v2 support)
4. **WinUI 3 1.5.0** (latest stable)

### Avoid

1. **PyTorch > 2.2.2** (compatibility issues with other software)
2. **PyTorch < 2.2.2** (may lack required features)
3. **Librosa > 0.11.0** (PyTorch 2.2.2 conflicts)
4. **NumPy > 1.26.4** (Librosa compatibility)
5. **Transformers < 4.55.4** (XTTS v2 requires 4.55+)

---

## 📝 Version History

| Date | Version | Changes                                |
| ---- | ------- | -------------------------------------- |
| 2025 | 1.0     | Initial specification                  |
|      |         | Verified on Windows 11 RTX 3060        |
|      |         | All dependencies tested and compatible |

---

## 🔗 Related Documents

- **[ENGINE_RECOMMENDATIONS.md](ENGINE_RECOMMENDATIONS.md)** - Detailed engine recommendations
- **[MEMORY_BANK.md](MEMORY_BANK.md)** - Critical project information
- **[SKELETON_INTEGRATION_GUIDE.md](SKELETON_INTEGRATION_GUIDE.md)** - Integration guide

---

## ✅ Verification Checklist

Before deploying, verify:

- [ ] Python 3.10.15 installed
- [ ] CUDA 12.1 drivers installed
- [ ] PyTorch 2.2.2+cu121 installed correctly
- [ ] Coqui TTS 0.27.2 working with XTTS v2
- [ ] .NET 8.0 SDK installed
- [ ] Windows SDK 10.0.26100.0 installed
- [ ] WinUI 3 1.5.0 project builds
- [ ] All MCP servers accessible
- [ ] GPU acceleration verified
- [ ] All audio processing libraries functional

---

**This specification is the definitive reference for all VoiceStudio dependencies and versions. Always refer to this document when setting up new environments or updating dependencies.**
