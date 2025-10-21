#!/usr/bin/env python3
"""
VoiceStudio ML Model Optimization Service
Advanced model management with caching, optimization, and performance monitoring.
Runs on port 5084 with comprehensive model lifecycle management.
"""

import json
import logging
import time
import threading
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import numpy as np
import psutil
import gc
from functools import lru_cache
import pickle
import hashlib

# Import our optimized modules
from services.service_discovery import register_service, service_client
from services.security import security_middleware, create_service_auth_token
from services.database import (
    get_database_logger, record_metric, db_manager,
    record_voice_cloning_metric
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelCache:
    """Advanced model caching system with memory management"""
    
    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.models = {}
        self.model_metadata = {}
        self.access_times = {}
        self.model_sizes = {}
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._running = False
    
    def start_cleanup_thread(self):
        """Start background cleanup thread"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("Model cache cleanup thread started")
    
    def stop_cleanup_thread(self):
        """Stop cleanup thread"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join()
        logger.info("Model cache cleanup thread stopped")
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self._running:
            try:
                self._cleanup_memory()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(10)
    
    def _cleanup_memory(self):
        """Clean up memory based on usage"""
        with self._lock:
            current_memory = self._get_total_memory_usage()
            
            if current_memory > self.max_memory_bytes:
                logger.info(f"Memory usage {current_memory / 1024**3:.2f}GB exceeds limit {self.max_memory_bytes / 1024**3:.2f}GB")
                
                # Remove least recently used models
                sorted_models = sorted(
                    self.access_times.items(),
                    key=lambda x: x[1]
                )
                
                for model_id, _ in sorted_models:
                    if current_memory <= self.max_memory_bytes * 0.8:  # Stop at 80% usage
                        break
                    
                    self._remove_model(model_id)
                    current_memory = self._get_total_memory_usage()
    
    def _get_total_memory_usage(self) -> int:
        """Get total memory usage of cached models"""
        total_size = 0
        for model_id in self.models:
            if model_id in self.model_sizes:
                total_size += self.model_sizes[model_id]
        return total_size
    
    def _remove_model(self, model_id: str):
        """Remove model from cache"""
        if model_id in self.models:
            del self.models[model_id]
            if model_id in self.model_metadata:
                del self.model_metadata[model_id]
            if model_id in self.access_times:
                del self.access_times[model_id]
            if model_id in self.model_sizes:
                del self.model_sizes[model_id]
            
            # Force garbage collection
            gc.collect()
            logger.info(f"Removed model {model_id} from cache")
    
    def store_model(self, model_id: str, model: Any, metadata: Dict[str, Any] = None):
        """Store model in cache"""
        with self._lock:
            # Calculate model size (approximate)
            try:
                model_size = self._estimate_model_size(model)
            except:
                model_size = 1024 * 1024  # Default 1MB estimate
            
            self.models[model_id] = model
            self.model_metadata[model_id] = metadata or {}
            self.access_times[model_id] = time.time()
            self.model_sizes[model_id] = model_size
            
            logger.info(f"Stored model {model_id} in cache (size: {model_size / 1024**2:.2f}MB)")
    
    def get_model(self, model_id: str) -> Optional[Any]:
        """Get model from cache"""
        with self._lock:
            if model_id in self.models:
                self.access_times[model_id] = time.time()
                return self.models[model_id]
            return None
    
    def has_model(self, model_id: str) -> bool:
        """Check if model exists in cache"""
        with self._lock:
            return model_id in self.models
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        with self._lock:
            return self.model_metadata.get(model_id)
    
    def _estimate_model_size(self, model: Any) -> int:
        """Estimate model size in bytes"""
        try:
            # Try to get size using pickle
            pickled = pickle.dumps(model)
            return len(pickled)
        except:
            # Fallback estimation
            return 1024 * 1024  # 1MB default

class ModelOptimizer:
    """Model optimization and performance enhancement"""
    
    def __init__(self):
        self.optimization_cache = {}
        self._lock = threading.Lock()
    
    def optimize_model(self, model: Any, optimization_type: str = "inference") -> Any:
        """Optimize model for better performance"""
        try:
            # Create cache key
            model_hash = self._get_model_hash(model)
            cache_key = f"{model_hash}:{optimization_type}"
            
            with self._lock:
                if cache_key in self.optimization_cache:
                    return self.optimization_cache[cache_key]
            
            # Apply optimizations based on type
            if optimization_type == "inference":
                optimized_model = self._optimize_for_inference(model)
            elif optimization_type == "memory":
                optimized_model = self._optimize_for_memory(model)
            elif optimization_type == "speed":
                optimized_model = self._optimize_for_speed(model)
            else:
                optimized_model = model
            
            # Cache optimized model
            with self._lock:
                self.optimization_cache[cache_key] = optimized_model
            
            return optimized_model
            
        except Exception as e:
            logger.error(f"Model optimization failed: {e}")
            return model
    
    def _optimize_for_inference(self, model: Any) -> Any:
        """Optimize model for inference"""
        # Placeholder for actual optimization
        # This would integrate with frameworks like PyTorch, TensorFlow, etc.
        return model
    
    def _optimize_for_memory(self, model: Any) -> Any:
        """Optimize model for memory usage"""
        # Placeholder for memory optimization
        return model
    
    def _optimize_for_speed(self, model: Any) -> Any:
        """Optimize model for speed"""
        # Placeholder for speed optimization
        return model
    
    def _get_model_hash(self, model: Any) -> str:
        """Get hash of model for caching"""
        try:
            model_str = str(model)
            return hashlib.md5(model_str.encode()).hexdigest()
        except:
            return str(uuid.uuid4())

class ModelManager:
    """Advanced model manager with lifecycle management"""
    
    def __init__(self):
        self.model_cache = ModelCache()
        self.model_optimizer = ModelOptimizer()
        self.loaded_models = {}
        self.model_loaders = {}
        self._lock = threading.Lock()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # Initialize model loaders
        self._init_model_loaders()
        
        # Start cache cleanup
        self.model_cache.start_cleanup_thread()
    
    def _init_model_loaders(self):
        """Initialize model loaders for different model types"""
        self.model_loaders = {
            "gpt_sovits": self._load_gpt_sovits_model,
            "openvoice": self._load_openvoice_model,
            "coqui_xtts": self._load_coqui_xtts_model,
            "tortoise_tts": self._load_tortoise_tts_model,
            "rvc": self._load_rvc_model
        }
    
    def load_model(self, model_type: str, model_path: str = None, 
                   optimization: str = "inference") -> Dict[str, Any]:
        """Load model with optimization"""
        try:
            model_id = f"{model_type}:{model_path or 'default'}"
            
            # Check cache first
            if self.model_cache.has_model(model_id):
                logger.info(f"Loading model {model_id} from cache")
                model = self.model_cache.get_model(model_id)
                metadata = self.model_cache.get_model_metadata(model_id)
                
                return {
                    "model_id": model_id,
                    "model": model,
                    "metadata": metadata,
                    "loaded_from_cache": True,
                    "load_time": 0.0
                }
            
            # Load model
            start_time = time.time()
            
            if model_type in self.model_loaders:
                model = self.model_loaders[model_type](model_path)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            load_time = time.time() - start_time
            
            # Optimize model
            optimized_model = self.model_optimizer.optimize_model(model, optimization)
            
            # Create metadata
            metadata = {
                "model_type": model_type,
                "model_path": model_path,
                "load_time": load_time,
                "optimization": optimization,
                "loaded_at": datetime.now().isoformat(),
                "memory_usage": self._get_model_memory_usage(optimized_model)
            }
            
            # Cache model
            self.model_cache.store_model(model_id, optimized_model, metadata)
            
            # Track loaded models
            with self._lock:
                self.loaded_models[model_id] = {
                    "model": optimized_model,
                    "metadata": metadata,
                    "last_used": time.time()
                }
            
            logger.info(f"Loaded model {model_id} in {load_time:.2f}s")
            
            return {
                "model_id": model_id,
                "model": optimized_model,
                "metadata": metadata,
                "loaded_from_cache": False,
                "load_time": load_time
            }
            
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
            return {"error": str(e)}
    
    def unload_model(self, model_id: str) -> bool:
        """Unload model from memory"""
        try:
            with self._lock:
                if model_id in self.loaded_models:
                    del self.loaded_models[model_id]
            
            # Remove from cache
            self.model_cache._remove_model(model_id)
            
            # Force garbage collection
            gc.collect()
            
            logger.info(f"Unloaded model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_id}: {e}")
            return False
    
    def get_model_info(self, model_id: str = None) -> Dict[str, Any]:
        """Get model information"""
        with self._lock:
            if model_id:
                if model_id in self.loaded_models:
                    return self.loaded_models[model_id]["metadata"]
                else:
                    return {"error": "Model not found"}
            else:
                # Return all loaded models
                models_info = {}
                for mid, info in self.loaded_models.items():
                    models_info[mid] = info["metadata"]
                return models_info
    
    def _get_model_memory_usage(self, model: Any) -> int:
        """Get model memory usage"""
        try:
            return self.model_cache._estimate_model_size(model)
        except:
            return 0
    
    # Model loader methods (placeholders for actual implementations)
    def _load_gpt_sovits_model(self, model_path: str = None):
        """Load GPT-SoVITS model"""
        # Placeholder for actual GPT-SoVITS loading
        return f"gpt_sovits_model_{model_path or 'default'}"
    
    def _load_openvoice_model(self, model_path: str = None):
        """Load OpenVoice model"""
        # Placeholder for actual OpenVoice loading
        return f"openvoice_model_{model_path or 'default'}"
    
    def _load_coqui_xtts_model(self, model_path: str = None):
        """Load Coqui XTTS model"""
        # Placeholder for actual Coqui XTTS loading
        return f"coqui_xtts_model_{model_path or 'default'}"
    
    def _load_tortoise_tts_model(self, model_path: str = None):
        """Load Tortoise TTS model"""
        # Placeholder for actual Tortoise TTS loading
        return f"tortoise_tts_model_{model_path or 'default'}"
    
    def _load_rvc_model(self, model_path: str = None):
        """Load RVC model"""
        # Placeholder for actual RVC loading
        return f"rvc_model_{model_path or 'default'}"

class MLModelService:
    """ML Model optimization service with full integration"""
    
    def __init__(self):
        self.service_id = str(uuid.uuid4())
        self.service_name = "ml_model_optimizer"
        self.status = "running"
        self.start_time = datetime.now()
        
        # Initialize components
        self.db_logger = get_database_logger(self.service_id, self.service_name)
        self.model_manager = ModelManager()
        
        # Register with service discovery
        register_service(self.service_name, port=5084, metadata={
            "capabilities": ["model_management", "model_optimization", "memory_management"],
            "supported_models": ["gpt_sovits", "openvoice", "coqui_xtts", "tortoise_tts", "rvc"]
        })
        
        # Create service auth token
        self.auth_token = create_service_auth_token(self.service_id, self.service_name)
        
        # Log service startup
        self.db_logger.info("ML Model optimization service started", {
            "service_id": self.service_id,
            "start_time": self.start_time.isoformat()
        })
        
        logger.info(f"ML Model Optimization Service initialized with ID: {self.service_id}")
    
    def get_health(self):
        """Get comprehensive health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Record health metric
        record_metric(self.service_id, self.service_name, "uptime_seconds", uptime)
        
        # Get memory usage
        memory_info = psutil.virtual_memory()
        
        health_data = {
            "ok": True,
            "service": "ml_model_optimizer",
            "service_id": self.service_id,
            "status": self.status,
            "uptime_seconds": uptime,
            "features": {
                "model_management": True,
                "model_optimization": True,
                "memory_management": True,
                "caching": True,
                "performance_monitoring": True
            },
            "system_info": {
                "memory_total_gb": memory_info.total / 1024**3,
                "memory_available_gb": memory_info.available / 1024**3,
                "memory_percent": memory_info.percent,
                "cpu_count": psutil.cpu_count()
            },
            "ts": datetime.now().isoformat()
        }
        
        self.db_logger.info("Health check performed", {"uptime": uptime})
        return health_data
    
    def load_model(self, model_type: str, model_path: str = None, 
                   optimization: str = "inference") -> Dict[str, Any]:
        """Load model with optimization"""
        try:
            start_time = time.time()
            
            result = self.model_manager.load_model(model_type, model_path, optimization)
            
            load_time = time.time() - start_time
            
            # Record metrics
            record_voice_cloning_metric(
                self.service_id, "model_load_time", load_time,
                "performance", model_type=model_type
            )
            
            self.db_logger.info("Model loaded", {
                "model_type": model_type,
                "model_path": model_path,
                "load_time": load_time,
                "optimization": optimization
            })
            
            return result
            
        except Exception as e:
            self.db_logger.error(f"Failed to load model: {e}")
            return {"error": str(e)}
    
    def unload_model(self, model_id: str) -> Dict[str, Any]:
        """Unload model"""
        try:
            success = self.model_manager.unload_model(model_id)
            
            if success:
                self.db_logger.info("Model unloaded", {"model_id": model_id})
                return {"success": True, "message": "Model unloaded successfully"}
            else:
                return {"error": "Failed to unload model"}
                
        except Exception as e:
            self.db_logger.error(f"Failed to unload model: {e}")
            return {"error": str(e)}
    
    def get_model_info(self, model_id: str = None) -> Dict[str, Any]:
        """Get model information"""
        try:
            info = self.model_manager.get_model_info(model_id)
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_model(self, model_id: str, optimization_type: str) -> Dict[str, Any]:
        """Optimize existing model"""
        try:
            with self.model_manager._lock:
                if model_id not in self.model_manager.loaded_models:
                    return {"error": "Model not found"}
                
                model = self.model_manager.loaded_models[model_id]["model"]
            
            # Optimize model
            optimized_model = self.model_manager.model_optimizer.optimize_model(
                model, optimization_type
            )
            
            # Update loaded model
            with self.model_manager._lock:
                self.model_manager.loaded_models[model_id]["model"] = optimized_model
                self.model_manager.loaded_models[model_id]["metadata"]["optimization"] = optimization_type
            
            self.db_logger.info("Model optimized", {
                "model_id": model_id,
                "optimization_type": optimization_type
            })
            
            return {"success": True, "message": "Model optimized successfully"}
            
        except Exception as e:
            self.db_logger.error(f"Failed to optimize model: {e}")
            return {"error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            # Get system metrics
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get model cache metrics
            cache_memory = self.model_manager.model_cache._get_total_memory_usage()
            loaded_models_count = len(self.model_manager.loaded_models)
            
            metrics = {
                "system": {
                    "memory_total_gb": memory_info.total / 1024**3,
                    "memory_used_gb": memory_info.used / 1024**3,
                    "memory_percent": memory_info.percent,
                    "cpu_percent": cpu_percent
                },
                "models": {
                    "loaded_count": loaded_models_count,
                    "cache_memory_mb": cache_memory / 1024**2,
                    "max_cache_memory_gb": self.model_manager.model_cache.max_memory_bytes / 1024**3
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}

class MLModelHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ML model service"""
    
    def __init__(self, *args, ml_service=None, **kwargs):
        self.ml_service = ml_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/models":
                self._handle_models()
            elif path == "/performance":
                self._handle_performance()
            else:
                self._handle_not_found()
        except Exception as e:
            self.ml_service.db_logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/load":
                self._handle_load_model()
            elif path == "/unload":
                self._handle_unload_model()
            elif path == "/optimize":
                self._handle_optimize_model()
            else:
                self._handle_not_found()
        except Exception as e:
            self.ml_service.db_logger.error(f"Error handling POST request {path}: {e}")
            self._handle_error(str(e))
    
    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.ml_service.get_health()
        self._send_json_response(200, health_data)
    
    def _handle_models(self):
        """Handle models endpoint"""
        query_params = parse_qs(urlparse(self.path).query)
        model_id = query_params.get('model_id', [None])[0]
        
        result = self.ml_service.get_model_info(model_id)
        self._send_json_response(200, result)
    
    def _handle_performance(self):
        """Handle performance endpoint"""
        result = self.ml_service.get_performance_metrics()
        self._send_json_response(200, result)
    
    def _handle_load_model(self):
        """Handle load model endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return
        
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            model_type = data.get('model_type')
            model_path = data.get('model_path')
            optimization = data.get('optimization', 'inference')
            
            if not model_type:
                self._send_json_response(400, {"error": "model_type required"})
                return
            
            result = self.ml_service.load_model(model_type, model_path, optimization)
            self._send_json_response(200, result)
            
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
    
    def _handle_unload_model(self):
        """Handle unload model endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return
        
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            model_id = data.get('model_id')
            if not model_id:
                self._send_json_response(400, {"error": "model_id required"})
                return
            
            result = self.ml_service.unload_model(model_id)
            self._send_json_response(200, result)
            
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
    
    def _handle_optimize_model(self):
        """Handle optimize model endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return
        
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            model_id = data.get('model_id')
            optimization_type = data.get('optimization_type', 'inference')
            
            if not model_id:
                self._send_json_response(400, {"error": "model_id required"})
                return
            
            result = self.ml_service.optimize_model(model_id, optimization_type)
            self._send_json_response(200, result)
            
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
    
    def _handle_not_found(self):
        """Handle 404 errors"""
        self._send_json_response(404, {"error": "Not Found", "path": self.path})
    
    def _handle_error(self, error_message):
        """Handle server errors"""
        self._send_json_response(500, {"error": "Internal Server Error", "message": error_message})
    
    def _send_json_response(self, status_code, data):
        """Send JSON response with security headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Service-ID', self.ml_service.service_id)
        self.end_headers()
        
        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our database logger"""
        message = format % args
        self.ml_service.db_logger.info(f"HTTP Request: {message}")

def create_handler(ml_service):
    """Create HTTP handler with ML service"""
    def handler(*args, **kwargs):
        return MLModelHTTPHandler(*args, ml_service=ml_service, **kwargs)
    return handler

def start_ml_model_service(port=5084):
    """Start the ML Model Optimization Service"""
    ml_service = MLModelService()
    handler = create_handler(ml_service)
    
    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"ML Model Optimization Service starting on port {port}")
    logger.info(f"Service ID: {ml_service.service_id}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Models endpoint: http://127.0.0.1:{port}/models")
    logger.info(f"Performance endpoint: http://127.0.0.1:{port}/performance")
    logger.info(f"Load model endpoint: http://127.0.0.1:{port}/load")
    logger.info(f"Unload model endpoint: http://127.0.0.1:{port}/unload")
    logger.info(f"Optimize model endpoint: http://127.0.0.1:{port}/optimize")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("ML Model Optimization Service shutting down...")
        ml_service.db_logger.info("Service shutting down")
        ml_service.model_manager.model_cache.stop_cleanup_thread()
        server.shutdown()

if __name__ == "__main__":
    start_ml_model_service()
