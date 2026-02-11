"""
VoiceStudio Runtime Layer

Orchestration, Governor, and runtime management.

Migration Note (GAP-ENG-003):
- Prefer EnhancedRuntimeEngine over RuntimeEngine for new code
- RuntimeEngine is maintained for backward compatibility
- EnhancedRuntimeEngine adds lifecycle, port, resource management, and security
"""

from .runtime_engine import RuntimeEngine, RuntimeEngineManager
from .runtime_engine_enhanced import EnhancedRuntimeEngine, EnhancedRuntimeEngineManager
from .engine_hook import EngineHook, hook
from .port_manager import PortManager, get_port_manager
from .resource_manager import ResourceManager, get_resource_manager, JobPriority, ResourceRequirement, JobStatus
from .engine_lifecycle import EngineLifecycleManager, get_lifecycle_manager, EngineState
from .hooks import HookRegistry, get_hook_registry
from .security import SecurityPolicy, load_security_policy

__all__ = [
    # Core runtime engine (prefer EnhancedRuntimeEngine for new code)
    "RuntimeEngine",
    "RuntimeEngineManager",
    # Enhanced runtime engine (recommended)
    "EnhancedRuntimeEngine",
    "EnhancedRuntimeEngineManager",
    "EngineHook",
    "hook",
    # Port management
    "PortManager",
    "get_port_manager",
    # Resource management
    "ResourceManager",
    "get_resource_manager",
    "JobPriority",
    "ResourceRequirement",
    "JobStatus",
    # Lifecycle management
    "EngineLifecycleManager",
    "get_lifecycle_manager",
    "EngineState",
    # Hooks
    "HookRegistry",
    "get_hook_registry",
    # Security
    "SecurityPolicy",
    "load_security_policy",
]
