# VoiceStudio Quantum+ Development Setup Guide

Complete guide to setting up a development environment for VoiceStudio Quantum+.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Building from Source](#building-from-source)
4. [Running the Application](#running-the-application)
5. [Running Tests](#running-tests)
6. [Debugging](#debugging)
7. [Common Development Issues](#common-development-issues)

---

## Prerequisites

### Required Software

**Windows:**
- Windows 10 (version 1903 or later) or Windows 11
- Visual Studio 2022 (Community or higher)
- .NET 8 SDK
- Python 3.10 or later
- Git

**Optional but Recommended:**
- NVIDIA GPU with CUDA support (for GPU acceleration)
- Visual Studio Code (for Python development)
- Python virtual environment manager (venv, conda, etc.)

### System Requirements

- **RAM:** 16 GB minimum (32 GB recommended)
- **Storage:** 20+ GB free space
- **GPU:** NVIDIA GPU with 4+ GB VRAM (recommended for engines)

---

## Environment Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/your-repo/voicestudio.git
cd voicestudio
```

### Step 2: Install .NET 8 SDK

1. Download .NET 8 SDK from [Microsoft](https://dotnet.microsoft.com/download/dotnet/8.0)
2. Run installer
3. Verify installation:
   ```bash
   dotnet --version
   # Should show: 8.0.x
   ```

### Step 3: Install Python 3.10+

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run installer
   - **Important:** Check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   # Should show: Python 3.10.x or higher
   ```

### Step 4: Install Python Dependencies

**Option A: Using venv (Recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# Install dependencies
pip install -r backend/requirements.txt

# Install engine dependencies
# - XTTS CPU profile:
powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'
# - XTTS GPU profile (sm_120):
# powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-gpu-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts -Gpu 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'
# - Full engine stack (all engines; longer install):
# powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-full-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile full 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'
```

**Option B: Using conda**

```bash
# Create conda environment
conda create -n voicestudio python=3.10
conda activate voicestudio

# Install dependencies
pip install -r backend/requirements.txt

# Install engine dependencies (XTTS + full engine stack)
pip uninstall -y torch torchaudio torchvision
pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
pip install --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cu121 -r requirements_engines.txt
```

### Step 5: Install Frontend Dependencies

**Using Visual Studio:**
1. Open `src/VoiceStudio.App/VoiceStudio.App.csproj` in Visual Studio
2. Visual Studio will restore NuGet packages automatically

**Using Command Line:**
```bash
cd src/VoiceStudio.App
dotnet restore
```

### Step 6: Verify Setup

**Check Python:**
```bash
python -c "import fastapi; print('FastAPI installed')"
python -c "import torch; print('PyTorch installed')"
python -c "from TTS.api import TTS; print('Coqui TTS installed')"
```

**Check .NET:**
```bash
dotnet build src/VoiceStudio.App/VoiceStudio.App.csproj
```

---

## Building from Source

### Frontend (WinUI 3)

**Using Visual Studio:**
1. Open `src/VoiceStudio.App/VoiceStudio.App.csproj`
2. Select build configuration (Debug/Release)
3. Build → Build Solution (Ctrl+Shift+B)

**Using Command Line:**
```bash
cd src/VoiceStudio.App
dotnet build
```

**Output:**
- Debug: `src/VoiceStudio.App/bin/Debug/net8.0-windows10.0.19041.0/`
- Release: `src/VoiceStudio.App/bin/Release/net8.0-windows10.0.19041.0/`

### Backend (Python)

**No build step required** - Python is interpreted. Just ensure dependencies are installed.

**Verify Backend:**
```bash
cd backend
python -m uvicorn api.main:app --reload
```

Backend should start on `http://localhost:8000`

---

## Running the Application

### Option 1: Run from Visual Studio

1. **Set Startup Project:**
   - Right-click `VoiceStudio.App` project
   - Select "Set as Startup Project"

2. **Start Backend:**
   - Open terminal in `backend/` directory
   - Run: `python -m uvicorn api.main:app --reload`

3. **Start Frontend:**
   - Press F5 or click "Start" in Visual Studio
   - Application launches

### Option 2: Run from Command Line

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd src/VoiceStudio.App
dotnet run
```

### Option 3: Run Both with Script

Create `run-dev.ps1`:
```powershell
# Start backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn api.main:app --reload"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
cd src/VoiceStudio.App
dotnet run
```

Run: `.\run-dev.ps1`

---

## Running Tests

### Frontend Tests

**Using Visual Studio:**
1. Open Test Explorer (Test → Test Explorer)
2. Run All Tests

**Using Command Line:**
```bash
dotnet test
```

**Run Specific Test:**
```bash
dotnet test --filter "FullyQualifiedName~TestClassName"
```

### Backend Tests

**Using pytest:**
```bash
cd backend
pytest
```

**Run Specific Test:**
```bash
pytest tests/test_profiles.py
pytest tests/test_profiles.py::test_create_profile
```

**With Coverage:**
```bash
pytest --cov=api --cov-report=html
```

### Integration Tests

**End-to-End Test:**
```bash
# Start backend
python -m uvicorn api.main:app

# In another terminal, run integration tests
pytest tests/integration/
```

---

## Debugging

### Frontend Debugging (Visual Studio)

1. **Set Breakpoints:**
   - Click in left margin to set breakpoint
   - Or press F9 on line

2. **Start Debugging:**
   - Press F5 to start with debugger
   - Application pauses at breakpoints

3. **Debug Tools:**
   - **Watch Window:** Monitor variable values
   - **Call Stack:** See execution path
   - **Immediate Window:** Evaluate expressions
   - **Output Window:** View debug output

4. **Debug Configuration:**
   - Project Properties → Debug
   - Configure launch settings
   - Set environment variables if needed

### Backend Debugging (VS Code)

1. **Install Python Extension:**
   - Install "Python" extension in VS Code

2. **Create Launch Configuration:**
   Create `.vscode/launch.json`:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "module": "uvicorn",
         "args": [
           "api.main:app",
           "--reload",
           "--host",
           "127.0.0.1",
           "--port",
           "8000"
         ],
         "jinja": true,
         "justMyCode": false
       }
     ]
   }
   ```

3. **Set Breakpoints:**
   - Click in left margin
   - Red dot appears

4. **Start Debugging:**
   - Press F5
   - Backend starts with debugger
   - Pauses at breakpoints

### Backend Debugging (PyCharm)

1. **Create Run Configuration:**
   - Run → Edit Configurations
   - Add Python configuration
   - Script: `-m uvicorn`
   - Parameters: `api.main:app --reload`

2. **Set Breakpoints:**
   - Click in left margin

3. **Debug:**
   - Click Debug button
   - Or press Shift+F9

### Logging

**Frontend Logging:**
```csharp
using System.Diagnostics;

Debug.WriteLine("Debug message");
_logger.LogInformation("Info message");
_logger.LogError("Error message");
```

**Backend Logging:**
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", exc_info=True)
```

**View Logs:**
- Frontend: Output window in Visual Studio
- Backend: Console output or log files

---

## Common Development Issues

### Issue: Backend Won't Start

**Symptoms:**
- `ModuleNotFoundError` or import errors
- Port already in use

**Solutions:**

1. **Check Python Environment:**
   ```bash
   python --version
   which python  # Verify using correct Python
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Check Port:**
   ```bash
   # Windows: Check if port 8000 is in use
   netstat -ano | findstr :8000
   # Kill process if needed
   taskkill /PID <pid> /F
   ```

4. **Check Virtual Environment:**
   ```bash
   # Verify virtual environment is activated
   which python  # Should point to venv
   ```

### Issue: Frontend Won't Build

**Symptoms:**
- Build errors
- Missing NuGet packages

**Solutions:**

1. **Restore Packages:**
   ```bash
   dotnet restore
   ```

2. **Clean and Rebuild:**
   ```bash
   dotnet clean
   dotnet build
   ```

3. **Check .NET Version:**
   ```bash
   dotnet --version  # Should be 8.0.x
   ```

4. **Check Project File:**
   - Verify `TargetFramework` is `net8.0-windows10.0.19041.0`
   - Verify Windows App SDK version

### Issue: Engines Not Loading

**Symptoms:**
- No engines available
- Engine import errors

**Solutions:**

1. **Check Engine Manifests:**
   ```bash
   # Verify manifests exist
   ls engines/audio/*/engine.manifest.json
   ```

2. **Check Engine Dependencies:**
   ```bash
   # Install the pinned engine dependency set (includes XTTS)
   powershell -ExecutionPolicy Bypass -File .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts
   ```

3. **Check Engine Entry Points:**
   - Verify entry_point in manifest is correct
   - Verify engine class exists and is importable

4. **Check Logs:**
   - Review backend logs for import errors
   - Check for missing dependencies

### Issue: Backend Connection Failed

**Symptoms:**
- Frontend can't connect to backend
- Connection refused errors

**Solutions:**

1. **Verify Backend Running:**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   ```

2. **Check Backend URL:**
   - Verify `BackendClientConfig.BaseUrl` is correct
   - Default: `http://localhost:8000`

3. **Check Firewall:**
   - Windows Firewall may block connections
   - Add exception if needed

4. **Check CORS:**
   - Backend should allow CORS from frontend
   - Check `main.py` CORS configuration

### Issue: GPU Not Available

**Symptoms:**
- Engines fall back to CPU
- Slow performance

**Solutions:**

1. **Check CUDA Installation:**
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Install CUDA Toolkit:**
   - Download from NVIDIA
   - Install CUDA 11.8 or 12.1

3. **Install PyTorch with CUDA:**
   ```bash
   pip install torch==2.2.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Verify GPU:**
   ```python
   import torch
   print(torch.cuda.is_available())
   print(torch.cuda.get_device_name(0))
   ```

### Issue: Import Errors

**Symptoms:**
- `ModuleNotFoundError`
- Import errors in Python

**Solutions:**

1. **Check Python Path:**
   ```python
   import sys
   print(sys.path)
   ```

2. **Install Missing Packages:**
   ```bash
   pip install <package-name>
   ```

3. **Check Virtual Environment:**
   - Ensure virtual environment is activated
   - Verify packages installed in correct environment

4. **Relative Imports:**
   - Use absolute imports when possible
   - Check import paths

---

## Development Workflow

### Typical Development Session

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload
   ```

2. **Start Frontend:**
   - Open in Visual Studio
   - Press F5 to debug

3. **Make Changes:**
   - Edit code
   - Backend auto-reloads (with --reload flag)
   - Frontend requires rebuild (or auto-rebuild if enabled)

4. **Test Changes:**
   - Test in application
   - Run unit tests
   - Check logs for errors

5. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

### Hot Reload

**Backend:**
- Use `--reload` flag for auto-reload on file changes
- Changes to Python files trigger automatic restart

**Frontend:**
- Visual Studio supports hot reload for XAML
- C# changes require rebuild
- Enable "Hot Reload" in Visual Studio settings

---

## IDE Configuration

### Visual Studio

**Recommended Extensions:**
- XAML Styler (format XAML)
- CodeMaid (code cleanup)
- ReSharper (optional, code analysis)

**Settings:**
- Enable "Hot Reload"
- Enable "IntelliSense"
- Set tab size to 4 spaces

### VS Code (for Python)

**Recommended Extensions:**
- Python
- Pylance
- Python Test Explorer
- FastAPI Snippets

**Settings:**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

---

## Environment Variables

### Backend Environment Variables

Create `.env` file in `backend/` directory:

```env
# Backend Configuration
VOICESTUDIO_BACKEND_URL=http://localhost:8000
VOICESTUDIO_LOG_LEVEL=DEBUG

# Engine Configuration
VOICESTUDIO_ENGINES_PATH=engines
VOICESTUDIO_MODELS_PATH=E:\VoiceStudio\models

# Force all Hugging Face / Transformers / Coqui caches onto E:\ (avoid C:\ user cache spill)
HF_HOME=E:\VoiceStudio\models\hf_cache
HUGGINGFACE_HUB_CACHE=E:\VoiceStudio\models\hf_cache\hub
TRANSFORMERS_CACHE=E:\VoiceStudio\models\hf_cache\transformers
HF_DATASETS_CACHE=E:\VoiceStudio\models\hf_cache\datasets
TTS_HOME=E:\VoiceStudio\models\xtts
TORCH_HOME=E:\VoiceStudio\models\torch

# Python Configuration
PYTHONPATH=.
```

### Frontend Environment Variables

Set in `launchSettings.json` or project properties:

```json
{
  "environmentVariables": {
    "VOICESTUDIO_BACKEND_URL": "http://localhost:8000"
  }
}
```

---

## Performance Optimization

### Backend Performance

**Enable GPU:**
- Install CUDA
- Install PyTorch with CUDA support
- Engines will use GPU automatically

**Optimize Python:**
```python
# Use async/await for I/O
async def process_request():
    result = await async_operation()
    return result
```

### Frontend Performance

**Enable Hot Reload:**
- Visual Studio → Tools → Options → Debugging → Hot Reload
- Enable "Hot Reload on File Save"

**Optimize Build:**
- Use Release configuration for performance testing
- Disable debug symbols in Release builds

---

## Next Steps

After setup is complete:

1. **[Architecture Documentation](ARCHITECTURE.md)** - Understand system architecture
2. **[Code Structure](CODE_STRUCTURE.md)** - Learn code organization
3. **[Contributing Guide](CONTRIBUTING.md)** - Read contribution guidelines
4. **[Engine Plugin System](ENGINE_PLUGIN_SYSTEM.md)** - Create custom engines

---

**Last Updated:** 2025-01-27  
**Version:** 1.0

