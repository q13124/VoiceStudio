@echo off
echo Starting VoiceStudio WinUI Application...
cd /d "%~dp0"
dotnet run --configuration Release
pause
