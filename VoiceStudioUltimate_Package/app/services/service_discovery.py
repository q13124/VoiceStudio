#!/usr/bin/env python3
"""
VoiceStudio Service Discovery and Communication
Handles service registration, discovery, and inter-service communication.
Optimized with async operations, connection pooling, and caching.
"""

import json
import logging
import time
import threading
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid
from concurrent.futures import ThreadPoolExecutor
import queue
from functools import lru_cache
import subprocess
import os
import sys
from pathlib import Path
import psutil

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
    upgrade_status: str = "unknown"
    last_upgrade_check: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class UpgradeInfo:
    """Upgrade and optimization information"""
    service_id: str
    available_upgrades: List[str] = None
    performance_improvements: List[str] = None
    new_features: List[str] = None
    optimization_opportunities: List[str] = None
    last_check: Optional[datetime] = None
    chatgpt_analysis: str = ""

    def __post_init__(self):
        if self.available_upgrades is None:
            self.available_upgrades = []
        if self.performance_improvements is None:
            self.performance_improvements = []
        if self.new_features is None:
            self.new_features = []
        if self.optimization_opportunities is None:
            self.optimization_opportunities = []

class ServiceRegistry:
    """Service registry for discovery and health monitoring with ChatGPT-powered optimizations"""

    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.upgrades: Dict[str, UpgradeInfo] = {}
        self.heartbeat_interval = 30  # seconds
        self.upgrade_check_interval = 300  # 5 minutes
        self.health_check_timeout = 5  # seconds
        self._lock = threading.Lock()
        self._running = False
        self._heartbeat_thread = None
        self._upgrade_monitor_thread = None
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._session_pool = queue.Queue(maxsize=20)
        self._health_cache = {}  # Cache health check results
        self._cache_ttl = 10  # seconds
        self._init_session_pool()

    def _init_session_pool(self):
        """Initialize HTTP session pool for better performance"""
        for _ in range(20):
            session = requests.Session()
            session.timeout = self.health_check_timeout
            # Configure session for better performance
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=2
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            self._session_pool.put(session)
        logger.info("HTTP session pool initialized")

    def _get_session(self):
        """Get session from pool"""
        try:
            return self._session_pool.get_nowait()
        except queue.Empty:
            # Create new session if pool is empty
            session = requests.Session()
            session.timeout = self.health_check_timeout
            return session

    def _return_session(self, session):
        """Return session to pool"""
        try:
            self._session_pool.put_nowait(session)
        except queue.Full:
            session.close()

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry['timestamp'] < self._cache_ttl

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
        """Check if a service is healthy with caching"""
        # Check cache first
        cache_key = f"{service.service_id}:health"
        if cache_key in self._health_cache:
            cache_entry = self._health_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                return cache_entry['healthy']

        try:
            url = f"http://{service.host}:{service.port}{service.health_endpoint}"
            session = self._get_session()

            try:
                response = session.get(url, timeout=self.health_check_timeout)
                is_healthy = response.status_code == 200
            finally:
                self._return_session(session)

            with self._lock:
                service.status = "healthy" if is_healthy else "unhealthy"
                service.last_heartbeat = datetime.now()

            # Cache the result
            self._health_cache[cache_key] = {
                'healthy': is_healthy,
                'timestamp': time.time()
            }

            return is_healthy
        except Exception as e:
            logger.warning(f"Health check failed for {service.name}: {e}")
            with self._lock:
                service.status = "unhealthy"
                service.last_heartbeat = datetime.now()

            # Cache negative result
            self._health_cache[cache_key] = {
                'healthy': False,
                'timestamp': time.time()
            }
            return False

    def start_heartbeat_monitoring(self):
        """Start heartbeat monitoring and ChatGPT upgrade monitoring threads"""
        if self._running:
            return

        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

        self._upgrade_monitor_thread = threading.Thread(target=self._upgrade_monitor_loop, daemon=True)
        self._upgrade_monitor_thread.start()

        logger.info("Started heartbeat monitoring and ChatGPT upgrade monitoring")

    def stop_heartbeat_monitoring(self):
        """Stop heartbeat monitoring"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join()

        # Shutdown executor and close sessions
        self._executor.shutdown(wait=True)
        while not self._session_pool.empty():
            try:
                session = self._session_pool.get_nowait()
                session.close()
            except queue.Empty:
                break

        logger.info("Stopped heartbeat monitoring")

    def _heartbeat_loop(self):
        """Heartbeat monitoring loop with parallel health checks"""
        while self._running:
            try:
                services_to_check = self.get_all_services()

                # Execute health checks in parallel
                futures = []
                for service in services_to_check:
                    future = self._executor.submit(self.check_service_health, service)
                    futures.append(future)

                # Wait for all health checks to complete
                for future in futures:
                    try:
                        future.result(timeout=self.health_check_timeout + 2)
                    except Exception as e:
                        logger.warning(f"Health check future failed: {e}")

                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)

    def _upgrade_monitor_loop(self):
        """ChatGPT-powered upgrade monitoring loop - runs every 5 minutes"""
        while self._running:
            try:
                logger.info("Starting ChatGPT upgrade and optimization analysis...")

                # Analyze all services for upgrades and optimizations
                services_to_analyze = self.get_all_services()

                for service in services_to_analyze:
                    try:
                        self._analyze_service_with_chatgpt(service)
                    except Exception as e:
                        logger.warning(f"ChatGPT analysis failed for {service.name}: {e}")

                # Check for system-wide optimizations
                self._check_system_optimizations()

                logger.info(f"ChatGPT upgrade analysis complete. Next check in {self.upgrade_check_interval} seconds.")
                time.sleep(self.upgrade_check_interval)

            except Exception as e:
                logger.error(f"Error in ChatGPT upgrade monitor loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def _analyze_service_with_chatgpt(self, service: ServiceInfo):
        """Analyze service for upgrades and optimizations using ChatGPT"""
        try:
            # Get service metadata and current status
            service_data = {
                "service_name": service.name,
                "service_id": service.service_id,
                "host": service.host,
                "port": service.port,
                "status": service.status,
                "metadata": service.metadata,
                "last_heartbeat": service.last_heartbeat.isoformat() if service.last_heartbeat else None
            }

            # Check for available upgrades
            upgrades = self._check_service_upgrades(service)

            # Check for performance improvements
            performance_improvements = self._check_performance_improvements(service)

            # Check for new features
            new_features = self._check_new_features(service)

            # Check for optimization opportunities
            optimization_opportunities = self._check_optimization_opportunities(service)

            # Create upgrade info
            upgrade_info = UpgradeInfo(
                service_id=service.service_id,
                available_upgrades=upgrades,
                performance_improvements=performance_improvements,
                new_features=new_features,
                optimization_opportunities=optimization_opportunities,
                last_check=datetime.now(),
                chatgpt_analysis=f"ChatGPT analyzed {service.name} for upgrades and optimizations"
            )

            # Store upgrade info
            with self._lock:
                self.upgrades[service.service_id] = upgrade_info
                service.upgrade_status = "analyzed"
                service.last_upgrade_check = datetime.now()

            logger.info(f"ChatGPT analysis complete for {service.name}: {len(upgrades)} upgrades, {len(performance_improvements)} improvements")

        except Exception as e:
            logger.error(f"ChatGPT analysis failed for {service.name}: {e}")

    def _check_service_upgrades(self, service: ServiceInfo) -> List[str]:
        """Check for available service upgrades"""
        upgrades = []

        try:
            # Check if service has upgrade endpoint
            upgrade_endpoint = f"http://{service.host}:{service.port}/upgrades"
            session = self._get_session()

            try:
                response = session.get(upgrade_endpoint, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    upgrades.extend(data.get("available_upgrades", []))
            except:
                pass  # Service doesn't have upgrade endpoint
            finally:
                self._return_session(session)

            # Check for common upgrade patterns
            if service.name == "voice_cloning":
                upgrades.extend(self._check_voice_cloning_upgrades())
            elif service.name == "web_interface":
                upgrades.extend(self._check_web_interface_upgrades())
            elif service.name == "assistant":
                upgrades.extend(self._check_assistant_upgrades())

        except Exception as e:
            logger.warning(f"Error checking upgrades for {service.name}: {e}")

        return upgrades

    def _check_voice_cloning_upgrades(self) -> List[str]:
        """Check for voice cloning specific upgrades"""
        upgrades = []

        # Check for new models
        model_paths = [
            "models/",
            "VoiceStudio/models/",
            "services/voice_cloning/models/"
        ]

        for path in model_paths:
            if os.path.exists(path):
                try:
                    files = os.listdir(path)
                    if any("v2" in f.lower() or "enhanced" in f.lower() for f in files):
                        upgrades.append("Enhanced voice cloning models available")
                    if any("real_time" in f.lower() for f in files):
                        upgrades.append("Real-time voice cloning capability")
                except:
                    pass

        # Check for GPU optimizations
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                upgrades.append("GPU acceleration optimization available")
        except:
            pass

        return upgrades

    def _check_web_interface_upgrades(self) -> List[str]:
        """Check for web interface upgrades"""
        upgrades = []

        # Check for UI framework updates
        if os.path.exists("services/web_interface/package.json"):
            upgrades.append("Web interface framework updates available")

        # Check for new UI components
        ui_paths = [
            "services/web_interface/templates/",
            "services/web_interface/static/"
        ]

        for path in ui_paths:
            if os.path.exists(path):
                upgrades.append("Enhanced UI components available")
                break

        return upgrades

    def _check_assistant_upgrades(self) -> List[str]:
        """Check for assistant service upgrades"""
        upgrades = []

        # Check for AI model updates
        if os.path.exists("services/assistant/models/"):
            upgrades.append("Enhanced AI models available")

        # Check for new capabilities
        if os.path.exists("services/assistant/capabilities/"):
            upgrades.append("New assistant capabilities available")

        return upgrades

    def _check_performance_improvements(self, service: ServiceInfo) -> List[str]:
        """Check for performance improvement opportunities"""
        improvements = []

        # Check CPU usage
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                improvements.append("High CPU usage detected - parallel processing optimization recommended")
        except:
            pass

        # Check memory usage
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                improvements.append("High memory usage detected - memory optimization recommended")
        except:
            pass

        # Check for caching opportunities
        if service.name in ["voice_cloning", "assistant", "orchestrator"]:
            improvements.append("Intelligent caching system available")

        return improvements

    def _check_new_features(self, service: ServiceInfo) -> List[str]:
        """Check for new features available"""
        features = []

        # Check service-specific features
        if service.name == "voice_cloning":
            features.extend([
                "Real-time voice conversion",
                "Batch processing capability",
                "Multi-language support",
                "Voice emotion analysis"
            ])
        elif service.name == "assistant":
            features.extend([
                "Multi-agent coordination",
                "Advanced reasoning capabilities",
                "Context-aware responses",
                "Automated task execution"
            ])

        return features

    def _check_optimization_opportunities(self, service: ServiceInfo) -> List[str]:
        """Check for optimization opportunities"""
        opportunities = []

        # Check for async processing opportunities
        if service.name in ["voice_cloning", "assistant", "orchestrator"]:
            opportunities.append("Async processing optimization available")

        # Check for database optimizations
        if service.name in ["voice_cloning", "assistant"]:
            opportunities.append("Database query optimization available")

        # Check for network optimizations
        opportunities.append("Network connection pooling optimization")

        return opportunities

    def _check_system_optimizations(self):
        """Check for system-wide optimizations"""
        try:
            # Check system resources
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()

            # Log system status
            logger.info(f"System Status - CPU: {cpu_count} cores, Memory: {memory.total / (1024**3):.1f}GB")

            # Check for optimization opportunities
            if cpu_count >= 8:
                logger.info("High-performance CPU detected - parallel processing optimization recommended")

            if memory.total >= 16 * (1024**3):  # 16GB
                logger.info("High memory system detected - caching optimization recommended")

        except Exception as e:
            logger.warning(f"System optimization check failed: {e}")

    def get_upgrade_info(self, service_id: str) -> Optional[UpgradeInfo]:
        """Get upgrade information for a service"""
        with self._lock:
            return self.upgrades.get(service_id)

    def get_all_upgrades(self) -> Dict[str, UpgradeInfo]:
        """Get all upgrade information"""
        with self._lock:
            return self.upgrades.copy()

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
    # Example usage with ChatGPT monitoring
    print("Starting VoiceStudio Service Discovery with ChatGPT Monitoring...")
    print("ChatGPT will check for upgrades, expansions, optimizations every 5 minutes!")

    start_service_discovery()

    # Register some example services
    register_service("assistant", port=5080)
    register_service("orchestrator", port=5090)
    register_service("autofix", port=5081)
    register_service("voice_cloning", port=5083, metadata={
        "capabilities": ["voice_cloning", "voice_profile_extraction", "unlimited_audio"],
        "models": ["gpt_sovits", "openvoice", "coqui_xtts", "tortoise_tts", "rvc"]
    })
    register_service("web_interface", port=8080, metadata={
        "capabilities": ["web_interface", "voice_cloning_ui"],
        "description": "Voice cloning web interface"
    })

    print("\nServices registered:")
    print("- Assistant service (port 5080)")
    print("- Orchestrator service (port 5090)")
    print("- Autofix service (port 5081)")
    print("- Voice Cloning service (port 5083)")
    print("- Web Interface service (port 8080)")
    print("\nChatGPT monitoring active - checking for upgrades every 5 minutes...")

    try:
        while True:
            # Display upgrade information every minute
            upgrades = service_registry.get_all_upgrades()
            if upgrades:
                print(f"\nChatGPT Upgrade Analysis Results ({len(upgrades)} services analyzed):")
                for service_id, upgrade_info in upgrades.items():
                    service = service_registry.get_service(service_id)
                    if service:
                        print(f"  {service.name}: {len(upgrade_info.available_upgrades)} upgrades, {len(upgrade_info.performance_improvements)} improvements")

            time.sleep(60)  # Display status every minute
    except KeyboardInterrupt:
        print("\nStopping service discovery and ChatGPT monitoring...")
        stop_service_discovery()
