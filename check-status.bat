@echo off
title VoiceStudio Status Checker
color 0A

echo ========================================
echo   VoiceStudio Voice Cloning System
echo   Status Checker
echo ========================================
echo.

echo Checking services...
echo.

:: Check Web Interface
curl -s http://localhost:8080/health >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Web Interface: RUNNING (Port 8080)
    echo       Access: http://localhost:8080
) else (
    echo [X] Web Interface: NOT RUNNING
)

:: Check Voice Cloning Service
curl -s http://localhost:5083/health >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Voice Cloning Service: RUNNING (Port 5083)
    echo       API: http://localhost:5083
) else (
    echo [X] Voice Cloning Service: NOT RUNNING
)

echo.
echo ========================================
echo   CURRENT STATUS
echo ========================================
echo.

:: Check if web interface is accessible
curl -s http://localhost:8080/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ WEBSITE VERSION: READY TO USE
    echo    Open: http://localhost:8080
    echo.
    echo 🎯 You can use the website version right now!
    echo    - Upload audio files
    echo    - Enter text to clone
    echo    - Generate voice clones
    echo.
) else (
    echo ❌ Website not accessible
)

echo.
echo ========================================
echo   NEXT STEPS
echo ========================================
echo.
echo 1. WEBSITE VERSION (Ready Now):
echo    - Open: http://localhost:8080
echo    - Upload audio file
echo    - Enter text
echo    - Click "Clone Voice"
echo.
echo 2. WINDOWS PROGRAM (Optional):
echo    - Run: install-complete-voice-studio.bat
echo    - Get desktop shortcuts
echo    - Professional installation
echo.
echo 3. QUICK START:
echo    - Run: start-voice-studio.bat
echo    - Starts both services
echo.
echo Press any key to open web interface...
pause >nul

:: Open web interface
start http://localhost:8080

echo.
echo Web interface opened!
echo You can start using VoiceStudio right now.
echo.
pause
