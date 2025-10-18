#!/usr/bin/env python3
"""
Enhanced VoiceStudio Assistant Service
Integrates service discovery, authentication, database logging, and autofix capabilities.
Runs on port 5080 with comprehensive API endpoints.
"""

import json
import logging
import time
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid

# Import our custom modules
from services.service_discovery import register_service, service_client
from services.security import security_middleware, create_service_auth_token
from services.database import get_database_logger, record_metric, db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAssistantService:
    """Enhanced assistant service with full integration"""
    
    def __init__(self):
        self.service_id = str(uuid.uuid4())
        self.service_name = "assistant"
        self.status = "running"
        self.start_time = datetime.now()
        self.autofix_enabled = True
        self.autofix_status = "active"
        
        # Initialize database logger
        self.db_logger = get_database_logger(self.service_id, self.service_name)
        
        # Register with service discovery
        register_service(self.service_name, port=5080)
        
        # Create service auth token
        self.auth_token = create_service_auth_token(self.service_id, self.service_name)
        
        # Log service startup
        self.db_logger.info("Assistant service started", {
            "service_id": self.service_id,
            "start_time": self.start_time.isoformat()
        })
        
        logger.info(f"Enhanced Assistant Service initialized with ID: {self.service_id}")
    
    def get_health(self):
        """Get comprehensive health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Record health metric
        record_metric(self.service_id, self.service_name, "uptime_seconds", uptime)
        
        health_data = {
            "ok": True,
            "service": "assistant",
            "service_id": self.service_id,
            "status": self.status,
            "uptime_seconds": uptime,
            "features": {
                "autofix": self.autofix_enabled,
                "service_discovery": True,
                "authentication": True,
                "database_logging": True
            },
            "ts": datetime.now().isoformat()
        }
        
        self.db_logger.info("Health check performed", {"uptime": uptime})
        return health_data
    
    def get_autofix_status(self):
        """Get detailed autofix service status"""
        # Check if autofix service is available
        autofix_status = service_client.get_service_status("autofix")
        
        autofix_data = {
            "enabled": self.autofix_enabled,
            "status": self.autofix_status,
            "last_check": datetime.now().isoformat(),
            "features": [
                "error_detection",
                "code_repair", 
                "service_monitoring",
                "performance_optimization"
            ],
            "autofix_service_status": autofix_status,
            "service_id": self.service_id
        }
        
        self.db_logger.info("Autofix status checked", {"autofix_available": autofix_status is not None})
        return autofix_data
    
    def analyze_error(self, error_data: dict):
        """Analyze error using autofix service"""
        try:
            # Call autofix service for analysis
            analysis = service_client.call_service(
                "autofix", "/analyze", "POST", error_data
            )
            
            if analysis:
                self.db_logger.info("Error analysis completed", {
                    "error_type": error_data.get("error_type"),
                    "analysis_id": analysis.get("timestamp")
                })
                return analysis
            else:
                # Fallback analysis if autofix service unavailable
                fallback_analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "error_type": error_data.get("error_type", "unknown"),
                    "error_message": error_data.get("error_message", ""),
                    "suggestions": [{
                        "pattern": "fallback",
                        "suggestion": "Check service logs and configuration",
                        "confidence": 0.5
                    }],
                    "source": "assistant_fallback"
                }
                
                self.db_logger.warning("Autofix service unavailable, used fallback analysis")
                return fallback_analysis
                
        except Exception as e:
            self.db_logger.error(f"Error analysis failed: {e}")
            return {"error": "Analysis failed", "message": str(e)}
    
    def get_service_discovery_info(self):
        """Get service discovery information"""
        services = service_client.discover_services()
        
        discovery_data = {
            "registered_services": len(services),
            "services": services,
            "assistant_service_id": self.service_id,
            "timestamp": datetime.now().isoformat()
        }
        
        return discovery_data
    
    def get_service_metrics(self):
        """Get service performance metrics"""
        # Get metrics from database
        metrics = db_manager.get_service_metrics(self.service_id, limit=50)
        
        metrics_data = {
            "service_id": self.service_id,
            "metrics_count": len(metrics),
            "recent_metrics": [
                {
                    "metric_name": m.metric_name,
                    "metric_value": m.metric_value,
                    "timestamp": m.timestamp.isoformat(),
                    "tags": m.tags
                } for m in metrics[:10]
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics_data

class EnhancedAssistantHTTPHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP request handler with authentication and logging"""
    
    def __init__(self, *args, assistant_service=None, **kwargs):
        self.assistant_service = assistant_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests with authentication"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Authenticate request
        user = security_middleware.authenticate_request(dict(self.headers))
        
        try:
            if path == "/health":
                self._handle_health()
            elif path == "/autofix/status":
                self._handle_autofix_status()
            elif path == "/discovery":
                if not user:
                    self._handle_unauthorized()
                    return
                self._handle_service_discovery()
            elif path == "/metrics":
                if not user:
                    self._handle_unauthorized()
                    return
                self._handle_metrics()
            elif path == "/auth/login":
                self._handle_auth_login()
            else:
                self._handle_not_found()
        except Exception as e:
            self.assistant_service.db_logger.error(f"Error handling request {path}: {e}")
            self._handle_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Authenticate request
        user = security_middleware.authenticate_request(dict(self.headers))
        
        try:
            if path == "/autofix/analyze":
                if not user:
                    self._handle_unauthorized()
                    return
                self._handle_error_analysis()
            else:
                self._handle_not_found()
        except Exception as e:
            self.assistant_service.db_logger.error(f"Error handling POST request {path}: {e}")
            self._handle_error(str(e))
    
    def _handle_health(self):
        """Handle health check endpoint"""
        health_data = self.assistant_service.get_health()
        self._send_json_response(200, health_data)
    
    def _handle_autofix_status(self):
        """Handle autofix status endpoint"""
        autofix_data = self.assistant_service.get_autofix_status()
        self._send_json_response(200, autofix_data)
    
    def _handle_service_discovery(self):
        """Handle service discovery endpoint"""
        discovery_data = self.assistant_service.get_service_discovery_info()
        self._send_json_response(200, discovery_data)
    
    def _handle_metrics(self):
        """Handle metrics endpoint"""
        metrics_data = self.assistant_service.get_service_metrics()
        self._send_json_response(200, metrics_data)
    
    def _handle_error_analysis(self):
        """Handle error analysis endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "No data provided"})
            return
        
        post_data = self.rfile.read(content_length)
        try:
            error_data = json.loads(post_data.decode('utf-8'))
            analysis = self.assistant_service.analyze_error(error_data)
            self._send_json_response(200, analysis)
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
    
    def _handle_auth_login(self):
        """Handle authentication login"""
        # Simple API key authentication for demo
        api_key = self.headers.get('X-API-Key')
        if api_key:
            user = security_middleware.security_manager.authenticate_api_key(api_key)
            if user:
                auth_response = security_middleware.create_auth_response(user)
                self._send_json_response(200, auth_response)
            else:
                self._send_json_response(401, {"error": "Invalid API key"})
        else:
            self._send_json_response(400, {"error": "API key required"})
    
    def _handle_unauthorized(self):
        """Handle unauthorized requests"""
        self._send_json_response(401, {"error": "Unauthorized", "message": "Authentication required"})
    
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
        self.send_header('X-Service-ID', self.assistant_service.service_id)
        self.end_headers()
        
        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our database logger"""
        message = format % args
        self.assistant_service.db_logger.info(f"HTTP Request: {message}")

def create_handler(assistant_service):
    """Create HTTP handler with assistant service"""
    def handler(*args, **kwargs):
        return EnhancedAssistantHTTPHandler(*args, assistant_service=assistant_service, **kwargs)
    return handler

def start_enhanced_assistant_service(port=5080):
    """Start the Enhanced Assistant Service"""
    assistant_service = EnhancedAssistantService()
    handler = create_handler(assistant_service)
    
    server = HTTPServer(('127.0.0.1', port), handler)
    logger.info(f"Enhanced Assistant Service starting on port {port}")
    logger.info(f"Service ID: {assistant_service.service_id}")
    logger.info(f"Health endpoint: http://127.0.0.1:{port}/health")
    logger.info(f"Autofix endpoint: http://127.0.0.1:{port}/autofix/status")
    logger.info(f"Discovery endpoint: http://127.0.0.1:{port}/discovery")
    logger.info(f"Metrics endpoint: http://127.0.0.1:{port}/metrics")
    logger.info(f"Auth endpoint: http://127.0.0.1:{port}/auth/login")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Enhanced Assistant Service shutting down...")
        assistant_service.db_logger.info("Service shutting down")
        server.shutdown()

if __name__ == "__main__":
    start_enhanced_assistant_service()
