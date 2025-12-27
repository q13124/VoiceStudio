# VoiceStudio Quantum+ API Usage Guide

Complete usage guide with code examples, error handling, and best practices.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Making Requests](#making-requests)
4. [Error Handling](#error-handling)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Rate Limiting](#rate-limiting)
8. [WebSocket Usage](#websocket-usage)

---

## Getting Started

### Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://api.voicestudio.com
```

### Quick Start

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())
# {"status": "ok", "version": "1.0"}
```

---

## Authentication

Currently, VoiceStudio API does not require authentication for local use. All endpoints are accessible without API keys.

**Future:** API key authentication may be added for remote access.

---

## Making Requests

### Python Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Create a voice profile
profile_data = {
    "name": "My Voice",
    "language": "en",
    "tags": ["male", "professional"]
}

response = requests.post(
    f"{BASE_URL}/profiles",
    json=profile_data
)

if response.status_code == 200:
    profile = response.json()
    print(f"Created profile: {profile['id']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = "http://localhost:8000/api";

// Create a voice profile
const profileData = {
  name: "My Voice",
  language: "en",
  tags: ["male", "professional"]
};

const response = await fetch(`${BASE_URL}/profiles`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(profileData),
});

if (response.ok) {
  const profile = await response.json();
  console.log(`Created profile: ${profile.id}`);
} else {
  const error = await response.json();
  console.error("Error:", error);
}
```

### cURL Example

```bash
# Create a voice profile
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Voice",
    "language": "en",
    "tags": ["male", "professional"]
  }'
```

---

## Error Handling

### Error Response Format

All errors follow a standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    },
    "recovery_suggestion": "How to fix this error"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Error Handling Example

```python
import requests

def create_profile_safe(name: str, language: str = "en"):
    """Create profile with error handling."""
    try:
        response = requests.post(
            f"{BASE_URL}/profiles",
            json={"name": name, "language": language},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            error = response.json()
            print(f"Validation error: {error['error']['message']}")
            if 'recovery_suggestion' in error['error']:
                print(f"Suggestion: {error['error']['recovery_suggestion']}")
        elif response.status_code == 429:
            print("Rate limit exceeded. Please wait and try again.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    return None
```

---

## Code Examples

### Voice Profile Management

#### List Profiles

```python
# Python
response = requests.get(f"{BASE_URL}/profiles")
profiles = response.json()["items"]
for profile in profiles:
    print(f"{profile['name']} ({profile['id']})")
```

#### Get Profile

```python
profile_id = "profile-123"
response = requests.get(f"{BASE_URL}/profiles/{profile_id}")
profile = response.json()
print(f"Profile: {profile['name']}")
```

#### Create Profile

```python
profile_data = {
    "name": "John Doe Voice",
    "language": "en",
    "emotion": "neutral",
    "tags": ["male", "professional"]
}

response = requests.post(
    f"{BASE_URL}/profiles",
    json=profile_data
)
profile = response.json()
print(f"Created: {profile['id']}")
```

#### Update Profile

```python
profile_id = "profile-123"
update_data = {
    "name": "Updated Name",
    "tags": ["male", "professional", "updated"]
}

response = requests.put(
    f"{BASE_URL}/profiles/{profile_id}",
    json=update_data
)
```

#### Delete Profile

```python
profile_id = "profile-123"
response = requests.delete(f"{BASE_URL}/profiles/{profile_id}")
```

### Voice Synthesis

#### Basic Synthesis

```python
synthesis_data = {
    "text": "Hello, this is a test of voice synthesis.",
    "voice_profile_id": "profile-123",
    "language": "en",
    "speed": 1.0,
    "pitch": 0.0
}

response = requests.post(
    f"{BASE_URL}/voice/synthesize",
    json=synthesis_data
)

result = response.json()
print(f"Audio URL: {result['audio_url']}")
print(f"Quality Score: {result['quality_metrics']['mos_score']}")
```

#### Multi-Pass Synthesis

```python
multipass_data = {
    "text": "This will use multi-pass synthesis for better quality.",
    "voice_profile_id": "profile-123",
    "passes": 3,
    "quality_mode": "professional"
}

response = requests.post(
    f"{BASE_URL}/voice/synthesize/multipass",
    json=multipass_data
)
```

### Project Management

#### Create Project

```python
project_data = {
    "name": "My Voice Project",
    "description": "A sample project",
    "voice_profile_ids": ["profile-123"]
}

response = requests.post(
    f"{BASE_URL}/projects",
    json=project_data
)
project = response.json()
```

#### List Projects

```python
response = requests.get(f"{BASE_URL}/projects?page=1&page_size=50")
projects = response.json()["items"]
```

### Batch Processing

#### Create Batch Job

```python
batch_data = {
    "items": [
        {"text": "First item", "voice_profile_id": "profile-123"},
        {"text": "Second item", "voice_profile_id": "profile-123"},
    ],
    "priority": "normal"
}

response = requests.post(
    f"{BASE_URL}/batch/jobs",
    json=batch_data
)
job = response.json()
job_id = job["id"]
```

#### Check Job Status

```python
response = requests.get(f"{BASE_URL}/batch/jobs/{job_id}")
job = response.json()
print(f"Status: {job['status']}")
print(f"Progress: {job.get('progress', 0)}%")
```

### Quality Metrics

#### Calculate Quality Metrics

```python
# Upload audio file first
with open("audio.wav", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/audio/upload", files=files)
    audio_id = response.json()["id"]

# Calculate metrics
response = requests.post(
    f"{BASE_URL}/quality/calculate",
    json={"audio_id": audio_id}
)
metrics = response.json()
print(f"MOS Score: {metrics['mos_score']}")
print(f"Similarity: {metrics['similarity']}")
```

---

## Best Practices

### 1. Use Pagination

Always use pagination for list endpoints:

```python
def list_all_profiles():
    """List all profiles with pagination."""
    all_profiles = []
    page = 1
    page_size = 50
    
    while True:
        response = requests.get(
            f"{BASE_URL}/profiles",
            params={"page": page, "page_size": page_size}
        )
        data = response.json()
        all_profiles.extend(data["items"])
        
        if len(data["items"]) < page_size:
            break
        page += 1
    
    return all_profiles
```

### 2. Handle Rate Limits

```python
import time

def make_request_with_retry(url, max_retries=3):
    """Make request with rate limit handling."""
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

### 3. Use Timeouts

Always set timeouts for requests:

```python
response = requests.get(
    f"{BASE_URL}/profiles",
    timeout=10  # 10 seconds
)
```

### 4. Validate Responses

```python
def safe_request(method, url, **kwargs):
    """Make request with validation."""
    response = requests.request(method, url, **kwargs)
    
    if response.status_code >= 400:
        error = response.json()
        raise Exception(f"API Error: {error.get('error', {}).get('message', 'Unknown error')}")
    
    return response.json()
```

---

## Rate Limiting

### Rate Limit Headers

Rate limit information is provided in response headers:

- `X-RateLimit-Limit-Second` - Requests per second limit
- `X-RateLimit-Remaining-Second` - Remaining requests this second
- `X-RateLimit-Remaining-Minute` - Remaining requests this minute
- `X-RateLimit-Remaining-Hour` - Remaining requests this hour
- `X-RateLimit-Reset` - Reset timestamp
- `Retry-After` - Seconds to wait (when rate limited)

### Rate Limit Example

```python
response = requests.get(f"{BASE_URL}/profiles")

# Check rate limit headers
remaining = response.headers.get("X-RateLimit-Remaining-Second", "unknown")
print(f"Remaining requests this second: {remaining}")

if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    print(f"Rate limited. Retry after {retry_after} seconds")
```

---

## WebSocket Usage

### Real-time Updates

```python
import asyncio
import websockets
import json

async def listen_to_updates():
    """Listen to real-time WebSocket updates."""
    uri = "ws://localhost:8000/ws/realtime?topics=meters,training,batch"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Update: {data}")
            
            # Handle different event types
            if data.get("type") == "training_progress":
                print(f"Training progress: {data.get('progress')}%")
            elif data.get("type") == "batch_complete":
                print(f"Batch job {data.get('job_id')} completed")

# Run
asyncio.run(listen_to_updates())
```

---

## Complete Example: Voice Cloning Workflow

```python
import requests
import time

BASE_URL = "http://localhost:8000/api"

def complete_voice_cloning_workflow():
    """Complete workflow example."""
    
    # 1. Create voice profile
    print("Creating voice profile...")
    profile_data = {
        "name": "My Cloned Voice",
        "language": "en",
        "tags": ["male", "professional"]
    }
    profile_response = requests.post(
        f"{BASE_URL}/profiles",
        json=profile_data
    )
    profile = profile_response.json()
    profile_id = profile["id"]
    print(f"Created profile: {profile_id}")
    
    # 2. Synthesize voice
    print("Synthesizing voice...")
    synthesis_data = {
        "text": "Hello, this is my cloned voice speaking.",
        "voice_profile_id": profile_id,
        "language": "en"
    }
    synthesis_response = requests.post(
        f"{BASE_URL}/voice/synthesize",
        json=synthesis_data
    )
    synthesis_result = synthesis_response.json()
    print(f"Audio URL: {synthesis_result['audio_url']}")
    print(f"Quality Score: {synthesis_result['quality_metrics']['mos_score']}")
    
    # 3. Create project
    print("Creating project...")
    project_data = {
        "name": "My Voice Project",
        "voice_profile_ids": [profile_id]
    }
    project_response = requests.post(
        f"{BASE_URL}/projects",
        json=project_data
    )
    project = project_response.json()
    print(f"Created project: {project['id']}")
    
    return {
        "profile_id": profile_id,
        "audio_url": synthesis_result["audio_url"],
        "project_id": project["id"]
    }

# Run workflow
result = complete_voice_cloning_workflow()
print(f"\nWorkflow complete!")
print(f"Profile: {result['profile_id']}")
print(f"Audio: {result['audio_url']}")
print(f"Project: {result['project_id']}")
```

---

## Additional Resources

- **OpenAPI Specification:** `http://localhost:8000/openapi.json`
- **Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc`
- **API Reference:** See `API_REFERENCE.md`
- **Endpoints List:** See `ENDPOINTS.md`

---

**Last Updated:** 2025-01-28

