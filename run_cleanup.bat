@echo off
echo Running VoiceCloner Cleanup Script...
powershell.exe -ExecutionPolicy Bypass -File "scripts\Clean-VoiceCloner.ps1" -CleanNow
echo Cleanup completed!
pause
