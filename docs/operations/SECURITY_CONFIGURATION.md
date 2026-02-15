# VoiceStudio Security Configuration Guide

> **Version**: 1.0
> **Last Updated**: 2026-02-14
> **Classification**: Operations Documentation

---

## Overview

This guide documents VoiceStudio's security infrastructure, including credential management, error handling, health monitoring, and operational security controls. It serves as the authoritative reference for security configuration and operations.

---

## 1. Credential Storage

### 1.1 Architecture

VoiceStudio uses a secure, multi-layered credential storage system:

| Layer | Technology | Use Case |
|-------|------------|----------|
| Windows Credential Manager | `PasswordVault` | API keys, tokens (< 1KB) |
| DPAPI | `ProtectedData` | Larger secrets, OAuth tokens, configs |
| Environment Variables | System env | CI/CD, production overrides |
| Dev Vault | Encrypted JSON | Development-only fallback |

### 1.2 Key Components

#### SecureStorageService (`src/VoiceStudio.App/Services/SecureStorage.cs`)

```csharp
// Store API key securely
var storage = new SecureStorageService();
storage.StoreCredential("apikey:elevenlabs", apiKey);

// Retrieve API key
string? key = storage.GetCredential("apikey:elevenlabs");

// Store larger data with DPAPI
await storage.StoreProtectedObjectAsync("oauth:github", tokenObject);
```

**Features:**
- User-scoped DPAPI encryption (current Windows user only)
- Key-specific entropy for additional protection
- Secure memory wipe on disposal
- Availability detection for DPAPI

#### ISecretsService Interface (`src/VoiceStudio.App/Core/Services/ISecretsService.cs`)

```csharp
public interface ISecretsService
{
    Task<string?> GetSecretAsync(string key, string? defaultValue = null, CancellationToken ct = default);
    Task<bool> SetSecretAsync(string key, string value, CancellationToken ct = default);
    Task<bool> DeleteSecretAsync(string key, CancellationToken ct = default);
    Task<IReadOnlyList<string>> ListSecretsAsync(CancellationToken ct = default);
    Task<bool> SecretExistsAsync(string key, CancellationToken ct = default);
}
```

**Implementations:**
- `WindowsCredentialManagerSecretsService` - Production (uses Windows Credential Manager)
- `DevVaultSecretsService` - Development (uses encrypted local file)

### 1.3 Priority Order

Secret retrieval follows this priority:
1. **Environment Variable** - Highest priority, for CI/CD overrides
2. **Credential Manager / Dev Vault** - Application-stored secrets
3. **Default Value** - Fallback if not found

### 1.4 Security Best Practices

```csharp
// ✅ DO: Use SecureStorageService for API keys
storage.StoreApiKey("openai", apiKey);

// ✅ DO: Use DPAPI for larger sensitive data
await storage.StoreProtectedObjectAsync("session", sessionData);

// ✅ DO: Check availability before use
if (!SecureStorageService.IsDpapiAvailable())
{
    // Handle gracefully - DPAPI unavailable
}

// ❌ DON'T: Store secrets in plaintext config files
// ❌ DON'T: Log secrets or include in error messages
// ❌ DON'T: Commit api-keys.json or .env.mcp.local
```

---

## 2. Error Boundaries

### 2.1 Architecture

VoiceStudio implements defense-in-depth error handling:

```
┌─────────────────────────────────────────────────────────────┐
│                    Global Exception Handler                  │
│                  (App.xaml.cs, Program.cs)                  │
├─────────────────────────────────────────────────────────────┤
│                   Error Boundary Utilities                   │
│                    (ErrorBoundary.cs)                        │
├─────────────────────────────────────────────────────────────┤
│                   Error Handler Utilities                    │
│                    (ErrorHandler.cs)                         │
├─────────────────────────────────────────────────────────────┤
│                  Error Presentation Service                  │
│                 (ErrorDialogService.cs)                      │
├─────────────────────────────────────────────────────────────┤
│                   ViewModel Error Handling                   │
│                   (per-feature catch blocks)                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Key Components

#### ErrorHandler (`src/VoiceStudio.App/Utilities/ErrorHandler.cs`)

Centralized error processing with:
- User-friendly message generation
- Recovery suggestion mapping
- Transient error detection
- Exception-type-specific handling

```csharp
try
{
    await SomeOperation();
}
catch (Exception ex)
{
    // Get user-friendly message
    ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
    
    // Check if retry might help
    if (ErrorHandler.IsTransientError(ex))
    {
        // Offer retry option
    }
    
    // Get recovery suggestion
    var suggestion = ErrorHandler.GetRecoverySuggestion(ex);
}
```

#### ErrorBoundary (`src/VoiceStudio.App/Core/ErrorHandling/ErrorBoundary.cs`)

Static helper methods for safe execution:

```csharp
// Execute with fallback on error
var result = ErrorBoundary.TryExecute(
    () => RiskyOperation(),
    fallbackValue: defaultResult
);

// Execute with async support
var result = await ErrorBoundary.TryExecuteAsync(
    async () => await RiskyAsyncOperation(),
    fallbackValue: defaultResult
);
```

#### Global Exception Handlers

**App.xaml.cs:**
```csharp
this.UnhandledException += App_UnhandledException;
```

**Program.cs:**
```csharp
AppDomain.CurrentDomain.UnhandledException += (sender, evt) => { ... };
```

### 2.3 Error Response Patterns

| Exception Type | User Message | Recovery Action |
|----------------|--------------|-----------------|
| `BackendUnavailableException` | "Backend server not available" | Check server, retry |
| `BackendTimeoutException` | "Operation timed out" | Retry, check connection |
| `BackendAuthenticationException` | "Authentication failed" | Re-authenticate |
| `BackendValidationException` | "Invalid input" | Fix input, retry |
| `HttpRequestException` | Network-specific message | Check connection |
| `TaskCanceledException` | "Operation cancelled" | Retry |

### 2.4 Best Practices

```csharp
// ✅ DO: Use ErrorHandler for consistent messages
ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);

// ✅ DO: Log full exception, show friendly message
ErrorHandler.LogError(ex, "MyOperation");
ShowUserMessage(ErrorHandler.GetUserFriendlyMessage(ex));

// ✅ DO: Check for transient errors before retry
if (ErrorHandler.IsTransientError(ex))
{
    await RetryWithBackoff();
}

// ❌ DON'T: Show raw exception messages to users
// ❌ DON'T: Swallow exceptions without logging
// ❌ DON'T: Crash the application on recoverable errors
```

---

## 3. Health Check System

### 3.1 Architecture

VoiceStudio provides comprehensive health monitoring:

```
┌─────────────────────────────────────────────────────────────┐
│                    Health Check Endpoints                    │
│                  GET /api/health/*                          │
├─────────────────────────────────────────────────────────────┤
│                  Health Check Service                        │
│            (backend/monitoring/health/health_check.py)       │
├───────────┬───────────┬───────────┬───────────┬─────────────┤
│  Database │   GPU     │  Engines  │   Disk    │   Memory    │
│   Check   │   Check   │   Check   │   Check   │   Check     │
└───────────┴───────────┴───────────┴───────────┴─────────────┘
```

### 3.2 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Quick health status |
| `/api/health/detailed` | GET | Full component status |
| `/v1/health/metrics` | GET | Metrics for sentinel testing |

### 3.3 Health Check Types

```python
# Critical checks - must pass for system healthy
_health_checker.register_check("database", _check_database, critical=True)

# Non-critical checks - degraded but functional
_health_checker.register_check("gpu", lambda: _check_gpu()["status"] == "healthy")
_health_checker.register_check("engines", lambda: _check_engines()["status"] == "healthy")
```

### 3.4 Health Status Values

| Status | Meaning | Response Code |
|--------|---------|---------------|
| `healthy` | All checks pass | 200 |
| `degraded` | Non-critical checks fail | 200 |
| `unhealthy` | Critical checks fail | 503 |

### 3.5 Configuration

```bash
# Environment variables
VOICESTUDIO_HEALTH_CHECK_TIMEOUT=5.0  # Timeout per check (seconds)
VOICESTUDIO_HEALTH_CHECK_INTERVAL=5000  # Check interval (ms)
VOICESTUDIO_HEALTH_ENABLE_TORCH=1  # Enable GPU detection (can crash on some systems)
```

---

## 4. Graceful Shutdown

### 4.1 Architecture

VoiceStudio implements phased graceful shutdown:

```
RUNNING → INITIATED → DRAINING → COMPLETING → ENGINES → CONNECTIONS → CLEANUP → COMPLETED
```

| Phase | Description | Timeout |
|-------|-------------|---------|
| DRAINING | Stop accepting new requests | 5s |
| COMPLETING | Wait for in-flight requests | 5s |
| ENGINES | Shutdown ML engines | 12s |
| CONNECTIONS | Close DB/network connections | 5s |
| CLEANUP | Final resource cleanup | 3s |

### 4.2 Key Components

#### GracefulShutdownOrchestrator (`backend/lifecycle/shutdown.py`)

```python
from backend.lifecycle.shutdown import get_shutdown_orchestrator

orchestrator = get_shutdown_orchestrator()

# Register a shutdown handler
@orchestrator.register(
    name="my_service",
    phase=ShutdownPhase.CONNECTIONS,
    timeout_seconds=5.0
)
async def shutdown_my_service():
    await my_service.close()
```

#### Main.py Integration

```python
@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown with engine cleanup and 30-second timeout."""
    # Phase 1: Job queue
    await asyncio.wait_for(_shutdown_job_queue(), timeout=shutdown_timeout * 0.3)
    
    # Phase 2: Engines
    await asyncio.wait_for(_shutdown_engines(), timeout=shutdown_timeout * 0.4)
    
    # Phase 3: Parallel cleanup
    await asyncio.gather(
        _shutdown_temp_files(),
        _shutdown_scheduler(),
        _shutdown_database(),
        _shutdown_security_services(),
    )
```

### 4.3 Configuration

```bash
# Environment variables
VOICESTUDIO_SHUTDOWN_TIMEOUT=30.0  # Total shutdown timeout (seconds)
```

### 4.4 Signal Handling

The orchestrator handles system signals:
- `SIGTERM` - Graceful shutdown (Kubernetes, Docker)
- `SIGINT` - Graceful shutdown (Ctrl+C)

---

## 5. Correlation ID Logging

### 5.1 Architecture

All requests are traced with correlation IDs:

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Request                           │
│               X-Correlation-ID: <optional>                   │
├─────────────────────────────────────────────────────────────┤
│                Correlation ID Middleware                     │
│         (Accept or generate correlation ID)                  │
├─────────────────────────────────────────────────────────────┤
│                    Request Processing                        │
│           (correlation_id in all logs)                       │
├─────────────────────────────────────────────────────────────┤
│                     Response                                 │
│               X-Correlation-ID: <id>                         │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Usage

#### In Route Handlers

```python
from backend.api.middleware.correlation_id import get_correlation_id

@router.post("/my-endpoint")
async def my_endpoint(request: Request):
    correlation_id = get_correlation_id()
    logger.info(f"Processing request", extra={"correlation_id": correlation_id})
```

#### Log Format

```
[abc123-def456-789] - 2026-02-14 10:30:00 - INFO - Processing request
```

### 5.3 Configuration

The middleware is automatically enabled in `main.py`:

```python
from backend.api.middleware.correlation_id import (
    CorrelationIdMiddleware,
    setup_correlation_logging,
)

app.add_middleware(CorrelationIdMiddleware)
setup_correlation_logging()
```

---

## 6. Security Checklist

### Pre-Deployment

- [ ] All API keys stored via `SecureStorageService` or environment variables
- [ ] No plaintext secrets in config files
- [ ] `api-keys.json` and `.env.mcp.local` in `.gitignore`
- [ ] DPAPI availability verified on target systems
- [ ] Health check endpoints tested
- [ ] Shutdown timeout configured appropriately

### Ongoing Operations

- [ ] Monitor health check endpoints
- [ ] Review correlation IDs in error logs
- [ ] Rotate API keys periodically
- [ ] Test graceful shutdown procedures
- [ ] Verify error messages don't leak sensitive info

---

## 7. Troubleshooting

### Credential Storage Issues

**Problem:** DPAPI not available
```csharp
if (!SecureStorageService.IsDpapiAvailable())
{
    // Fall back to environment variables
}
```

**Problem:** Windows Credential Manager access denied
- Ensure application runs as the correct user
- Check Windows Credential Manager has available slots

### Health Check Failures

**Problem:** Database health check fails
- Verify SQLite database path exists and is writable
- Check disk space availability

**Problem:** Engine health check shows unhealthy
- This is normal if ML engines aren't installed
- System operates in degraded mode (CPU-only)

### Shutdown Issues

**Problem:** Shutdown timeout exceeded
- Check for hung engine processes
- Review shutdown handler logs for failures
- Consider increasing `VOICESTUDIO_SHUTDOWN_TIMEOUT`

### Correlation ID Missing

**Problem:** Logs don't show correlation IDs
- Verify `setup_correlation_logging()` was called
- Check log formatter includes `%(correlation_id)s`

---

## 8. Related Documentation

- [API Key Management Rule](../../.cursor/rules/security/api-key-management.mdc)
- [Secure Coding Rules](../../.cursor/rules/security/secure-coding.mdc)
- [MCP Security Rules](../../.cursor/rules/security/mcp-security.mdc)
- [Architecture Decision Records](../architecture/decisions/)

---

## Appendix A: File Reference

| Component | File Path |
|-----------|-----------|
| SecureStorage | `src/VoiceStudio.App/Services/SecureStorage.cs` |
| ISecretsService | `src/VoiceStudio.App/Core/Services/ISecretsService.cs` |
| DevVaultSecretsService | `src/VoiceStudio.App/Services/DevVaultSecretsService.cs` |
| WindowsCredentialManager | `src/VoiceStudio.App/Services/WindowsCredentialManagerSecretsService.cs` |
| ErrorHandler | `src/VoiceStudio.App/Utilities/ErrorHandler.cs` |
| ErrorBoundary | `src/VoiceStudio.App/Core/ErrorHandling/ErrorBoundary.cs` |
| Health Routes | `backend/api/routes/health.py` |
| HealthCheckService | `backend/monitoring/health/health_check.py` |
| GracefulShutdown | `backend/lifecycle/shutdown.py` |
| CorrelationIdMiddleware | `backend/api/middleware/correlation_id.py` |
