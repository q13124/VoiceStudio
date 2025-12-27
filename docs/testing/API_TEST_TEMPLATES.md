# API Endpoint Testing Templates
## VoiceStudio Quantum+ - Reusable Test Templates

**Date:** 2025-01-28  
**Status:** Complete  
**Purpose:** Provide reusable test templates for all API endpoint types

---

## Overview

This document provides comprehensive test templates for testing API endpoints in VoiceStudio Quantum+. Templates are organized by HTTP method and include examples for common scenarios.

**Test Framework:** Python `pytest` with `fastapi.testclient.TestClient`

---

## Template Structure

Each template includes:
- **Setup:** Test data and client initialization
- **Happy Path:** Successful request/response
- **Error Cases:** Common error scenarios
- **Edge Cases:** Boundary conditions
- **Validation:** Response validation

---

## GET Endpoint Template

### Basic GET Template

```python
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_get_endpoint_success():
    """Test successful GET request."""
    # Arrange
    endpoint = "/api/resource"
    
    # Act
    response = client.get(endpoint)
    
    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, (list, dict))
    assert "expected_field" in data or len(data) > 0

def test_get_endpoint_not_found():
    """Test GET request with non-existent resource."""
    # Arrange
    endpoint = "/api/resource/99999"
    
    # Act
    response = client.get(endpoint)
    
    # Assert
    assert response.status_code == 404
    error = response.json()
    assert "detail" in error or "error" in error

def test_get_endpoint_with_query_params():
    """Test GET request with query parameters."""
    # Arrange
    endpoint = "/api/resource"
    params = {"limit": 10, "offset": 0, "filter": "active"}
    
    # Act
    response = client.get(endpoint, params=params)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10  # Respects limit

def test_get_endpoint_with_invalid_params():
    """Test GET request with invalid query parameters."""
    # Arrange
    endpoint = "/api/resource"
    params = {"limit": -1, "offset": "invalid"}
    
    # Act
    response = client.get(endpoint, params=params)
    
    # Assert
    assert response.status_code in [400, 422]  # Bad Request or Validation Error
    error = response.json()
    assert "detail" in error
```

### GET with Authentication Template

```python
def test_get_endpoint_with_auth():
    """Test GET request with authentication."""
    # Arrange
    endpoint = "/api/protected/resource"
    headers = {"Authorization": "Bearer test_token"}
    
    # Act
    response = client.get(endpoint, headers=headers)
    
    # Assert
    assert response.status_code == 200

def test_get_endpoint_without_auth():
    """Test GET request without authentication."""
    # Arrange
    endpoint = "/api/protected/resource"
    
    # Act
    response = client.get(endpoint)
    
    # Assert
    assert response.status_code == 401  # Unauthorized
```

---

## POST Endpoint Template

### Basic POST Template

```python
def test_post_endpoint_success():
    """Test successful POST request."""
    # Arrange
    endpoint = "/api/resource"
    payload = {
        "name": "Test Resource",
        "description": "Test description",
        "value": 100
    }
    
    # Act
    response = client.post(endpoint, json=payload)
    
    # Assert
    assert response.status_code == 201  # Created
    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]

def test_post_endpoint_validation_error():
    """Test POST request with invalid data."""
    # Arrange
    endpoint = "/api/resource"
    payload = {
        "name": "",  # Invalid: empty name
        "value": -1  # Invalid: negative value
    }
    
    # Act
    response = client.post(endpoint, json=payload)
    
    # Assert
    assert response.status_code == 422  # Validation Error
    error = response.json()
    assert "detail" in error
    assert len(error["detail"]) > 0

def test_post_endpoint_missing_required_fields():
    """Test POST request with missing required fields."""
    # Arrange
    endpoint = "/api/resource"
    payload = {
        "name": "Test Resource"
        # Missing required "description" field
    }
    
    # Act
    response = client.post(endpoint, json=payload)
    
    # Assert
    assert response.status_code == 422
    error = response.json()
    assert "detail" in error

def test_post_endpoint_duplicate():
    """Test POST request creating duplicate resource."""
    # Arrange
    endpoint = "/api/resource"
    payload = {"name": "Existing Resource"}
    
    # Act
    response1 = client.post(endpoint, json=payload)
    response2 = client.post(endpoint, json=payload)
    
    # Assert
    assert response1.status_code == 201
    assert response2.status_code in [400, 409]  # Bad Request or Conflict
```

### POST with File Upload Template

```python
def test_post_endpoint_with_file():
    """Test POST request with file upload."""
    # Arrange
    endpoint = "/api/resource/upload"
    files = {
        "file": ("test.wav", b"fake audio data", "audio/wav")
    }
    data = {
        "name": "Test Audio",
        "format": "wav"
    }
    
    # Act
    response = client.post(endpoint, files=files, data=data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "file_path" in data or "url" in data

def test_post_endpoint_invalid_file():
    """Test POST request with invalid file."""
    # Arrange
    endpoint = "/api/resource/upload"
    files = {
        "file": ("test.txt", b"not audio data", "text/plain")
    }
    
    # Act
    response = client.post(endpoint, files=files)
    
    # Assert
    assert response.status_code == 400
    error = response.json()
    assert "detail" in error
```

---

## PUT Endpoint Template

### Basic PUT Template

```python
def test_put_endpoint_success():
    """Test successful PUT request."""
    # Arrange
    # First create a resource
    create_response = client.post("/api/resource", json={"name": "Original"})
    resource_id = create_response.json()["id"]
    
    endpoint = f"/api/resource/{resource_id}"
    payload = {
        "name": "Updated Resource",
        "description": "Updated description"
    }
    
    # Act
    response = client.put(endpoint, json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]

def test_put_endpoint_not_found():
    """Test PUT request with non-existent resource."""
    # Arrange
    endpoint = "/api/resource/99999"
    payload = {"name": "Updated"}
    
    # Act
    response = client.put(endpoint, json=payload)
    
    # Assert
    assert response.status_code == 404

def test_put_endpoint_partial_update():
    """Test PUT request with partial data."""
    # Arrange
    create_response = client.post("/api/resource", json={
        "name": "Original",
        "description": "Original description",
        "value": 100
    })
    resource_id = create_response.json()["id"]
    
    endpoint = f"/api/resource/{resource_id}"
    payload = {"name": "Updated Name"}  # Only update name
    
    # Act
    response = client.put(endpoint, json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    # Other fields should remain unchanged or be set to defaults
```

---

## DELETE Endpoint Template

### Basic DELETE Template

```python
def test_delete_endpoint_success():
    """Test successful DELETE request."""
    # Arrange
    # First create a resource
    create_response = client.post("/api/resource", json={"name": "To Delete"})
    resource_id = create_response.json()["id"]
    
    endpoint = f"/api/resource/{resource_id}"
    
    # Act
    response = client.delete(endpoint)
    
    # Assert
    assert response.status_code in [200, 204]  # OK or No Content
    
    # Verify resource is deleted
    get_response = client.get(endpoint)
    assert get_response.status_code == 404

def test_delete_endpoint_not_found():
    """Test DELETE request with non-existent resource."""
    # Arrange
    endpoint = "/api/resource/99999"
    
    # Act
    response = client.delete(endpoint)
    
    # Assert
    assert response.status_code == 404

def test_delete_endpoint_cascade():
    """Test DELETE request with cascade deletion."""
    # Arrange
    # Create parent resource with children
    parent_response = client.post("/api/parent", json={"name": "Parent"})
    parent_id = parent_response.json()["id"]
    
    child_response = client.post("/api/child", json={
        "parent_id": parent_id,
        "name": "Child"
    })
    child_id = child_response.json()["id"]
    
    # Act
    response = client.delete(f"/api/parent/{parent_id}")
    
    # Assert
    assert response.status_code in [200, 204]
    
    # Verify child is also deleted
    child_get = client.get(f"/api/child/{child_id}")
    assert child_get.status_code == 404
```

---

## WebSocket Endpoint Template

### Basic WebSocket Template

```python
def test_websocket_endpoint_connection():
    """Test WebSocket connection."""
    # Arrange
    endpoint = "/api/stream/{session_id}"
    session_id = "test_session"
    
    # Act
    with client.websocket_connect(f"/api/stream/{session_id}") as websocket:
        # Send message
        websocket.send_json({"action": "start", "data": "test"})
        
        # Receive message
        data = websocket.receive_json()
        
        # Assert
        assert "status" in data
        assert data["status"] == "connected"

def test_websocket_endpoint_streaming():
    """Test WebSocket streaming."""
    # Arrange
    endpoint = "/api/stream/{session_id}"
    session_id = "test_session"
    
    # Act
    with client.websocket_connect(f"/api/stream/{session_id}") as websocket:
        # Send start command
        websocket.send_json({"action": "start"})
        
        # Receive multiple messages
        messages = []
        for _ in range(5):
            try:
                data = websocket.receive_json(timeout=1.0)
                messages.append(data)
            except:
                break
        
        # Assert
        assert len(messages) > 0
        assert all("data" in msg for msg in messages)

def test_websocket_endpoint_error():
    """Test WebSocket error handling."""
    # Arrange
    endpoint = "/api/stream/invalid_session"
    
    # Act & Assert
    with pytest.raises(Exception):  # Connection should fail
        with client.websocket_connect(endpoint) as websocket:
            pass
```

---

## Error Handling Template

### Common Error Scenarios

```python
def test_endpoint_rate_limit():
    """Test rate limiting."""
    # Arrange
    endpoint = "/api/resource"
    
    # Act - Send many requests
    responses = []
    for _ in range(100):
        response = client.get(endpoint)
        responses.append(response.status_code)
    
    # Assert
    # Some requests should be rate limited
    assert 429 in responses  # Too Many Requests

def test_endpoint_server_error():
    """Test server error handling."""
    # Arrange
    endpoint = "/api/resource/error"
    
    # Act
    response = client.get(endpoint)
    
    # Assert
    assert response.status_code == 500
    error = response.json()
    assert "detail" in error or "error" in error

def test_endpoint_timeout():
    """Test request timeout."""
    # Arrange
    endpoint = "/api/resource/slow"
    
    # Act
    with pytest.raises(Exception):  # Should timeout
        response = client.get(endpoint, timeout=0.1)
```

---

## Response Validation Template

### Response Structure Validation

```python
def test_response_structure():
    """Test response structure matches expected schema."""
    # Arrange
    endpoint = "/api/resource"
    
    # Act
    response = client.get(endpoint)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Validate structure
    assert isinstance(data, dict)
    required_fields = ["id", "name", "created_at"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Validate types
    assert isinstance(data["id"], (int, str))
    assert isinstance(data["name"], str)
    assert isinstance(data["created_at"], str)

def test_response_pagination():
    """Test paginated response structure."""
    # Arrange
    endpoint = "/api/resource"
    params = {"page": 1, "per_page": 10}
    
    # Act
    response = client.get(endpoint, params=params)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Validate pagination structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert len(data["items"]) <= data["per_page"]
```

---

## Integration Test Template

### Multi-Endpoint Workflow

```python
def test_complete_workflow():
    """Test complete workflow across multiple endpoints."""
    # 1. Create resource
    create_response = client.post("/api/resource", json={
        "name": "Workflow Test",
        "description": "Test description"
    })
    assert create_response.status_code == 201
    resource_id = create_response.json()["id"]
    
    # 2. Get resource
    get_response = client.get(f"/api/resource/{resource_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Workflow Test"
    
    # 3. Update resource
    update_response = client.put(f"/api/resource/{resource_id}", json={
        "name": "Updated Workflow Test"
    })
    assert update_response.status_code == 200
    
    # 4. Verify update
    verify_response = client.get(f"/api/resource/{resource_id}")
    assert verify_response.json()["name"] == "Updated Workflow Test"
    
    # 5. Delete resource
    delete_response = client.delete(f"/api/resource/{resource_id}")
    assert delete_response.status_code in [200, 204]
    
    # 6. Verify deletion
    final_get = client.get(f"/api/resource/{resource_id}")
    assert final_get.status_code == 404
```

---

## Performance Test Template

### Response Time Testing

```python
import time

def test_endpoint_performance():
    """Test endpoint response time."""
    # Arrange
    endpoint = "/api/resource"
    max_response_time = 1.0  # seconds
    
    # Act
    start_time = time.time()
    response = client.get(endpoint)
    elapsed_time = time.time() - start_time
    
    # Assert
    assert response.status_code == 200
    assert elapsed_time < max_response_time, \
        f"Response time {elapsed_time}s exceeds maximum {max_response_time}s"

def test_endpoint_concurrent_requests():
    """Test endpoint with concurrent requests."""
    import concurrent.futures
    
    # Arrange
    endpoint = "/api/resource"
    num_requests = 10
    
    # Act
    def make_request():
        return client.get(endpoint)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Assert
    assert len(responses) == num_requests
    assert all(r.status_code == 200 for r in responses)
```

---

## Test Fixtures Template

### Reusable Test Fixtures

```python
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def test_resource(client):
    """Create test resource for testing."""
    response = client.post("/api/resource", json={
        "name": "Test Resource",
        "description": "Test description"
    })
    return response.json()

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    # Login or set auth token
    headers = {"Authorization": "Bearer test_token"}
    client.headers.update(headers)
    return client

# Usage in tests
def test_with_fixture(client, test_resource):
    """Test using fixtures."""
    resource_id = test_resource["id"]
    response = client.get(f"/api/resource/{resource_id}")
    assert response.status_code == 200
```

---

## Best Practices

### 1. Test Organization

- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Data

- Use fixtures for reusable test data
- Clean up test data after tests
- Use unique identifiers to avoid conflicts

### 3. Error Testing

- Test all error scenarios
- Verify error messages are helpful
- Test edge cases and boundary conditions

### 4. Performance

- Set performance baselines
- Test under load
- Monitor response times

### 5. Documentation

- Document test purpose
- Explain complex test scenarios
- Keep tests readable and maintainable

---

## Test Execution

### Run All Tests

```bash
pytest tests/integration/ -v
```

### Run Specific Test File

```bash
pytest tests/integration/test_resource.py -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=backend.api.routes --cov-report=html
```

### Run Performance Tests

```bash
pytest tests/integration/ -m performance -v
```

---

## Related Documentation

- **Endpoint Inventory:** `docs/api/ENDPOINT_INVENTORY.md`
- **API Reference:** `docs/api/API_REFERENCE.md`
- **Integration Tests:** `tests/integration/README.md`

---

**Last Updated:** 2025-01-28  
**Maintained By:** Worker 3  
**Status:** Complete

