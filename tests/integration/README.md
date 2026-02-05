# Integration Test Suite

## Overview

This directory contains integration tests for the VoiceStudio backend API and related components.

## Test Structure

```
tests/integration/
├── conftest.py              # Shared fixtures and configuration
├── api/                     # API endpoint integration tests
│   ├── test_core_api_integration.py
│   ├── test_backend_endpoints.py
│   └── test_comprehensive_api_endpoints.py
├── engines/                 # Engine integration tests
├── quality_features/        # Quality features tests
├── route_integrations/      # Route workflow tests
└── ui_features/             # UI feature backend tests
```

## Running Tests

### Run all integration tests

```bash
python -m pytest tests/integration -v
```

### Run specific test file

```bash
python -m pytest tests/integration/api/test_core_api_integration.py -v
```

### Run tests by marker

```bash
# Run only API tests
python -m pytest tests/integration -m "api" -v

# Run smoke tests only
python -m pytest tests/integration -m "smoke" -v

# Skip slow tests
python -m pytest tests/integration -m "not slow" -v
```

### Run with timeout

```bash
python -m pytest tests/integration --timeout=30 -v
```

## Test Fixtures

### Core Fixtures (from conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `app` | session | FastAPI application instance |
| `client` | function | FastAPI TestClient |
| `test_client` | function | Enhanced IntegrationTestClient with tracking |
| `api_base_url` | session | API base URL |
| `test_config` | session | Test configuration object |

### Sample Data Fixtures

| Fixture | Description |
|---------|-------------|
| `sample_profile_id` | Test profile ID |
| `sample_project_id` | Test project ID |
| `sample_audio_id` | Test audio ID |
| `sample_text` | Test synthesis text |
| `sample_synthesis_request` | Complete synthesis request payload |

## Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.integration` | Integration test |
| `@pytest.mark.api` | API endpoint test |
| `@pytest.mark.slow` | Slow-running test |
| `@pytest.mark.smoke` | Smoke test (quick verification) |
| `@pytest.mark.requires_backend` | Requires running backend |
| `@pytest.mark.requires_gpu` | Requires GPU |

## IntegrationTestClient

The `IntegrationTestClient` provides enhanced testing capabilities:

```python
def test_example(test_client):
    # Make request with automatic version header
    response = test_client.get("/api/health")
    
    # Assert success
    test_client.assert_success(response)
    
    # Assert specific status
    test_client.assert_status(response, 200)
    
    # Access response data
    print(response.body)       # Response body
    print(response.headers)    # Response headers
    print(response.elapsed_ms) # Request duration
```

### Response Tracking

The test client tracks all responses:

```python
def test_tracking(test_client):
    test_client.get("/api/health")
    test_client.get("/api/version")
    
    # Get last response
    last = test_client.tracker.last
    
    # Get all failures
    failures = test_client.tracker.get_failures()
    
    # Get slow responses
    slow = test_client.tracker.get_slow_responses(threshold_ms=1000)
```

## Validation Helpers

### Schema Validation

```python
from tests.integration.conftest import validate_response_schema

def test_endpoint(test_client):
    response = test_client.get("/api/version")
    validate_response_schema(response, [
        "current_version",
        "min_supported_version",
        "negotiated_version",
    ])
```

### Error Response Validation

```python
from tests.integration.conftest import validate_error_response

def test_error(test_client):
    response = test_client.get("/api/nonexistent")
    validate_error_response(response)  # Warns if non-standard format
```

### Version Header Validation

```python
from tests.integration.conftest import validate_version_headers

def test_versioning(test_client):
    response = test_client.get("/api/health")
    validate_version_headers(response)  # Checks X-API-Version headers
```

## Writing New Tests

### Basic Test Template

```python
import pytest


@pytest.mark.integration
@pytest.mark.api
class TestMyFeature:
    """Integration tests for MyFeature."""

    def test_basic_functionality(self, test_client):
        """Test basic feature functionality."""
        response = test_client.get("/api/my-endpoint")
        test_client.assert_success(response)
        
        assert "expected_field" in response.body

    def test_error_handling(self, test_client):
        """Test error handling."""
        response = test_client.post(
            "/api/my-endpoint",
            json={"invalid": "data"}
        )
        test_client.assert_status(response, 422)

    @pytest.mark.slow
    def test_performance(self, test_client):
        """Test response time."""
        response = test_client.get("/api/my-endpoint")
        assert response.elapsed_ms < 1000
```

### Test with Sample Data

```python
@pytest.mark.integration
class TestWithData:
    def test_with_sample(
        self,
        test_client,
        sample_profile_id,
        sample_text,
    ):
        response = test_client.post(
            "/api/voice/synthesize",
            json={
                "profile_id": sample_profile_id,
                "text": sample_text,
            }
        )
        test_client.assert_success(response)
```

## Best Practices

1. **Use markers appropriately** - Mark tests with relevant markers for filtering
2. **Keep tests independent** - Each test should work in isolation
3. **Use fixtures** - Leverage shared fixtures for common data
4. **Assert specific conditions** - Use meaningful assertions
5. **Test edge cases** - Include error handling and boundary tests
6. **Add timeouts** - Prevent tests from hanging indefinitely
7. **Document test purpose** - Add clear docstrings

## Configuration

Test configuration is managed via `IntegrationTestConfig`:

```python
@dataclass
class IntegrationTestConfig:
    api_base_url: str = "http://localhost:8000/api"
    api_version: str = "1.0"
    timeout: float = 60.0
    retry_count: int = 3
    retry_delay: float = 1.0
    enable_logging: bool = True
    validate_responses: bool = True
```

Modify `TEST_CONFIG` in conftest.py to change defaults.

## Troubleshooting

### Tests failing with import errors

Ensure the project root is in PYTHONPATH:

```bash
export PYTHONPATH=$PWD:$PYTHONPATH
python -m pytest tests/integration -v
```

### Tests hanging

Add timeout:

```bash
python -m pytest tests/integration --timeout=30 -v
```

### Backend not available

Skip tests requiring backend:

```bash
python -m pytest tests/integration -m "not requires_backend" -v
```
