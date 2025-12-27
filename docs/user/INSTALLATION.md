# VoiceStudio Quantum+ Installation Guide

Complete installation instructions for VoiceStudio Quantum+.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [First-Time Setup](#first-time-setup)
4. [Engine Installation](#engine-installation)
5. [Configuration](#configuration)
6. [Uninstallation](#uninstallation)
7. [Troubleshooting Installation](#troubleshooting-installation)

---

## System Requirements

### Minimum Requirements

- **Operating System:**
  - Windows 10 (version 1903 or later, 64-bit)
  - Windows 11 (64-bit)

- **Processor:**
  - Intel Core i5 or AMD equivalent
  - 64-bit processor

- **Memory (RAM):**
  - 8 GB minimum
  - 16 GB recommended

- **Storage:**
  - 5 GB free space (minimum)
  - 20+ GB recommended (for models and projects)
  - SSD recommended for better performance

- **Graphics:**
  - DirectX 11 compatible GPU
  - NVIDIA GPU recommended for faster processing
  - 2 GB VRAM minimum (4+ GB recommended)
  - **VRAM Monitoring:** VoiceStudio monitors VRAM usage and displays warnings when usage exceeds 60% (warning) or 80% (critical). Close other GPU-intensive applications or reduce engine quality settings if VRAM warnings appear.

- **.NET Runtime:**
  - .NET 8 Runtime (included in installer)

- **Python:**
  - Python 3.10 or later (included in installer)

### Recommended Requirements

- **Operating System:** Windows 11 (latest version)
- **Processor:** Intel Core i7/i9 or AMD Ryzen 7/9 (6+ cores)
- **Memory:** 32 GB RAM
- **Storage:** 50+ GB SSD
- **Graphics:** NVIDIA GPU with 8+ GB VRAM (RTX series recommended)
- **Network:** Internet connection for engine downloads and updates

---

## Installation Steps

### Step 1: Download the Installer

1. Visit the VoiceStudio releases page (URL will be provided at release time)
2. Download the latest installer:
   - File name: `VoiceStudio-Setup-vX.X.X.exe`
   - File size: ~500 MB (includes Python runtime and dependencies)

### Step 2: Run the Installer

1. **Locate the downloaded file:**
   - Usually in your Downloads folder
   - File: `VoiceStudio-Setup-vX.X.X.exe`

2. **Run the installer:**
   - Double-click the installer file
   - If Windows SmartScreen appears:
     - Click **"More info"**
     - Click **"Run anyway"** (app is not yet code-signed)

3. **User Account Control (UAC):**
   - Click **"Yes"** when prompted
   - Administrator privileges required for installation

### Step 3: Installation Wizard

1. **Welcome Screen:**
   - Click **"Next"** to begin

2. **License Agreement:**
   - Read the license agreement
   - Check **"I accept the terms"**
   - Click **"Next"**

3. **Installation Location:**
   - Default: `C:\Program Files\VoiceStudio`
   - Click **"Browse"** to change location
   - Click **"Next"**

4. **Select Components:**
   - **VoiceStudio Application:** Required (checked)
   - **Python Runtime:** Required (checked)
   - **.NET 8 Runtime:** Required (checked)
   - **Example Projects:** Optional
   - **Documentation:** Recommended
   - Click **"Next"**

5. **Start Menu Folder:**
   - Default: `VoiceStudio`
   - Click **"Next"**

6. **Ready to Install:**
   - Review installation settings
   - Click **"Install"** to begin

7. **Installation Progress:**
   - Wait for installation (5-10 minutes)
   - Progress bar shows status
   - Do not close installer

8. **Installation Complete:**
   - Check **"Launch VoiceStudio"** to start immediately
   - Click **"Finish"**

### Step 4: Verify Installation

1. **Check Installation:**
   - Installation directory should contain:
     - `VoiceStudio.App.exe` (main application)
     - `backend/` (Python backend)
     - `engines/` (engine manifests)
     - `docs/` (documentation)

2. **Start Menu:**
   - VoiceStudio should appear in Start Menu
   - Shortcut created automatically

3. **File Associations:**
   - `.voiceproj` files associate with VoiceStudio
   - `.vprofile` files associate with VoiceStudio

---

## First-Time Setup

### Step 1: Launch VoiceStudio

1. **From Start Menu:**
   - Click Start Menu
   - Search "VoiceStudio"
   - Click VoiceStudio icon

2. **From Desktop:**
   - Double-click VoiceStudio shortcut (if created)

3. **From Installation Directory:**
   - Navigate to installation folder
   - Double-click `VoiceStudio.App.exe`

### Step 2: Welcome Dialog

1. **First Launch:**
   - Welcome dialog appears automatically
   - Review welcome information

2. **Welcome Options:**
   - **Show on startup:** Check/uncheck as desired
   - **Take tour:** Optional guided tour
   - **Skip:** Close dialog

### Step 3: Backend Initialization

1. **Backend Startup:**
   - Backend starts automatically
   - Check status in Diagnostics panel

2. **Verify Connection:**
   - Open Diagnostics panel (from navigation rail)
   - Check "Backend Status": Should show "Connected"
   - If not connected, see [Troubleshooting](#troubleshooting-installation)

### Step 4: Engine Discovery

1. **Engine Loading:**
   - Engines auto-discover from `engines/` directory
   - Check Diagnostics panel for available engines

2. **Expected Engines:**
   - XTTS v2 (Coqui TTS)
   - Chatterbox TTS (Resemble AI)
   - Tortoise TTS
   - Whisper (for transcription)

3. **If Engines Missing:**
   - See [Engine Installation](#engine-installation)

---

## Engine Installation

### Automatic Engine Installation

Engines are discovered automatically from `engines/` directory. Each engine has a manifest file (`engine.manifest.json`) that defines its configuration.

### Manual Engine Setup

If engines are not auto-discovered:

1. **Check Engine Directory:**
   - Location: `engines/audio/` (in installation directory)
   - Should contain engine folders:
     - `xtts_v2/`
     - `chatterbox/`
     - `tortoise/`
     - `whisper/`

2. **Verify Manifests:**
   - Each engine folder should have `engine.manifest.json`
   - Check manifest files exist

3. **Engine Dependencies:**
   - Engines may require additional Python packages
   - Backend installs dependencies automatically on first use
   - Check backend logs for dependency installation

### Installing Additional Engines

1. **Download Engine:**
   - Obtain engine files or model
   - Place in `engines/audio/[engine_name]/`

2. **Create Manifest:**
   - Create `engine.manifest.json`
   - Follow manifest schema (see developer docs)

3. **Restart Backend:**
   - Restart VoiceStudio
   - Engine auto-discovers on startup

---

## Configuration

### Application Settings

1. **Open Settings:**
   - **File > Settings** or **Ctrl+,**
   - Or Command Palette: **Ctrl+P**, type "settings"

2. **General Settings:**
   - Theme: Light/Dark/System
   - Language: Application language
   - Auto-save: Enable/disable, interval

3. **Engine Settings:**
   - Default engine selection
   - Quality mode defaults
   - Engine-specific settings

4. **Audio Settings:**
   - Output device selection
   - Input device selection
   - Sample rate (44.1 kHz, 48 kHz, etc.)
   - Buffer size

5. **Backend Settings:**
   - Backend URL (default: `http://localhost:8000`)
   - Timeout settings
   - Retry settings

### Environment Variables (Advanced)

For advanced configuration, set environment variables:

- `VOICESTUDIO_BACKEND_URL`: Backend API URL
- `VOICESTUDIO_ENGINES_PATH`: Custom engines directory
- `VOICESTUDIO_MODELS_PATH`: Custom models directory
- `VOICESTUDIO_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Configuration Files

Configuration stored in:
- **User Settings:** `%AppData%\VoiceStudio\settings.json`
- **Project Settings:** Per-project `.voiceproj` file
- **Engine Configs:** `engines/config.json`

---

## Uninstallation

### Standard Uninstallation

1. **Open Windows Settings:**
   - Press **Windows + I**
   - Go to **Apps > Apps & features**

2. **Find VoiceStudio:**
   - Search for "VoiceStudio"
   - Click on VoiceStudio entry

3. **Uninstall:**
   - Click **"Uninstall"**
   - Confirm uninstallation
   - Wait for removal

### Manual Uninstallation

If standard uninstallation fails:

1. **Stop VoiceStudio:**
   - Close all VoiceStudio windows
   - Check Task Manager for running processes
   - End any VoiceStudio processes

2. **Delete Installation Directory:**
   - Navigate to installation folder
   - Default: `C:\Program Files\VoiceStudio`
   - Delete entire folder

3. **Delete User Data (Optional):**
   - `%AppData%\VoiceStudio\` (settings, projects)
   - `%LocalAppData%\VoiceStudio\` (cache, logs)
   - **Warning:** This deletes all projects and settings

4. **Remove Start Menu Shortcut:**
   - Delete `%ProgramData%\Microsoft\Windows\Start Menu\Programs\VoiceStudio\`

5. **Remove File Associations:**
   - Open **Settings > Apps > Default apps**
   - Reset file associations for `.voiceproj` and `.vprofile`

### Clean Uninstallation

For complete removal:

1. Follow manual uninstallation steps
2. Remove registry entries (if any):
   - `HKEY_CURRENT_USER\Software\VoiceStudio`
   - `HKEY_LOCAL_MACHINE\Software\VoiceStudio`
3. Remove Python packages (if installed separately):
   - `pip uninstall voicestudio-backend`
4. Remove .NET components (if installed separately):
   - Usually not needed (system-wide)

---

## Troubleshooting Installation

### Installation Fails

**Problem:** Installer fails or errors occur

**Solutions:**
1. **Check System Requirements:**
   - Verify Windows version (10 1903+ or 11)
   - Check available disk space (5+ GB)
   - Verify administrator privileges

2. **Disable Antivirus:**
   - Temporarily disable antivirus
   - Some antivirus may block installation
   - Re-enable after installation

3. **Run as Administrator:**
   - Right-click installer
   - Select **"Run as administrator"**

4. **Check Logs:**
   - Installer creates log file
   - Location: `%Temp%\VoiceStudio-Install.log`
   - Review for error messages

5. **Clean Install:**
   - Uninstall previous version
   - Delete installation directory
   - Restart computer
   - Reinstall

### Backend Won't Start

**Problem:** Backend fails to start or connect

**Solutions:**
1. **Check Python Installation:**
   - Verify Python 3.10+ installed
   - Check Python in PATH
   - Reinstall Python if needed

2. **Check Port Availability:**
   - Default port: 8000
   - Ensure port not in use
   - Change port in settings if needed

3. **Check Dependencies:**
   - Backend installs dependencies automatically
   - Check backend logs for errors
   - Manually install: `pip install -r backend/requirements.txt`

4. **Check Firewall:**
   - Windows Firewall may block backend
   - Add exception for VoiceStudio
   - Or disable firewall temporarily

5. **Check Logs:**
   - Backend logs: `%LocalAppData%\VoiceStudio\logs\`
   - Review error messages
   - Check for Python errors

### Engines Not Loading

**Problem:** Engines not discovered or fail to load

**Solutions:**
1. **Check Engine Directory:**
   - Verify `engines/audio/` exists
   - Check for engine manifest files
   - Verify file permissions

2. **Check Engine Manifests:**
   - Validate JSON syntax
   - Check required fields
   - Compare with working engines

3. **Check Dependencies:**
   - Engines may need additional packages
   - Check backend logs for missing dependencies
   - Install manually if needed

4. **Restart Backend:**
   - Restart VoiceStudio
   - Engines reload on startup

### Performance Issues

**Problem:** Slow performance or high CPU/memory usage

**Solutions:**
1. **Check System Resources:**
   - Close other applications
   - Check available RAM
   - Monitor CPU usage

2. **GPU Acceleration:**
   - Enable GPU acceleration in settings
   - Requires compatible GPU
   - Significantly improves performance

3. **Reduce Quality Settings:**
   - Use "Fast" quality mode for previews
   - Use "High" only for final output
   - Disable quality enhancement if not needed

4. **Optimize Settings:**
   - Reduce buffer size (if causing issues)
   - Disable real-time effects
   - Use proxy files for large projects

### File Associations Not Working

**Problem:** `.voiceproj` or `.vprofile` files don't open with VoiceStudio

**Solutions:**
1. **Reinstall:**
   - Reinstall VoiceStudio
   - File associations set during installation

2. **Manual Association:**
   - Right-click `.voiceproj` file
   - Select **"Open with"**
   - Choose VoiceStudio
   - Check **"Always use this app"**

3. **Windows Settings:**
   - Open **Settings > Apps > Default apps**
   - Click **"Choose default apps by file type"**
   - Set `.voiceproj` to VoiceStudio
   - Set `.vprofile` to VoiceStudio

---

## Getting Help

If installation issues persist:

1. **Check Documentation:**
   - [Troubleshooting Guide](TROUBLESHOOTING.md)
   - [User Manual](USER_MANUAL.md)

2. **Check Logs:**
   - Application logs: `%LocalAppData%\VoiceStudio\logs\`
   - Backend logs: `backend/logs/` (if available)
   - Installer logs: `%Temp%\VoiceStudio-Install.log`

3. **Report Issues:**
   - GitHub Issues: Report bug on the project repository (URL will be provided at release time)
   - Include:
     - Windows version
     - Error messages
     - Log files
     - Steps to reproduce

---

## Next Steps

After successful installation:

1. **[Getting Started Guide](GETTING_STARTED.md)** - Learn the basics
2. **[User Manual](USER_MANUAL.md)** - Complete feature guide
3. **[Tutorials](TUTORIALS.md)** - Step-by-step workflows

**Welcome to VoiceStudio Quantum+!**

