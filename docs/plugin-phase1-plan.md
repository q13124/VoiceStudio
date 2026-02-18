# VoiceStudio Plugin System - Phase 1 Implementation Plan

## Executive Summary

This document provides a complete, actionable implementation plan for Phase 1 of the VoiceStudio Plugin System project. Phase 1 focuses on unifying the existing backend and frontend plugin architectures, establishing security foundations, and creating the core infrastructure needed for plugin development.

**Timeline:** 2 weeks (10 business days)
**Team Size:** 2-3 developers
**Prerequisites:** Existing plugin infrastructure (backend and frontend systems already in place)

## Phase 1 Goals and Success Criteria

### Primary Goals

1. Create a unified plugin manifest schema that both backend (Python/FastAPI) and frontend (C#/WinUI) can understand and validate
2. Implement a plugin bridge service that synchronizes plugin state between backend and frontend
3. Establish basic security measures including plugin validation, permission system, and sandboxing
4. Validate the implementation with at least one working example plugin that demonstrates full-stack capabilities

### Success Criteria

By the end of Phase 1, we should be able to:

- Load a plugin with a single manifest that is understood by both backend and frontend
- See accurate plugin status in the frontend UI that reflects backend plugin state
- Install a plugin that requests permissions and have the user approve those permissions
- Load the example plugin successfully on both backend and frontend with synchronized state
- Validate that a malicious plugin is blocked from accessing unauthorized resources

### Non-Goals for Phase 1

These important features are deferred to later phases:

- Plugin marketplace or distribution infrastructure (Phase 4)
- Cross-plugin communication (Phase 5)
- Advanced sandboxing with process isolation (Phase 5)
- Plugin monetization (Phase 5)
- Comprehensive developer documentation (Phase 2)

## Architecture Overview

### Current State

Your VoiceStudio application currently has two independent plugin systems:

**Backend System** (`backend/services/plugin_service.py`):
- Discovers plugins from `plugins/` directory
- Loads Python plugins that implement `BasePlugin`
- Reads `manifest.json` but expects specific fields
- Manages plugin lifecycle (discovered → loaded → activated)
- Provides hot-reload capability

**Frontend System** (`src/VoiceStudio.App/Services/PluginManager.cs`):
- Discovers plugins from `Plugins/` directory
- Loads C# DLL assemblies that implement `IPlugin`
- Reads `manifest.json` with different field expectations
- Registers UI panels with `IPanelRegistry`
- Connects plugins to backend via `IBackendClient`

**The Problem**: These systems don't coordinate. A plugin loaded in backend might not have frontend components, or vice versa. The manifest schemas differ, making it difficult to create full-stack plugins.

### Target State

After Phase 1, we will have:

**Unified Manifest Schema**:
- Single JSON schema file that validates plugin manifests
- Schema supports plugins with backend-only, frontend-only, or both
- Clear specification of capabilities, permissions, and dependencies
- Versioning fields for compatibility checking

**Plugin Bridge Service**:
- C# service running in frontend that communicates with backend
- Synchronizes plugin state between the two systems
- Coordinates plugin loading across both layers
- Provides unified status reporting

**Security Infrastructure**:
- Permission system requiring plugins to declare needed capabilities
- User approval workflow for plugin permissions
- Basic sandboxing preventing unauthorized file system access
- Validation of plugin manifests before loading

## Detailed Task Breakdown

### Week 1: Schema and Bridge Infrastructure

#### Task 1.1: Create Unified Manifest Schema (2 days)

**Objective**: Define and implement a JSON schema that both backend and frontend can validate.

**Steps**:

1. Create the schema file at `shared/schemas/plugin-manifest.schema.json`

2. Define core required fields that every plugin must have:
   ```json
   {
     "name": "unique-plugin-identifier",
     "version": "1.0.0",
     "author": "Developer Name",
     "plugin_type": "full_stack"
   }
   ```

3. Define optional but recommended fields for rich plugin descriptions:
   ```json
   {
     "display_name": "User-Friendly Plugin Name",
     "description": "Brief one-line description",
     "long_description": "Detailed multi-paragraph description supporting Markdown",
     "homepage": "https://plugin-website.com",
     "documentation": "https://docs.plugin-website.com"
   }
   ```

4. Define capability declarations that tell the system what the plugin provides:
   ```json
   {
     "capabilities": {
       "backend_routes": true,
       "ui_panels": ["settings_panel", "main_panel"],
       "engines": ["custom_tts_engine"],
       "effects": ["reverb_effect", "echo_effect"],
       "export_formats": ["flac", "opus"],
       "import_formats": ["m4a"],
       "integrations": ["aws_s3", "google_drive"]
     }
   }
   ```

5. Define entry points that specify where to find the plugin code:
   ```json
   {
     "entry_points": {
       "backend": "plugin.register",
       "frontend": "MyPlugin.dll"
     }
   }
   ```

6. Define dependency declarations for managing plugin dependencies:
   ```json
   {
     "dependencies": {
       "python": ["numpy>=1.20.0", "scipy>=1.7.0"],
       "plugins": ["audio_toolkit>=2.0.0"],
       "system": ["ffmpeg"]
     }
   }
   ```

7. Define permission declarations for security:
   ```json
   {
     "permissions": [
       "filesystem.read",
       "filesystem.write",
       "network.http",
       "audio.input"
     ]
   }
   ```

8. Create validation utilities in Python at `backend/services/plugin_schema_validator.py`:

```python
"""
Plugin manifest schema validation.

Validates plugin manifest files against the unified schema.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import jsonschema
    from jsonschema import Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    Draft7Validator = None

logger = logging.getLogger(__name__)


class PluginSchemaValidator:
    """Validates plugin manifests against the unified schema."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize validator with schema file.
        
        Args:
            schema_path: Path to plugin-manifest.schema.json
                        If None, uses default location
        """
        if not HAS_JSONSCHEMA:
            raise ImportError(
                "jsonschema package required for plugin validation. "
                "Install with: pip install jsonschema"
            )
        
        if schema_path is None:
            # Default to shared/schemas/plugin-manifest.schema.json
            project_root = Path(__file__).parent.parent.parent
            schema_path = project_root / "shared" / "schemas" / "plugin-manifest.schema.json"
        
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema from file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load plugin schema from {self.schema_path}: {e}")
            raise
    
    def validate(self, manifest: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a plugin manifest against the schema.
        
        Args:
            manifest: Plugin manifest dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Validate against schema
            schema_errors = list(self.validator.iter_errors(manifest))
            
            if schema_errors:
                for error in schema_errors:
                    # Build readable error message
                    path = ".".join(str(p) for p in error.path) if error.path else "root"
                    errors.append(f"{path}: {error.message}")
            
            # Additional semantic validations
            semantic_errors = self._validate_semantics(manifest)
            errors.extend(semantic_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [f"Validation exception: {str(e)}"]
    
    def _validate_semantics(self, manifest: Dict[str, Any]) -> List[str]:
        """
        Perform semantic validation beyond schema structure.
        
        Checks for logical consistency and best practices.
        """
        errors = []
        
        # Check that entry points match declared capabilities
        capabilities = manifest.get("capabilities", {})
        entry_points = manifest.get("entry_points", {})
        
        if capabilities.get("backend_routes") and not entry_points.get("backend"):
            errors.append(
                "Plugin declares backend_routes capability but has no backend entry point"
            )
        
        if capabilities.get("ui_panels") and not entry_points.get("frontend"):
            errors.append(
                "Plugin declares ui_panels but has no frontend entry point"
            )
        
        # Check version format
        version = manifest.get("version", "")
        if version and not self._is_valid_semver(version):
            errors.append(f"Version '{version}' is not valid semantic versioning format")
        
        # Check plugin type consistency
        plugin_type = manifest.get("plugin_type", "")
        has_backend = entry_points.get("backend") is not None
        has_frontend = entry_points.get("frontend") is not None
        
        if plugin_type == "full_stack" and not (has_backend and has_frontend):
            errors.append(
                "Plugin type 'full_stack' requires both backend and frontend entry points"
            )
        
        return errors
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version string is valid semantic versioning."""
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'
        return bool(re.match(pattern, version))
    
    def validate_file(self, manifest_path: Path) -> tuple[bool, List[str], Optional[Dict[str, Any]]]:
        """
        Validate a manifest file.
        
        Args:
            manifest_path: Path to manifest.json file
            
        Returns:
            Tuple of (is_valid, error_messages, manifest_dict)
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            is_valid, errors = self.validate(manifest)
            return is_valid, errors, manifest
            
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"], None
        except Exception as e:
            return False, [f"Failed to read manifest: {e}"], None


# Global validator instance
_validator: Optional[PluginSchemaValidator] = None


def get_validator() -> PluginSchemaValidator:
    """Get or create the global plugin schema validator."""
    global _validator
    if _validator is None:
        _validator = PluginSchemaValidator()
    return _validator


def validate_plugin_manifest(manifest: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Convenience function to validate a plugin manifest.
    
    Args:
        manifest: Plugin manifest dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    validator = get_validator()
    return validator.validate(manifest)
```

9. Create corresponding validation utilities in C# at `src/VoiceStudio.Core/Plugins/PluginSchemaValidator.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Linq;
using Newtonsoft.Json.Schema;
using Newtonsoft.Json.Linq;

namespace VoiceStudio.Core.Plugins
{
    /// <summary>
    /// Validates plugin manifests against the unified schema.
    /// </summary>
    public class PluginSchemaValidator
    {
        private readonly JSchema _schema;
        private readonly string _schemaPath;

        public PluginSchemaValidator(string? schemaPath = null)
        {
            // Default to shared/schemas/plugin-manifest.schema.json
            _schemaPath = schemaPath ?? Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory,
                "shared",
                "schemas",
                "plugin-manifest.schema.json"
            );

            _schema = LoadSchema();
        }

        private JSchema LoadSchema()
        {
            try
            {
                var schemaJson = File.ReadAllText(_schemaPath);
                return JSchema.Parse(schemaJson);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException(
                    $"Failed to load plugin schema from {_schemaPath}: {ex.Message}",
                    ex
                );
            }
        }

        /// <summary>
        /// Validate a plugin manifest against the schema.
        /// </summary>
        /// <param name="manifestJson">Manifest JSON string</param>
        /// <returns>Tuple of (isValid, errorMessages)</returns>
        public (bool IsValid, List<string> Errors) Validate(string manifestJson)
        {
            var errors = new List<string>();

            try
            {
                var manifest = JObject.Parse(manifestJson);

                // Validate against schema
                if (!manifest.IsValid(_schema, out IList<string> schemaErrors))
                {
                    errors.AddRange(schemaErrors);
                }

                // Additional semantic validations
                var semanticErrors = ValidateSemantics(manifest);
                errors.AddRange(semanticErrors);

                return (errors.Count == 0, errors);
            }
            catch (JsonException ex)
            {
                errors.Add($"Invalid JSON: {ex.Message}");
                return (false, errors);
            }
            catch (Exception ex)
            {
                errors.Add($"Validation exception: {ex.Message}");
                return (false, errors);
            }
        }

        /// <summary>
        /// Validate a plugin manifest file.
        /// </summary>
        public (bool IsValid, List<string> Errors, JObject? Manifest) ValidateFile(string manifestPath)
        {
            try
            {
                var manifestJson = File.ReadAllText(manifestPath);
                var (isValid, errors) = Validate(manifestJson);
                var manifest = isValid ? JObject.Parse(manifestJson) : null;
                return (isValid, errors, manifest);
            }
            catch (Exception ex)
            {
                return (false, new List<string> { $"Failed to read manifest: {ex.Message}" }, null);
            }
        }

        private List<string> ValidateSemantics(JObject manifest)
        {
            var errors = new List<string>();

            // Get relevant sections
            var capabilities = manifest["capabilities"]?.ToObject<Dictionary<string, object>>();
            var entryPoints = manifest["entry_points"]?.ToObject<Dictionary<string, string>>();
            var pluginType = manifest["plugin_type"]?.ToString();

            // Check entry points match capabilities
            if (capabilities != null && entryPoints != null)
            {
                if (capabilities.ContainsKey("backend_routes") && 
                    (bool)capabilities["backend_routes"] &&
                    !entryPoints.ContainsKey("backend"))
                {
                    errors.Add("Plugin declares backend_routes capability but has no backend entry point");
                }

                if (capabilities.ContainsKey("ui_panels") &&
                    !entryPoints.ContainsKey("frontend"))
                {
                    errors.Add("Plugin declares ui_panels but has no frontend entry point");
                }
            }

            // Check plugin type consistency
            if (pluginType == "full_stack" && entryPoints != null)
            {
                var hasBackend = entryPoints.ContainsKey("backend");
                var hasFrontend = entryPoints.ContainsKey("frontend");

                if (!hasBackend || !hasFrontend)
                {
                    errors.Add("Plugin type 'full_stack' requires both backend and frontend entry points");
                }
            }

            return errors;
        }
    }
}
```

10. Update existing plugin loaders to use the new validator:

In `backend/services/plugin_service.py`, add validation during discovery:

```python
from backend.services.plugin_schema_validator import get_validator

async def discover_plugins(self) -> list[PluginInfo]:
    """Discover available plugins."""
    discovered = []
    validator = get_validator()

    if not self._plugins_dir.exists():
        return discovered

    for plugin_path in self._plugins_dir.iterdir():
        if not plugin_path.is_dir():
            continue

        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            # Validate manifest
            is_valid, errors, manifest_data = validator.validate_file(manifest_path)
            
            if not is_valid:
                logger.warning(
                    f"Invalid manifest for plugin at {plugin_path}:\n" +
                    "\n".join(f"  - {error}" for error in errors)
                )
                continue

            # Continue with existing discovery logic...
            manifest = PluginManifest.from_dict(manifest_data)
            # ... rest of discovery code
```

**Deliverables**:
- `shared/schemas/plugin-manifest.schema.json` - The unified schema
- `backend/services/plugin_schema_validator.py` - Python validation
- `src/VoiceStudio.Core/Plugins/PluginSchemaValidator.cs` - C# validation
- Updated plugin loaders in both backend and frontend to validate manifests
- Unit tests for the validators

**Testing**:
- Create test manifests (valid and invalid) to verify validation
- Test that invalid manifests are rejected with clear error messages
- Test that valid manifests pass validation

#### Task 1.2: Implement Plugin Bridge Service (3 days)

**Objective**: Create a C# service that synchronizes plugin state between backend and frontend.

**Steps**:

1. Create the bridge service at `src/VoiceStudio.App/Services/PluginBridgeService.cs` (code provided earlier in main document)

2. Define data models for synchronization at `src/VoiceStudio.App/Models/PluginSyncModels.cs`:

```csharp
using System;

namespace VoiceStudio.App.Models
{
    public class PluginSyncState
    {
        public string PluginId { get; set; } = string.Empty;
        public bool BackendLoaded { get; set; }
        public bool FrontendLoaded { get; set; }
        public DateTime LastSync { get; set; }
        public string? ErrorMessage { get; set; }
        
        public bool IsSynchronized => BackendLoaded == FrontendLoaded && ErrorMessage == null;
        
        public string StatusDescription
        {
            get
            {
                if (!string.IsNullOrEmpty(ErrorMessage))
                    return $"Error: {ErrorMessage}";
                    
                if (IsSynchronized)
                    return BackendLoaded ? "Loaded" : "Not Loaded";
                    
                if (BackendLoaded && !FrontendLoaded)
                    return "Backend Only";
                    
                if (!BackendLoaded && FrontendLoaded)
                    return "Frontend Only";
                    
                return "Unknown";
            }
        }
    }
    
    public class PluginLoadRequest
    {
        public string PluginId { get; set; } = string.Empty;
        public bool ForceReload { get; set; }
    }
    
    public class PluginLoadResponse
    {
        public bool Success { get; set; }
        public string? ErrorMessage { get; set; }
        public PluginSyncState? SyncState { get; set; }
    }
}
```

3. Register the bridge service in dependency injection at `src/VoiceStudio.App/App.xaml.cs`:

```csharp
// In ConfigureServices method
services.AddSingleton<PluginBridgeService>();
```

4. Initialize the bridge service during application startup:

```csharp
// In OnLaunched method, after other initializations
var pluginBridge = serviceProvider.GetRequiredService<PluginBridgeService>();
await pluginBridge.InitializeAsync();
```

5. Update `PluginManagementViewModel` to use the bridge service:

```csharp
private readonly PluginBridgeService? _pluginBridge;

public PluginManagementViewModel(IViewModelContext context)
    : base(context)
{
    try
    {
        _pluginManager = AppServices.GetPluginManager();
        _pluginBridge = AppServices.GetService<PluginBridgeService>();
    }
    catch
    {
        _pluginManager = null;
        _pluginBridge = null;
    }
    
    // ... rest of constructor
}

private async Task LoadPluginsAsync(CancellationToken cancellationToken)
{
    if (_pluginBridge == null)
    {
        ErrorMessage = "Plugin bridge not available";
        return;
    }

    IsLoading = true;
    ErrorMessage = null;
    StatusMessage = "Loading plugins...";

    try
    {
        // Initialize bridge (which loads plugins from both sides)
        await _pluginBridge.InitializeAsync();
        
        // Get sync state
        var syncStates = _pluginBridge.GetSyncState();
        
        UpdatePluginListFromSyncState(syncStates);

        StatusMessage = $"{Plugins.Count} plugins loaded";
    }
    catch (Exception ex)
    {
        await HandleErrorAsync(ex, "LoadPlugins");
        StatusMessage = null;
    }
    finally
    {
        IsLoading = false;
    }
}

private void UpdatePluginListFromSyncState(
    IReadOnlyDictionary<string, PluginSyncState> syncStates)
{
    Plugins.Clear();
    
    foreach (var (pluginId, syncState) in syncStates)
    {
        Plugins.Add(new PluginInfo
        {
            Name = pluginId,
            IsEnabled = syncState.BackendLoaded || syncState.FrontendLoaded,
            Status = syncState.StatusDescription,
            ErrorMessage = syncState.ErrorMessage
        });
    }
    
    ApplyFilters();
}
```

6. Add real-time synchronization using SignalR or polling:

Create `backend/api/ws/plugins.py`:

```python
"""
WebSocket support for real-time plugin updates.

Notifies frontend when plugins load, unload, or change state.
"""

import asyncio
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class PluginNotificationManager:
    """Manages WebSocket connections for plugin notifications."""
    
    def __init__(self):
        self._connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Register a new WebSocket connection."""
        await websocket.accept()
        self._connections.add(websocket)
        logger.info(f"Plugin notification client connected. Total: {len(self._connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Unregister a WebSocket connection."""
        self._connections.discard(websocket)
        logger.info(f"Plugin notification client disconnected. Total: {len(self._connections)}")
    
    async def notify_plugin_loaded(self, plugin_id: str):
        """Notify all clients that a plugin was loaded."""
        await self._broadcast({
            "event": "plugin_loaded",
            "plugin_id": plugin_id
        })
    
    async def notify_plugin_unloaded(self, plugin_id: str):
        """Notify all clients that a plugin was unloaded."""
        await self._broadcast({
            "event": "plugin_unloaded",
            "plugin_id": plugin_id
        })
    
    async def notify_plugin_error(self, plugin_id: str, error_message: str):
        """Notify all clients about a plugin error."""
        await self._broadcast({
            "event": "plugin_error",
            "plugin_id": plugin_id,
            "error": error_message
        })
    
    async def _broadcast(self, message: dict):
        """Send a message to all connected clients."""
        disconnected = []
        
        for connection in self._connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send plugin notification: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global notification manager
_notification_manager = PluginNotificationManager()


def get_notification_manager() -> PluginNotificationManager:
    """Get the global plugin notification manager."""
    return _notification_manager


async def plugin_notifications_handler(websocket: WebSocket):
    """WebSocket endpoint handler for plugin notifications."""
    manager = get_notification_manager()
    await manager.connect(websocket)
    
    try:
        # Keep connection alive and handle pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

Register the WebSocket endpoint in `backend/api/main.py`:

```python
from backend.api.ws.plugins import plugin_notifications_handler

@app.websocket("/ws/plugins")
async def ws_plugin_notifications(websocket: WebSocket):
    """WebSocket endpoint for real-time plugin notifications."""
    await plugin_notifications_handler(websocket)
```

Update `backend/services/plugin_service.py` to send notifications:

```python
from backend.api.ws.plugins import get_notification_manager

async def load_plugin(self, plugin_id: str) -> bool:
    """Load a plugin."""
    # ... existing loading code ...
    
    if success:
        # Notify clients
        notification_manager = get_notification_manager()
        await notification_manager.notify_plugin_loaded(plugin_id)
    
    return success
```

**Deliverables**:
- `src/VoiceStudio.App/Services/PluginBridgeService.cs`
- `src/VoiceStudio.App/Models/PluginSyncModels.cs`
- `backend/api/ws/plugins.py` for real-time updates
- Updated `PluginManagementViewModel` to use bridge
- Registration in dependency injection
- Unit tests for bridge service
- Integration tests for backend-frontend synchronization

**Testing**:
- Load a backend-only plugin and verify frontend shows correct state
- Load a full-stack plugin and verify both sides load
- Simulate backend plugin failure and verify frontend reflects error
- Test WebSocket notifications for real-time updates

### Week 2: Security and Example Plugin

#### Task 1.3: Implement Permission System (3 days)

**Objective**: Create a security layer that requires plugins to declare permissions and allows users to review/approve them.

**Steps**:

1. Define permission constants at `src/VoiceStudio.Core/Plugins/PluginPermissions.cs`:

```csharp
namespace VoiceStudio.Core.Plugins
{
    /// <summary>
    /// Standard plugin permissions.
    /// </summary>
    public static class PluginPermissions
    {
        // Filesystem permissions
        public const string FileSystemRead = "filesystem.read";
        public const string FileSystemWrite = "filesystem.write";
        
        // Network permissions
        public const string NetworkHttp = "network.http";
        public const string NetworkWebSocket = "network.websocket";
        
        // System permissions
        public const string SystemProcess = "system.process";
        public const string SystemInfo = "system.info";
        
        // Audio permissions
        public const string AudioInput = "audio.input";
        public const string AudioOutput = "audio.output";
        
        // User data permissions
        public const string UserCredentials = "user.credentials";
        public const string Clipboard = "clipboard";
        public const string Notifications = "notifications";
        
        /// <summary>
        /// Get human-readable description for a permission.
        /// </summary>
        public static string GetDescription(string permission)
        {
            return permission switch
            {
                FileSystemRead => "Read files from your computer",
                FileSystemWrite => "Write files to your computer",
                NetworkHttp => "Make HTTP requests to internet services",
                NetworkWebSocket => "Establish WebSocket connections",
                SystemProcess => "Start and manage system processes",
                SystemInfo => "Access system information",
                AudioInput => "Access microphone input",
                AudioOutput => "Play audio through speakers",
                UserCredentials => "Access saved credentials and API keys",
                Clipboard => "Read and write clipboard content",
                Notifications => "Show system notifications",
                _ => permission
            };
        }
        
        /// <summary>
        /// Determine if a permission is high-risk.
        /// </summary>
        public static bool IsHighRisk(string permission)
        {
            return permission is 
                FileSystemWrite or 
                SystemProcess or 
                UserCredentials;
        }
    }
}
```

2. Create permission manager at `src/VoiceStudio.App/Services/PluginPermissionManager.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using VoiceStudio.Core.Plugins;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Manages plugin permissions and user approvals.
    /// </summary>
    public class PluginPermissionManager
    {
        private readonly Dictionary<string, HashSet<string>> _grantedPermissions;
        private readonly Dictionary<string, HashSet<string>> _requestedPermissions;
        
        public PluginPermissionManager()
        {
            _grantedPermissions = new Dictionary<string, HashSet<string>>();
            _requestedPermissions = new Dictionary<string, HashSet<string>>();
        }
        
        /// <summary>
        /// Request permissions for a plugin.
        /// Returns true if all permissions are granted, false if user review needed.
        /// </summary>
        public async Task<PermissionRequestResult> RequestPermissionsAsync(
            string pluginId,
            IEnumerable<string> permissions)
        {
            var permissionList = permissions.ToList();
            
            // Check if already granted
            if (ArePermissionsGranted(pluginId, permissionList))
            {
                return PermissionRequestResult.Granted();
            }
            
            // Store requested permissions
            _requestedPermissions[pluginId] = new HashSet<string>(permissionList);
            
            // Show permission dialog to user
            var dialogResult = await ShowPermissionDialogAsync(pluginId, permissionList);
            
            if (dialogResult.Approved)
            {
                // Grant permissions
                if (!_grantedPermissions.ContainsKey(pluginId))
                {
                    _grantedPermissions[pluginId] = new HashSet<string>();
                }
                
                foreach (var permission in permissionList)
                {
                    _grantedPermissions[pluginId].Add(permission);
                }
                
                // Save to persistent storage
                await SavePermissionsAsync();
                
                return PermissionRequestResult.Granted();
            }
            else
            {
                return PermissionRequestResult.Denied(dialogResult.DeniedPermissions);
            }
        }
        
        /// <summary>
        /// Check if specific permissions are granted for a plugin.
        /// </summary>
        public bool HasPermission(string pluginId, string permission)
        {
            return _grantedPermissions.TryGetValue(pluginId, out var permissions) &&
                   permissions.Contains(permission);
        }
        
        /// <summary>
        /// Revoke all permissions for a plugin.
        /// </summary>
        public async Task RevokePermissionsAsync(string pluginId)
        {
            _grantedPermissions.Remove(pluginId);
            _requestedPermissions.Remove(pluginId);
            await SavePermissionsAsync();
        }
        
        private bool ArePermissionsGranted(string pluginId, IEnumerable<string> permissions)
        {
            if (!_grantedPermissions.TryGetValue(pluginId, out var granted))
            {
                return false;
            }
            
            return permissions.All(p => granted.Contains(p));
        }
        
        private async Task<PermissionDialogResult> ShowPermissionDialogAsync(
            string pluginId,
            IEnumerable<string> permissions)
        {
            // This would show a UI dialog - implementation in Task 1.4
            // For now, auto-approve in development
            #if DEBUG
            return new PermissionDialogResult 
            { 
                Approved = true,
                DeniedPermissions = new List<string>()
            };
            #else
            // In production, show actual dialog
            var dialog = new PluginPermissionDialog(pluginId, permissions);
            return await dialog.ShowAsync();
            #endif
        }
        
        private async Task SavePermissionsAsync()
        {
            // Save to JSON file or database
            var settingsPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "VoiceStudio",
                "plugin-permissions.json"
            );
            
            var data = new Dictionary<string, object>
            {
                ["granted"] = _grantedPermissions.ToDictionary(
                    kvp => kvp.Key,
                    kvp => kvp.Value.ToList()
                ),
                ["version"] = "1.0"
            };
            
            var json = System.Text.Json.JsonSerializer.Serialize(data, new System.Text.Json.JsonSerializerOptions
            {
                WriteIndented = true
            });
            
            Directory.CreateDirectory(Path.GetDirectoryName(settingsPath)!);
            await File.WriteAllTextAsync(settingsPath, json);
        }
    }
    
    public class PermissionRequestResult
    {
        public bool IsGranted { get; set; }
        public List<string> DeniedPermissions { get; set; } = new();
        
        public static PermissionRequestResult Granted()
        {
            return new PermissionRequestResult { IsGranted = true };
        }
        
        public static PermissionRequestResult Denied(IEnumerable<string> denied)
        {
            return new PermissionRequestResult 
            { 
                IsGranted = false,
                DeniedPermissions = denied.ToList()
            };
        }
    }
    
    internal class PermissionDialogResult
    {
        public bool Approved { get; set; }
        public List<string> DeniedPermissions { get; set; } = new();
    }
}
```

3. Integrate permission checking into plugin loading:

Update `PluginBridgeService.LoadPluginAsync`:

```csharp
public async Task<bool> LoadPluginAsync(string pluginId)
{
    try
    {
        // Get plugin manifest to check permissions
        var plugin = _pluginManager.GetPlugin(pluginId);
        if (plugin != null)
        {
            // Request permissions from user
            var permissionManager = ServiceProvider.GetService<PluginPermissionManager>();
            if (permissionManager != null)
            {
                var manifest = LoadManifest(pluginId);
                var permissions = manifest["permissions"]?.ToObject<List<string>>() ?? new List<string>();
                
                var result = await permissionManager.RequestPermissionsAsync(pluginId, permissions);
                
                if (!result.IsGranted)
                {
                    _logger.LogWarning(
                        $"Plugin {pluginId} denied permissions: {string.Join(", ", result.DeniedPermissions)}");
                    return false;
                }
            }
        }
        
        // Continue with existing load logic...
```

4. Implement sandboxing for file system access:

Create `backend/services/plugin_sandbox.py`:

```python
"""
Plugin sandboxing for security.

Restricts plugin access to authorized resources only.
"""

import logging
import os
from pathlib import Path
from typing import Set, Optional

logger = logging.getLogger(__name__)


class PluginSandbox:
    """
    Sandbox environment for plugin execution.
    
    Restricts file system access based on granted permissions.
    """
    
    def __init__(self, plugin_id: str, granted_permissions: Set[str]):
        self.plugin_id = plugin_id
        self.granted_permissions = granted_permissions
        self._allowed_paths: Set[Path] = set()
        self._setup_allowed_paths()
    
    def _setup_allowed_paths(self):
        """Configure allowed file system paths based on permissions."""
        # Plugin's own directory is always allowed
        plugin_dir = Path("plugins") / self.plugin_id
        self._allowed_paths.add(plugin_dir.absolute())
        
        # If has filesystem.read permission, allow reading from designated directories
        if "filesystem.read" in self.granted_permissions:
            # Allow reading from application data directory
            data_dir = Path(os.getenv("VOICESTUDIO_DATA_PATH", "data"))
            self._allowed_paths.add(data_dir.absolute())
            
            # Allow reading from user's documents (with caution)
            # In production, this should be more restrictive
            docs_dir = Path.home() / "Documents" / "VoiceStudio"
            self._allowed_paths.add(docs_dir.absolute())
        
        # If has filesystem.write permission, allow writing to output directory
        if "filesystem.write" in self.granted_permissions:
            output_dir = Path(os.getenv("VOICESTUDIO_OUTPUT_PATH", "output"))
            self._allowed_paths.add(output_dir.absolute())
    
    def check_file_access(self, path: str, operation: str) -> bool:
        """
        Check if plugin is allowed to access a file.
        
        Args:
            path: File path to check
            operation: 'read' or 'write'
            
        Returns:
            True if access is allowed, False otherwise
        """
        requested_path = Path(path).absolute()
        
        # Check if operation is permitted
        required_permission = f"filesystem.{operation}"
        if required_permission not in self.granted_permissions:
            logger.warning(
                f"Plugin {self.plugin_id} attempted {operation} without permission: {path}"
            )
            return False
        
        # Check if path is within allowed directories
        for allowed_path in self._allowed_paths:
            try:
                requested_path.relative_to(allowed_path)
                return True
            except ValueError:
                continue
        
        logger.warning(
            f"Plugin {self.plugin_id} attempted to access unauthorized path: {path}"
        )
        return False
    
    def check_network_access(self, url: str, protocol: str = "http") -> bool:
        """
        Check if plugin is allowed to access a network resource.
        
        Args:
            url: URL to access
            protocol: 'http' or 'websocket'
            
        Returns:
            True if access is allowed, False otherwise
        """
        required_permission = f"network.{protocol}"
        if required_permission not in self.granted_permissions:
            logger.warning(
                f"Plugin {self.plugin_id} attempted {protocol} access without permission: {url}"
            )
            return False
        
        return True


class SandboxedFileAccess:
    """
    Provides sandboxed file access for plugins.
    
    Wraps file operations with permission checks.
    """
    
    def __init__(self, sandbox: PluginSandbox):
        self.sandbox = sandbox
    
    def read_file(self, path: str) -> Optional[str]:
        """Read a file if permitted."""
        if not self.sandbox.check_file_access(path, "read"):
            raise PermissionError(
                f"Plugin {self.sandbox.plugin_id} not authorized to read: {path}"
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return None
    
    def write_file(self, path: str, content: str) -> bool:
        """Write a file if permitted."""
        if not self.sandbox.check_file_access(path, "write"):
            raise PermissionError(
                f"Plugin {self.sandbox.plugin_id} not authorized to write: {path}"
            )
        
        try:
            # Ensure directory exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}")
            return False


def create_plugin_sandbox(plugin_id: str, permissions: Set[str]) -> PluginSandbox:
    """
    Create a sandbox for a plugin.
    
    Args:
        plugin_id: Plugin identifier
        permissions: Set of granted permissions
        
    Returns:
        Configured PluginSandbox instance
    """
    return PluginSandbox(plugin_id, permissions)
```

**Deliverables**:
- `src/VoiceStudio.Core/Plugins/PluginPermissions.cs`
- `src/VoiceStudio.App/Services/PluginPermissionManager.cs`
- `backend/services/plugin_sandbox.py`
- Updated plugin loading to check permissions
- Permission persistence (JSON file storage)
- Unit tests for permission checking and sandboxing

**Testing**:
- Load a plugin requesting permissions and verify user sees approval dialog
- Deny permissions and verify plugin doesn't load
- Test sandboxing prevents unauthorized file access
- Test permission persistence across application restarts

#### Task 1.4: Create Permission Dialog UI (1 day)

**Objective**: Build a user interface for reviewing and approving plugin permissions.

**Steps**:

1. Create the dialog XAML at `src/VoiceStudio.App/Dialogs/PluginPermissionDialog.xaml`:

```xml
<ContentDialog
    x:Class="VoiceStudio.App.Dialogs.PluginPermissionDialog"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="Plugin Permissions"
    PrimaryButtonText="Allow"
    SecondaryButtonText="Deny"
    DefaultButton="Primary">
    
    <StackPanel Spacing="16">
        <TextBlock Text="{x:Bind PluginDisplayName}" 
                   Style="{StaticResource SubtitleTextBlockStyle}"/>
        
        <TextBlock Text="This plugin requests the following permissions:"
                   TextWrapping="Wrap"/>
        
        <ItemsRepeater ItemsSource="{x:Bind Permissions}">
            <ItemsRepeater.ItemTemplate>
                <DataTemplate x:DataType="local:PermissionViewModel">
                    <Grid Margin="0,8">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="Auto"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>
                        
                        <!-- Warning icon for high-risk permissions -->
                        <FontIcon Grid.Column="0"
                                  Glyph="&#xE7BA;"
                                  Foreground="{ThemeResource SystemFillColorCautionBrush}"
                                  Visibility="{x:Bind IsHighRisk}"/>
                        
                        <StackPanel Grid.Column="1" Margin="8,0,0,0">
                            <TextBlock Text="{x:Bind Description}"
                                       TextWrapping="Wrap"
                                       FontWeight="SemiBold"/>
                            <TextBlock Text="{x:Bind Details}"
                                       TextWrapping="Wrap"
                                       Foreground="{ThemeResource TextFillColorSecondaryBrush}"
                                       FontSize="12"/>
                        </StackPanel>
                    </Grid>
                </DataTemplate>
            </ItemsRepeater.ItemTemplate>
        </ItemsRepeater>
        
        <Border BorderThickness="1"
                BorderBrush="{ThemeResource CardStrokeColorDefaultBrush}"
                Background="{ThemeResource LayerFillColorDefaultBrush}"
                Padding="12"
                CornerRadius="8"
                Margin="0,8,0,0">
            <StackPanel Spacing="4">
                <TextBlock Text="Security Notice" 
                           FontWeight="SemiBold"
                           FontSize="12"/>
                <TextBlock TextWrapping="Wrap"
                           FontSize="11"
                           Foreground="{ThemeResource TextFillColorSecondaryBrush}">
                    Only grant permissions to plugins you trust. Malicious plugins
                    could potentially access sensitive data or harm your system.
                </TextBlock>
            </StackPanel>
        </Border>
    </StackPanel>
</ContentDialog>
```

2. Create code-behind at `src/VoiceStudio.App/Dialogs/PluginPermissionDialog.xaml.cs`:

```csharp
using Microsoft.UI.Xaml.Controls;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using VoiceStudio.Core.Plugins;

namespace VoiceStudio.App.Dialogs
{
    public sealed partial class PluginPermissionDialog : ContentDialog
    {
        public string PluginDisplayName { get; }
        public ObservableCollection<PermissionViewModel> Permissions { get; }
        
        public PluginPermissionDialog(string pluginId, IEnumerable<string> permissions)
        {
            this.InitializeComponent();
            
            PluginDisplayName = pluginId; // Could be enhanced with display name from manifest
            
            Permissions = new ObservableCollection<PermissionViewModel>(
                permissions.Select(p => new PermissionViewModel(p))
            );
        }
        
        public bool WerePermissionsGranted { get; private set; }
        
        protected override void OnPrimaryButtonClick(ContentDialogButtonClickEventArgs args)
        {
            WerePermissionsGranted = true;
            base.OnPrimaryButtonClick(args);
        }
        
        protected override void OnSecondaryButtonClick(ContentDialogButtonClickEventArgs args)
        {
            WerePermissionsGranted = false;
            base.OnSecondaryButtonClick(args);
        }
    }
    
    public class PermissionViewModel
    {
        public string Permission { get; }
        public string Description { get; }
        public string Details { get; }
        public bool IsHighRisk { get; }
        
        public PermissionViewModel(string permission)
        {
            Permission = permission;
            Description = PluginPermissions.GetDescription(permission);
            Details = GetPermissionDetails(permission);
            IsHighRisk = PluginPermissions.IsHighRisk(permission);
        }
        
        private string GetPermissionDetails(string permission)
        {
            return permission switch
            {
                PluginPermissions.FileSystemRead => 
                    "Plugin can read files from designated directories",
                PluginPermissions.FileSystemWrite => 
                    "Plugin can create and modify files in output directories",
                PluginPermissions.NetworkHttp => 
                    "Plugin can communicate with internet services via HTTP/HTTPS",
                PluginPermissions.NetworkWebSocket => 
                    "Plugin can establish real-time connections to servers",
                PluginPermissions.SystemProcess => 
                    "Plugin can execute external programs",
                PluginPermissions.SystemInfo => 
                    "Plugin can read system information like OS version and hardware specs",
                PluginPermissions.AudioInput => 
                    "Plugin can access microphone for recording",
                PluginPermissions.AudioOutput => 
                    "Plugin can play audio through your speakers",
                PluginPermissions.UserCredentials => 
                    "Plugin can access saved API keys and login credentials",
                PluginPermissions.Clipboard => 
                    "Plugin can read and modify clipboard content",
                PluginPermissions.Notifications => 
                    "Plugin can display system notifications",
                _ => "Custom permission"
            };
        }
    }
}
```

3. Update `PluginPermissionManager` to use the real dialog in production builds

**Deliverables**:
- `src/VoiceStudio.App/Dialogs/PluginPermissionDialog.xaml`
- `src/VoiceStudio.App/Dialogs/PluginPermissionDialog.xaml.cs`
- Updated `PluginPermissionManager` to show dialog
- UI tests for permission dialog

#### Task 1.5: Create Full-Stack Example Plugin (2 days)

**Objective**: Build a working example plugin that demonstrates all Phase 1 capabilities.

**Steps**:

1. Create plugin directory structure:
```
plugins/
  example_audio_effect/
    manifest.json
    plugin.py
    README.md
    ExampleAudioEffectPlugin.dll  (C# compiled)
    ExampleAudioEffectPlugin/
      ExampleAudioEffectPlugin.cs
      ExamplePanel.xaml
      ExamplePanel.xaml.cs
```

2. Create the unified manifest at `plugins/example_audio_effect/manifest.json`:

```json
{
  "name": "example_audio_effect",
  "display_name": "Example Audio Effect",
  "version": "1.0.0",
  "author": "VoiceStudio Team",
  "description": "Example plugin demonstrating full-stack architecture",
  "long_description": "This plugin provides a simple audio effect (echo) and a settings panel in the UI. It demonstrates how to create a plugin with both backend processing and frontend UI components.",
  "plugin_type": "full_stack",
  "min_app_version": "1.0.0",
  "min_api_version": "1.0.0",
  
  "capabilities": {
    "backend_routes": true,
    "ui_panels": ["example_settings"],
    "effects": ["example_echo"]
  },
  
  "entry_points": {
    "backend": "plugin.register",
    "frontend": "ExampleAudioEffectPlugin.dll"
  },
  
  "dependencies": {
    "python": ["numpy>=1.20.0"],
    "system": []
  },
  
  "permissions": [
    "filesystem.read",
    "audio.output"
  ],
  
  "settings_schema": {
    "type": "object",
    "properties": {
      "delay_ms": {
        "type": "number",
        "minimum": 0,
        "maximum": 2000,
        "default": 500,
        "description": "Echo delay in milliseconds"
      },
      "decay": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "default": 0.5,
        "description": "Echo decay factor"
      }
    }
  },
  
  "metadata": {
    "homepage": "https://voicestudio.example.com/plugins/example-audio-effect",
    "repository": "https://github.com/voicestudio/plugin-example-audio-effect",
    "license": "MIT",
    "tags": ["audio", "effect", "echo", "example"]
  }
}
```

3. Create the backend implementation at `plugins/example_audio_effect/plugin.py`:

```python
"""
Example Audio Effect Plugin

Demonstrates full-stack plugin architecture with:
- Backend audio processing (echo effect)
- API endpoints for configuration
- Permission usage
- Settings management
"""

import logging
import numpy as np
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.plugins_api.base import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)


class EchoSettings(BaseModel):
    """Echo effect settings."""
    delay_ms: int = 500
    decay: float = 0.5


class ExampleAudioEffectPlugin(BasePlugin):
    """Example plugin implementing an echo effect."""
    
    def __init__(self, plugin_dir: Path):
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
        
        self.router = APIRouter(
            prefix="/api/plugin/example_audio_effect",
            tags=["plugin", "example"]
        )
        
        self.settings = EchoSettings()
    
    def register(self, app):
        """Register plugin with FastAPI."""
        # Register routes
        self.router.get("/settings")(self.get_settings)
        self.router.put("/settings")(self.update_settings)
        self.router.post("/process")(self.process_audio)
        
        app.include_router(self.router)
        logger.info(f"Example Audio Effect plugin registered with {len(self.router.routes)} routes")
    
    async def get_settings(self) -> EchoSettings:
        """Get current effect settings."""
        return self.settings
    
    async def update_settings(self, settings: EchoSettings) -> dict:
        """Update effect settings."""
        self.settings = settings
        logger.info(f"Echo settings updated: delay={settings.delay_ms}ms, decay={settings.decay}")
        return {"message": "Settings updated successfully"}
    
    async def process_audio(self, audio_data: bytes) -> bytes:
        """
        Apply echo effect to audio data.
        
        This is a simplified example. Real audio processing would need
        proper format handling and sample rate conversion.
        """
        # Convert bytes to numpy array (assuming 16-bit PCM)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate delay in samples (assuming 44100 Hz sample rate)
        sample_rate = 44100
        delay_samples = int(self.settings.delay_ms * sample_rate / 1000)
        
        # Create output array
        output_length = len(audio_array) + delay_samples
        output = np.zeros(output_length, dtype=np.float32)
        
        # Mix original and delayed signal
        output[:len(audio_array)] += audio_array.astype(np.float32)
        output[delay_samples:] += audio_array.astype(np.float32) * self.settings.decay
        
        # Normalize and convert back to int16
        output = np.clip(output, -32768, 32767).astype(np.int16)
        
        return output.tobytes()


def register(app, plugin_dir: Path):
    """
    Plugin entry point called by plugin loader.
    
    Args:
        app: FastAPI application instance
        plugin_dir: Path to plugin directory
        
    Returns:
        Plugin instance
    """
    plugin = ExampleAudioEffectPlugin(plugin_dir)
    plugin.register(app)
    plugin.initialize()
    return plugin
```

4. Create the frontend C# implementation at `plugins/example_audio_effect/ExampleAudioEffectPlugin/ExampleAudioEffectPlugin.cs`:

```csharp
using System;
using VoiceStudio.Core.Plugins;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace ExampleAudioEffectPlugin
{
    /// <summary>
    /// Example plugin demonstrating full-stack architecture.
    /// </summary>
    public class ExampleAudioEffectPlugin : IPlugin
    {
        private IBackendClient? _backendClient;
        private bool _isInitialized;
        
        public string Name => "example_audio_effect";
        public string Version => "1.0.0";
        public string Author => "VoiceStudio Team";
        public string Description => "Example audio effect plugin with echo";
        
        public bool IsInitialized => _isInitialized;
        
        public void RegisterPanels(IPanelRegistry registry)
        {
            // Register the settings panel
            registry.RegisterPanel(
                "example_settings",
                "Example Effect Settings",
                typeof(ExampleSettingsPanel),
                PanelRegion.Right
            );
        }
        
        public void Initialize(IBackendClient backend)
        {
            _backendClient = backend;
            _isInitialized = true;
        }
        
        public void Cleanup()
        {
            _isInitialized = false;
        }
    }
}
```

5. Create the settings panel UI at `plugins/example_audio_effect/ExampleAudioEffectPlugin/ExampleSettingsPanel.xaml`:

```xml
<UserControl
    x:Class="ExampleAudioEffectPlugin.ExampleSettingsPanel"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <StackPanel Spacing="16" Padding="16">
        <TextBlock Text="Example Echo Effect" 
                   Style="{StaticResource SubtitleTextBlockStyle}"/>
        
        <StackPanel Spacing="8">
            <TextBlock Text="Delay (ms)"/>
            <Slider x:Name="DelaySlider"
                    Minimum="0"
                    Maximum="2000"
                    Value="{x:Bind ViewModel.DelayMs, Mode=TwoWay}"
                    StepFrequency="50"
                    Header="{x:Bind ViewModel.DelayMs, Mode=OneWay}"/>
        </StackPanel>
        
        <StackPanel Spacing="8">
            <TextBlock Text="Decay"/>
            <Slider x:Name="DecaySlider"
                    Minimum="0"
                    Maximum="1"
                    Value="{x:Bind ViewModel.Decay, Mode=TwoWay}"
                    StepFrequency="0.05"
                    Header="{x:Bind ViewModel.Decay, Mode=OneWay}"/>
        </StackPanel>
        
        <Button Content="Apply Settings"
                Command="{x:Bind ViewModel.ApplySettingsCommand}"/>
    </StackPanel>
</UserControl>
```

6. Write comprehensive README at `plugins/example_audio_effect/README.md` explaining the plugin architecture and how to modify it

**Deliverables**:
- Complete example plugin with backend and frontend
- Manifest using unified schema
- Working echo effect implementation
- Settings panel UI
- README documentation
- Build scripts for compiling the C# DLL

**Testing**:
- Load the example plugin and verify it appears in plugin list
- Open the settings panel and adjust values
- Process audio through the echo effect
- Verify permissions are requested and enforced

## Testing Strategy

### Unit Tests

Each component should have comprehensive unit tests:

**Schema Validator Tests** (`test_plugin_schema_validator.py`):
- Test valid manifests pass validation
- Test invalid manifests are rejected with clear errors
- Test semantic validation catches logical inconsistencies
- Test version format validation

**Permission Manager Tests** (`PluginPermissionManagerTests.cs`):
- Test permission granting and revocation
- Test permission persistence across restarts
- Test checking specific permissions
- Test permission inheritance (if implemented)

**Sandbox Tests** (`test_plugin_sandbox.py`):
- Test authorized file access succeeds
- Test unauthorized file access is blocked
- Test network access control
- Test sandbox applies correct restrictions based on permissions

**Bridge Service Tests** (`PluginBridgeServiceTests.cs`):
- Test backend-frontend synchronization
- Test handling of load failures
- Test WebSocket notifications
- Test concurrent plugin operations

### Integration Tests

**End-to-End Plugin Loading**:
1. Place plugin in directory
2. Start application
3. Verify plugin discovered
4. Approve permissions
5. Verify plugin loaded on both backend and frontend
6. Verify UI panel appears
7. Verify API endpoints work

**Permission Flow**:
1. Install plugin requesting permissions
2. Deny permissions
3. Verify plugin doesn't load
4. Retry installation
5. Grant permissions
6. Verify plugin loads successfully

**Synchronization**:
1. Load plugin on backend
2. Verify frontend shows correct state within 2 seconds
3. Unload plugin on backend
4. Verify frontend updates state
5. Test WebSocket reconnection after network interruption

### Performance Tests

**Plugin Loading Performance**:
- Measure time to discover 10 plugins (should be < 500ms)
- Measure time to validate manifest (should be < 50ms)
- Measure time to load single plugin (should be < 1000ms)
- Measure memory overhead per plugin (should be < 10MB)

**Synchronization Performance**:
- Measure latency of backend-frontend sync (should be < 100ms)
- Test synchronization with 20 concurrent plugins
- Measure WebSocket message throughput

## Deployment Plan

### Development Environment Setup

1. Install required dependencies:
```bash
pip install jsonschema watchdog
dotnet add package Newtonsoft.Json.Schema
```

2. Create shared directory structure:
```bash
mkdir -p shared/schemas
mkdir -p plugins/example_audio_effect/ExampleAudioEffectPlugin
```

3. Copy schema file to shared location

4. Configure both backend and frontend to reference shared schema

### Production Deployment

**Phase 1 Release Checklist**:
- [ ] Schema file deployed to shared location
- [ ] Backend validator integrated and tested
- [ ] Frontend validator integrated and tested
- [ ] Bridge service registered in DI container
- [ ] Permission manager initialized at startup
- [ ] Permission dialog styled consistently
- [ ] Example plugin packaged and documented
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Performance tests meet targets
- [ ] Documentation updated
- [ ] Release notes prepared

**Rollback Plan**:
If Phase 1 deployment causes issues:
1. Disable plugin loading at startup (add feature flag)
2. Revert to previous plugin system if critical
3. Investigate and fix issues
4. Redeploy with fixes
5. Re-enable plugin loading

## Success Metrics

We will measure Phase 1 success through:

**Technical Metrics**:
- Plugin discovery success rate: 100% for valid plugins
- Manifest validation accuracy: 100% for schema violations
- Backend-frontend sync latency: < 100ms average
- Permission dialog response time: < 500ms to display
- Plugin load time: < 1 second per plugin

**Quality Metrics**:
- Unit test coverage: > 90% for new code
- Integration test success rate: 100%
- Zero critical bugs in plugin loading
- Zero security vulnerabilities in permission system

**User Experience Metrics**:
- Example plugin loads successfully: 100% of test cases
- Permission dialog is understandable: Verified through user testing
- Plugin status accurately reflects state: 100% accuracy in tests

## Risks and Mitigation

**Risk: Schema Changes Break Existing Plugins**
- Mitigation: Version schema and support multiple schema versions
- Mitigation: Provide clear migration guide
- Mitigation: Warn users before breaking changes

**Risk: Permission System Too Restrictive**
- Mitigation: Start with reasonable defaults
- Mitigation: Collect user feedback
- Mitigation: Allow power users to grant additional permissions

**Risk: Backend-Frontend Sync Fails**
- Mitigation: Implement retry logic with exponential backoff
- Mitigation: Show clear error messages to user
- Mitigation: Allow manual refresh of plugin state

**Risk: Example Plugin Doesn't Build**
- Mitigation: Provide pre-built DLL in repository
- Mitigation: Document build process clearly
- Mitigation: Test build process on clean machine

## Next Steps After Phase 1

Once Phase 1 is complete, we proceed to:

**Phase 2: Developer Experience** (Weeks 3-4)
- Comprehensive documentation
- Plugin templates and generators
- Development tools and CLI

**Phase 3: Core Plugin Migration** (Weeks 5-8)
- Migrate audio effects to plugins
- Migrate TTS engines to plugins
- Migrate export formats to plugins

This creates momentum and demonstrates the value of the plugin system to stakeholders.

## Conclusion

Phase 1 establishes the critical foundation for the VoiceStudio plugin ecosystem. By unifying the backend and frontend systems, implementing security controls, and providing a working example, we enable the development of rich, full-stack plugins while maintaining system security and stability.

The deliverables from Phase 1 directly support the strategic goals of extensibility, modularity, and ecosystem development outlined in the overall architectural plan. Successfully completing Phase 1 validates the technical approach and provides the infrastructure needed for subsequent phases.

---

**Document Version**: 1.0
**Last Updated**: 2025-02-16
**Author**: Lead/Principal Architect
**Status**: Ready for Implementation