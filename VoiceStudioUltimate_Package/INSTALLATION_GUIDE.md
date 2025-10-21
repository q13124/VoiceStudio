# VoiceStudio Ultimate - Installation Guide

## 🎉 Welcome to VoiceStudio Ultimate!

VoiceStudio Ultimate is a comprehensive voice cloning and AI assistant system with full Windows integration.

## 🚀 Quick Installation

### **Method 1: Double-Click Install (Recommended)**
1. Double-click `install.bat` in the installer folder
2. Follow the on-screen prompts
3. Installation will complete automatically

### **Method 2: PowerShell Install**
1. Right-click PowerShell and "Run as Administrator"
2. Navigate to the installer directory
3. Run: `powershell -ExecutionPolicy Bypass -File install.ps1`

## ✨ What Gets Installed

### **Applications**
- **VoiceStudio Ultimate Launcher**: Main control panel and service manager
- **VoiceStudio Assistant**: AI Assistant with voice cloning capabilities
- **Voice Cloning Studio**: Advanced voice cloning application
- **Service Dashboard**: Service management and monitoring

### **Windows Integration**
- **Control Panel**: Install/Uninstall from Windows Control Panel
- **Desktop Shortcut**: Quick access from desktop
- **Start Menu**: Complete program group with all applications
- **Taskbar Pin**: Pin to Windows taskbar for quick access
- **Windows Services**: Background services for voice processing

### **Services Installed**
- **VoiceStudio Assistant Service** (Port 5080)
- **VoiceStudio Voice Cloning Service** (Port 5081)
- **VoiceStudio Service Orchestrator** (Port 5082)

## 🎯 Post-Installation

After installation, you can access VoiceStudio through:

1. **Desktop Shortcut**: Double-click "VoiceStudio Ultimate"
2. **Start Menu**: Programs → VoiceStudio Ultimate
3. **Taskbar**: Click the pinned icon
4. **Control Panel**: Programs and Features → VoiceStudio Ultimate

## 🔧 Service Management

Services are automatically installed and started. You can manage them through:

- **VoiceStudio Launcher**: Main control panel
- **Windows Services**: services.msc
- **Service Dashboard**: http://127.0.0.1:5082
- **Command Line**: `sc start/stop VoiceStudioAssistant`

## 🗑️ Uninstallation

### **Method 1: Control Panel**
1. Open Control Panel → Programs and Features
2. Find "VoiceStudio Ultimate"
3. Click "Uninstall"

### **Method 2: PowerShell**
1. Run PowerShell as Administrator
2. Run: `powershell -ExecutionPolicy Bypass -File uninstall.ps1`

### **Method 3: Start Menu**
1. Start Menu → VoiceStudio Ultimate → Uninstall VoiceStudio Ultimate

## 📋 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8GB+ recommended
- **Storage**: 10GB+ free space
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Python**: 3.8+ (will be installed if needed)

## 🆘 Troubleshooting

### **Installation Issues**
- Ensure you're running as Administrator
- Check Windows PowerShell execution policy
- Verify sufficient disk space and permissions

### **Service Issues**
- Check Windows Services (services.msc)
- Verify ports 5080-5082 are available
- Check Windows Event Viewer for errors

### **Performance Issues**
- Ensure GPU drivers are up to date
- Check system resources (RAM, CPU)
- Verify CUDA installation for GPU acceleration

## 📞 Support

For support and updates:
- **Website**: https://voicestudio.ai
- **Version**: 1.0.0
- **Publisher**: VoiceStudio Team

---

**VoiceStudio Ultimate** - Advanced Voice Cloning and AI Assistant System
