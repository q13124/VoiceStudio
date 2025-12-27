# VoiceStudio Quantum+ Error Handling Guide

Complete guide for standardized error handling in the VoiceStudio API.

## Table of Contents

1. [Error Response Format](#error-response-format)
2. [Error Code Categories](#error-code-categories)
3. [Using Standardized Errors in Backend](#using-standardized-errors-in-backend)
4. [Handling Errors in C# Client](#handling-errors-in-c-client)
5. [Error Code Reference](#error-code-reference)
6. [Best Practices](#best-practices)

---

## Error Response Format

All API errors follow a standardized format:

```json
{
  "error": true,
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "Profile 'profile_123' not found",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-28T10:00:00Z",
  "details": {
    "profile_id": "profile_123"
  },
  "path": "/api/profiles/profile_123",
  "recovery_suggestion": "Please verify the profile ID exists or create a new profile."
}
```

### Response Fields

- **`error`**: Always `true` for error responses
- **`error_code`**: Standard error code (see [Error Code Reference](#error-code-reference))
- **`message`**: Human-readable error message
- **`request_id`**: Unique request identifier for tracking
- **`timestamp`**: ISO 8601 timestamp of when the error occurred
- **`details`**: Additional error context (optional)
- **`path`**: API endpoint path where error occurred
- **`recovery_suggestion`**: Suggested action to resolve the error (optional)

---

## Error Code Categories

### 4xx Client Errors

These errors indicate issues with the client request:

- **VALIDATION_ERROR** (422): Request validation failed
- **INVALID_INPUT** (400): Invalid input provided
- **RESOURCE_NOT_FOUND** (404): Requested resource not found
- **RESOURCE_ALREADY_EXISTS** (409): Resource already exists
- **AUTHENTICATION_FAILED** (401): Authentication failed
- **AUTHORIZATION_FAILED** (403): Insufficient permissions
- **RATE_LIMIT_EXCEEDED** (429): Rate limit exceeded

### 5xx Server Errors

These errors indicate server-side issues:

- **INTERNAL_SERVER_ERROR** (500): Unexpected server error
- **SERVICE_UNAVAILABLE** (503): Service temporarily unavailable
- **ENGINE_ERROR** (500): Voice engine error
- **AUDIO_PROCESSING_ERROR** (500): Audio processing failed
- **TIMEOUT_ERROR** (504): Request timeout

---

## Using Standardized Errors in Backend

### Option 1: Use Custom Exceptions (Recommended)

Use domain-specific exceptions from `backend.api.exceptions`:

```python
from backend.api.exceptions import ProfileNotFoundException, InvalidInputException

# Raise not found error
if not profile:
    raise ProfileNotFoundException(profile_id)

# Raise validation error
if not name or len(name.strip()) == 0:
    raise InvalidInputException("Profile name cannot be empty", field="name")
```

### Option 2: Use Helper Function

Use the `raise_standardized_error` helper function:

```python
from backend.api.error_handling import raise_standardized_error, ErrorCodes

# Raise standardized error
if not profile:
    raise raise_standardized_error(
        ErrorCodes.RESOURCE_NOT_FOUND,
        f"Profile '{profile_id}' not found",
        status_code=404,
        details={"profile_id": profile_id},
        recovery_suggestion="Please verify the profile ID exists or create a new profile."
    )
```

### Option 3: Use HTTPException (Automatically Converted)

Plain `HTTPException` is automatically converted to standardized format:

```python
from fastapi import HTTPException

# This will be automatically converted to standardized format
if not profile:
    raise HTTPException(status_code=404, detail="Profile not found")
```

**Note:** While this works, using custom exceptions or the helper function provides better error context and recovery suggestions.

---

## Handling Errors in C# Client

### Standard Error Handling Pattern

```csharp
try
{
    var profile = await _backendClient.GetProfileAsync("profile_123", cancellationToken);
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    // Handle 404 - Resource not found
    var errorResponse = await ParseErrorResponseAsync(ex);
    Console.WriteLine($"Error: {errorResponse.ErrorCode} - {errorResponse.Message}");
    Console.WriteLine($"Recovery: {errorResponse.RecoverySuggestion}");
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.BadRequest)
{
    // Handle 400 - Validation error
    var errorResponse = await ParseErrorResponseAsync(ex);
    Console.WriteLine($"Validation Error: {errorResponse.Message}");
    if (errorResponse.Details != null)
    {
        // Process validation details
    }
}
catch (HttpRequestException ex)
{
    // Handle other HTTP errors
    Console.WriteLine($"HTTP Error {ex.StatusCode}: {ex.Message}");
}
catch (Exception ex)
{
    // Handle other errors
    Console.WriteLine($"Error: {ex.Message}");
}
```

### Error Response Model

Create a model to deserialize error responses:

```csharp
public class ErrorResponse
{
    [JsonPropertyName("error")]
    public bool Error { get; set; }

    [JsonPropertyName("error_code")]
    public string ErrorCode { get; set; }

    [JsonPropertyName("message")]
    public string Message { get; set; }

    [JsonPropertyName("request_id")]
    public string RequestId { get; set; }

    [JsonPropertyName("timestamp")]
    public DateTime Timestamp { get; set; }

    [JsonPropertyName("details")]
    public Dictionary<string, object> Details { get; set; }

    [JsonPropertyName("path")]
    public string Path { get; set; }

    [JsonPropertyName("recovery_suggestion")]
    public string RecoverySuggestion { get; set; }
}

// Helper method to parse error response
private async Task<ErrorResponse> ParseErrorResponseAsync(HttpRequestException ex)
{
    // Extract error response from exception
    // Implementation depends on your HTTP client library
    return JsonSerializer.Deserialize<ErrorResponse>(errorJson);
}
```

### Error Code Handling

```csharp
public enum ApiErrorCode
{
    ValidationError,
    InvalidInput,
    ResourceNotFound,
    ResourceAlreadyExists,
    AuthenticationFailed,
    AuthorizationFailed,
    RateLimitExceeded,
    InternalServerError,
    ServiceUnavailable,
    EngineError,
    AudioProcessingError,
    TimeoutError
}

public static class ErrorCodeMapper
{
    public static ApiErrorCode MapFromString(string errorCode)
    {
        return errorCode switch
        {
            "VALIDATION_ERROR" => ApiErrorCode.ValidationError,
            "INVALID_INPUT" => ApiErrorCode.InvalidInput,
            "RESOURCE_NOT_FOUND" => ApiErrorCode.ResourceNotFound,
            "RESOURCE_ALREADY_EXISTS" => ApiErrorCode.ResourceAlreadyExists,
            "AUTHENTICATION_FAILED" => ApiErrorCode.AuthenticationFailed,
            "AUTHORIZATION_FAILED" => ApiErrorCode.AuthorizationFailed,
            "RATE_LIMIT_EXCEEDED" => ApiErrorCode.RateLimitExceeded,
            "INTERNAL_SERVER_ERROR" => ApiErrorCode.InternalServerError,
            "SERVICE_UNAVAILABLE" => ApiErrorCode.ServiceUnavailable,
            "ENGINE_ERROR" => ApiErrorCode.EngineError,
            "AUDIO_PROCESSING_ERROR" => ApiErrorCode.AudioProcessingError,
            "TIMEOUT_ERROR" => ApiErrorCode.TimeoutError,
            _ => ApiErrorCode.InternalServerError
        };
    }
}
```

---

## Error Code Reference

### Validation Errors (4xx)

| Error Code               | Status | Description               |
| ------------------------ | ------ | ------------------------- |
| `VALIDATION_ERROR`       | 422    | Request validation failed |
| `INVALID_INPUT`          | 400    | Invalid input provided    |
| `MISSING_REQUIRED_FIELD` | 400    | Required field is missing |
| `INVALID_FORMAT`         | 400    | Invalid format            |
| `INVALID_RANGE`          | 400    | Value out of valid range  |
| `INVALID_TYPE`           | 400    | Invalid data type         |
| `INVALID_ENUM_VALUE`     | 400    | Invalid enum value        |

### Resource Errors (4xx)

| Error Code                | Status | Description             |
| ------------------------- | ------ | ----------------------- |
| `RESOURCE_NOT_FOUND`      | 404    | Resource not found      |
| `RESOURCE_ALREADY_EXISTS` | 409    | Resource already exists |
| `RESOURCE_CONFLICT`       | 409    | Resource conflict       |
| `RESOURCE_LOCKED`         | 423    | Resource is locked      |
| `RESOURCE_DELETED`        | 410    | Resource was deleted    |

### Authentication/Authorization (4xx)

| Error Code                 | Status | Description              |
| -------------------------- | ------ | ------------------------ |
| `AUTHENTICATION_FAILED`    | 401    | Authentication failed    |
| `AUTHORIZATION_FAILED`     | 403    | Insufficient permissions |
| `TOKEN_EXPIRED`            | 401    | Token expired            |
| `TOKEN_INVALID`            | 401    | Invalid token            |
| `INSUFFICIENT_PERMISSIONS` | 403    | Insufficient permissions |

### Engine Errors (4xx/5xx)

| Error Code                     | Status | Description                  |
| ------------------------------ | ------ | ---------------------------- |
| `ENGINE_ERROR`                 | 500    | Engine error                 |
| `ENGINE_UNAVAILABLE`           | 503    | Engine unavailable           |
| `ENGINE_TIMEOUT`               | 504    | Engine timeout               |
| `ENGINE_INITIALIZATION_FAILED` | 500    | Engine initialization failed |
| `ENGINE_PROCESSING_ERROR`      | 500    | Engine processing error      |

### Audio Processing Errors (5xx)

| Error Code               | Status | Description            |
| ------------------------ | ------ | ---------------------- |
| `AUDIO_PROCESSING_ERROR` | 500    | Audio processing error |
| `AUDIO_FORMAT_ERROR`     | 400    | Invalid audio format   |
| `AUDIO_TOO_LARGE`        | 413    | Audio file too large   |
| `AUDIO_CORRUPTED`        | 400    | Audio file corrupted   |

### Server Errors (5xx)

| Error Code              | Status | Description           |
| ----------------------- | ------ | --------------------- |
| `INTERNAL_SERVER_ERROR` | 500    | Internal server error |
| `SERVICE_UNAVAILABLE`   | 503    | Service unavailable   |
| `PROCESSING_ERROR`      | 500    | Processing error      |
| `TIMEOUT_ERROR`         | 504    | Request timeout       |
| `DATABASE_ERROR`        | 500    | Database error        |
| `CONFIGURATION_ERROR`   | 500    | Configuration error   |

---

## Best Practices

### For Backend Developers

1. **Use Custom Exceptions**: Prefer domain-specific exceptions from `backend.api.exceptions`
2. **Provide Context**: Always include relevant context in error details
3. **Add Recovery Suggestions**: Help users understand how to fix the error
4. **Use Appropriate Status Codes**: Match HTTP status codes to error types
5. **Log Errors**: All errors are automatically logged with request IDs

### For Frontend/C# Developers

1. **Handle Errors Gracefully**: Always catch and handle API errors
2. **Display User-Friendly Messages**: Show error messages to users
3. **Use Recovery Suggestions**: Display recovery suggestions when available
4. **Log Request IDs**: Include request IDs in error reports for debugging
5. **Retry Transient Errors**: Retry 5xx errors with exponential backoff
6. **Don't Retry Client Errors**: Don't retry 4xx errors (except 429)

### Error Handling Checklist

- [ ] All errors return standardized format
- [ ] Error codes are consistent across endpoints
- [ ] Recovery suggestions are provided
- [ ] Request IDs are included for tracking
- [ ] Errors are logged with context
- [ ] Frontend handles all error types
- [ ] Error messages are user-friendly

---

## Examples

### Example 1: Resource Not Found

**Request:**

```http
GET /api/profiles/invalid_id
```

**Response:**

```json
{
  "error": true,
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "Profile 'invalid_id' not found",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-28T10:00:00Z",
  "details": {
    "profile_id": "invalid_id"
  },
  "path": "/api/profiles/invalid_id",
  "recovery_suggestion": "Please verify the profile ID exists or create a new profile."
}
```

### Example 2: Validation Error

**Request:**

```http
POST /api/profiles
Content-Type: application/json

{
  "name": ""
}
```

**Response:**

```json
{
  "error": true,
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed. Please check your input.",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-01-28T10:00:01Z",
  "details": {
    "validation_errors": [
      {
        "field": "body -> name",
        "message": "String should have at least 1 character",
        "type": "string_too_short"
      }
    ]
  },
  "path": "/api/profiles",
  "recovery_suggestion": "Please provide a valid profile name."
}
```

### Example 3: Engine Error

**Request:**

```http
POST /api/voice/synthesize
```

**Response:**

```json
{
  "error": true,
  "error_code": "ENGINE_PROCESSING_ERROR",
  "message": "Engine 'xtts_v2' failed during synthesis: Model loading failed",
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2025-01-28T10:00:02Z",
  "details": {
    "engine": "xtts_v2",
    "operation": "synthesis",
    "error_message": "Model loading failed"
  },
  "path": "/api/voice/synthesize",
  "recovery_suggestion": "Please try again or contact support if the issue persists."
}
```

---

**Last Updated:** 2025-01-28  
**Version:** 1.0.0
