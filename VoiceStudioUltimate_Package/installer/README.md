# VoiceStudio Ultimate Windows Installer

## 🎉 Complete Windows Integration

This installer provides full Windows integration for VoiceStudio Ultimate with voice cloning capabilities.

## ✨ Features Included

### 🖥️ **Windows Integration**
- ✅ **Control Panel**: Install/Uninstall from Windows Control Panel
- ✅ **Desktop Shortcut**: Quick access from desktop
- ✅ **Start Menu**: Full program group with all applications
- ✅ **Taskbar Pin**: Pin to Windows taskbar for quick access
- ✅ **Windows Services**: Background services for voice processing

### 🎯 **Applications Installed**
- **VoiceStudio Ultimate**: Main launcher and control panel
- **VoiceStudio Assistant**: AI Assistant with voice cloning
- **Voice Cloning Studio**: Advanced voice cloning application
- **Service Dashboard**: Service management and monitoring

### 🔧 **Services Installed**
- **VoiceStudio Assistant Service** (Port 5080)
- **VoiceStudio Voice Cloning Service** (Port 5081)
- **VoiceStudio Service Orchestrator** (Port 5082)

## 🚀 **Installation**

### **Method 1: Double-Click Install**
1. Double-click `install.bat`
2. Follow the on-screen prompts
3. Installation will complete automatically

### **Method 2: PowerShell Install**
1. Right-click PowerShell and "Run as Administrator"
2. Navigate to installer directory
3. Run: `powershell -ExecutionPolicy Bypass -File install.ps1`

## 📋 **System Requirements**

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 8GB+ recommended
- **Storage**: 10GB+ free space
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Python**: 3.8+ (will be installed if needed)

## 🎯 **Post-Installation**

After installation, you can access VoiceStudio through:

1. **Desktop Shortcut**: Double-click VoiceStudio Ultimate
2. **Start Menu**: Programs → VoiceStudio Ultimate
3. **Taskbar**: Click the pinned icon
4. **Control Panel**: Programs and Features → VoiceStudio Ultimate

## 🔧 **Service Management**

Services are automatically installed and started. You can manage them through:

- **Windows Services**: services.msc
- **VoiceStudio Dashboard**: http://127.0.0.1:5082
- **Command Line**: `sc start/stop VoiceStudioAssistant`

## 🗑️ **Uninstallation**

### **Method 1: Control Panel**
1. Open Control Panel → Programs and Features
2. Find "VoiceStudio Ultimate"
3. Click "Uninstall"

### **Method 2: PowerShell**
1. Run PowerShell as Administrator
2. Run: `powershell -ExecutionPolicy Bypass -File uninstall.ps1`

### **Method 3: Start Menu**
1. Start Menu → VoiceStudio Ultimate → Uninstall VoiceStudio Ultimate

## 🎉 **What Gets Installed**

### **Files and Directories**
```
C:\Program Files\VoiceStudio\
├── services\                    # All service files
├── VoiceStudio\                 # Core application
├── logs\                        # Log files
├── temp\                        # Temporary files
├── models\                      # AI models
├── config\                      # Configuration files
├── cache\                       # Cache files
├── voicestudio_launcher.exe      # Main launcher
├── install.ps1                   # Installer script
└── uninstall.ps1                 # Uninstaller script
```

### **Registry Entries**
- Control Panel uninstall information
- Service configurations
- Application settings

### **Shortcuts Created**
- Desktop: VoiceStudio Ultimate
- Start Menu: Complete program group
- Taskbar: Pinned application

## 🆘 **Troubleshooting**

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

## 📞 **Support**

For support and updates:
- **Website**: https://voicestudio.ai
- **Version**: 1.0.0
- **Publisher**: VoiceStudio Team

---

**VoiceStudio Ultimate** - Advanced Voice Cloning and AI Assistant System
