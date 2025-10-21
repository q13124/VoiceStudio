#!/usr/bin/env python3
"""
VoiceStudio Performance Monitor Service
Real-time performance monitoring for maximum performance voice cloning system.
"""

import asyncio
import logging
import signal
import sys
import time
import os
import psutil
import json
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, timedelta
import threading
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Real-time performance monitoring for VoiceStudio"""
    
    def __init__(self):
        self.cpu_count = os.cpu_count()
        self.memory_total = psutil.virtual_memory().total
        self.disk_total = psutil.disk_usage('/').total
        
        # Performance history (last 100 measurements)
        self.performance_history = deque(maxlen=100)
        
        # Service monitoring
        self.services = {
            "voice_cloning_main": {"port": 5083, "status": "unknown"},
            "voice_cloning_worker_1": {"port": 5084, "status": "unknown"},
            "voice_cloning_worker_2": {"port": 5085, "status": "unknown"},
            "voice_cloning_worker_3": {"port": 5086, "status": "unknown"},
            "voice_cloning_worker_4": {"port": 5087, "status": "unknown"},
            "web_interface": {"port": 8080, "status": "unknown"},
            "ai_coordinator": {"port": 8081, "status": "unknown"},
            "performance_monitor": {"port": 8082, "status": "unknown"}
        }
        
        # Performance metrics
        self.metrics = {
            "system": {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "network_io": {"bytes_sent": 0, "bytes_recv": 0},
                "load_average": [0.0, 0.0, 0.0]
            },
            "services": {},
            "voice_cloning": {
                "total_requests": 0,
                "successful_clones": 0,
                "failed_clones": 0,
                "average_processing_time": 0.0,
                "peak_concurrent_sessions": 0,
                "current_concurrent_sessions": 0
            },
            "ai_agents": {
                "total_workers": 0,
                "active_tasks": 0,
                "completed_tasks": 0,
                "utilization_percentage": 0.0
            }
        }
        
        # WebSocket connections for real-time updates
        self.websocket_connections = set()
        self.websocket_lock = threading.Lock()
        
        logger.info(f"📊 Performance Monitor initialized:")
        logger.info(f"   CPU Cores: {self.cpu_count}")
        logger.info(f"   Memory: {self.memory_total / (1024**3):.1f}GB")
        logger.info(f"   Services Monitored: {len(self.services)}")
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        logger.info("📊 Starting performance monitoring...")
        
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Check service health
                await self._check_service_health()
                
                # Collect voice cloning metrics
                await self._collect_voice_cloning_metrics()
                
                # Collect AI agent metrics
                await self._collect_ai_agent_metrics()
                
                # Store in history
                self._store_performance_snapshot()
                
                # Broadcast to WebSocket connections
                await self._broadcast_performance_update()
                
                # Log performance summary
                self._log_performance_summary()
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Load average (if available)
            try:
                load_avg = os.getloadavg()
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]  # Windows doesn't have loadavg
            
            self.metrics["system"] = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "disk_usage": disk_percent,
                "network_io": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                },
                "load_average": list(load_avg)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to collect system metrics: {e}")
    
    async def _check_service_health(self):
        """Check health of all services"""
        import aiohttp
        
        for service_name, service_info in self.services.items():
            try:
                url = f"http://127.0.0.1:{service_info['port']}/health"
                timeout = aiohttp.ClientTimeout(total=2)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            service_info["status"] = "healthy"
                            data = await response.json()
                            service_info["last_check"] = datetime.now().isoformat()
                            service_info["response_data"] = data
                        else:
                            service_info["status"] = "unhealthy"
                            
            except Exception as e:
                service_info["status"] = "unreachable"
                service_info["error"] = str(e)
        
        self.metrics["services"] = dict(self.services)
    
    async def _collect_voice_cloning_metrics(self):
        """Collect voice cloning service metrics"""
        try:
            import aiohttp
            
            # Get metrics from main voice cloning service
            url = "http://127.0.0.1:5083/metrics"
            timeout = aiohttp.ClientTimeout(total=2)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.metrics["voice_cloning"].update(data)
                        
        except Exception as e:
            logger.debug(f"Could not collect voice cloning metrics: {e}")
    
    async def _collect_ai_agent_metrics(self):
        """Collect AI agent metrics"""
        try:
            import aiohttp
            
            # Get metrics from AI coordinator
            url = "http://127.0.0.1:8081/system-performance"
            timeout = aiohttp.ClientTimeout(total=2)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.metrics["ai_agents"] = {
                            "total_workers": data.get("total_ai_workers", 0),
                            "active_tasks": data.get("active_tasks", 0),
                            "completed_tasks": data.get("completed_tasks", 0),
                            "utilization_percentage": data.get("overall_utilization", 0.0)
                        }
                        
        except Exception as e:
            logger.debug(f"Could not collect AI agent metrics: {e}")
    
    def _store_performance_snapshot(self):
        """Store current performance snapshot in history"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "metrics": dict(self.metrics)
        }
        self.performance_history.append(snapshot)
    
    async def _broadcast_performance_update(self):
        """Broadcast performance update to WebSocket connections"""
        if not self.websocket_connections:
            return
        
        update_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "type": "performance_update"
        }
        
        disconnected = set()
        async with self.websocket_lock:
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(json.dumps(update_data))
                except Exception as e:
                    logger.debug(f"WebSocket broadcast error: {e}")
                    disconnected.add(websocket)
        
        # Remove disconnected WebSockets
        self.websocket_connections -= disconnected
    
    def _log_performance_summary(self):
        """Log performance summary"""
        system = self.metrics["system"]
        voice_cloning = self.metrics["voice_cloning"]
        ai_agents = self.metrics["ai_agents"]
        
        healthy_services = sum(1 for s in self.services.values() if s["status"] == "healthy")
        
        logger.info(f"📊 Performance Summary:")
        logger.info(f"   CPU: {system['cpu_usage']:.1f}% | Memory: {system['memory_usage']:.1f}% | Disk: {system['disk_usage']:.1f}%")
        logger.info(f"   Services: {healthy_services}/{len(self.services)} healthy")
        logger.info(f"   Voice Cloning: {voice_cloning['successful_clones']} successful, {voice_cloning['current_concurrent_sessions']} active")
        logger.info(f"   AI Agents: {ai_agents['utilization_percentage']:.1f}% utilization ({ai_agents['active_tasks']}/{ai_agents['total_workers']})")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.metrics["system"],
            "services": {
                "total": len(self.services),
                "healthy": sum(1 for s in self.services.values() if s["status"] == "healthy"),
                "unhealthy": sum(1 for s in self.services.values() if s["status"] == "unhealthy"),
                "unreachable": sum(1 for s in self.services.values() if s["status"] == "unreachable")
            },
            "voice_cloning": self.metrics["voice_cloning"],
            "ai_agents": self.metrics["ai_agents"],
            "history_count": len(self.performance_history)
        }
    
    def get_performance_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get performance history for the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            snapshot for snapshot in self.performance_history
            if datetime.fromisoformat(snapshot["timestamp"]) >= cutoff_time
        ]

class PerformanceMonitorService:
    """Performance Monitor Service for VoiceStudio"""
    
    def __init__(self, port: int = 8082):
        self.port = port
        self.app = FastAPI(
            title="VoiceStudio Performance Monitor Service",
            version="1.0.0",
            description="Real-time performance monitoring for VoiceStudio"
        )
        
        # Initialize performance monitor
        self.monitor = PerformanceMonitor()
        
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/performance-summary")
        async def get_performance_summary():
            """Get current performance summary"""
            return self.monitor.get_performance_summary()
        
        @self.app.get("/performance-history")
        async def get_performance_history(minutes: int = 60):
            """Get performance history"""
            return self.monitor.get_performance_history(minutes)
        
        @self.app.get("/system-metrics")
        async def get_system_metrics():
            """Get current system metrics"""
            return self.monitor.metrics["system"]
        
        @self.app.get("/service-status")
        async def get_service_status():
            """Get status of all services"""
            return self.monitor.services
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "performance_monitor",
                "port": self.port,
                "monitoring_active": True,
                "services_monitored": len(self.monitor.services)
            }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time performance updates"""
            await websocket.accept()
            
            async with self.monitor.websocket_lock:
                self.monitor.websocket_connections.add(websocket)
            
            logger.info(f"📊 WebSocket connected: {websocket.client}")
            
            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except WebSocketDisconnect:
                logger.info(f"📊 WebSocket disconnected: {websocket.client}")
            except Exception as e:
                logger.error(f"📊 WebSocket error: {e}")
            finally:
                async with self.monitor.websocket_lock:
                    self.monitor.websocket_connections.discard(websocket)

async def start_performance_monitor_service(port: int = 8082):
    """Start the Performance Monitor service"""
    service = PerformanceMonitorService(port)
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(service.monitor.start_monitoring())
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down Performance Monitor...")
        monitoring_task.cancel()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = uvicorn.Config(
        service.app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_performance_monitor_service())
