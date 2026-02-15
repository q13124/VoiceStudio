VoiceStudio Quantum+ - Installation Guide
==========================================

QUICK START
-----------
1. Run VoiceStudio-Setup-v1.1.0.exe
2. Follow the installer wizard
3. Launch VoiceStudio from Start Menu or Desktop

PREREQUISITES (checked by installer)
-------------------------------------
- Windows 10 version 1903 or later (64-bit)
- .NET 8 Desktop Runtime (installer will prompt to download if missing)
- Windows App SDK Runtime (installer will prompt to download if missing)

WHAT'S INCLUDED
---------------
- VoiceStudio application (WinUI 3 native desktop app)
- Python backend with FastAPI (embedded Python runtime)
- FFmpeg for audio/video processing
- 68 engine manifests (TTS, STT, voice conversion, image/video generation)
- 100+ API endpoints for all voice and media workflows

OPTIONAL MODEL PACKS
--------------------
Copy model packs to your Models folder after installation:

  ModelPack-Starter.zip   (~200MB) - Piper TTS + Whisper STT (CPU only, works immediately)
  ModelPack-Full.zip      (~4GB)   - All engines including XTTS, Whisper large (GPU recommended)

Default models folder: C:\ProgramData\VoiceStudio\models

SYSTEM REQUIREMENTS
-------------------
Minimum:
- CPU: 4 cores, 2.5 GHz+
- RAM: 8 GB
- Disk: 2 GB (app) + model storage
- OS: Windows 10 1903+

Recommended (for GPU acceleration):
- GPU: NVIDIA with 4+ GB VRAM and CUDA support
- RAM: 16 GB+
- Disk: SSD with 20+ GB free (models + cache)

SUPPORT
-------
Documentation is installed with the app:
  Start Menu > VoiceStudio > User Manual
  Start Menu > VoiceStudio > Getting Started
