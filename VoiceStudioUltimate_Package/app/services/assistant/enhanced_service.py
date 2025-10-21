#!/usr/bin/env python3
"""
VoiceStudio Enhanced Assistant Service
High-performance async HTTP server with advanced caching, metrics, and optimization.
"""

import json
import logging
import time
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
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
from voice_cloning_service import voice_cloning_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAssistantService:
    """Enhanced assistant service with performance optimizations"""

    def __init__(self):
        self.status = "running"
        self.start_time = datetime.now()
        self.autofix_enabled = True
        self.autofix_status = "active"

        # Performance optimizations
        self.response_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute cache
        self.metrics_cache = TTLCache(maxsize=100, ttl=60)    # 1 minute cache
        self._cache_lock = asyncio.Lock()

        # Database logger
        self.db_logger = get_database_logger("assistant-service", "Assistant Service")

        # Service registration
        self.service_id = register_service("assistant", port=5080)

        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

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
        health_data = {
            "ok": True,
            "service": "assistant",
            "status": self.status,
            "uptime_seconds": uptime,
            "ts": datetime.now().isoformat(),
            "performance": {
                "request_count": self.request_count,
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "memory_usage": self._get_memory_usage()
            }
        }

        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = health_data
            self.cache_misses += 1

        # Record metrics
        record_metric("assistant-service", "Assistant Service", "health_check",
                     time.time(), {"uptime": uptime})

        return health_data

    async def get_autofix_status(self) -> Dict[str, Any]:
        """Get autofix service status with caching"""
        cache_key = "autofix_status"

        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]

        # Generate fresh data
        autofix_data = {
            "enabled": self.autofix_enabled,
            "status": self.autofix_status,
            "last_check": datetime.now().isoformat(),
            "features": [
                "error_detection",
                "code_repair",
                "service_monitoring",
                "performance_optimization",
                "intelligent_caching"
            ],
            "performance": {
                "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "response_time_ms": 0  # Will be updated by middleware
            }
        }

        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = autofix_data
            self.cache_misses += 1

    async def get_voice_cloning_status(self) -> Dict[str, Any]:
        """Get voice cloning service status"""
        cache_key = "voice_cloning_status"

        # Check cache first
        async with self._cache_lock:
            if cache_key in self.response_cache:
                self.cache_hits += 1
                return self.response_cache[cache_key]

        # Get fresh status
        voice_status = voice_cloning_service.get_status()

        # Cache the result
        async with self._cache_lock:
            self.response_cache[cache_key] = voice_status
            self.cache_misses += 1

        return voice_status

    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        cache_key = "service_metrics"

        # Check cache first
        async with self._cache_lock:
            if cache_key in self.metrics_cache:
                return self.metrics_cache[cache_key]

        # Generate metrics
        uptime = (datetime.now() - self.start_time).total_seconds()
        metrics = {
            "service": "assistant",
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            "memory_usage": self._get_memory_usage(),
            "timestamp": datetime.now().isoformat()
        }

        # Cache metrics
        async with self._cache_lock:
            self.metrics_cache[cache_key] = metrics

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
            # TTLCache handles expiration automatically, but we can force cleanup
            self.response_cache.clear()
            self.metrics_cache.clear()

# Global service instance
assistant_service = EnhancedAssistantService()

# Request handlers
async def handle_health(request: Request) -> Response:
    """Handle health check endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        health_data = await assistant_service.get_health()

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/health"})

        return web.json_response(health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        assistant_service.db_logger.error(f"Health check failed: {e}")
        return web.json_response({"error": "Health check failed"}, status=500)

async def handle_autofix_status(request: Request) -> Response:
    """Handle autofix status endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        autofix_data = await assistant_service.get_autofix_status()

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/autofix/status"})

        return web.json_response(autofix_data)
    except Exception as e:
        logger.error(f"Autofix status failed: {e}")
        assistant_service.db_logger.error(f"Autofix status failed: {e}")
        return web.json_response({"error": "Autofix status failed"}, status=500)

async def handle_metrics(request: Request) -> Response:
    """Handle metrics endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        metrics_data = await assistant_service.get_metrics()

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/metrics"})

        return web.json_response(metrics_data)
    except Exception as e:
        logger.error(f"Metrics failed: {e}")
        assistant_service.db_logger.error(f"Metrics failed: {e}")
        return web.json_response({"error": "Metrics failed"}, status=500)

async def handle_discovery(request: Request) -> Response:
    """Handle service discovery endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        # Get all registered services
        services = service_client.discover_services()

        discovery_data = {
            "services": services,
            "timestamp": datetime.now().isoformat(),
            "service_count": len(services)
        }

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/discovery"})

        return web.json_response(discovery_data)
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        assistant_service.db_logger.error(f"Discovery failed: {e}")
        return web.json_response({"error": "Discovery failed"}, status=500)

async def handle_voice_cloning_status(request: Request) -> Response:
    """Handle voice cloning status endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        voice_status = await assistant_service.get_voice_cloning_status()

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/voice-cloning/status"})

        return web.json_response(voice_status)
    except Exception as e:
        logger.error(f"Voice cloning status failed: {e}")
        assistant_service.db_logger.error(f"Voice cloning status failed: {e}")
        return web.json_response({"error": "Voice cloning status failed"}, status=500)

async def handle_synthesize_speech(request: Request) -> Response:
    """Handle speech synthesis endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        # Parse request data
        data = await request.json()
        text = data.get("text", "")
        model_type = data.get("model_type", "basic")
        speaker_wav = data.get("speaker_wav")
        language = data.get("language", "en")

        if not text:
            return web.json_response({"error": "Text is required"}, status=400)

        # Synthesize speech
        result = await voice_cloning_service.synthesize_speech(
            text=text,
            model_type=model_type,
            speaker_wav=speaker_wav,
            language=language
        )

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/voice-cloning/synthesize"})

        return web.json_response(result)
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}")
        assistant_service.db_logger.error(f"Speech synthesis failed: {e}")
        return web.json_response({"error": "Speech synthesis failed"}, status=500)

async def handle_clone_voice(request: Request) -> Response:
    """Handle voice cloning endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        # Parse request data
        data = await request.json()
        text = data.get("text", "")
        reference_audio_path = data.get("reference_audio_path", "")
        language = data.get("language", "en")

        if not text:
            return web.json_response({"error": "Text is required"}, status=400)

        if not reference_audio_path:
            return web.json_response({"error": "Reference audio path is required"}, status=400)

        # Clone voice
        result = await voice_cloning_service.clone_voice(
            text=text,
            reference_audio_path=reference_audio_path,
            language=language
        )

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/voice-cloning/clone"})

        return web.json_response(result)
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        assistant_service.db_logger.error(f"Voice cloning failed: {e}")
        return web.json_response({"error": "Voice cloning failed"}, status=500)

async def handle_transcribe_audio(request: Request) -> Response:
    """Handle audio transcription endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        # Parse request data
        data = await request.json()
        audio_path = data.get("audio_path", "")
        language = data.get("language", "en")

        if not audio_path:
            return web.json_response({"error": "Audio path is required"}, status=400)

        # Transcribe audio
        result = await voice_cloning_service.transcribe_audio(
            audio_path=audio_path,
            language=language
        )

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/voice-cloning/transcribe"})

        return web.json_response(result)
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        assistant_service.db_logger.error(f"Audio transcription failed: {e}")
        return web.json_response({"error": "Audio transcription failed"}, status=500)

async def handle_available_models(request: Request) -> Response:
    """Handle available models endpoint"""
    start_time = time.time()
    assistant_service.request_count += 1

    try:
        # Get available models
        result = await voice_cloning_service.get_available_models()

        # Record response time
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "response_time",
                     response_time, {"endpoint": "/voice-cloning/models"})

        return web.json_response(result)
    except Exception as e:
        logger.error(f"Get models failed: {e}")
        assistant_service.db_logger.error(f"Get models failed: {e}")
        return web.json_response({"error": "Get models failed"}, status=500)

# Middleware for performance monitoring
@web.middleware
async def performance_middleware(request: Request, handler):
    """Middleware to track performance metrics"""
    start_time = time.time()

    try:
        response = await handler(request)

        # Record request metrics
        response_time = (time.time() - start_time) * 1000
        record_metric("assistant-service", "Assistant Service", "request_duration",
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
        record_metric("assistant-service", "Assistant Service", "error_duration",
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
    app.router.add_get('/autofix/status', handle_autofix_status)
    app.router.add_get('/metrics', handle_metrics)
    app.router.add_get('/discovery', handle_discovery)

    # Voice cloning routes
    app.router.add_get('/voice-cloning/status', handle_voice_cloning_status)
    app.router.add_post('/voice-cloning/synthesize', handle_synthesize_speech)
    app.router.add_post('/voice-cloning/clone', handle_clone_voice)
    app.router.add_post('/voice-cloning/transcribe', handle_transcribe_audio)
    app.router.add_get('/voice-cloning/models', handle_available_models)

    # Add CORS headers
    async def cors_handler(request: Request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    app.middlewares.append(cors_handler)

    return app

async def start_enhanced_assistant_service(port: int = 5080):
    """Start the enhanced assistant service"""
    app = create_app()

    # Log startup
    logger.info(f"Enhanced Assistant Service starting on port {port}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Autofix endpoint: http://127.0.0.1:{port}/autofix/status")
    logger.info(f"Metrics endpoint: http://127.0.0.1:{port}/metrics")
    logger.info(f"Discovery endpoint: http://127.0.0.1:{port}/discovery")
    logger.info(f"Voice cloning status: http://127.0.0.1:{port}/voice-cloning/status")
    logger.info(f"Voice synthesis: http://127.0.0.1:{port}/voice-cloning/synthesize")
    logger.info(f"Voice cloning: http://127.0.0.1:{port}/voice-cloning/clone")
    logger.info(f"Audio transcription: http://127.0.0.1:{port}/voice-cloning/transcribe")
    logger.info(f"Available models: http://127.0.0.1:{port}/voice-cloning/models")

    # Start service discovery
    from service_discovery import start_service_discovery
    start_service_discovery()

    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', port)
    await site.start()

    # Log successful startup
    assistant_service.db_logger.info("Enhanced Assistant Service started successfully")

    try:
        # Keep the service running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Enhanced Assistant Service shutting down...")
        await assistant_service.cleanup_cache()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(start_enhanced_assistant_service())
