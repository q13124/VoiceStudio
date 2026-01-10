# IMPORTANT: Import Hugging Face fix FIRST to set environment variables
# before any huggingface_hub imports
try:
    from .routes import huggingface_fix  # noqa: F401
except ImportError:
    # If the fix module doesn't exist, set environment variable directly
    import os

    os.environ["HF_INFERENCE_API_BASE"] = "https://router.huggingface.co"
    os.environ["HF_ENDPOINT"] = "https://router.huggingface.co"

# Set default model/cache locations (override with env if needed)
import os

_default_models_root = os.environ.get(
    "VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"
)
os.environ.setdefault("VOICESTUDIO_MODELS_PATH", _default_models_root)
os.environ.setdefault("HF_HOME", os.path.join(_default_models_root, "hf_cache"))
os.environ.setdefault("TTS_HOME", os.path.join(_default_models_root, "xtts"))
os.environ.setdefault(
    "WHISPER_CPP_MODEL_PATH",
    os.path.join(_default_models_root, "whisper", "whisper-medium.en.gguf"),
)
try:
    os.makedirs(_default_models_root, exist_ok=True)
    os.makedirs(os.environ["HF_HOME"], exist_ok=True)
    os.makedirs(os.path.join(_default_models_root, "whisper"), exist_ok=True)
    os.makedirs(os.path.join(_default_models_root, "piper"), exist_ok=True)
    os.makedirs(os.path.join(_default_models_root, "xtts"), exist_ok=True)
except Exception as e:
    import logging

    logging.getLogger(__name__).warning("Failed to precreate model directories: %s", e)

import logging
import os
import time
from typing import Optional

from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Try importing Prometheus for metrics
try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest
    from prometheus_fastapi_instrumentator import Instrumentator

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    Counter = Histogram = Gauge = generate_latest = None
    Instrumentator = None
    logging.getLogger(__name__).debug(
        "prometheus-client or prometheus-fastapi-instrumentator not installed. "
        "Metrics will be limited."
    )

# Lazy imports - defer heavy imports until needed
# Exception handlers are lightweight, import immediately
from .error_handling import (
    add_request_id_middleware,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .exceptions import VoiceStudioException
from .version_info import get_version_info, get_version_string

# Defer heavy imports until startup
_PerformanceMonitoringMiddleware = None
_CompressionMiddleware = None
_load_all_plugins = None
_get_response_cache = None
_response_cache_middleware = None


def _lazy_import_performance_middleware():
    """Lazy import of performance monitoring middleware."""
    global _PerformanceMonitoringMiddleware
    if _PerformanceMonitoringMiddleware is None:
        from .middleware.performance_monitoring import PerformanceMonitoringMiddleware

        _PerformanceMonitoringMiddleware = PerformanceMonitoringMiddleware
    return _PerformanceMonitoringMiddleware


def _lazy_import_compression_middleware():
    """Lazy import of compression middleware."""
    global _CompressionMiddleware
    if _CompressionMiddleware is None:
        from .optimization import CompressionMiddleware

        _CompressionMiddleware = CompressionMiddleware
    return _CompressionMiddleware


def _lazy_import_plugins():
    """Lazy import of plugins module."""
    global _load_all_plugins
    if _load_all_plugins is None:
        from .plugins import load_all_plugins

        _load_all_plugins = load_all_plugins
    return _load_all_plugins


def _lazy_import_response_cache():
    """Lazy import of response cache."""
    global _get_response_cache, _response_cache_middleware
    if _get_response_cache is None:
        from .response_cache import get_response_cache, response_cache_middleware

        _get_response_cache = get_response_cache
        _response_cache_middleware = response_cache_middleware
    return _get_response_cache, _response_cache_middleware


# Lazy route imports - routes will be imported during startup
_ROUTES_LOADED = False

app = FastAPI(
    title="VoiceStudio Quantum+ Backend API",
    description="""
    VoiceStudio Quantum+ provides a comprehensive REST API for voice cloning, audio processing, and project management.
    
    ## Features
    
    - **Voice Cloning:** Multiple engines (XTTS v2, Chatterbox TTS, Tortoise TTS, OpenVoice, RVC, and more)
    - **Audio Processing:** 17+ audio effects and processing tools
    - **Project Management:** Projects, tracks, clips, and timeline management
    - **Quality Metrics:** MOS score, similarity, naturalness, SNR, artifact detection
    - **Training:** Custom voice model training with data optimization
    - **Batch Processing:** Queue-based batch synthesis
    - **Transcription:** Whisper-based speech-to-text
    - **Real-time Updates:** WebSocket support for real-time updates
    
    ## Error Handling
    
    All errors follow a standardized format with error codes, recovery suggestions, and context.
    See the error handling documentation for details.
    
    ## Rate Limiting
    
    API endpoints are rate-limited to ensure fair usage and system stability.
    Rate limit information is provided in response headers.
    See the rate limiting documentation for details.
    """,
    version="1.0.0",
    contact={
        "name": "VoiceStudio Support",
        "url": "https://github.com/voicestudio",
    },
    license_info={
        "name": "MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.voicestudio.com", "description": "Production server"},
    ],
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "persistAuthorization": True,
        "displayRequestDuration": True,
        # Disable service worker to prevent registration errors
        "deepLinking": False,
    },
    openapi_tags=[
        {"name": "profiles", "description": "Voice profile management operations."},
        {"name": "projects", "description": "Project management operations."},
        {"name": "voice", "description": "Voice synthesis and cloning operations."},
        {"name": "effects", "description": "Audio effects and processing operations."},
        {"name": "macros", "description": "Macros and automation operations."},
        {"name": "training", "description": "Voice model training operations."},
        {
            "name": "transcribe",
            "description": "Speech-to-text transcription operations.",
        },
        {"name": "models", "description": "Model management operations."},
        {"name": "quality", "description": "Quality metrics and analysis operations."},
        {"name": "batch", "description": "Batch processing operations."},
        {
            "name": "documentation",
            "description": "API documentation and validation operations.",
        },
    ],
)


# Lazy OpenAPI schema generation - only generate when requested
_openapi_schema_generated = False


def custom_openapi():
    """Generate custom OpenAPI schema with enhancements (lazy)."""
    global _openapi_schema_generated

    if app.openapi_schema:
        return app.openapi_schema

    # Only generate schema on first request (not during startup)
    if not _openapi_schema_generated:
        try:
            from .documentation import enhance_openapi_schema

            openapi_schema = enhance_openapi_schema(app)
            app.openapi_schema = openapi_schema
            _openapi_schema_generated = True
            return app.openapi_schema
        except ImportError:
            # Fallback to default OpenAPI generation
            from fastapi.openapi.utils import get_openapi

            openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
            )
            app.openapi_schema = openapi_schema
            _openapi_schema_generated = True
            return app.openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi

logger = logging.getLogger(__name__)


# Performance profiling middleware (imported at top)


# Request size limit middleware
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size."""

    def __init__(self, app, max_size_mb: float = 100.0):
        super().__init__(app)
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size_bytes:
                    logger.warning(
                        f"Request too large: {size} bytes "
                        f"(max: {self.max_size_bytes} bytes)"
                    )
                    from fastapi import HTTPException

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"Request body too large. "
                            f"Maximum size: "
                            f"{self.max_size_bytes / (1024*1024):.1f}MB"
                        ),
                    )
            except ValueError:
                pass  # Invalid content-length, let request proceed

        return await call_next(request)


# Lazy middleware initialization - middleware will be created on first use
_performance_middleware = None
_request_size_middleware = None
_rate_limit_middleware_loaded = False


def _get_performance_middleware():
    """Lazy initialization of performance middleware."""
    global _performance_middleware
    if _performance_middleware is None:
        PerformanceMonitoringMiddleware = _lazy_import_performance_middleware()
        _performance_middleware = PerformanceMonitoringMiddleware(app, enabled=True)
    return _performance_middleware


def _get_request_size_middleware():
    """Lazy initialization of request size middleware."""
    global _request_size_middleware
    if _request_size_middleware is None:
        _request_size_middleware = RequestSizeLimitMiddleware(app)
    return _request_size_middleware


# Add performance profiling middleware (lazy initialization)
@app.middleware("http")
async def performance_profiling_middleware(request: Request, call_next):
    middleware = _get_performance_middleware()
    return await middleware.dispatch(request, call_next)


# Add request size limit middleware (lazy initialization)
@app.middleware("http")
async def request_size_limit_middleware(request: Request, call_next):
    middleware = _get_request_size_middleware()
    return await middleware.dispatch(request, call_next)


# Add request ID middleware (must be first)
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    return await add_request_id_middleware(request, call_next)


# Middleware to disable service worker registration in Swagger UI
@app.middleware("http")
async def disable_swagger_service_worker_middleware(request: Request, call_next):
    """
    Inject JavaScript to prevent service worker registration in Swagger UI.
    This fixes the 'InvalidStateError: Failed to register a ServiceWorker' error.
    """
    response = await call_next(request)

    # Only modify responses from /docs endpoint (Swagger UI)
    if request.url.path == "/docs" and response.status_code == 200:
        # Check if response is HTML
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            # Read the response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Decode to string
            try:
                html_content = body.decode("utf-8")
            except UnicodeDecodeError:
                # If decoding fails, return original response
                import io

                from starlette.responses import StreamingResponse

                return StreamingResponse(
                    io.BytesIO(body),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=content_type,
                )

            # Inject script to disable service worker registration before closing </body> tag
            script = """
<script>
// Disable service worker registration to prevent InvalidStateError
if ('serviceWorker' in navigator) {
    // Override register method to prevent registration
    navigator.serviceWorker.register = function() {
        console.log('[Swagger UI] Service worker registration disabled to prevent errors');
        return Promise.reject(new Error('Service worker registration disabled'));
    };
    
    // Also unregister any existing service workers
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
            registration.unregister();
        }
    });
}
</script>
"""
            # Insert script before </body> tag
            body_tag = "</body>"
            if body_tag in html_content:
                html_content = html_content.replace(body_tag, script + body_tag, 1)
                # Create new response with modified content
                from fastapi.responses import HTMLResponse

                # Copy headers but exclude content-length since we're changing the body size
                headers = {
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() != "content-length"
                }
                return HTMLResponse(
                    content=html_content,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=content_type,
                )
            else:
                # If no body_tag found, return original response
                import io

                from starlette.responses import StreamingResponse

                return StreamingResponse(
                    io.BytesIO(body),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=content_type,
                )

    return response


# Add response caching middleware (after request ID, before rate limiting)
@app.middleware("http")
async def api_response_cache_middleware(request: Request, call_next):
    _, response_cache_middleware = _lazy_import_response_cache()
    return await response_cache_middleware(request, call_next)


# Lazy rate limiting middleware initialization
def _initialize_rate_limiting():
    """Lazy initialization of rate limiting middleware."""
    global _rate_limit_middleware_loaded
    if _rate_limit_middleware_loaded:
        return

    try:
        from .rate_limiting_enhanced import RateLimitMiddleware

        app.add_middleware(
            RateLimitMiddleware,
            skip_paths=["/health", "/api/health", "/", "/docs", "/openapi.json"],
        )
        logger.info("Enhanced rate limiting middleware enabled")
        _rate_limit_middleware_loaded = True
    except ImportError:
        logger.warning(
            "Enhanced rate limiting not available, using basic rate limiting"
        )
        # Fallback to basic rate limiting
        from .rate_limiting import rate_limit_middleware

        @app.middleware("http")
        async def basic_rate_limit_middleware(request: Request, call_next):
            return await rate_limit_middleware(request, call_next)

        _rate_limit_middleware_loaded = True


# Add CORS middleware (essential, load immediately)
# Configure CORS with security best practices
# For production, replace ["*"] with specific allowed origins
allowed_origins = (
    os.getenv(
        "CORS_ALLOWED_ORIGINS", "*"  # Default to all for local development
    ).split(",")
    if os.getenv("CORS_ALLOWED_ORIGINS")
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
        "X-RateLimit-Remaining",
        "X-RateLimit-Limit",
        "X-RateLimit-Reset",
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Initialize middleware before app starts (must be done before startup_event)
# Initialize validation optimization middleware
try:
    from .validation_middleware import setup_validation_optimization

    setup_validation_optimization(app)
    logger.info("Validation optimization initialized")
except Exception as e:
    logger.warning(f"Failed to initialize validation optimization: {e}")

# Initialize rate limiting middleware
_initialize_rate_limiting()

# Add compression middleware for large responses (lazy initialization)
_compression_middleware_loaded = False


def _initialize_compression_middleware():
    """Lazy initialization of compression middleware."""
    global _compression_middleware_loaded
    if not _compression_middleware_loaded:
        CompressionMiddleware = _lazy_import_compression_middleware()
        app.add_middleware(CompressionMiddleware, min_size=1024)
        _compression_middleware_loaded = True


# Register exception handlers
# Note: VoiceStudioException is a subclass of HTTPException, so it's handled by http_exception_handler
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Lazy route registration function
def _register_all_routes():
    """Register all routes lazily during startup."""
    global _ROUTES_LOADED
    if _ROUTES_LOADED:
        return

    logger.info("Loading routes (lazy initialization)...")
    start_time = time.time()

    # Import routes lazily - batch import for better performance
    # Routes are imported in a single batch to minimize import overhead
    try:
        from .routes import (
            adr,
            advanced_settings,
            ai_production_assistant,
            analytics,
            api_key_manager,
            articulation,
            assistant,
            assistant_run,
            audio,
            audio_analysis,
            audio_audit,
            auth,
            automation,
            backup,
            batch,
            dataset,
            deepfake_creator,
            docs,
            dubbing,
            effects,
            embedding_explorer,
            emotion,
            engine,
            engine_audit,
            engines,
            ensemble,
            eval_abx,
            formant,
            gpu_status,
            granular,
            health,
            help,
            image_gen,
            image_search,
            img_sampler,
            jobs,
            lexicon,
            library,
            macros,
            markers,
            mcp_dashboard,
            mix_scene,
            mixer,
            ml_optimization,
            model_inspect,
            models,
            monitoring,
            multi_voice_generator,
            nr,
            pdf,
            plugins,
            presets,
            profiles,
            projects,
            prosody,
            quality,
            quality_pipelines,
            realtime_converter,
            realtime_visualizer,
            recording,
            repair,
            reward,
            rvc,
            safety,
            scenes,
            script_editor,
            settings,
            shortcuts,
            sonography,
            spatial_audio,
            spectral,
            ssml,
            style_transfer,
            tags,
            templates,
            text_highlighting,
            text_speech_editor,
            todo_panel,
            tracks,
            training,
            training_audit,
            transcribe,
            ultimate_dashboard,
            upscaling,
            video_edit,
            video_gen,
            voice,
            voice_cloning_wizard,
            voice_speech,
            workflows,
        )
    except ImportError as e:
        logger.error(f"Failed to import routes: {e}")
        _ROUTES_LOADED = True
        return

    # Authentication routes (must be early for dependency injection)
    app.include_router(auth.router)

    # Core routes (from skeleton)
    app.include_router(advanced_settings.router)
    app.include_router(lexicon.router)
    app.include_router(spatial_audio.router)
    app.include_router(style_transfer.router)
    app.include_router(embedding_explorer.router)
    app.include_router(voice.router)
    app.include_router(voice_speech.router)
    app.include_router(quality.router)
    app.include_router(quality_pipelines.router)

    # Management routes
    app.include_router(profiles.router)
    app.include_router(projects.router)
    app.include_router(tracks.router)
    app.include_router(audio.router)
    app.include_router(audio_audit.router)
    app.include_router(macros.router)
    app.include_router(workflows.router)
    app.include_router(models.router)
    app.include_router(effects.router)
    app.include_router(batch.router)
    app.include_router(transcribe.router)
    app.include_router(training.router)
    app.include_router(training_audit.router)
    app.include_router(mixer.router)
    app.include_router(ml_optimization.router)
    app.include_router(docs.router)
    app.include_router(health.router)
    app.include_router(monitoring.router)

    # Additional routes
    app.include_router(eval_abx.router)
    app.include_router(dataset.router)
    app.include_router(engine.router)
    app.include_router(engines.router)
    app.include_router(engine_audit.router)
    app.include_router(adr.router)
    app.include_router(prosody.router)
    app.include_router(emotion.router)
    app.include_router(formant.router)
    app.include_router(spectral.router)
    app.include_router(model_inspect.router)
    app.include_router(granular.router)
    app.include_router(gpu_status.router)
    app.include_router(rvc.router)
    app.include_router(dubbing.router)
    app.include_router(articulation.router)
    app.include_router(nr.router)
    app.include_router(repair.router)
    app.include_router(mix_scene.router)
    app.include_router(reward.router)
    app.include_router(safety.router)
    app.include_router(img_sampler.router)
    app.include_router(assistant_run.router)
    app.include_router(ai_production_assistant.router)
    app.include_router(image_gen.router)
    app.include_router(image_search.router)
    app.include_router(upscaling.router)
    app.include_router(deepfake_creator.router)
    app.include_router(todo_panel.router)
    app.include_router(ultimate_dashboard.router)
    app.include_router(mcp_dashboard.router)
    app.include_router(pdf.router)
    app.include_router(voice_cloning_wizard.router)
    app.include_router(multi_voice_generator.router)
    app.include_router(video_gen.router)
    app.include_router(video_edit.router)
    app.include_router(settings.router)
    app.include_router(recording.router)
    app.include_router(library.router)
    app.include_router(presets.router)
    app.include_router(help.router)
    app.include_router(shortcuts.router)
    app.include_router(tags.router)
    app.include_router(backup.router)
    app.include_router(jobs.router)
    app.include_router(templates.router)
    app.include_router(automation.router)
    app.include_router(scenes.router)
    app.include_router(script_editor.router)
    app.include_router(markers.router)
    app.include_router(audio_analysis.router)
    app.include_router(ensemble.router)
    app.include_router(ssml.router)
    app.include_router(realtime_converter.router)
    app.include_router(text_highlighting.router)
    app.include_router(sonography.router)
    app.include_router(realtime_visualizer.router)
    app.include_router(text_speech_editor.router)
    app.include_router(assistant.router)
    app.include_router(api_key_manager.router)
    app.include_router(plugins.router)
    app.include_router(analytics.router)

    load_time = (time.time() - start_time) * 1000
    logger.info(f"Routes loaded in {load_time:.2f}ms")
    _ROUTES_LOADED = True
    logger.debug(f"Total routes registered: {len(app.routes)}")


@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    """Legacy WebSocket endpoint (heartbeat only)."""
    from .ws import events

    await events.stream(ws)


@app.websocket("/ws/realtime")
async def ws_realtime(ws: WebSocket, topics: Optional[str] = None):
    """
    Enhanced WebSocket endpoint for real-time updates.

    Query parameters:
    - topics: Comma-separated list of topics (meters, training, batch, general)
    """
    from .ws import realtime

    topic_list = topics.split(",") if topics else None
    await realtime.connect(ws, topic_list)


@app.get("/")
def root():
    """Root endpoint with version information."""
    version_info = get_version_info()
    return {
        "message": "VoiceStudio Backend API",
        "version": version_info["version"],
        "version_string": get_version_string(),
        "build_date": version_info.get("build_date"),
        "git_commit": version_info.get("git_commit"),
    }


@app.get("/health")
def health():
    """Basic health check endpoint."""
    return {"status": "ok", "version": "1.0"}


@app.get("/api/health")
def api_health():
    """API health check endpoint with performance metrics."""
    import os

    try:
        # Get system metrics
        import psutil  # type: ignore

        process = psutil.Process(os.getpid())  # type: ignore
        memory_info = process.memory_info()  # type: ignore
        cpu_percent = process.cpu_percent(interval=0.1)  # type: ignore

        middleware = _get_performance_middleware()
        version_info = get_version_info()
        return {
            "status": "ok",
            "version": version_info["version"],
            "version_string": get_version_string(),
            "version_info": version_info,
            "metrics": {
                "memory_mb": memory_info.rss / (1024 * 1024),
                "cpu_percent": cpu_percent,
                "request_count": getattr(middleware, "_request_count", 0),
                "slow_request_count": getattr(middleware, "_slow_request_count", 0),
            },
        }
    except Exception as e:
        logger.warning(f"Failed to get health metrics: {e}")
        version_info = get_version_info()
        return {
            "status": "ok",
            "version": version_info["version"],
            "version_string": get_version_string(),
            "metrics": "unavailable",
        }


@app.get("/api/cache/stats")
def cache_stats():
    """Get response cache statistics."""
    get_response_cache, _ = _lazy_import_response_cache()
    cache = get_response_cache()
    return cache.get_stats()


@app.post("/api/cache/clear")
def clear_cache():
    """Clear all response cache entries."""
    get_response_cache, _ = _lazy_import_response_cache()
    cache = get_response_cache()
    count = len(cache._cache)
    cache.clear()
    return {"message": "Cache cleared", "entries_cleared": count}


@app.get("/api/profiler/stats")
def profiler_stats():
    """Get performance profiler statistics."""
    try:
        from app.core.monitoring.profiler import get_profiler

        profiler = get_profiler()
        return profiler.get_stats()
    except Exception as e:
        logger.warning(f"Failed to get profiler stats: {e}")
        return {"error": str(e)}


@app.get("/api/profiler/detailed")
def profiler_detailed():
    """Get detailed performance profiler statistics."""
    try:
        from app.core.monitoring.profiler import get_profiler

        profiler = get_profiler()
        return profiler.get_detailed_stats()
    except Exception as e:
        logger.warning(f"Failed to get detailed profiler stats: {e}")
        return {"error": str(e)}


@app.post("/api/profiler/reset")
def profiler_reset():
    """Reset performance profiler data."""
    try:
        from app.core.monitoring.profiler import get_profiler

        profiler = get_profiler()
        profiler.reset()
        return {"message": "Profiler reset successfully"}
    except Exception as e:
        logger.warning(f"Failed to reset profiler: {e}")
        return {"error": str(e)}


@app.get("/api/engines/metrics")
def engine_metrics():
    """Get engine performance metrics."""
    try:
        from app.core.engines.router import router

        return router.get_engine_performance_stats()
    except Exception as e:
        logger.warning(f"Failed to get engine metrics: {e}")
        return {"error": str(e)}


@app.get("/api/engines/metrics/{engine_name}")
def engine_metrics_detail(engine_name: str):
    """Get performance metrics for a specific engine."""
    try:
        from app.core.engines.performance_metrics import get_engine_metrics

        metrics = get_engine_metrics()
        return metrics.get_engine_stats(engine_name)
    except Exception as e:
        logger.warning(f"Failed to get engine metrics for {engine_name}: {e}")
        return {"error": str(e)}


@app.post("/api/engines/metrics/reset")
def engine_metrics_reset(engine_name: Optional[str] = None):
    """Reset engine performance metrics."""
    try:
        from app.core.engines.performance_metrics import get_engine_metrics

        metrics = get_engine_metrics()
        metrics.clear(engine_name)
        return {"message": f"Metrics reset for {engine_name or 'all engines'}"}
    except Exception as e:
        logger.warning(f"Failed to reset engine metrics: {e}")
        return {"error": str(e)}


@app.get("/api/endpoints/metrics")
def endpoint_metrics():
    """Get API endpoint performance metrics."""
    try:
        middleware = _get_performance_middleware()
        if middleware is None:
            return {"error": "Performance monitoring middleware not initialized"}
        return middleware.get_stats()
    except Exception as e:
        logger.warning(f"Failed to get endpoint metrics: {e}")
        return {"error": str(e)}


@app.get("/api/endpoints/metrics/{endpoint_key:path}")
def endpoint_metrics_detail(endpoint_key: str):
    """Get performance metrics for a specific endpoint."""
    try:
        middleware = _get_performance_middleware()
        if middleware is None:
            return {"error": "Performance monitoring middleware not initialized"}
        return middleware.get_metrics(endpoint_key)
    except Exception as e:
        logger.warning(f"Failed to get endpoint metrics for {endpoint_key}: {e}")
        return {"error": str(e)}


@app.post("/api/endpoints/metrics/reset")
def endpoint_metrics_reset():
    """Reset API endpoint performance metrics."""
    try:
        middleware = _get_performance_middleware()
        if middleware is None:
            return {"error": "Performance monitoring middleware not initialized"}
        middleware.reset()
        return {"message": "Endpoint metrics reset successfully"}
    except Exception as e:
        logger.warning(f"Failed to reset endpoint metrics: {e}")
        return {"error": str(e)}


@app.post("/api/cache/invalidate")
def invalidate_cache(
    pattern: Optional[str] = None,
    tags: Optional[str] = None,
    path_prefix: Optional[str] = None,
):
    """
    Invalidate cache entries by pattern, tags, or path prefix.

    Args:
        pattern: Pattern to match in cache key
        tags: Comma-separated list of tags to invalidate
        path_prefix: Path prefix to invalidate (e.g., "/api/profiles")
    """
    get_response_cache, _ = _lazy_import_response_cache()
    cache = get_response_cache()

    tag_list = tags.split(",") if tags else None
    if tag_list:
        tag_list = [tag.strip() for tag in tag_list]

    count = cache.invalidate(
        pattern=pattern,
        tags=tag_list,
        path_prefix=path_prefix,
    )

    return {
        "message": "Cache invalidated",
        "entries_invalidated": count,
        "pattern": pattern,
        "tags": tag_list,
        "path_prefix": path_prefix,
    }


@app.get("/api/validation/stats")
def validation_stats(model_name: Optional[str] = None):
    """Get validation statistics."""
    try:
        from .validation_optimizer import get_cache_stats, get_validation_stats

        stats = get_validation_stats(model_name)
        cache_stats = get_cache_stats()
        return {
            "validation_stats": stats,
            "cache_stats": cache_stats,
        }
    except Exception as e:
        logger.warning(f"Failed to get validation stats: {e}")
        return {"error": str(e)}


@app.post("/api/validation/cache/clear")
def validation_cache_clear():
    """Clear validation cache."""
    try:
        from .validation_optimizer import clear_schema_cache, clear_validation_cache

        clear_validation_cache()
        clear_schema_cache()
        return {"message": "Validation cache cleared successfully"}
    except Exception as e:
        logger.warning(f"Failed to clear validation cache: {e}")
        return {"error": str(e)}


@app.get("/api/scheduler/stats")
def scheduler_stats():
    """Get background task scheduler statistics."""
    try:
        from app.core.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()
        return scheduler.get_stats()
    except Exception as e:
        logger.warning(f"Failed to get scheduler stats: {e}")
        return {"error": str(e)}


@app.get("/api/scheduler/tasks")
def scheduler_tasks(status: Optional[str] = None, priority: Optional[str] = None):
    """List scheduled tasks."""
    try:
        from app.core.tasks.scheduler import TaskPriority, TaskStatus, get_scheduler

        scheduler = get_scheduler()

        # Parse filters
        status_filter = None
        if status:
            try:
                status_filter = TaskStatus[status.upper()]
            except KeyError:
                return {"error": f"Invalid status: {status}"}

        priority_filter = None
        if priority:
            try:
                priority_filter = TaskPriority[priority.upper()]
            except KeyError:
                return {"error": f"Invalid priority: {priority}"}

        tasks = scheduler.list_tasks(status=status_filter, priority=priority_filter)

        return {
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "priority": task.priority.name,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "scheduled_at": (
                        task.scheduled_at.isoformat() if task.scheduled_at else None
                    ),
                    "next_run": (task.next_run.isoformat() if task.next_run else None),
                    "last_run": (task.last_run.isoformat() if task.last_run else None),
                    "interval": task.interval,
                    "retry_count": task.retry_count,
                    "max_retries": task.max_retries,
                    "error": task.error,
                }
                for task in tasks
            ],
            "count": len(tasks),
        }
    except Exception as e:
        logger.warning(f"Failed to list scheduler tasks: {e}")
        return {"error": str(e)}


@app.get("/api/scheduler/tasks/{task_id}")
def scheduler_task_detail(task_id: str):
    """Get details for a specific task."""
    try:
        from app.core.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()
        task = scheduler.get_task(task_id)

        if not task:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Task not found")

        return {
            "id": task.id,
            "name": task.name,
            "priority": task.priority.name,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "scheduled_at": (
                task.scheduled_at.isoformat() if task.scheduled_at else None
            ),
            "next_run": task.next_run.isoformat() if task.next_run else None,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "interval": task.interval,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "error": task.error,
            "resource_requirements": task.resource_requirements,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Failed to get task details: {e}")
        return {"error": str(e)}


@app.post("/api/scheduler/tasks/{task_id}/cancel")
def scheduler_task_cancel(task_id: str):
    """Cancel a scheduled task."""
    try:
        from app.core.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()
        success = scheduler.cancel_task(task_id)

        if not success:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Task not found")

        return {"message": f"Task {task_id} cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Failed to cancel task: {e}")
        return {"error": str(e)}


# Load plugins and routes on application startup (lazy initialization)
@app.on_event("startup")
async def startup_event():
    """Load plugins and routes on application startup."""
    startup_start = time.time()

    # Initialize temp file manager and perform startup cleanup
    try:
        from app.core.utils.temp_file_manager import get_temp_file_manager

        temp_manager = get_temp_file_manager()
        temp_manager.cleanup_on_startup()
        logger.info("Temp file manager initialized and startup cleanup performed")
    except Exception as e:
        logger.warning(f"Failed to initialize temp file manager: {e}")

    try:
        # Initialize background task scheduler
        try:
            from app.core.tasks.scheduler import TaskPriority, get_scheduler

            scheduler = get_scheduler()
            scheduler.start()

            # Register periodic temp file cleanup task
            from app.core.utils.temp_file_manager import get_temp_file_manager

            temp_manager = get_temp_file_manager()

            def cleanup_temp_files():
                """Periodic temp file cleanup."""
                temp_manager.cleanup_old_files()
                temp_manager.cleanup_by_disk_space()

            scheduler.add_task(
                name="Temp File Cleanup",
                func=cleanup_temp_files,
                interval=temp_manager.cleanup_interval_seconds,
                priority=TaskPriority.LOW,
            )

            logger.info("Background task scheduler started")
        except Exception as e:
            logger.warning(f"Failed to initialize task scheduler: {e}")

        # Register all routes (lazy)
        _register_all_routes()

        # Load plugins after all routes are registered (lazy import)
        load_all_plugins = _lazy_import_plugins()
        plugin_count = load_all_plugins(app)
        logger.info(f"Loaded {plugin_count} plugin(s) on startup")

        startup_time = (time.time() - startup_start) * 1000
        logger.info(f"FastAPI startup completed in {startup_time:.2f}ms")
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    # Cleanup temp files on shutdown
    try:
        from app.core.utils.temp_file_manager import get_temp_file_manager

        temp_manager = get_temp_file_manager()
        temp_manager.cleanup_on_shutdown()
        logger.info("Temp file manager shutdown cleanup performed")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp files on shutdown: {e}")
    try:
        # Stop background task scheduler
        try:
            from app.core.tasks.scheduler import get_scheduler

            scheduler = get_scheduler()
            scheduler.stop()
            logger.info("Background task scheduler stopped")
        except Exception as e:
            logger.warning(f"Failed to stop task scheduler: {e}")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)
