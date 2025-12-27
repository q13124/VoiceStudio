# VoiceStudio Architecture
## Current Architecture and Design Patterns

**Version:** 2.0  
**Last Updated:** 2025  
**Purpose:** Definitive architecture reference for VoiceStudio project

---

## 🏗️ High-Level Architecture

```
[WinUI 3 App (C#)]
      |
      |  JSON over HTTP/WebSocket
      v
[Backend API (Python/FastAPI)]
      |
      |  internal calls
      v
[MCP Bridge Layer] ---> [MCP Servers (Figma/Magic/Flux/Shadcn/etc.)]
      |
      v
[Engine Layer] ---> [XTTS, Whisper, RVC, etc.]
```

---

## 📁 Project Structure

### Active Project (`E:\VoiceStudio`)

```
E:\VoiceStudio/
├── app/
│   ├── cli/                    # CLI tools and tests
│   ├── core/
│   │   ├── engines/           # TTS/VC/ASR engines
│   │   │   ├── xtts_engine.py
│   │   │   └── __init__.py
│   │   ├── pipelines/         # Audio processing pipelines
│   │   ├── plugins_api/       # Plugin system API
│   │   ├── runtime/           # Runtime services
│   │   └── storage/           # Storage abstractions
│   └── ui/
│       ├── panels/            # UI panels
│       ├── themes/            # Theme files
│       └── VoiceStudio.App/   # WinUI 3 application
├── backend/
│   └── api/                   # FastAPI backend
│       ├── main.py
│       ├── models.py
│       ├── routes/
│       └── ws/
├── docs/
│   ├── design/                # Architecture and design docs
│   └── governance/            # Migration and rules
└── src/
    ├── VoiceStudio.App/        # WinUI 3 frontend
    └── VoiceStudio.Core/       # Shared core library
```

---

## 🔧 Engine Layer Architecture

### Engine Registry System

Engines are organized by type in `engines/` directory:

```
engines/
├── audio/          # Audio engines (TTS, VC, ASR)
├── image/          # Image engines (generation, upscaling)
└── video/          # Video engines (generation, enhancement)
```

Each engine has an `engine.manifest.json` file describing:
- Engine metadata (ID, name, version)
- Dependencies and requirements
- Model paths (using `%PROGRAMDATA%\VoiceStudio\models`)
- Capabilities and configuration schema
- Entry point class path

### Engine Protocol

All engines must implement `EngineProtocol` from `app/core/engines/protocols.py`:

```python
from app.core.engines.protocols import EngineProtocol

class MyEngine(EngineProtocol):
    def __init__(self, device: Optional[str] = None, gpu: bool = True):
        super().__init__(device=device, gpu=gpu)
        # Engine-specific initialization
    
    def initialize(self) -> bool:
        """Initialize the engine model"""
        # Load model, setup device, etc.
        self._initialized = True
        return True
    
    def cleanup(self):
        """Clean up resources"""
        # Free memory, clear cache, etc.
        self._initialized = False
```

**Required Methods:**
- `initialize()` - Initialize the engine model
- `cleanup()` - Clean up resources

**Inherited Methods:**
- `is_initialized()` - Check initialization status
- `get_device()` - Get current device
- `get_info()` - Get engine metadata

### Current Engines

- **XTTS Engine** (`app/core/engines/xtts_engine.py`)
  - Coqui TTS 0.27.2 with XTTS v2
  - Voice cloning and synthesis
  - Multi-language support

### Engine Integration

Engines are integrated via:
- Backend API routes (`backend/api/routes/`)
- Plugin system (`app/core/plugins_api/`)
- CLI tools (`app/cli/`)

---

## 🎨 UI Architecture

### WinUI 3 Frontend

- **Location:** `src/VoiceStudio.App/`
- **Pattern:** MVVM (Model-View-ViewModel)
- **Framework:** WinUI 3 1.5.0 on .NET 8.0

### Panel System

- **PanelHost:** Reusable container for panels
- **PanelRegistry:** Dynamic panel registration
- **PanelStack:** Tabbed panel support
- **Design Tokens:** Centralized styling

### Theme System

- **Themes:** Dark, SciFi, Light
- **Density:** Compact, Comfort
- **ThemeManager:** Runtime theme switching

---

## 🔌 Backend API Architecture

### FastAPI Structure

```
backend/api/
├── main.py              # FastAPI app
├── models.py            # Pydantic models
├── models_additional.py # Additional models
├── routes/              # API route modules
│   ├── tts.py
│   ├── asr.py
│   ├── voice.py
│   └── ...
└── ws/
    └── events.py        # WebSocket events
```

### API Endpoints

- **TTS:** `/api/tts/synthesize`
- **ASR:** `/api/asr/align`
- **Voice:** `/api/voice/blend`, `/api/voice/morph`
- **Analysis:** `/api/analyze/spectrogram`
- **WebSocket:** `/ws/events`

---

## 📦 Plugin System

### Plugin Architecture

- **Location:** `app/core/plugins_api/`
- **Format:** Signed `.ucpkg` files
- **Isolation:** Subprocess-based
- **Loading:** Dynamic plugin discovery

### Plugin Interface

Plugins must implement:
- Plugin manifest
- Entry points
- Configuration schema
- Lifecycle hooks

---

## 🔄 Data Flow

### Voice Synthesis Flow

```
UI (WinUI 3)
  ↓ HTTP POST
Backend API (/api/tts/synthesize)
  ↓
XTTS Engine (app/core/engines/xtts_engine.py)
  ↓
Coqui TTS Model
  ↓
Audio Output
  ↓ WebSocket
UI (Real-time updates)
```

### Transcription Flow

```
UI (WinUI 3)
  ↓ HTTP POST
Backend API (/api/asr/align)
  ↓
Whisper Engine
  ↓
Transcript + Timestamps
  ↓ JSON Response
UI (Display transcript)
```

---

## 🎯 Design Patterns

### MVVM Pattern
- **View:** XAML UserControl
- **ViewModel:** C# class with ObservableObject
- **Model:** Data models in Core library

### Dependency Injection
- Services registered in DI container
- ViewModels receive dependencies via constructor
- Backend clients injected into ViewModels

### Event-Driven Architecture
- WebSocket for real-time updates
- Event handlers in ViewModels
- UI updates via data binding

---

## 🔐 Configuration Management

### Configuration Files

- **Settings:** `%APPDATA%/VoiceStudio/settings.json`
- **Layout:** `%APPDATA%/VoiceStudio/layouts/{workspace}.json`
- **Models:** `E:\VoiceStudio_models\...` (configurable)
- **Cache:** `E:\VoiceStudio_data\...` (configurable)

### Environment Variables

- `VOICESTUDIO_MODELS_PATH` - Model storage path
- `VOICESTUDIO_DATA_PATH` - Data/cache path
- `VOICESTUDIO_DEVICE` - Force device selection (cuda/cpu)

---

## 🚀 Deployment Architecture

### Development
- **Frontend:** Visual Studio 2022
- **Backend:** Python FastAPI with uvicorn
- **Hot Reload:** Enabled for both

### Production
- **Frontend:** MSIX package or NSIS installer
- **Backend:** Standalone executable or service
- **Models:** Separate installation package

---

## 📚 Key Technologies

### Frontend
- WinUI 3 1.5.0
- .NET 8.0
- CommunityToolkit.Mvvm
- CommunityToolkit.WinUI

### Backend
- Python 3.10.15
- FastAPI 0.115.0
- PyTorch 2.2.2+cu121
- Coqui TTS 0.27.2
- Transformers 4.55.4

### Audio Processing
- Librosa 0.11.0
- SoundFile 0.12.1
- NumPy 1.26.4

---

## 🔗 Related Documents

- **Technical Stack:** `TECHNICAL_STACK_SPECIFICATION.md`
- **Migration Rules:** `../governance/Cursor-Migration-Ruleset.md`
- **Operational Ruleset:** `CURSOR_OPERATIONAL_RULESET.md`
- **Panel Implementation:** `PANEL_IMPLEMENTATION_GUIDE.md`

---

**This architecture document is the authoritative reference for all development work on VoiceStudio.**

