#!/usr/bin/env python3
"""
VoiceStudio Enhanced Assistant Service Startup Script
Optimized startup with voice cloning capabilities and performance monitoring.
"""

import os
import sys
import time
import logging
import subprocess
import signal
import psutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AssistantServiceManager:
    """Manager for the Enhanced Assistant Service"""
    
    def __init__(self):
        self.service_process = None
        self.service_dir = Path(__file__).parent
        self.pid_file = self.service_dir / "assistant_service.pid"
        self.log_file = self.service_dir / "assistant_service.log"
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            "aiohttp", "asyncio", "psutil", "numpy", "soundfile", 
            "torch", "TTS", "librosa", "whisperx"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"✗ {package} - MISSING")
        
        if missing_packages:
            logger.error(f"Missing packages: {', '.join(missing_packages)}")
            logger.error("Please install missing dependencies:")
            logger.error(f"pip install {' '.join(missing_packages)}")
            return False
        
        logger.info("All dependencies available")
        return True
    
    def check_system_resources(self) -> bool:
        """Check system resources"""
        logger.info("Checking system resources...")
        
        # Check memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        if memory_gb < 8:
            logger.warning(f"Low memory: {memory_gb:.1f}GB (recommended: 8GB+)")
        else:
            logger.info(f"Memory: {memory_gb:.1f}GB")
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        logger.info(f"CPU cores: {cpu_count}")
        
        # Check disk space
        disk = psutil.disk_usage('/')
        disk_gb = disk.free / (1024**3)
        
        if disk_gb < 10:
            logger.warning(f"Low disk space: {disk_gb:.1f}GB (recommended: 10GB+)")
        else:
            logger.info(f"Disk space: {disk_gb:.1f}GB")
        
        return True
    
    def check_gpu_availability(self) -> bool:
        """Check GPU availability for voice processing"""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            
            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)")
                return True
            else:
                logger.warning("CUDA not available - voice processing will use CPU")
                return False
                
        except ImportError:
            logger.warning("PyTorch not available - cannot check GPU")
            return False
    
    def optimize_system(self):
        """Apply system optimizations"""
        logger.info("Applying system optimizations...")
        
        try:
            # Set process priority
            if hasattr(os, 'nice'):
                os.nice(-5)  # Higher priority
                logger.info("Set higher process priority")
            
            # Optimize Python garbage collection
            import gc
            gc.set_threshold(700, 10, 10)
            logger.info("Optimized garbage collection")
            
            # Set environment variables for better performance
            os.environ['OMP_NUM_THREADS'] = str(psutil.cpu_count())
            os.environ['MKL_NUM_THREADS'] = str(psutil.cpu_count())
            logger.info("Set thread optimization")
            
        except Exception as e:
            logger.warning(f"Could not apply all optimizations: {e}")
    
    def start_service(self) -> bool:
        """Start the Enhanced Assistant Service"""
        logger.info("Starting Enhanced Assistant Service...")
        
        try:
            # Check if service is already running
            if self.is_service_running():
                logger.warning("Service is already running")
                return True
            
            # Start the service
            self.service_process = subprocess.Popen(
                [sys.executable, "enhanced_service.py"],
                cwd=self.service_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.service_process.pid))
            
            # Wait for service to initialize
            logger.info("Waiting for service to initialize...")
            time.sleep(3)
            
            # Check if service started successfully
            if self.service_process.poll() is None:
                logger.info(f"Service started successfully (PID: {self.service_process.pid})")
                logger.info("Service endpoints:")
                logger.info("  Health: http://127.0.0.1:5080/health")
                logger.info("  Voice Cloning Status: http://127.0.0.1:5080/voice-cloning/status")
                logger.info("  Speech Synthesis: http://127.0.0.1:5080/voice-cloning/synthesize")
                logger.info("  Voice Cloning: http://127.0.0.1:5080/voice-cloning/clone")
                logger.info("  Audio Transcription: http://127.0.0.1:5080/voice-cloning/transcribe")
                logger.info("  Available Models: http://127.0.0.1:5080/voice-cloning/models")
                return True
            else:
                logger.error("Service failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    def is_service_running(self) -> bool:
        """Check if service is running"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process exists
                if psutil.pid_exists(pid):
                    return True
                else:
                    # Clean up stale PID file
                    self.pid_file.unlink()
                    
            except (ValueError, FileNotFoundError):
                pass
        
        return False
    
    def stop_service(self):
        """Stop the service"""
        logger.info("Stopping Enhanced Assistant Service...")
        
        if self.service_process:
            try:
                self.service_process.terminate()
                self.service_process.wait(timeout=10)
                logger.info("Service stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Service did not stop gracefully, forcing...")
                self.service_process.kill()
                self.service_process.wait()
            except Exception as e:
                logger.error(f"Error stopping service: {e}")
        
        # Clean up PID file
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def restart_service(self) -> bool:
        """Restart the service"""
        logger.info("Restarting Enhanced Assistant Service...")
        self.stop_service()
        time.sleep(2)
        return self.start_service()
    
    def get_service_status(self) -> dict:
        """Get service status"""
        status = {
            "running": self.is_service_running(),
            "pid_file": str(self.pid_file),
            "log_file": str(self.log_file),
            "service_dir": str(self.service_dir)
        }
        
        if status["running"] and self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                status["pid"] = pid
                
                # Get process info
                process = psutil.Process(pid)
                status["memory_usage"] = process.memory_info().rss / (1024**2)  # MB
                status["cpu_percent"] = process.cpu_percent()
                
            except Exception as e:
                status["error"] = str(e)
        
        return status
    
    def monitor_service(self):
        """Monitor service and restart if needed"""
        logger.info("Starting service monitoring...")
        
        try:
            while True:
                if not self.is_service_running():
                    logger.warning("Service is not running, restarting...")
                    if not self.start_service():
                        logger.error("Failed to restart service")
                        break
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Enhanced Assistant Service Manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "monitor", "check"],
                      help="Action to perform")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    parser.add_argument("--optimize", action="store_true", help="Apply system optimizations")
    
    args = parser.parse_args()
    
    manager = AssistantServiceManager()
    
    if args.action == "check":
        logger.info("Running system checks...")
        deps_ok = manager.check_dependencies()
        resources_ok = manager.check_system_resources()
        gpu_ok = manager.check_gpu_availability()
        
        if deps_ok and resources_ok:
            logger.info("System checks passed")
        else:
            logger.error("System checks failed")
            sys.exit(1)
    
    elif args.action == "start":
        if args.check_deps:
            if not manager.check_dependencies():
                sys.exit(1)
        
        if args.optimize:
            manager.optimize_system()
        
        if manager.start_service():
            logger.info("Service started successfully")
        else:
            logger.error("Failed to start service")
            sys.exit(1)
    
    elif args.action == "stop":
        manager.stop_service()
    
    elif args.action == "restart":
        if manager.restart_service():
            logger.info("Service restarted successfully")
        else:
            logger.error("Failed to restart service")
            sys.exit(1)
    
    elif args.action == "status":
        status = manager.get_service_status()
        logger.info(f"Service Status: {json.dumps(status, indent=2)}")
    
    elif args.action == "monitor":
        manager.monitor_service()

if __name__ == "__main__":
    main()
