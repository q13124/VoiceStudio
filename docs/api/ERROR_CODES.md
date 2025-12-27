# VoiceStudio Quantum+ API Error Codes

Complete reference of all error codes, their meanings, and recovery suggestions.

## Error Response Format

All errors follow this standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error details"
    },
    "recovery_suggestion": "How to fix this error",
    "request_id": "unique-request-id"
  }
}
```

---

## Error Code Categories

### 4xx Client Errors

#### VALIDATION_ERROR (400)

**Status Code:** 400  
**Description:** Request validation failed

**Common Causes:**
- Missing required fields
- Invalid field types
- Field value out of range
- Invalid format

**Example:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "field": "name",
      "issue": "Field is required"
    },
    "recovery_suggestion": "Provide the required 'name' field in your request"
  }
}
```

**Recovery:**
- Check request body against API schema
- Verify all required fields are present
- Ensure field types match expected types
- Validate field values are within acceptable ranges

---

#### NOT_FOUND (404)

**Status Code:** 404  
**Description:** Resource not found

**Common Causes:**
- Invalid resource ID
- Resource was deleted
- Incorrect endpoint path

**Example:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Profile not found",
    "details": {
      "resource_type": "profile",
      "resource_id": "profile-123"
    },
    "recovery_suggestion": "Verify the profile ID exists by listing profiles first"
  }
}
```

**Recovery:**
- Verify resource ID is correct
- Check if resource exists by listing resources
- Ensure endpoint path is correct

---

#### CONFLICT (409)

**Status Code:** 409  
**Description:** Resource conflict

**Common Causes:**
- Duplicate resource name
- Resource already exists
- Concurrent modification conflict

**Example:**
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Profile with this name already exists",
    "details": {
      "field": "name",
      "value": "My Voice"
    },
    "recovery_suggestion": "Use a different name or update the existing profile"
  }
}
```

**Recovery:**
- Use a unique name
- Update existing resource instead of creating new
- Resolve concurrent modification conflicts

---

#### RATE_LIMIT_EXCEEDED (429)

**Status Code:** 429  
**Description:** Rate limit exceeded

**Common Causes:**
- Too many requests per second
- Too many requests per minute
- Too many requests per hour

**Example:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded: 60 requests per minute",
    "details": {
      "limit": 60,
      "window": "minute"
    },
    "recovery_suggestion": "Wait before making more requests. Check Retry-After header for wait time"
  }
}
```

**Recovery:**
- Wait for the rate limit window to reset
- Check `Retry-After` header for wait time
- Implement exponential backoff
- Reduce request frequency

---

### 5xx Server Errors

#### INTERNAL_ERROR (500)

**Status Code:** 500  
**Description:** Internal server error

**Common Causes:**
- Unexpected server error
- Database error
- Processing failure

**Example:**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal error occurred",
    "details": {
      "request_id": "req-123"
    },
    "recovery_suggestion": "Retry the request. If the issue persists, contact support with the request ID"
  }
}
```

**Recovery:**
- Retry the request
- Check server status
- Contact support with request ID if issue persists

---

#### SERVICE_UNAVAILABLE (503)

**Status Code:** 503  
**Description:** Service temporarily unavailable

**Common Causes:**
- Service maintenance
- High load
- Resource exhaustion

**Example:**
```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service temporarily unavailable",
    "details": {
      "reason": "high_load"
    },
    "recovery_suggestion": "Retry after a short delay. Check service status"
  }
}
```

**Recovery:**
- Retry after a short delay
- Check service status
- Implement exponential backoff

---

## Domain-Specific Error Codes

### Voice Profile Errors

#### PROFILE_NOT_FOUND (404)
- **Message:** "Profile not found"
- **Recovery:** Verify profile ID exists

#### PROFILE_INVALID (400)
- **Message:** "Invalid profile data"
- **Recovery:** Check profile data format

#### PROFILE_QUOTA_EXCEEDED (429)
- **Message:** "Profile quota exceeded"
- **Recovery:** Delete unused profiles or upgrade plan

### Voice Synthesis Errors

#### SYNTHESIS_FAILED (500)
- **Message:** "Voice synthesis failed"
- **Recovery:** Check audio quality, retry with different parameters

#### ENGINE_UNAVAILABLE (503)
- **Message:** "Synthesis engine unavailable"
- **Recovery:** Wait and retry, or use different engine

#### INVALID_TEXT (400)
- **Message:** "Invalid text for synthesis"
- **Recovery:** Check text format and length

### Project Errors

#### PROJECT_NOT_FOUND (404)
- **Message:** "Project not found"
- **Recovery:** Verify project ID exists

#### PROJECT_QUOTA_EXCEEDED (429)
- **Message:** "Project quota exceeded"
- **Recovery:** Delete unused projects or upgrade plan

### Training Errors

#### TRAINING_FAILED (500)
- **Message:** "Training failed"
- **Recovery:** Check training data quality, verify resources

#### INSUFFICIENT_DATA (400)
- **Message:** "Insufficient training data"
- **Recovery:** Provide more training samples

### Batch Processing Errors

#### BATCH_JOB_NOT_FOUND (404)
- **Message:** "Batch job not found"
- **Recovery:** Verify job ID exists

#### BATCH_QUEUE_FULL (503)
- **Message:** "Batch queue is full"
- **Recovery:** Wait for queue space or cancel old jobs

---

## Error Handling Best Practices

### 1. Always Check Status Codes

```python
response = requests.post(url, json=data)

if response.status_code == 200:
    return response.json()
elif response.status_code == 400:
    error = response.json()
    print(f"Validation error: {error['error']['message']}")
elif response.status_code == 429:
    retry_after = response.headers.get("Retry-After", "60")
    print(f"Rate limited. Retry after {retry_after} seconds")
else:
    print(f"Error {response.status_code}")
```

### 2. Use Recovery Suggestions

```python
error = response.json()["error"]
if "recovery_suggestion" in error:
    print(f"Recovery: {error['recovery_suggestion']}")
```

### 3. Log Request IDs

```python
error = response.json()["error"]
if "request_id" in error:
    logger.error(f"Request ID: {error['request_id']}")
```

### 4. Implement Retry Logic

```python
import time

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            time.sleep(retry_after)
            continue
        
        if response.status_code < 500:
            return response
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return response
```

---

## Complete Error Code List

| Code | Status | Category | Description |
|------|--------|----------|-------------|
| `VALIDATION_ERROR` | 400 | Client | Request validation failed |
| `NOT_FOUND` | 404 | Client | Resource not found |
| `CONFLICT` | 409 | Client | Resource conflict |
| `RATE_LIMIT_EXCEEDED` | 429 | Client | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Server | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Server | Service unavailable |
| `PROFILE_NOT_FOUND` | 404 | Domain | Profile not found |
| `PROFILE_INVALID` | 400 | Domain | Invalid profile data |
| `SYNTHESIS_FAILED` | 500 | Domain | Synthesis failed |
| `ENGINE_UNAVAILABLE` | 503 | Domain | Engine unavailable |
| `TRAINING_FAILED` | 500 | Domain | Training failed |
| `BATCH_QUEUE_FULL` | 503 | Domain | Batch queue full |

---

**Last Updated:** 2025-01-28

