# Phase 7: Error Recovery Testing Evidence

**Date**: 2026-02-06
**Owner**: Core Platform (Role 4) + UI Engineer (Role 3)
**Status**: STRUCTURE VERIFIED - AWAITING RUNTIME TESTING

---

## 1. Crash Recovery Service

### Implementation Details

Source: `src/VoiceStudio.App/Services/CrashRecoveryService.cs`

| Component | Description | Status |
|-----------|-------------|--------|
| Class | `CrashRecoveryService : IDisposable` | ✅ Verified |
| Auto-save | Timer-based (60s interval) | ✅ Verified |
| Session State | JSON serialization | ✅ Verified |
| Crash Marker | File-based detection | ✅ Verified |
| Events | `SessionRecovered`, `RecoveryFailed` | ✅ Verified |

### Storage Locations

```
%LOCALAPPDATA%\VoiceStudio\Recovery\
├── session.json      # Current session state
└── .crash_marker     # Crash detection marker
```

### Session State Contents

- `SessionId`: Unique session identifier
- `ActiveProject`: Current project path/name
- `OpenFiles`: List of open files
- `Timestamp`: Last save time
- `UnsavedChanges`: Pending modifications

### Recovery Flow

1. **App Launch**: Check for crash marker
2. **Marker Present**: Crash detected → read session.json
3. **Session Valid**: Raise `SessionRecovered` event
4. **User Prompted**: Offer to restore session
5. **Clean Start**: Create new crash marker
6. **Clean Shutdown**: Remove crash marker

### Deferred Initialization

From `DeferredServiceInitializer.CreateDefault()`:
```csharp
initializer.RegisterAsync(
    "CrashRecoveryCheck",
    async ct => {
        var crashRecovery = serviceProvider.GetService<CrashRecoveryService>();
        await crashRecovery?.InitializeAsync();
    },
    ServicePriority.Normal);
```

---

## 2. Circuit Breaker Pattern

### Implementation Details

Source: `backend/services/circuit_breaker.py` (382 lines)

| Component | Description | Status |
|-----------|-------------|--------|
| Module | TD-014 implementation | ✅ Verified |
| States | CLOSED, OPEN, HALF_OPEN | ✅ Verified |
| Config | `CircuitBreakerConfig` dataclass | ✅ Verified |
| Stats | `CircuitBreakerStats` dataclass | ✅ Verified |
| Error | `CircuitBreakerOpenError` | ✅ Verified |

### State Machine

```
CLOSED  ──[failure_threshold reached]──> OPEN
   ↑                                        │
   └──[success_threshold reached]── HALF_OPEN <──[recovery_timeout]──┘
```

### Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | 3 | Failures before opening |
| `success_threshold` | 2 | Successes to close from half-open |
| `recovery_timeout` | 60.0s | Seconds before testing recovery |
| `half_open_max_calls` | 3 | Max concurrent calls in half-open |

### Integration in Engine Service

Source: `backend/services/engine_service.py`

```python
self._circuit_breakers: Dict[str, CircuitBreaker] = {}
self._circuit_breaker_config = CircuitBreakerConfig(
    failure_threshold=3,
    success_threshold=2,
    recovery_timeout=60.0,
)
```

### Usage in Routes

Sources: `backend/api/routes/image_gen.py`, `backend/api/routes/video_gen.py`

```python
try:
    async with breaker():
        result = engine.generate(**gen_kwargs)
except CircuitBreakerOpenError as e:
    raise HTTPException(
        status_code=503,
        detail=f"Engine temporarily unavailable: {e}",
    )
```

### Health Endpoint

```python
def get_engine_health(self, engine_id: EngineId) -> Dict[str, Any]:
    breaker = self._get_circuit_breaker(engine_id)
    stats = breaker.get_stats()
    return {
        "engine_id": engine_id,
        "circuit_state": stats.state.name,
        "failure_count": stats.failure_count,
        "success_count": stats.success_count,
        "total_calls": stats.total_calls,
    }
```

---

## 3. Data Backup Service

### Implementation Details

Source: `src/VoiceStudio.App/Services/DataBackupService.cs`

| Component | Description | Status |
|-----------|-------------|--------|
| Class | `DataBackupService : IDisposable` | ✅ Verified |
| Auto-backup | Timer-based (configurable) | ✅ Verified |
| Retention | Max backups with cleanup | ✅ Verified |
| Events | `BackupCompleted`, `BackupFailed` | ✅ Verified |
| Settings | JSON config file | ✅ Verified |

### Storage Locations

```
%LOCALAPPDATA%\VoiceStudio\
├── Backups\
│   ├── backup_2026-02-06_001.zip
│   └── backup_2026-02-05_001.zip
└── backup_settings.json
```

### Configuration Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `AutoBackupEnabled` | true | Enable automatic backups |
| `BackupIntervalHours` | 24 | Hours between backups |
| `MaxBackups` | 10 | Retention count |

### Backup Contents

- User projects
- Application settings
- Voice presets
- Custom configurations

---

## Test Execution Requirements

### Test 7.1: Crash Recovery

| Step | Action | Expected Result |
|------|--------|-----------------|
| 7.1.1 | Launch VoiceStudio | App starts normally |
| 7.1.2 | Open a project | Project loads |
| 7.1.3 | Make unsaved changes | Changes visible |
| 7.1.4 | Force-kill process | `taskkill /F /IM VoiceStudio.exe` |
| 7.1.5 | Relaunch app | Crash recovery dialog appears |
| 7.1.6 | Accept recovery | Previous session restored |
| 7.1.7 | Verify state | Unsaved changes present |

### Test 7.2: Circuit Breaker

```bash
# Simulate engine failures
# Step 1: Trigger 3 consecutive failures
curl -X POST http://localhost:8001/api/synthesis/synthesize \
  -d '{"engine": "test_engine", "text": "fail_test"}'
# (repeat 3 times with simulated failures)

# Step 2: Verify circuit OPEN
curl http://localhost:8001/api/engines/health
# Expected: {"test_engine": {"circuit_state": "OPEN"}}

# Step 3: Wait 60 seconds
Start-Sleep -Seconds 60

# Step 4: Verify HALF_OPEN
curl http://localhost:8001/api/engines/health
# Expected: {"test_engine": {"circuit_state": "HALF_OPEN"}}

# Step 5: Successful request
curl -X POST http://localhost:8001/api/synthesis/synthesize \
  -d '{"engine": "test_engine", "text": "success_test"}'

# Step 6: Verify CLOSED
curl http://localhost:8001/api/engines/health
# Expected: {"test_engine": {"circuit_state": "CLOSED"}}
```

### Test 7.3: Data Backup

| Step | Action | Expected Result |
|------|--------|-----------------|
| 7.3.1 | Open Settings | Backup settings visible |
| 7.3.2 | Enable auto-backup | Setting saved |
| 7.3.3 | Click "Backup Now" | Manual backup created |
| 7.3.4 | Check backup folder | Zip file present |
| 7.3.5 | Verify backup contents | Projects/settings included |
| 7.3.6 | Create 11 backups | Oldest backup pruned |
| 7.3.7 | Restore from backup | Data restored correctly |

### Test 7.4: Error Dialog Service

Source: `src/VoiceStudio.App/Services/ErrorDialogService.cs`

| Step | Action | Expected Result |
|------|--------|-----------------|
| 7.4.1 | Trigger recoverable error | Dialog with suggestion shown |
| 7.4.2 | Trigger fatal error | Dialog with contact info shown |
| 7.4.3 | Check error logging | Error logged to file |
| 7.4.4 | Verify UI remains responsive | No UI freeze |

---

## Evidence Files

| File | Purpose | Status |
|------|---------|--------|
| CrashRecoveryService.cs | Crash detection/recovery | ✅ Analyzed |
| circuit_breaker.py | Circuit breaker pattern | ✅ Analyzed |
| engine_service.py | Circuit breaker integration | ✅ Analyzed |
| DataBackupService.cs | Automatic/manual backups | ✅ Analyzed |
| ErrorDialogService.cs | User-friendly error dialogs | ✅ Analyzed |
| IErrorDialogService.cs | Error dialog contract | ✅ Analyzed |

---

## Phase 7 Code Analysis: PASS

- ✅ CrashRecoveryService with session state persistence
- ✅ Crash marker file for detection
- ✅ Auto-save timer (60s interval)
- ✅ CircuitBreaker with 3 states (CLOSED/OPEN/HALF_OPEN)
- ✅ Configurable thresholds (failure, success, timeout)
- ✅ Integration in EngineService for all engines
- ✅ HTTP 503 response when circuit open
- ✅ DataBackupService with retention policy
- ✅ Auto-backup with configurable interval
- ✅ ErrorDialogService with recovery suggestions
- ⏳ Runtime testing requires application execution
