# VoiceStudio Quantum+ Error Handling Patterns

Comprehensive guide to error handling patterns across backend, frontend, and services.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Backend Error Handling](#backend-error-handling)
3. [Frontend Error Handling](#frontend-error-handling)
4. [Service Error Handling](#service-error-handling)
5. [Error Recovery Patterns](#error-recovery-patterns)
6. [User-Facing Error Messages](#user-facing-error-messages)
7. [Error Logging and Monitoring](#error-logging-and-monitoring)
8. [Best Practices](#best-practices)
9. [Error Handling Checklist](#error-handling-checklist)

---

## Overview

### Principles

1. **Fail Fast**: Detect errors early and fail immediately
2. **Fail Safe**: Graceful degradation when possible
3. **User-Friendly**: Always provide actionable error messages
4. **Logging**: Comprehensive error logging for debugging
5. **Recovery**: Automatic retry for transient errors
6. **Consistency**: Standardized error formats across all layers

### Error Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Error Flow                             │
│                                                           │
│  [Operation]                                             │
│      │                                                   │
│      ├─► [Error Occurs]                                 │
│      │       │                                           │
│      │       ├─► [Log Error]                            │
│      │       │                                           │
│      │       ├─► [Classify Error]                       │
│      │       │   ├─► Transient?                         │
│      │       │   ├─► Retryable?                         │
│      │       │   └─► User Actionable?                    │
│      │       │                                           │
│      │       ├─► [Handle Error]                          │
│      │       │   ├─► Retry (if transient)               │
│      │       │   ├─► Fallback (if available)            │
│      │       │   └─► Show User Message                   │
│      │       │                                           │
│      └─► [Continue or Abort]                             │
└─────────────────────────────────────────────────────────┘
```

---

## Backend Error Handling

### Standardized Error Response Format

**Location:** `backend/api/error_handling.py`

All backend errors follow a standardized format:

```python
{
    "error": true,
    "error_code": "ERROR_CODE",
    "message": "User-friendly error message",
    "request_id": "uuid",
    "timestamp": "2025-01-28T12:00:00Z",
    "details": {
        // Additional error details
    },
    "path": "/api/endpoint"
}
```

### Error Codes

**Location:** `backend/api/error_handling.py` - `ErrorCodes` class

#### Validation Errors (4xx)
- `VALIDATION_ERROR`: General validation failure
- `INVALID_INPUT`: Invalid input data
- `MISSING_REQUIRED_FIELD`: Required field missing
- `INVALID_FORMAT`: Invalid data format

#### Authentication/Authorization (4xx)
- `AUTHENTICATION_FAILED`: Authentication failed
- `AUTHORIZATION_FAILED`: Authorization failed
- `TOKEN_EXPIRED`: Token expired

#### Resource Errors (4xx)
- `RESOURCE_NOT_FOUND`: Resource not found
- `RESOURCE_ALREADY_EXISTS`: Resource already exists
- `RESOURCE_CONFLICT`: Resource conflict

#### Rate Limiting (4xx)
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded

#### Server Errors (5xx)
- `INTERNAL_SERVER_ERROR`: Internal server error
- `SERVICE_UNAVAILABLE`: Service unavailable
- `ENGINE_ERROR`: Engine error
- `PROCESSING_ERROR`: Processing error
- `TIMEOUT_ERROR`: Request timeout

### Exception Handlers

#### 1. Validation Exception Handler

**Handles:** `RequestValidationError` (Pydantic validation errors)

```python
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    # Format validation errors for user-friendly display
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        error_code=ErrorCodes.VALIDATION_ERROR,
        message="Request validation failed. Please check your input.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": errors}
    )
```

**Example Response:**
```json
{
    "error": true,
    "error_code": "VALIDATION_ERROR",
    "message": "Request validation failed. Please check your input.",
    "details": {
        "validation_errors": [
            {
                "field": "body -> name",
                "message": "field required",
                "type": "value_error.missing"
            }
        ]
    }
}
```

#### 2. HTTP Exception Handler

**Handles:** `HTTPException` (FastAPI HTTP exceptions)

```python
async def http_exception_handler(
    request: Request,
    exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions with standardized format."""
    # Map status codes to error codes
    status_to_code = {
        400: ErrorCodes.INVALID_INPUT,
        401: ErrorCodes.AUTHENTICATION_FAILED,
        403: ErrorCodes.AUTHORIZATION_FAILED,
        404: ErrorCodes.RESOURCE_NOT_FOUND,
        409: ErrorCodes.RESOURCE_CONFLICT,
        422: ErrorCodes.VALIDATION_ERROR,
        429: ErrorCodes.RATE_LIMIT_EXCEEDED,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
        503: ErrorCodes.SERVICE_UNAVAILABLE,
        504: ErrorCodes.TIMEOUT_ERROR,
    }
    
    error_code = status_to_code.get(exc.status_code, ErrorCodes.INTERNAL_SERVER_ERROR)
    
    return create_error_response(
        error_code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code
    )
```

#### 3. General Exception Handler

**Handles:** All unhandled exceptions

```python
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions."""
    # Log full traceback for debugging
    error_traceback = traceback.format_exc()
    logger.error(f"Unhandled exception: {str(exc)}\n{error_traceback}")
    
    # Don't expose internal errors in production
    message = "An internal server error occurred. Please try again later."
    details = None
    
    # In development, include more details
    if os.getenv("ENVIRONMENT", "production") == "development":
        details = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
    
    return create_error_response(
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details
    )
```

### Request ID Middleware

**Purpose:** Track requests across the system for debugging

```python
async def add_request_id_middleware(request: Request, call_next):
    """Middleware to add request ID to all requests."""
    request_id = generate_request_id()
    request.state.request_id = request_id
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response
```

### Usage in Route Handlers

**Example:**
```python
@router.post("/api/profiles")
async def create_profile(profile: ProfileCreate):
    try:
        # Validate profile
        if not profile.name:
            raise HTTPException(
                status_code=400,
                detail="Profile name is required"
            )
        
        # Create profile
        created = await profile_service.create(profile)
        return created
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create profile"
        )
```

---

## Frontend Error Handling

### Exception Hierarchy

**Location:** `src/VoiceStudio.Core/Exceptions/BackendException.cs`

#### Base Exception: `BackendException`

```csharp
public class BackendException : Exception
{
    public int? StatusCode { get; }
    public string? ErrorCode { get; }
    public bool IsRetryable { get; }
}
```

#### Specific Exceptions

1. **BackendUnavailableException**
   - **When:** Backend server unreachable
   - **Retryable:** Yes
   - **Error Code:** `BACKEND_UNAVAILABLE`

2. **BackendTimeoutException**
   - **When:** Request timeout
   - **Retryable:** Yes
   - **Error Code:** `BACKEND_TIMEOUT`

3. **BackendAuthenticationException**
   - **When:** Authentication failed
   - **Retryable:** No
   - **Error Code:** `AUTHENTICATION_FAILED`
   - **Status Code:** 401

4. **BackendNotFoundException**
   - **When:** Resource not found
   - **Retryable:** No
   - **Error Code:** `RESOURCE_NOT_FOUND`
   - **Status Code:** 404

5. **BackendValidationException**
   - **When:** Validation failed
   - **Retryable:** No
   - **Error Code:** `VALIDATION_ERROR`
   - **Status Code:** 400

6. **BackendServerException**
   - **When:** Server error (5xx)
   - **Retryable:** Yes (if 5xx)
   - **Error Code:** `SERVER_ERROR`

7. **BackendDeserializationException**
   - **When:** Response deserialization failed
   - **Retryable:** No
   - **Error Code:** `DESERIALIZATION_ERROR`

### Error Handler Utility

**Location:** `src/VoiceStudio.App/Utilities/ErrorHandler.cs`

#### Get User-Friendly Message

```csharp
public static string GetUserFriendlyMessage(Exception ex)
{
    return ex switch
    {
        BackendUnavailableException bex => bex.Message,
        BackendTimeoutException bex => bex.Message,
        BackendAuthenticationException bex => bex.Message,
        BackendNotFoundException bex => bex.Message,
        BackendValidationException bex => bex.Message,
        BackendServerException bex => bex.Message,
        BackendDeserializationException bex => bex.Message,
        HttpRequestException httpEx => GetHttpErrorMessage(httpEx),
        TaskCanceledException => "The operation was cancelled or timed out.",
        TimeoutException => "The operation timed out.",
        _ => $"An error occurred: {ex.Message}"
    };
}
```

#### Check if Transient Error

```csharp
public static bool IsTransientError(Exception ex)
{
    return ex switch
    {
        BackendException bex => bex.IsRetryable,
        HttpRequestException httpEx => 
            httpEx.Message.Contains("timeout") ||
            httpEx.Message.Contains("connection") ||
            (httpEx.Data.Contains("StatusCode") && 
             httpEx.Data["StatusCode"]?.ToString() is "408" or "429" or "502" or "503" or "504"),
        TaskCanceledException => true,
        TimeoutException => true,
        _ => false
    };
}
```

#### Get Recovery Suggestion

```csharp
public static string GetRecoverySuggestion(Exception ex)
{
    return ex switch
    {
        BackendUnavailableException => 
            "Make sure the backend server is running and accessible.",
        BackendTimeoutException => 
            "Check your network connection and try again.",
        BackendAuthenticationException => 
            "Please check your credentials and try again.",
        BackendNotFoundException => 
            "The requested resource may have been deleted or moved.",
        BackendValidationException => 
            "Please check your input and try again.",
        BackendServerException bex when bex.StatusCode >= 500 => 
            "The server encountered an error. Please try again in a moment.",
        _ => "Please try again. If the problem persists, check the logs."
    };
}
```

### BaseViewModel Error Handling

**Location:** `src/VoiceStudio.App/ViewModels/BaseViewModel.cs`

#### Execute with Error Handling

```csharp
protected async Task<T?> ExecuteWithErrorHandlingAsync<T>(
    Func<Task<T>> operation,
    string context = "",
    int maxRetries = 0,
    bool showDialog = true,
    Func<Exception, bool>? shouldRetry = null)
{
    int attempts = 0;
    Exception? lastException = null;

    while (attempts <= maxRetries)
    {
        try
        {
            return await operation();
        }
        catch (Exception ex)
        {
            lastException = ex;
            attempts++;

            // Check if we should retry
            bool canRetry = attempts <= maxRetries;
            if (canRetry && shouldRetry != null)
            {
                canRetry = shouldRetry(ex);
            }

            if (canRetry && IsRetryableException(ex))
            {
                // Wait before retrying (exponential backoff)
                await Task.Delay(Math.Min(1000 * (int)Math.Pow(2, attempts - 1), 10000));
                continue;
            }

            // Can't retry or max retries reached
            await HandleErrorAsync(ex, context, showDialog);
            return default(T);
        }
    }

    // If we get here, all retries failed
    if (lastException != null)
    {
        await HandleErrorAsync(lastException, context, showDialog);
    }

    return default(T);
}
```

#### Handle Error

```csharp
protected async Task HandleErrorAsync(Exception exception, string context = "", bool showDialog = true)
{
    if (exception == null)
        return;

    // Log the error
    ErrorLoggingService?.LogError(exception, context);

    // Show error dialog if requested
    if (showDialog && ErrorDialogService != null)
    {
        await ErrorDialogService.ShowErrorAsync(exception, context: context);
    }
}
```

### BackendClient Error Handling

**Location:** `src/VoiceStudio.App/Services/BackendClient.cs`

#### Retry with Circuit Breaker

```csharp
private async Task<T> ExecuteWithRetryAsync<T>(Func<Task<T>> operation, int maxRetries = MaxRetries)
{
    // Check connection status periodically
    await UpdateConnectionStatusAsync();

    // Execute through circuit breaker with exponential backoff retry
    try
    {
        return await _circuitBreaker.ExecuteAsync(async () =>
            await RetryHelper.ExecuteWithExponentialBackoffAsync(
                operation,
                maxRetries: maxRetries,
                initialDelayMs: RetryDelayMs,
                maxDelayMs: 10000
            )
        );
    }
    catch (Exception ex)
    {
        // Update connection status on failure
        await UpdateConnectionStatusAsync();
        
        // Convert to appropriate BackendException
        if (ex is HttpRequestException httpEx)
        {
            _isConnected = false;
            throw new BackendUnavailableException(
                "Unable to connect to the backend server.",
                httpEx);
        }
        else if (ex is TaskCanceledException timeoutEx)
        {
            _isConnected = false;
            throw new BackendTimeoutException(
                "The request timed out.",
                timeoutEx);
        }
        
        throw;
    }
}
```

#### Create Exception from Response

```csharp
private async Task<BackendException> CreateExceptionFromResponseAsync(HttpResponseMessage response)
{
    var statusCode = (int)response.StatusCode;
    string? errorMessage = null;
    string? errorCode = null;

    try
    {
        var content = await response.Content.ReadAsStringAsync();
        if (!string.IsNullOrEmpty(content))
        {
            var errorJson = JsonSerializer.Deserialize<JsonElement>(content, _jsonOptions);
            if (errorJson.TryGetProperty("message", out var messageProp))
                errorMessage = messageProp.GetString();
            if (errorJson.TryGetProperty("error_code", out var codeProp))
                errorCode = codeProp.GetString();
        }
    }
    catch
    {
        // Ignore errors reading response
    }

    // Create appropriate exception based on status code
    return statusCode switch
    {
        400 => new BackendValidationException(errorMessage ?? "Invalid request"),
        401 => new BackendAuthenticationException(errorMessage ?? "Authentication failed"),
        404 => new BackendNotFoundException(errorMessage ?? "Resource not found"),
        408 => new BackendTimeoutException(errorMessage ?? "Request timeout"),
        429 => new BackendServerException(errorMessage ?? "Rate limit exceeded", statusCode),
        >= 500 => new BackendServerException(errorMessage ?? "Server error", statusCode),
        _ => new BackendException(errorMessage ?? "Unknown error", statusCode, errorCode)
    };
}
```

---

## Service Error Handling

### Error Logging Service

**Location:** `src/VoiceStudio.App/Services/ErrorLoggingService.cs`

```csharp
public interface IErrorLoggingService
{
    void LogError(Exception exception, string context = "");
    void LogWarning(string message, string context = "");
    void LogInfo(string message, string context = "");
}
```

### Error Dialog Service

**Location:** `src/VoiceStudio.App/Services/ErrorDialogService.cs`

```csharp
public interface IErrorDialogService
{
    Task ShowErrorAsync(Exception exception, string? title = null, string? context = null);
    Task ShowErrorAsync(string message, string? title = null, string? recoverySuggestion = null);
    Task ShowWarningAsync(string message, string? title = null);
}
```

**Implementation:**
```csharp
public async Task ShowErrorAsync(Exception exception, string? title = null, string? context = null)
{
    if (exception == null)
        return;

    // Log the error
    _errorLoggingService?.LogError(exception, context);

    var userMessage = ErrorHandler.GetUserFriendlyMessage(exception);
    var recoverySuggestion = ErrorHandler.GetRecoverySuggestion(exception);
    var dialogTitle = title ?? GetErrorTitle(exception);

    await ShowErrorDialogAsync(dialogTitle, userMessage, recoverySuggestion, exception);
}
```

---

## Error Recovery Patterns

### 1. Retry Pattern

**Use Case:** Transient errors (network issues, timeouts)

**Implementation:**
```csharp
protected async Task<T?> ExecuteWithRetryAsync<T>(
    Func<Task<T>> operation,
    int maxRetries = 3,
    int initialDelayMs = 1000)
{
    int attempts = 0;
    Exception? lastException = null;

    while (attempts <= maxRetries)
    {
        try
        {
            return await operation();
        }
        catch (Exception ex)
        {
            lastException = ex;
            attempts++;

            if (attempts > maxRetries || !IsRetryableException(ex))
            {
                throw;
            }

            // Exponential backoff
            await Task.Delay(Math.Min(initialDelayMs * (int)Math.Pow(2, attempts - 1), 10000));
        }
    }

    throw lastException ?? new Exception("Retry failed");
}
```

### 2. Circuit Breaker Pattern

**Use Case:** Prevent cascading failures when backend is down

**Implementation:**
```csharp
public class CircuitBreaker
{
    private CircuitState _state = CircuitState.Closed;
    private int _failureCount = 0;
    private DateTime _lastFailureTime = DateTime.MinValue;
    private readonly int _failureThreshold;
    private readonly TimeSpan _timeout;

    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
        if (_state == CircuitState.Open)
        {
            if (DateTime.UtcNow - _lastFailureTime > _timeout)
            {
                _state = CircuitState.HalfOpen;
            }
            else
            {
                throw new InvalidOperationException("Circuit breaker is open");
            }
        }

        try
        {
            var result = await operation();
            OnSuccess();
            return result;
        }
        catch (Exception ex)
        {
            OnFailure();
            throw;
        }
    }

    private void OnSuccess()
    {
        _failureCount = 0;
        _state = CircuitState.Closed;
    }

    private void OnFailure()
    {
        _failureCount++;
        _lastFailureTime = DateTime.UtcNow;

        if (_failureCount >= _failureThreshold)
        {
            _state = CircuitState.Open;
        }
    }
}
```

### 3. Fallback Pattern

**Use Case:** Provide alternative behavior when primary operation fails

**Implementation:**
```csharp
protected async Task<T> ExecuteWithFallbackAsync<T>(
    Func<Task<T>> primaryOperation,
    Func<Task<T>> fallbackOperation)
{
    try
    {
        return await primaryOperation();
    }
    catch (Exception ex)
    {
        if (IsRetryableException(ex))
        {
            // Try fallback
            try
            {
                return await fallbackOperation();
            }
            catch
            {
                throw ex; // Throw original exception
            }
        }
        throw;
    }
}
```

### 4. State Persistence Pattern

**Use Case:** Save state before critical operations for recovery

**Implementation:**
```csharp
protected async Task<T?> ExecuteWithStatePersistenceAsync<T>(
    Func<Task<T>> operation,
    string operationId,
    object? stateToSave = null)
{
    // Save state before operation
    string? savedStatePath = null;
    if (stateToSave != null && StatePersistenceService != null)
    {
        savedStatePath = await StatePersistenceService.SaveStateAsync(operationId, stateToSave);
    }

    try
    {
        return await operation();
    }
    catch (Exception ex)
    {
        // If operation fails and we have saved state, offer to restore
        if (!string.IsNullOrEmpty(savedStatePath) && ErrorDialogService != null)
        {
            var restore = await ErrorDialogService.ShowErrorAsync(
                ex,
                title: "Operation Failed",
                retryAction: async () =>
                {
                    // Restore state and retry
                    if (StatePersistenceService != null && stateToSave != null)
                    {
                        var restored = await StatePersistenceService.RestoreStateAsync<object>(savedStatePath);
                        if (restored != null)
                        {
                            await operation();
                        }
                    }
                });
        }
        else
        {
            await HandleErrorAsync(ex);
        }
        return default(T);
    }
}
```

---

## User-Facing Error Messages

### Message Guidelines

1. **Be Clear**: Use plain language, avoid technical jargon
2. **Be Actionable**: Tell the user what they can do
3. **Be Specific**: Include relevant details (field names, values)
4. **Be Helpful**: Provide recovery suggestions
5. **Be Concise**: Keep messages short and to the point

### Message Templates

#### Validation Errors
```
❌ "Please check your input"
✅ "The profile name is required. Please enter a name and try again."
```

#### Network Errors
```
❌ "Connection failed"
✅ "Cannot connect to the server. Please check your connection and ensure the backend is running."
```

#### Not Found Errors
```
❌ "Not found"
✅ "The profile 'Test Profile' was not found. It may have been deleted or moved."
```

#### Server Errors
```
❌ "Server error"
✅ "The server encountered an error. Please try again in a moment. If the problem persists, check the server logs."
```

### Error Dialog Structure

```
┌─────────────────────────────────────────┐
│  [Icon]  Error Title                    │
├─────────────────────────────────────────┤
│                                         │
│  Error Message                          │
│  (User-friendly, clear)                 │
│                                         │
│  ────────────────────────────────────  │
│                                         │
│  Suggestion:                            │
│  Recovery steps or suggestions          │
│                                         │
│  ────────────────────────────────────  │
│                                         │
│  [Show Details] [Retry] [OK]            │
│                                         │
└─────────────────────────────────────────┘
```

---

## Error Logging and Monitoring

### Log Levels

1. **Error**: Exceptions, failures, critical issues
2. **Warning**: Recoverable issues, deprecations
3. **Info**: Important events, state changes
4. **Debug**: Detailed information for debugging

### Log Format

```
[Timestamp] [Level] [Context] Message
[Timestamp] [Level] [Context] Exception: Type - Message
[Timestamp] [Level] [Context] Stack Trace: ...
```

### Log Context

Include:
- Request ID (if available)
- User ID (if available)
- Operation context
- Relevant parameters (sanitized)
- Error code
- Status code

### Example Log Entry

```
2025-01-28 12:00:00 [ERROR] [BackendClient.CreateProfile] 
Exception: BackendValidationException - Profile name is required
Request ID: 123e4567-e89b-12d3-a456-426614174000
Status Code: 400
Stack Trace: ...
```

---

## Best Practices

### 1. Always Handle Errors

```csharp
// ❌ Bad
await backendClient.CreateProfileAsync(profile);

// ✅ Good
try
{
    await backendClient.CreateProfileAsync(profile);
}
catch (Exception ex)
{
    await HandleErrorAsync(ex, "Creating profile");
}
```

### 2. Use Specific Exceptions

```csharp
// ❌ Bad
throw new Exception("Error");

// ✅ Good
throw new BackendValidationException("Profile name is required");
```

### 3. Log Before Handling

```csharp
// ✅ Good
catch (Exception ex)
{
    ErrorLoggingService?.LogError(ex, "Creating profile");
    await HandleErrorAsync(ex, "Creating profile");
}
```

### 4. Provide Recovery Suggestions

```csharp
// ✅ Good
var suggestion = ErrorHandler.GetRecoverySuggestion(ex);
await ErrorDialogService.ShowErrorAsync(ex, recoverySuggestion: suggestion);
```

### 5. Don't Expose Internal Details

```csharp
// ❌ Bad (in production)
message = f"Database error: {str(ex)}"

// ✅ Good
message = "An internal server error occurred. Please try again later."
if environment == "development":
    details = {"exception": str(ex)}
```

### 6. Use Retry for Transient Errors

```csharp
// ✅ Good
if (ErrorHandler.IsTransientError(ex))
{
    await ExecuteWithRetryAsync(operation, maxRetries: 3);
}
```

### 7. Validate Early

```csharp
// ✅ Good
if (string.IsNullOrWhiteSpace(profile.Name))
{
    throw new BackendValidationException("Profile name is required");
}
```

### 8. Use Circuit Breaker for External Services

```csharp
// ✅ Good
return await _circuitBreaker.ExecuteAsync(async () =>
    await backendClient.CreateProfileAsync(profile)
);
```

---

## Error Handling Checklist

### For Backend Routes

- [ ] Validate input using Pydantic models
- [ ] Use appropriate HTTP status codes
- [ ] Return standardized error format
- [ ] Log errors with context
- [ ] Include request ID in response
- [ ] Don't expose internal errors in production
- [ ] Provide user-friendly error messages

### For Frontend ViewModels

- [ ] Use `BaseViewModel` error handling methods
- [ ] Handle exceptions in async operations
- [ ] Show user-friendly error messages
- [ ] Log errors with context
- [ ] Retry transient errors
- [ ] Use circuit breaker for backend calls
- [ ] Provide recovery suggestions

### For Services

- [ ] Handle service-specific exceptions
- [ ] Log errors appropriately
- [ ] Return meaningful error information
- [ ] Use retry for transient errors
- [ ] Implement fallback when possible
- [ ] Don't swallow exceptions silently

### For UI Components

- [ ] Show loading states during operations
- [ ] Display error messages clearly
- [ ] Provide retry options when appropriate
- [ ] Disable actions during error states
- [ ] Use toast notifications for non-critical errors
- [ ] Use dialogs for critical errors

---

## Summary

VoiceStudio Quantum+ uses a comprehensive error handling system:

1. **Backend**: Standardized error responses with error codes
2. **Frontend**: Exception hierarchy with user-friendly messages
3. **Services**: Centralized error handling utilities
4. **Recovery**: Retry, circuit breaker, and fallback patterns
5. **Logging**: Comprehensive error logging with context
6. **User Experience**: Clear, actionable error messages

**Key Files:**
- `backend/api/error_handling.py` - Backend error handling
- `src/VoiceStudio.Core/Exceptions/BackendException.cs` - Exception hierarchy
- `src/VoiceStudio.App/Utilities/ErrorHandler.cs` - Error handling utilities
- `src/VoiceStudio.App/ViewModels/BaseViewModel.cs` - Base error handling
- `src/VoiceStudio.App/Services/BackendClient.cs` - Backend client error handling

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After major error handling changes

