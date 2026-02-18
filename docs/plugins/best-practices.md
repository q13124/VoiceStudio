# Plugin Development Best Practices

This guide covers patterns, anti-patterns, and best practices for creating high-quality VoiceStudio plugins.

---

## 1. Architecture Patterns

### Backend Plugin Patterns

#### Pattern 1: The Router-Service Split

For complex plugins, separate your FastAPI router from your business logic:

**✅ GOOD**:

```python
# plugin.py - Router and FastAPI integration
from fastapi import APIRouter
from typing import Any
from pydantic import BaseModel

class ProcessRequest(BaseModel):
    text: str
    options: dict[str, Any]

async def process(request: ProcessRequest) -> dict:
    service = TextProcessingService()
    return service.transform(request.text, request.options)

# plugin.py - RegisterRoute
def register(self, app):
    router = APIRouter(prefix="/api/plugin/text_process")
    router.post("/process")(process)
    app.include_router(router)

# service.py - Business logic
class TextProcessingService:
    def transform(self, text: str, options: dict) -> dict:
        # Pure business logic, testable independently
        return {"result": text.upper()}
```

**Advantages**:
- Routes are thin and focused on FastAPI concerns
- Service is testable without FastAPI TestClient
- Clear separation of concerns
- Easy to reuse service logic

**❌ POOR**:

```python
# plugin.py - Everything mixed together
def register(self, app):
    @app.post("/api/plugin/text_process/process")
    async def process_route(request: ProcessRequest):
        # Business logic mixed with routing
        if not request.text:
            return {"error": "empty"}
        transformed = request.text.upper()
        saved = save_to_db(transformed)  # I/O mixed in
        
        # Too much happening in one function
        return {"result": transformed, "saved": saved}
```

**Problems**:
- Hard to test without full FastAPI setup
- I/O and business logic mixed
- Route handler does too much
- Tight coupling

#### Pattern 2: Data Models at Boundaries

Always use Pydantic for request/response validation:

**✅ GOOD**:

```python
from pydantic import BaseModel, Field, validator

class AudioProcessRequest(BaseModel):
    audio_file: bytes = Field(..., description="Raw audio bytes")
    sample_rate: int = Field(..., gt=0, description="Sample rate in Hz")
    effects: list[str] = Field(default=[], description="Effects to apply")
    
    @validator('effects')
    def validate_effects(cls, v):
        allowed = {"normalize", "amplify", "fade"}
        invalid = set(v) - allowed
        if invalid:
            raise ValueError(f"Unknown effects: {invalid}")
        return v

class AudioProcessResponse(BaseModel):
    processed_bytes: bytes = Field(..., description="Processed audio")
    applied_effects: list[str]
    processing_time_ms: float
```

**Advantages**:
- Input validated automatically
- Type hints enforce contracts
- API documentation generated
- Clear boundaries

**❌ POOR**:

```python
@router.post("/process")
async def process(request: dict):
    # No validation - accepts anything
    audio = request.get("audio")  # Could be None
    sample_rate = request.get("sample_rate", 44100)  # Wrong default
    
    # Defensive checks scattered everywhere
    if audio is None:
        return {"error": "..."}
    if not isinstance(sample_rate, int):
        return {"error": "..."}
    # ... more checks
```

#### Pattern 3: Dependency Injection

Initialize dependencies in constructor, not in functions:

**✅ GOOD**:

```python
class MyPlugin(BasePlugin):
    def __init__(self, plugin_dir: Path):
        metadata = PluginMetadata(plugin_dir / "manifest.json")
        super().__init__(metadata)
        
        # Initialize dependencies once
        self.db = Database()
        self.cache = Cache()
        self.logger = logging.getLogger(self.name)
    
    async def process_request(self, request: dict):
        # Dependencies are ready
        cached = self.cache.get(request["id"])
        if cached:
            return cached
        
        result = self.db.query(request["id"])
        self.cache.set(request["id"], result)
        return result
```

**Advantages**:
- Dependencies initialized once, not per request
- Easy to mock for testing
- Clear where dependencies come from
- Better performance

**❌ POOR**:

```python
@router.post("/process")
async def process(request: dict):
    # Creating dependencies in every request
    db = Database()  # New connection every time!
    cache = Cache()  # New cache every time!
    
    # This is inefficient and hard to test
    result = db.query(request["id"])
    return result
```

### Frontend Plugin Patterns

#### Pattern 1: MVVM with Async Operations

**✅ GOOD**:

```csharp
public class MyViewModel : INotifyPropertyChanged
{
    private readonly IBackendClient _backend;
    private string _status = "Idle";
    private bool _isLoading;
    
    public string Status
    {
        get => _status;
        set => SetProperty(ref _status, value);
    }
    
    public bool IsLoading
    {
        get => _isLoading;
        set => SetProperty(ref _isLoading, value);
    }
    
    public RelayCommand RefreshCommand { get; }
    
    public MyViewModel(IBackendClient backend)
    {
        _backend = backend;
        RefreshCommand = new RelayCommand(async () => await RefreshAsync());
    }
    
    public async Task RefreshAsync(CancellationToken ct = default)
    {
        try
        {
            IsLoading = true;
            Status = "Loading...";
            
            var data = await _backend.GetAsync<Data>(
                "/api/plugin/my_plugin/data"
            );
            
            Status = "Ready";
        }
        catch (Exception ex)
        {
            Status = $"Error: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
    
    protected void SetProperty<T>(ref T field, T value, 
        [CallerMemberName] string name = "")
    {
        if (!Equals(field, value))
        {
            field = value;
            OnPropertyChanged(name);
        }
    }
}
```

**Advantages**:
- UI doesn't block during async operations
- IsLoading prevents duplicate requests
- Proper error handling and user feedback
- Testable without UI

**❌ POOR**:

```csharp
public partial class MyPanel : UserControl
{
    private IBackendClient _backend;
    
    public async void RefreshButton_Click(object sender, RoutedEventArgs e)
    {
        // Void async - dangerous!
        try
        {
            var data = await _backend.GetAsync<Data>("/api/...");
            UpdateUI(data);
        }
        catch
        {
            // Swallowing exceptions
        }
    }
    
    private void UpdateUI(Data data)
    {
        // Directly updating UI from click handler
        // Mixing concerns
        StatusTextBox.Text = data.Status;
        DataGrid.ItemsSource = data.Items;
    }
}
```

#### Pattern 2: Proper Resource Cleanup

**✅ GOOD**:

```csharp
public partial class MyPanel : UserControl, ILifecyclePanelView
{
    private Timer _updateTimer;
    private CancellationTokenSource _cts;
    
    public string PanelId => "my_plugin_panel";
    public string DisplayName => "My Plugin";
    public PanelRegion Region => PanelRegion.Center;
    
    public async Task OnActivatedAsync(CancellationToken ct)
    {
        // Start with clean token source
        _cts?.Dispose();
        _cts = new CancellationTokenSource();
        
        // Start periodic updates
        _updateTimer = new Timer(async _ => 
        {
            try
            {
                await RefreshAsync(_cts.Token);
            }
            catch (OperationCanceledException) { }
            catch (Exception ex)
            {
                // Log error
            }
        }, null, 0, 5000);
        
        await RefreshAsync(ct);
    }
    
    public async Task OnDeactivatedAsync(CancellationToken ct)
    {
        // Cancel pending operations
        _cts?.Cancel();
        
        // Stop timer
        _updateTimer?.Dispose();
        _updateTimer = null;
        
        // Save state
        await SaveStateAsync();
    }
    
    public async Task RefreshAsync(CancellationToken ct)
    {
        // Use provided cancellation token
        try
        {
            var data = await _backend.GetAsync<Data>(
                "/api/plugin/my_plugin/data",
                ct
            );
            UpdateUI(data);
        }
        catch (OperationCanceledException)
        {
            // Expected when deactivating
        }
    }
}
```

**Advantages**:
- Resources properly cleaned up
- No dangling timers or connections
- Supports cancellation
- Safe panel switching

**❌ POOR**:

```csharp
public partial class MyPanel : UserControl
{
    private Timer _updateTimer;
    
    public void Initialize()
    {
        // Timer never disposed!
        _updateTimer = new Timer(_ => RefreshUI(), null, 0, 5000);
    }
    
    // No cleanup - timer runs forever
    // Memory leak when panel is closed
}
```

---

## 2. Error Handling

### Boundary Error Handling

**✅ GOOD**:

```python
from fastapi import HTTPException
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

@router.post("/process")
async def process(request: ProcessRequest) -> ProcessResponse:
    """
    Process data from request.
    
    Pydantic validates the request - ValidationError
    converted to 422 automatically.
    """
    try:
        result = service.process(request.text)
        logger.info(f"Processed: {len(request.text)} chars")
        return ProcessResponse(result=result)
        
    except ValueError as e:
        logger.warning(f"Invalid data: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except TimeoutError as e:
        logger.error(f"Processing timeout: {e}")
        raise HTTPException(status_code=504, detail="Processing timeout")
        
    except Exception as e:
        logger.error(f"Unexpected error in process: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Key principles**:
- Catch specific exceptions, not `Exception`
- Log with context and `exc_info=True`
- Return appropriate HTTP status codes
- Never expose internal errors to users
- Pydantic handles validation errors

**❌ POOR**:

```python
@router.post("/process")
async def process(request: dict):
    try:
        # Don't validate inputs
        text = request["text"]  # KeyError not caught
        result = service.process(text)
        return result
    except:
        # Bare except - swallows everything!
        pass  # Silent failure
```

### Custom Exception Hierarchy

**✅ GOOD**:

```python
class PluginError(Exception):
    """Base plugin exception."""
    pass

class AudioProcessingError(PluginError):
    """Raised when audio processing fails."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}

class ConfigurationError(PluginError):
    """Raised when plugin configuration is invalid."""
    pass

class NetworkError(PluginError):
    """Raised when network operation fails."""
    pass

# Usage
try:
    process_audio(data)
except AudioProcessingError as e:
    logger.error(f"Audio processing failed: {e}", extra=e.details)
    raise HTTPException(status_code=400, detail=str(e))
except ConfigurationError as e:
    logger.error(f"Configuration invalid: {e}")
    raise HTTPException(status_code=500, detail="Plugin misconfigured")
```

**Advantages**:
- Specific exception types
- Can handle different errors differently
- Extra context for debugging
- Clear error hierarchy

**❌ POOR**:

```python
try:
    process_audio(data)
except:
    return {"error": "something went wrong"}  # Vague error
```

---

## 3. Logging Standards

### ✅ GOOD Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_audio(audio_bytes, sample_rate, options):
    """Process audio with comprehensive logging."""
    
    logger.debug(f"process_audio called: sample_rate={sample_rate}, "
                f"audio_size={len(audio_bytes)}, options={options}")
    
    # Log lifecycle
    logger.info(f"Starting audio processing for {len(audio_bytes)} bytes")
    
    try:
        if not audio_bytes:
            logger.warning("Empty audio received, returning empty result")
            return b""
        
        # Process
        logger.debug("Converting to NumPy array")
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        
        logger.debug(f"Audio shape: {audio_array.shape}, min={audio_array.min():.3f}, max={audio_array.max():.3f}")
        
        processed = apply_effects(audio_array, options)
        
        logger.info(f"Audio processing completed successfully ({len(processed)} samples)")
        return processed.tobytes()
        
    except ValueError as e:
        logger.error(f"Invalid audio data: {e}", exc_info=False)
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during audio processing: {e}", 
                    exc_info=True)  # Full stack trace
        raise
```

**Logging levels**:
- `DEBUG` — Low-level details (function calls, values)
- `INFO` — Important lifecycle events (start, complete)
- `WARNING` — Recoverable issues (missing optional data)
- `ERROR` — Errors that need attention
- `CRITICAL` — System failures

**❌ POOR**:

```python
def process_audio(audio_bytes):
    print(f"Processing {len(audio_bytes)} bytes")  # print not logging
    
    try:
        result = do_something(audio_bytes)
    except Exception:
        logger.error("Error")  # Too vague
        pass  # Suppress error
    
    # No logging on success
    return result
```

---

## 4. Performance Optimization

### Backend Performance

#### Use Async for I/O

**✅ GOOD**:

```python
# Async routes for non-blocking I/O
@router.post("/fetch")
async def fetch_data(request: FetchRequest):
    # These don't block the event loop
    data = await _backend.GetAsync("/api/data")
    result = await process_async(data)
    return result
```

#### Use NumPy for Audio

**✅ GOOD**:

```python
def apply_effect(audio_bytes: bytes, gain_db: float) -> bytes:
    # Convert to NumPy (vectorized)
    audio = np.frombuffer(audio_bytes, dtype=np.float32)
    
    # Vectorized operation (fast)
    gain_linear = 10 ** (gain_db / 20)
    processed = audio * gain_linear
    
    # Clip and convert back
    processed = np.clip(processed, -1.0, 1.0)
    return processed.tobytes()
```

**❌ POOR**:

```python
def apply_effect(audio_bytes: bytes, gain_db: float) -> bytes:
    # Loop over every sample (slow!)
    gain_linear = 10 ** (gain_db / 20)
    processed = []
    for sample in audio_bytes:
        processed.append(sample * gain_linear)
    return bytes(processed)
```

### Frontend Performance

#### Lazy Load Heavy Operations

**✅ GOOD**:

```csharp
public class MyViewModel : INotifyPropertyChanged
{
    private Data _data;
    private bool _dataLoaded;
    
    public Data Data
    {
        get => _data;
        private set => SetProperty(ref _data, value);
    }
    
    public async Task LoadDataAsync()
    {
        if (_dataLoaded)
            return;  // Already loaded
        
        // Load on demand
        Data = await _backend.GetAsync<Data>("/api/data");
        _dataLoaded = true;
    }
}
```

#### Minimize UI Updates

**✅ GOOD**:

```csharp
public async Task RefreshAsync()
{
    var items = await _backend.GetAsync<List<Item>>("/api/items");
    
    // Update collection in batch
    ItemsCollection.Clear();
    foreach (var item in items)
    {
        ItemsCollection.Add(item);
    }
}
```

---

## 5. Security Best Practices

### Input Validation

**✅ GOOD**:

```python
from pathlib import Path

@router.post("/process_file")
async def process_file(request: FileRequest):
    """Process a file safely."""
    
    try:
        # Validate path
        file_path = Path(request.file_path)
        
        # Prevent directory traversal
        resolved = file_path.resolve()
        allowed_dir = Path("/plugin/workspace").resolve()
        
        if not str(resolved).startswith(str(allowed_dir)):
            logger.warning(f"Path traversal attempt: {request.file_path}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check permissions with sandbox
        sandbox.check_file_permission(resolved, "read")
        
        # Now safe to read
        data = resolved.read_bytes()
        return process_data(data)
        
    except PermissionViolation:
        raise HTTPException(status_code=403, detail="Permission denied")
```

### Minimal Permissions

**✅ GOOD Manifest**:

```json
{
  "permissions": [
    "filesystem.read.workspace",
    "filesystem.write.workspace"
  ]
}
```

Request only what you need. Each permission opens up security surface.

### Never Store Credentials

**✅ GOOD**:

```python
# Load credentials from secure storage
api_key = os.getenv("MY_PLUGIN_API_KEY")

if not api_key:
    logger.error("API_KEY not configured")
    raise ConfigurationError("API_KEY not set in environment")
```

**❌ POOR**:

```json
{
  "settings": {
    "api_key": "sk-12345..."  // Don't hardcode!
  }
}
```

---

## 6. Testing Patterns

### Unit Testing Backend Plugins

**✅ GOOD**:

```python
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    plugin = MyPlugin(Path(__file__).parent)
    plugin.register(app)
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)

def test_process_valid_input(client):
    """Test processing with valid input."""
    response = client.post("/api/plugin/my_plugin/process",
        json={"text": "hello"})
    
    assert response.status_code == 200
    assert response.json()["result"] == "HELLO"

def test_process_empty_input(client):
    """Test processing with empty input."""
    response = client.post("/api/plugin/my_plugin/process",
        json={"text": ""})
    
    assert response.status_code == 200
    assert response.json()["result"] == ""

def test_process_invalid_input(client):
    """Test processing with invalid input."""
    response = client.post("/api/plugin/my_plugin/process",
        json={})  # Missing 'text'
    
    assert response.status_code == 422  # Validation error
```

### Testing Frontend Plugins

**✅ GOOD**:

```csharp
[TestClass]
public class MyViewModelTests
{
    [TestMethod]
    public async Task RefreshAsync_WhenSuccessful_UpdatesUI()
    {
        // Arrange
        var mockBackend = new Mock<IBackendClient>();
        mockBackend.Setup(b => b.GetAsync<Data>(It.IsAny<string>()))
            .ReturnsAsync(new Data { Status = "Active" });
        
        var vm = new MyViewModel(mockBackend.Object);
        
        // Act
        await vm.RefreshAsync();
        
        // Assert
        Assert.AreEqual("Active", vm.Status);
        Assert.IsFalse(vm.IsLoading);
    }
    
    [TestMethod]
    public async Task RefreshAsync_WhenFails_ShowsError()
    {
        // Arrange
        var mockBackend = new Mock<IBackendClient>();
        mockBackend.Setup(b => b.GetAsync<Data>(It.IsAny<string>()))
            .ThrowsAsync(new HttpRequestException("Connection failed"));
        
        var vm = new MyViewModel(mockBackend.Object);
        
        // Act
        await vm.RefreshAsync();
        
        // Assert
        StringAssert.Contains(vm.Status, "Error");
        Assert.IsFalse(vm.IsLoading);
    }
}
```

---

## 7. Code Organization

### Small Plugins (Single File)

For simple plugins with <200 lines, keep everything in `plugin.py`:

```
plugins/my_plugin/
  manifest.json
  plugin.py        # All code here
  tests/
    test_plugin.py
  requirements.txt
  README.md
```

### Medium Plugins (Multiple Modules)

For complex plugins, organize by concern:

```
plugins/my_plugin/
  manifest.json
  plugin.py          # Only router and entry point
  models.py          # Pydantic models
  service.py         # Business logic
  exceptions.py      # Custom exceptions
  tests/
    test_service.py
    test_routes.py
  requirements.txt
  README.md
```

### Large Plugins (Package Structure)

```
plugins/my_plugin/
  manifest.json
  my_plugin/
    __init__.py
    plugin.py        # Main plugin class
    routes.py        # FastAPI routes
    services/
      __init__.py
      processor.py   # Business logic
      database.py    # Data access
    models.py        # Data models
    exceptions.py
  tests/
    __init__.py
    conftest.py
    test_routes.py
    test_services.py
  requirements.txt
  README.md
```

---

## 8. Pre-Submission Checklist

Before publishing your plugin, verify:

**Code Quality**
- [ ] No empty except blocks or bare `except`
- [ ] No `print()` statements (use logging)
- [ ] No commented-out code
- [ ] No `# TODO` without context
- [ ] All functions have docstrings
- [ ] Code follows PEP 8 (Python) or style guide (C#)

**Error Handling**
- [ ] All API endpoints have error handling
- [ ] Errors logged with context
- [ ] User-friendly error messages
- [ ] No secrets in error messages

**Testing**
- [ ] Unit tests passing
- [ ] Tests cover happy path and error cases
- [ ] >80% code coverage for routes

**Security**
- [ ] Inputs validated
- [ ] File paths checked for traversal
- [ ] Credentials not in code
- [ ] Minimal permissions requested
- [ ] No hardcoded API keys

**Documentation**
- [ ] README.md is complete
- [ ] API endpoints documented
- [ ] Examples provided
- [ ] Dependencies listed

**Manifest**
- [ ] `manifest.json` validates against schema
- [ ] Version follows semantic versioning
- [ ] Author and description filled in
- [ ] Permissions documented

**Performance**
- [ ] No blocking I/O in routes
- [ ] No N+1 queries
- [ ] Resource limits set appropriately
- [ ] Tested with large data

**Compatibility**
- [ ] Works with minimum app version
- [ ] Tested on target Windows versions
- [ ] No conflicting dependencies

---

## Quick Reference

| Concern | ✅ DO | ❌ DON'T |
|---------|------|---------|
| Errors | Catch specific exceptions, log context | Bare except, swallow errors |
| Logging | Use logger at appropriate level | Use print() or no logging |
| Async | Use async/await for I/O | Block event loop |
| Input | Validate with Pydantic, check paths | Trust user input |
| Testing | Unit test business logic | Only manual testing |
| Resources | Manage with context managers | Leak timers/connections |
| Security | Request minimal permissions | Ask for everything |
| Structure | Separate concerns | Mix routing and logic |
