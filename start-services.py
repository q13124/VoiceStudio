#!/usr/bin/env python3
"""
VoiceStudio Service Manager
Starts and manages all VoiceStudio microservices.
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path

class ServiceManager:
    """Manages VoiceStudio services"""
    
    def __init__(self):
        self.services = {}
        self.base_path = Path(__file__).parent.parent
        
    def start_service(self, name, script_path, port):
        """Start a service"""
        try:
            full_path = self.base_path / script_path
            if not full_path.exists():
                print(f"Error: Service script not found: {full_path}")
                return False
            
            print(f"Starting {name} on port {port}...")
            process = subprocess.Popen([
                sys.executable, str(full_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.services[name] = {
                'process': process,
                'port': port,
                'script': script_path
            }
            
            print(f"✓ {name} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"Error starting {name}: {e}")
            return False
    
    def stop_service(self, name):
        """Stop a service"""
        if name in self.services:
            process = self.services[name]['process']
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✓ {name} stopped")
                del self.services[name]
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"✓ {name} force stopped")
                del self.services[name]
    
    def stop_all(self):
        """Stop all services"""
        print("\nStopping all services...")
        for name in list(self.services.keys()):
            self.stop_service(name)
    
    def start_all(self):
        """Start all services"""
        print("Starting VoiceStudio Services...")
        print("=" * 50)
        
        services_to_start = [
            ("Assistant", "services/assistant/service.py", 5080),
            ("Orchestrator", "services/orchestrator/service.py", 5090),
            ("Autofix", "services/autofix/service.py", 5081)
        ]
        
        for name, script, port in services_to_start:
            if not self.start_service(name, script, port):
                print(f"Failed to start {name}")
                return False
            time.sleep(1)  # Give each service time to start
        
        print("=" * 50)
        print("All services started successfully!")
        print("\nService Endpoints:")
        print("Assistant Service:")
        print("  - Health: http://127.0.0.1:5080/health")
        print("  - Autofix: http://127.0.0.1:5080/autofix/status")
        print("\nOrchestrator Service:")
        print("  - Health: http://127.0.0.1:5090/health")
        print("  - Settings: http://127.0.0.1:5090/settings")
        print("  - Weights: http://127.0.0.1:5090/weights")
        print("\nAutofix Service:")
        print("  - Health: http://127.0.0.1:5081/health")
        print("  - Status: http://127.0.0.1:5081/status")
        print("\nPress Ctrl+C to stop all services")
        
        return True
    
    def run(self):
        """Run the service manager"""
        def signal_handler(sig, frame):
            print("\nReceived interrupt signal...")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if not self.start_all():
            print("Failed to start services")
            sys.exit(1)
        
        try:
            # Keep the manager running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()

if __name__ == "__main__":
    manager = ServiceManager()
    manager.run()
