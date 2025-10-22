VoiceStudio Scripts — Drop 1
============================
1) VoiceStudio-AddOns-Install.ps1
   - Put VoiceStudio_AddOns_Drop1.zip in your Downloads folder.
   - Run as:  PowerShell 5.1
       Set-ExecutionPolicy -Scope Process Bypass -Force
       .\VoiceStudio-AddOns-Install.ps1
   - It installs files, creates/uses .venv, and ensures FastAPI + uvicorn.

2) VoiceStudio-RunWS.ps1
   - Starts a demo FastAPI app that serves /v1/stream/{voice_id} over WebSocket.
   - Run:
       .\VoiceStudio-RunWS.ps1 -ProjectRoot "C:\VoiceStudio" -Port 5071

3) VoiceStudio-QualityReport-Demo.ps1
   - Calls the quality_report stub and prints a JSON-like dict.
   - Run:
       .\VoiceStudio-QualityReport-Demo.ps1 -ProjectRoot "C:\VoiceStudio"
