#!/usr/bin/env python3
"""
VoiceStudio Enhanced Service Manager
Starts and manages all VoiceStudio microservices with full integration.
"""

import subprocess
import time
import signal
import sys
import os
import threading
from pathlib import Path

# Import our custom modules
from services.service_discovery import start_service_discovery, register_service
from services.security import security_manager
from services.database import db_manager

class EnhancedServiceManager:
    """Enhanced service manager with full integration"""
    
    def __init__(self):
        self.services = {}
        self.base_path = Path(__file__).parent
        
        # Start service discovery
        start_service_discovery()
        
        # Initialize database
        self._init_database()
        
        # Create default users
        self._create_default_users()
    
    def _init_database(self):
        """Initialize database with default data"""
        print("Initializing database...")
        
        # Set default configurations
        db_manager.set_configuration("app_version", "1.0.0", "system")
        db_manager.set_configuration("environment", "development", "system")
        db_manager.set_configuration("log_level", "INFO", "system")
        
        print("✓ Database initialized")
    
    def _create_default_users(self):
        """Create default users for testing"""
        print("Creating default users...")
        
        # Create test user
        test_user = security_manager.create_user("testuser", "test@voicestudio.local", ["user"])
        print(f"✓ Created test user: {test_user.username}")
        print(f"  API Key: {test_user.api_key}")
        
        print("✓ Default users created")
    
    def start_service(self, name, script_path, port):
        """Start a service with enhanced monitoring"""
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
            
            # Register with service discovery
            register_service(name, port=port)
            
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
        """Start all enhanced services"""
        print("Starting Enhanced VoiceStudio Services...")
        print("=" * 60)
        
        services_to_start = [
            ("Assistant", "services/assistant/enhanced_service.py", 5080),
            ("Orchestrator", "services/orchestrator/service.py", 5090),
            ("Autofix", "services/autofix/service.py", 5081)
        ]
        
        for name, script, port in services_to_start:
            if not self.start_service(name, script, port):
                print(f"Failed to start {name}")
                return False
            time.sleep(2)  # Give each service time to start
        
        print("=" * 60)
        print("All enhanced services started successfully!")
        print("\n🔧 Enhanced Features:")
        print("  ✓ Service Discovery & Communication")
        print("  ✓ Authentication & Security")
        print("  ✓ Database Logging & Metrics")
        print("  ✓ Inter-service API calls")
        print("  ✓ Comprehensive monitoring")
        
        print("\n📡 Service Endpoints:")
        print("Assistant Service (Enhanced):")
        print("  - Health: http://127.0.0.1:5080/health")
        print("  - Autofix Status: http://127.0.0.1:5080/autofix/status")
        print("  - Service Discovery: http://127.0.0.1:5080/discovery")
        print("  - Metrics: http://127.0.0.1:5080/metrics")
        print("  - Authentication: http://127.0.0.1:5080/auth/login")
        
        print("\nOrchestrator Service:")
        print("  - Health: http://127.0.0.1:5090/health")
        print("  - Settings: http://127.0.0.1:5090/settings")
        print("  - Weights: http://127.0.0.1:5090/weights")
        
        print("\nAutofix Service:")
        print("  - Health: http://127.0.0.1:5081/health")
        print("  - Status: http://127.0.0.1:5081/status")
        print("  - Analyze: http://127.0.0.1:5081/analyze")
        
        print("\n🔐 Authentication:")
        print("  - Default Admin API Key: Check logs above")
        print("  - Test User API Key: Check logs above")
        print("  - Use X-API-Key header for authentication")
        
        print("\n📊 Monitoring:")
        print("  - Database: voicestudio.db")
        print("  - Logs: services/logs/")
        print("  - Metrics: Available via /metrics endpoints")
        
        print("\nPress Ctrl+C to stop all services")
        
        return True
    
    def run_health_monitor(self):
        """Run health monitoring in background"""
        def monitor():
            while True:
                try:
                    import requests
                    
                    # Check each service
                    for name, service_info in self.services.items():
                        port = service_info['port']
                        try:
                            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
                            if response.status_code != 200:
                                print(f"⚠️  {name} service health check failed")
                        except:
                            print(f"⚠️  {name} service not responding")
                    
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"Health monitor error: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        print("✓ Health monitoring started")
    
    def run(self):
        """Run the enhanced service manager"""
        def signal_handler(sig, frame):
            print("\nReceived interrupt signal...")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if not self.start_all():
            print("Failed to start services")
            sys.exit(1)
        
        # Start health monitoring
        self.run_health_monitor()
        
        try:
            # Keep the manager running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()

if __name__ == "__main__":
    manager = EnhancedServiceManager()
    manager.run()
