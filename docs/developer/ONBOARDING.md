# VoiceStudio Quantum+ Developer Onboarding Guide

Welcome to VoiceStudio Quantum+! This guide will help you get started as a new developer on the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Overview](#project-overview)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Key Concepts](#key-concepts)
6. [Resources](#resources)
7. [Next Steps](#next-steps)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Windows 10/11** (development environment)
- **Visual Studio 2022** (Community or higher)
- **.NET 8 SDK**
- **Python 3.10+**
- **Git**
- **Basic knowledge of:**
  - C# and .NET
  - Python
  - XAML (for UI)
  - REST APIs
  - MVVM pattern

### Quick Start

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-repo/voicestudio.git
   cd voicestudio
   ```

2. **Set Up Development Environment:**

   - Follow [SETUP.md](SETUP.md) for detailed setup instructions
   - Install all prerequisites (.NET 8 SDK, Python 3.10+, Visual Studio 2022)
   - Install dependencies (Python packages, NuGet packages)
   - Set up Python virtual environment

3. **Run the Application:**

   - Start backend: `python -m uvicorn backend.api.main:app`
   - Open `src/VoiceStudio.App/VoiceStudio.App.csproj` in Visual Studio
   - Run the application (F5)

4. **Verify Installation:**
   - Backend should start on `http://localhost:8000`
   - Frontend should launch and connect to backend
   - Check Diagnostics panel for connection status

---

## Project Overview

### What is VoiceStudio Quantum+?

VoiceStudio Quantum+ is a professional voice cloning and audio production studio with:

- Multiple voice cloning engines (XTTS v2, Chatterbox TTS, Tortoise TTS)
- Professional timeline editor
- Comprehensive audio effects (17 types)
- Quality metrics and enhancement features
- Modern WinUI 3 interface

### Architecture

**High-Level Architecture:**

```
WinUI 3 Frontend (C#/.NET 8)
    ↓ HTTP/WebSocket
FastAPI Backend (Python 3.10+)
    ↓ Engine Protocol
Engine Layer (Python)
```

**Key Technologies:**

- **Frontend:** WinUI 3, C#, XAML, MVVM
- **Backend:** FastAPI, Python
- **Engines:** Python-based voice cloning engines
- **Communication:** REST API, WebSocket

### Project Goals

- **Quality:** State-of-the-art voice cloning quality
- **Performance:** Fast synthesis and processing
- **Usability:** Intuitive, professional interface
- **Extensibility:** Easy to add new engines and features

---

## Project Structure

### Directory Layout

```
VoiceStudio/
├── app/                      # Python application core
│   ├── cli/                 # CLI tools
│   ├── core/                # Core systems (engines, audio processing)
│   └── ui/                  # UI-related Python code
├── backend/                 # FastAPI backend
│   ├── api/                 # API routes
│   │   ├── routes/          # Route handlers
│   │   ├── models/          # Pydantic models
│   │   └── main.py         # FastAPI app
│   └── mcp_bridge/          # MCP integration (future)
├── src/                     # C# frontend
│   ├── VoiceStudio.App/    # WinUI 3 application
│   │   ├── Views/          # XAML views
│   │   ├── ViewModels/     # ViewModels
│   │   ├── Services/       # Services
│   │   └── Controls/       # Custom controls
│   └── VoiceStudio.Core/   # Shared core library
│       ├── Models/         # Data models
│       └── Panels/         # Panel interfaces
├── engines/                 # Engine manifests
│   ├── audio/              # Audio engine manifests
│   ├── image/              # Image engine manifests
│   └── video/              # Video engine manifests
├── docs/                    # Documentation
│   ├── design/             # Architecture docs
│   ├── governance/         # Project governance
│   ├── user/               # User documentation
│   ├── api/                # API documentation
│   └── developer/          # Developer documentation
├── shared/                  # Shared contracts
│   └── contracts/          # JSON schemas
├── tools/                   # Development tools
└── models/                  # Model storage (runtime)
```

### Key Directories

**Frontend (`src/VoiceStudio.App/`):**

- `Views/` - XAML UI files
- `ViewModels/` - MVVM ViewModels
- `Services/` - Application services
- `Controls/` - Custom UI controls
- `Converters/` - Value converters

**Backend (`backend/api/`):**

- `routes/` - API route handlers
- `models/` - Pydantic request/response models
- `main.py` - FastAPI application entry point

**Core (`app/core/`):**

- `engines/` - Engine implementations
- `audio/` - Audio processing
- `utils/` - Utility functions

---

## Development Workflow

### 1. Understanding the Codebase

**Start Here:**

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
2. Read [CODE_STRUCTURE.md](CODE_STRUCTURE.md) - Code organization
3. Read [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

**Key Files to Understand:**

- `backend/api/main.py` - Backend entry point
- `src/VoiceStudio.App/App.xaml.cs` - Frontend entry point
- `src/VoiceStudio.App/ViewModels/` - ViewModels
- `backend/api/routes/` - API routes

### 2. Making Changes

**Workflow:**

1. **Create Feature Branch:**

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes:**

   - Follow code style guidelines
   - Write tests for new functionality
   - Update documentation

3. **Test Changes:**

   - Run unit tests
   - Test manually
   - Verify no regressions

4. **Commit Changes:**

   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

5. **Push and Create PR:**
   ```bash
   git push origin feature/my-feature
   ```
   - Create pull request on GitHub
   - Wait for code review

### 3. Code Review Process

**Before Submitting:**

- [ ] Code follows style guidelines
- [ ] No TODO comments or placeholders
- [ ] Error handling implemented
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No code duplication

**Review Checklist:**

- Code quality and style
- Functionality correctness
- Test coverage
- Documentation completeness
- Performance considerations

### 4. Building the Application

**Frontend Build:**

```bash
# Using Visual Studio
# Build → Build Solution (Ctrl+Shift+B)

# Using Command Line
cd src/VoiceStudio.App
dotnet build
```

**Backend Build:**

- Python is interpreted, no build step required
- Ensure backend/dev dependencies are installed: `pip install -r backend/requirements.txt`
- Ensure engine dependencies are installed:
  - XTTS CPU profile:
    - `powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'`
  - XTTS GPU profile (sm_120):
    - `powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-gpu-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts -Gpu 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'`
  - Full engine stack (all engines; longer install):
    - `powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-full-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile full 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'`
  - Logs land in `.buildlogs\engine-deps-install*.log`.

**Full Build Process:**
See [SETUP.md](SETUP.md#building-from-source) for complete build instructions.

### 5. Testing

**Types of Tests:**

- **Unit Tests:** Test individual functions/classes
- **Integration Tests:** Test API endpoints
- **E2E Tests:** Test complete workflows
- **Performance Tests:** Test performance characteristics

**Running Tests:**

```bash
# Python tests
pytest tests/

# C# tests (Visual Studio Test Explorer)
# Or: dotnet test
```

**Testing Setup:**

- See [SETUP.md](SETUP.md#running-tests) for detailed testing instructions
- See [TESTING.md](TESTING.md) for comprehensive testing guide

---

## Key Concepts

### MVVM Pattern

**Model-View-ViewModel:**

- **Model:** Data and business logic
- **View:** XAML UI files
- **ViewModel:** Connects View and Model

**Example:**

```csharp
// ViewModel
public class ProfilesViewModel : ViewModelBase
{
    private readonly IBackendClient _backendClient;
    public ObservableCollection<Profile> Profiles { get; }

    public ICommand LoadProfilesCommand { get; }
}

// View (XAML)
<Page DataContext="{x:Bind ViewModel}">
    <ListView ItemsSource="{x:Bind ViewModel.Profiles}" />
</Page>
```

### Engine Protocol

**All engines implement `EngineProtocol`:**

```python
class MyEngine(EngineProtocol):
    def initialize(self) -> None:
        # Initialize engine
        pass

    def synthesize(self, text: str, **kwargs) -> bytes:
        # Synthesize speech
        pass

    def cleanup(self) -> None:
        # Cleanup resources
        pass
```

### API Communication

**Frontend → Backend:**

- HTTP REST API for synchronous operations
- WebSocket for real-time updates

**Example:**

```csharp
// Frontend (C#)
var response = await _backendClient.SynthesizeAsync(
    profileId: "profile-123",
    text: "Hello, world!"
);
```

```python
# Backend (Python)
@router.post("/api/voice/synthesize")
async def synthesize(request: VoiceSynthesizeRequest):
    # Process request
    return VoiceSynthesizeResponse(...)
```

### Services

**Service Pattern:**

- Services provide reusable functionality
- Injected via dependency injection
- Examples: `IBackendClient`, `IAudioPlayerService`, `IUpdateService`

**Example:**

```csharp
public class MyViewModel : ViewModelBase
{
    private readonly IBackendClient _backendClient;

    public MyViewModel(IBackendClient backendClient)
    {
        _backendClient = backendClient;
    }
}
```

---

## Resources

### Documentation

**Essential Reading:**

- [SETUP.md](SETUP.md) - **Start here!** Complete development setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [CODE_STRUCTURE.md](CODE_STRUCTURE.md) - Code organization
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [ENGINE_PLUGIN_SYSTEM.md](ENGINE_PLUGIN_SYSTEM.md) - Engine development

**Developer Guides:**

- [SERVICES.md](SERVICES.md) - All services documentation
- [SERVICE_EXAMPLES.md](SERVICE_EXAMPLES.md) - Service usage examples
- [TESTING.md](TESTING.md) - Testing guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - **Developer troubleshooting** - Common issues and solutions
- [BUILD_AND_DEPLOYMENT.md](BUILD_AND_DEPLOYMENT.md) - Build and deployment guide

**User Documentation:**

- [User Manual](../user/USER_MANUAL.md) - User features
- [API Documentation](../api/COMPLETE_ENDPOINT_DOCUMENTATION.md) - Complete API reference
- [OpenAPI Specification](../api/OPENAPI_SPECIFICATION.md) - OpenAPI/Swagger docs
- [User Troubleshooting](../user/TROUBLESHOOTING.md) - User-facing troubleshooting

### External Resources

**Technologies:**

- [WinUI 3 Documentation](https://learn.microsoft.com/en-us/windows/apps/winui/winui3/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [.NET 8 Documentation](https://learn.microsoft.com/en-us/dotnet/)
- [Python 3.10 Documentation](https://docs.python.org/3.10/)

**Tools:**

- [Visual Studio 2022](https://visualstudio.microsoft.com/)
- [Postman](https://www.postman.com/) - API testing
- [Git](https://git-scm.com/) - Version control

### Getting Help

**Internal:**

- Check documentation first
- Search existing issues
- Ask team members

**External:**

- Stack Overflow
- Technology documentation
- Community forums

---

## Next Steps

### Week 1: Orientation

1. **Day 1-2: Setup**

   - Complete development environment setup
   - Run the application
   - Explore the codebase

2. **Day 3-4: Understanding**

   - Read architecture documentation
   - Understand key concepts
   - Review existing code

3. **Day 5: First Contribution**
   - Pick a small task
   - Make your first change
   - Submit pull request

### Week 2-4: Active Development

1. **Pick Tasks:**

   - Start with small, well-defined tasks
   - Gradually take on larger features
   - Ask for help when needed

2. **Learn by Doing:**

   - Work on real features
   - Review code from others
   - Participate in code reviews

3. **Build Expertise:**
   - Focus on specific areas
   - Become expert in domain
   - Share knowledge with team

### Ongoing: Growth

1. **Continuous Learning:**

   - Stay updated with technology
   - Learn new patterns
   - Improve skills

2. **Contribution:**

   - Contribute to codebase
   - Help other developers
   - Improve documentation

3. **Innovation:**
   - Suggest improvements
   - Propose new features
   - Experiment with ideas

---

## Common Tasks

### Adding a New API Endpoint

1. **Create Route Handler:**

   ```python
   # backend/api/routes/my_feature.py
   @router.post("/api/my-feature")
   async def my_endpoint(request: MyRequest):
       # Implementation
       return MyResponse(...)
   ```

2. **Add to Main App:**

   ```python
   # backend/api/main.py
   from backend.api.routes import my_feature
   app.include_router(my_feature.router)
   ```

3. **Add Frontend Method:**

   ```csharp
   // IBackendClient.cs
   Task<MyResponse> MyFeatureAsync(MyRequest request);

   // BackendClient.cs
   public async Task<MyResponse> MyFeatureAsync(MyRequest request)
   {
       // Implementation
   }
   ```

### Adding a New UI Panel

1. **Create ViewModel:**

   ```csharp
   // ViewModels/MyPanelViewModel.cs
   public class MyPanelViewModel : ViewModelBase
   {
       // Properties and commands
   }
   ```

2. **Create View:**

   ```xml
   <!-- Views/Panels/MyPanelView.xaml -->
   <UserControl>
       <Grid>
           <!-- UI content -->
       </Grid>
   </UserControl>
   ```

3. **Register Panel:**
   - Add to `PanelTemplates.xaml`
   - Register in `PanelTemplateSelector.cs`

### Adding a New Engine

1. **Create Engine Class:**

   ```python
   # app/core/engines/my_engine.py
   class MyEngine(EngineProtocol):
       # Implement protocol
   ```

2. **Create Manifest:**

   ```json
   // engines/audio/my_engine.manifest.json
   {
     "id": "my_engine",
     "name": "My Engine",
     "type": "audio"
     // ...
   }
   ```

3. **Register Engine:**
   - Add to `app/core/engines/__init__.py`
   - Engine automatically discovered

---

## Troubleshooting

### Common Issues

**Backend won't start:**

- Check Python environment is activated
- Verify dependencies installed: `pip install -r backend/requirements.txt`
- Check port 8000 is available
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#backend-wont-start) for detailed solutions

**Frontend won't build:**

- Run `dotnet restore` to restore NuGet packages
- Clean and rebuild: `dotnet clean && dotnet build`
- Verify .NET 8 SDK is installed: `dotnet --version`
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#build-errors) for detailed solutions

**Connection failed:**

- Verify backend is running on `http://localhost:8000`
- Check backend health: `curl http://localhost:8000/health`
- Verify firewall isn't blocking the connection
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#runtime-errors) for detailed solutions

**For more troubleshooting help:**

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for comprehensive troubleshooting guide
- Check [SETUP.md](SETUP.md#common-development-issues) for setup-related issues

## Tips for Success

### Code Quality

- **Follow Style Guidelines:** Consistent code style (see [CODE_STYLE_GUIDE.md](CODE_STYLE_GUIDE.md))
- **Write Tests:** Test your code thoroughly (see [TESTING.md](TESTING.md))
- **Document Code:** Clear comments and documentation
- **No Placeholders:** 100% complete implementations only
- **Error Handling:** Always handle errors properly (see [ERROR_HANDLING_PATTERNS.md](ERROR_HANDLING_PATTERNS.md))

### Communication

- **Ask Questions:** Don't hesitate to ask
- **Share Knowledge:** Help others learn
- **Provide Feedback:** Constructive code reviews
- **Be Respectful:** Professional communication

### Productivity

- **Start Small:** Begin with small tasks
- **Iterate:** Make incremental improvements
- **Learn Continuously:** Stay updated
- **Use Services:** Leverage existing services (see [SERVICES.md](SERVICES.md))
- **Have Fun:** Enjoy the development process

---

## Summary

**Welcome to VoiceStudio Quantum+!**

You now have:

- ✅ Development environment set up
- ✅ Understanding of project structure
- ✅ Knowledge of key concepts
- ✅ Resources for learning
- ✅ Path forward

**Remember:**

- Start with small tasks
- Ask for help when needed
- Learn by doing
- Contribute actively

**Happy Coding!**

---

**Last Updated:** 2025-01-28  
**Version:** 1.0.0
