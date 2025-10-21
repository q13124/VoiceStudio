# VoiceStudio Enhanced Auto Handoff System

## Overview

The VoiceStudio Enhanced Auto Handoff system provides comprehensive automated integration with Cursor AI, including advanced package management, SBOM export, GPU VRAM testing, and comprehensive system monitoring.

## 🚀 **Enhanced Features**

### **Package Management**
- **Winget Integration**: Automatic package installation via Windows Package Manager
- **Chocolatey Support**: Fallback package management via Choco
- **Dependency Resolution**: Automatic FFmpeg, Git, and other tool installation

### **SBOM Export**
- **Software Bill of Materials**: Complete component inventory
- **File Hashing**: SHA256 hashes for integrity verification
- **Package Tracking**: .NET, Python, Winget, and Choco package lists
- **Light Mode**: Skip file hashing for faster runs with `-LightSBOM`

### **GPU VRAM Testing**
- **Memory Allocation**: Tests GPU memory allocation stability
- **CUDA Validation**: Verifies CUDA functionality and performance
- **Pressure Testing**: Ensures GPU can handle voice processing workloads

### **Enhanced Monitoring**
- **Service Health**: Comprehensive VoiceStudio service monitoring
- **Risk Assessment**: Advanced drift detection and issue identification
- **Recommendations**: Automated suggestions for system improvements

## 📋 **Installation**

### **Method 1: Integrated Installer**
The Enhanced Auto Handoff system is automatically installed with VoiceStudio Ultimate.

### **Method 2: Standalone Installation**
```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File installer\handoff\install_enhanced_handoff.ps1
```

## 🎯 **Usage**

### **Basic Enhanced Handoff**
```powershell
# Generate enhanced handoff for Cursor AI
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1
```

### **Performance Options**
```powershell
# Skip build validation for faster runs
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -SkipBuild

# Skip Python validation
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -SkipPython

# Skip snapshot creation
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -NoSnapshot

# Light SBOM (skip file hashing for speed)
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -LightSBOM
```

### **Quick Launcher**
```powershell
# Use the enhanced launcher
powershell -ExecutionPolicy Bypass -File installer\handoff\launch_enhanced_handoff.ps1
```

## 📊 **Output Files**

### **Handoff Report**
- **Location**: `C:\VoiceStudio\handoff\cursor_handoff.json`
- **Format**: Enhanced structured JSON for Cursor AI consumption
- **Contents**: Environment state, build results, risks, actions, SBOM reference

### **SBOM Export**
- **Location**: `C:\VoiceStudio\handoff\sbom_YYYYMMDD_HHMMSS.json`
- **Format**: CycloneDX-style software bill of materials
- **Contents**: Complete component inventory with versions and hashes

### **Environment Snapshot**
- **Location**: `C:\VoiceStudio\handoff\env_snapshot.json`
- **Format**: Complete system state capture
- **Contents**: Tools, hardware, services, configuration

### **Rollback Snapshot**
- **Location**: `C:\VoiceStudio\handoff\snapshot_YYYYMMDD_HHMMSS.zip`
- **Format**: Compressed archive of entire VoiceStudio directory
- **Purpose**: Safe rollback point for system changes

## 🤖 **Cursor AI Integration**

### **Enhanced Agent Prompt**
Use this exact prompt in Cursor's agent chat:

```
You are the VoiceStudio/UltraClone CI upgrader.
Read C:\VoiceStudio\handoff\cursor_handoff.json.
Follow "actions" in order:
- cd to "cwd"; run each "commands" element exactly.
- If a command fails, capture stderr and stop. Suggest the minimal fix; do not change roles or architecture.
- After each action, verify "success_hint". If unmet, propose a targeted patch and wait for approval.
- Keep pins.json contracts. Never alter agent roles/instructions.
- Write a concise report to C:\VoiceStudio\handoff\cursor_run_report.txt.
- Confirm service health: GET http://127.0.0.1:5080/health returns 200.
```

### **Enhanced Handoff Schema**
```json
{
  "schema": "voiceStudio.cursorHandoff/v1",
  "summary": "Enhanced system status summary",
  "env": { /* Enhanced environment state */ },
  "packages": { /* Winget/Choco inventories */ },
  "build": { /* Enhanced build results */ },
  "sbom": "path/to/sbom.json",
  "risks": [ /* Enhanced risk assessment */ ],
  "recommendations": [ /* Automated recommendations */ ],
  "rollback": { /* Rollback information */ },
  "actions": [ /* Enhanced actionable tasks */ ]
}
```

## ⏰ **Automated Scheduling**

### **Windows Task Scheduler Setup**
```powershell
# Create 15-minute scheduled task
powershell -ExecutionPolicy Bypass -File installer\handoff\setup_scheduler.ps1

# Remove scheduled task
powershell -ExecutionPolicy Bypass -File installer\handoff\setup_scheduler.ps1 -Remove
```

### **Manual Scheduling**
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -SkipBuild -LightSBOM"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "VoiceStudio Auto Handoff" -Action $action -Trigger $trigger -Description "Builds Cursor handoff every 15m" -User "$env:USERNAME" -RunLevel Highest
```

## 🔧 **Configuration**

### **Enhanced Pins Configuration**
Edit `C:\VoiceStudio\pins.json` to specify version requirements:

```json
{
  "python": "3.10.*",
  "dotnet_sdk": "8.*",
  "torch": "2.2.2",
  "torchaudio": "2.2.2",
  "coqui_tts": "0.24.1",
  "transformers": "4.55.4",
  "faster_whisper": "1.0.3",
  "nv_driver_min": "546.00",
  "cuda_toolkit": "12.1",
  "ffmpeg": ">=6.0"
}
```

## 🎯 **Enhanced Action Plans**

The system generates comprehensive actionable tasks for Cursor AI:

### **Package Management**
- Automatic FFmpeg installation via Winget/Choco
- Git installation if missing
- Dependency resolution and validation

### **Build Validation**
- .NET restore, build, and test commands
- Python dependency synchronization
- GPU VRAM pressure testing

### **Service Management**
- VoiceStudio service startup and health validation
- Service orchestration and monitoring
- Health endpoint verification

### **Voice Cloning Validation**
- Pipeline testing and optimization
- Model validation and performance testing
- CUDA functionality verification

### **System Maintenance**
- IPC regeneration
- SBOM generation and validation
- Comprehensive health monitoring

## 🆘 **Troubleshooting**

### **Common Issues**
- **Permission Errors**: Run as Administrator
- **Service Failures**: Check VoiceStudio service status
- **Build Errors**: Validate .NET SDK and Python environment
- **CUDA Issues**: Verify NVIDIA drivers and CUDA installation
- **Package Manager Issues**: Ensure Winget or Choco is available

### **Performance Optimization**
- Use `-LightSBOM` for faster runs without file hashing
- Use `-SkipBuild` for quick handoff generation
- Use `-NoSnapshot` to skip rollback creation

### **Logs**
- **Location**: `C:\VoiceStudio\logs\auto_handoff_YYYYMMDD.log`
- **Format**: Timestamped log entries with enhanced detail
- **Contents**: Complete execution information and diagnostics

## 🔮 **Advanced Features**

### **SBOM Export**
- Complete software inventory
- File integrity verification
- Component dependency tracking
- Security vulnerability assessment

### **GPU VRAM Testing**
- Memory allocation stability
- CUDA performance validation
- VRAM pressure testing
- GPU workload compatibility

### **Enhanced Risk Assessment**
- Version drift detection
- Dependency compatibility analysis
- Performance bottleneck identification
- Security vulnerability scanning

## 📈 **Integration Benefits**

### **Development Workflow**
- Seamless Cursor AI integration
- Automated environment validation
- Continuous system monitoring
- Proactive issue detection

### **Production Readiness**
- Comprehensive system validation
- Automated testing and verification
- Performance monitoring
- Security assessment

### **Maintenance Automation**
- Automated dependency management
- System health monitoring
- Performance optimization
- Issue resolution guidance

---

**VoiceStudio Enhanced Auto Handoff System** - Complete Cursor AI Integration with Advanced Features
