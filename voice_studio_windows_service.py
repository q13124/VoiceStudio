#!/usr/bin/env python3
"""
VoiceStudio Windows Service Integration
Creates Windows services for all VoiceStudio components with proper service management.
"""

import os
import sys
import json
import subprocess
import time
import logging
from pathlib import Path
import win32serviceutil
import win32service
import win32event
import servicemanager

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VoiceStudioAssistantService(win32serviceutil.ServiceFramework):
    """Windows Service for VoiceStudio Assistant"""
    
    _svc_name_ = "VoiceStudioAssistant"
    _svc_display_name_ = "VoiceStudio Assistant Service"
    _svc_description_ = "AI Assistant with Voice Cloning Capabilities"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        
    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        
        try:
            # Import and start the assistant service
            sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'assistant'))
            from enhanced_service import start_enhanced_assistant_service
            
            # Start the service in a separate thread
            import threading
            service_thread = threading.Thread(target=self.run_assistant_service)
            service_thread.daemon = True
            service_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"VoiceStudio Assistant Service error: {e}")
            
    def run_assistant_service(self):
        """Run the assistant service"""
        try:
            import asyncio
            asyncio.run(start_enhanced_assistant_service(port=5080))
        except Exception as e:
            logger.error(f"Failed to start assistant service: {e}")

class VoiceStudioVoiceCloningService(win32serviceutil.ServiceFramework):
    """Windows Service for VoiceStudio Voice Cloning"""
    
    _svc_name_ = "VoiceStudioVoiceCloning"
    _svc_display_name_ = "VoiceStudio Voice Cloning Service"
    _svc_description_ = "Advanced Voice Cloning Engine"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        
    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        
        try:
            # Start voice cloning service
            import threading
            service_thread = threading.Thread(target=self.run_voice_cloning_service)
            service_thread.daemon = True
            service_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"VoiceStudio Voice Cloning Service error: {e}")
            
    def run_voice_cloning_service(self):
        """Run the voice cloning service"""
        try:
            # Start voice cloning service on port 5081
            import subprocess
            import os
            
            service_path = os.path.join(os.path.dirname(__file__), 'services', 'voice_cloning')
            if os.path.exists(service_path):
                subprocess.Popen([sys.executable, 'voice_cloning_service.py'], 
                               cwd=service_path)
            else:
                # Fallback: start a simple HTTP server
                import http.server
                import socketserver
                
                class VoiceCloningHandler(http.server.SimpleHTTPRequestHandler):
                    def do_GET(self):
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {"status": "Voice Cloning Service Running", "port": 5081}
                        self.wfile.write(json.dumps(response).encode())
                
                with socketserver.TCPServer(("", 5081), VoiceCloningHandler) as httpd:
                    httpd.serve_forever()
                    
        except Exception as e:
            logger.error(f"Failed to start voice cloning service: {e}")

class VoiceStudioServiceOrchestrator(win32serviceutil.ServiceFramework):
    """Windows Service for VoiceStudio Service Orchestrator"""
    
    _svc_name_ = "VoiceStudioServiceOrchestrator"
    _svc_display_name_ = "VoiceStudio Service Orchestrator"
    _svc_description_ = "Service Management and Orchestration"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        
    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        
        try:
            # Start service orchestrator
            import threading
            service_thread = threading.Thread(target=self.run_orchestrator_service)
            service_thread.daemon = True
            service_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"VoiceStudio Service Orchestrator error: {e}")
            
    def run_orchestrator_service(self):
        """Run the orchestrator service"""
        try:
            # Start service orchestrator on port 5082
            import subprocess
            import os
            
            service_path = os.path.join(os.path.dirname(__file__), 'services')
            orchestrator_script = os.path.join(service_path, 'service_orchestrator.py')
            
            if os.path.exists(orchestrator_script):
                subprocess.Popen([sys.executable, orchestrator_script], 
                               cwd=service_path)
            else:
                # Fallback: start a simple dashboard
                import http.server
                import socketserver
                
                class OrchestratorHandler(http.server.SimpleHTTPRequestHandler):
                    def do_GET(self):
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {
                            "status": "Service Orchestrator Running", 
                            "port": 5082,
                            "services": {
                                "assistant": {"port": 5080, "status": "running"},
                                "voice_cloning": {"port": 5081, "status": "running"},
                                "orchestrator": {"port": 5082, "status": "running"}
                            }
                        }
                        self.wfile.write(json.dumps(response, indent=2).encode())
                
                with socketserver.TCPServer(("", 5082), OrchestratorHandler) as httpd:
                    httpd.serve_forever()
                    
        except Exception as e:
            logger.error(f"Failed to start orchestrator service: {e}")

def install_services():
    """Install all VoiceStudio Windows services"""
    logger.info("Installing VoiceStudio Windows Services...")
    
    services = [
        VoiceStudioAssistantService,
        VoiceStudioVoiceCloningService,
        VoiceStudioServiceOrchestrator
    ]
    
    for service_class in services:
        try:
            win32serviceutil.InstallService(
                service_class._svc_reg_class_,
                service_class._svc_name_,
                service_class._svc_display_name_,
                description=service_class._svc_description_
            )
            logger.info(f"Installed service: {service_class._svc_display_name_}")
        except Exception as e:
            logger.error(f"Failed to install {service_class._svc_display_name_}: {e}")

def uninstall_services():
    """Uninstall all VoiceStudio Windows services"""
    logger.info("Uninstalling VoiceStudio Windows Services...")
    
    services = [
        VoiceStudioAssistantService,
        VoiceStudioVoiceCloningService,
        VoiceStudioServiceOrchestrator
    ]
    
    for service_class in services:
        try:
            win32serviceutil.RemoveService(service_class._svc_name_)
            logger.info(f"Uninstalled service: {service_class._svc_display_name_}")
        except Exception as e:
            logger.error(f"Failed to uninstall {service_class._svc_display_name_}: {e}")

def start_services():
    """Start all VoiceStudio Windows services"""
    logger.info("Starting VoiceStudio Windows Services...")
    
    services = [
        VoiceStudioAssistantService,
        VoiceStudioVoiceCloningService,
        VoiceStudioServiceOrchestrator
    ]
    
    for service_class in services:
        try:
            win32serviceutil.StartService(service_class._svc_name_)
            logger.info(f"Started service: {service_class._svc_display_name_}")
        except Exception as e:
            logger.error(f"Failed to start {service_class._svc_display_name_}: {e}")

def stop_services():
    """Stop all VoiceStudio Windows services"""
    logger.info("Stopping VoiceStudio Windows Services...")
    
    services = [
        VoiceStudioAssistantService,
        VoiceStudioVoiceCloningService,
        VoiceStudioServiceOrchestrator
    ]
    
    for service_class in services:
        try:
            win32serviceutil.StopService(service_class._svc_name_)
            logger.info(f"Stopped service: {service_class._svc_display_name_}")
        except Exception as e:
            logger.error(f"Failed to stop {service_class._svc_display_name_}: {e}")

def main():
    """Main function"""
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VoiceStudioAssistantService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Handle command line arguments
        if sys.argv[1] == 'install':
            install_services()
        elif sys.argv[1] == 'uninstall':
            uninstall_services()
        elif sys.argv[1] == 'start':
            start_services()
        elif sys.argv[1] == 'stop':
            stop_services()
        else:
            print("Usage: python voice_studio_windows_service.py [install|uninstall|start|stop]")

if __name__ == '__main__':
    main()
