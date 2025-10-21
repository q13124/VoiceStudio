# VoiceStudio CycloneDX SBOM + VRAM Telemetry + Cursor Integration

## Overview

The VoiceStudio CycloneDX SBOM + VRAM Telemetry + Cursor Integration system provides professional-grade software inventory management, GPU monitoring, and seamless Cursor AI integration with advanced automation features.

## 🚀 **Advanced Features**

### **CycloneDX SBOM Generation**
- **Python SBOM**: Complete Python environment inventory using cyclonedx-py
- **.NET SBOM**: Complete .NET package inventory using CycloneDX CLI
- **Industry Standard**: OWASP CycloneDX format for security and compliance
- **Automated Generation**: Integrated into handoff workflow

### **VRAM Telemetry Monitoring**
- **Background Monitoring**: Scheduled task samples GPU VRAM every 5 minutes
- **Dual Detection**: Uses PyTorch CUDA when available, falls back to nvidia-smi
- **CSV Logging**: Structured telemetry data in CSV format
- **Chart Generation**: Automatic PNG chart generation from telemetry data

### **Cursor AI Integration**
- **Auto-Open**: Automatically opens Cursor with generated handoff file
- **Enhanced Handoff**: Structured JSON with CycloneDX SBOM references
- **Action Planning**: Pre-defined tasks for Cursor AI execution
- **Service Monitoring**: Real-time VoiceStudio service health checks

### **File Management**
- **Auto-Purge**: Keeps last 10 handoff files, 5 snapshots
- **Organized Storage**: Structured file organization in handoff directory
- **Rollback Support**: Safe snapshot creation for system changes

## 📋 **Installation**

### **Method 1: Integrated Installer**
The CycloneDX + VRAM Telemetry + Cursor system is automatically installed with VoiceStudio Ultimate.

### **Method 2: Standalone Installation**
```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File installer\handoff\install_cyclonedx_telemetry.ps1
```

## 🎯 **Usage**

### **Basic CycloneDX + Telemetry Handoff**
```powershell
# Generate handoff with CycloneDX SBOMs and open Cursor
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -OpenCursor
```

### **Install VRAM Telemetry Monitoring**
```powershell
# Install VRAM telemetry scheduler (runs every 5 minutes)
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -InstallTelemetry -OpenCursor
```

### **Performance Options**
```powershell
# Skip build validation for faster runs
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -SkipBuild -OpenCursor

# Skip Python validation
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -SkipPython -OpenCursor

# Skip snapshot creation
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -NoSnapshot -OpenCursor

# Light SBOM (skip file hashing for speed)
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -LightSBOM -OpenCursor
```

### **Advanced Launcher**
```powershell
# Use the enhanced launcher with all features
powershell -ExecutionPolicy Bypass -File installer\handoff\launch_cyclonedx_telemetry.ps1 -OpenCursor

# Generate VRAM chart and purge old files
powershell -ExecutionPolicy Bypass -File installer\handoff\launch_cyclonedx_telemetry.ps1 -GenerateVRAMChart -PurgeOldFiles -OpenCursor
```

## 📊 **Output Files**

### **Handoff Report**
- **Location**: `C:\VoiceStudio\handoff\cursor_handoff.json`
- **Format**: Enhanced structured JSON for Cursor AI consumption
- **Contents**: Environment state, build results, CycloneDX SBOM references, actions

### **CycloneDX SBOMs**
- **Python SBOM**: `C:\VoiceStudio\handoff\sbom_python_cyclonedx_YYYYMMDD_HHMMSS.json`
- **.NET SBOM**: `C:\VoiceStudio\handoff\sbom_dotnet_cyclonedx_YYYYMMDD_HHMMSS.json`
- **Format**: OWASP CycloneDX standard format
- **Contents**: Complete software inventory with dependencies and metadata

### **VRAM Telemetry**
- **CSV Log**: `C:\VoiceStudio\logs\vram_telemetry.csv`
- **Format**: CSV with columns: time_utc, total_mb, used_mb, method
- **Contents**: GPU memory usage over time with detection method

### **VRAM Charts**
- **PNG Chart**: `C:\VoiceStudio\logs\vram_usage_chart.png`
- **Format**: High-resolution PNG chart
- **Contents**: Visual representation of VRAM usage over time

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

SBOMs available:
- Lite SBOM: see `sbom_* .json` in the handoff folder.
- CycloneDX (Python): `sbom_python_cyclonedx_*.json`
- CycloneDX (.NET): `sbom_dotnet_cyclonedx_*.json`

VRAM telemetry available:
- CSV log: `C:\VoiceStudio\logs\vram_telemetry.csv`
- Chart: `C:\VoiceStudio\logs\vram_usage_chart.png` (if generated)
```

### **Enhanced Handoff Schema**
```json
{
  "schema": "voiceStudio.cursorHandoff/v1",
  "summary": "Enhanced system status summary with CycloneDX",
  "env": { /* Enhanced environment state */ },
  "build": { /* Enhanced build results */ },
  "sbom": {
    "lite": "path/to/lite_sbom.json",
    "cyclonedx": {
      "python": "path/to/python_cyclonedx.json",
      "dotnet": "path/to/dotnet_cyclonedx.json"
    }
  },
  "rollback": { /* Rollback information */ },
  "actions": [ /* Enhanced actionable tasks */ ]
}
```

## ⏰ **Automated Scheduling**

### **VRAM Telemetry Scheduler**
```powershell
# Install VRAM telemetry (runs every 5 minutes)
powershell -ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -InstallTelemetry

# Remove VRAM telemetry task
Unregister-ScheduledTask -TaskName "VoiceStudio VRAM Telemetry" -Confirm:$false
```

### **Windows Task Scheduler Setup**
```powershell
# Create 15-minute scheduled task for handoff generation
powershell -ExecutionPolicy Bypass -File installer\handoff\setup_scheduler.ps1

# Remove scheduled task
powershell -ExecutionPolicy Bypass -File installer\handoff\setup_scheduler.ps1 -Remove
```

## 🔧 **Configuration**

### **CycloneDX Tools**
The system automatically installs and updates:
- **cyclonedx-py**: Python SBOM generation
- **CycloneDX CLI**: .NET SBOM generation

### **VRAM Telemetry Configuration**
- **Sampling Interval**: 5 minutes (configurable)
- **Detection Methods**: PyTorch CUDA → nvidia-smi fallback
- **Log Format**: CSV with UTC timestamps
- **Storage**: `C:\VoiceStudio\logs\vram_telemetry.csv`

### **File Management**
- **Handoff Retention**: Last 10 files kept
- **Snapshot Retention**: Last 5 snapshots kept
- **Auto-Purge**: Available via launcher option

## 🎯 **Enhanced Action Plans**

The system generates comprehensive actionable tasks for Cursor AI:

### **Package Management**
- Automatic FFmpeg installation via Winget/Choco
- Git installation if missing
- Dependency resolution and validation

### **Build Validation**
- .NET restore, build, and test commands
- Python dependency synchronization
- CycloneDX SBOM generation

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
- **CycloneDX Issues**: Ensure tools are installed and updated

### **Performance Optimization**
- Use `-LightSBOM` for faster runs without file hashing
- Use `-SkipBuild` for quick handoff generation
- Use `-NoSnapshot` to skip rollback creation
- Use `-SkipPython` to skip Python validation

### **VRAM Telemetry Issues**
- Verify NVIDIA GPU and drivers
- Check Python venv availability
- Ensure scheduled task permissions
- Validate CSV file permissions

### **Logs**
- **Location**: `C:\VoiceStudio\logs\auto_handoff_YYYYMMDD.log`
- **Format**: Timestamped log entries with enhanced detail
- **Contents**: Complete execution information and diagnostics

## 🔮 **Advanced Features**

### **CycloneDX SBOM Export**
- Complete software inventory in industry standard format
- Security vulnerability assessment
- License compliance tracking
- Component dependency mapping

### **VRAM Telemetry Analysis**
- GPU memory usage trends
- Performance bottleneck identification
- CUDA workload optimization
- Resource planning insights

### **Enhanced Risk Assessment**
- Version drift detection
- Dependency compatibility analysis
- Performance bottleneck identification
- Security vulnerability scanning

### **Automated File Management**
- Intelligent file retention policies
- Automatic cleanup of old files
- Organized storage structure
- Rollback point management

## 📈 **Integration Benefits**

### **Development Workflow**
- Seamless Cursor AI integration with auto-open
- Automated environment validation
- Continuous system monitoring
- Proactive issue detection

### **Production Readiness**
- Comprehensive system validation
- Automated testing and verification
- Performance monitoring
- Security assessment

### **Compliance & Security**
- Industry-standard SBOM generation
- Software inventory management
- License compliance tracking
- Security vulnerability assessment

### **Maintenance Automation**
- Automated dependency management
- System health monitoring
- Performance optimization
- Issue resolution guidance

---

**VoiceStudio CycloneDX SBOM + VRAM Telemetry + Cursor Integration** - Professional-grade software inventory management, GPU monitoring, and AI development workflow automation
