#!/usr/bin/env python3
"""
VoiceStudio Service Discovery and Communication
Handles service registration, discovery, and inter-service communication.
"""

import json
import logging
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceInfo:
    """Service information structure"""
    service_id: str
    name: str
    host: str
    port: int
    health_endpoint: str
    status: str = "unknown"
    last_heartbeat: Optional[datetime] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ServiceRegistry:
    """Service registry for discovery and health monitoring"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.heartbeat_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self._lock = threading.Lock()
        self._running = False
        self._heartbeat_thread = None
        
    def register_service(self, service_info: ServiceInfo) -> bool:
        """Register a service"""
        with self._lock:
            self.services[service_info.service_id] = service_info
            logger.info(f"Registered service: {service_info.name} at {service_info.host}:{service_info.port}")
            return True
    
    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        with self._lock:
            if service_id in self.services:
                service = self.services.pop(service_id)
                logger.info(f"Unregistered service: {service.name}")
                return True
            return False
    
    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service information by ID"""
        with self._lock:
            return self.services.get(service_id)
    
    def get_services_by_name(self, name: str) -> List[ServiceInfo]:
        """Get all services with a specific name"""
        with self._lock:
            return [service for service in self.services.values() if service.name == name]
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        with self._lock:
            return list(self.services.values())
    
    def check_service_health(self, service: ServiceInfo) -> bool:
        """Check if a service is healthy"""
        try:
            url = f"http://{service.host}:{service.port}{service.health_endpoint}"
            response = requests.get(url, timeout=self.health_check_timeout)
            is_healthy = response.status_code == 200
            
            with self._lock:
                service.status = "healthy" if is_healthy else "unhealthy"
                service.last_heartbeat = datetime.now()
            
            return is_healthy
        except Exception as e:
            logger.warning(f"Health check failed for {service.name}: {e}")
            with self._lock:
                service.status = "unhealthy"
                service.last_heartbeat = datetime.now()
            return False
    
    def start_heartbeat_monitoring(self):
        """Start heartbeat monitoring thread"""
        if self._running:
            return
        
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        logger.info("Started heartbeat monitoring")
    
    def stop_heartbeat_monitoring(self):
        """Stop heartbeat monitoring"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join()
        logger.info("Stopped heartbeat monitoring")
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        while self._running:
            try:
                services_to_check = self.get_all_services()
                for service in services_to_check:
                    self.check_service_health(service)
                
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)

class ServiceClient:
    """Client for inter-service communication"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.session = requests.Session()
        self.session.timeout = 10
    
    def call_service(self, service_name: str, endpoint: str, method: str = "GET", 
                    data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Call a service endpoint"""
        services = self.registry.get_services_by_name(service_name)
        if not services:
            logger.error(f"No services found with name: {service_name}")
            return None
        
        # Use the first healthy service
        healthy_services = [s for s in services if s.status == "healthy"]
        if not healthy_services:
            logger.error(f"No healthy services found with name: {service_name}")
            return None
        
        service = healthy_services[0]
        url = f"http://{service.host}:{service.port}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Service call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling service {service_name}: {e}")
            return None
    
    def get_service_status(self, service_name: str) -> Optional[Dict]:
        """Get status of a service"""
        return self.call_service(service_name, "/health")
    
    def discover_services(self) -> List[Dict]:
        """Discover all available services"""
        services = self.registry.get_all_services()
        return [asdict(service) for service in services]

# Global registry instance
service_registry = ServiceRegistry()
service_client = ServiceClient(service_registry)

def register_service(name: str, host: str = "127.0.0.1", port: int = None, 
                   health_endpoint: str = "/health", metadata: Dict = None) -> str:
    """Register a service with the registry"""
    service_id = str(uuid.uuid4())
    service_info = ServiceInfo(
        service_id=service_id,
        name=name,
        host=host,
        port=port,
        health_endpoint=health_endpoint,
        metadata=metadata or {}
    )
    
    service_registry.register_service(service_info)
    return service_id

def start_service_discovery():
    """Start the service discovery system"""
    service_registry.start_heartbeat_monitoring()
    logger.info("Service discovery system started")

def stop_service_discovery():
    """Stop the service discovery system"""
    service_registry.stop_heartbeat_monitoring()
    logger.info("Service discovery system stopped")

if __name__ == "__main__":
    # Example usage
    start_service_discovery()
    
    # Register some example services
    register_service("assistant", port=5080)
    register_service("orchestrator", port=5090)
    register_service("autofix", port=5081)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_service_discovery()
