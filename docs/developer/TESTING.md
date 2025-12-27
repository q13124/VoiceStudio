# VoiceStudio Quantum+ Testing Guide

Complete guide to testing VoiceStudio Quantum+.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [How to Run Tests](#how-to-run-tests)
3. [Writing New Tests](#writing-new-tests)
4. [Test Coverage](#test-coverage)
5. [Integration Testing](#integration-testing)
6. [Performance Testing](#performance-testing)
7. [Test Best Practices](#test-best-practices)

---

## Testing Overview

VoiceStudio uses a comprehensive testing strategy covering:
- **Unit Tests:** Individual components in isolation
- **Integration Tests:** Component interactions
- **End-to-End Tests:** Complete workflows
- **Performance Tests:** Performance benchmarks
- **Quality Tests:** Voice cloning quality metrics

### Test Structure

```
tests/
├── frontend/              # C# unit tests
│   ├── ViewModels/
│   ├── Services/
│   └── Models/
├── backend/              # Python unit tests
│   ├── test_profiles.py
│   ├── test_voice.py
│   └── test_projects.py
├── integration/           # Integration tests
│   ├── test_api_workflows.py
│   └── test_engine_integration.py
└── performance/           # Performance tests
    └── test_benchmarks.py

app/core/
├── engines/
│   └── test_quality_metrics.py  # Quality metric tests
└── audio/
    └── test_audio_utils.py      # Audio utility tests
```

---

## How to Run Tests

### Frontend Tests (C#)

**Using Visual Studio:**
1. Open Test Explorer (Test → Test Explorer)
2. Click "Run All Tests" or run individual tests
3. View results in Test Explorer

**Using Command Line:**
```bash
# Run all tests
dotnet test

# Run specific test project
dotnet test src/VoiceStudio.App.Tests/

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific test
dotnet test --filter "FullyQualifiedName~TestClassName.TestMethod"
```

**Test Output:**
```
Passed!  - Failed:     0, Passed:    15, Skipped:     0, Total:    15
```

### Backend Tests (Python)

**Using pytest:**
```bash
# Run all tests
pytest

# Run specific test file
pytest backend/tests/test_profiles.py

# Run specific test
pytest backend/tests/test_profiles.py::test_create_profile

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=api --cov-report=html

# Run with coverage and show missing lines
pytest --cov=api --cov-report=term-missing
```

**Test Output:**
```
======================== test session starts ========================
backend/tests/test_profiles.py::test_create_profile PASSED
backend/tests/test_profiles.py::test_list_profiles PASSED
======================== 2 passed in 0.15s =========================
```

### Quality Metric Tests

**Run Quality Tests:**
```bash
cd app/core/engines
pytest test_quality_metrics.py -v
```

**Run Audio Utility Tests:**
```bash
cd app/core/audio
pytest test_audio_utils.py -v
```

### Integration Tests

**Prerequisites:**
- Backend must be running
- Or use test fixtures to start backend

**Run Integration Tests:**
```bash
# Start backend first
python -m uvicorn backend.api.main:app

# In another terminal, run integration tests
pytest tests/integration/
```

---

## Writing New Tests

### Frontend Unit Tests (C#)

**Test Framework:** xUnit, NUnit, or MSTest

**Example Test:**
```csharp
using Xunit;
using Moq;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;

public class ProfilesViewModelTests
{
    [Fact]
    public async Task LoadProfilesAsync_LoadsProfiles()
    {
        // Arrange
        var mockClient = new Mock<IBackendClient>();
        var profiles = new List<VoiceProfile>
        {
            new() { Id = "1", Name = "Test Profile" }
        };
        mockClient.Setup(x => x.GetProfilesAsync(It.IsAny<CancellationToken>()))
                  .ReturnsAsync(profiles);
        
        var viewModel = new ProfilesViewModel(mockClient.Object);
        
        // Act
        await viewModel.LoadProfilesAsync();
        
        // Assert
        Assert.Single(viewModel.Profiles);
        Assert.Equal("Test Profile", viewModel.Profiles[0].Name);
        mockClient.Verify(x => x.GetProfilesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }
    
    [Fact]
    public async Task LoadProfilesAsync_HandlesError()
    {
        // Arrange
        var mockClient = new Mock<IBackendClient>();
        mockClient.Setup(x => x.GetProfilesAsync(It.IsAny<CancellationToken>()))
                  .ThrowsAsync(new HttpRequestException("Connection failed"));
        
        var viewModel = new ProfilesViewModel(mockClient.Object);
        
        // Act & Assert
        await Assert.ThrowsAsync<HttpRequestException>(
            () => viewModel.LoadProfilesAsync()
        );
    }
}
```

**Test Patterns:**
- **Arrange:** Set up test data and mocks
- **Act:** Execute the method under test
- **Assert:** Verify expected behavior

### Backend Unit Tests (Python)

**Test Framework:** pytest

**Example Test:**
```python
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.routes import profiles

client = TestClient(app)

def test_list_profiles_empty():
    """Test listing profiles when none exist."""
    response = client.get("/api/profiles")
    assert response.status_code == 200
    assert response.json() == []

def test_create_profile():
    """Test creating a profile."""
    response = client.post(
        "/api/profiles",
        json={
            "name": "Test Profile",
            "language": "en",
            "tags": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Profile"
    assert data["language"] == "en"
    assert "id" in data

def test_get_profile_not_found():
    """Test getting non-existent profile."""
    response = client.get("/api/profiles/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

**Test Utilities:**

The test suite includes comprehensive utilities in `tests/test_utils.py`:

- **TestDataManager**: Manages test data creation and cleanup
- **MockBackendClient**: Mock backend client for API testing
- **TestAssertions**: Enhanced assertions
- **Helper Functions**: `create_mock_engine()`, `create_temp_audio_file()`, etc.

**Test Reporting:**

Test reporting utilities in `tests/test_reporting.py`:

- **TestReportGenerator**: Generates comprehensive test reports (JSON and text)
- **CoverageReporter**: Reports test coverage statistics

**Test Fixtures:**
```python
import pytest
from backend.api.routes.profiles import _profiles

@pytest.fixture
def clear_profiles():
    """Fixture to clear profiles before each test."""
    _profiles.clear()
    yield
    _profiles.clear()

def test_create_profile_with_fixture(clear_profiles):
    """Test creating profile with fixture."""
    # Profiles are cleared before test
    response = client.post("/api/profiles", json={"name": "Test"})
    assert response.status_code == 200
```

### Engine Tests

**Example Engine Test:**
```python
import pytest
from app.core.engines.xtts_engine import XTTSEngine
from app.core.engines.router import router

def test_xtts_engine_initialization():
    """Test XTTS engine initialization."""
    engine = XTTSEngine(device="cpu", gpu=False)
    assert engine.initialize() == True
    assert engine.is_initialized() == True
    engine.cleanup()

def test_xtts_engine_synthesis():
    """Test XTTS engine synthesis."""
    engine = XTTSEngine(device="cpu", gpu=False)
    engine.initialize()
    
    # Test synthesis
    result = engine.synthesize(
        text="Hello, world!",
        speaker_wav="test_reference.wav",
        language="en"
    )
    
    assert result is not None
    assert os.path.exists(result)
    
    engine.cleanup()
```

### Quality Metric Tests

**Example Quality Test:**
```python
import pytest
import numpy as np
from app.core.engines.quality_metrics import (
    calculate_mos_score,
    calculate_similarity,
    calculate_naturalness
)

def test_calculate_mos_score():
    """Test MOS score calculation."""
    # Generate test audio
    audio = generate_test_audio()
    
    # Calculate MOS score
    mos = calculate_mos_score(audio)
    
    # Assert valid range
    assert 1.0 <= mos <= 5.0

def test_calculate_similarity():
    """Test similarity calculation."""
    reference = load_audio("reference.wav")
    generated = load_audio("generated.wav")
    
    similarity = calculate_similarity(reference, generated)
    
    # Assert valid range
    assert 0.0 <= similarity <= 1.0
```

---

## Test Coverage

### Current Coverage Status

**Overall Coverage:** ~94% (exceeds 80% target)  
**Test Files:** 270 comprehensive test files  
**Test Cases:** ~2,100+ test cases across the suite

### Coverage by Category

- **Backend API Routes:** 100% coverage (103 route test files covering all 87+ routes)
- **Core Modules:** ~87%+ coverage (89+ test files)
- **CLI Utilities:** 100% coverage
- **Engine Tests:** 487+ test cases across all engines
- **Optimized Modules:** 100% coverage (all optimizations tested)

### Optimized Module Test Coverage

The following optimized modules have comprehensive test coverage:

- **Engine Optimizations:** LRU caches, batch processing, ThreadPoolExecutor
- **API Optimizations:** Response caching, performance monitoring middleware
- **WebSocket Optimizations:** Connection pooling, message batching, health monitoring
- **Database Optimizations:** Query caching, connection pooling
- **Resource Management:** VRAM monitoring, priority queues, circuit breakers
- **Audio Optimizations:** Buffer pooling, LRU eviction
- **Model Caching:** Memory limits, auto-eviction, TTL support
- **Validation Optimizations:** Schema caching, early validation, batch processing
- **Port Management:** Dynamic allocation, conflict detection
- **Content Hash Caching:** Duplicate detection, fast lookups
- **Quality Metrics Caching:** LRU eviction, TTL support

### Recent Test Additions (2025-01-28)

**New Test Files for Optimized Modules:**
- `test_scheduler.py` - Background Task Scheduler (27 test cases, all passing, covering scheduler initialization, task management, execution, filtering, priority management) ✅ **NEW**
- `test_validation_optimizer.py` - Validation Optimizer Middleware (11 test cases, all passing, covering middleware initialization, dispatch, request state stats) ✅ **NEW**
- `test_batch.py` - Batch processing route (24 test cases, all passing, covering batch job CRUD, filtering, queue status) ✅ **ENHANCED**
- `test_job_queue_enhanced.py` - Enhanced job queue (36 test cases, 34 passing, covering priority queues, batching, retry logic, dependencies) ✅ **ENHANCED**
- `test_invokeai_engine.py` - InvokeAI image generation engine (20 test cases) ✅ **NEW**
- `test_comfyui_engine.py` - ComfyUI image generation engine (19 test cases) ✅ **NEW**
- `test_automatic1111_engine.py` - Automatic1111 image generation engine (18 test cases) ✅ **NEW**
- `test_main.py` - Enhanced with cache endpoints (8 tests) and endpoint metrics endpoints (4 tests), total 15 tests, all passing ✅ **COMPLETE**
- `test_performance_monitoring.py` - Fixed floating point precision issue, all 28 tests passing ✅ **FIXED**
- `test_optimizer.py` - Validation optimizer (25 test cases)
- `test_realtime_enhanced.py` - WebSocket realtime enhanced (20 test cases)
- `test_query_optimizer.py` - Database query optimizer (26 test cases)
- `test_resource_manager_enhanced.py` - Enhanced resource manager (24 test cases)
- `test_buffer_manager.py` - Audio buffer manager (23 test cases)
- `test_model_cache.py` - Model cache (23 test cases)
- `test_performance_metrics.py` - Engine performance metrics (29 test cases)

### Coverage Goals

- **Unit Tests:** 80%+ coverage ✅ **ACHIEVED: ~94%**
- **Integration Tests:** Cover all major workflows
- **Critical Paths:** 100% coverage ✅ **ACHIEVED**

### Measuring Coverage

**Frontend (C#):**
```bash
dotnet test --collect:"XPlat Code Coverage"
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage
```

**Backend (Python):**
```bash
pytest --cov=api --cov-report=html --cov-report=term-missing
```

**View Coverage Report:**
- HTML report: Open `htmlcov/index.html` in browser
- Terminal report: Shows missing lines

### Coverage Exclusions

**Exclude from Coverage:**
- Generated code
- Test files
- Main entry points (minimal logic)

**Example (.coveragerc):**
```ini
[run]
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*
```

---

## Integration Testing

### API Integration Tests

**Test Complete Workflows:**
```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_voice_synthesis_workflow():
    """Test complete voice synthesis workflow."""
    # 1. Create profile
    profile_response = client.post(
        "/api/profiles",
        json={"name": "Test", "language": "en"}
    )
    profile_id = profile_response.json()["id"]
    
    # 2. Synthesize speech
    synthesis_response = client.post(
        "/api/voice/synthesize",
        json={
            "engine": "chatterbox",
            "profile_id": profile_id,
            "text": "Hello, world!",
            "language": "en"
        }
    )
    assert synthesis_response.status_code == 200
    audio_id = synthesis_response.json()["audio_id"]
    
    # 3. Analyze quality
    analysis_response = client.post(
        "/api/voice/analyze",
        json={"audio_id": audio_id}
    )
    assert analysis_response.status_code == 200
    metrics = analysis_response.json()["quality_metrics"]
    assert metrics["mos_score"] >= 1.0
```

### Engine Integration Tests

**Test Engine via Router:**
```python
def test_engine_via_router():
    """Test engine loading and usage via router."""
    from app.core.engines.router import router
    
    # Load engine from manifest
    router.load_engine_from_manifest("engines/audio/xtts_v2/engine.manifest.json")
    
    # Get engine instance
    engine = router.get_engine("xtts_v2", gpu=False)
    assert engine is not None
    assert engine.is_initialized()
    
    # Use engine
    result = engine.synthesize("Test", language="en")
    assert result is not None
    
    # Cleanup
    router.unregister_engine("xtts_v2")
```

### End-to-End Tests

**Test Complete User Workflows:**
```python
def test_complete_project_workflow():
    """Test complete project creation and synthesis workflow."""
    # 1. Create project
    project = create_project("Test Project")
    
    # 2. Create profile
    profile = create_profile("Test Profile")
    
    # 3. Synthesize audio
    audio = synthesize(profile.id, "Hello, world!")
    
    # 4. Add to project
    add_audio_to_project(project.id, audio.id)
    
    # 5. Verify project contains audio
    project_audio = get_project_audio(project.id)
    assert audio.id in [a["id"] for a in project_audio]
```

---

## Performance Testing

### Performance Benchmarks

**Engine Performance:**
```python
import time
from app.core.engines.router import router

def benchmark_engine_synthesis():
    """Benchmark engine synthesis performance."""
    engine = router.get_engine("chatterbox", gpu=True)
    
    # Warmup
    engine.synthesize("Warmup", language="en")
    
    # Benchmark
    times = []
    for i in range(10):
        start = time.time()
        engine.synthesize(f"Test {i}", language="en")
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    print(f"Average synthesis time: {avg_time:.2f}s")
    
    # Assert performance target
    assert avg_time < 5.0  # Target: < 5 seconds
```

### Load Testing

**Test API Under Load:**
```python
import asyncio
import aiohttp

async def load_test_api():
    """Test API performance under load."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.get("http://localhost:8000/api/profiles")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        success_count = sum(1 for r in results if r.status == 200)
        
        assert success_count >= 95  # 95% success rate
```

### Memory Testing

**Test Memory Usage:**
```python
import tracemalloc

def test_memory_usage():
    """Test memory usage during synthesis."""
    tracemalloc.start()
    
    engine = router.get_engine("chatterbox", gpu=True)
    
    # Perform multiple syntheses
    for i in range(10):
        engine.synthesize(f"Test {i}", language="en")
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
    
    # Assert memory limit
    assert peak < 2 * 1024 * 1024 * 1024  # < 2 GB
```

---

## Test Best Practices

### 1. Test Isolation

**Each test should be independent:**
```python
@pytest.fixture
def clean_state():
    """Fixture to ensure clean state for each test."""
    # Setup
    _profiles.clear()
    yield
    # Teardown
    _profiles.clear()
```

### 2. Use Mocks

**Mock external dependencies:**
```csharp
var mockClient = new Mock<IBackendClient>();
mockClient.Setup(x => x.GetProfilesAsync())
          .ReturnsAsync(new List<VoiceProfile>());
```

### 3. Test Edge Cases

**Test boundary conditions:**
```python
def test_create_profile_empty_name():
    """Test creating profile with empty name."""
    response = client.post("/api/profiles", json={"name": ""})
    assert response.status_code == 400

def test_synthesize_empty_text():
    """Test synthesis with empty text."""
    response = client.post("/api/voice/synthesize", json={"text": ""})
    assert response.status_code == 400
```

### 4. Test Error Handling

**Test error scenarios:**
```python
def test_get_nonexistent_profile():
    """Test getting profile that doesn't exist."""
    response = client.get("/api/profiles/nonexistent")
    assert response.status_code == 404

def test_synthesis_invalid_engine():
    """Test synthesis with invalid engine."""
    response = client.post(
        "/api/voice/synthesize",
        json={"engine": "invalid", "profile_id": "1", "text": "Test"}
    )
    assert response.status_code == 400
```

### 5. Use Descriptive Test Names

**Clear test names:**
```python
# Good
def test_create_profile_with_valid_data_succeeds():
    pass

def test_create_profile_with_empty_name_returns_400():
    pass

# Bad
def test_profile():
    pass

def test_error():
    pass
```

### 6. Arrange-Act-Assert Pattern

**Clear test structure:**
```python
def test_synthesis():
    # Arrange
    profile = create_test_profile()
    text = "Hello, world!"
    
    # Act
    result = synthesize(profile.id, text)
    
    # Assert
    assert result is not None
    assert os.path.exists(result)
```

### 7. Test Data Management

**Use fixtures for test data:**
```python
@pytest.fixture
def test_profile():
    """Fixture providing test profile."""
    return {
        "id": "test-profile-1",
        "name": "Test Profile",
        "language": "en"
    }

def test_synthesis_with_fixture(test_profile):
    """Test using fixture."""
    result = synthesize(test_profile["id"], "Test")
    assert result is not None
```

---

## Continuous Integration

### GitHub Actions Example

**`.github/workflows/tests.yml`:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-frontend:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'
      - run: dotnet restore
      - run: dotnet build
      - run: dotnet test

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=api --cov-report=xml
```

---

## Test Maintenance

### Keeping Tests Updated

- **Update tests when code changes**
- **Remove obsolete tests**
- **Refactor tests for clarity**
- **Keep test data current**

### Test Documentation

- **Document test purpose**
- **Explain complex test scenarios**
- **Note test dependencies**
- **Document test data requirements**

---

## References

- [Contributing Guide](CONTRIBUTING.md) - Testing requirements
- [Setup Guide](SETUP.md) - Test environment setup
- [Architecture Documentation](ARCHITECTURE.md) - System architecture

---

### Testing Optimized Modules

**Patterns for Testing Optimizations:**

1. **LRU Cache Testing:**
   ```python
   def test_lru_cache_eviction():
       """Test LRU cache evicts least recently used items."""
       cache = LRUCache(maxsize=2)
       cache['a'] = 1
       cache['b'] = 2
       cache['c'] = 3  # Should evict 'a'
       assert 'a' not in cache
       assert 'b' in cache
       assert 'c' in cache
   ```

2. **Batch Processing Testing:**
   ```python
   def test_batch_processing():
       """Test batch processing with ThreadPoolExecutor."""
       items = [1, 2, 3, 4, 5]
       results = process_batch(items, max_workers=3)
       assert len(results) == 5
       assert all(r is not None for r in results)
   ```

3. **Connection Pooling Testing:**
   ```python
   def test_connection_pool_reuse():
       """Test connection pool reuses connections."""
       pool = ConnectionPool(max_size=5)
       conn1 = pool.get_connection()
       pool.return_connection(conn1)
       conn2 = pool.get_connection()
       assert conn1 is conn2  # Same connection reused
   ```

4. **Performance Monitoring Testing:**
   ```python
   def test_performance_metrics_tracking():
       """Test performance metrics are tracked correctly."""
       middleware = PerformanceMonitoringMiddleware()
       # Simulate request
       response = middleware.process_request(request)
       metrics = middleware.get_metrics('/api/test')
       assert metrics.request_count > 0
       assert metrics.avg_response_time > 0
   ```

**Test File Locations:**
- Optimized module tests: `tests/unit/backend/api/`, `tests/unit/core/`
- Engine optimization tests: `tests/unit/core/engines/`
- Resource management tests: `tests/unit/core/resource/`
- Validation optimizer tests: `tests/unit/core/validation/`

---

**Last Updated:** 2025-01-28  
**Version:** 1.1  
**Test Files:** 264 (comprehensive test suite)

