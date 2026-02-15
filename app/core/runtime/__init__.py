"""
VoiceStudio Runtime Layer

Orchestration, Governor, and runtime management.

Migration Note (GAP-ENG-003):
- Prefer EnhancedRuntimeEngine over RuntimeEngine for new code
- RuntimeEngine is maintained for backward compatibility
- EnhancedRuntimeEngine adds lifecycle, port, resource management, and security
"""

from .engine_hook import EngineHook, hook
from .engine_lifecycle import EngineLifecycleManager, EngineState, get_lifecycle_manager
from .hooks import HookRegistry, get_hook_registry
from .port_manager import PortManager, get_port_manager
from .resource_manager import (
    JobPriority,
    JobStatus,
    ResourceManager,
    ResourceRequirement,
    get_resource_manager,
)
from .runtime_engine import RuntimeEngine, RuntimeEngineManager
from .runtime_engine_enhanced import EnhancedRuntimeEngine, EnhancedRuntimeEngineManager
from .security import SecurityPolicy, load_security_policy

__all__ = [
    "EngineHook",
    # Lifecycle management
    "EngineLifecycleManager",
    "EngineState",
    # Enhanced runtime engine (recommended)
    "EnhancedRuntimeEngine",
    "EnhancedRuntimeEngineManager",
    # Hooks
    "HookRegistry",
    "JobPriority",
    "JobStatus",
    # Port management
    "PortManager",
    # Resource management
    "ResourceManager",
    "ResourceRequirement",
    # Core runtime engine (prefer EnhancedRuntimeEngine for new code)
    "RuntimeEngine",
    "RuntimeEngineManager",
    # Security
    "SecurityPolicy",
    "get_hook_registry",
    "get_lifecycle_manager",
    "get_port_manager",
    "get_resource_manager",
    "hook",
    "load_security_policy",
]
