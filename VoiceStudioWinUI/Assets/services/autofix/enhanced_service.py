#!/usr/bin/env python3
"""
VoiceStudio Enhanced Autofix Service
High-performance async HTTP server with intelligent error analysis and automated fixes.
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
import re

# Add services to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database_logger, record_metric
from service_discovery import register_service, service_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAutofixService:
    """Enhanced autofix service with intelligent error analysis"""
    
    def __init__(self):
        self.status = "running"
        self.start_time = datetime.now()
        
        # Enhanced features with performance tracking
        self.features = {
            "error_detection": True,
            "code_repair": True,
            "service_monitoring": True,
            "performance_optimization": True,
            "intelligent_caching": True,
            "pattern_matching": True,
            "automated_fixes": True
        }
        
        # Enhanced error patterns with confidence scores
        self.error_patterns = {
            "connection_timeout": {
                "pattern": r"connection.*timeout|timeout.*connection",
                "suggestion": "Increase timeout settings and implement retry logic",
                "confidence": 0.9,
                "fix_type": "configuration"
            },
            "memory_leak": {
                "pattern": r"memory.*leak|out of memory|memory.*exhausted",
                "suggestion": "Review object lifecycle management and implement proper cleanup",
                "confidence": 0.8,
                "fix_type": "code"
            },
            "null_reference": {
                "pattern": r"null.*reference|none.*type|attribute.*error",
                "suggestion": "Add null checks before object access and implement defensive programming",
                "confidence": 0.85,
                "fix_type": "code"
            },
            "database_connection": {
                "pattern": r"database.*connection|connection.*pool|sql.*error",
                "suggestion": "Check database connectivity and connection pool configuration",
                "confidence": 0.8,
                "fix_type": "infrastructure"
            },
            "service_unavailable": {
                "pattern": r"service.*unavailable|connection.*refused|port.*unreachable",
                "suggestion": "Verify service is running and check network connectivity",
                "confidence": 0.9,
                "fix_type": "infrastructure"
            },
            "permission_denied": {
                "pattern": r"permission.*denied|access.*denied|unauthorized",
                "suggestion": "Check file permissions and user access rights",
                "confidence": 0.95,
                "fix_type": "security"
            }
        }
        
        # Performance optimizations
        self.response_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute cache
        self.analysis_cache = TTLCache(maxsize=500, ttl=600)   # 10 minute cache
        self._cache_lock = asyncio.Lock()
        
        # Database logger
        self.db_logger = get_database_logger("autofix-service", "Autofix Service")
        
        # Service registration
        self.service_id = register_service("autofix", port=5081)
        
        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.analyses_performed = 0
        self.fixes_applied = 0
        
        # Recent fixes with enhanced tracking
        self.recent_fixes = []
        self.fix_statistics = {
            "total_analyses": 0,
            "successful_fixes": 0,
            "failed_fixes": 0,
            "pattern_matches": {}
        }
        
    async def get_status(self) -> Dict[str, Any]:
        """Get autofix service status with caching"""
        cache_key = "service_status"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        status_data = {
            "ok": True,
            "service": "autofix",
            "status": self.status,
            "uptime_seconds": uptime,
            "features": self.features,
            "recent_fixes_count": len(self.recent_fixes),
            "statistics": self.fix_statistics,
            "performance": {
                "request_count": self.request_count,
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "analysis_success_rate": self.fix_statistics["successful_fixes"] / max(1, self.fix_statistics["total_analyses"]),
                "memory_usage": self._get_memory_usage()
            },
            "ts": datetime.now().isoformat()
        }
        
        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = status_data
            self.cache_misses += 1
        
        return status_data
    
    async def analyze_error(self, error_type: str, error_message: str, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced error analysis with pattern matching and caching"""
        cache_key = f"analysis_{hash(error_message)}_{error_type}"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.analysis_cache:
                self.cache_hits += 1
                cached_result = self.analysis_cache[cache_key]
                # Update timestamp but return cached analysis
                cached_result["timestamp"] = datetime.now().isoformat()
                cached_result["cached"] = True
                return cached_result
        
        self.analyses_performed += 1
        self.fix_statistics["total_analyses"] += 1
        
        suggestions = []
        matched_patterns = []
        
        # Enhanced pattern matching
        error_text = f"{error_type} {error_message}".lower()
        
        for pattern_name, pattern_info in self.error_patterns.items():
            if re.search(pattern_info["pattern"], error_text, re.IGNORECASE):
                suggestions.append({
                    "pattern": pattern_name,
                    "suggestion": pattern_info["suggestion"],
                    "confidence": pattern_info["confidence"],
                    "fix_type": pattern_info["fix_type"],
                    "priority": self._calculate_priority(pattern_info["confidence"], pattern_name)
                })
                matched_patterns.append(pattern_name)
                
                # Update pattern statistics
                if pattern_name not in self.fix_statistics["pattern_matches"]:
                    self.fix_statistics["pattern_matches"][pattern_name] = 0
                self.fix_statistics["pattern_matches"][pattern_name] += 1
        
        # Sort suggestions by priority
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        # Add generic suggestions if no patterns matched
        if not suggestions:
            suggestions.append({
                "pattern": "unknown",
                "suggestion": "Review logs and check service configuration",
                "confidence": 0.3,
                "fix_type": "general",
                "priority": 1
            })
        
        # Generate automated fix recommendations
        automated_fixes = self._generate_automated_fixes(suggestions, context)
        
        fix_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "suggestions": suggestions,
            "matched_patterns": matched_patterns,
            "automated_fixes": automated_fixes,
            "analysis_id": f"analysis_{int(time.time())}",
            "cached": False
        }
        
        # Store in recent fixes
        self.recent_fixes.append(fix_record)
        if len(self.recent_fixes) > 100:  # Keep only recent 100 fixes
            self.recent_fixes = self.recent_fixes[-100:]
        
        # Cache the result
        async with self._cache_lock:
            self.analysis_cache[cache_key] = fix_record
            self.cache_misses += 1
        
        # Record metrics
        record_metric("autofix-service", "Autofix Service", "error_analysis", 
                     time.time(), {
                         "error_type": error_type,
                         "patterns_matched": len(matched_patterns),
                         "suggestions_count": len(suggestions)
                     })
        
        return fix_record
    
    def _calculate_priority(self, confidence: float, pattern_name: str) -> int:
        """Calculate priority score for suggestions"""
        base_priority = int(confidence * 100)
        
        # Boost priority for critical patterns
        critical_patterns = ["memory_leak", "service_unavailable", "permission_denied"]
        if pattern_name in critical_patterns:
            base_priority += 20
        
        return min(base_priority, 100)
    
    def _generate_automated_fixes(self, suggestions: List[Dict], context: Optional[Dict]) -> List[Dict]:
        """Generate automated fix recommendations"""
        automated_fixes = []
        
        for suggestion in suggestions:
            if suggestion["fix_type"] == "configuration":
                automated_fixes.append({
                    "type": "config_update",
                    "description": f"Update configuration: {suggestion['suggestion']}",
                    "confidence": suggestion["confidence"],
                    "automated": True
                })
            elif suggestion["fix_type"] == "code":
                automated_fixes.append({
                    "type": "code_review",
                    "description": f"Code review needed: {suggestion['suggestion']}",
                    "confidence": suggestion["confidence"],
                    "automated": False
                })
            elif suggestion["fix_type"] == "infrastructure":
                automated_fixes.append({
                    "type": "infrastructure_check",
                    "description": f"Infrastructure check: {suggestion['suggestion']}",
                    "confidence": suggestion["confidence"],
                    "automated": False
                })
        
        return automated_fixes
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        cache_key = "service_metrics"
        
        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                return self.response_cache[cache_key]
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        metrics = {
            "service": "autofix",
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            "analyses_performed": self.analyses_performed,
            "fixes_applied": self.fixes_applied,
            "fix_success_rate": self.fix_statistics["successful_fixes"] / max(1, self.fix_statistics["total_analyses"]),
            "pattern_statistics": self.fix_statistics["pattern_matches"],
            "recent_fixes_count": len(self.recent_fixes),
            "memory_usage": self._get_memory_usage(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache metrics
        async with self._cache_lock:
            self.response_cache[cache_key] = metrics
        
        return metrics
    
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
            self.analysis_cache.clear()

# Global service instance
autofix_service = EnhancedAutofixService()

# Request handlers
async def handle_health(request: Request) -> Response:
    """Handle health check endpoint"""
    start_time = time.time()
    autofix_service.request_count += 1
    
    try:
        status_data = await autofix_service.get_status()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("autofix-service", "Autofix Service", "response_time", 
                     response_time, {"endpoint": "/health"})
        
        return web.json_response(status_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        autofix_service.db_logger.error(f"Health check failed: {e}")
        return web.json_response({"error": "Health check failed"}, status=500)

async def handle_status(request: Request) -> Response:
    """Handle status endpoint"""
    start_time = time.time()
    autofix_service.request_count += 1
    
    try:
        status_data = await autofix_service.get_status()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("autofix-service", "Autofix Service", "response_time", 
                     response_time, {"endpoint": "/status"})
        
        return web.json_response(status_data)
    except Exception as e:
        logger.error(f"Status failed: {e}")
        autofix_service.db_logger.error(f"Status failed: {e}")
        return web.json_response({"error": "Status failed"}, status=500)

async def handle_analyze(request: Request) -> Response:
    """Handle error analysis endpoint"""
    start_time = time.time()
    autofix_service.request_count += 1
    
    try:
        data = await request.json()
        error_type = data.get('error_type', 'unknown')
        error_message = data.get('error_message', '')
        context = data.get('context', {})
        
        analysis = await autofix_service.analyze_error(error_type, error_message, context)
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("autofix-service", "Autofix Service", "response_time", 
                     response_time, {"endpoint": "/analyze", "error_type": error_type})
        
        return web.json_response(analysis)
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        autofix_service.db_logger.error(f"Analysis failed: {e}")
        return web.json_response({"error": "Analysis failed"}, status=500)

async def handle_metrics(request: Request) -> Response:
    """Handle metrics endpoint"""
    start_time = time.time()
    autofix_service.request_count += 1
    
    try:
        metrics_data = await autofix_service.get_metrics()
        
        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("autofix-service", "Autofix Service", "response_time", 
                     response_time, {"endpoint": "/metrics"})
        
        return web.json_response(metrics_data)
    except Exception as e:
        logger.error(f"Metrics failed: {e}")
        autofix_service.db_logger.error(f"Metrics failed: {e}")
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
        record_metric("autofix-service", "Autofix Service", "request_duration", 
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
        record_metric("autofix-service", "Autofix Service", "error_duration", 
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
    app.router.add_get('/status', handle_status)
    app.router.add_post('/analyze', handle_analyze)
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

async def start_enhanced_autofix_service(port: int = 5081):
    """Start the enhanced autofix service"""
    app = create_app()
    
    # Log startup
    logger.info(f"Enhanced Autofix Service starting on port {port}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Status endpoint: http://127.0.0.1:{port}/status")
    logger.info(f"Analyze endpoint: http://127.0.0.1:{port}/analyze")
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
    autofix_service.db_logger.info("Enhanced Autofix Service started successfully")
    
    try:
        # Keep the service running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Enhanced Autofix Service shutting down...")
        await autofix_service.cleanup_cache()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(start_enhanced_autofix_service())
