# VoiceStudio Quantum+ Developer Guide

Complete developer guide for VoiceStudio Quantum+ including architecture, API documentation, and plugin development.

**Version:** 1.0  
**Last Updated:** 2025-01-28

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [API Documentation](#api-documentation)
4. [Plugin Development](#plugin-development)
5. [Testing](#testing)
6. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- **Python 3.10+** for backend development
- **.NET 8 SDK** for frontend development
- **Visual Studio 2022** or **VS Code** for C# development
- **Windows 10/11** (Windows 17763+)

### Setup

See [SETUP.md](SETUP.md) for complete setup instructions.

**Quick Start:**
```bash
# Backend setup
cd backend/api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd src/VoiceStudio.App
dotnet restore
dotnet build
```

---

## Architecture Overview

VoiceStudio Quantum+ follows a client-server architecture:

```
┌─────────────────────────────────────────────────────────┐
│              WinUI 3 Frontend (C#/.NET 8)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Profiles │  │ Timeline │  │ Effects  │  │ Macros  ││
│  │   View   │  │   View   │  │  Mixer   │  │   View  ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         BackendClient (HTTP/WebSocket)            │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          │
┌─────────────────────────────────────────────────────────┐
│            FastAPI Backend (Python 3.10+)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Profiles │  │  Voice   │  │ Quality  │  │ Engines ││
│  │  Routes  │  │  Routes  │  │  Routes  │  │ Router  ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Engine System (44 Engines)                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Key Components

**Frontend (WinUI 3/C#):**
- MVVM pattern with ViewModels
- Panel-based UI architecture
- Design tokens for consistent styling
- Services for backend communication

**Backend (FastAPI/Python):**
- RESTful API with 133+ endpoints
- WebSocket support for real-time updates
- Engine router for dynamic engine selection
- Quality metrics calculation

**Engine System:**
- Plugin-based architecture
- 44 engines (TTS, STT, image, video)
- Automatic discovery via manifests
- Resource-aware loading

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete architecture documentation.

---

## API Documentation

### OpenAPI Specification

The complete OpenAPI specification is available at:
- **Swagger UI:** `http://localhost:8000/docs` (when backend is running)
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### API Reference

See [API_REFERENCE.md](../api/API_REFERENCE.md) for complete API documentation.

**Key Endpoints:**
- `/api/profiles` - Voice profile management
- `/api/projects` - Project management
- `/api/voice/synthesize` - Voice synthesis
- `/api/quality/analyze` - Quality analysis
- `/api/engines/recommend` - Engine recommendation

### Authentication

Currently, the API does not require authentication for local development. In production, authentication will be added.

### Error Handling

All endpoints return standard HTTP status codes:
- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses follow this format:
```json
{
  "detail": "Error message"
}
```

---

## Plugin Development

### Engine Plugins

Engines are implemented as plugins that implement the `EngineProtocol` interface.

**Creating a New Engine:**

1. Create engine file: `app/core/engines/my_engine.py`
2. Implement `EngineProtocol`:
```python
from app.core.engines.protocols import EngineProtocol

class MyEngine(EngineProtocol):
    def __init__(self, model_path: str, device: str = "cpu"):
        # Initialize engine
        pass
    
    def synthesize(self, text: str, voice_profile_id: str, **kwargs):
        # Implement synthesis
        pass
```

3. Create manifest: `engines/audio/my_engine.json`
```json
{
  "id": "my_engine",
  "name": "My Engine",
  "type": "tts",
  "version": "1.0.0"
}
```

See [ENGINE_PLUGIN_SYSTEM.md](ENGINE_PLUGIN_SYSTEM.md) for complete engine plugin documentation.

### UI Plugins

UI plugins extend the WinUI 3 frontend with custom panels.

**Creating a New Panel:**

1. Create View: `src/VoiceStudio.App/Views/Panels/MyPanelView.xaml`
2. Create ViewModel: `src/VoiceStudio.App/ViewModels/MyPanelViewModel.cs`
3. Register in PanelRegistry

See [PANEL_INTEGRATION_GUIDE.md](../PANEL_INTEGRATION_GUIDE.md) for complete panel integration guide.

---

## Testing

### Test Structure

```
tests/
├── integration/     # Integration tests
├── e2e/            # End-to-end tests
├── unit/            # Unit tests
├── performance/     # Performance tests
└── quality/         # Quality verification
```

### Running Tests

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test suite
pytest tests/integration/engines/test_engine_integration.py -v

# Run with backend
pytest tests/integration/api/test_backend_endpoints.py -v --backend-available
```

### Writing Tests

**Engine Test Example:**
```python
def test_engine_synthesis():
    engine = MyEngine(model_path=None, device="cpu")
    result = engine.synthesize(text="Test", voice_profile_id="test")
    assert result is not None
```

**API Test Example:**
```python
def test_api_endpoint():
    response = requests.get(f"{API_BASE_URL}/profiles")
    assert response.status_code == 200
```

See [TESTING.md](TESTING.md) for complete testing documentation.

---

## Contributing

### Code Standards

- **Python:** Follow PEP 8, use type hints
- **C#:** Follow Microsoft C# coding conventions
- **No Placeholders:** All code must be 100% complete
- **Tests Required:** All new features must include tests

### Pull Request Process

1. Create feature branch
2. Implement feature with tests
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete contribution guidelines.

---

## Additional Resources

- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Code Structure:** [CODE_STRUCTURE.md](CODE_STRUCTURE.md)
- **API Reference:** [../api/API_REFERENCE.md](../api/API_REFERENCE.md)
- **Testing Guide:** [TESTING.md](TESTING.md)
- **Engine Plugin System:** [ENGINE_PLUGIN_SYSTEM.md](ENGINE_PLUGIN_SYSTEM.md)

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

