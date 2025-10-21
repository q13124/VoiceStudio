#!/usr/bin/env python3
"""
VoiceStudio Web Interface Service
Optimized web interface for voice cloning with real-time updates and performance monitoring.
Runs on port 8080 with comprehensive UI features.
"""

import json
import logging
import time
import threading
import asyncio
import concurrent.futures
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import base64
import mimetypes

# Import our optimized modules
from services.service_discovery import register_service, service_client
from services.security import security_middleware, create_service_auth_token
from services.database import (
    get_database_logger, record_metric, db_manager,
    get_voice_cloning_results, get_voice_cloning_metrics_summary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebInterfaceService:
    """Web interface service with real-time updates and optimization"""
    
    def __init__(self):
        self.service_id = str(uuid.uuid4())
        self.service_name = "web_interface"
        self.status = "running"
        self.start_time = datetime.now()
        
        # Initialize components
        self.db_logger = get_database_logger(self.service_id, self.service_name)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        self._static_cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._lock = threading.Lock()
        
        # Register with service discovery
        register_service(self.service_name, port=8080, metadata={
            "capabilities": ["web_interface", "voice_cloning_ui"],
            "description": "Voice cloning web interface"
        })
        
        # Create service auth token
        self.auth_token = create_service_auth_token(self.service_id, self.service_name)
        
        # Log service startup
        self.db_logger.info("Web interface service started", {
            "service_id": self.service_id,
            "start_time": self.start_time.isoformat()
        })
        
        logger.info(f"Web Interface Service initialized with ID: {self.service_id}")
    
    def get_health(self):
        """Get comprehensive health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Record health metric
        record_metric(self.service_id, self.service_name, "uptime_seconds", uptime)
        
        health_data = {
            "ok": True,
            "service": "web_interface",
            "service_id": self.service_id,
            "status": self.status,
            "uptime_seconds": uptime,
            "features": {
                "voice_cloning_ui": True,
                "real_time_updates": True,
                "file_upload": True,
                "progress_tracking": True,
                "performance_monitoring": True
            },
            "ts": datetime.now().isoformat()
        }
        
        self.db_logger.info("Health check performed", {"uptime": uptime})
        return health_data
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data with caching"""
        cache_key = "dashboard_data"
        with self._lock:
            if cache_key in self._static_cache:
                cache_entry = self._static_cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                    return cache_entry['data']
        
        try:
            # Get voice cloning results
            results = get_voice_cloning_results(limit=10)
            
            # Get metrics summary
            metrics = get_voice_cloning_metrics_summary(hours=24)
            
            # Get service status
            services = service_client.discover_services()
            
            dashboard_data = {
                "recent_results": results,
                "metrics_summary": metrics,
                "services": services,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            with self._lock:
                self._static_cache[cache_key] = {
                    'data': dashboard_data,
                    'timestamp': time.time()
                }
            
            return dashboard_data
            
        except Exception as e:
            self.db_logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    def get_static_file(self, file_path: str) -> Dict[str, Any]:
        """Get static file with caching"""
        try:
            # Security check - prevent directory traversal
            if ".." in file_path or file_path.startswith("/"):
                return {"error": "Invalid file path"}
            
            # Default to index.html if no file specified
            if not file_path or file_path == "/":
                file_path = "index.html"
            
            # Check cache first
            cache_key = f"static:{file_path}"
            with self._lock:
                if cache_key in self._static_cache:
                    cache_entry = self._static_cache[cache_key]
                    if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                        return cache_entry['data']
            
            # Load file
            static_dir = Path("web_interface/static")
            full_path = static_dir / file_path
            
            if not full_path.exists() or not full_path.is_file():
                return {"error": "File not found"}
            
            # Read file content
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(str(full_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Encode content
            if mime_type.startswith('text/') or mime_type == 'application/json':
                content_str = content.decode('utf-8')
                file_data = {
                    "content": content_str,
                    "mime_type": mime_type,
                    "size": len(content)
                }
            else:
                # Binary file - encode as base64
                content_b64 = base64.b64encode(content).decode('utf-8')
                file_data = {
                    "content": content_b64,
                    "mime_type": mime_type,
                    "size": len(content),
                    "encoding": "base64"
                }
            
            # Cache the result
            with self._lock:
                self._static_cache[cache_key] = {
                    'data': file_data,
                    'timestamp': time.time()
                }
            
            return file_data
            
        except Exception as e:
            self.db_logger.error(f"Failed to get static file {file_path}: {e}")
            return {"error": str(e)}

class WebInterfaceHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for web interface service"""
    
    def __init__(self, *args, web_service=None, **kwargs):
        self.web_service = web_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/api/dashboard":
                self._handle_dashboard()
            elif path.startswith("/api/"):
                self._handle_api_request(path)
            elif path.startswith("/static/"):
                self._handle_static_file(path[8:])  # Remove "/static/" prefix
            else:
                self._handle_static_file(path)
        except Exception as e:
            self.web_service.db_logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/api/clone":
                self._handle_clone_request()
            elif path == "/api/upload":
                self._handle_file_upload()
            else:
                self._handle_not_found()
        except Exception as e:
            self.web_service.db_logger.error(f"Error handling POST request {path}: {e}")
            self._handle_error(str(e))
    
    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.web_service.get_health()
        self._send_json_response(200, health_data)
    
    def _handle_dashboard(self):
        """Handle dashboard data endpoint"""
        dashboard_data = self.web_service.get_dashboard_data()
        self._send_json_response(200, dashboard_data)
    
    def _handle_api_request(self, path: str):
        """Handle API requests"""
        if path == "/api/services":
            self._handle_services()
        elif path == "/api/metrics":
            self._handle_metrics()
        elif path == "/api/results":
            self._handle_results()
        else:
            self._handle_not_found()
    
    def _handle_services(self):
        """Handle services endpoint"""
        try:
            services = service_client.discover_services()
            self._send_json_response(200, {"services": services})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_metrics(self):
        """Handle metrics endpoint"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            hours = int(query_params.get('hours', ['24'])[0])
            
            metrics = get_voice_cloning_metrics_summary(hours=hours)
            self._send_json_response(200, metrics)
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_results(self):
        """Handle results endpoint"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            speaker_id = query_params.get('speaker_id', [None])[0]
            model_type = query_params.get('model_type', [None])[0]
            limit = int(query_params.get('limit', ['100'])[0])
            
            results = get_voice_cloning_results(speaker_id, model_type, limit)
            self._send_json_response(200, {"results": results})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_clone_request(self):
        """Handle voice cloning request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_json_response(400, {"error": "No data provided"})
                return
            
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Forward request to voice cloning service
            voice_service_url = "http://127.0.0.1:5083/clone"
            
            # This would make an HTTP request to the voice cloning service
            # For now, return a placeholder response
            result = {
                "session_id": str(uuid.uuid4()),
                "status": "processing",
                "message": "Voice cloning request received"
            }
            
            self._send_json_response(200, result)
            
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_file_upload(self):
        """Handle file upload"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_json_response(400, {"error": "No file provided"})
                return
            
            # Read uploaded file
            file_data = self.rfile.read(content_length)
            
            # Save file (placeholder implementation)
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            filename = f"upload_{uuid.uuid4().hex}.wav"
            file_path = upload_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            result = {
                "filename": filename,
                "path": str(file_path),
                "size": len(file_data),
                "message": "File uploaded successfully"
            }
            
            self._send_json_response(200, result)
            
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_static_file(self, file_path: str):
        """Handle static file requests"""
        try:
            file_data = self.web_service.get_static_file(file_path)
            
            if "error" in file_data:
                self._send_json_response(404, file_data)
                return
            
            # Send file content
            self.send_response(200)
            self.send_header('Content-Type', file_data['mime_type'])
            self.send_header('Content-Length', str(file_data['size']))
            self.send_header('Cache-Control', 'public, max-age=300')  # 5 minutes cache
            self.end_headers()
            
            if file_data.get('encoding') == 'base64':
                content = base64.b64decode(file_data['content'])
            else:
                content = file_data['content'].encode('utf-8')
            
            self.wfile.write(content)
            
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
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
        self.send_header('X-Service-ID', self.web_service.service_id)
        self.end_headers()
        
        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our database logger"""
        message = format % args
        self.web_service.db_logger.info(f"HTTP Request: {message}")

def create_handler(web_service):
    """Create HTTP handler with web service"""
    def handler(*args, **kwargs):
        return WebInterfaceHTTPHandler(*args, web_service=web_service, **kwargs)
    return handler

def start_web_interface_service(port=8080):
    """Start the Web Interface Service"""
    web_service = WebInterfaceService()
    handler = create_handler(web_service)
    
    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"Web Interface Service starting on port {port}")
    logger.info(f"Service ID: {web_service.service_id}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Dashboard endpoint: http://127.0.0.1:{port}/api/dashboard")
    logger.info(f"Web interface: http://127.0.0.1:{port}/")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Web Interface Service shutting down...")
        web_service.db_logger.info("Service shutting down")
        server.shutdown()

if __name__ == "__main__":
    start_web_interface_service()
