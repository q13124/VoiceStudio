# VoiceStudio Quantum+ Testing Infrastructure

Complete documentation for testing infrastructure, frameworks, and tools.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Ready for Use

---

## Table of Contents

1. [Overview](#overview)
2. [Test Frameworks](#test-frameworks)
3. [Test Organization](#test-organization)
4. [Test Execution](#test-execution)
5. [Test Coverage](#test-coverage)
6. [CI/CD Integration](#cicd-integration)
7. [Testing Tools](#testing-tools)
8. [Best Practices](#best-practices)

---

## Overview

VoiceStudio Quantum+ uses a comprehensive testing infrastructure covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Performance and load testing
- **Quality Tests**: Voice cloning quality metric testing

### Test Philosophy

- **Fast**: Tests should run quickly
- **Reliable**: Tests should be stable and repeatable
- **Isolated**: Tests should not depend on each other
- **Comprehensive**: Cover happy paths, edge cases, and errors

---

## Test Frameworks

### Python Testing

**Framework:** pytest

**Version:** Latest stable (7.0+)

**Features:**
- Fixture system for test setup
- Parameterized tests
- Markers for test categorization
- Plugins for coverage, reporting, etc.

**Installation:**
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

**Configuration:**
- Default: No `pytest.ini` required
- Custom: Create `pytest.ini` in project root for custom settings

**Test Discovery:**
- Files: `test_*.py` or `*_test.py`
- Classes: `Test*`
- Functions: `test_*`

### C# Testing

**Framework:** xUnit (recommended), MSTest, or NUnit

**Version:** Latest for .NET 8

**Features:**
- Attribute-based test discovery
- Assertion library
- Theory/data-driven tests
- Fixtures and test lifecycle

**Installation:**
```bash
dotnet add package xunit
dotnet add package xunit.runner.visualstudio
dotnet add package Moq  # For mocking
```

**Test Discovery:**
- Classes: Public classes with `[Fact]` or `[Theory]` attributes
- Methods: Methods with `[Fact]` or `[Theory]` attributes

---

## Test Organization

### Directory Structure

```
tests/
├── e2e/                        # End-to-end tests
│   ├── __init__.py
│   ├── README.md
│   ├── test_ab_testing_workflow.py
│   ├── test_engine_recommendation_workflow.py
│   └── test_quality_benchmarking_workflow.py
├── integration/                # Integration tests
│   ├── quality_features/
│   │   ├── __init__.py
│   │   ├── conftest.py         # Pytest fixtures
│   │   ├── README.md
│   │   ├── test_ab_testing.py
│   │   ├── test_engine_recommendation.py
│   │   ├── test_quality_benchmarking.py
│   │   └── test_quality_dashboard.py
│   └── ui_features/
│       └── README.md
├── performance/                # Performance tests
│   ├── __init__.py
│   └── test_quality_features_performance.py
└── test_data/                  # Test data
    ├── README.md
    ├── profiles/
    ├── projects/
    ├── metadata/
    └── scripts/
```

### Test Categories

#### Unit Tests

**Location:** Not yet organized (future: `tests/unit/`)

**Purpose:** Test individual functions, classes, and methods in isolation.

**Scope:**
- Service methods
- Utility functions
- Model validation
- Business logic

**Example:**
```python
def test_validate_profile_name():
    """Test profile name validation."""
    assert InputValidator.validate_profile_name("Valid Name").is_valid
    assert not InputValidator.validate_profile_name("").is_valid
```

#### Integration Tests

**Location:** `tests/integration/`

**Purpose:** Test component interactions and API endpoints.

**Scope:**
- API endpoint testing
- Service integration
- Database operations
- External service integration

**Example:**
```python
def test_create_profile(client: TestClient):
    """Test creating a profile via API."""
    response = client.post(
        "/api/profiles",
        json={"name": "Test Profile", "language": "en"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Profile"
```

#### End-to-End Tests

**Location:** `tests/e2e/`

**Purpose:** Test complete user workflows from start to finish.

**Scope:**
- Complete workflows
- Multi-step processes
- User journeys
- System integration

**Example:**
```python
def test_complete_ab_testing_workflow(client: TestClient):
    """Test complete A/B testing workflow."""
    # 1. Start A/B test
    start_response = client.post("/api/eval/abx/start", json={"items": [...]})
    assert start_response.status_code == 200
    
    # 2. Get results
    results_response = client.get("/api/eval/abx/results")
    assert results_response.status_code == 200
```

#### Performance Tests

**Location:** `tests/performance/`

**Purpose:** Test performance, response times, and resource usage.

**Scope:**
- Response time benchmarks
- Throughput testing
- Resource usage
- Load testing

**Example:**
```python
def test_ab_test_start_performance(client: TestClient):
    """Test A/B test start endpoint performance."""
    times = []
    for i in range(10):
        start_time = time.time()
        response = client.post("/api/eval/abx/start", json={...})
        elapsed = (time.time() - start_time) * 1000
        times.append(elapsed)
    
    avg_time = mean(times)
    assert avg_time < 1000  # Should be under 1 second
```

---

## Test Execution

### Running Python Tests

#### Run All Tests

```bash
# From project root
pytest

# Verbose output
pytest -v

# Very verbose (print statements)
pytest -v -s
```

#### Run Specific Test Categories

```bash
# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/

# Performance tests only
pytest tests/performance/

# Specific test file
pytest tests/integration/quality_features/test_ab_testing.py

# Specific test class
pytest tests/integration/quality_features/test_ab_testing.py::TestABTesting

# Specific test method
pytest tests/integration/quality_features/test_ab_testing.py::TestABTesting::test_start_ab_test_success
```

#### Run Tests by Marker

```bash
# Tests marked with @pytest.mark.slow
pytest -m slow

# Tests marked with @pytest.mark.integration
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

#### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect number of CPUs
pytest -n auto
```

### Running C# Tests

#### Run All Tests

```bash
# From project root
dotnet test

# Verbose output
dotnet test --verbosity normal

# Minimal output
dotnet test --verbosity minimal
```

#### Run Specific Tests

```bash
# Run specific test project
dotnet test tests/VoiceStudio.App.Tests/

# Run tests matching filter
dotnet test --filter "FullyQualifiedName~TestClassName"

# Run specific test method
dotnet test --filter "FullyQualifiedName~TestClassName.TestMethod"
```

#### Run Tests with Configuration

```bash
# Run tests in Debug configuration
dotnet test --configuration Debug

# Run tests in Release configuration
dotnet test --configuration Release

# Run tests with logger
dotnet test --logger "console;verbosity=detailed"
```

---

## Test Coverage

### Python Coverage

**Tool:** pytest-cov

**Installation:**
```bash
pip install pytest-cov
```

#### Generate Coverage Report

```bash
# Terminal output
pytest --cov=backend.api --cov-report=term

# HTML report
pytest --cov=backend.api --cov-report=html

# XML report (for CI/CD)
pytest --cov=backend.api --cov-report=xml

# Multiple formats
pytest --cov=backend.api --cov-report=term --cov-report=html --cov-report=xml
```

#### Coverage Reports

**Terminal Report:**
```
Name                                    Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------
backend/api/main.py                       420     45    89%   45-50, 100-105
backend/api/routes/profiles.py            150     10    93%   45-50
-------------------------------------------------------------------------
TOTAL                                      570     55    90%
```

**HTML Report:**
- Location: `htmlcov/index.html`
- Open in browser to view line-by-line coverage
- Shows covered and missed lines

#### Coverage Configuration

Create `.coveragerc` file:

```ini
[run]
source = backend
omit = 
    */tests/*
    */__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

### C# Coverage

**Tool:** Coverlet + ReportGenerator

**Installation:**
```bash
dotnet add package coverlet.collector
dotnet add package coverlet.msbuild
```

#### Generate Coverage Report

```bash
# Collect coverage
dotnet test --collect:"XPlat Code Coverage"

# Generate HTML report (requires ReportGenerator)
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage -reporttypes:Html
```

---

## CI/CD Integration

### GitHub Actions

**Example Workflow:**
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-python:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest tests/ --cov=backend.api --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  test-csharp:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'
      - name: Build
        run: dotnet build
      - name: Test
        run: dotnet test --collect:"XPlat Code Coverage"
```

### Azure DevOps

**Example Pipeline:**
```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'windows-latest'

stages:
  - stage: Test
    jobs:
      - job: PythonTests
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.10'
          - script: |
              pip install -r backend/requirements.txt
              pip install pytest pytest-cov
              pytest tests/ --cov=backend.api --cov-report=xml
          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: 'Cobertura'
              summaryFileLocation: 'coverage.xml'
      
      - job: CSharpTests
        steps:
          - task: UseDotNet@2
            inputs:
              versionSpec: '8.0.x'
          - script: |
              dotnet build
              dotnet test --collect:"XPlat Code Coverage"
```

---

## Testing Tools

### Test Fixtures

#### Pytest Fixtures

**Location:** `tests/integration/quality_features/conftest.py`

**Common Fixtures:**
```python
@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)

@pytest.fixture
def sample_profile_id():
    """Sample profile ID for testing."""
    return "test-profile-123"

@pytest.fixture
def sample_test_text():
    """Sample test text for synthesis."""
    return "This is a test sentence for quality testing."
```

**Usage:**
```python
def test_something(client: TestClient, sample_profile_id: str):
    response = client.get(f"/api/profiles/{sample_profile_id}")
    assert response.status_code == 200
```

### Test Clients

#### FastAPI TestClient

**Purpose:** Test FastAPI endpoints without running a server.

**Usage:**
```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
```

#### Mock Backend Client (C#)

**Purpose:** Mock backend client for frontend tests.

**Example:**
```csharp
var mockClient = new Mock<IBackendClient>();
mockClient.Setup(x => x.GetProfilesAsync())
    .ReturnsAsync(new List<VoiceProfile> { /* test data */ });

var viewModel = new ProfilesViewModel(mockClient.Object);
```

### Test Data Management

**Location:** `tests/test_data/`

**Features:**
- Sample profiles (`profiles/sample_profiles.json`)
- Sample projects (`projects/sample_projects.json`)
- Audio metadata (`metadata/audio_metadata.json`)
- Generation scripts (`scripts/generate_test_data.py`)

**Usage:**
```python
import json
from pathlib import Path

test_data_dir = Path(__file__).parent.parent / "test_data"
profile_path = test_data_dir / "profiles" / "sample_profiles.json"

with open(profile_path) as f:
    profiles = json.load(f)
    test_profile = profiles[0]
```

---

## Test Execution Best Practices

### Test Independence

**✅ Good:**
- Each test is independent
- Tests can run in any order
- No shared state between tests

**❌ Bad:**
- Tests depend on execution order
- Shared state between tests
- Tests modify global state

### Test Isolation

**✅ Good:**
```python
@pytest.fixture
def clean_state():
    """Fixture to clean state before each test."""
    # Setup
    yield
    # Cleanup
    _profiles.clear()
```

**❌ Bad:**
```python
def test_one():
    _profiles["test"] = Profile(...)  # Modifies global state

def test_two():
    assert "test" in _profiles  # Depends on test_one
```

### Fast Tests

**✅ Good:**
- Unit tests: < 10ms
- Integration tests: < 100ms
- E2E tests: < 5s

**❌ Bad:**
- Tests that take minutes
- Tests with unnecessary delays
- Tests that wait for real network calls

---

## Test Coverage Targets

### Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **Overall**: 85%+ coverage

### Coverage Reports

**Generate Reports:**
```bash
# Python
pytest --cov=backend.api --cov-report=html

# C# (after test run)
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage
```

**View Reports:**
- HTML: Open `htmlcov/index.html` or `coverage/index.html`
- Terminal: View in console output

---

## CI/CD Testing

### Pre-Commit Hooks

**Python:**
```bash
# Run tests before commit
pre-commit install
pre-commit run --all-files
```

**C#:**
```bash
# Run tests before commit
dotnet test
```

### Pull Request Checks

**Required Checks:**
- [ ] All tests pass
- [ ] Coverage threshold met (85%+)
- [ ] No test failures
- [ ] Code review approved

### Release Testing

**Pre-Release:**
- [ ] All tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance tests pass
- [ ] Coverage report generated

---

## Testing Tools

### Python Tools

**pytest:**
- Test framework
- Fixtures, markers, parametrization
- Plugin system

**pytest-cov:**
- Coverage collection
- Coverage reporting

**pytest-asyncio:**
- Async test support
- Async fixtures

**pytest-mock:**
- Mocking support
- Mock fixtures

**pytest-xdist:**
- Parallel test execution
- Test distribution

### C# Tools

**xUnit:**
- Test framework
- Theory/data-driven tests
- Fixtures

**Moq:**
- Mocking framework
- Mock objects
- Verification

**FluentAssertions:**
- Fluent assertions
- Better error messages

**Coverlet:**
- Code coverage
- Multiple formats

---

## Best Practices

### Writing Tests

1. **Use Descriptive Names:**
   ```python
   # ✅ Good
   def test_create_profile_with_valid_name_succeeds():
   
   # ❌ Bad
   def test_create():
   ```

2. **Follow AAA Pattern:**
   ```python
   def test_example():
       # Arrange
       client = TestClient(app)
       data = {"name": "Test"}
       
       # Act
       response = client.post("/api/profiles", json=data)
       
       # Assert
       assert response.status_code == 200
   ```

3. **Test One Thing:**
   ```python
   # ✅ Good - One assertion per test
   def test_profile_name_validation():
       assert validate_name("Valid") == True
   
   def test_profile_name_required():
       assert validate_name("") == False
   
   # ❌ Bad - Multiple concerns
   def test_profile():
       assert validate_name("Valid") == True
       assert validate_age(25) == True
       assert create_profile(...) == success
   ```

4. **Use Fixtures:**
   ```python
   # ✅ Good
   def test_something(client: TestClient):
       response = client.get("/api/health")
   
   # ❌ Bad
   def test_something():
       client = TestClient(app)  # Duplicated setup
       response = client.get("/api/health")
   ```

### Test Organization

1. **Group Related Tests:**
   ```python
   class TestProfileCreation:
       def test_create_with_valid_name(self):
           pass
       
       def test_create_with_invalid_name(self):
           pass
   ```

2. **Use Test Markers:**
   ```python
   @pytest.mark.integration
   def test_api_endpoint():
       pass
   
   @pytest.mark.slow
   def test_performance():
       pass
   ```

3. **Document Test Purpose:**
   ```python
   def test_create_profile_with_valid_name():
       """Test that creating a profile with valid name succeeds."""
       # Test implementation
   ```

### Test Maintenance

1. **Keep Tests Updated:**
   - Update tests when code changes
   - Remove obsolete tests
   - Refactor for clarity

2. **Fix Failing Tests Immediately:**
   - Don't leave broken tests
   - Fix or remove failing tests
   - Document known issues

3. **Review Test Coverage:**
   - Check coverage regularly
   - Identify gaps
   - Add tests for missing coverage

---

## Troubleshooting

### Common Issues

**Issue: Tests Fail Intermittently**

**Solution:**
- Check for race conditions
- Ensure test isolation
- Verify no shared state
- Use proper fixtures

**Issue: Tests Too Slow**

**Solution:**
- Use mocks instead of real services
- Parallelize test execution
- Optimize test setup
- Cache fixtures

**Issue: Coverage Not Accurate**

**Solution:**
- Verify source paths in coverage config
- Check omit patterns
- Ensure tests are running
- Review coverage report

---

## Summary

This testing infrastructure provides:

1. **Test Frameworks:** pytest (Python), xUnit (C#)
2. **Test Organization:** Unit, integration, E2E, performance
3. **Test Execution:** Multiple ways to run tests
4. **Test Coverage:** Tools and targets for coverage
5. **CI/CD Integration:** GitHub Actions, Azure DevOps
6. **Testing Tools:** Fixtures, clients, mocks
7. **Best Practices:** Guidelines for writing and maintaining tests

**Key Features:**
- ✅ Comprehensive test coverage
- ✅ Fast test execution
- ✅ CI/CD integration
- ✅ Coverage reporting
- ✅ Test data management

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After major infrastructure changes

