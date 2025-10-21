#!/usr/bin/env python3
"""
VoiceStudio Voice Cloning Services Startup Script
Starts voice cloning services with performance monitoring and health checks.
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import threading
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoiceCloningServiceManager:
    """Manages voice cloning services with performance monitoring"""
    
    def __init__(self):
        self.services = {}
        self.processes = {}
        self.running = False
        self.start_time = datetime.now()
        
        # Voice cloning service configurations
        self.service_configs = {
            "voice_cloning": {
                "module": "services.voice_cloning.enhanced_service",
                "port": 5083,
                "name": "Enhanced Voice Cloning Service",
                "health_endpoint": "/health",
                "required": True,
                "startup_delay": 0
            },
            "web_interface": {
                "module": "services.voice_cloning.web_server",
                "port": 8080,
                "name": "Voice Cloning Web Interface",
                "health_endpoint": "/health",
                "required": False,
                "startup_delay": 2  # Start after voice cloning service
            }
        }
        
        # Performance monitoring
        self.performance_metrics = {
            "startup_time": 0,
            "services_started": 0,
            "services_failed": 0,
            "total_uptime": 0,
            "voice_clones_processed": 0,
            "active_sessions": 0
        }
    
    async def start_all_services(self):
        """Start all voice cloning services concurrently"""
        logger.info("Starting VoiceStudio Voice Cloning Services...")
        start_time = time.time()
        
        # Start services concurrently
        tasks = []
        for service_name, config in self.service_configs.items():
            task = asyncio.create_task(self._start_service(service_name, config))
            tasks.append(task)
        
        # Wait for all services to start
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        for i, (service_name, config) in enumerate(self.service_configs.items()):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to start {service_name}: {result}")
                self.performance_metrics["services_failed"] += 1
            else:
                logger.info(f"Successfully started {service_name}")
                self.performance_metrics["services_started"] += 1
        
        self.performance_metrics["startup_time"] = time.time() - start_time
        self.running = True
        
        logger.info(f"Voice cloning services startup completed in {self.performance_metrics['startup_time']:.2f} seconds")
        logger.info(f"Started {self.performance_metrics['services_started']} services")
        
        if self.performance_metrics["services_failed"] > 0:
            logger.warning(f"Failed to start {self.performance_metrics['services_failed']} services")
    
    async def _start_service(self, service_name: str, config: Dict[str, Any]):
        """Start a single voice cloning service"""
        try:
            # Add startup delay if specified
            if config.get("startup_delay", 0) > 0:
                await asyncio.sleep(config["startup_delay"])
            
            logger.info(f"Starting {config['name']} on port {config['port']}")
            
            # Start the service in a subprocess for better isolation
            if service_name == "voice_cloning":
                cmd = [
                    sys.executable, "-c", 
                    f"import sys; import os; sys.path.append(os.getcwd()); "
                    f"import asyncio; from {config['module']} import start_enhanced_voice_cloning_service; "
                    f"asyncio.run(start_enhanced_voice_cloning_service({config['port']}))"
                ]
            elif service_name == "web_interface":
                cmd = [
                    sys.executable, "-c", 
                    f"import sys; import os; sys.path.append(os.getcwd()); "
                    f"import asyncio; from {config['module']} import start_web_interface_server; "
                    f"asyncio.run(start_web_interface_server({config['port']}))"
                ]
            else:
                cmd = [
                    sys.executable, "-c", 
                    f"import sys; import os; sys.path.append(os.getcwd()); "
                    f"import asyncio; from {config['module']} import start_enhanced_voice_cloning_service; "
                    f"asyncio.run(start_enhanced_voice_cloning_service({config['port']}))"
                ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.processes[service_name] = process
            self.services[service_name] = {
                "config": config,
                "process": process,
                "start_time": datetime.now(),
                "status": "starting"
            }
            
            # Wait a moment for service to initialize
            await asyncio.sleep(3)
            
            # Check if service is healthy
            if await self._check_service_health(service_name, config):
                self.services[service_name]["status"] = "healthy"
                logger.info(f"{config['name']} is healthy and running")
            else:
                self.services[service_name]["status"] = "unhealthy"
                logger.warning(f"{config['name']} failed health check")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting {service_name}: {e}")
            raise
    
    async def _check_service_health(self, service_name: str, config: Dict[str, Any]) -> bool:
        """Check if a voice cloning service is healthy"""
        try:
            import aiohttp
            
            url = f"http://127.0.0.1:{config['port']}{config['health_endpoint']}"
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("ok", False)
                    return False
        except Exception as e:
            logger.debug(f"Health check failed for {service_name}: {e}")
            return False
    
    async def monitor_services(self):
        """Monitor all voice cloning services and restart if needed"""
        logger.info("Starting voice cloning service monitoring...")
        
        while self.running:
            try:
                for service_name, service_info in self.services.items():
                    config = service_info["config"]
                    
                    # Check service health
                    is_healthy = await self._check_service_health(service_name, config)
                    
                    if is_healthy:
                        if service_info["status"] != "healthy":
                            logger.info(f"{config['name']} recovered and is now healthy")
                            service_info["status"] = "healthy"
                    else:
                        if service_info["status"] == "healthy":
                            logger.warning(f"{config['name']} became unhealthy")
                            service_info["status"] = "unhealthy"
                        
                        # Restart service if it's critical and unhealthy
                        if config.get("required", False) and service_info["status"] == "unhealthy":
                            logger.warning(f"Restarting critical service {service_name}")
                            await self._restart_service(service_name)
                
                # Update uptime
                self.performance_metrics["total_uptime"] = (datetime.now() - self.start_time).total_seconds()
                
                # Update voice cloning specific metrics
                await self._update_voice_cloning_metrics()
                
                # Sleep before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in service monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _update_voice_cloning_metrics(self):
        """Update voice cloning specific metrics"""
        try:
            import aiohttp
            
            # Get metrics from voice cloning service
            url = "http://127.0.0.1:5083/metrics"
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        metrics = await response.json()
                        
                        # Update voice cloning metrics
                        voice_cloning_metrics = metrics.get("voice_cloning", {})
                        self.performance_metrics["voice_clones_processed"] = voice_cloning_metrics.get("voice_clones_created", 0)
                        
                        # Get active sessions from health check
                        health_url = "http://127.0.0.1:5083/health"
                        async with session.get(health_url) as health_response:
                            if health_response.status == 200:
                                health_data = await health_response.json()
                                self.performance_metrics["active_sessions"] = health_data.get("active_sessions", 0)
                        
        except Exception as e:
            logger.debug(f"Failed to update voice cloning metrics: {e}")
    
    async def _restart_service(self, service_name: str):
        """Restart a failed voice cloning service"""
        try:
            logger.info(f"Restarting {service_name}...")
            
            # Stop the current process
            if service_name in self.processes:
                process = self.processes[service_name]
                process.terminate()
                await process.wait()
                del self.processes[service_name]
            
            # Start the service again
            config = self.service_configs[service_name]
            await self._start_service(service_name, config)
            
            logger.info(f"Successfully restarted {service_name}")
            
        except Exception as e:
            logger.error(f"Failed to restart {service_name}: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive voice cloning system status"""
        status = {
            "system": {
                "running": self.running,
                "uptime_seconds": self.performance_metrics["total_uptime"],
                "startup_time": self.performance_metrics["startup_time"],
                "services_started": self.performance_metrics["services_started"],
                "services_failed": self.performance_metrics["services_failed"]
            },
            "voice_cloning": {
                "voice_clones_processed": self.performance_metrics["voice_clones_processed"],
                "active_sessions": self.performance_metrics["active_sessions"]
            },
            "services": {}
        }
        
        for service_name, service_info in self.services.items():
            config = service_info["config"]
            uptime = (datetime.now() - service_info["start_time"]).total_seconds()
            
            status["services"][service_name] = {
                "name": config["name"],
                "port": config["port"],
                "status": service_info["status"],
                "uptime_seconds": uptime,
                "health_endpoint": config["health_endpoint"]
            }
        
        return status
    
    async def stop_all_services(self):
        """Stop all voice cloning services gracefully"""
        logger.info("Stopping all voice cloning services...")
        self.running = False
        
        # Stop all processes
        for service_name, process in self.processes.items():
            try:
                logger.info(f"Stopping {service_name}...")
                process.terminate()
                await process.wait()
                logger.info(f"Stopped {service_name}")
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")
        
        logger.info("All voice cloning services stopped")

async def main():
    """Main function"""
    service_manager = VoiceCloningServiceManager()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(service_manager.stop_all_services())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all services
        await service_manager.start_all_services()
        
        # Start monitoring
        monitor_task = asyncio.create_task(service_manager.monitor_services())
        
        # Keep running
        logger.info("VoiceStudio Voice Cloning Services are running. Press Ctrl+C to stop.")
        logger.info("Voice Cloning Service: http://localhost:5083")
        logger.info("Web Interface: http://localhost:8080")
        
        # Print status every 5 minutes
        while service_manager.running:
            await asyncio.sleep(300)  # 5 minutes
            status = await service_manager.get_system_status()
            logger.info(f"Voice Cloning System Status: {json.dumps(status, indent=2)}")
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await service_manager.stop_all_services()

if __name__ == "__main__":
    asyncio.run(main())
