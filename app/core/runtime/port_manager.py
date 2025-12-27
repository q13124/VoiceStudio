"""
Port Manager
Manages port allocation and prevents conflicts for engine processes
"""

import json
import socket
import logging
from typing import Dict, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class PortManager:
    """
    Manages port allocation for engine processes.
    
    Features:
    - Dynamic port allocation from reserved ranges
    - Port conflict detection
    - Port reservation registry
    - Automatic port cleanup on process exit
    """
    
    # Reserved port ranges
    COMFYUI_PORT = 8188
    BASE_HTTP_PORT = 8200  # VoiceStudio engines start here
    PORT_RANGE_SIZE = 100  # Allocate 8200-8299 for VoiceStudio
    
    def __init__(self, ports_file: str = "runtime/ports.json"):
        """
        Initialize port manager.
        
        Args:
            ports_file: Path to port registry file
        """
        self.ports_file = Path(ports_file)
        self.ports_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Reserved ports (fixed assignments)
        self.reserved_ports: Dict[str, int] = {
            "comfyui": self.COMFYUI_PORT,
        }
        
        # Active port assignments
        self.active_ports: Dict[str, Dict[str, any]] = {}
        
        # Load existing port registry
        self._load_registry()
    
    def _load_registry(self):
        """Load port registry from file."""
        if self.ports_file.exists():
            try:
                with open(self.ports_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_ports = data.get("active", {})
                    # Clean up stale ports (processes that may have died)
                    self._cleanup_stale_ports()
            except Exception as e:
                logger.warning(f"Failed to load port registry: {e}")
                self.active_ports = {}
        else:
            self.active_ports = {}
    
    def _save_registry(self):
        """Save port registry to file."""
        try:
            data = {
                "active": self.active_ports,
                "reserved": self.reserved_ports,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.ports_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save port registry: {e}")
    
    def _cleanup_stale_ports(self):
        """Remove ports from registry if process is no longer running."""
        stale_engines = []
        
        for engine_id, info in self.active_ports.items():
            pid = info.get("pid")
            if pid and not self._is_process_running(pid):
                stale_engines.append(engine_id)
        
        for engine_id in stale_engines:
            logger.info(f"Cleaning up stale port for engine: {engine_id}")
            del self.active_ports[engine_id]
        
        if stale_engines:
            self._save_registry()
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if process is still running (cross-platform)."""
        try:
            if os.name == 'nt':  # Windows
                import psutil
                return psutil.pid_exists(pid)
            else:  # Unix-like
                os.kill(pid, 0)
                return True
        except (OSError, ImportError, ProcessLookupError):
            return False
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result != 0  # Port is available if connection fails
        except Exception as e:
            logger.debug(f"Error checking port {port}: {e}")
            return False
    
    def _find_available_port(self, start_port: int, end_port: int) -> Optional[int]:
        """Find an available port in the given range."""
        for port in range(start_port, end_port + 1):
            if port in self.reserved_ports.values():
                continue  # Skip reserved ports
            
            if port in [info.get("port") for info in self.active_ports.values()]:
                continue  # Skip already assigned ports
            
            if self._is_port_available(port):
                return port
        
        return None
    
    def allocate_port(self, engine_id: str, preferred_port: Optional[int] = None, pid: Optional[int] = None) -> Optional[int]:
        """
        Allocate a port for an engine.
        
        Args:
            engine_id: Engine identifier
            preferred_port: Preferred port (if available)
            pid: Process ID (for cleanup tracking)
        
        Returns:
            Allocated port number or None if allocation failed
        """
        # Check if engine already has a port
        if engine_id in self.active_ports:
            existing_port = self.active_ports[engine_id].get("port")
            if self._is_port_available(existing_port):
                logger.debug(f"Engine {engine_id} already has port {existing_port}")
                return existing_port
            else:
                # Port is in use, remove from registry
                logger.warning(f"Port {existing_port} for {engine_id} is in use, reallocating")
                del self.active_ports[engine_id]
        
        # Try preferred port first
        if preferred_port:
            if self._is_port_available(preferred_port):
                port = preferred_port
            else:
                logger.warning(f"Preferred port {preferred_port} is not available")
                port = None
        else:
            port = None
        
        # Find available port if preferred not available
        if not port:
            port = self._find_available_port(self.BASE_HTTP_PORT, self.BASE_HTTP_PORT + self.PORT_RANGE_SIZE - 1)
        
        if not port:
            logger.error(f"Failed to allocate port for engine {engine_id}")
            return None
        
        # Reserve port
        self.active_ports[engine_id] = {
            "port": port,
            "pid": pid,
            "allocated_at": datetime.now().isoformat()
        }
        
        self._save_registry()
        logger.info(f"Allocated port {port} for engine {engine_id}")
        return port
    
    def release_port(self, engine_id: str):
        """Release a port assigned to an engine."""
        if engine_id in self.active_ports:
            port = self.active_ports[engine_id].get("port")
            del self.active_ports[engine_id]
            self._save_registry()
            logger.info(f"Released port {port} for engine {engine_id}")
    
    def get_port(self, engine_id: str) -> Optional[int]:
        """Get the port assigned to an engine."""
        if engine_id in self.active_ports:
            return self.active_ports[engine_id].get("port")
        return None
    
    def get_reserved_port(self, name: str) -> Optional[int]:
        """Get a reserved port by name."""
        return self.reserved_ports.get(name)
    
    def list_active_ports(self) -> Dict[str, int]:
        """List all active port assignments."""
        return {engine_id: info.get("port") for engine_id, info in self.active_ports.items()}


# Global port manager instance
_port_manager: Optional[PortManager] = None


def get_port_manager(ports_file: str = "runtime/ports.json") -> PortManager:
    """Get or create global port manager instance."""
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager(ports_file)
    return _port_manager

