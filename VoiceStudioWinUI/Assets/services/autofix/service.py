#!/usr/bin/env python3
"""
VoiceStudio Autofix Service
Provides automated debugging and repair capabilities for VoiceStudio.
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

class AutofixService:
    """Core autofix service logic"""
    
    def __init__(self):
        self.status = "running"
        self.start_time = datetime.now()
        self.features = {
            "error_detection": True,
            "code_repair": True,
            "service_monitoring": True,
            "performance_optimization": True
        }
        self.recent_fixes = []
        self.error_patterns = {
            "connection_timeout": "Increase timeout settings",
            "memory_leak": "Review object lifecycle management",
            "null_reference": "Add null checks before object access"
        }
        
    def get_status(self):
        """Get autofix service status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "ok": True,
            "service": "autofix",
            "status": self.status,
            "uptime_seconds": uptime,
            "features": self.features,
            "recent_fixes_count": len(self.recent_fixes),
            "ts": datetime.now().isoformat()
        }
    
    def analyze_error(self, error_type, error_message):
        """Analyze an error and suggest fixes"""
        suggestions = []
        
        for pattern, suggestion in self.error_patterns.items():
            if pattern in error_message.lower():
                suggestions.append({
                    "pattern": pattern,
                    "suggestion": suggestion,
                    "confidence": 0.8
                })
        
        if not suggestions:
            suggestions.append({
                "pattern": "unknown",
                "suggestion": "Review logs and check service configuration",
                "confidence": 0.3
            })
        
        fix_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "suggestions": suggestions
        }
        
        self.recent_fixes.append(fix_record)
        if len(self.recent_fixes) > 100:  # Keep only recent 100 fixes
            self.recent_fixes = self.recent_fixes[-100:]
        
        return fix_record

class AutofixHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Autofix Service"""
    
    def __init__(self, *args, autofix_service=None, **kwargs):
        self.autofix_service = autofix_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/status":
                self._handle_status()
            else:
                self._handle_not_found()
        except Exception as e:
            logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/analyze":
                self._handle_analyze()
            else:
                self._handle_not_found()
        except Exception as e:
            logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.autofix_service.get_status()
        self._send_json_response(200, health_data)
    
    def _handle_status(self):
        """Handle status endpoint"""
        status_data = self.autofix_service.get_status()
        self._send_json_response(200, status_data)
    
    def _handle_analyze(self):
        """Handle error analysis endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return
        
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            error_type = data.get('error_type', 'unknown')
            error_message = data.get('error_message', '')
            
            analysis = self.autofix_service.analyze_error(error_type, error_message)
            self._send_json_response(200, analysis)
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
    
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

def create_handler(autofix_service):
    """Create HTTP handler with autofix service"""
    def handler(*args, **kwargs):
        return AutofixHTTPHandler(*args, autofix_service=autofix_service, **kwargs)
    return handler

def start_autofix_service(port=5081):
    """Start the Autofix Service"""
    autofix_service = AutofixService()
    handler = create_handler(autofix_service)
    
    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"Autofix Service starting on port {port}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Status endpoint: http://127.0.0.1:{port}/status")
    logger.info(f"Analyze endpoint: http://127.0.0.1:{port}/analyze")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Autofix Service shutting down...")
        server.shutdown()

if __name__ == "__main__":
    start_autofix_service()
