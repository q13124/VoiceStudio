"""
VoiceStudio Voice Cloning - Windows Service Wrapper
Professional Windows service implementation for voice cloning services.
"""

import os
import sys
import time
import logging
import threading
import subprocess
from pathlib import Path
import win32serviceutil
import win32service
import win32event
import servicemanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Program Files/VoiceStudio/logs/voice_studio_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceStudioService(win32serviceutil.ServiceFramework):
    """Windows Service for VoiceStudio Voice Cloning"""
    
    _svc_name_ = "VoiceStudioVoiceCloning"
    _svc_display_name_ = "VoiceStudio Voice Cloning Service"
    _svc_description_ = "Professional voice cloning service for VoiceStudio"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.processes = {}
        self.running = False
        
        # Service paths
        self.base_path = Path("C:/Program Files/VoiceStudio")
        self.service_path = self.base_path / "services" / "voice_cloning"
        
    def SvcStop(self):
        """Stop the service"""
        logger.info("Stopping VoiceStudio Voice Cloning Service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        
        # Stop all subprocesses
        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait()
        
        logger.info("VoiceStudio Voice Cloning Service stopped")
    
    def SvcDoRun(self):
        """Run the service"""
        logger.info("Starting VoiceStudio Voice Cloning Service...")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.running = True
        self.start_services()
        
        # Wait for stop signal
        while self.running:
            rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break
            
            # Check if processes are still running
            self.monitor_processes()
    
    def start_services(self):
        """Start voice cloning services"""
        logger.info("Starting voice cloning services...")
        
        try:
            # Start Enhanced Voice Cloning Service
            voice_cloning_cmd = [
                sys.executable,
                str(self.service_path / "enhanced_service.py")
            ]
            
            self.processes['voice_cloning'] = subprocess.Popen(
                voice_cloning_cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info("Voice Cloning Service started on port 5083")
            
            # Wait a moment for the first service to start
            time.sleep(3)
            
            # Start Web Interface Service
            web_server_cmd = [
                sys.executable,
                str(self.service_path / "web_server.py")
            ]
            
            self.processes['web_interface'] = subprocess.Popen(
                web_server_cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info("Web Interface Service started on port 8080")
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            servicemanager.LogErrorMsg(f"Failed to start services: {e}")
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed"""
        for name, process in self.processes.items():
            if process and process.poll() is not None:
                logger.warning(f"{name} process stopped, restarting...")
                self.restart_process(name)
    
    def restart_process(self, service_name):
        """Restart a specific service process"""
        try:
            if service_name == 'voice_cloning':
                cmd = [sys.executable, str(self.service_path / "enhanced_service.py")]
            elif service_name == 'web_interface':
                cmd = [sys.executable, str(self.service_path / "web_server.py")]
            else:
                return
            
            self.processes[service_name] = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"{service_name} restarted successfully")
            
        except Exception as e:
            logger.error(f"Failed to restart {service_name}: {e}")

class VoiceStudioServiceManager:
    """Manager for VoiceStudio Windows Service"""
    
    def __init__(self):
        self.service_name = "VoiceStudioVoiceCloning"
    
    def install_service(self):
        """Install the Windows service"""
        try:
            win32serviceutil.InstallService(
                VoiceStudioService,
                self.service_name,
                "VoiceStudio Voice Cloning Service",
                description="Professional voice cloning service for VoiceStudio",
                startType=win32service.SERVICE_AUTO_START
            )
            print(f"✅ Service '{self.service_name}' installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install service: {e}")
            return False
    
    def uninstall_service(self):
        """Uninstall the Windows service"""
        try:
            win32serviceutil.RemoveService(self.service_name)
            print(f"✅ Service '{self.service_name}' uninstalled successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to uninstall service: {e}")
            return False
    
    def start_service(self):
        """Start the Windows service"""
        try:
            win32serviceutil.StartService(self.service_name)
            print(f"✅ Service '{self.service_name}' started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            return False
    
    def stop_service(self):
        """Stop the Windows service"""
        try:
            win32serviceutil.StopService(self.service_name)
            print(f"✅ Service '{self.service_name}' stopped successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to stop service: {e}")
            return False
    
    def get_service_status(self):
        """Get Windows service status"""
        try:
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            status_map = {
                win32service.SERVICE_STOPPED: "STOPPED",
                win32service.SERVICE_START_PENDING: "STARTING",
                win32service.SERVICE_STOP_PENDING: "STOPPING",
                win32service.SERVICE_RUNNING: "RUNNING",
                win32service.SERVICE_CONTINUE_PENDING: "CONTINUING",
                win32service.SERVICE_PAUSE_PENDING: "PAUSING",
                win32service.SERVICE_PAUSED: "PAUSED"
            }
            return status_map.get(status[1], "UNKNOWN")
        except Exception as e:
            print(f"❌ Failed to get service status: {e}")
            return "ERROR"

def main():
    """Main function for service management"""
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VoiceStudioService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Service management commands
        manager = VoiceStudioServiceManager()
        
        command = sys.argv[1].lower()
        
        if command == "install":
            manager.install_service()
        elif command == "uninstall":
            manager.uninstall_service()
        elif command == "start":
            manager.start_service()
        elif command == "stop":
            manager.stop_service()
        elif command == "status":
            status = manager.get_service_status()
            print(f"Service Status: {status}")
        else:
            print("Usage: python voice_studio_service.py [install|uninstall|start|stop|status]")

if __name__ == "__main__":
    main()
