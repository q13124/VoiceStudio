# VoiceStudio Concurrency Guide

**GAP-I13: No Documented Lock Acquisition Order**

## Overview

This document defines the canonical lock acquisition order for VoiceStudio to prevent
deadlocks and ensure thread-safe operation across the application.

## Lock Acquisition Order (MUST Follow)

All locks must be acquired in **ascending order** by level. Never acquire a lower-level
lock while holding a higher-level lock.

| Level | Lock | Owner | Purpose | Async? |
|-------|------|-------|---------|--------|
| L1 | `AppStateStore._lock` | AppStateStore | Global application state | No |
| L2 | `EventAggregator._lock` | EventAggregator | Event subscriptions | No |
| L3 | `SettingsService._semaphore` | SettingsService | Settings cache | Yes |
| L4 | `AudioPlayerService._playbackLock` | AudioPlayerService | Playback state | Yes |
| L5 | `WorkspaceService._rwLock` | WorkspaceService | Project files | Yes |
| L6 | `PanelStateService._panelLocks[id]` | PanelStateService | Per-panel state | Yes |
| L7 | `CommandMutexService._lockSync` | CommandMutexService | Command group mutex | No |

## Lock Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        L1: AppStateStore                        │
│                     (Global application state)                  │
├─────────────────────────────────────────────────────────────────┤
│                       L2: EventAggregator                       │
│                      (Event subscriptions)                      │
├─────────────────────────────────────────────────────────────────┤
│                       L3: SettingsService                       │
│                        (Settings cache)                         │
├─────────────────────────────────────────────────────────────────┤
│                     L4: AudioPlayerService                      │
│                        (Playback state)                         │
├─────────────────────────────────────────────────────────────────┤
│                      L5: WorkspaceService                       │
│                         (Project files)                         │
├─────────────────────────────────────────────────────────────────┤
│                     L6: PanelStateService                       │
│                       (Per-panel state)                         │
├─────────────────────────────────────────────────────────────────┤
│                    L7: CommandMutexService                      │
│                     (Command group mutex)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Rules

### Rule 1: Always Acquire in Ascending Order

When multiple locks are needed, always acquire them in ascending order (L1 before L2,
L2 before L3, etc.).

**Correct:**
```csharp
// Acquiring L3 then L5 - ascending order ✓
await _settingsLock.WaitAsync();
try
{
    await _workspaceLock.WaitAsync();
    try
    {
        // Work with both
    }
    finally
    {
        _workspaceLock.Release();
    }
}
finally
{
    _settingsLock.Release();
}
```

**Incorrect:**
```csharp
// Acquiring L5 then L3 - descending order ✗ DEADLOCK RISK
await _workspaceLock.WaitAsync();  // L5
await _settingsLock.WaitAsync();   // L3 - WRONG ORDER!
```

### Rule 2: Never Hold a Higher Lock While Acquiring a Lower Lock

If you hold L5, you cannot acquire L3 or L4. Release higher locks first if you need
lower locks.

### Rule 3: Use Timeout-Based Acquisition

All lock acquisitions should use timeouts to prevent indefinite blocking:

```csharp
// Good: Timeout prevents indefinite wait
var acquired = await _semaphore.WaitAsync(TimeSpan.FromSeconds(10));
if (!acquired)
{
    throw new TimeoutException("Failed to acquire lock within timeout");
}

// Bad: No timeout - can block forever
await _semaphore.WaitAsync();
```

### Rule 4: Prefer SemaphoreSlim for Async, lock for Sync

| Scenario | Use |
|----------|-----|
| Async method with awaits | `SemaphoreSlim` |
| Quick synchronous access | `lock` statement |
| Reader/writer pattern | `ReaderWriterLockSlim` |
| Cross-process | `Mutex` |

### Rule 5: Use Debug Validator in DEBUG Builds

In debug builds, use `LockOrderValidator` to detect violations:

```csharp
#if DEBUG
using var _ = LockOrderValidator.AcquireLock(5, "WorkspaceService");
#endif
await _workspaceLock.WaitAsync(timeout);
```

## Lock Types Reference

### SemaphoreSlim (Async-Safe)

```csharp
private readonly SemaphoreSlim _semaphore = new(1, 1);

public async Task DoWorkAsync()
{
    await _semaphore.WaitAsync(TimeSpan.FromSeconds(10));
    try
    {
        // Critical section
    }
    finally
    {
        _semaphore.Release();
    }
}
```

### lock Statement (Sync Only)

```csharp
private readonly object _sync = new();

public void DoWork()
{
    lock (_sync)
    {
        // Critical section - NO async/await allowed
    }
}
```

### ReaderWriterLockSlim (Multiple Readers)

```csharp
private readonly ReaderWriterLockSlim _rwLock = new();

public void Read()
{
    _rwLock.EnterReadLock();
    try { /* read */ }
    finally { _rwLock.ExitReadLock(); }
}

public void Write()
{
    _rwLock.EnterWriteLock();
    try { /* write */ }
    finally { _rwLock.ExitWriteLock(); }
}
```

## Debug Mode Lock Order Validation

In DEBUG builds, `LockOrderValidator` tracks lock acquisition order and fails fast
on violations:

```csharp
// LockOrderValidator detects this violation:
using var _ = LockOrderValidator.AcquireLock(5, "L5");  // Acquire L5
using var __ = LockOrderValidator.AcquireLock(3, "L3"); // Attempt L3 → DEBUG FAIL
```

The validator is DEBUG-only and has zero overhead in release builds.

## Common Deadlock Patterns to Avoid

### Pattern 1: Lock Inversion

```csharp
// Thread A           Thread B
// --------           --------
// lock(A)            lock(B)
// lock(B)            lock(A)  ← DEADLOCK

// Fix: Always acquire A before B
```

### Pattern 2: Async in lock

```csharp
// Wrong: await inside lock causes issues
lock (_sync)
{
    await DoSomethingAsync();  // ✗ Can cause deadlock
}

// Fix: Use SemaphoreSlim instead
await _semaphore.WaitAsync();
try
{
    await DoSomethingAsync();  // ✓ Safe
}
finally
{
    _semaphore.Release();
}
```

### Pattern 3: Missing Release on Exception

```csharp
// Wrong: Exception prevents release
_semaphore.WaitAsync();
DoWork();  // If this throws, semaphore never released
_semaphore.Release();

// Fix: try/finally
await _semaphore.WaitAsync();
try
{
    DoWork();
}
finally
{
    _semaphore.Release();
}
```

## Adding a New Lock

When adding a new lock to the system:

1. **Determine the appropriate level** based on what other locks it might interact with
2. **Update this document** with the new lock's level, owner, and purpose
3. **Add DEBUG validation** using `LockOrderValidator.AcquireLock()`
4. **Use timeout-based acquisition** with appropriate timeout values
5. **Document any exceptions** to the ordering rules with justification

## References

- `src/VoiceStudio.App/Utilities/LockOrderValidator.cs` - Debug validator
- `src/VoiceStudio.App/Services/CommandMutexService.cs` - Command mutex implementation
- `docs/architecture/VOICESTUDIO_ARCHITECTURE_PORTFOLIO.md` - Original lock documentation

---

*Last updated: 2026-02-16*
*GAP Reference: GAP-I13 (No Documented Lock Acquisition Order)*
