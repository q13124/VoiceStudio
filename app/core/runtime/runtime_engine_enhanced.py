"""
Enhanced Runtime Engine Manager
Integrated with lifecycle, port, and resource management
"""

import subprocess
import time
import requests
import logging
import os
from typing import Dict, Optional, List, Any
from pathlib import Path
import json

from .port_manager import get_port_manager
from .resource_manager import get_resource_manager, JobPriority, ResourceRequirement
from .engine_lifecycle import get_lifecycle_manager, EngineState
from .hooks import get_hook_registry
from .security import load_security_policy, SecurityPolicy

logger = logging.getLogger(__name__)


class EnhancedRuntimeEngine:
    """
    Enhanced runtime engine with lifecycle, port, and resource management.
    
    Features:
    - State machine integration
    - Port allocation via PortManager
    - Resource management via ResourceManager
    - Pre/post hooks via HookRegistry
    - Security policies via SecurityPolicy
    - Logging to file
    """
    
    def __init__(
        self,
        manifest: Dict[str, Any],
        workspace_root: str = ".",
        lifecycle_manager: Optional[Any] = None,
        port_manager: Optional[Any] = None,
        resource_manager: Optional[Any] = None,
        hook_registry: Optional[Any] = None
    ):
        """
        Initialize enhanced runtime engine.
        
        Args:
            manifest: Engine manifest dictionary (v1.1 format)
            workspace_root: Root directory of workspace
            lifecycle_manager: Lifecycle manager instance (or None for global)
            port_manager: Port manager instance (or None for global)
            resource_manager: Resource manager instance (or None for global)
            hook_registry: Hook registry instance (or None for global)
        """
        self.manifest = manifest
        self.workspace_root = Path(workspace_root)
        self.engine_id = manifest["id"]
        self.display_name = manifest.get("displayName", manifest.get("name", self.engine_id))
        self.engine_type = manifest.get("type", "unknown")
        self.tasks = manifest.get("tasks", [])
        self.protocol = manifest.get("protocol", "v1.0")
        
        # Managers
        self.lifecycle_manager = lifecycle_manager or get_lifecycle_manager(str(workspace_root))
        self.port_manager = port_manager or get_port_manager()
        self.resource_manager = resource_manager or get_resource_manager()
        self.hook_registry = hook_registry or get_hook_registry()
        
        # Security policy
        self.security_policy = load_security_policy(manifest)
        
        # Process
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.port: Optional[int] = None
        
        # Logging configuration
        self.log_config = manifest.get("log", {})
        self.log_file: Optional[Path] = None
        self.stderr_file: Optional[Path] = None
        
        # Lifecycle configuration
        self.lifecycle_config = manifest.get("lifecycle", {})
        self.idle_timeout = self.lifecycle_config.get("idle_timeout_seconds")
        self.pool_size = self.lifecycle_config.get("pool_size", 1)
        self.is_singleton = self.pool_size == 1
        
        # State
        self.state = EngineState.STOPPED
        self.last_activity = None
        
        # Initialize logging
        self._setup_logging()
        
        # Register with lifecycle manager
        self.lifecycle_manager.register_engine(
            engine_id=self.engine_id,
            manifest=manifest,
            pool_size=self.pool_size,
            is_singleton=self.is_singleton,
            idle_timeout_seconds=self.idle_timeout
        )
    
    def _setup_logging(self):
        """Setup logging configuration from manifest."""
        if not self.log_config.get("stderr_to_file") and not self.log_config.get("stdout_to_file"):
            return
        
        log_dir = Path(self.log_config.get("log_dir", "runtime/logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        if self.log_config.get("stderr_to_file"):
            self.stderr_file = log_dir / f"{self.engine_id}_stderr.log"
        
        if self.log_config.get("stdout_to_file"):
            self.log_file = log_dir / f"{self.engine_id}_stdout.log"
    
    def start(self, job_id: Optional[str] = None) -> bool:
        """
        Start the engine process with lifecycle management.
        
        Args:
            job_id: Optional job ID for lease tracking
        
        Returns:
            True if started successfully, False otherwise
        """
        # Check security policy for network access
        if not self._check_network_access():
            logger.warning(f"Network access denied for {self.engine_id} by security policy")
            return False
        
        # Execute pre-hooks
        pre_hooks = self.manifest.get("preHooks", [])
        context = {
            "manifest": self.manifest,
            "workspace_root": str(self.workspace_root),
            "engine_id": self.engine_id
        }
        
        if not self.hook_registry.execute_pre_hooks(pre_hooks, context):
            logger.error(f"Pre-hooks failed for {self.engine_id}")
            return False
        
        # Acquire engine from lifecycle manager
        lifecycle_engine = self.lifecycle_manager.acquire_engine(
            engine_id=self.engine_id,
            job_id=job_id,
            auto_start=True
        )
        
        if not lifecycle_engine:
            logger.error(f"Failed to acquire engine {self.engine_id} from lifecycle manager")
            return False
        
        # Update state
        self.state = EngineState.STARTING
        
        # Get port from lifecycle manager (if allocated)
        self.port = self.port_manager.get_port(self.engine_id)
        
        # Allocate port if not allocated
        if not self.port:
            preferred_port = self.manifest.get("entry", {}).get("port")
            self.port = self.port_manager.allocate_port(
                engine_id=self.engine_id,
                preferred_port=preferred_port,
                pid=self.pid
            )
            
            if not self.port:
                logger.error(f"Failed to allocate port for {self.engine_id}")
                self.state = EngineState.ERROR
                return False
        
        # Start process
        try:
            entry = self.manifest.get("entry", {})
            if entry.get("kind") != "python":
                logger.error(f"Unsupported entry kind: {entry.get('kind')}")
                self.state = EngineState.ERROR
                return False
            
            # Resolve executable path
            exe_path = entry.get("exe", "")
            if exe_path.startswith(".."):
                manifest_dir = Path(self.manifest.get("_manifest_path", ".")).parent
                exe_path = (manifest_dir / exe_path).resolve()
            else:
                exe_path = Path(exe_path)
            
            if not exe_path.exists():
                logger.error(f"Executable not found: {exe_path}")
                self.state = EngineState.ERROR
                return False
            
            # Build command with port injection
            args = entry.get("args", [])
            cmd = [str(exe_path)] + args
            
            # Inject port if needed
            if "--port" not in args and self.port:
                cmd.extend(["--port", str(self.port)])
            
            # Check file access for executable
            if not self.security_policy.check_file_access(str(exe_path)):
                logger.error(f"File access denied for {exe_path} by security policy")
                self.state = EngineState.ERROR
                return False
            
            # Setup log files
            stdout_file = None
            stderr_file = None
            
            if self.log_file:
                stdout_file = open(self.log_file, 'a')
            
            if self.stderr_file:
                stderr_file = open(self.stderr_file, 'a')
            
            # Start process
            logger.info(f"Starting engine {self.engine_id} on port {self.port}: {cmd}")
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.workspace_root),
                stdout=stdout_file or subprocess.PIPE,
                stderr=stderr_file or subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_NO_WINDOW') else 0
            )
            
            self.pid = self.process.pid
            
            # Update port manager with PID
            if self.port:
                self.port_manager.allocate_port(
                    engine_id=self.engine_id,
                    preferred_port=self.port,
                    pid=self.pid
                )
            
            # Wait for startup
            startup_timeout = self.lifecycle_config.get("startup_timeout_seconds", 30)
            time.sleep(2)  # Initial wait
            
            # Check if process is still running
            if self.process.poll() is not None:
                logger.error(f"Engine {self.engine_id} exited immediately")
                self.state = EngineState.ERROR
                if stdout_file:
                    stdout_file.close()
                if stderr_file:
                    stderr_file.close()
                return False
            
            # Health check
            health_check_timeout = startup_timeout - 2
            health_ok = False
            for _ in range(int(health_check_timeout / 2)):
                if self.is_healthy():
                    health_ok = True
                    break
                time.sleep(2)
            
            if health_ok:
                self.state = EngineState.HEALTHY
                logger.info(f"Engine {self.engine_id} started and healthy on port {self.port}")
                return True
            else:
                logger.warning(f"Engine {self.engine_id} started but health check failed")
                self.state = EngineState.HEALTHY  # Still mark as healthy, health might be delayed
                return True
                
        except Exception as e:
            logger.error(f"Failed to start engine {self.engine_id}: {e}")
            self.state = EngineState.ERROR
            if self.port:
                self.port_manager.release_port(self.engine_id)
            return False
    
    def stop(self, job_id: Optional[str] = None):
        """Stop the engine process gracefully."""
        # Release from lifecycle manager
        if job_id:
            self.lifecycle_manager.release_engine(self.engine_id, job_id)
        
        # Set draining state
        self.state = EngineState.DRAINING
        
        # Stop process
        if self.process is not None:
            logger.info(f"Stopping engine {self.engine_id}")
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Engine {self.engine_id} did not terminate, killing")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping engine {self.engine_id}: {e}")
            finally:
                self.process = None
                self.pid = None
        
        # Release port
        if self.port:
            self.port_manager.release_port(self.engine_id)
            self.port = None
        
        # Execute post-hooks
        post_hooks = self.manifest.get("postHooks", [])
        context = {
            "manifest": self.manifest,
            "workspace_root": str(self.workspace_root),
            "engine_id": self.engine_id,
            "output_path": None  # Could be set based on engine output
        }
        
        self.hook_registry.execute_post_hooks(post_hooks, context)
        
        # Update state
        self.state = EngineState.STOPPED
    
    def is_running(self) -> bool:
        """Check if engine process is running."""
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def is_healthy(self) -> bool:
        """Check engine health."""
        if not self.is_running():
            return False
        
        health = self.manifest.get("health", {})
        if not health:
            return True  # No health check defined
        
        kind = health.get("kind")
        if kind == "http":
            url = health.get("url")
            if url and self.port:
                # Replace port placeholder if present
                url = url.replace("{port}", str(self.port))
                try:
                    response = requests.get(url, timeout=2)
                    return response.status_code == 200
                except Exception as e:
                    logger.debug(f"Health check failed for {self.engine_id}: {e}")
                    return False
        
        return True
    
    def _check_network_access(self) -> bool:
        """Check if network access is allowed by security policy."""
        health = self.manifest.get("health", {})
        if health.get("kind") == "http":
            url = health.get("url", "")
            # Parse host and port from URL
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                host = parsed.hostname or "127.0.0.1"
                port = parsed.port or 80
                return self.security_policy.check_network_access(host, port)
            except Exception:
                return True  # Default to allow if parsing fails
        
        return True
    
    def supports_task(self, task: str) -> bool:
        """Check if engine supports a specific task."""
        return task in self.tasks
    
    def get_info(self) -> Dict[str, Any]:
        """Get engine information."""
        return {
            "id": self.engine_id,
            "display_name": self.display_name,
            "type": self.engine_type,
            "tasks": self.tasks,
            "protocol": self.protocol,
            "state": self.state.name,
            "port": self.port,
            "pid": self.pid,
            "running": self.is_running(),
            "healthy": self.is_healthy()
        }


class EnhancedRuntimeEngineManager:
    """
    Enhanced runtime engine manager with lifecycle integration.
    """
    
    def __init__(self, workspace_root: str = "."):
        """Initialize enhanced runtime engine manager."""
        self.workspace_root = Path(workspace_root)
        self.engines: Dict[str, EnhancedRuntimeEngine] = {}
        
        # Get managers
        self.lifecycle_manager = get_lifecycle_manager(str(workspace_root))
        self.port_manager = get_port_manager()
        self.resource_manager = get_resource_manager()
        self.hook_registry = get_hook_registry()
    
    def load_engine(self, manifest_path: str) -> Optional[EnhancedRuntimeEngine]:
        """Load an engine from a manifest (v1.1 format)."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Store manifest path for relative path resolution
            manifest["_manifest_path"] = str(Path(manifest_path).absolute())
            
            engine = EnhancedRuntimeEngine(
                manifest=manifest,
                workspace_root=str(self.workspace_root),
                lifecycle_manager=self.lifecycle_manager,
                port_manager=self.port_manager,
                resource_manager=self.resource_manager,
                hook_registry=self.hook_registry
            )
            
            self.engines[engine.engine_id] = engine
            logger.info(f"Loaded enhanced runtime engine: {engine.engine_id}")
            return engine
            
        except Exception as e:
            logger.error(f"Failed to load engine from {manifest_path}: {e}")
            return None
    
    def find_manifests(self, engines_root: str = "engines") -> Dict[str, str]:
        """Find all engine manifest files (both v1.0 and v1.1)."""
        manifests = {}
        engines_dir = Path(engines_root)
        
        if not engines_dir.exists():
            logger.warning(f"Engines directory not found: {engines_root}")
            return manifests
        
        # Search for engine.manifest.json files (v1.1)
        for manifest_file in engines_dir.rglob("engine.manifest.json"):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                engine_id = manifest.get("engine_id")
                if engine_id:
                    manifests[engine_id] = str(manifest_file)
            except Exception as e:
                logger.error(f"Failed to read manifest {manifest_file}: {e}")
        
        # Search for runtime.manifest.json files (v1.0 - legacy)
        for manifest_file in engines_dir.rglob("runtime.manifest.json"):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                engine_id = manifest.get("id")
                if engine_id:
                    manifests[engine_id] = str(manifest_file)
            except Exception as e:
                logger.error(f"Failed to read manifest {manifest_file}: {e}")
        
        logger.info(f"Found {len(manifests)} engine manifests")
        return manifests
    
    def load_all_engines(self, engines_root: str = "engines"):
        """Load all engines from manifests."""
        manifests = self.find_manifests(engines_root)
        
        for engine_id, manifest_path in manifests.items():
            self.load_engine(manifest_path)
    
    def start_engine(self, engine_id: str, job_id: Optional[str] = None) -> bool:
        """Start an engine by ID."""
        if engine_id not in self.engines:
            logger.error(f"Engine not found: {engine_id}")
            return False
        
        return self.engines[engine_id].start(job_id=job_id)
    
    def stop_engine(self, engine_id: str, job_id: Optional[str] = None):
        """Stop an engine by ID."""
        if engine_id in self.engines:
            self.engines[engine_id].stop(job_id=job_id)
    
    def get_engine(self, engine_id: str) -> Optional[EnhancedRuntimeEngine]:
        """Get engine by ID."""
        return self.engines.get(engine_id)
    
    def list_engines(self) -> List[str]:
        """List all loaded engine IDs."""
        return list(self.engines.keys())
    
    def stop_all(self, audit_log: bool = True):
        """Stop all engines (panic switch)."""
        logger.warning("STOP ALL ENGINES requested - panic switch activated")
        results = self.lifecycle_manager.kill_all(audit_log=audit_log)
        
        # Also stop all managed engines
        for engine in list(self.engines.values()):
            try:
                engine.stop()
            except Exception as e:
                logger.error(f"Error stopping engine {engine.engine_id}: {e}")
        
        return results

