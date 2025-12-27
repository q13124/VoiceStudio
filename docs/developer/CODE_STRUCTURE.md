# VoiceStudio Quantum+ Code Structure

Complete guide to the codebase organization and structure.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Key Directories](#key-directories)
3. [Important Files](#important-files)
4. [Code Organization](#code-organization)
5. [Naming Conventions](#naming-conventions)

---

## Project Structure

### Root Directory

```
E:\VoiceStudio/
├── app/                      # Python application core
│   ├── cli/                 # CLI tools and test scripts
│   ├── core/                # Core engine and runtime systems
│   └── ui/                  # UI-related Python code (if any)
├── backend/                 # FastAPI backend
│   ├── api/                 # API routes and handlers
│   └── mcp_bridge/          # MCP integration (future)
├── src/                     # C# frontend source
│   ├── VoiceStudio.App/     # WinUI 3 application
│   └── VoiceStudio.Core/    # Shared core library
├── engines/                 # Engine manifests
│   ├── audio/               # Audio engine manifests
│   ├── image/               # Image engine manifests
│   └── video/               # Video engine manifests
├── docs/                    # Documentation
│   ├── design/              # Architecture and design docs
│   ├── governance/          # Project governance docs
│   ├── user/                # User documentation
│   ├── api/                 # API documentation
│   └── developer/           # Developer documentation
├── shared/                  # Shared contracts
│   └── contracts/           # JSON schemas
├── tools/                   # Development tools and scripts
└── models/                  # Model storage (runtime)
```

---

## Key Directories

### Frontend (`src/VoiceStudio.App/`)

**Views/**
- Panel views (XAML files)
- Shell components
- Window definitions

**ViewModels/**
- Business logic for views
- State management
- Command implementations

**Services/**
- Backend communication (BackendClient)
- Audio playback (AudioPlayerService)
- Other cross-cutting services

**Models/**
- Data structures
- Business entities
- Shared with backend

**Controls/**
- Reusable UI controls
- Custom controls (Waveform, Spectrogram, etc.)

**Resources/**
- Design tokens (DesignTokens.xaml)
- Themes
- Styles

### Backend (`backend/api/`)

**routes/**
- API route handlers
- One file per feature area
- 30+ route files

**models.py / models_additional.py**
- Pydantic models
- Request/response schemas
- Data validation

**ws/**
- WebSocket handlers
- Real-time update broadcasting

### Core (`app/core/`)

**engines/**
- Engine implementations
- Engine protocol
- Engine router
- Quality metrics

**audio/**
- Audio processing utilities
- Quality enhancement functions

**runtime/**
- Engine lifecycle management
- Port management
- Resource management

**training/**
- Training module
- XTTS trainer

### Engines (`engines/`)

**audio/**, **image/**, **video/**
- Engine manifest files
- One directory per engine
- `engine.manifest.json` in each

---

## Important Files

### Frontend

**App.xaml.cs**
- Application entry point
- Service registration
- Application lifecycle

**MainWindow.xaml / MainWindow.xaml.cs**
- Main application window
- Panel layout
- Navigation

**Services/BackendClient.cs**
- HTTP/WebSocket client
- API communication
- Retry logic

**Resources/DesignTokens.xaml**
- Design system tokens
- Colors, typography, spacing

### Backend

**api/main.py**
- FastAPI application
- Route registration
- Middleware setup

**api/models.py**
- Core Pydantic models
- Shared data structures

**api/routes/*.py**
- Individual route modules
- API endpoint handlers

### Core

**core/engines/protocols.py**
- EngineProtocol base class
- Engine interface definition

**core/engines/router.py**
- Engine router
- Dynamic engine loading
- Engine management

**core/engines/xtts_engine.py**
- XTTS v2 engine implementation
- Example engine

**core/audio/audio_utils.py**
- Audio processing utilities
- Quality enhancement

---

## Code Organization

### Frontend Organization

**MVVM Pattern:**
```
View (XAML)
  ↓ Data Binding
ViewModel (C#)
  ↓ Service Calls
Service (C#)
  ↓ HTTP/WebSocket
Backend (Python)
```

**Example:**
- `Views/Panels/ProfilesView.xaml` → View
- `ViewModels/ProfilesViewModel.cs` → ViewModel
- `Services/BackendClient.cs` → Service
- `backend/api/routes/profiles.py` → Backend

### Backend Organization

**Route-Based Organization:**
- One route file per feature
- Routes grouped by prefix
- Shared models in `models.py`

**Example:**
- `routes/profiles.py` → `/api/profiles/*`
- `routes/voice.py` → `/api/voice/*`
- `routes/projects.py` → `/api/projects/*`

### Engine Organization

**Manifest-Based:**
- Engines in `engines/` directory
- Organized by type (audio/image/video)
- Manifest defines engine

**Implementation:**
- Engine classes in `app/core/engines/`
- One file per engine
- All implement `EngineProtocol`

---

## Naming Conventions

### C# Naming

**Classes:** `PascalCase`
```csharp
public class VoiceProfileService { }
public class ProfilesViewModel { }
```

**Methods:** `PascalCase`
```csharp
public async Task<List<VoiceProfile>> GetProfilesAsync() { }
public void OnPropertyChanged() { }
```

**Properties:** `PascalCase`
```csharp
public ObservableCollection<VoiceProfile> Profiles { get; set; }
public bool IsLoading { get; private set; }
```

**Fields:** `_camelCase` (private), `camelCase` (public)
```csharp
private readonly IBackendClient _backendClient;
private bool _isInitialized;
public string Name;
```

**Local Variables:** `camelCase`
```csharp
var profileId = "profile-123";
var response = await GetProfileAsync(profileId);
```

**Constants:** `PascalCase`
```csharp
private const int MaxRetries = 3;
private const string DefaultEngine = "chatterbox";
```

**Interfaces:** `I` prefix
```csharp
public interface IBackendClient { }
public interface IAudioPlayerService { }
```

**Events:** `PascalCase` with `EventHandler` suffix
```csharp
public event EventHandler<PlaybackStateChangedEventArgs> StateChanged;
```

### Python Naming

**Modules:** `snake_case`
```python
# File: profiles.py
# File: voice_synthesis.py
```

**Classes:** `PascalCase`
```python
class VoiceProfile:
    pass

class XTTSEngine(EngineProtocol):
    pass
```

**Functions:** `snake_case`
```python
def list_profiles():
    pass

def synthesize_audio():
    pass
```

**Variables:** `snake_case`
```python
profile_id = "profile-123"
audio_path = "/path/to/audio.wav"
```

**Constants:** `UPPER_SNAKE_CASE`
```python
MAX_RETRIES = 3
DEFAULT_ENGINE = "chatterbox"
```

**Private:** `_leading_underscore`
```python
def _internal_method():
    pass

_private_variable = "value"
```

### XAML Naming

**Controls:** `PascalCase` with type suffix
```xml
<ListView x:Name="ProfilesListView" />
<Button x:Name="CreateProfileButton" />
<TextBlock x:Name="StatusTextBlock" />
```

**Resources:** `PascalCase` with type prefix
```xml
<SolidColorBrush x:Key="PrimaryBrush" />
<Style x:Key="ButtonStyle" />
```

**Design Tokens:** `VSQ.Category.Property` format
```xml
<StaticResource ResourceKey="VSQ.Color.Accent.Primary" />
<StaticResource ResourceKey="VSQ.FontSize.Medium" />
```

---

## File Organization Patterns

### View Files

**Naming:** `{Feature}View.xaml` / `{Feature}View.xaml.cs`
- `ProfilesView.xaml`
- `TimelineView.xaml`
- `EffectsMixerView.xaml`

**Location:** `Views/Panels/` or `Views/Shell/`

### ViewModel Files

**Naming:** `{Feature}ViewModel.cs`
- `ProfilesViewModel.cs`
- `TimelineViewModel.cs`
- `EffectsMixerViewModel.cs`

**Location:** `ViewModels/` or `ViewModels/Panels/`

### Service Files

**Naming:** `{Service}Service.cs` or `I{Service}Service.cs`
- `BackendClient.cs` / `IBackendClient.cs`
- `AudioPlayerService.cs` / `IAudioPlayerService.cs`

**Location:** `Services/`

### Model Files

**Naming:** `{Entity}.cs`
- `VoiceProfile.cs`
- `Project.cs`
- `AudioClip.cs`

**Location:** `Models/` or `Core/Models/`

### Route Files

**Naming:** `{feature}.py`
- `profiles.py` - Voice profiles, reference audio pre-processing
- `voice.py` - Voice synthesis, multi-pass, artifact removal, analysis, prosody, post-processing
- `projects.py` - Project management
- `image_gen.py` - Image generation, face enhancement
- `video_gen.py` - Video generation, temporal consistency
- `training.py` - Training, data optimization

**Location:** `backend/api/routes/`

### Engine Files

**Naming:** `{engine}_engine.py`
- `xtts_engine.py`
- `chatterbox_engine.py`
- `tortoise_engine.py`

**Location:** `app/core/engines/`

---

## Code Patterns

### Dependency Injection

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

### Async/Await Pattern

**Frontend:**
```csharp
public async Task LoadProfilesAsync()
{
    try
    {
        IsLoading = true;
        Profiles = await _backendClient.GetProfilesAsync();
    }
    finally
    {
        IsLoading = false;
    }
}
```

**Backend:**
```python
@router.get("", response_model=List[VoiceProfile])
async def list_profiles() -> List[VoiceProfile]:
    """List all voice profiles."""
    return list(_profiles.values())
```

### Error Handling Pattern

**Frontend:**
```csharp
try
{
    var result = await _backendClient.SynthesizeAsync(request);
    // Handle success
}
catch (HttpRequestException ex)
{
    _logger.LogError(ex, "Synthesis failed");
    await ShowErrorDialogAsync("Synthesis failed. Please try again.");
}
```

**Backend:**
```python
@router.post("", response_model=VoiceProfile)
def create_profile(req: ProfileCreateRequest) -> VoiceProfile:
    try:
        # Create profile
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Data Binding Pattern

**XAML:**
```xml
<TextBlock Text="{x:Bind ViewModel.ProfileName, Mode=OneWay}" />
<Button Command="{x:Bind ViewModel.CreateProfileCommand}" />
```

**ViewModel:**
```csharp
private string _profileName;
public string ProfileName
{
    get => _profileName;
    set
    {
        _profileName = value;
        OnPropertyChanged();
    }
}
```

---

## Module Dependencies

### Frontend Dependencies

```
VoiceStudio.App
  ├── VoiceStudio.Core (Models, Interfaces)
  ├── Microsoft.WindowsAppSDK (WinUI 3)
  ├── CommunityToolkit.WinUI (Controls)
  └── NAudio (Audio playback)
```

### Backend Dependencies

```
backend/api
  ├── fastapi (Web framework)
  ├── uvicorn (ASGI server)
  ├── pydantic (Data validation)
  └── app/core (Engine system)
```

### Core Dependencies

```
app/core
  ├── torch (PyTorch for engines)
  ├── transformers (Hugging Face)
  └── numpy (Numerical operations)
```

---

## Code Quality Standards

### File Size Guidelines

- **Classes:** < 500 lines (target)
- **Methods:** < 50 lines (target)
- **Files:** < 1000 lines (target)

### Complexity Guidelines

- **Cyclomatic Complexity:** < 10 per method
- **Nesting Depth:** < 4 levels
- **Parameters:** < 5 per method

### Documentation Requirements

- **Public APIs:** XML comments (C#) or docstrings (Python)
- **Complex Logic:** Inline comments
- **Classes:** Class-level documentation

---

## New System Files

### Quality Features System

**Backend Routes (`backend/api/routes/`):**
- `voice.py` - Multi-pass synthesis, artifact removal, voice analysis, prosody control, post-processing endpoints
  - `POST /api/voice/synthesize/multipass` - Multi-pass synthesis
  - `POST /api/voice/remove-artifacts` - Artifact removal
  - `POST /api/voice/analyze-characteristics` - Voice characteristic analysis
  - `POST /api/voice/prosody-control` - Prosody control
  - `POST /api/voice/post-process` - Post-processing pipeline
- `profiles.py` - Reference audio pre-processing
  - `POST /api/profiles/{profile_id}/preprocess-reference` - Reference audio pre-processing
- `image_gen.py` - Face enhancement
  - `POST /api/image/enhance-face` - Face enhancement for images/videos
- `video_gen.py` - Temporal consistency
  - `POST /api/video/temporal-consistency` - Temporal consistency enhancement
- `training.py` - Training data optimization
  - `POST /api/training/datasets/{dataset_id}/optimize` - Training data optimization

**Backend Models (`backend/api/models_additional.py`):**
- `MultiPassSynthesizeRequest` - Multi-pass synthesis request model
- `MultiPassSynthesizeResponse` - Multi-pass synthesis response model
- `ArtifactRemovalRequest` - Artifact removal request model
- `ArtifactRemovalResponse` - Artifact removal response model
- `VoiceCharacteristicAnalysisRequest` - Voice analysis request model
- `VoiceCharacteristicAnalysisResponse` - Voice analysis response model
- `ProsodyControlRequest` - Prosody control request model
- `ProsodyControlResponse` - Prosody control response model
- `PostProcessingRequest` - Post-processing request model
- `PostProcessingResponse` - Post-processing response model
- `ReferenceAudioPreprocessRequest` - Reference pre-processing request model
- `ReferenceAudioPreprocessResponse` - Reference pre-processing response model
- `FaceEnhancementRequest` - Face enhancement request model
- `FaceEnhancementResponse` - Face enhancement response model
- `TemporalConsistencyRequest` - Temporal consistency request model
- `TemporalConsistencyResponse` - Temporal consistency response model
- `TrainingDataOptimizationRequest` - Training optimization request model
- `TrainingDataOptimizationResponse` - Training optimization response model

**Frontend Services (`src/VoiceStudio.App/Services/`):**
- `BackendClient.cs` - Quality feature API methods:
  - `SynthesizeMultiPassAsync()` - Multi-pass synthesis
  - `RemoveArtifactsAsync()` - Artifact removal
  - `AnalyzeVoiceCharacteristicsAsync()` - Voice analysis
  - `ControlProsodyAsync()` - Prosody control
  - `PostProcessAsync()` - Post-processing
  - `PreprocessReferenceAudioAsync()` - Reference pre-processing
  - `EnhanceFaceAsync()` - Face enhancement
  - `EnhanceTemporalConsistencyAsync()` - Temporal consistency
  - `OptimizeTrainingDataAsync()` - Training optimization

**Frontend ViewModels (`src/VoiceStudio.App/ViewModels/`):**
- Quality features integrated into existing ViewModels:
  - `VoiceSynthesisViewModel.cs` - Multi-pass synthesis integration
  - `EffectsMixerViewModel.cs` - Artifact removal, post-processing integration
  - `ProfilesViewModel.cs` - Reference pre-processing integration
  - `TrainingViewModel.cs` - Training optimization integration
  - `VideoGenViewModel.cs` - Face enhancement, temporal consistency integration

**Frontend Models (`src/VoiceStudio.Core/Models/`):**
- `MultiPassSynthesizeRequest.cs` - Multi-pass synthesis request
- `MultiPassSynthesizeResponse.cs` - Multi-pass synthesis response
- `ArtifactRemovalRequest.cs` - Artifact removal request
- `ArtifactRemovalResponse.cs` - Artifact removal response
- `VoiceCharacteristicAnalysisRequest.cs` - Voice analysis request
- `VoiceCharacteristicAnalysisResponse.cs` - Voice analysis response
- `ProsodyControlRequest.cs` - Prosody control request
- `ProsodyControlResponse.cs` - Prosody control response
- `PostProcessingRequest.cs` - Post-processing request
- `PostProcessingResponse.cs` - Post-processing response
- `ReferenceAudioPreprocessRequest.cs` - Reference pre-processing request
- `ReferenceAudioPreprocessResponse.cs` - Reference pre-processing response
- `FaceEnhancementRequest.cs` - Face enhancement request
- `FaceEnhancementResponse.cs` - Face enhancement response
- `TemporalConsistencyRequest.cs` - Temporal consistency request
- `TemporalConsistencyResponse.cs` - Temporal consistency response
- `TrainingDataOptimizationRequest.cs` - Training optimization request
- `TrainingDataOptimizationResponse.cs` - Training optimization response

**WebSocket Integration (`backend/api/ws/`):**
- Quality topic support in WebSocket server
- Real-time quality preview events
- Quality metrics streaming

**Documentation (`docs/`):**
- `docs/api/ENDPOINTS.md` - Quality feature endpoints documentation
- `docs/api/EXAMPLES.md` - Quality feature code examples
- `docs/api/QUALITY_FEATURES_QUICK_REFERENCE.md` - Quick reference guide
- `docs/user/USER_MANUAL.md` - User manual quality features section
- `docs/user/TUTORIALS.md` - Quality feature tutorials
- `docs/user/GETTING_STARTED.md` - Quality features quick start
- `docs/user/TROUBLESHOOTING.md` - Quality features troubleshooting
- `docs/developer/ARCHITECTURE.md` - Quality features architecture
- `docs/api/examples/quality_features/` - Quality feature code examples directory

**File Organization:**
- Quality features integrated into existing route files
- No separate quality features directory
- Models organized in `models_additional.py` (backend) and `Models/` (frontend)
- Examples in dedicated `quality_features/` subdirectory

**Key Patterns:**
- All quality features follow REST API patterns
- Preview mode support (analyze without applying)
- Quality metrics returned with all responses
- Real-time updates via WebSocket
- Error handling with user-friendly messages

### Settings System

**Frontend:**
- `src/VoiceStudio.App/Services/ISettingsService.cs` - Settings service interface
- `src/VoiceStudio.App/Services/SettingsService.cs` - Settings service implementation
- `src/VoiceStudio.App/ViewModels/SettingsViewModel.cs` - Settings UI ViewModel
- `src/VoiceStudio.App/Views/Panels/SettingsView.xaml` - Settings UI panel
- `src/VoiceStudio.Core/Models/SettingsData.cs` - Settings data models

**Backend:**
- `backend/api/routes/settings.py` - Settings API routes
- `data/settings.json` - Settings persistence file

**Key Features:**
- 5-minute frontend cache with thread-safe access
- 60-second backend cache to reduce file I/O
- Atomic file writes for safety
- Local storage fallback for offline support
- Category-based settings organization

### Backup & Restore System

**Backend:**
- `backend/api/routes/backup.py` - Backup/restore API routes
- `backups/` - Backup storage directory

**Key Features:**
- Selective component backup (profiles, projects, settings, models)
- ZIP compression for efficient storage
- Disk space validation
- 5GB maximum backup size
- Automatic cleanup of old backups

### Tag Management System

**Backend:**
- `backend/api/routes/tags.py` - Tag management API routes

**Key Features:**
- In-memory tag storage (10,000 tag limit)
- Usage count tracking
- Category-based organization
- Color coding support
- Default system tags (protected from deletion)
- Tag merging capabilities

### Panel Registry System

**Core:**
- `src/VoiceStudio.Core/Panels/IPanelView.cs` - Panel interface
- `src/VoiceStudio.Core/Panels/PanelRegion.cs` - Panel region enum
- `src/VoiceStudio.Core/Panels/IPanelRegistry.cs` - Registry interface
- `src/VoiceStudio.Core/Panels/PanelRegistry.cs` - Registry implementation

**Frontend:**
- `src/VoiceStudio.App/Resources/PanelTemplates.xaml` - Panel templates
- `src/VoiceStudio.App/Controls/PanelTemplateSelector.cs` - Template selector

**Key Features:**
- Centralized panel registry for 100+ panels
- Region-based organization (Left, Center, Right, Bottom, Floating)
- Dynamic panel discovery
- Plugin integration support

## References

- [Architecture Documentation](ARCHITECTURE.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Memory Bank](../design/MEMORY_BANK.md)

---

**Last Updated:** 2025-01-27  
**Version:** 1.1

### Recent Updates

**2025-01-27: Quality Features System**
- Added 9 quality improvement API endpoints
- Integrated quality features into existing routes
- Added quality feature models (backend and frontend)
- Added WebSocket quality topic support
- Created comprehensive documentation (API, user, developer)
- Added code examples for all quality features

- Added Settings System file structure
- Added Backup & Restore System file structure
- Added Tag Management System file structure
- Added Panel Registry System file structure

