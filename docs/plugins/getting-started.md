# Getting Started with VoiceStudio Plugins

## Introduction

Welcome to VoiceStudio plugin development! This guide will walk you through creating your first plugin from scratch. By the end of this tutorial, you'll have a working plugin that demonstrates the core concepts and patterns you'll use in all your future plugin development.

### What You'll Learn

- How to create a plugin manifest file
- How to implement the plugin lifecycle methods
- How to register API endpoints with VoiceStudio
- How to add plugin configuration
- How to write unit tests for your plugin
- How to test and verify your plugin works

### Prerequisites

- **Python 3.9+** for backend plugin development OR **C# 10+** for frontend plugin development
- Basic understanding of JSON syntax
- Familiarity with command-line tools
- A text editor or IDE (VS Code, Visual Studio, PyCharm, etc.)
- VoiceStudio installed and running

### Time Required

Approximately **90 minutes** for a developer who is following along actively with the tutorial.

---

## Understanding the Plugin Architecture

Before we write code, let's understand how plugins work in VoiceStudio at a high level.

### System Architecture

VoiceStudio uses a layered architecture where the WinUI 3 frontend communicates with a FastAPI backend through both HTTP REST APIs and WebSockets for real-time synchronization. Plugins integrate at the backend level, where they can process audio, provide API endpoints, or integrate with external services.

```
┌─────────────────────────────────┐
│   WinUI 3 Frontend (C#)         │
│   - UI Panels                   │
│   - User Interactions           │
└──────────────┬──────────────────┘
               │ HTTP REST + WebSocket
┌──────────────▼──────────────────┐
│   PluginBridgeService           │
│   - Synchronizes state          │
│   - Manages connections         │
└──────────────┬──────────────────┘
               │ WebSocket /ws/plugins
┌──────────────▼──────────────────┐
│   FastAPI Backend               │
│   - Plugin loader               │
│   - API routes                  │
│   - Permission manager          │
└──────────────┬──────────────────┘
               │ Process calls
┌──────────────▼──────────────────┐
│   Your Plugin (Python)          │
│   - Business logic              │
│   - Audio processing            │
│   - External integrations       │
└─────────────────────────────────┘
```

### Three Types of Plugins

VoiceStudio supports three types of plugins:

#### Backend Plugins (Python)
These plugins run in the FastAPI backend and can:
- Process audio files
- Provide API endpoints
- Integrate with external services
- Implement custom synthesis or transcription
- Manage data and configuration

Backend plugins are the easiest to create and require only Python knowledge.

#### Frontend Plugins (C#)
These plugins run in the WinUI 3 frontend and can:
- Add custom UI panels
- Create custom controls and visualizations
- Extend application menus
- Integrate with Windows system features

Frontend plugins require C# and WinUI knowledge.

#### Full-Stack Plugins
These plugins have both backend (Python) and frontend (C#) components that work together:
- Backend handles processing and data
- Frontend provides user interface
- Components communicate via HTTP API

Full-stack plugins are powerful but more complex to develop.

### The Plugin Manifest

Every plugin starts with a `manifest.json` file. This file describes your plugin to VoiceStudio:

```json
{
  "name": "plugin_identifier",
  "display_name": "Human-Readable Name",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "What your plugin does",
  "plugin_type": "backend_only",
  "entry_points": {
    "backend": "plugin.register"
  }
}
```

The manifest serves as a **contract** between your plugin and VoiceStudio. It declares:
- What your plugin is called (must be unique)
- What capabilities it provides
- What permissions it needs
- How VoiceStudio should load it

### Plugin Lifecycle

When VoiceStudio runs, it manages plugins through these phases:

1. **Discovery** — Scans the `plugins/` directory for `manifest.json` files
2. **Validation** — Validates manifests against the JSON schema
3. **Loading** — Imports your plugin module using the entry point
4. **Registration** — Calls your plugin's `register()` method to set up routes
5. **Initialization** — Calls your plugin's `initialize()` method for setup
6. **Active** — Your plugin is running and can handle requests
7. **Cleanup** — When VoiceStudio shuts down, `cleanup()` is called

Your plugin code implements methods that hook into this lifecycle.

---

## Setting Up Your Development Environment

### For Backend Plugin Development

#### Step 1: Create the Plugin Directory

Open a terminal in your VoiceStudio project root and create a directory for your plugin:

```bash
mkdir -p plugins/text_transform
cd plugins/text_transform
```

The plugin name (`text_transform`) should be lowercase with underscores (no spaces).

#### Step 2: Create a Python Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

#### Step 3: Install Dependencies

Create a `requirements.txt` file in your plugin directory:

```
# No external dependencies needed for this tutorial
# Add any pip packages your plugin needs here
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The base plugin framework is already installed with VoiceStudio, so you don't need to install it separately.

#### Step 4: Configure Your IDE

If using VS Code or PyCharm:
1. Select the Python interpreter from your virtual environment (`./venv/bin/python`)
2. Enable PyLint or Flake8 for linting
3. Configure auto-format on save (optional but recommended)

### For Frontend Plugin Development

Frontend plugin development requires Visual Studio 2022 or VS Code with the .NET SDK.

#### Step 1: Create the Plugin Project

```bash
mkdir -p plugins/MyPlugin
cd plugins/MyPlugin

# Create a C# class library
dotnet new classlib -n MyPlugin
cd MyPlugin
```

#### Step 2: Add Required NuGet Packages

Edit `MyPlugin.csproj`:

```xml
<ItemGroup>
  <ProjectReference Include="..\..\src\VoiceStudio.Core\VoiceStudio.Core.csproj" />
  <ProjectReference Include="..\..\src\VoiceStudio.App\VoiceStudio.App.csproj" />
</ItemGroup>
```

#### Step 3: Set the Output Path

Add to `PropertyGroup` in `.csproj`:

```xml
<OutputPath>..\..\plugins\MyPlugin\</OutputPath>
```

This ensures the compiled DLL goes to the right location.

---

## Creating Your First Plugin

We'll create a simple **text transformation plugin** that transforms text to uppercase and adds timestamps. This demonstrates all the essential concepts.

### Step 1: Create the Manifest

Create a file called `manifest.json` in `plugins/text_transform/`:

```json
{
  "$schema": "../../shared/schemas/plugin-manifest.schema.json",
  "name": "text_transform",
  "display_name": "Text Transform",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Transform text to uppercase and add timestamps",
  "plugin_type": "backend_only",
  "min_app_version": "1.0.0",
  "capabilities": {
    "backend_routes": true
  },
  "entry_points": {
    "backend": "plugin.register"
  },
  "dependencies": {
    "python": [],
    "plugins": [],
    "system": []
  },
  "permissions": [],
  "settings_schema": {
    "type": "object",
    "properties": {
      "add_timestamp": {
        "type": "boolean",
        "default": true,
        "description": "Add timestamp to transformed text"
      },
      "include_original": {
        "type": "boolean",
        "default": false,
        "description": "Include original text in response"
      }
    }
  },
  "metadata": {
    "license": "MIT",
    "tags": ["text", "transform", "example"]
  },
  "security": {
    "isolation_mode": "sandboxed"
  },
  "resource_limits": {
    "max_memory_mb": 64,
    "max_cpu_percent": 10,
    "max_execution_time_ms": 5000
  },
  "lifecycle": {
    "auto_start": true,
    "lazy_load": false,
    "restart_on_failure": true
  }
}
```

**What this manifest does:**
- **name**: Unique identifier (lowercase, underscores)
- **display_name**: Human-readable name shown in UI
- **version**: Semantic version (major.minor.patch)
- **plugin_type**: This is a backend-only plugin
- **capabilities**: Declares we provide backend routes
- **entry_points**: Tells VoiceStudio to call `plugin.register` from our `plugin.py`
- **settings_schema**: Configuration options users can set
- **permissions**: Which resources the plugin can access (empty = no special access needed)
- **resource_limits**: CPU, memory, and time limits for security

### Step 2: Create the Plugin Class

Create a file called `plugin.py` in `plugins/text_transform/`:

```python
"""
Text Transform Plugin

A simple plugin demonstrating basic plugin structure and lifecycle.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.plugins_api.base import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class TransformRequest(BaseModel):
    """Request model for text transformation."""
    text: str
    uppercase: bool = True


class TransformResponse(BaseModel):
    """Response model for text transformation."""
    original: str
    transformed: str
    timestamp: Optional[str] = None


class HealthStatus(BaseModel):
    """Plugin health status response."""
    healthy: bool
    plugin_name: str
    version: str


# ============================================================================
# Plugin Implementation
# ============================================================================

class TextTransformPlugin(BasePlugin):
    """
    Text Transform Plugin implementation.
    
    This plugin demonstrates:
    - Plugin lifecycle (initialize, cleanup)
    - API endpoint registration
    - Configuration from manifest settings
    - Error handling
    - Logging
    """
    
    def __init__(self, plugin_dir: Path):
        """
        Initialize the plugin.
        
        Args:
            plugin_dir: Directory where the plugin is installed
        """
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
        
        # Store plugin directory for later use
        self.plugin_dir = plugin_dir
        
        # Create router for our API endpoints
        self.router = APIRouter(
            prefix="/api/plugin/text_transform",
            tags=["text_transform"]
        )
        
        # Settings (will be loaded in initialize)
        self.add_timestamp = True
        self.include_original = False
        
        logger.debug(f"TextTransformPlugin.__init__ called with plugin_dir={plugin_dir}")
    
    def register(self, app) -> None:
        """
        Register plugin routes with FastAPI app.
        
        This method is called by the plugin loader after the plugin is instantiated.
        It's responsible for registering all API endpoints.
        
        Args:
            app: FastAPI application instance
        """
        try:
            # Register our routes
            self.router.get("/health")(self.get_health)
            self.router.post("/transform")(self.transform_text)
            
            # Include router in the app
            app.include_router(self.router)
            
            logger.info(
                f"Text Transform Plugin registered with {len(self.router.routes)} routes"
            )
        except Exception as e:
            logger.error(f"Failed to register plugin routes: {e}", exc_info=True)
            raise
    
    def initialize(self) -> None:
        """
        Initialize the plugin after registration.
        
        This method is called after register(). Use it for:
        - Loading configuration
        - Connecting to databases
        - Pre-loading models or data
        - Starting background tasks
        """
        try:
            super().initialize()
            
            # Load settings from manifest (in a real plugin, these would come from persistent storage)
            settings = self.metadata.manifest_data.get("settings_schema", {}).get("properties", {})
            
            self.add_timestamp = settings.get("add_timestamp", {}).get("default", True)
            self.include_original = settings.get("include_original", {}).get("default", False)
            
            logger.info(
                f"{self.name} initialized successfully "
                f"(add_timestamp={self.add_timestamp}, include_original={self.include_original})"
            )
        except Exception as e:
            logger.error(f"Error initializing plugin: {e}", exc_info=True)
            raise
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        This method is called when VoiceStudio is shutting down.
        Use it to:
        - Close database connections
        - Save state
        - Stop background tasks
        - Release file handles
        """
        try:
            super().cleanup()
            logger.info(f"{self.name} cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during plugin cleanup: {e}", exc_info=True)
    
    # ========================================================================
    # API Endpoints
    # ========================================================================
    
    async def get_health(self) -> HealthStatus:
        """
        Get plugin health status.
        
        Returns:
            Health status object
        """
        try:
            return HealthStatus(
                healthy=self.is_initialized(),
                plugin_name=self.name,
                version=self.version
            )
        except Exception as e:
            logger.error(f"Error in health check: {e}", exc_info=True)
            return HealthStatus(
                healthy=False,
                plugin_name=self.name,
                version=self.version
            )
    
    async def transform_text(self, request: TransformRequest) -> TransformResponse:
        """
        Transform text according to settings.
        
        Args:
            request: Transform request with text and options
            
        Returns:
            Transform response with original and transformed text
        """
        try:
            # Validate input
            if not request.text:
                logger.warning("Empty text provided to transform_text")
                return TransformResponse(
                    original="",
                    transformed="",
                    timestamp=datetime.now().isoformat() if self.add_timestamp else None
                )
            
            # Transform the text
            if request.uppercase:
                transformed = request.text.upper()
            else:
                transformed = request.text.lower()
            
            # Prepare response
            response = TransformResponse(
                original=request.text if self.include_original else "",
                transformed=transformed,
                timestamp=datetime.now().isoformat() if self.add_timestamp else None
            )
            
            logger.debug(f"Transformed text: '{request.text}' -> '{transformed}'")
            return response
            
        except Exception as e:
            logger.error(f"Error transforming text: {e}", exc_info=True)
            return TransformResponse(
                original=request.text,
                transformed="",
                timestamp=datetime.now().isoformat() if self.add_timestamp else None
            )


# ============================================================================
# Plugin Entry Point
# ============================================================================

def register(app, plugin_dir: Path) -> TextTransformPlugin:
    """
    Plugin entry point called by the plugin loader.
    
    This function is called when VoiceStudio loads the plugin.
    The name and signature MUST match what's in the manifest's entry_points.backend.
    
    Args:
        app: FastAPI application instance
        plugin_dir: Path to the plugin directory
        
    Returns:
        The plugin instance (so the loader can track it)
    """
    try:
        plugin = TextTransformPlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        logger.info(f"Text Transform Plugin loaded successfully from {plugin_dir}")
        return plugin
    except Exception as e:
        logger.error(f"Failed to load Text Transform Plugin: {e}", exc_info=True)
        raise
```

**Key points in the plugin code:**

- **Imports**: We import from `app.core.plugins_api.base` which is the base plugin framework
- **Pydantic models**: For request/response validation
- **BasePlugin inheritance**: Our plugin class inherits from BasePlugin
- **register() method**: This is required and is called to register API endpoints
- **initialize() method**: Optional, called after registration for setup
- **cleanup() method**: Optional, called on shutdown for cleanup
- **Router**: We use FastAPI's APIRouter to organize our endpoints
- **Entry point function**: Must be named exactly as specified in `entry_points.backend`
- **Error handling**: Every method has try-except with logging (no silent errors!)

### Step 3: Create Unit Tests

Create `tests/test_plugin.py`:

```python
"""
Unit tests for Text Transform Plugin
"""

import pytest
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Note: This assumes you run tests from the plugin directory
# or that the app package is in your Python path


@pytest.fixture
def mock_app():
    """Create a test FastAPI application."""
    return FastAPI()


@pytest.fixture
def plugin_dir():
    """Get the plugin directory."""
    return Path(__file__).parent.parent


def test_plugin_initialization(mock_app, plugin_dir):
    """Test that plugin initializes correctly."""
    # Import here to ensure it can find the modules
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        
        assert plugin is not None
        assert plugin.name == "text_transform"
        assert plugin.is_initialized()
    except ImportError as e:
        pytest.skip(f"Could not import plugin: {e}")


def test_transform_endpoint(mock_app, plugin_dir):
    """Test the transform text endpoint."""
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        client = TestClient(mock_app)
        
        # Test uppercase transformation
        response = client.post(
            "/api/plugin/text_transform/transform",
            json={"text": "hello world", "uppercase": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transformed"] == "HELLO WORLD"
        assert data["timestamp"] is not None
    except ImportError as e:
        pytest.skip(f"Could not import plugin: {e}")


def test_health_endpoint(mock_app, plugin_dir):
    """Test the health check endpoint."""
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        client = TestClient(mock_app)
        
        response = client.get("/api/plugin/text_transform/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["healthy"] is True
        assert data["plugin_name"] == "text_transform"
    except ImportError as e:
        pytest.skip(f"Could not import plugin: {e}")
```

Create `tests/__init__.py` (empty file):

```python
# Test package marker
```

### Step 4: Create a README

Create `README.md`:

```markdown
# Text Transform Plugin

A simple text transformation plugin that demonstrates core VoiceStudio plugin concepts.

## Features

- Transform text to uppercase
- Add timestamps to transformed text
- Include original text in response (configurable)
- Health check endpoint

## Installation

This plugin comes with VoiceStudio. To enable it, ensure it's in the `plugins/` directory.

## Usage

### API Endpoint

```bash
POST /api/plugin/text_transform/transform

{
  "text": "hello world",
  "uppercase": true
}
```

Response:

```json
{
  "original": "hello world",
  "transformed": "HELLO WORLD",
  "timestamp": "2025-02-16T10:30:45.123456"
}
```

### Health Check

```bash
GET /api/plugin/text_transform/health
```

## Configuration

Edit `manifest.json` to modify plugin settings:

- `add_timestamp` (boolean): Whether to include timestamp in response
- `include_original` (boolean): Whether to include original text in response

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Structure

- `plugin.py` — Main plugin implementation
- `manifest.json` — Plugin metadata and configuration
- `tests/` — Unit tests
- `requirements.txt` — Python dependencies

## License

MIT
```

### Step 5: Test Your Plugin Locally

#### Run Tests

```bash
cd plugins/text_transform
pytest tests/ -v
```

You should see all tests pass (assuming the imports can find the app module).

#### Manual Testing with cURL

Once VoiceStudio is running:

```bash
# Get plugin health
curl http://localhost:8000/api/plugin/text_transform/health

# Transform text
curl -X POST http://localhost:8000/api/plugin/text_transform/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "uppercase": true}'
```

---

## Testing and Verifying Your Plugin

### Step 1: Place Your Plugin in the Plugins Directory

Make sure your plugin directory is at `plugins/text_transform/` from the VoiceStudio root.

### Step 2: Start VoiceStudio

```bash
python backend/api/main.py
```

Or run the application normally.

### Step 3: Verify Plugin Discovery

Check the console output. You should see:

```
Successfully loaded plugin: text_transform
Text Transform Plugin registered with X routes
Text Transform Plugin initialized successfully
```

### Step 4: Verify Plugin Appears in API

Open your browser or use curl:

```bash
curl http://localhost:8000/api/plugins
```

You should see your `text_transform` plugin in the list with status "active".

### Step 5: Test Your Endpoints

Use curl, Postman, or any HTTP client to test:

```bash
# Health check
curl http://localhost:8000/api/plugin/text_transform/health

# Transform text
curl -X POST http://localhost:8000/api/plugin/text_transform/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "hello", "uppercase": true}'
```

---

## Next Steps

Congratulations! You've created your first VoiceStudio plugin. Here's what to explore next:

### Learn More

1. **API Reference** — Read the complete backend and frontend API documentation
   - [Backend API Reference](api-reference-backend.md)
   - [Frontend API Reference](api-reference-frontend.md)

2. **Best Practices** — Follow our guide to patterns and anti-patterns
   - [Best Practices Guide](best-practices.md)
   - Error handling, logging, performance, security

3. **Plugin Templates** — Use production-ready templates as starting points
   - Minimal backend plugin
   - Frontend plugin with UI
   - Full-stack plugin (backend + frontend)
   - Audio effect processor

### Create More Complex Plugins

- **Audio Processing** — Process audio files using NumPy
- **External Integration** — Connect to APIs or services
- **Full-Stack** — Add a UI panel with C# frontend component
- **Custom Engines** — Implement TTS or transcription engines

### Share Your Plugin

- Package your plugin as a zip file
- Share with the community
- Contribute to VoiceStudio ecosystem

---

## Troubleshooting

### Plugin Not Loading

**Check the logs:**
```bash
# Look for error messages in VoiceStudio console output
```

**Common issues:**
- Manifest is invalid JSON — validate with a JSON linter
- `entry_points.backend` doesn't match function name
- Required import paths are missing

### API Endpoints Not Responding

**Check if plugin loaded:**
```bash
curl http://localhost:8000/api/plugins | grep text_transform
```

**If plugin is not in the list:**
- Plugin failed to initialize — check logs
- Manifest validation failed — check manifest.json

### Tests Won't Run

**Ensure pytest is installed:**
```bash
pip install pytest
```

**Run with verbose output:**
```bash
pytest tests/ -vv --tb=short
```

---

## Getting Help

- Check the API reference for method signatures and examples
- Review the best practices guide for common patterns
- Examine the example plugin at `plugins/example_audio_effect/`
- Ask questions in the VoiceStudio community

Happy plugin development!
