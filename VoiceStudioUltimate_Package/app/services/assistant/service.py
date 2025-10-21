#!/usr/bin/env python3
"""
VoiceStudio Assistant Service
Handles AI/ML interactions and provides intelligent responses.
Runs on port 5080 with health and autofix endpoints.
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

class AssistantService:
    """Core assistant service logic"""
    
    def __init__(self):
        self.status = "running"
        self.start_time = datetime.now()
        self.autofix_enabled = True
        self.autofix_status = "active"
        
    def get_health(self):
        """Get service health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "ok": True,
            "service": "assistant",
            "status": self.status,
            "uptime_seconds": uptime,
            "ts": datetime.now().isoformat()
        }
    
    def get_autofix_status(self):
        """Get autofix service status"""
        return {
            "enabled": self.autofix_enabled,
            "status": self.autofix_status,
            "last_check": datetime.now().isoformat(),
            "features": [
                "error_detection",
                "code_repair",
                "service_monitoring"
            ]
        }

class AssistantHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Assistant Service"""
    
    def __init__(self, *args, assistant_service=None, **kwargs):
        self.assistant_service = assistant_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/autofix/status":
                self._handle_autofix_status()
            else:
                self._handle_not_found()
        except Exception as e:
            logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.assistant_service.get_health()
        self._send_json_response(200, health_data)
    
    def _handle_autofix_status(self):
        """Handle autofix status endpoint"""
        autofix_data = self.assistant_service.get_autofix_status()
        self._send_json_response(200, autofix_data)
    
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

def create_handler(assistant_service):
    """Create HTTP handler with assistant service"""
    def handler(*args, **kwargs):
        return AssistantHTTPHandler(*args, assistant_service=assistant_service, **kwargs)
    return handler

def start_assistant_service(port=5080):
    """Start the Assistant Service"""
    assistant_service = AssistantService()
    handler = create_handler(assistant_service)
    
    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"Assistant Service starting on port {port}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Autofix endpoint: http://127.0.0.1:{port}/autofix/status")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Assistant Service shutting down...")
        server.shutdown()

if __name__ == "__main__":
    start_assistant_service()
