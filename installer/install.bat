@echo off
echo VoiceStudio Ultimate Windows Installer
echo =====================================
echo.
echo This will install VoiceStudio Ultimate with the following features:
echo - Control Panel integration
echo - Desktop shortcut
echo - Start Menu shortcuts  
echo - Taskbar pinning
echo - Windows Services
echo.
echo Press any key to continue or close this window to cancel...
pause >nul

echo.
echo Starting installation...
echo.

REM Run PowerShell installer
powershell.exe -ExecutionPolicy Bypass -File "%~dp0install.ps1"

echo.
echo Installation complete!
echo Press any key to exit...
pause >nul
