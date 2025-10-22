# VoiceStudio Default Project Alias

## 🎯 **PROJECT ALIASES CREATED**

The following aliases and shortcuts have been created for easy access to the VoiceStudio Ultimate Voice Cloning System:

### **Command Line Aliases**
```bash
# VoiceStudio aliases
alias vs="cd C:\Users\Tyler\VoiceStudio"
alias voice-clone="cd C:\Users\Tyler\VoiceStudio && python start-voice-cloning-services.py"
alias voice-studio="cd C:\Users\Tyler\VoiceStudio && python voicestudio_launcher.py"
alias vs-services="cd C:\Users\Tyler\VoiceStudio && python start-services.py"
alias vs-ultimate="cd C:\Users\Tyler\VoiceStudio && python start-voice-studio-ultimate.py"

# Service management aliases
alias vs-start="cd C:\Users\Tyler\VoiceStudio && python start-services.py"
alias vs-stop="cd C:\Users\Tyler\VoiceStudio && python stop-services.py"
alias vs-status="cd C:\Users\Tyler\VoiceStudio && python health_check.py"

# Voice cloning specific aliases
alias clone-voice="cd C:\Users\Tyler\VoiceStudio && python services/voice_cloning/voice_cloning_service.py"
alias voice-synthesis="cd C:\Users\Tyler\VoiceStudio && python services/assistant/enhanced_service.py"
```

### **PowerShell Functions**
```powershell
# VoiceStudio PowerShell functions
function Start-VoiceStudio { Set-Location "C:\Users\Tyler\VoiceStudio"; python start-voice-studio-ultimate.py }
function Start-VoiceCloning { Set-Location "C:\Users\Tyler\VoiceStudio"; python start-voice-cloning-services.py }
function Get-VoiceStudioStatus { Set-Location "C:\Users\Tyler\VoiceStudio"; python health_check.py }
function Restart-VoiceStudioServices { Set-Location "C:\Users\Tyler\VoiceStudio"; python restart-services.py }

# Quick access functions
function vs { Set-Location "C:\Users\Tyler\VoiceStudio" }
function voice-clone { Start-VoiceCloning }
function voice-studio { Start-VoiceStudio }
```

### **Windows Shortcuts**
- **Desktop**: "VoiceStudio Ultimate" shortcut
- **Start Menu**: Programs → VoiceStudio Ultimate
- **Taskbar**: Pinned VoiceStudio icon
- **Control Panel**: Programs and Features → VoiceStudio Ultimate

### **Service Endpoints**
- **Assistant Service**: http://127.0.0.1:5080
- **Voice Cloning Service**: http://127.0.0.1:5081  
- **Orchestrator Service**: http://127.0.0.1:5082
- **Web Interface**: http://127.0.0.1:8080

### **Quick Commands**
```bash
# Start VoiceStudio Ultimate
vs-ultimate

# Start voice cloning services
voice-clone

# Check system status
vs-status

# Access VoiceStudio directory
vs
```

### **Default Project Behavior**
- **ALL voice cloning requests** → VoiceStudio (automatic)
- **ALL audio processing requests** → VoiceStudio (automatic)
- **ALL TTS/speech synthesis requests** → VoiceStudio (automatic)
- **ALL voice analysis requests** → VoiceStudio (automatic)

**Status**: ✅ **ALIASES CREATED & ACTIVE**  
**Last Updated**: 2025-10-20  
**Version**: 1.0.0
