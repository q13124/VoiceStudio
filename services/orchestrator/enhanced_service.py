#!/usr/bin/env python3
"""
VoiceStudio Enhanced Orchestrator Service
High-performance async HTTP server with advanced workflow orchestration and caching.
"""

import json
import logging
import time
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response
import threading
from functools import lru_cache
from cachetools import TTLCache
import sys
import os

# Add services to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database_logger, record_metric
from service_discovery import register_service, service_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedOrchestratorService:
    """Enhanced orchestrator service with performance optimizations"""
    
    def __init__(self):
        self.status = "running"
        self.start_time = datetime.now()
        
        # Service registry with health monitoring
        self.services = {
            "assistant": {"port": 5080, "status": "unknown", "last_check": None},
            "autofix": {"port": 5081, "status": "unknown", "last_check": None}
        }
        
        # Optimized settings with caching
        self.settings = {
            "max_concurrent_requests": 100,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "log_level": "INFO",
            "enable_caching": True,
            "cache_ttl": 300,
            "parallel_processing": True,
            "connection_pool_size": 20
        }
        
        # Model weights with versioning
        self.weights = {
            "model_version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "models": {
                "speech_recognition": {"weight": 0.8, "enabled": True, "version": "1.0.0"},
                "text_processing": {"weight": 0.7, "enabled": True, "version": "1.0.0"},
                "voice_synthesis": {"weight": 0.9, "enabled": True, "version": "1.0.0"},
                "diarization": {"weight": 0.6, "enabled": True, "version": "1.0.0"}
            }
        }
        
        # Performance optimizations
        self.response_cache = TTLCache(maxsize=2000, ttl=300)  # 5 minute cache
        self.service_health_cache = TTLCache(maxsize=100, ttl=30)  # 30 second cache
        self._cache_lock = asyncio.Lock()
        
        # Database logger
        self.db_logger = get_database_logger("orchestrator-service", "Orchestrator Service")
        
        # Service registration
        self.service_id = register_service("orchestrator", port=5090)
        
        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.service_calls = 0
        self.failed_service_calls = 0
        
        # HTTP client session for service calls
        self.http_session: Optional[ClientSession] = None
        
    async def init_http_session(self):
        """Initialize HTTP session for service calls"""
        connector = aiohttp.TCPConnector(
            limit=self.settings["connection_pool_size"],
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        timeout = aiohttp.ClientTimeout(total=self.settings["timeout_seconds"])
        self.http_session = ClientSession(connector=connector, timeout=timeout)
    
    async def get_health(self) -> Dict[str, Any]:
        """Get service health status with caching"""
        cache_key = "health_status"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]
        
        # Generate fresh data
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Check service health in parallel
        service_statuses = await self._check_all_services_health()
        
        health_data = {
            "ok": True,
            "service": "orchestrator",
            "status": self.status,
            "uptime_seconds": uptime,
            "managed_services": len(self.services),
            "service_statuses": service_statuses,
            "performance": {
                "request_count": self.request_count,
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "service_call_success_rate": (self.service_calls - self.failed_service_calls) / max(1, self.service_calls),
                "memory_usage": self._get_memory_usage()
            },
            "ts": datetime.now().isoformat()
        }
        
        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = health_data
            self.cache_misses += 1
        
        # Record metrics
        record_metric("orchestrator-service", "Orchestrator Service", "health_check", 
                     time.time(), {"uptime": uptime, "services": len(service_statuses)})
        
        return health_data
    
    async def get_settings(self) -> Dict[str, Any]:
        """Get service settings with caching"""
        cache_key = "service_settings"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]
        
        settings_data = {
            "settings": self.settings,
            "last_updated": datetime.now().isoformat(),
            "performance": {
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "response_time_ms": 0  # Will be updated by middleware
            }
        }
        
        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = settings_data
            self.cache_misses += 1
        
        return settings_data
    
    async def get_weights(self) -> Dict[str, Any]:
        """Get model weights configuration with caching"""
        cache_key = "model_weights"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]
        
        weights_data = {
            "weights": self.weights,
            "last_updated": datetime.now().isoformat(),
            "performance": {
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "response_time_ms": 0  # Will be updated by middleware
            }
        }
        
        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = weights_data
            self.cache_misses += 1
        
        return weights_data
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        cache_key = "service_metrics"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.service_health_cache:
                return self.service_health_cache[cache_key]
        
        # Generate metrics
        uptime = (datetime.now() - self.start_time).total_seconds()
        service_statuses = await self._check_all_services_health()
        
        metrics = {
            "service": "orchestrator",
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            "service_calls": self.service_calls,
            "failed_service_calls": self.failed_service_calls,
            "service_success_rate": (self.service_calls - self.failed_service_calls) / max(1, self.service_calls),
            "managed_services": len(self.services),
            "healthy_services": len([s for s in service_statuses.values() if s.get("status") == "healthy"]),
            "memory_usage": self._get_memory_usage(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache metrics
        async with self._cache_lock:
            self.service_health_cache[cache_key] = metrics
        
        return metrics
    
    async def _check_all_services_health(self) -> Dict[str, Any]:
        """Check health of all managed services in parallel"""
        if not self.http_session:
            await self.init_http_session()
        
        health_tasks = []
        for service_name, service_info in self.services.items():
            task = self._check_service_health(service_name, service_info)
            health_tasks.append(task)
        
        # Execute all health checks in parallel
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        service_statuses = {}
        for i, (service_name, service_info) in enumerate(self.services.items()):
            result = results[i]
            if isinstance(result, Exception):
                service_statuses[service_name] = {
                    "status": "unhealthy",
                    "error": str(result),
                    "last_check": datetime.now().isoformat()
                }
                self.failed_service_calls += 1
            else:
                service_statuses[service_name] = result
                if result.get("status") == "healthy":
                    self.service_calls += 1
        
        return service_statuses
    
    async def _check_service_health(self, service_name: str, service_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a single service"""
        cache_key = f"health_{service_name}"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.service_health_cache:
                return self.service_health_cache[cache_key]
        
        try:
            port = service_info["port"]
            url = f"http://127.0.0.1:{port}/health"
            
            async with self.http_session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    health_result = {
                        "status": "healthy",
                        "port": port,
                        "last_check": datetime.now().isoformat(),
                        "response_time_ms": 0,  # Could be measured
                        "data": data
                    }
                else:
                    health_result = {
                        "status": "unhealthy",
                        "port": port,
                        "last_check": datetime.now().isoformat(),
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            health_result = {
                "status": "unhealthy",
                "port": service_info["port"],
                "last_check": datetime.now().isoformat(),
                "error": str(e)
            }
        
        # Cache the result
        async with self._cache_lock:
            self.service_health_cache[cache_key] = health_result
        
        return health_result
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    async def cleanup_cache(self):
        """Clean up expired cache entries"""
        async with self._cache_lock:
            self.response_cache.clear()
            self.service_health_cache.clear()
    
    async def close(self):
        """Close the service and cleanup resources"""
        if self.http_session:
            await self.http_session.close()
        await self.cleanup_cache()

# Global service instance
orchestrator_service = EnhancedOrchestratorService()

# Request handlers
async def handle_health(request: Request) -> Response:
    """Handle health check endpoint"""
    start_time = time.time()
    orchestrator_service.request_count += 1
    
    try:
        health_data = await orchestrator_service.get_health()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("orchestrator-service", "Orchestrator Service", "response_time", 
                     response_time, {"endpoint": "/health"})
        
        return web.json_response(health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        orchestrator_service.db_logger.error(f"Health check failed: {e}")
        return web.json_response({"error": "Health check failed"}, status=500)

async def handle_settings(request: Request) -> Response:
    """Handle settings endpoint"""
    start_time = time.time()
    orchestrator_service.request_count += 1
    
    try:
        settings_data = await orchestrator_service.get_settings()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("orchestrator-service", "Orchestrator Service", "response_time", 
                     response_time, {"endpoint": "/settings"})
        
        return web.json_response(settings_data)
    except Exception as e:
        logger.error(f"Settings failed: {e}")
        orchestrator_service.db_logger.error(f"Settings failed: {e}")
        return web.json_response({"error": "Settings failed"}, status=500)

async def handle_weights(request: Request) -> Response:
    """Handle weights endpoint"""
    start_time = time.time()
    orchestrator_service.request_count += 1
    
    try:
        weights_data = await orchestrator_service.get_weights()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("orchestrator-service", "Orchestrator Service", "response_time", 
                     response_time, {"endpoint": "/weights"})
        
        return web.json_response(weights_data)
    except Exception as e:
        logger.error(f"Weights failed: {e}")
        orchestrator_service.db_logger.error(f"Weights failed: {e}")
        return web.json_response({"error": "Weights failed"}, status=500)

async def handle_metrics(request: Request) -> Response:
    """Handle metrics endpoint"""
    start_time = time.time()
    orchestrator_service.request_count += 1
    
    try:
        metrics_data = await orchestrator_service.get_metrics()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("orchestrator-service", "Orchestrator Service", "response_time", 
                     response_time, {"endpoint": "/metrics"})
        
        return web.json_response(metrics_data)
    except Exception as e:
        logger.error(f"Metrics failed: {e}")
        orchestrator_service.db_logger.error(f"Metrics failed: {e}")
        return web.json_response({"error": "Metrics failed"}, status=500)

# Middleware for performance monitoring
@web.middleware
async def performance_middleware(request: Request, handler):
    """Middleware to track performance metrics"""
    start_time = time.time()
    
    try:
        response = await handler(request)
        
        # Record request metrics
        response_time = (time.time() - start_time) * 1000
        record_metric("orchestrator-service", "Orchestrator Service", "request_duration", 
                     response_time, {
                         "method": request.method,
                         "path": request.path,
                         "status": response.status
                     })
        
        # Add performance headers
        response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
        response.headers['X-Cache-Status'] = 'HIT' if 'cached' in str(response.body) else 'MISS'
        
        return response
    except Exception as e:
        # Record error metrics
        response_time = (time.time() - start_time) * 1000
        record_metric("orchestrator-service", "Orchestrator Service", "error_duration", 
                     response_time, {
                         "method": request.method,
                         "path": request.path,
                         "error": str(e)
                     })
        raise

def create_app() -> web.Application:
    """Create the web application with routes and middleware"""
    app = web.Application(middlewares=[performance_middleware])
    
    # Add routes
    app.router.add_get('/health', handle_health)
    app.router.add_get('/settings', handle_settings)
    app.router.add_get('/weights', handle_weights)
    app.router.add_get('/metrics', handle_metrics)
    
    # Add CORS headers
    async def cors_handler(request: Request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    app.middlewares.append(cors_handler)
    
    return app

async def start_enhanced_orchestrator_service(port: int = 5090):
    """Start the enhanced orchestrator service"""
    app = create_app()
    
    # Initialize HTTP session
    await orchestrator_service.init_http_session()
    
    # Log startup
    logger.info(f"Enhanced Orchestrator Service starting on port {port}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Settings endpoint: http://127.0.0.1:{port}/settings")
    logger.info(f"Weights endpoint: http://127.0.0.1:{port}/weights")
    logger.info(f"Metrics endpoint: http://127.0.0.1:{port}/metrics")
    
    # Start service discovery
    from service_discovery import start_service_discovery
    start_service_discovery()
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', port)
    await site.start()
    
    # Log successful startup
    orchestrator_service.db_logger.info("Enhanced Orchestrator Service started successfully")
    
    try:
        # Keep the service running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Enhanced Orchestrator Service shutting down...")
        await orchestrator_service.close()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(start_enhanced_orchestrator_service())
