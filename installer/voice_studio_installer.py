#!/usr/bin/env python3
"""
VoiceStudio Ultimate Installer
Professional installer for VoiceStudio WinUI application
Version: 1.0.0
"""

import os
import sys
import shutil
import subprocess
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
import winreg
import ctypes
from ctypes import wintypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('installer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceStudioInstaller:
    """Professional installer for VoiceStudio"""
    
    def __init__(self):
        self.install_dir = Path("C:\\Program Files\\VoiceStudio")
        self.data_dir = Path("C:\\ProgramData\\VoiceStudio")
        self.user_dir = Path(os.path.expanduser("~\\VoiceStudio"))
        self.desktop_dir = Path(os.path.expanduser("~\\Desktop"))
        self.start_menu_dir = Path(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\VoiceStudio"))
        
        self.required_dependencies = [
            "Microsoft.WindowsAppSDK",
            "Microsoft.VCRedist.2015+.x64",
            "Microsoft.DotNet.DesktopRuntime.8.0",
            "Python.3.11"
        ]
        
        self.python_packages = [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "numpy>=1.24.0",
            "torch>=2.0.0",
            "transformers>=4.38.0",
            "tokenizers>=0.15.0",
            "psutil>=5.9.0",
            "websockets>=12.0",
            "aiohttp>=3.9.0"
        ]
        
        self.install_log = []
        
    def check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_system_requirements(self) -> Dict[str, bool]:
        """Check system requirements"""
        requirements = {
            "windows_version": False,
            "dotnet_runtime": False,
            "python_installed": False,
            "sufficient_memory": False,
            "sufficient_disk_space": False
        }
        
        try:
            # Check Windows version (Windows 10 19041+ or Windows 11)
            import platform
            version = platform.version()
            major, minor, build = map(int, version.split('.'))
            
            if major >= 10 and build >= 19041:
                requirements["windows_version"] = True
            
            # Check .NET runtime
            try:
                result = subprocess.run(["dotnet", "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    requirements["dotnet_runtime"] = True
            except:
                pass
            
            # Check Python
            try:
                result = subprocess.run([sys.executable, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    requirements["python_installed"] = True
            except:
                pass
            
            # Check memory (4GB+)
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb >= 4:
                requirements["sufficient_memory"] = True
            
            # Check disk space (10GB+)
            disk_usage = shutil.disk_usage(self.install_dir.parent)
            free_gb = disk_usage.free / (1024**3)
            if free_gb >= 10:
                requirements["sufficient_disk_space"] = True
                
        except Exception as e:
            logger.error(f"Error checking requirements: {e}")
        
        return requirements
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        try:
            logger.info("Installing dependencies...")
            
            # Install .NET Desktop Runtime
            self._install_dotnet_runtime()
            
            # Install Python packages
            self._install_python_packages()
            
            # Install Windows App SDK
            self._install_windows_app_sdk()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def _install_dotnet_runtime(self):
        """Install .NET Desktop Runtime"""
        try:
            logger.info("Installing .NET Desktop Runtime...")
            
            # Download and install .NET Desktop Runtime
            dotnet_url = "https://download.microsoft.com/download/8/8/5/885e5c8c-4c4b-4b3b-9b0b-1b5b0b0b0b0b/dotnet-desktop-runtime-8.0.0-win-x64.exe"
            
            # For now, just check if it's already installed
            result = subprocess.run(["dotnet", "--list-runtimes"], 
                                  capture_output=True, text=True, timeout=30)
            if "Microsoft.WindowsDesktop.App 8.0" in result.stdout:
                logger.info(".NET Desktop Runtime 8.0 already installed")
            else:
                logger.warning(".NET Desktop Runtime 8.0 not found - please install manually")
                
        except Exception as e:
            logger.error(f"Error installing .NET runtime: {e}")
    
    def _install_python_packages(self):
        """Install Python packages"""
        try:
            logger.info("Installing Python packages...")
            
            for package in self.python_packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package, "--upgrade"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"Successfully installed {package}")
                else:
                    logger.warning(f"Failed to install {package}: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"Error installing Python packages: {e}")
    
    def _install_windows_app_sdk(self):
        """Install Windows App SDK"""
        try:
            logger.info("Installing Windows App SDK...")
            
            # Check if Windows App SDK is already installed
            sdk_path = Path("C:\\Program Files\\Windows Kits\\10\\bin")
            if sdk_path.exists():
                logger.info("Windows App SDK already installed")
            else:
                logger.warning("Windows App SDK not found - please install manually")
                
        except Exception as e:
            logger.error(f"Error checking Windows App SDK: {e}")
    
    def create_directories(self):
        """Create installation directories"""
        try:
            logger.info("Creating installation directories...")
            
            directories = [
                self.install_dir,
                self.data_dir,
                self.user_dir,
                self.start_menu_dir,
                self.install_dir / "bin",
                self.install_dir / "services",
                self.install_dir / "config",
                self.install_dir / "logs",
                self.data_dir / "workers",
                self.data_dir / "workers" / "ops",
                self.data_dir / "models",
                self.data_dir / "cache",
                self.user_dir / "outputs",
                self.user_dir / "temp"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    def copy_files(self):
        """Copy application files"""
        try:
            logger.info("Copying application files...")
            
            # Copy WinUI application
            winui_source = Path("VoiceStudioWinUI")
            if winui_source.exists():
                winui_dest = self.install_dir / "VoiceStudioWinUI"
                shutil.copytree(winui_source, winui_dest, dirs_exist_ok=True)
                logger.info("Copied WinUI application")
            
            # Copy services
            services_source = Path("services")
            if services_source.exists():
                services_dest = self.install_dir / "services"
                shutil.copytree(services_source, services_dest, dirs_exist_ok=True)
                logger.info("Copied services")
            
            # Copy workers
            workers_source = Path("C:\\ProgramData\\VoiceStudio\\workers")
            if workers_source.exists():
                workers_dest = self.data_dir / "workers"
                shutil.copytree(workers_source, workers_dest, dirs_exist_ok=True)
                logger.info("Copied workers")
            
            # Copy solution files
            solution_files = ["VoiceStudio.sln", "VoiceStudio.Contracts", "UltraClone.EngineService"]
            for solution_file in solution_files:
                if Path(solution_file).exists():
                    dest = self.install_dir / solution_file
                    if Path(solution_file).is_dir():
                        shutil.copytree(solution_file, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(solution_file, dest)
                    logger.info(f"Copied {solution_file}")
            
            # Copy configuration files
            config_source = Path("config")
            if config_source.exists():
                config_dest = self.install_dir / "config"
                shutil.copytree(config_source, config_dest, dirs_exist_ok=True)
                logger.info("Copied configuration files")
                
        except Exception as e:
            logger.error(f"Error copying files: {e}")
            raise
    
    def create_shortcuts(self):
        """Create desktop and start menu shortcuts"""
        try:
            logger.info("Creating shortcuts...")
            
            # Create desktop shortcut
            desktop_shortcut = self.desktop_dir / "VoiceStudio.lnk"
            self._create_shortcut(
                desktop_shortcut,
                "VoiceStudio Ultimate",
                str(self.install_dir / "bin" / "VoiceStudio.exe"),
                str(self.install_dir)
            )
            
            # Create start menu shortcuts
            start_menu_shortcuts = [
                ("VoiceStudio Ultimate", "VoiceStudio.exe"),
                ("VoiceStudio Service Manager", "ServiceManager.exe"),
                ("VoiceStudio Configuration", "ConfigEditor.exe")
            ]
            
            for name, exe_name in start_menu_shortcuts:
                shortcut_path = self.start_menu_dir / f"{name}.lnk"
                self._create_shortcut(
                    shortcut_path,
                    name,
                    str(self.install_dir / "bin" / exe_name),
                    str(self.install_dir)
                )
                
        except Exception as e:
            logger.error(f"Error creating shortcuts: {e}")
    
    def _create_shortcut(self, shortcut_path: Path, name: str, target: str, working_dir: str):
        """Create a Windows shortcut"""
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = working_dir
            shortcut.Description = name
            shortcut.save()
            
            logger.info(f"Created shortcut: {shortcut_path}")
            
        except ImportError:
            # Fallback: create a batch file
            batch_content = f"""@echo off
cd /d "{working_dir}"
"{target}"
"""
            batch_path = shortcut_path.with_suffix('.bat')
            batch_path.write_text(batch_content)
            logger.info(f"Created batch file: {batch_path}")
        except Exception as e:
            logger.error(f"Error creating shortcut {shortcut_path}: {e}")
    
    def create_registry_entries(self):
        """Create Windows registry entries"""
        try:
            logger.info("Creating registry entries...")
            
            # Register file associations
            self._register_file_associations()
            
            # Register application in Programs and Features
            self._register_uninstall_info()
            
        except Exception as e:
            logger.error(f"Error creating registry entries: {e}")
    
    def _register_file_associations(self):
        """Register file associations"""
        try:
            # Register .vsproj files
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".vsproj") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "VoiceStudio.Project")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "VoiceStudio.Project") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "VoiceStudio Project File")
                winreg.SetValue(key, "DefaultIcon", winreg.REG_SZ, 
                              f"{self.install_dir}\\bin\\VoiceStudio.exe,0")
                
        except Exception as e:
            logger.error(f"Error registering file associations: {e}")
    
    def _register_uninstall_info(self):
        """Register uninstall information"""
        try:
            uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\VoiceStudio"
            
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "VoiceStudio Ultimate")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "VoiceStudio Team")
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(self.install_dir))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, 
                                f"{self.install_dir}\\bin\\uninstall.exe")
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, 
                                f"{self.install_dir}\\bin\\VoiceStudio.exe")
                
        except Exception as e:
            logger.error(f"Error registering uninstall info: {e}")
    
    def create_services(self):
        """Create Windows services"""
        try:
            logger.info("Creating Windows services...")
            
            # Create VoiceStudio service
            service_script = self.install_dir / "bin" / "install_service.py"
            service_script.write_text(self._get_service_script())
            
            # Install service
            result = subprocess.run([
                sys.executable, str(service_script), "install"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("VoiceStudio service installed successfully")
            else:
                logger.warning(f"Service installation warning: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error creating services: {e}")
    
    def _get_service_script(self) -> str:
        """Get service installation script"""
        return '''
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
from pathlib import Path

class VoiceStudioService(win32serviceutil.ServiceFramework):
    _svc_name_ = "VoiceStudio"
    _svc_display_name_ = "VoiceStudio Ultimate Service"
    _svc_description_ = "VoiceStudio Ultimate Voice Cloning Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def main(self):
        # Start VoiceStudio services
        import subprocess
        import time
        
        install_dir = Path("C:\\\\Program Files\\\\VoiceStudio")
        service_script = install_dir / "services" / "voice_cloning" / "ultimate_web_server.py"
        
        if service_script.exists():
            process = subprocess.Popen([
                sys.executable, str(service_script), "--host", "127.0.0.1", "--port", "8083"
            ])
            
            while self.is_running:
                time.sleep(1)
            
            process.terminate()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VoiceStudioService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(VoiceStudioService)
'''
    
    def create_configuration(self):
        """Create default configuration"""
        try:
            logger.info("Creating default configuration...")
            
            # Create main configuration
            config = {
                "application": {
                    "name": "VoiceStudio Ultimate",
                    "version": "1.0.0",
                    "install_directory": str(self.install_dir),
                    "data_directory": str(self.data_dir),
                    "user_directory": str(self.user_dir)
                },
                "services": {
                    "web_server": {
                        "host": "127.0.0.1",
                        "port": 8083,
                        "enabled": True
                    },
                    "realtime_service": {
                        "enabled": True,
                        "buffer_size": 100,
                        "latency_mode": "low"
                    }
                },
                "ai_models": {
                    "gpt_sovits_2": {
                        "enabled": True,
                        "path": str(self.data_dir / "models" / "gpt_sovits_2")
                    },
                    "coqui_xtts_3": {
                        "enabled": True,
                        "path": str(self.data_dir / "models" / "coqui_xtts_3")
                    }
                },
                "workers": {
                    "max_workers": 32,
                    "worker_directory": str(self.data_dir / "workers"),
                    "enabled": True
                }
            }
            
            config_file = self.install_dir / "config" / "voice_studio_config.json"
            config_file.write_text(json.dumps(config, indent=2))
            
            logger.info("Created default configuration")
            
        except Exception as e:
            logger.error(f"Error creating configuration: {e}")
    
    def build_application(self):
        """Build the WinUI application"""
        try:
            logger.info("Building WinUI application...")
            
            # Build the solution
            solution_path = self.install_dir / "VoiceStudio.sln"
            if solution_path.exists():
                result = subprocess.run([
                    "dotnet", "build", str(solution_path), "--configuration", "Release"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("Solution built successfully")
                else:
                    logger.error(f"Build failed: {result.stderr}")
                    return False
            
            # Publish WinUI application
            winui_project = self.install_dir / "VoiceStudioWinUI" / "VoiceStudioWinUI.csproj"
            if winui_project.exists():
                result = subprocess.run([
                    "dotnet", "publish", str(winui_project), 
                    "--configuration", "Release",
                    "--runtime", "win-x64",
                    "--self-contained", "true",
                    "--output", str(self.install_dir / "bin")
                ], capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    logger.info("WinUI application published successfully")
                else:
                    logger.error(f"Publish failed: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error building application: {e}")
            return False
    
    def run_post_install_tests(self):
        """Run post-installation tests"""
        try:
            logger.info("Running post-installation tests...")
            
            # Test web server
            self._test_web_server()
            
            # Test WinUI application
            self._test_winui_application()
            
            # Test services
            self._test_services()
            
            logger.info("Post-installation tests completed")
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
    
    def _test_web_server(self):
        """Test web server functionality"""
        try:
            import requests
            
            # Start web server in background
            service_script = self.install_dir / "services" / "voice_cloning" / "ultimate_web_server.py"
            if service_script.exists():
                process = subprocess.Popen([
                    sys.executable, str(service_script), "--host", "127.0.0.1", "--port", "8083"
                ])
                
                time.sleep(5)  # Wait for server to start
                
                # Test API endpoint
                response = requests.get("http://127.0.0.1:8083/api/status", timeout=10)
                if response.status_code == 200:
                    logger.info("Web server test passed")
                else:
                    logger.warning(f"Web server test failed: {response.status_code}")
                
                process.terminate()
                
        except Exception as e:
            logger.error(f"Web server test error: {e}")
    
    def _test_winui_application(self):
        """Test WinUI application"""
        try:
            exe_path = self.install_dir / "bin" / "VoiceStudioWinUI.exe"
            if exe_path.exists():
                logger.info("WinUI application executable found")
            else:
                logger.warning("WinUI application executable not found")
                
        except Exception as e:
            logger.error(f"WinUI test error: {e}")
    
    def _test_services(self):
        """Test Windows services"""
        try:
            result = subprocess.run([
                "sc", "query", "VoiceStudio"
            ], capture_output=True, text=True, timeout=30)
            
            if "SERVICE_NAME: VoiceStudio" in result.stdout:
                logger.info("VoiceStudio service found")
            else:
                logger.warning("VoiceStudio service not found")
                
        except Exception as e:
            logger.error(f"Service test error: {e}")
    
    def create_uninstaller(self):
        """Create uninstaller"""
        try:
            logger.info("Creating uninstaller...")
            
            uninstaller_script = self.install_dir / "bin" / "uninstall.py"
            uninstaller_script.write_text(self._get_uninstaller_script())
            
            # Create uninstaller executable
            uninstaller_exe = self.install_dir / "bin" / "uninstall.exe"
            # For now, just copy the script
            shutil.copy2(uninstaller_script, uninstaller_exe.with_suffix('.py'))
            
            logger.info("Uninstaller created")
            
        except Exception as e:
            logger.error(f"Error creating uninstaller: {e}")
    
    def _get_uninstaller_script(self) -> str:
        """Get uninstaller script"""
        return f'''
import os
import shutil
import winreg
import subprocess
import sys
from pathlib import Path

def uninstall_voicestudio():
    """Uninstall VoiceStudio"""
    print("Uninstalling VoiceStudio Ultimate...")
    
    install_dir = Path("{self.install_dir}")
    data_dir = Path("{self.data_dir}")
    user_dir = Path("{self.user_dir}")
    
    try:
        # Stop services
        subprocess.run(["sc", "stop", "VoiceStudio"], capture_output=True)
        subprocess.run(["sc", "delete", "VoiceStudio"], capture_output=True)
        
        # Remove registry entries
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, ".vsproj")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, "VoiceStudio.Project")
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VoiceStudio")
        except:
            pass
        
        # Remove directories
        if install_dir.exists():
            shutil.rmtree(install_dir)
        if data_dir.exists():
            shutil.rmtree(data_dir)
        if user_dir.exists():
            shutil.rmtree(user_dir)
        
        print("VoiceStudio Ultimate uninstalled successfully")
        
    except Exception as e:
        print(f"Error during uninstall: {{e}}")

if __name__ == "__main__":
    uninstall_voicestudio()
'''
    
    def install(self):
        """Main installation process"""
        try:
            logger.info("Starting VoiceStudio Ultimate installation...")
            
            # Check admin privileges
            if not self.check_admin_privileges():
                logger.error("Administrator privileges required")
                return False
            
            # Check system requirements
            requirements = self.check_system_requirements()
            logger.info(f"System requirements check: {requirements}")
            
            if not all(requirements.values()):
                logger.error("System requirements not met")
                return False
            
            # Installation steps
            steps = [
                ("Installing dependencies", self.install_dependencies),
                ("Creating directories", self.create_directories),
                ("Copying files", self.copy_files),
                ("Building application", self.build_application),
                ("Creating shortcuts", self.create_shortcuts),
                ("Creating registry entries", self.create_registry_entries),
                ("Creating services", self.create_services),
                ("Creating configuration", self.create_configuration),
                ("Creating uninstaller", self.create_uninstaller),
                ("Running tests", self.run_post_install_tests)
            ]
            
            for step_name, step_func in steps:
                logger.info(f"Step: {step_name}")
                if not step_func():
                    logger.error(f"Step failed: {step_name}")
                    return False
                logger.info(f"Step completed: {step_name}")
            
            logger.info("VoiceStudio Ultimate installation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False

def main():
    """Main function"""
    installer = VoiceStudioInstaller()
    
    print("VoiceStudio Ultimate Installer v1.0.0")
    print("=" * 50)
    
    if installer.install():
        print("\nInstallation completed successfully!")
        print(f"VoiceStudio installed to: {installer.install_dir}")
        print("You can now start VoiceStudio from the Start Menu or Desktop shortcut.")
    else:
        print("\nInstallation failed. Check installer.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
