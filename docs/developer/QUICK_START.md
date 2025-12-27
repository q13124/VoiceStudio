# VoiceStudio Quantum+ Developer Quick Start Guide

**Get up and running in 15 minutes!**

This guide provides a streamlined path to get VoiceStudio Quantum+ running on your development machine. For detailed setup, see [SETUP.md](SETUP.md). For comprehensive onboarding, see [ONBOARDING.md](ONBOARDING.md).

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Estimated Setup Time:** 15-30 minutes

---

## Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Quick Setup (5 Steps)](#quick-setup-5-steps)
3. [Verify Installation](#verify-installation)
4. [Run the Application](#run-the-application)
5. [Common Issues](#common-issues)
6. [Next Steps](#next-steps)

---

## Prerequisites Check

### Required Software

Before starting, ensure you have:

- ✅ **Windows 10 (1903+)** or **Windows 11**
- ✅ **Visual Studio 2022** (Community or higher) with:
  - .NET desktop development workload
  - Windows App SDK (1.4+)
- ✅ **.NET 8 SDK** ([Download](https://dotnet.microsoft.com/download/dotnet/8.0))
- ✅ **Python 3.10+** ([Download](https://www.python.org/downloads/))
- ✅ **Git** ([Download](https://git-scm.com/download/win))

### Quick Verification

Open PowerShell and run:

```powershell
# Check .NET
dotnet --version
# Should show: 8.0.x

# Check Python
python --version
# Should show: Python 3.10.x or higher

# Check Git
git --version
```

**If any check fails, install the missing software before proceeding.**

---

## Quick Setup (5 Steps)

### Step 1: Clone the Repository

```powershell
git clone https://github.com/your-repo/voicestudio.git
cd voicestudio
```

**Note:** Replace `your-repo` with the actual repository URL.

### Step 2: Set Up Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Python dependencies
pip install -r backend/requirements.txt
```

**Expected Time:** 5-10 minutes (depending on internet speed)

### Step 3: Restore .NET Dependencies

```powershell
# Restore NuGet packages
cd src/VoiceStudio.App
dotnet restore
cd ..\..
```

**Expected Time:** 1-2 minutes

### Step 4: Build the Frontend

```powershell
# Build the application
cd src/VoiceStudio.App
dotnet build
cd ..\..
```

**Expected Output:**
```
Build succeeded.
    0 Warning(s)
    0 Error(s)
```

### Step 5: Verify Backend Setup

```powershell
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Verify Python dependencies
python -c "import fastapi; print('FastAPI: OK')"
python -c "import torch; print('PyTorch: OK')"
```

**Expected Output:**
```
FastAPI: OK
PyTorch: OK
```

---

## Verify Installation

### Quick Health Check

Run this PowerShell script to verify everything is set up correctly:

```powershell
# Check .NET
Write-Host "Checking .NET..." -ForegroundColor Cyan
dotnet --version

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Cyan
python --version

# Check virtual environment
Write-Host "`nChecking virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found" -ForegroundColor Red
}

# Check Python packages
Write-Host "`nChecking Python packages..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1
python -c "import fastapi; print('✓ FastAPI installed')"
python -c "import torch; print('✓ PyTorch installed')"

# Check .NET build
Write-Host "`nChecking .NET build..." -ForegroundColor Cyan
cd src/VoiceStudio.App
if (Test-Path "bin\Debug\net8.0-windows10.0.19041.0\VoiceStudio.App.exe") {
    Write-Host "✓ Frontend built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend not built. Run: dotnet build" -ForegroundColor Yellow
}
cd ..\..
```

**All checks should pass before proceeding.**

---

## Run the Application

### Option 1: Visual Studio (Recommended)

1. **Open Project:**
   - Open `src/VoiceStudio.App/VoiceStudio.App.csproj` in Visual Studio 2022

2. **Set Startup Project:**
   - Right-click `VoiceStudio.App` in Solution Explorer
   - Select "Set as Startup Project"

3. **Start Backend (Terminal 1):**
   ```powershell
   .\venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn api.main:app --reload
   ```
   **Expected Output:**
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   ```

4. **Start Frontend (Visual Studio):**
   - Press **F5** or click "Start" button
   - Application should launch

### Option 2: Command Line

**Terminal 1 - Backend:**
```powershell
.\venv\Scripts\Activate.ps1
cd backend
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd src/VoiceStudio.App
dotnet run
```

### Option 3: PowerShell Script

Create `run-dev.ps1` in the project root:

```powershell
# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\..\venv\Scripts\Activate.ps1; python -m uvicorn api.main:app --reload"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
cd src/VoiceStudio.App
dotnet run
```

Run: `.\run-dev.ps1`

---

## Common Issues

### Issue 1: Python Virtual Environment Activation Fails

**Error:**
```
.\venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled on this system.
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Backend Won't Start

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue 3: Port 8000 Already in Use

**Error:**
```
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
```

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
python -m uvicorn api.main:app --reload --port 8001
```

**Update frontend config** to use port 8001 (if changed).

### Issue 4: Frontend Build Fails

**Error:**
```
error NU1101: Unable to find package
```

**Solution:**
```powershell
# Clean and restore
cd src/VoiceStudio.App
dotnet clean
dotnet restore
dotnet build
```

### Issue 5: Frontend Can't Connect to Backend

**Error:**
```
Connection refused
```

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check backend URL in frontend config
3. Check Windows Firewall settings

### Issue 6: Missing .NET SDK

**Error:**
```
.NET SDK not found
```

**Solution:**
1. Download .NET 8 SDK from [Microsoft](https://dotnet.microsoft.com/download/dotnet/8.0)
2. Install and restart terminal
3. Verify: `dotnet --version`

### Issue 7: Python Not in PATH

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Reinstall Python and check "Add Python to PATH"
2. Or use full path: `C:\Python310\python.exe`
3. Or add Python to PATH manually

---

## Next Steps

### Immediate Next Steps

1. **Explore the Application:**
   - Open the application
   - Navigate through panels
   - Test voice synthesis
   - Check Diagnostics panel

2. **Read Documentation:**
   - [ONBOARDING.md](ONBOARDING.md) - Comprehensive developer onboarding
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
   - [CODE_STRUCTURE.md](CODE_STRUCTURE.md) - Code organization

3. **Set Up IDE:**
   - Configure Visual Studio settings
   - Install recommended extensions
   - Set up debugging

### Development Workflow

**Typical Development Session:**

1. **Start Backend:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn api.main:app --reload
   ```

2. **Start Frontend:**
   - Open in Visual Studio
   - Press F5 to debug

3. **Make Changes:**
   - Edit code
   - Backend auto-reloads (with `--reload`)
   - Frontend requires rebuild

4. **Test Changes:**
   - Test in application
   - Run unit tests
   - Check logs

### Recommended Reading

**Essential:**
- [SETUP.md](SETUP.md) - Detailed setup guide
- [ONBOARDING.md](ONBOARDING.md) - Developer onboarding
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

**Important:**
- [CODE_STRUCTURE.md](CODE_STRUCTURE.md) - Code organization
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [SERVICE_ARCHITECTURE.md](SERVICE_ARCHITECTURE.md) - Service architecture

**Reference:**
- [PANEL_SYSTEM_ARCHITECTURE.md](PANEL_SYSTEM_ARCHITECTURE.md) - Panel system
- [ERROR_HANDLING_PATTERNS.md](ERROR_HANDLING_PATTERNS.md) - Error handling
- [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) - Security practices

### Getting Help

**If you encounter issues:**

1. **Check Common Issues** section above
2. **Review Detailed Documentation:**
   - [SETUP.md](SETUP.md) - Detailed setup troubleshooting
   - [ONBOARDING.md](ONBOARDING.md) - Comprehensive guide
3. **Check Logs:**
   - Backend: Console output
   - Frontend: Visual Studio Output window
4. **Ask for Help:**
   - GitHub Issues (if available)
   - Team chat (if available)

---

## Quick Reference

### Essential Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start backend
cd backend
python -m uvicorn api.main:app --reload

# Build frontend
cd src/VoiceStudio.App
dotnet build

# Run frontend
dotnet run

# Run tests
dotnet test                    # Frontend tests
pytest                         # Backend tests
```

### Project Structure

```
VoiceStudio/
├── src/
│   ├── VoiceStudio.App/      # WinUI 3 frontend
│   └── VoiceStudio.Core/     # Shared core library
├── backend/                  # Python FastAPI backend
│   ├── api/                  # API routes
│   └── mcp_bridge/           # MCP integration
├── docs/                     # Documentation
│   ├── developer/            # Developer docs
│   ├── user/                 # User docs
│   └── api/                  # API docs
└── engines/                  # Engine manifests
```

### Key Files

- **Frontend Entry:** `src/VoiceStudio.App/App.xaml.cs`
- **Backend Entry:** `backend/api/main.py`
- **Configuration:** `backend/.env` (create if needed)
- **Dependencies:** `backend/requirements.txt`, `src/VoiceStudio.App/*.csproj`

---

## Success Checklist

Before you start developing, verify:

- [ ] All prerequisites installed
- [ ] Repository cloned
- [ ] Python virtual environment created and activated
- [ ] Python dependencies installed
- [ ] .NET dependencies restored
- [ ] Frontend builds successfully
- [ ] Backend starts without errors
- [ ] Frontend launches and connects to backend
- [ ] Application is functional (can navigate panels)

**If all checks pass, you're ready to develop!**

---

## Summary

**You should now have:**

✅ Development environment set up  
✅ Application running  
✅ Basic understanding of project structure  
✅ Knowledge of common issues and solutions  

**Next:** Read [ONBOARDING.md](ONBOARDING.md) for comprehensive developer onboarding, or start exploring the codebase!

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**For Detailed Setup:** See [SETUP.md](SETUP.md)  
**For Comprehensive Onboarding:** See [ONBOARDING.md](ONBOARDING.md)

