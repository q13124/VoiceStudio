# VoiceStudio Quantum+ Architecture Documentation

Complete architecture reference for developers working on VoiceStudio Quantum+.

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Frontend Architecture](#frontend-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Engine System Architecture](#engine-system-architecture)
5. [Settings System Architecture](#settings-system-architecture)
6. [Backup & Restore System Architecture](#backup--restore-system-architecture)
7. [Tag Management System Architecture](#tag-management-system-architecture)
8. [Panel Registry System Architecture](#panel-registry-system-architecture)
9. [Quality Features Architecture](#quality-features-architecture)
10. [Quality Testing & Comparison Architecture](#quality-testing--comparison-architecture)
11. [UI Services Architecture](#ui-services-architecture)
12. [Communication Patterns](#communication-patterns)
13. [Data Flow](#data-flow)
14. [Key Design Patterns](#key-design-patterns)

---

## System Architecture Overview

VoiceStudio Quantum+ follows a client-server architecture with clear separation between frontend and backend.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│              WinUI 3 Frontend (C#/.NET 8)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Profiles │  │ Timeline │  │ Effects  │  │ Macros  ││
│  │   View   │  │   View   │  │  Mixer   │  │   View  ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
│                                                          │
│  MVVM Pattern: ViewModels + Services                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │  BackendClient (HTTP/WebSocket Communication)     │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ JSON over HTTP/WebSocket
                       │ (localhost:8000)
                       │
┌──────────────────────▼──────────────────────────────────┐
│         FastAPI Backend (Python 3.10+)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  REST API Routes (520+ endpoints)                │  │
│  │  - /api/profiles, /api/voice, /api/projects      │  │
│  │  - /api/effects, /api/mixer, /api/training       │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  WebSocket Server (/ws/realtime)                 │  │
│  │  - Real-time updates (meters, training, batch)   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Engine Router (Dynamic Engine Discovery)        │  │
│  │  - Loads engines from manifests                   │  │
│  │  - Manages engine lifecycle                       │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Engine Protocol Interface
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Engine Layer (Python)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  XTTS    │  │Chatterbox │  │ Tortoise │  ...        │
│  │   v2     │  │    TTS    │  │   TTS    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  All engines implement EngineProtocol                   │
│  Discovered via engine.manifest.json files              │
└──────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Separation of Concerns:** Frontend handles UI, backend handles processing
2. **Local-First:** All processing happens locally, no cloud dependencies
3. **Extensibility:** Engine system supports unlimited engines via manifests
4. **Quality Focus:** Comprehensive quality metrics throughout
5. **MVVM Pattern:** Clean separation in frontend
6. **RESTful API:** Standard HTTP/JSON communication

---

## Frontend Architecture

### Technology Stack

- **Framework:** WinUI 3 (Windows App SDK)
- **Language:** C# (.NET 8)
- **UI Markup:** XAML
- **Pattern:** MVVM (Model-View-ViewModel)
- **Audio:** NAudio (WASAPI for playback)

### Project Structure

```
src/VoiceStudio.App/
├── MainWindow.xaml          # Main application window
├── MainWindow.xaml.cs       # Window code-behind
├── App.xaml                 # Application resources
├── App.xaml.cs              # Application entry point
│
├── Views/
│   ├── Panels/              # Panel views (XAML)
│   │   ├── ProfilesView.xaml
│   │   ├── TimelineView.xaml
│   │   ├── EffectsMixerView.xaml
│   │   ├── AnalyzerView.xaml
│   │   ├── MacroView.xaml
│   │   └── DiagnosticsView.xaml
│   └── Shell/               # Shell components
│       ├── StatusBarView.xaml
│       └── NavigationView.xaml
│
├── ViewModels/
│   └── Panels/              # ViewModels for panels
│       ├── ProfilesViewModel.cs
│       ├── TimelineViewModel.cs
│       ├── EffectsMixerViewModel.cs
│       ├── AnalyzerViewModel.cs
│       ├── MacroViewModel.cs
│       └── DiagnosticsViewModel.cs
│
├── Services/
│   ├── IBackendClient.cs   # Backend communication interface
│   ├── BackendClient.cs    # HTTP/WebSocket client implementation
│   ├── IAudioPlayerService.cs
│   ├── AudioPlayerService.cs
│   └── KeyboardShortcutService.cs
│
├── Models/
│   ├── VoiceProfile.cs
│   ├── Project.cs
│   ├── AudioClip.cs
│   ├── QualityMetrics.cs
│   └── ...
│
├── Controls/
│   ├── PanelHost.xaml       # Reusable panel container
│   ├── WaveformControl.xaml # Win2D waveform visualization
│   ├── SpectrogramControl.xaml # Win2D spectrogram
│   ├── FaderControl.xaml   # Mixer fader
│   └── ...
│
└── Resources/
    └── DesignTokens.xaml   # Design system tokens (VSQ.*)
```

### MVVM Pattern

**View (XAML):**
- Pure UI markup
- Data binding to ViewModel properties
- Minimal code-behind (only event handlers)

**ViewModel:**
- Implements `INotifyPropertyChanged`
- Contains business logic
- Communicates with Services
- No direct UI references

**Model:**
- Data structures
- Business entities
- Shared with backend via JSON

**Service:**
- Backend communication (IBackendClient)
- Audio playback (IAudioPlayerService)
- Cross-cutting concerns

### Example: ProfilesView MVVM

**View (ProfilesView.xaml):**
```xml
<Grid>
    <ListView ItemsSource="{x:Bind ViewModel.Profiles, Mode=OneWay}">
        <ListView.ItemTemplate>
            <DataTemplate>
                <TextBlock Text="{Binding Name}" />
            </DataTemplate>
        </ListView.ItemTemplate>
    </ListView>
</Grid>
```

**ViewModel (ProfilesViewModel.cs):**
```csharp
public class ProfilesViewModel : INotifyPropertyChanged
{
    private readonly IBackendClient _backendClient;
    private ObservableCollection<VoiceProfile> _profiles;
    
    public ObservableCollection<VoiceProfile> Profiles
    {
        get => _profiles;
        set
        {
            _profiles = value;
            OnPropertyChanged();
        }
    }
    
    public async Task LoadProfilesAsync()
    {
        Profiles = await _backendClient.GetProfilesAsync();
    }
}
```

**Service (BackendClient.cs):**
```csharp
public async Task<List<VoiceProfile>> GetProfilesAsync()
{
    var response = await _httpClient.GetAsync("/api/profiles");
    return await response.Content.ReadFromJsonAsync<List<VoiceProfile>>();
}
```

### Design System

**Design Tokens (DesignTokens.xaml):**
- Colors: `VSQ.Color.Background.*`, `VSQ.Color.Accent.*`
- Typography: `VSQ.FontSize.*`, `VSQ.FontWeight.*`
- Spacing: `VSQ.Spacing.*`
- Corner Radius: `VSQ.CornerRadius.*`

**Usage:**
```xml
<Button Background="{StaticResource VSQ.Color.Accent.Primary}"
        FontSize="{StaticResource VSQ.FontSize.Medium}">
    Click Me
</Button>
```

### Audio Playback

**NAudio Integration:**
- WASAPI for low-latency playback
- Supports WAV, MP3, FLAC
- Real-time VU meters
- Position and duration tracking

**Service Interface:**
```csharp
public interface IAudioPlayerService
{
    Task PlayAsync(string audioUrl);
    Task PauseAsync();
    Task StopAsync();
    double Position { get; }
    double Duration { get; }
    event EventHandler<PlaybackStateChangedEventArgs> StateChanged;
}
```

### UI-Backend Integration

**BackendClient Service:**
- Centralized HTTP/WebSocket communication
- Automatic retry logic (3 retries with 1-second delay)
- Circuit breaker pattern (prevents cascading failures)
- Connection status tracking
- Error handling with user-friendly messages

**API Call Patterns:**
```csharp
// GET request
var profiles = await _backendClient.GetAsync<List<VoiceProfile>>("/api/profiles");

// POST request
var request = new SynthesisRequest { Text = "Hello", ProfileId = "profile123" };
var response = await _backendClient.SendRequestAsync<SynthesisRequest, SynthesisResponse>(
    "/api/synthesize", 
    request
);

// File upload
var fileStream = File.OpenRead(filePath);
var response = await _backendClient.UploadFileAsync(
    "/api/profiles/upload", 
    fileStream, 
    "audio.wav"
);
```

**Error Handling Pattern:**
```csharp
private async Task LoadDataAsync()
{
    try
    {
        IsLoading = true;
        ErrorMessage = null;
        HasError = false;
        
        var data = await _backendClient.GetAsync<List<Item>>("/api/items");
        Items.Clear();
        foreach (var item in data)
        {
            Items.Add(item);
        }
    }
    catch (Exception ex)
    {
        ErrorHandler.LogError(ex, "LoadData");
        ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
        HasError = true;
        _toastNotificationService?.ShowError("Operation Failed", ErrorMessage);
    }
    finally
    {
        IsLoading = false;
    }
}
```

**Input Validation:**
```csharp
// Before backend call
var validation = InputValidator.ValidateSynthesisText(Text);
if (!validation.IsValid)
{
    ErrorMessage = validation.ErrorMessage;
    HasError = true;
    return;
}

// Command CanExecute validation
public bool CanSynthesize => 
    SelectedProfile != null && 
    !string.IsNullOrWhiteSpace(Text) && 
    !IsLoading;
```

**WebSocket Integration:**
```csharp
var webSocketService = _backendClient.WebSocketService;
if (webSocketService != null)
{
    await webSocketService.ConnectAsync(new[] { "synthesis_status", "job_progress" });
    webSocketService.MessageReceived += OnWebSocketMessage;
}

private void OnWebSocketMessage(object sender, WebSocketMessage message)
{
    if (message.Topic == "synthesis_status")
    {
        var status = JsonSerializer.Deserialize<SynthesisStatus>(message.Data);
        UpdateUI(status);
    }
}
```

**UI Controls for Backend Integration:**
- `LoadingOverlay`: Shows loading state during async operations
- `ErrorMessage`: Displays user-friendly error messages
- `HelpOverlay`: Provides contextual help and keyboard shortcuts

---

## Backend Architecture

### Technology Stack

- **Framework:** FastAPI (Python 3.10+)
- **Async:** asyncio for concurrent operations
- **WebSocket:** FastAPI WebSocket support
- **Engine Integration:** Dynamic engine loading

### Project Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI application
│   ├── models.py             # Pydantic models
│   ├── models_additional.py  # Additional models
│   ├── error_handling.py    # Error handlers
│   ├── rate_limiting.py     # Rate limiting middleware
│   │
│   ├── routes/              # API route modules
│   │   ├── profiles.py      # Voice profile endpoints
│   │   ├── voice.py         # Voice synthesis endpoints
│   │   ├── projects.py      # Project management
│   │   ├── tracks.py        # Timeline tracks/clips
│   │   ├── effects.py       # Effects chain
│   │   ├── mixer.py         # Mixer state
│   │   ├── macros.py        # Macro system
│   │   ├── training.py       # Training module
│   │   ├── batch.py         # Batch processing
│   │   ├── transcribe.py    # Transcription
│   │   └── ...              # 30+ route files
│   │
│   └── ws/                  # WebSocket handlers
│       ├── events.py        # Legacy heartbeat
│       └── realtime.py      # Real-time updates
│
app/
├── core/
│   ├── engines/             # Engine implementations
│   │   ├── base.py         # EngineProtocol base
│   │   ├── router.py       # Engine router
│   │   ├── xtts_engine.py
│   │   ├── chatterbox_engine.py
│   │   ├── tortoise_engine.py
│   │   └── whisper_engine.py
│   │
│   ├── audio/               # Audio utilities
│   │   └── audio_utils.py   # Audio processing functions
│   │
│   ├── runtime/             # Runtime services
│   │   ├── engine_lifecycle.py
│   │   ├── port_manager.py
│   │   └── resource_manager.py
│   │
│   └── training/             # Training module
│       └── xtts_trainer.py
│
engines/                     # Engine manifests
├── audio/
│   ├── xtts_v2/
│   │   └── engine.manifest.json
│   ├── chatterbox/
│   │   └── engine.manifest.json
│   └── ...
```

### FastAPI Application

**Main Application (main.py):**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VoiceStudio Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

# Register routes
app.include_router(profiles.router)
app.include_router(voice.router)
app.include_router(projects.router)
# ... 30+ route modules
```

### Route Structure

**Example Route (profiles.py):**
```python
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import ApiOk
from pydantic import BaseModel

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

@router.get("", response_model=List[VoiceProfile])
def list_profiles() -> List[VoiceProfile]:
    """List all voice profiles."""
    return list(_profiles.values())

@router.post("", response_model=VoiceProfile)
def create_profile(req: ProfileCreateRequest) -> VoiceProfile:
    """Create a new voice profile."""
    # Implementation
```

### Error Handling

**Centralized Error Handlers:**
```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### WebSocket Support

**Real-time Updates:**
```python
@app.websocket("/ws/realtime")
async def ws_realtime(ws: WebSocket, topics: str = None):
    """Enhanced WebSocket for real-time updates."""
    topic_list = topics.split(",") if topics else None
    await realtime.connect(ws, topic_list)
```

**Broadcasting:**
```python
async def broadcast_meter_updates(project_id: str, meter_data: dict):
    """Broadcast VU meter updates to subscribed clients."""
    message = {
        "topic": "meters",
        "payload": meter_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await realtime.broadcast("meters", message)
```

---

## Engine System Architecture

### Engine Protocol

All engines implement `EngineProtocol`:

```python
from app.core.engines.protocols import EngineProtocol

class MyEngine(EngineProtocol):
    def __init__(self, device: Optional[str] = None, gpu: bool = True):
        super().__init__(device=device, gpu=gpu)
    
    def initialize(self) -> bool:
        """Initialize the engine model."""
        # Load model, setup device
        self._initialized = True
        return True
    
    def synthesize(self, text: str, **kwargs) -> Union[str, Tuple[str, dict]]:
        """Synthesize audio from text."""
        # Implementation
        return output_path, quality_metrics
```

### Engine Router

**Dynamic Discovery:**
```python
from app.core.engines.router import router

# Auto-load all engines from manifests
router.load_all_engines("engines")

# Get engine instance
engine = router.get_engine("chatterbox", gpu=True)

# List available engines
engines = router.list_engines()  # ["xtts_v2", "chatterbox", "tortoise", ...]
```

### Manifest System

**Engine Manifest (engine.manifest.json):**
```json
{
  "engine_id": "chatterbox",
  "name": "Chatterbox TTS",
  "type": "audio",
  "subtype": "tts",
  "version": "1.0.0",
  "entry_point": "app.core.engines.chatterbox_engine.ChatterboxEngine",
  "dependencies": {
    "torch": ">=2.0.0",
    "transformers": ">=4.30.0"
  },
  "capabilities": [
    "voice_cloning",
    "text_to_speech",
    "emotion_control"
  ],
  "supported_languages": ["en", "es", "fr", "de", ...],
  "device_requirements": {
    "gpu": "recommended",
    "vram_min_gb": 4
  }
}
```

### Engine Lifecycle

1. **Discovery:** Router scans `engines/` for manifests
2. **Loading:** Engine class loaded from entry point
3. **Registration:** Engine registered in router
4. **Initialization:** Engine initialized on first use
5. **Execution:** Engine methods called via router
6. **Cleanup:** Engine cleaned up when done

### Runtime Management

**Lifecycle Manager:**
- Manages engine state (idle, initializing, ready, busy)
- Handles engine lifecycle transitions
- Tracks engine usage

**Port Manager:**
- Allocates ports for engine services
- Manages port conflicts
- Tracks port usage

**Resource Manager:**
- VRAM-aware resource allocation
- Memory management
- GPU device selection

---

## Settings System Architecture

### Overview

The Settings System provides application-wide configuration management with backend persistence and local caching for offline support.

### Architecture Components

**Frontend (`SettingsService.cs`):**
- Implements `ISettingsService` interface
- 5-minute in-memory cache with thread-safe access
- Local storage fallback (Windows.Storage.ApplicationData)
- Backend API integration via `IBackendClient`
- Atomic file operations for safety

**Backend (`backend/api/routes/settings.py`):**
- FastAPI router at `/api/settings`
- 60-second in-memory cache to reduce file I/O
- Atomic file writes using temporary files
- JSON persistence to `data/settings.json`
- Maximum file size: 10MB

### Settings Categories

1. **General Settings:** Theme, language, auto-save
2. **Engine Settings:** Default engines, quality levels
3. **Audio Settings:** Output/input devices, sample rate
4. **Timeline Settings:** Time format, snap, grid
5. **Backend Settings:** API URL, timeout, retry count
6. **Performance Settings:** Caching, threads, memory limits
7. **Plugin Settings:** Enabled plugins list
8. **MCP Settings:** MCP server configuration
9. **Quality Settings:** Quality presets, thresholds, metrics

### Data Flow

```
User changes setting in UI
  ↓
SettingsViewModel.UpdateCategoryAsync()
  ↓
SettingsService.UpdateCategoryAsync()
  ↓
BackendClient.PutAsync("/api/settings/{category}")
  ↓
Backend route handler validates and saves
  ↓
SettingsService updates local cache
  ↓
SettingsService saves to local storage (fallback)
```

### Example Usage

**Frontend:**
```csharp
var settingsService = ServiceProvider.GetSettingsService();
var audioSettings = await settingsService.LoadCategoryAsync<AudioSettings>("audio");
audioSettings.SampleRate = 48000;
await settingsService.UpdateCategoryAsync("audio", audioSettings);
```

**Backend:**
```python
@router.put("/{category}")
async def update_settings_category(category: str, data: Dict):
    settings = load_settings()
    # Validate and update category
    updated = category_class(**data)
    settings.category = updated
    save_settings(settings)
    return updated
```

### Integration with Backup/Restore

Settings are included in backup/restore operations via the `includes_settings` flag in `BackupCreateRequest`.

---

## Backup & Restore System Architecture

### Overview

The Backup & Restore System provides comprehensive data protection with selective component backup, compression, and restore capabilities.

### Architecture Components

**Backend (`backend/api/routes/backup.py`):**
- FastAPI router at `/api/backup`
- ZIP archive creation with compression
- Selective component backup (profiles, projects, settings, models)
- Disk space checking (via psutil)
- Backup size limits (5GB maximum)
- Automatic cleanup of old backups

### Backup Components

1. **Profiles:** Voice profile data and audio samples
2. **Projects:** Project files, audio clips, timelines
3. **Settings:** Application settings (`settings.json`)
4. **Models:** AI model files (optional, can be large)

### Backup Process

```
1. User creates backup request
   ↓
2. Backend validates request (name, components)
   ↓
3. Check disk space availability
   ↓
4. Create temporary directory
   ↓
5. Copy selected components to temp directory
   ↓
6. Create metadata.json with backup info
   ↓
7. Create ZIP archive with compression
   ↓
8. Validate final backup size
   ↓
9. Store backup metadata in memory
   ↓
10. Clean up temporary directory
```

### Restore Process

```
1. User selects backup to restore
   ↓
2. Backend validates backup file exists
   ↓
3. Extract ZIP archive to temp directory
   ↓
4. Validate backup metadata
   ↓
5. Restore selected components
   ↓
6. Update application state
   ↓
7. Clean up temporary files
```

### Example Usage

**Create Backup:**
```python
POST /api/backup
{
    "name": "My Backup",
    "includes_profiles": true,
    "includes_projects": true,
    "includes_settings": true,
    "includes_models": false,
    "description": "Full backup before update"
}
```

**Restore Backup:**
```python
POST /api/backup/{backup_id}/restore
{
    "restore_profiles": true,
    "restore_projects": true,
    "restore_settings": true,
    "restore_models": false
}
```

### Error Handling

- Disk space validation before backup
- File size limits enforced
- Path traversal protection
- Atomic operations where possible
- Comprehensive error messages

---

## Tag Management System Architecture

### Overview

The Tag Management System provides flexible tagging across all resources (profiles, projects, audio clips) with usage tracking and categorization.

### Architecture Components

**Backend (`backend/api/routes/tags.py`):**
- FastAPI router at `/api/tags`
- In-memory storage (10,000 tag limit)
- Usage count tracking
- Category-based organization
- Color coding support
- Default system tags (voice, quality, language)

### Tag Structure

```python
class Tag(BaseModel):
    id: str                    # Unique identifier
    name: str                  # Tag name (unique, case-insensitive)
    category: Optional[str]    # Category grouping
    color: Optional[str]       # Hex color code (#RRGGBB)
    description: Optional[str]  # Tag description
    usage_count: int           # Number of resources using tag
    created: str              # ISO datetime
    modified: str             # ISO datetime
```

### Tag Operations

1. **Create Tag:** Validate name uniqueness, assign ID
2. **Update Tag:** Modify properties, preserve usage count
3. **Delete Tag:** Check usage count, prevent deletion if in use
4. **Get Tags:** Filter by category, search by name/description
5. **Usage Tracking:** Increment/decrement usage counts
6. **Merge Tags:** Combine two tags, transfer usage counts

### Default System Tags

- **Voice Tags:** `tag-voice-*` (e.g., "Male", "Female", "Neutral")
- **Quality Tags:** `tag-quality-*` (e.g., "High", "Standard", "Low")
- **Language Tags:** `tag-language-*` (e.g., "English", "Spanish")

System tags cannot be deleted and are protected.

### Example Usage

**Create Tag:**
```python
POST /api/tags
{
    "name": "Podcast",
    "category": "content-type",
    "color": "#FF5733",
    "description": "Podcast content"
}
```

**Increment Usage:**
```python
POST /api/tags/{tag_id}/increment-usage
```

**Get Tags by Category:**
```python
GET /api/tags?category=content-type
```

### Integration Points

Tags are used across:
- Voice profiles (tagging voice characteristics)
- Projects (content type, genre)
- Audio clips (processing type, quality level)
- Timeline tracks (organization, workflow)

---

## Panel Registry System Architecture

### Overview

The Panel Registry System provides a centralized registry for managing 100+ UI panels with region-based organization and dynamic discovery.

### Architecture Components

**Core (`src/VoiceStudio.Core/Panels/`):**
- `IPanelView` interface: Defines panel contract
- `PanelRegion` enum: Left, Center, Right, Bottom, Floating
- `IPanelRegistry` interface: Registry operations
- `PanelRegistry` implementation: Concrete registry

**Frontend (`src/VoiceStudio.App/`):**
- Panel views in `Views/Panels/`
- ViewModels in `ViewModels/`
- Panel templates in `Resources/PanelTemplates.xaml`
- `PanelTemplateSelector`: Dynamic template selection

### Panel Registration

**Interface:**
```csharp
public interface IPanelView
{
    string PanelId { get; }      // e.g., "Profiles", "Timeline"
    string DisplayName { get; }  // User-visible name
    PanelRegion Region { get; }   // Placement region
}
```

**Registration:**
```csharp
var registry = ServiceProvider.GetPanelRegistry();
registry.RegisterPanel(new PanelDescriptor
{
    PanelId = "Profiles",
    DisplayName = "Voice Profiles",
    Region = PanelRegion.Left,
    ViewType = typeof(ProfilesView),
    ViewModelType = typeof(ProfilesViewModel)
});
```

### Panel Regions

- **Left:** Navigation panels (Profiles, Library, Presets)
- **Center:** Main workspace (Timeline, Mixer, Effects)
- **Right:** Properties panels (Track Properties, Effects Chain)
- **Bottom:** Utility panels (Diagnostics, Logs, Macros)
- **Floating:** Pop-out windows (future)

### Panel Discovery

Panels can be:
1. **Manually Registered:** Explicit registration in code
2. **Auto-Discovered:** Via reflection from `Views/Panels/` directory
3. **Plugin-Loaded:** Dynamic loading from plugins

### Example Usage

**Get Panels for Region:**
```csharp
var leftPanels = registry.GetPanelsForRegion(PanelRegion.Left);
```

**Get Default Panel:**
```csharp
var defaultCenter = registry.GetDefaultPanel(PanelRegion.Center);
```

**Template Selection:**
```xml
<ContentControl Content="{Binding CurrentPanel}"
                ContentTemplateSelector="{StaticResource PanelTemplateSelector}"/>
```

### Integration with Plugin System

Plugins can register panels via:
```csharp
public interface IPlugin
{
    void RegisterPanels(IPanelRegistry registry);
}
```

### Workspace Profiles

Workspace profiles determine which panels appear in each region (Left, Center, Right, Bottom). The toolbar workspace dropdown (Studio, Recording, Mixing, Synthesis, Training, Analysis, Batch Lab, Pro Mix) switches the active profile.

- **Persistence:** Profiles are persisted under `%LocalAppData%/VoiceStudio/WorkspaceProfiles/`. The current workspace is also stored in app settings.
- **Embedded layouts:** When a profile has no saved file or its layout has no regions, the app loads a matching embedded layout from `Resources/Workspaces/*.json` (e.g. `Studio.json`, `Recording.json`). These JSON files use panel IDs that match the panel registry in MainWindow so that `RestorePanelsFromLayout()` can resolve every panel. Embedded workspace JSON is loaded from the application base directory (Content with CopyToOutputDirectory). Packaged (MSIX) deployment may require an additional fallback (e.g. ms-appx or Package.Current.InstalledLocation) if content is not placed in the same path; currently unpackaged and self-contained deployments are the primary target.
- **Single path:** The toolbar workspace switcher uses only PanelStateService; WorkspaceManager is a separate system and is not used for the toolbar. WorkspaceManager (Features/Workspaces) is deprecated for toolbar use; the toolbar and app settings use only PanelStateService and IUnifiedWorkspaceService.
- **Restore scope:** Restore applies only the active panel per region; OpenedPanels is saved but not yet restored (PanelHost single-content model). Multi-tab restore is a future enhancement.

---

## Quality Features Architecture

The Quality Features Architecture implements 9 advanced quality improvement features (IDEA 61-70) that enhance voice cloning, deepfake, and post-processing quality. These features are integrated throughout the system and work together to provide maximum quality output.

### Overview

Quality features are organized into four categories:

1. **Voice Quality Enhancement** - Multi-pass synthesis, artifact removal, voice analysis, prosody control, post-processing
2. **Reference Audio Optimization** - Pre-processing reference audio for optimal cloning
3. **Image/Video Quality Enhancement** - Face enhancement, temporal consistency
4. **Training Data Optimization** - Dataset quality analysis and optimization

### Architecture Components

**Backend Routes (`backend/api/routes/`):**
- `voice.py` - Multi-pass synthesis, artifact removal, voice analysis, prosody control, post-processing
- `profiles.py` - Reference audio pre-processing
- `image_gen.py` - Face enhancement
- `video_gen.py` - Temporal consistency
- `training.py` - Training data optimization

**Frontend Services (`src/VoiceStudio.App/Services/`):**
- `BackendClient.cs` - API communication for quality features
- Quality feature methods integrated into existing services

**Frontend ViewModels (`src/VoiceStudio.App/ViewModels/`):**
- Quality feature ViewModels for UI interaction
- Integration with existing synthesis/editing ViewModels

**WebSocket Integration:**
- Real-time quality preview via `/ws/realtime?topics=quality`
- Quality metrics streaming during processing

### Quality Feature Implementations

#### 1. Multi-Pass Synthesis (IDEA 61)

**Architecture:**
```
User Request → Backend Route → Engine Router
    ↓
For each pass (1 to max_passes):
    ↓
    Engine.synthesize() → Audio Generation
    ↓
    Quality Analysis → Quality Score
    ↓
    Store Pass Result
    ↓
Select Best Pass (highest quality score)
    ↓
Return Best Audio + Quality Metrics
```

**Key Components:**
- **Backend:** `POST /api/voice/synthesize/multipass` in `voice.py`
- **Parameters:** `max_passes`, `pass_preset`, `adaptive`
- **Quality Metrics:** MOS score, similarity, naturalness per pass
- **Adaptive Stopping:** Stops early if quality plateaus

**Data Flow:**
1. Frontend sends multi-pass request with parameters
2. Backend performs multiple synthesis passes
3. Each pass analyzed for quality
4. Best pass selected automatically
5. Quality metrics returned for all passes
6. Real-time updates via WebSocket

#### 2. Reference Audio Pre-Processing (IDEA 62)

**Architecture:**
```
Reference Audio Upload → Pre-Processing Request
    ↓
Audio Analysis:
    - Quality Score Calculation
    - Noise Detection
    - Clipping Detection
    - Distortion Detection
    ↓
Auto-Enhancement (if enabled):
    - Denoising
    - Normalization
    - Artifact Removal
    ↓
Optimal Segment Selection (if enabled):
    - Segment Quality Analysis
    - Best Segments Selection
    ↓
Processed Audio + Analysis Results
```

**Key Components:**
- **Backend:** `POST /api/profiles/{profile_id}/preprocess-reference` in `profiles.py`
- **Analysis:** Quality scoring, artifact detection, segment analysis
- **Enhancement:** Audio processing pipeline
- **Storage:** Processed audio saved, original preserved

**Data Flow:**
1. User uploads reference audio
2. Pre-processing analysis performed
3. Enhancement applied (if enabled)
4. Optimal segments selected (if enabled)
5. Processed audio saved
6. Analysis results returned

#### 3. Artifact Removal (IDEA 63)

**Architecture:**
```
Audio Input → Artifact Detection
    ↓
Artifact Analysis:
    - Click Detection (spectral analysis)
    - Pop Detection (transient analysis)
    - Distortion Detection (harmonic analysis)
    - Glitch Detection (temporal analysis)
    - Phase Issue Detection (phase analysis)
    ↓
Artifact Removal (if not preview):
    - Click Removal (spectral repair)
    - Pop Removal (transient repair)
    - Distortion Repair (harmonic repair)
    - Glitch Repair (temporal repair)
    - Phase Correction (phase alignment)
    ↓
Quality Verification → Repaired Audio
```

**Key Components:**
- **Backend:** `POST /api/voice/remove-artifacts` in `voice.py`
- **Detection:** Multiple detection algorithms per artifact type
- **Removal:** Repair algorithms specific to artifact type
- **Preview Mode:** Analysis without removal

**Data Flow:**
1. User selects audio for artifact removal
2. Preview mode analyzes artifacts (optional)
3. Artifact detection performed
4. Removal applied (if not preview)
5. Quality improvement verified
6. Repaired audio returned

#### 4. Voice Characteristic Analysis (IDEA 64)

**Architecture:**
```
Audio Input → Characteristic Extraction
    ↓
Pitch Analysis:
    - Pitch Tracking (F0 estimation)
    - Pitch Statistics (mean, std, range)
    ↓
Formant Analysis:
    - Formant Extraction (LPC analysis)
    - F1, F2, F3 frequencies
    ↓
Timbre Analysis:
    - Spectral Centroid
    - Spectral Rolloff
    - MFCC Features
    ↓
Prosody Analysis (if enabled):
    - Pitch Contour
    - Rhythm Patterns
    - Stress Patterns
    ↓
Reference Comparison (if provided):
    - Similarity Calculation
    - Preservation Score
    - Recommendations
    ↓
Analysis Results + Recommendations
```

**Key Components:**
- **Backend:** `POST /api/voice/analyze-characteristics` in `voice.py`
- **Analysis:** Pitch, formants, timbre, prosody extraction
- **Comparison:** Similarity calculation with reference
- **Recommendations:** Suggestions for improvement

**Data Flow:**
1. User requests characteristic analysis
2. Audio analyzed for all characteristics
3. Reference compared (if provided)
4. Similarity/preservation scores calculated
5. Recommendations generated
6. Analysis results returned

#### 5. Prosody Control (IDEA 65)

**Architecture:**
```
Audio Input → Prosody Analysis
    ↓
Prosody Modification:
    - Intonation Pattern Application
    - Pitch Contour Adjustment
    - Rhythm Adjustment
    - Stress Marker Application
    ↓
Quality Verification → Processed Audio
```

**Key Components:**
- **Backend:** `POST /api/voice/prosody-control` in `voice.py`
- **Patterns:** Rising, falling, flat intonation
- **Contour:** Custom pitch curve support
- **Stress:** Word-level stress markers

**Data Flow:**
1. User configures prosody settings
2. Prosody analysis performed
3. Modifications applied
4. Quality verified
5. Processed audio returned

#### 6. Face Enhancement (IDEA 66)

**Architecture:**
```
Image/Video Input → Face Detection
    ↓
Face Analysis:
    - Resolution Score
    - Artifact Score
    - Alignment Score
    - Realism Score
    ↓
Face Enhancement (multi-stage if enabled):
    - Upscaling
    - Artifact Removal
    - Alignment Correction
    - Realism Enhancement
    ↓
Quality Verification → Enhanced Media
```

**Key Components:**
- **Backend:** `POST /api/image/enhance-face` in `image_gen.py`
- **Presets:** Portrait, full_body, close_up
- **Multi-Stage:** Multiple enhancement passes
- **Face-Specific:** Face-focused algorithms

**Data Flow:**
1. User selects image/video for enhancement
2. Face detection and analysis performed
3. Enhancement applied (multi-stage if enabled)
4. Quality verified
5. Enhanced media returned

#### 7. Temporal Consistency (IDEA 67)

**Architecture:**
```
Video Input → Frame Analysis
    ↓
Temporal Analysis:
    - Frame Stability Calculation
    - Motion Smoothness Analysis
    - Flicker Detection
    - Jitter Detection
    ↓
Temporal Smoothing:
    - Frame-to-Frame Smoothing
    - Motion Consistency Enforcement
    - Artifact Removal
    ↓
Quality Verification → Processed Video
```

**Key Components:**
- **Backend:** `POST /api/video/temporal-consistency` in `video_gen.py`
- **Smoothing:** Configurable smoothing strength (0.0-1.0)
- **Motion:** Motion consistency enforcement
- **Detection:** Temporal artifact detection

**Data Flow:**
1. User selects video for enhancement
2. Temporal analysis performed
3. Smoothing applied
4. Quality verified
5. Processed video returned

#### 8. Training Data Optimization (IDEA 68)

**Architecture:**
```
Dataset Input → Quality Analysis
    ↓
Per-Sample Analysis:
    - Quality Score Calculation
    - Diversity Analysis
    - Coverage Analysis
    ↓
Optimal Sample Selection:
    - Quality-Based Selection
    - Diversity-Based Selection
    - Coverage-Based Selection
    ↓
Augmentation Suggestions:
    - Data Augmentation Strategies
    - Diversity Improvement
    ↓
Optimized Dataset + Recommendations
```

**Key Components:**
- **Backend:** `POST /api/training/datasets/{dataset_id}/optimize` in `training.py`
- **Analysis:** Quality, diversity, coverage scoring
- **Selection:** Optimal sample selection algorithms
- **Augmentation:** Strategy suggestions

**Data Flow:**
1. User requests dataset optimization
2. All samples analyzed
3. Optimal samples selected
4. Augmentation suggestions generated
5. Optimized dataset created
6. Results returned

#### 9. Post-Processing Pipeline (IDEA 70)

**Architecture:**
```
Media Input → Stage Configuration
    ↓
For each stage (in optimized order):
    ↓
    Stage Processing:
        - Denoise (audio)
        - Normalize (audio)
        - Enhance (audio/image/video)
        - Repair (audio)
        - Upscale (image/video)
        - Temporal Smoothing (video)
    ↓
    Quality Analysis → Stage Result
    ↓
    Store Stage Result
    ↓
Combine Stage Results → Final Output
```

**Key Components:**
- **Backend:** `POST /api/voice/post-process` in `voice.py`
- **Stages:** Configurable processing stages
- **Order Optimization:** Automatic stage order optimization
- **Preview Mode:** Preview without applying

**Data Flow:**
1. User configures post-processing stages
2. Stage order optimized (if enabled)
3. Each stage processed sequentially
4. Quality tracked per stage
5. Final output combined
6. Results returned

#### 10. Real-Time Quality Preview (IDEA 69)

**Architecture:**
```
Processing Operation → Quality Monitoring
    ↓
Real-Time Quality Updates:
    - Quality Score Updates
    - Stage Progress Updates
    - Pass Progress Updates
    - Artifact Detection Updates
    ↓
WebSocket Broadcasting:
    - Quality Topic Subscription
    - Real-Time Event Publishing
    ↓
Frontend Display:
    - Quality Metrics Display
    - Progress Visualization
    - Trend Analysis
```

**Key Components:**
- **WebSocket:** `/ws/realtime?topics=quality`
- **Events:** Quality updates during processing
- **Frontend:** Real-time quality display

**Data Flow:**
1. User starts processing operation
2. Quality monitoring enabled
3. Real-time updates published via WebSocket
4. Frontend subscribes to quality topic
5. Updates displayed in real-time
6. User can make decisions based on quality

### Quality Metrics System

**Metrics Calculated:**
- **MOS Score:** Mean Opinion Score (1.0-5.0)
- **Similarity:** Voice similarity to reference (0.0-1.0)
- **Naturalness:** Speech naturalness (0.0-1.0)
- **SNR:** Signal-to-noise ratio (dB)
- **Artifact Score:** Artifact presence (0.0-1.0, lower is better)
- **Quality Score:** Overall quality (0.0-1.0)

**Quality Calculation:**
```python
quality_score = weighted_average(
    mos_score_normalized,
    similarity,
    naturalness,
    snr_normalized,
    1.0 - artifact_score
)
```

### Integration Points

**With Voice Synthesis:**
- Multi-pass synthesis integrated into synthesis pipeline
- Quality metrics returned with all synthesis results
- Real-time quality preview during synthesis

**With Engine System:**
- Quality features work with all engines
- Engine-specific quality optimizations
- Quality-aware engine selection

**With Effects System:**
- Post-processing pipeline uses effect system
- Artifact removal integrates with effects
- Quality-aware effect application

**With Training System:**
- Training data optimization integrated
- Quality metrics for training evaluation
- Quality-aware training recommendations

### Performance Considerations

**Processing Time:**
- Multi-pass: 3-10x normal synthesis time
- Artifact removal: +10-30% processing time
- Post-processing: +20-50% processing time
- Face enhancement: +30-60% (images), +100-200% (videos)
- Temporal consistency: +50-100% processing time

**Memory Usage:**
- Multi-pass: High (stores multiple passes)
- Post-processing: Moderate-High (temporary buffers)
- Temporal consistency: High (frame buffers)
- Most features: Low-Moderate

**Optimization Strategies:**
- Adaptive stopping for multi-pass
- Preview mode to avoid unnecessary processing
- Caching of analysis results
- Streaming for large files

### Error Handling

**Quality Feature Errors:**
- Invalid input validation
- Processing failure recovery
- Quality degradation detection
- Resource exhaustion handling

**Error Recovery:**
- Fallback to standard processing
- Partial results if processing fails
- Clear error messages with recommendations

---

## Quality Testing & Comparison Architecture

The Quality Testing & Comparison Architecture provides comprehensive tools for evaluating, comparing, and optimizing voice synthesis quality. This architecture includes A/B Testing, Engine Recommendation, Quality Benchmarking, and Quality Dashboard features.

### Overview

Quality testing features are organized into four main components:

1. **A/B Testing** (IDEA 46) - Side-by-side comparison of two synthesis configurations
2. **Engine Recommendation** (IDEA 47) - AI-powered engine selection based on quality requirements
3. **Quality Benchmarking** (IDEA 52) - Comprehensive testing across multiple engines
4. **Quality Dashboard** (IDEA 49) - Visual overview of quality metrics and trends

### Architecture Components

**Backend Routes (`backend/api/routes/`):**
- `eval_abx.py` - A/B testing endpoints (`/api/eval/abx/start`, `/api/eval/abx/results`)
- `quality.py` - Engine recommendation, benchmarking, dashboard endpoints

**Frontend Components:**
- `ABTestingView.xaml` / `ABTestingViewModel.cs` - A/B testing UI
- Quality Dashboard panel (if implemented)
- Integration with Voice Synthesis panel for recommendations

**Backend Services:**
- `QualityOptimizer` - Engine recommendation algorithm
- `QualityComparison` - Quality comparison utilities
- Quality metrics calculation system

### A/B Testing Architecture

**Data Flow:**
```
User Input → ABTestingViewModel → BackendClient
    → POST /api/eval/abx/start
    → Synthesize Sample A & B
    → Calculate Quality Metrics
    → Compare & Return Results
```

**Key Components:**
- Frontend: `ABTestingView`, `ABTestingViewModel`
- Backend: `eval_abx.py` routes
- Models: `AbxStartRequest`, `AbxResult`

### Engine Recommendation Architecture

**Data Flow:**
```
User Requirements → GET /api/quality/engine-recommendation
    → QualityOptimizer.suggest_engine()
    → Evaluate Engines Against Requirements
    → Select Best Match
    → Return Recommendation + Reasoning
```

**Key Components:**
- Backend: `quality.py::get_engine_recommendation()`
- Algorithm: `QualityOptimizer` with engine evaluation
- Models: `EngineRecommendationResponse`

### Quality Benchmarking Architecture

**Data Flow:**
```
User Input → POST /api/quality/benchmark
    → For Each Engine:
        → Initialize Engine
        → Synthesize Audio
        → Calculate Quality Metrics
        → Measure Performance
    → Aggregate & Rank Results
    → Return BenchmarkResponse
```

**Key Components:**
- Backend: `quality.py::run_benchmark()`
- Engine Router integration
- Quality metrics calculation
- Models: `BenchmarkRequest`, `BenchmarkResponse`, `BenchmarkResult`

### Quality Dashboard Architecture

**Data Flow:**
```
User Request → GET /api/quality/dashboard
    → Aggregate Quality Metrics (from database/future)
    → Calculate Trends
    → Analyze Distribution
    → Generate Alerts & Insights
    → Return Dashboard Data
```

**Key Components:**
- Backend: `quality.py::get_quality_dashboard()`
- Data aggregation (future: database)
- Models: `QualityDashboardResponse`

### Integration Points

**With Engine System:**
- All features use Engine Router for synthesis
- Engine characteristics used for recommendations
- Engine performance tracked in benchmarks

**With Quality Metrics:**
- All features use quality metrics calculation
- MOS, similarity, naturalness, SNR tracked
- Quality trends analyzed in dashboard

**With WebSocket:**
- Real-time quality updates (IDEA 69)
- Benchmark progress updates
- Dashboard real-time updates

### Performance Considerations

**A/B Testing:**
- Parallel synthesis of both samples
- Response time: < 500ms to start, < 100ms for results

**Engine Recommendation:**
- Cached recommendations for common requirements
- Response time: < 200ms

**Quality Benchmarking:**
- Sequential or parallel engine testing
- Response time: < 120s for 3 engines

**Quality Dashboard:**
- Cached dashboard data
- Response time: < 300ms

For complete architecture details, see [Quality Features Architecture](QUALITY_FEATURES_ARCHITECTURE.md) and [Quality Features Diagrams](QUALITY_FEATURES_DIAGRAMS.md).

---
- Logging for debugging

### Example Usage

**Multi-Pass Synthesis:**
```python
POST /api/voice/synthesize/multipass
{
    "profile_id": "profile-123",
    "text": "Hello, world!",
    "engine": "chatterbox",
    "max_passes": 5,
    "pass_preset": "naturalness_focus",
    "adaptive": true
}
```

**Artifact Removal:**
```python
POST /api/voice/remove-artifacts
{
    "audio_id": "audio-123",
    "artifact_types": ["clicks", "pops", "distortion"],
    "repair_preset": "comprehensive",
    "preview": false
}
```

**Post-Processing:**
```python
POST /api/voice/post-process
{
    "audio_id": "audio-123",
    "enhancement_stages": ["denoise", "normalize", "enhance", "repair"],
    "optimize_order": true,
    "preview": false
}
```

---

## UI Services Architecture

VoiceStudio Quantum+ includes several UI services that enhance user experience and provide consistent functionality across panels.

### Overview

The UI services architecture provides:
- **Context-Sensitive Actions:** Action bars in panel headers (IDEA 2)
- **Enhanced Drag-and-Drop:** Visual feedback during drag operations (IDEA 4)
- **Global Search:** Search across all content types (IDEA 5)
- **Panel Resizing:** Resize handles for panels (IDEA 9)
- **Contextual Menus:** Right-click menus for interactive elements (IDEA 10)
- **Toast Notifications:** User-friendly notifications (IDEA 11)
- **Multi-Select:** Multi-item selection with batch operations (IDEA 12)
- **Undo/Redo:** Visual indicator for undo/redo operations (IDEA 15)

### Service Registration

All UI services are registered in `ServiceProvider.cs`:

```csharp
// UI Services
services.AddSingleton<ContextMenuService>();
services.AddSingleton<MultiSelectService>();
services.AddSingleton<DragDropVisualFeedbackService>();
services.AddSingleton<UndoRedoService>();
services.AddSingleton<ToastNotificationService>();
services.AddSingleton<RecentProjectsService>();
```

### ContextMenuService

**Purpose:** Provides contextual right-click menus for interactive elements.

**Location:** `src/VoiceStudio.App/Services/ContextMenuService.cs`

**Usage:**
```csharp
// Inject service
private readonly ContextMenuService _contextMenuService;

// Create context menu
var menu = _contextMenuService.CreateContextMenu("timeline", contextData);

// Attach to element
element.ContextFlyout = menu;
```

**Supported Contexts:**
- `timeline`: Timeline clips, tracks, empty area
- `profile`: Profile cards
- `audio`: Audio files
- `effect`: Effects and channels
- `track`: Track headers
- `clip`: Timeline clips
- `marker`: Timeline markers

**Integration Example:**
```csharp
private void TimelineClip_RightTapped(object sender, RightTappedRoutedEventArgs e)
{
    var menu = _contextMenuService.CreateContextMenu("clip", selectedClip);
    menu.ShowAt(sender as UIElement, e.GetPosition(sender as UIElement));
}
```

### MultiSelectService

**Purpose:** Manages multi-select state across panels with visual indicators.

**Location:** `src/VoiceStudio.App/Services/MultiSelectService.cs`

**Usage:**
```csharp
// Inject service
private readonly MultiSelectService _multiSelectService;

// Get panel state
var state = _multiSelectService.GetState("timeline");

// Add item to selection
state.Add(selectedItem);

// Check if item is selected
if (state.Contains(item))
{
    // Item is selected
}

// Clear selection
_multiSelectService.ClearSelection("timeline");
```

**Selection Methods:**
- **Ctrl+Click:** Add item to selection
- **Shift+Click:** Select range
- **Ctrl+A:** Select all

**Visual Indicators:**
- Selected items highlighted
- Selection count badge in panel header
- Batch operations available

**Integration Example:**
```csharp
private void Item_Click(object sender, RoutedEventArgs e)
{
    var item = (sender as FrameworkElement)?.DataContext as Item;
    var state = _multiSelectService.GetState("timeline");
    
    if (Keyboard.Modifiers.HasFlag(ModifierKeys.Control))
    {
        // Toggle selection
        if (state.Contains(item))
            state.Remove(item);
        else
            state.Add(item);
    }
    else
    {
        // Single selection
        state.Clear();
        state.Add(item);
    }
    
    UpdateVisualSelection();
}
```

### DragDropVisualFeedbackService

**Purpose:** Provides enhanced visual feedback during drag-and-drop operations.

**Location:** `src/VoiceStudio.App/Services/DragDropVisualFeedbackService.cs`

**Usage:**
```csharp
// Inject service
private readonly DragDropVisualFeedbackService _dragDropService;

// Create drag preview
var preview = _dragDropService.CreateDragPreview(sourceElement, "Item Label");

// Show drop target indicator
_dragDropService.ShowDropTargetIndicator(targetElement, isValid: true);

// Hide drop target indicator
_dragDropService.HideDropTargetIndicator();
```

**Features:**
- Drag preview with label
- Drop target highlighting
- Valid/invalid drop indicators
- Smooth animations

**Integration Example:**
```csharp
private void Item_DragStarting(UIElement sender, DragStartingEventArgs args)
{
    var preview = _dragDropService.CreateDragPreview(sender, item.Name);
    args.DragUI.SetContentFromDataPackage();
}

private void Target_DragOver(object sender, DragEventArgs e)
{
    var isValid = CanDrop(e.DataView);
    _dragDropService.ShowDropTargetIndicator(sender as UIElement, isValid);
    e.AcceptedOperation = isValid ? DataPackageOperation.Move : DataPackageOperation.None;
}
```

### UndoRedoService

**Purpose:** Manages undo/redo operations with visual indicator support.

**Location:** `src/VoiceStudio.App/Services/UndoRedoService.cs`

**Usage:**
```csharp
// Inject service
private readonly UndoRedoService _undoRedoService;

// Create undoable action
var action = new UndoableAction
{
    ActionName = "Delete Clip",
    Execute = () => DeleteClip(clip),
    Undo = () => RestoreClip(clip)
};

// Execute action
_undoRedoService.Execute(action);

// Undo last action
_undoRedoService.Undo();

// Redo last undone action
_undoRedoService.Redo();

// Check availability
if (_undoRedoService.CanUndo)
{
    var nextAction = _undoRedoService.NextUndoActionName;
}
```

**Visual Indicator:**
- Shows undo/redo count
- Displays action names in tooltips
- Updates automatically

**Integration Example:**
```csharp
private void DeleteClip(Clip clip)
{
    var action = new UndoableAction
    {
        ActionName = "Delete Clip",
        Execute = () =>
        {
            _clips.Remove(clip);
            OnPropertyChanged(nameof(Clips));
        },
        Undo = () =>
        {
            _clips.Add(clip);
            OnPropertyChanged(nameof(Clips));
        }
    };
    
    _undoRedoService.Execute(action);
}
```

### ToastNotificationService

**Purpose:** Displays user-friendly toast notifications for important events.

**Location:** `src/VoiceStudio.App/Services/ToastNotificationService.cs`

**Usage:**
```csharp
// Inject service (requires container StackPanel)
private readonly ToastNotificationService _toastService;

// Show success toast
_toastService.ShowSuccess("Profile created successfully");

// Show error toast
_toastService.ShowError("Failed to save project", "Error", viewDetailsAction);

// Show warning toast
_toastService.ShowWarning("Low disk space remaining");

// Show info toast
_toastService.ShowInfo("Synthesis completed");

// Show progress toast
var progressToast = _toastService.ShowProgress("Processing...", "Synthesizing audio");
// Update progress
progressToast.UpdateProgress(0.5); // 50%
// Complete
progressToast.Complete("Synthesis complete");
```

**Toast Types:**
- **Success:** Green, auto-dismiss (3 seconds)
- **Error:** Red, manual dismiss
- **Warning:** Yellow, auto-dismiss (5 seconds)
- **Info:** Blue, auto-dismiss (5 seconds)
- **Progress:** Progress indicator with completion

**Integration Example:**
```csharp
private async Task SynthesizeVoiceAsync()
{
    try
    {
        _toastService.ShowProgress("Synthesizing...", "Generating audio");
        var result = await _backendClient.SynthesizeAsync(request);
        _toastService.ShowSuccess("Audio synthesized successfully");
    }
    catch (Exception ex)
    {
        _toastService.ShowError($"Synthesis failed: {ex.Message}", "Error");
    }
}
```

### PanelResizeHandle Control

**Purpose:** Resize handle control for panels with visual feedback.

**Location:** `src/VoiceStudio.App/Controls/PanelResizeHandle.xaml` and `.xaml.cs`

**Usage:**
```xml
<controls:PanelResizeHandle
    ResizeDirection="Horizontal"
    TargetElement="{Binding ElementName=MyPanel}" />
```

**Properties:**
- `ResizeDirection`: Horizontal, Vertical, or Both
- `TargetElement`: Element to resize

**Integration Example:**
```xml
<Grid>
    <Grid Name="MyPanel">
        <!-- Panel content -->
    </Grid>
    <controls:PanelResizeHandle
        ResizeDirection="Horizontal"
        TargetElement="{Binding ElementName=MyPanel}"
        HorizontalAlignment="Right"
        Width="4" />
</Grid>
```

### UndoRedoIndicator Control

**Purpose:** Visual indicator for undo/redo operations.

**Location:** `src/VoiceStudio.App/Controls/UndoRedoIndicator.xaml` and `.xaml.cs`

**Usage:**
```xml
<controls:UndoRedoIndicator
    UndoRedoService="{Binding UndoRedoService}" />
```

**Properties:**
- `UndoRedoService`: Reference to UndoRedoService instance

**Integration Example:**
```xml
<StatusBar>
    <controls:UndoRedoIndicator
        UndoRedoService="{x:Bind ViewModel.UndoRedoService}" />
</StatusBar>
```

### IPanelActionable Interface

**Purpose:** Interface for panels that provide context-sensitive header actions.

**Location:** `src/VoiceStudio.Core/Panels/IPanelActionable.cs`

**Usage:**
```csharp
public class MyPanelViewModel : ViewModelBase, IPanelActionable
{
    public IEnumerable<PanelHeaderAction> GetHeaderActions()
    {
        yield return new PanelHeaderAction
        {
            Icon = "➕",
            Name = "Add Item",
            KeyboardShortcut = "Ctrl+N",
            Command = AddItemCommand,
            IsEnabled = CanAddItem
        };
        
        yield return new PanelHeaderAction
        {
            Icon = "🗑️",
            Name = "Delete",
            KeyboardShortcut = "Delete",
            Command = DeleteCommand,
            IsEnabled = HasSelection
        };
    }
}
```

**PanelHeaderAction Properties:**
- `Icon`: Icon symbol or emoji
- `Name`: Action name/tooltip text
- `KeyboardShortcut`: Keyboard shortcut hint
- `Command`: Command to execute
- `IsEnabled`: Whether action is enabled
- `IsVisible`: Whether action is visible

**Integration:**
- PanelHost automatically detects `IPanelActionable` panels
- Actions appear in panel header
- Maximum 4 actions recommended

### RecentProjectsService

**Purpose:** Manages recent projects history with pinning support.

**Location:** `src/VoiceStudio.App/Services/RecentProjectsService.cs`

**Features:**
- Tracks last 10 opened projects
- Supports pinning up to 3 favorite projects
- Automatic tracking when projects are opened
- Persistent storage across sessions
- Observable collections for UI binding

**Usage:**
```csharp
// Inject service
private readonly RecentProjectsService _recentProjectsService;

// Add project to recent list
await _recentProjectsService.AddRecentProjectAsync(projectPath, projectName);

// Pin a project
await _recentProjectsService.PinProjectAsync(projectPath);

// Unpin a project
await _recentProjectsService.UnpinProjectAsync(projectPath);

// Remove from recent
await _recentProjectsService.RemoveRecentProjectAsync(projectPath);

// Clear all recent (keeps pinned)
await _recentProjectsService.ClearRecentProjectsAsync();
```

**Properties:**
- `RecentProjects`: IReadOnlyList<RecentProject> - Recent projects (excluding pinned)
- `PinnedProjects`: IReadOnlyList<RecentProject> - Pinned projects
- `AllProjects`: IReadOnlyList<RecentProject> - All projects (pinned first, then recent)

**RecentProject Model:**
```csharp
public class RecentProject
{
    public string Name { get; set; }
    public string Path { get; set; }
    public DateTime LastAccessed { get; set; }
    public bool IsPinned { get; set; }
}
```

**Integration Example:**
```csharp
// In ViewModel
public IReadOnlyList<RecentProject> RecentProjects => 
    _recentProjectsService.AllProjects;

// When opening a project
private async Task OpenProjectAsync(string projectPath)
{
    // Open project...
    await _recentProjectsService.AddRecentProjectAsync(
        projectPath, 
        Path.GetFileNameWithoutExtension(projectPath)
    );
}
```

**Storage:**
- Stored in Windows ApplicationData.LocalSettings
- JSON serialization
- Automatic loading on service initialization
- Automatic saving on changes

**Limits:**
- Maximum 10 recent projects
- Maximum 3 pinned projects
- Oldest projects automatically removed when limit reached

### Best Practices

1. **Service Injection:** Always inject services via constructor
2. **State Management:** Use MultiSelectService for selection state
3. **Visual Feedback:** Use DragDropVisualFeedbackService for drag operations
4. **User Feedback:** Use ToastNotificationService for important events
5. **Undo/Redo:** Wrap all user actions in UndoableAction
6. **Context Menus:** Use ContextMenuService for right-click menus
7. **Panel Actions:** Implement IPanelActionable for header actions
8. **Resize Handles:** Add PanelResizeHandle to resizable panels
9. **Recent Projects:** Use RecentProjectsService to track project access

### Extension Points

**Custom Context Menus:**
- Extend ContextMenuService with new context types
- Add custom menu items per context

**Custom Toast Types:**
- Extend ToastNotificationService with custom toast types
- Add custom animations and styles

**Custom Undoable Actions:**
- Implement IUndoableAction interface
- Create composite actions for complex operations

---

## Communication Patterns

### REST API Communication

**Request Flow:**
```
Frontend (C#)
  ↓ HTTP POST /api/voice/synthesize
  ↓ JSON: { "text": "...", "profile_id": "..." }
Backend (Python)
  ↓ Process request
  ↓ Call engine
  ↓ Return JSON: { "audio_id": "...", "quality_metrics": {...} }
Frontend (C#)
  ↓ Parse response
  ↓ Update UI
```

### WebSocket Communication

**Connection:**
```csharp
var ws = new ClientWebSocket();
await ws.ConnectAsync(new Uri("ws://localhost:8000/ws/realtime?topics=meters,training"), cancellationToken);
```

**Receiving Updates:**
```csharp
while (ws.State == WebSocketState.Open)
{
    var message = await ReceiveMessageAsync(ws);
    if (message.Topic == "meters")
    {
        UpdateVUMeters(message.Payload);
    }
}
```

**Backend Broadcasting:**
```python
await broadcast_meter_updates(project_id, meter_data)
```

### Error Handling

**Retry Logic:**
```csharp
private async Task<T> ExecuteWithRetryAsync<T>(
    Func<Task<T>> operation, 
    int maxRetries = 3)
{
    for (int attempt = 0; attempt <= maxRetries; attempt++)
    {
        try
        {
            return await operation();
        }
        catch (HttpRequestException ex) when (attempt < maxRetries)
        {
            await Task.Delay(TimeSpan.FromSeconds(Math.Pow(2, attempt)));
        }
    }
    throw new AggregateException("Failed after retries");
}
```

---

## Data Flow

### Voice Synthesis Flow

```
1. User enters text in UI
   ↓
2. ViewModel calls BackendClient.SynthesizeAsync()
   ↓
3. BackendClient sends POST /api/voice/synthesize
   ↓
4. Backend route handler receives request
   ↓
5. Route handler calls EngineRouter.get_engine()
   ↓
6. EngineRouter returns engine instance
   ↓
7. Engine.synthesize() called
   ↓
8. Engine processes and returns audio + metrics
   ↓
9. Backend returns JSON response
   ↓
10. BackendClient receives response
   ↓
11. ViewModel updates with results
   ↓
12. UI updates via data binding
```

### Project Save Flow

```
1. User clicks Save
   ↓
2. ViewModel collects project data
   ↓
3. BackendClient.SaveProjectAsync()
   ↓
4. POST /api/projects/{id}
   ↓
5. Backend saves project data
   ↓
6. Backend saves audio files to project directory
   ↓
7. Response confirms save
   ↓
8. UI shows save confirmation
```

### Real-time Updates Flow

```
1. Backend detects change (e.g., VU meter update)
   ↓
2. Backend calls broadcast_meter_updates()
   ↓
3. WebSocket message sent to all subscribers
   ↓
4. Frontend WebSocket client receives message
   ↓
5. Message parsed and routed to handler
   ↓
6. ViewModel property updated
   ↓
7. UI updates via data binding
```

---

## Key Design Patterns

### 1. MVVM Pattern

**Separation:**
- View: XAML markup only
- ViewModel: Business logic, state management
- Model: Data structures

**Benefits:**
- Testability
- Maintainability
- Reusability

### 2. Service Locator / Dependency Injection

**Service Registration:**
```csharp
// In App.xaml.cs
services.AddSingleton<IBackendClient, BackendClient>();
services.AddSingleton<IAudioPlayerService, AudioPlayerService>();
```

**Usage:**
```csharp
public ProfilesViewModel(IBackendClient backendClient)
{
    _backendClient = backendClient;
}
```

### 3. Repository Pattern

**Backend Storage:**
- In-memory storage (current)
- Can be replaced with database
- Abstracted behind route handlers

### 4. Factory Pattern

**Engine Creation:**
```python
engine = router.get_engine("chatterbox", gpu=True)
# Router creates engine instance based on manifest
```

### 5. Observer Pattern

**WebSocket Updates:**
- Backend broadcasts events
- Frontend subscribes to topics
- Automatic UI updates

### 6. Strategy Pattern

**Engine Selection:**
- Different engines for different use cases
- Quality-based routing
- User selection

---

## Performance Considerations

### Frontend

- **Async/Await:** All I/O operations are async
- **Data Binding:** Efficient property change notifications
- **Win2D:** Hardware-accelerated graphics
- **NAudio:** Low-latency audio playback

### Backend

- **FastAPI:** High-performance async framework
- **Engine Pooling:** Reuse engine instances
- **Caching:** Cache frequently accessed data
- **Resource Management:** VRAM-aware allocation

### Communication

- **HTTP/2:** Efficient request multiplexing
- **WebSocket:** Persistent connection for real-time updates
- **JSON:** Lightweight serialization
- **Compression:** Gzip compression for large responses

---

## Security Considerations

### Local-First Architecture

- All processing happens locally
- No external API calls
- No data sent to cloud services

### Input Validation

- Pydantic models validate all inputs
- Type checking at API boundaries
- Sanitization of user input

### Error Handling

- No sensitive data in error messages
- Proper exception handling
- Logging without exposing secrets

---

## Extension Points

### Adding New Engines

1. Create engine directory in `engines/`
2. Create `engine.manifest.json`
3. Implement engine class
4. Engine auto-discovers on startup

### Adding New API Endpoints

1. Create route file in `backend/api/routes/`
2. Define route handlers
3. Register router in `main.py`
4. Document in API docs

### Adding New UI Panels

1. Create View XAML file
2. Create ViewModel class
3. Register in PanelRegistry
4. Add to navigation

---

## References

- [Engine Manifest System](../design/ENGINE_MANIFEST_SYSTEM.md)
- [Engine Extensibility](../design/ENGINE_EXTENSIBILITY.md)
- [VoiceStudio Architecture](../design/VoiceStudio-Architecture.md)
- [Memory Bank](../design/MEMORY_BANK.md)

---

**Last Updated:** 2025-01-27  
**Version:** 1.1

### Recent Updates

- Added Settings System Architecture documentation
- Added Backup & Restore System Architecture documentation
- Added Tag Management System Architecture documentation
- Added Panel Registry System Architecture documentation

