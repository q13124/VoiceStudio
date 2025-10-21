#!/usr/bin/env python3
"""
VoiceStudio Ultimate Complete Windows Package
Creates a comprehensive Windows installer package with all components.
"""

import os
import sys
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VoiceStudioCompletePackage:
    """Creates complete VoiceStudio Windows package"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.package_dir = self.project_root / "VoiceStudioUltimate_Package"
        self.installer_dir = self.package_dir / "installer"
        self.app_dir = self.package_dir / "app"
        
    def create_package_structure(self):
        """Create package directory structure"""
        logger.info("Creating package structure...")
        
        directories = [
            self.package_dir,
            self.installer_dir,
            self.app_dir,
            self.app_dir / "services",
            self.app_dir / "VoiceStudio",
            self.app_dir / "scripts",
            self.app_dir / "config",
            self.app_dir / "docs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def copy_application_files(self):
        """Copy all application files to package"""
        logger.info("Copying application files...")
        
        # Copy main application files
        source_files = [
            "services",
            "VoiceStudio", 
            "*.py",
            "*.bat",
            "*.ps1",
            "requirements*.txt",
            "*.md"
        ]
        
        for pattern in source_files:
            source_path = self.project_root / pattern
            if source_path.exists():
                if source_path.is_dir():
                    dest_path = self.app_dir / pattern
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, self.app_dir)
                logger.info(f"Copied: {pattern}")
        
        # Copy installer files
        installer_source = self.project_root / "installer"
        if installer_source.exists():
            shutil.copytree(installer_source, self.installer_dir, dirs_exist_ok=True)
            logger.info("Copied installer files")
    
    def create_launcher_executable(self):
        """Create main launcher executable"""
        logger.info("Creating launcher executable...")
        
        launcher_script = '''#!/usr/bin/env python3
"""
VoiceStudio Ultimate Launcher
Main application launcher with GUI and service management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os
import sys
import json
import webbrowser
from pathlib import Path
import psutil

class VoiceStudioLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VoiceStudio Ultimate")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set window icon
        try:
            self.root.iconbitmap("voicestudio.ico")
        except:
            pass
        
        self.services = {
            "assistant": {"name": "Assistant Service", "port": 5080, "running": False, "url": "http://127.0.0.1:5080"},
            "voice_cloning": {"name": "Voice Cloning Service", "port": 5081, "running": False, "url": "http://127.0.0.1:5081"},
            "orchestrator": {"name": "Service Orchestrator", "port": 5082, "running": False, "url": "http://127.0.0.1:5082"}
        }
        
        self.create_ui()
        self.check_services()
        
    def create_ui(self):
        """Create user interface"""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="VoiceStudio Ultimate", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="Advanced Voice Cloning & AI Assistant System", 
                                  font=("Arial", 12))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 30))
        
        # Service status frame
        status_frame = ttk.LabelFrame(main_frame, text="Service Status", padding="15")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        status_frame.columnconfigure(1, weight=1)
        
        self.service_vars = {}
        self.service_labels = {}
        
        for i, (service_id, service_info) in enumerate(self.services.items()):
            # Service name
            name_label = ttk.Label(status_frame, text=service_info["name"], 
                                 font=("Arial", 10, "bold"))
            name_label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            # Status indicator
            status_label = ttk.Label(status_frame, text="Checking...", foreground="orange")
            status_label.grid(row=i, column=1, sticky=tk.W, padx=(20, 0), pady=5)
            self.service_labels[service_id] = status_label
            
            # Open button
            open_btn = ttk.Button(status_frame, text="Open", 
                               command=lambda sid=service_id: self.open_service(sid))
            open_btn.grid(row=i, column=2, padx=(10, 0), pady=5)
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Service Control", padding="15")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, columnspan=3)
        
        ttk.Button(button_frame, text="Start All Services", 
                  command=self.start_all_services).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Stop All Services", 
                  command=self.stop_all_services).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Restart All Services", 
                  command=self.restart_all_services).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Check Status", 
                  command=self.check_services).grid(row=0, column=3, padx=5, pady=5)
        
        # Applications frame
        app_frame = ttk.LabelFrame(main_frame, text="Applications", padding="15")
        app_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        app_button_frame = ttk.Frame(app_frame)
        app_button_frame.grid(row=0, column=0, columnspan=3)
        
        ttk.Button(app_button_frame, text="VoiceStudio Assistant", 
                  command=self.open_assistant).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(app_button_frame, text="Voice Cloning Studio", 
                  command=self.open_voice_cloner).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(app_button_frame, text="Service Dashboard", 
                  command=self.open_dashboard).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(app_button_frame, text="System Monitor", 
                  command=self.open_monitor).grid(row=0, column=3, padx=5, pady=5)
        
        # System info frame
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="15")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = tk.Text(info_frame, height=10, width=80, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        # Update system info
        self.update_system_info()
        
    def check_services(self):
        """Check service status"""
        for service_id, service_info in self.services.items():
            try:
                # Check if port is in use
                running = False
                for conn in psutil.net_connections():
                    if conn.laddr.port == service_info["port"] and conn.status == "LISTEN":
                        running = True
                        break
                
                service_info["running"] = running
                
                if running:
                    self.service_labels[service_id].config(text="Running", foreground="green")
                else:
                    self.service_labels[service_id].config(text="Stopped", foreground="red")
                    
            except Exception as e:
                service_info["running"] = False
                self.service_labels[service_id].config(text="Error", foreground="orange")
        
        # Schedule next check
        self.root.after(5000, self.check_services)
    
    def start_all_services(self):
        """Start all services"""
        def start_services():
            for service_id, service_info in self.services.items():
                try:
                    if not service_info["running"]:
                        # Start service based on type
                        if service_id == "assistant":
                            subprocess.Popen([sys.executable, "services/assistant/enhanced_service.py"], 
                                          cwd=os.path.dirname(__file__))
                        elif service_id == "voice_cloning":
                            subprocess.Popen([sys.executable, "services/voice_cloning/voice_cloning_service.py"], 
                                          cwd=os.path.dirname(__file__))
                        elif service_id == "orchestrator":
                            subprocess.Popen([sys.executable, "services/service_orchestrator.py"], 
                                          cwd=os.path.dirname(__file__))
                        
                        time.sleep(2)
                        self.service_labels[service_id].config(text="Starting...", foreground="orange")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to start {service_info['name']}: {e}")
        
        threading.Thread(target=start_services, daemon=True).start()
    
    def stop_all_services(self):
        """Stop all services"""
        def stop_services():
            for service_id, service_info in self.services.items():
                try:
                    if service_info["running"]:
                        # Find and kill processes using the ports
                        for conn in psutil.net_connections():
                            if conn.laddr.port == service_info["port"] and conn.status == "LISTEN":
                                try:
                                    process = psutil.Process(conn.pid)
                                    process.terminate()
                                    process.wait(timeout=5)
                                except:
                                    pass
                        
                        self.service_labels[service_id].config(text="Stopping...", foreground="orange")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to stop {service_info['name']}: {e}")
        
        threading.Thread(target=stop_services, daemon=True).start()
    
    def restart_all_services(self):
        """Restart all services"""
        self.stop_all_services()
        time.sleep(3)
        self.start_all_services()
    
    def open_service(self, service_id):
        """Open a specific service"""
        service_info = self.services[service_id]
        if service_info["running"]:
            webbrowser.open(service_info["url"])
        else:
            messagebox.showwarning("Service Not Running", 
                                 f"{service_info['name']} is not running. Please start it first.")
    
    def open_assistant(self):
        """Open Assistant application"""
        self.open_service("assistant")
    
    def open_voice_cloner(self):
        """Open Voice Cloning application"""
        self.open_service("voice_cloning")
    
    def open_dashboard(self):
        """Open Service Dashboard"""
        self.open_service("orchestrator")
    
    def open_monitor(self):
        """Open System Monitor"""
        try:
            subprocess.Popen(["taskmgr"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open System Monitor: {e}")
    
    def update_system_info(self):
        """Update system information display"""
        try:
            # Get system information
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get Python version
            python_version = sys.version.split()[0]
            
            # Get installation directory
            install_dir = os.path.dirname(__file__)
            
            info = f"""System Information:
CPU: {cpu_count} cores
Memory: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available
Disk: {disk.free / (1024**3):.1f} GB free of {disk.total / (1024**3):.1f} GB total

VoiceStudio Services:
- Assistant Service: Port 5080 (AI Assistant with Voice Cloning)
- Voice Cloning Service: Port 5081 (Advanced Voice Cloning Engine)
- Service Orchestrator: Port 5082 (Service Management Dashboard)

Installation Information:
Installation Directory: {install_dir}
Python Version: {python_version}
VoiceStudio Version: 1.0.0

Quick Start:
1. Click "Start All Services" to launch all VoiceStudio services
2. Use the "Open" buttons to access each service
3. Check the Service Dashboard for detailed monitoring
4. Use Voice Cloning Studio for advanced voice synthesis

Support:
For help and documentation, visit: https://voicestudio.ai
"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"Error loading system information: {e}")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceStudioLauncher()
    app.run()
'''
        
        launcher_path = self.app_dir / "voicestudio_launcher.py"
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_script)
        
        logger.info(f"Created launcher: {launcher_path}")
    
    def create_package_info(self):
        """Create package information file"""
        logger.info("Creating package information...")
        
        package_info = {
            "name": "VoiceStudio Ultimate",
            "version": "1.0.0",
            "description": "Advanced Voice Cloning and AI Assistant System",
            "publisher": "VoiceStudio Team",
            "url": "https://voicestudio.ai",
            "installer": {
                "type": "powershell",
                "main_script": "install.ps1",
                "batch_launcher": "install.bat",
                "uninstaller": "uninstall.ps1"
            },
            "features": [
                "Voice Cloning with XTTS v2",
                "AI Assistant with Speech Synthesis",
                "Audio Transcription with WhisperX",
                "Windows Service Integration",
                "Control Panel Integration",
                "Desktop and Taskbar Shortcuts",
                "Service Management Dashboard",
                "GPU Acceleration Support"
            ],
            "services": [
                {
                    "name": "VoiceStudio Assistant Service",
                    "port": 5080,
                    "description": "AI Assistant with Voice Cloning Capabilities"
                },
                {
                    "name": "VoiceStudio Voice Cloning Service",
                    "port": 5081,
                    "description": "Advanced Voice Cloning Engine"
                },
                {
                    "name": "VoiceStudio Service Orchestrator",
                    "port": 5082,
                    "description": "Service Management and Orchestration"
                }
            ],
            "requirements": {
                "os": "Windows 10/11 (64-bit)",
                "ram": "8GB+ recommended",
                "storage": "10GB+ free space",
                "gpu": "NVIDIA GPU with CUDA support (optional)",
                "python": "3.8+"
            }
        }
        
        info_path = self.package_dir / "package_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Created package info: {info_path}")
    
    def create_installation_guide(self):
        """Create installation guide"""
        logger.info("Creating installation guide...")
        
        guide_content = '''# VoiceStudio Ultimate - Installation Guide

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
'''
        
        guide_path = self.package_dir / "INSTALLATION_GUIDE.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        logger.info(f"Created installation guide: {guide_path}")
    
    def create_zip_package(self):
        """Create ZIP package for distribution"""
        logger.info("Creating ZIP package...")
        
        zip_path = self.project_root / "VoiceStudioUltimate_v1.0.0_Windows.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(self.package_dir)
                    zipf.write(file_path, arc_path)
        
        logger.info(f"Created ZIP package: {zip_path}")
        return zip_path
    
    def build_complete_package(self):
        """Build the complete package"""
        logger.info("Building complete VoiceStudio package...")
        
        # Create all components
        self.create_package_structure()
        self.copy_application_files()
        self.create_launcher_executable()
        self.create_package_info()
        self.create_installation_guide()
        
        # Create ZIP package
        zip_path = self.create_zip_package()
        
        logger.info("✅ Complete VoiceStudio package created!")
        logger.info(f"📁 Package directory: {self.package_dir}")
        logger.info(f"📦 ZIP package: {zip_path}")
        
        return zip_path

def main():
    """Main function"""
    package = VoiceStudioCompletePackage()
    zip_path = package.build_complete_package()
    
    print("\n🎉 VoiceStudio Ultimate Windows Package Created Successfully!")
    print(f"\n📦 Package Location: {zip_path}")
    print("\n📋 Package Contents:")
    print("• Complete VoiceStudio application")
    print("• PowerShell installer with full Windows integration")
    print("• Desktop shortcut and taskbar pinning")
    print("• Control Panel integration")
    print("• Windows service installation")
    print("• Comprehensive documentation")
    print("\n🚀 Installation Instructions:")
    print("1. Extract the ZIP file")
    print("2. Navigate to the installer folder")
    print("3. Double-click 'install.bat'")
    print("4. Follow the installation prompts")
    print("\n✨ Features Included:")
    print("• Voice Cloning with XTTS v2")
    print("• AI Assistant with Speech Synthesis")
    print("• Audio Transcription with WhisperX")
    print("• Windows Service Integration")
    print("• Control Panel Integration")
    print("• Desktop and Taskbar Shortcuts")
    print("• Service Management Dashboard")
    print("• GPU Acceleration Support")

if __name__ == "__main__":
    main()
