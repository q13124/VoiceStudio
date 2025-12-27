# VoiceStudio Quantum+ Developer Troubleshooting Guide

Comprehensive troubleshooting guide for developers working on VoiceStudio Quantum+.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Ready for Use

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Common Development Issues](#common-development-issues)
3. [Build Errors](#build-errors)
4. [Runtime Errors](#runtime-errors)
5. [Debugging Tips](#debugging-tips)
6. [Performance Issues](#performance-issues)
7. [Development Environment Issues](#development-environment-issues)
8. [FAQ for Developers](#faq-for-developers)

---

## Quick Reference

### Most Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Backend won't start | Check Python environment, install dependencies |
| Frontend won't build | `dotnet restore`, clean and rebuild |
| Connection failed | Verify backend running on port 8000 |
| Import errors | Check virtual environment, verify Python path |
| GPU not available | Install CUDA, verify PyTorch CUDA support |
| Port already in use | Kill process using port 8000 |

---

## Common Development Issues

### Backend Won't Start

**Symptoms:**
- `ModuleNotFoundError` or import errors
- Port already in use
- Backend crashes on startup

**Solutions:**

1. **Check Python Environment:**
   ```powershell
   python --version  # Should be 3.10+
   which python      # Verify using correct Python
   ```

2. **Activate Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   # Verify: which python should point to venv
   ```

3. **Install Dependencies:**
   ```powershell
   pip install -r backend/requirements.txt
   ```

4. **Check Port Availability:**
   ```powershell
   # Check if port 8000 is in use
   netstat -ano | findstr :8000
   # Kill process if needed
   taskkill /PID <pid> /F
   ```

5. **Check Backend Logs:**
   - Review console output for errors
   - Check for missing dependencies
   - Verify Python path

**Common Causes:**
- Virtual environment not activated
- Missing Python packages
- Port conflict with another application
- Python version mismatch

---

### Frontend Won't Build

**Symptoms:**
- Build errors in Visual Studio
- Missing NuGet packages
- Type errors
- XAML compilation errors

**Solutions:**

1. **Restore NuGet Packages:**
   ```powershell
   cd src/VoiceStudio.App
   dotnet restore
   ```

2. **Clean and Rebuild:**
   ```powershell
   dotnet clean
   dotnet build --configuration Debug
   ```

3. **Check .NET Version:**
   ```powershell
   dotnet --version  # Should be 8.0.x
   ```

4. **Verify Project File:**
   - Check `TargetFramework` is `net8.0-windows10.0.19041.0`
   - Verify Windows App SDK version
   - Check package references

5. **Check Visual Studio:**
   - Update Visual Studio to latest version
   - Install .NET 8 SDK workload
   - Install Windows App SDK extension

**Common Build Errors:**

**Error: "Package restore failed"**
- Solution: Check internet connection, clear NuGet cache
- Command: `dotnet nuget locals all --clear`

**Error: "The type or namespace name could not be found"**
- Solution: Restore packages, check using statements
- Verify project references

**Error: "XAML compilation failed"**
- Solution: Check XAML syntax, verify resource references
- Check for missing design tokens

---

### Backend Connection Failed

**Symptoms:**
- Frontend can't connect to backend
- "Connection refused" errors
- API calls fail

**Solutions:**

1. **Verify Backend Running:**
   ```powershell
   # Check if backend is running
   curl http://localhost:8000/health
   # Or use browser: http://localhost:8000/docs
   ```

2. **Check Backend URL:**
   - Verify `BackendClientConfig.BaseUrl` is correct
   - Default: `http://localhost:8000`
   - Check in `src/VoiceStudio.Core/Services/BackendClientConfig.cs`

3. **Check Firewall:**
   - Windows Firewall may block connections
   - Add exception for Python/uvicorn
   - Allow localhost connections

4. **Check CORS:**
   - Backend should allow CORS from frontend
   - Check `backend/api/main.py` CORS configuration
   - Verify allowed origins include frontend

5. **Check Backend Logs:**
   - Review backend console output
   - Check for startup errors
   - Verify FastAPI app initialized

**Common Causes:**
- Backend not started
- Port conflict
- Firewall blocking
- CORS misconfiguration

---

### Engines Not Loading

**Symptoms:**
- No engines available in UI
- Engine import errors
- Engine initialization fails

**Solutions:**

1. **Check Engine Manifests:**
   ```powershell
   # Verify manifests exist
   Get-ChildItem engines\audio\*\engine.manifest.json -Recurse
   ```

2. **Check Engine Dependencies:**
   ```powershell
   # Install engine-specific dependencies
   pip install torch transformers coqui-tts
   ```

3. **Check Engine Entry Points:**
   - Verify `entry_point` in manifest is correct
   - Verify engine class exists and is importable
   - Check Python path includes engine directory

4. **Check Engine Logs:**
   - Review backend logs for import errors
   - Check for missing dependencies
   - Verify engine registration

5. **Test Engine Import:**
   ```python
   # Test engine import
   python -c "from app.core.engines.audio.xtts import XTTSEngine; print('OK')"
   ```

**Common Causes:**
- Missing engine dependencies
- Incorrect entry point in manifest
- Python path issues
- Engine class not found

---

### Import Errors

**Symptoms:**
- `ModuleNotFoundError` in Python
- `using` statement errors in C#
- Type not found errors

**Solutions:**

**Python Import Errors:**

1. **Check Python Path:**
   ```python
   import sys
   print(sys.path)  # Verify paths include project directories
   ```

2. **Check Virtual Environment:**
   ```powershell
   which python  # Should point to venv
   pip list      # Verify packages installed
   ```

3. **Install Missing Packages:**
   ```powershell
   pip install <package-name>
   ```

4. **Check Relative Imports:**
   - Use absolute imports when possible
   - Check `__init__.py` files exist
   - Verify package structure

**C# Import Errors:**

1. **Check Using Statements:**
   - Verify namespace is correct
   - Check project references
   - Verify assembly references

2. **Check Project References:**
   - Verify `VoiceStudio.Core` referenced in `VoiceStudio.App`
   - Check NuGet packages installed
   - Rebuild solution

3. **Check Assembly References:**
   - Verify DLLs in output directory
   - Check for missing dependencies
   - Verify .NET version compatibility

---

### GPU Not Available

**Symptoms:**
- Engines fall back to CPU
- Slow performance
- CUDA errors

**Solutions:**

1. **Check CUDA Installation:**
   ```python
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Install CUDA Toolkit:**
   - Download from NVIDIA
   - Install CUDA 11.8 or 12.1
   - Verify installation

3. **Install PyTorch with CUDA:**
   ```powershell
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Verify GPU:**
   ```python
   import torch
   print(torch.cuda.is_available())
   print(torch.cuda.get_device_name(0))
   ```

5. **Check GPU Memory:**
   ```python
   import torch
   print(torch.cuda.get_device_properties(0).total_memory / 1024**3)  # GB
   ```

**Common Causes:**
- CUDA not installed
- PyTorch CPU-only version
- GPU drivers outdated
- Insufficient GPU memory

---

## Build Errors

### .NET Build Errors

**Error: "The target framework is not supported"**

**Solution:**
- Verify .NET 8 SDK installed
- Check `TargetFramework` in `.csproj`
- Update Visual Studio

**Error: "Package restore failed"**

**Solution:**
```powershell
dotnet nuget locals all --clear
dotnet restore
```

**Error: "Windows App SDK not found"**

**Solution:**
- Install Windows App SDK extension in Visual Studio
- Verify package reference in `.csproj`
- Check Windows SDK version

**Error: "XAML compilation failed"**

**Solution:**
- Check XAML syntax
- Verify resource references
- Check for missing design tokens
- Verify `x:Class` attributes

### Python Build Errors

**Error: "pip install failed"**

**Solution:**
```powershell
pip install --upgrade pip
pip install -r backend/requirements.txt --no-cache-dir
```

**Error: "Wheel build failed"**

**Solution:**
- Install build tools: `pip install build`
- Check Python version compatibility
- Use pre-built wheels when available

---

## Runtime Errors

### Frontend Runtime Errors

**Error: "NullReferenceException"**

**Solution:**
- Check null checks before accessing properties
- Verify ViewModel initialization
- Check data binding

**Error: "XamlParseException"**

**Solution:**
- Check XAML syntax
- Verify resource references
- Check for missing converters
- Verify design tokens exist

**Error: "InvalidOperationException"**

**Solution:**
- Check thread affinity (UI thread)
- Verify dispatcher usage
- Check async/await patterns

### Backend Runtime Errors

**Error: "FastAPI startup failed"**

**Solution:**
- Check `main.py` for syntax errors
- Verify route imports
- Check middleware configuration
- Review startup logs

**Error: "Engine initialization failed"**

**Solution:**
- Check engine dependencies
- Verify model files exist
- Check GPU availability
- Review engine logs

**Error: "Database connection failed"**

**Solution:**
- Verify database running
- Check connection string
- Verify credentials
- Check network connectivity

---

## Debugging Tips

### Visual Studio Debugging

**Setting Breakpoints:**
1. Click in left margin to set breakpoint
2. Or press F9 on line
3. Breakpoint appears as red dot

**Debugging Controls:**
- **F5**: Start debugging
- **F10**: Step over
- **F11**: Step into
- **Shift+F11**: Step out
- **Ctrl+Shift+F5**: Restart debugging
- **Shift+F5**: Stop debugging

**Debug Windows:**
- **Watch Window**: Monitor variable values
- **Call Stack**: See execution path
- **Immediate Window**: Evaluate expressions
- **Output Window**: View debug output
- **Locals Window**: See local variables

**Debugging Tips:**
- Use conditional breakpoints
- Set breakpoints on exceptions
- Use Debug.WriteLine for logging
- Check exception details in Output window

### VS Code Python Debugging

**Launch Configuration:**
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

**Debugging Tips:**
- Set breakpoints in Python code
- Use debug console for evaluation
- Check variables panel
- Review call stack

### Logging

**Frontend Logging:**
```csharp
using System.Diagnostics;

Debug.WriteLine("Debug message");
_logger.LogInformation("Info message");
_logger.LogError("Error message", exception);
```

**Backend Logging:**
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", exc_info=True)
```

**Log Locations:**
- Frontend: `%LocalAppData%\VoiceStudio\logs\`
- Backend: Console output or `backend/logs/`

---

## Performance Issues

### Slow Application Startup

**Symptoms:**
- Application takes > 5 seconds to start
- UI freezes during startup

**Solutions:**

1. **Check Startup Code:**
   - Minimize work in `App.xaml.cs` constructor
   - Use async initialization
   - Defer heavy operations

2. **Check Service Initialization:**
   - Lazy load services
   - Initialize in background
   - Use dependency injection efficiently

3. **Check Resource Loading:**
   - Optimize XAML resources
   - Use resource dictionaries efficiently
   - Minimize image loading

### Slow API Responses

**Symptoms:**
- API calls take > 1 second
- Timeout errors

**Solutions:**

1. **Check Backend Performance:**
   - Profile backend code
   - Check database queries
   - Optimize engine operations

2. **Check Network:**
   - Verify localhost connection
   - Check for network latency
   - Verify no firewall issues

3. **Check Request Size:**
   - Minimize request payload
   - Use compression
   - Optimize data serialization

### High Memory Usage

**Symptoms:**
- Application uses > 2 GB RAM
- Out of memory errors

**Solutions:**

1. **Check Memory Leaks:**
   - Use memory profiler
   - Check event handler subscriptions
   - Verify object disposal

2. **Check Resource Management:**
   - Dispose of resources properly
   - Use using statements
   - Clear large collections

3. **Check Caching:**
   - Limit cache size
   - Implement cache eviction
   - Clear unused cache entries

---

## Development Environment Issues

### Visual Studio Issues

**Issue: IntelliSense not working**

**Solution:**
- Rebuild solution
- Clear IntelliSense cache
- Restart Visual Studio

**Issue: Hot Reload not working**

**Solution:**
- Enable Hot Reload in settings
- Check project supports Hot Reload
- Restart Visual Studio

**Issue: XAML Designer not loading**

**Solution:**
- Check XAML syntax
- Verify design-time data
- Restart Visual Studio

### Python Environment Issues

**Issue: Virtual environment not activating**

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

**Issue: Packages not installing**

**Solution:**
```powershell
pip install --upgrade pip
pip install -r backend/requirements.txt --no-cache-dir
```

**Issue: Python path issues**

**Solution:**
- Verify Python in PATH
- Check virtual environment activated
- Use full paths if needed

---

## FAQ for Developers

### General Questions

**Q: How do I add a new panel?**
A: See [PANEL_SYSTEM_ARCHITECTURE.md](PANEL_SYSTEM_ARCHITECTURE.md) for panel development guide.

**Q: How do I add a new service?**
A: Register service in `ServiceProvider.cs`, implement interface, inject via constructor.

**Q: How do I add a new API endpoint?**
A: Create route file in `backend/api/routes/`, register in `main.py`, document in API docs.

**Q: How do I test my changes?**
A: Run unit tests, integration tests, manual testing. See [TESTING.md](TESTING.md).

### Build Questions

**Q: Why does the build fail after pulling changes?**
A: Run `dotnet restore` and `pip install -r backend/requirements.txt` to update dependencies.

**Q: How do I clean the build?**
A: Run `dotnet clean` and delete `bin/` and `obj/` directories.

**Q: How do I build for Release?**
A: Use `dotnet build --configuration Release` or select Release in Visual Studio.

### Runtime Questions

**Q: Why does the backend crash on startup?**
A: Check Python version, virtual environment, dependencies, and logs.

**Q: Why can't the frontend connect to backend?**
A: Verify backend running on port 8000, check firewall, verify CORS settings.

**Q: Why are engines not loading?**
A: Check engine manifests, dependencies, Python path, and logs.

### Debugging Questions

**Q: How do I debug the frontend?**
A: Use Visual Studio debugger, set breakpoints, use Debug.WriteLine for logging.

**Q: How do I debug the backend?**
A: Use VS Code Python debugger, set breakpoints, use logging module.

**Q: How do I see backend logs?**
A: Check console output or log files in `backend/logs/` or `%LocalAppData%\VoiceStudio\logs\`.

### Performance Questions

**Q: Why is the application slow?**
A: Check memory usage, CPU usage, network latency, and optimize accordingly.

**Q: How do I profile the application?**
A: Use Visual Studio profiler for frontend, use Python profilers for backend.

**Q: How do I optimize performance?**
A: See [PERFORMANCE_TESTING_GUIDE.md](../testing/PERFORMANCE_TESTING_GUIDE.md) for optimization strategies.

---

## Getting Help

### Resources

- **Documentation:** `docs/developer/`
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Code Review:** [CODE_REVIEW_CHECKLIST.md](CODE_REVIEW_CHECKLIST.md)
- **Error Handling:** [ERROR_HANDLING_PATTERNS.md](ERROR_HANDLING_PATTERNS.md)

### Reporting Issues

**Before Reporting:**
1. Check this troubleshooting guide
2. Search existing issues
3. Review logs
4. Reproduce issue

**When Reporting:**
- Describe the issue clearly
- Include error messages
- Provide steps to reproduce
- Include relevant logs
- Specify environment details

---

## Summary

This troubleshooting guide covers:

1. **Common Development Issues:** Backend, frontend, engines, imports
2. **Build Errors:** .NET and Python build errors
3. **Runtime Errors:** Frontend and backend runtime errors
4. **Debugging Tips:** Visual Studio and VS Code debugging
5. **Performance Issues:** Startup, API, memory issues
6. **Development Environment Issues:** Visual Studio and Python issues
7. **FAQ:** Common developer questions

**Key Takeaways:**
- Always check logs first
- Verify environment setup
- Use debugging tools effectively
- Profile before optimizing
- Document issues for future reference

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After major changes or new issues discovered

