#!/usr/bin/env python3
"""
VoiceStudio Orchestrator Service
Coordinates between different VoiceStudio services and manages workflow orchestration.
Runs on port 5090 with health, settings, and weights endpoints.
"""

import json
import logging
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorService:
    """Core orchestrator service logic"""
    
    def __init__(self):
        self.status = "running"
        self.start_time = datetime.now()
        self.services = {
            "assistant": {"port": 5080, "status": "unknown"},
            "autofix": {"port": 5081, "status": "unknown"}
        }
        self.settings = {
            "max_concurrent_requests": 100,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "log_level": "INFO"
        }
        self.weights = {
            "model_version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "models": {
                "speech_recognition": {"weight": 0.8, "enabled": True},
                "text_processing": {"weight": 0.7, "enabled": True},
                "voice_synthesis": {"weight": 0.9, "enabled": True}
            }
        }
        
    def get_health(self):
        """Get service health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "ok": True,
            "service": "orchestrator",
            "status": self.status,
            "uptime_seconds": uptime,
            "managed_services": len(self.services),
            "ts": datetime.now().isoformat()
        }
    
    def get_settings(self):
        """Get service settings"""
        return {
            "settings": self.settings,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_weights(self):
        """Get model weights configuration"""
        return {
            "weights": self.weights,
            "last_updated": datetime.now().isoformat()
        }

class OrchestratorHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Orchestrator Service"""
    
    def __init__(self, *args, orchestrator_service=None, **kwargs):
        self.orchestrator_service = orchestrator_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/settings":
                self._handle_settings()
            elif path == "/weights":
                self._handle_weights()
            else:
                self._handle_not_found()
        except Exception as e:
            logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.orchestrator_service.get_health()
        self._send_json_response(200, health_data)
    
    def _handle_settings(self):
        """Handle settings endpoint"""
        settings_data = self.orchestrator_service.get_settings()
        self._send_json_response(200, settings_data)
    
    def _handle_weights(self):
        """Handle weights endpoint"""
        weights_data = self.orchestrator_service.get_weights()
        self._send_json_response(200, weights_data)
    
    def _handle_not_found(self):
        """Handle 404 errors"""
        self._send_json_response(404, {"error": "Not Found", "path": self.path})
    
    def _handle_error(self, error_message):
        """Handle server errors"""
        self._send_json_response(500, {"error": "Internal Server Error", "message": error_message})
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def create_handler(orchestrator_service):
    """Create HTTP handler with orchestrator service"""
    def handler(*args, **kwargs):
        return OrchestratorHTTPHandler(*args, orchestrator_service=orchestrator_service, **kwargs)
    return handler

def start_orchestrator_service(port=5090):
    """Start the Orchestrator Service"""
    orchestrator_service = OrchestratorService()
    handler = create_handler(orchestrator_service)
    
    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"Orchestrator Service starting on port {port}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Settings endpoint: http://127.0.0.1:{port}/settings")
    logger.info(f"Weights endpoint: http://127.0.0.1:{port}/weights")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Orchestrator Service shutting down...")
        server.shutdown()

if __name__ == "__main__":
    start_orchestrator_service()
